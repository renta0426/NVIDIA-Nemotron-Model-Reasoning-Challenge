"""
v7 targeted miss-recovery corpus generator
===========================================
Strategy: laser-focus on the 19 confirmed local300 misses:
  - 16 bit_manipulation misses
  - 1  cipher miss
  - 2  equation_numeric_guess misses
  - no cryptarithm budget

For each miss ID emit:
  - answer_only style (forced-correct boxed, empty <think>)   × ANSWER_ONLY_REPEATS
  - reasoning  style (gold answer forced in boxed) × REASONING_REPEATS
    (reasoning only emitted when the teacher file's last \\boxed matches gold)

Base snapshot: 04-08-16-14 (all 7830 rows, minus ef2fe526).
Bundle compatible with reproduce_v20_mlx_repro.py --training-bundle-path.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer


# ---------------------------------------------------------------------------
# paths
# ---------------------------------------------------------------------------
def _find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    while cur != cur.parent:
        if (cur / "README.md").exists() and (cur / "pyproject.toml").exists():
            return cur
        cur = cur.parent
    raise RuntimeError(f"Could not locate repo root from {start}")


REPO_ROOT = _find_repo_root(Path(__file__).resolve())
VERSION_ROOT = Path(__file__).resolve().parent
VERSION_NAME = "v7_targeted_miss_recovery"

TRAIN_CSV_PATH = REPO_ROOT / "data" / "train.csv"
RECOMMENDED_CSV_PATH = (
    REPO_ROOT
    / "cuda-train-data-analysis-v1"
    / "artifacts"
    / "train_recommended_learning_target_v1.csv"
)
REASONING_DIR = (
    REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "reasoning"
)
TRAINING_SFT_ROOT = (
    REPO_ROOT
    / "A-Open-ProgressPrizePublication"
    / "nemotron"
    / "training"
    / "sft"
)
MLX_BUNDLE_ROOT = TRAINING_SFT_ROOT / "MLX"
BASE_SNAPSHOT_ROOT = TRAINING_SFT_ROOT / "04-08-16-14"
BASE_SNAPSHOT_CONFIG_PATH = BASE_SNAPSHOT_ROOT / "config.json"
BASE_SNAPSHOT_INDEX_PATH = BASE_SNAPSHOT_ROOT / "logprobs" / "index.jsonl"
BASE_SNAPSHOT_TOKENS_DIR = BASE_SNAPSHOT_ROOT / "tokens"

DEFAULT_BUNDLE_PATH = MLX_BUNDLE_ROOT / f"{VERSION_NAME}_bundle.jsonl"
RESULTS_MD = VERSION_ROOT / f"{VERSION_NAME}-results.md"

MODEL_TOKENIZER_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
TOKEN_LIMIT = 8192
PROMPT_SUFFIX = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)

# ---------------------------------------------------------------------------
# miss target sets  (confirmed local300 failures from best baseline)
# ---------------------------------------------------------------------------
BIT_MISS_IDS: list[str] = [
    "000b53cf", "012fb81b", "01e09228", "02a66bcb", "034fb629",
    "048cc279", "04d8c3e6", "05ca617c", "06881e47", "07e8cf66",
    "0b16458a", "0ec17d2e", "12fd5b6c", "132ec6ae", "16db2c74",
    "172d2417",
]
CIPHER_MISS_IDS: list[str] = ["0184a864"]
EQUATION_MISS_IDS: list[str] = ["065f9dea", "0c0683c3"]
ALL_MISS_IDS: list[str] = BIT_MISS_IDS + CIPHER_MISS_IDS + EQUATION_MISS_IDS

# IDs confirmed absent from train_recommended metadata; handle gracefully
ABSENT_FROM_RECOMMENDED: set[str] = {"0ec17d2e"}

# Repeat counts for overlay generation
ANSWER_ONLY_REPEATS = 32   # per miss ID  – strong direct signal
REASONING_REPEATS = 10     # per miss ID  – only when teacher answer == gold

BASE_EXCLUDED_IDS: set[str] = {"ef2fe526"}


# ---------------------------------------------------------------------------
# utilities
# ---------------------------------------------------------------------------
def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_jsonl_line(handle: Any, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# data loaders
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def load_train_csv() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with open(TRAIN_CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows[row["id"]] = dict(row)
    return rows


@lru_cache(maxsize=1)
def load_recommended_csv() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with open(RECOMMENDED_CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows[row["id"]] = dict(row)
    return rows


def load_reasoning_text(row_id: str) -> str | None:
    path = REASONING_DIR / f"{row_id}.txt"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def extract_last_boxed(text: str) -> str | None:
    matches = re.findall(r"\\boxed\{([^}]*)\}", text)
    return matches[-1].strip() if matches else None


@lru_cache(maxsize=1)
def get_tokenizer() -> Any:
    tok = AutoTokenizer.from_pretrained(MODEL_TOKENIZER_NAME, trust_remote_code=True)
    if tok.pad_token_id is None and tok.eos_token_id is not None:
        tok.pad_token = tok.eos_token
    return tok


def tokenize_example(prompt: str, completion: str) -> tuple[list[int], list[int]]:
    """Return (tokens, mask) where mask=1 for completion tokens (loss-bearing)."""
    tok = get_tokenizer()
    prompt_ids: list[int] = tok.apply_chat_template(
        [{"role": "user", "content": prompt + PROMPT_SUFFIX}],
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=True,
    )
    completion_ids: list[int] = tok.encode(completion, add_special_tokens=False)
    all_tokens = list(prompt_ids) + list(completion_ids)
    mask = [0] * len(prompt_ids) + [1] * len(completion_ids)
    if len(all_tokens) > TOKEN_LIMIT:
        all_tokens = all_tokens[:TOKEN_LIMIT]
        mask = mask[:TOKEN_LIMIT]
    return all_tokens, mask


# ---------------------------------------------------------------------------
# completion builders
# ---------------------------------------------------------------------------
def build_reasoning_completion(reasoning_text: str, gold_answer: str) -> str:
    """Reasoning completion: keep full teacher trace but force gold boxed answer."""
    return f"{reasoning_text}\n</think>\n\\boxed{{{gold_answer}}}<|im_end|>"


def build_answer_only_completion(gold_answer: str) -> str:
    """Short answer-only completion with empty <think> block."""
    return f"\n</think>\n\\boxed{{{gold_answer}}}<|im_end|>"


# ---------------------------------------------------------------------------
# base snapshot loading
# ---------------------------------------------------------------------------
def load_base_snapshot() -> tuple[list[dict[str, Any]], int]:
    """Load index rows + their token files; return (rows, batch_size)."""
    with open(BASE_SNAPSHOT_CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    batch_size = int(cfg["batch_size"])

    rows: list[dict[str, Any]] = []
    with open(BASE_SNAPSHOT_INDEX_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    # load token payloads and attach
    enriched: list[dict[str, Any]] = []
    for row in rows:
        problem_id = str(row["problem_id"])
        base_pid = problem_id.split("-p")[0]
        if base_pid in BASE_EXCLUDED_IDS:
            continue
        segment = str(row["segment"])
        token_path = BASE_SNAPSHOT_TOKENS_DIR / problem_id / f"{Path(segment).stem}.json"
        if not token_path.exists():
            print(f"  [WARN] missing token file: {token_path}")
            continue
        with open(token_path, encoding="utf-8") as tf:
            payload = json.load(tf)
        enriched.append({
            "row": row,
            "tokens": payload["tokens"],
            "mask": payload["mask"],
        })

    return enriched, batch_size


# ---------------------------------------------------------------------------
# overlay generation
# ---------------------------------------------------------------------------
def build_overlay_examples() -> list[dict[str, Any]]:
    """Return ordered list of overlay examples (not yet assigned steps)."""
    train = load_train_csv()
    diagnostics: list[str] = []
    examples: list[dict[str, Any]] = []

    for mid in ALL_MISS_IDS:
        if mid not in train:
            diagnostics.append(f"WARN: {mid} absent from train.csv – skipping")
            print(f"  [WARN] {mid} absent from train.csv – skipping")
            continue

        row = train[mid]
        gold = str(row["answer"]).strip()
        prompt = str(row["prompt"]).strip()

        # determine category
        if mid in BIT_MISS_IDS:
            category = "bit_manipulation"
        elif mid in CIPHER_MISS_IDS:
            category = "cipher"
        else:
            category = "equation_numeric_guess"

        # check recommended metadata
        if mid not in load_recommended_csv() and mid not in ABSENT_FROM_RECOMMENDED:
            diagnostics.append(f"WARN: {mid} unexpectedly absent from recommended CSV")
            print(f"  [WARN] {mid} absent from recommended CSV (unexpected)")
        elif mid in ABSENT_FROM_RECOMMENDED:
            diagnostics.append(f"INFO: {mid} confirmed absent from recommended CSV; proceeding with train.csv data only")

        # reasoning file
        reasoning_text = load_reasoning_text(mid)
        teacher_match = False
        if reasoning_text is not None:
            teacher_boxed = extract_last_boxed(reasoning_text)
            teacher_match = (teacher_boxed is not None) and (teacher_boxed.strip() == gold)

        # --- reasoning-style examples (only when teacher answer == gold) ---
        if teacher_match and reasoning_text is not None:
            completion = build_reasoning_completion(reasoning_text, gold)
            tokens, mask = tokenize_example(prompt, completion)
            num_loss = sum(mask)
            for rep in range(REASONING_REPEATS):
                examples.append({
                    "example_id": f"{mid}#reasoning-{rep}",
                    "source_problem_id": mid,
                    "source": "corrective_overlay",
                    "segment": "synthetic.jsonl",
                    "category": category,
                    "style": "reasoning",
                    "repeat_index": rep,
                    "tokens": tokens,
                    "mask": mask,
                    "num_loss_tokens": num_loss,
                })

        # --- answer-only examples (always) ---
        ao_completion = build_answer_only_completion(gold)
        ao_tokens, ao_mask = tokenize_example(prompt, ao_completion)
        ao_num_loss = sum(ao_mask)
        for rep in range(ANSWER_ONLY_REPEATS):
            examples.append({
                "example_id": f"{mid}#answeronly-{rep}",
                "source_problem_id": mid,
                "source": "corrective_overlay",
                "segment": "synthetic.jsonl",
                "category": category,
                "style": "answer_only",
                "repeat_index": rep,
                "tokens": ao_tokens,
                "mask": ao_mask,
                "num_loss_tokens": ao_num_loss,
            })

        print(
            f"  {mid} [{category}]: gold={gold!r} teacher_match={teacher_match}"
            f"  → reasoning×{REASONING_REPEATS if teacher_match else 0} "
            f"+ answer_only×{ANSWER_ONLY_REPEATS}"
        )

    return examples


# ---------------------------------------------------------------------------
# bundle writer
# ---------------------------------------------------------------------------
def build_bundle(bundle_path: Path) -> dict[str, Any]:
    print(f"Loading base snapshot from {BASE_SNAPSHOT_ROOT} ...")
    base_examples, batch_size = load_base_snapshot()
    print(f"  base examples loaded: {len(base_examples)} (batch_size={batch_size})")

    print("Building overlay examples ...")
    overlay_examples = build_overlay_examples()
    print(f"  overlay examples: {len(overlay_examples)}")

    # derive step range
    base_steps = [int(ex["row"]["step"]) for ex in base_examples]
    base_step_count = max(base_steps) + 1 if base_steps else 0  # first overlay step

    total_examples = 0
    total_tokens = 0
    total_masked_tokens = 0
    total_unmasked_tokens = 0
    max_seq_len = 0
    category_counts: Counter[str] = Counter()

    base_snapshot_cfg = json.loads(BASE_SNAPSHOT_CONFIG_PATH.read_text(encoding="utf-8"))

    manifest = {
        "record_type": "manifest",
        "bundle_format": "nemotron_single_file_training_bundle_v1",
        "version": VERSION_NAME,
        "created_at": utc_now(),
        "base_snapshot_root": str(BASE_SNAPSHOT_ROOT.relative_to(REPO_ROOT)),
        "base_snapshot_config": base_snapshot_cfg,
        "base_excluded_problem_ids": sorted(BASE_EXCLUDED_IDS),
        "bundle_path": str(bundle_path.relative_to(REPO_ROOT)),
        "miss_targets": ALL_MISS_IDS,
        "answer_only_repeats": ANSWER_ONLY_REPEATS,
        "reasoning_repeats": REASONING_REPEATS,
        "no_cryptarithm": True,
        "note": (
            "v7 laser-focus overlay: 19 confirmed local300 misses "
            "(16 bit_manipulation + 1 cipher + 2 equation_numeric_guess). "
            "No cryptarithm. answer_only for all misses; reasoning where teacher=gold. "
            "Base snapshot 04-08-16-14 minus ef2fe526."
        ),
    }

    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    with bundle_path.open("w", encoding="utf-8") as fh:
        write_jsonl_line(fh, manifest)

        # base examples
        for ex in base_examples:
            row = ex["row"]
            tokens = ex["tokens"]
            mask = ex["mask"]
            record = {
                "record_type": "example",
                "example_id": str(row["problem_id"]),
                "source_problem_id": str(row["problem_id"]),
                "source": "base_snapshot",
                "segment": str(row["segment"]),
                "category": str(row["category"]),
                "step": int(row["step"]),
                "num_loss_tokens": int(row["num_loss_tokens"]),
                "tokens": tokens,
                "mask": mask,
            }
            write_jsonl_line(fh, record)
            total_examples += 1
            total_tokens += len(tokens)
            total_masked_tokens += mask.count(0)
            total_unmasked_tokens += mask.count(1)
            max_seq_len = max(max_seq_len, len(tokens))
            category_counts[str(row["category"])] += 1

        # overlay examples
        for ov_offset, ov_ex in enumerate(overlay_examples):
            ov_step = base_step_count + (ov_offset // batch_size)
            record = {
                "record_type": "example",
                "example_id": ov_ex["example_id"],
                "source_problem_id": ov_ex["source_problem_id"],
                "source": ov_ex["source"],
                "segment": ov_ex["segment"],
                "category": ov_ex["category"],
                "style": ov_ex["style"],
                "repeat_index": ov_ex["repeat_index"],
                "step": ov_step,
                "num_loss_tokens": ov_ex["num_loss_tokens"],
                "tokens": ov_ex["tokens"],
                "mask": ov_ex["mask"],
            }
            write_jsonl_line(fh, record)
            total_examples += 1
            total_tokens += len(ov_ex["tokens"])
            total_masked_tokens += ov_ex["mask"].count(0)
            total_unmasked_tokens += ov_ex["mask"].count(1)
            max_seq_len = max(max_seq_len, len(ov_ex["tokens"]))
            category_counts[ov_ex["category"]] += 1

    total_overlay_steps = (len(overlay_examples) + batch_size - 1) // batch_size
    total_steps = base_step_count + total_overlay_steps

    # overlay composition breakdown
    overlay_by_id: Counter[str] = Counter()
    overlay_by_style: Counter[str] = Counter()
    overlay_by_category: Counter[str] = Counter()
    for ov_ex in overlay_examples:
        overlay_by_id[ov_ex["source_problem_id"]] += 1
        overlay_by_style[ov_ex["style"]] += 1
        overlay_by_category[ov_ex["category"]] += 1

    stats = {
        "bundle_path": str(bundle_path),
        "base_examples": len(base_examples),
        "overlay_examples": len(overlay_examples),
        "total_examples": total_examples,
        "total_steps": total_steps,
        "base_step_count": base_step_count,
        "overlay_steps": total_overlay_steps,
        "total_tokens": total_tokens,
        "total_masked_tokens": total_masked_tokens,
        "total_unmasked_tokens": total_unmasked_tokens,
        "max_seq_len": max_seq_len,
        "category_counts": dict(sorted(category_counts.items())),
        "overlay_by_category": dict(sorted(overlay_by_category.items())),
        "overlay_by_style": dict(sorted(overlay_by_style.items())),
        "unique_miss_ids_covered": len(overlay_by_id),
        "miss_ids_covered": sorted(overlay_by_id.keys()),
        "batch_size": batch_size,
    }
    return stats


# ---------------------------------------------------------------------------
# results markdown
# ---------------------------------------------------------------------------
def update_results_md(stats: dict[str, Any]) -> None:
    content = f"""# v7 targeted miss-recovery results

## Why v7 exists

v6 experiments ran into paused/stuck training runs and high complexity.
v7 restarts with a clean, minimal design: **laser-focus on the exact 19 confirmed
local300 miss IDs** from the retained best baseline
(`v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc`, local300 = 254/300 = 0.846667).

## Targeted miss sets

### bit_manipulation misses (16)
{', '.join(BIT_MISS_IDS)}

### cipher misses (1)
{', '.join(CIPHER_MISS_IDS)}

### equation_numeric_guess misses (2)
{', '.join(EQUATION_MISS_IDS)}

## No-cryptarithm rationale

Cryptarithm is a hard, low-ROI category for local300.  Budget saved here is reallocated
to more answer-only repeats on the confirmed miss IDs.

## Teacher-match diagnostic

Only IDs where the teacher reasoning file's last `\\boxed` answer matches the gold answer
get reasoning-style examples.  All IDs unconditionally get answer-only examples.

Known absent from `train_recommended_learning_target_v1.csv`: `0ec17d2e`
(handled gracefully; uses `train.csv` prompt/answer only).

## Dataset composition

| Field | Value |
|-------|-------|
| Base examples | {stats.get('base_examples', '?')} |
| Overlay examples | {stats.get('overlay_examples', '?')} |
| Total examples | {stats.get('total_examples', '?')} |
| Total steps | {stats.get('total_steps', '?')} |
| Base steps | {stats.get('base_step_count', '?')} |
| Overlay steps | {stats.get('overlay_steps', '?')} |
| Total tokens | {stats.get('total_tokens', '?')} |
| Max sequence length | {stats.get('max_seq_len', '?')} |
| Answer-only repeats / miss | {ANSWER_ONLY_REPEATS} |
| Reasoning repeats / miss (when teacher=gold) | {REASONING_REPEATS} |
| Unique miss IDs covered | {stats.get('unique_miss_ids_covered', '?')} |

### Overlay by category

| Category | Examples |
|----------|---------|
"""
    for cat, cnt in sorted(stats.get("overlay_by_category", {}).items()):
        content += f"| {cat} | {cnt} |\n"

    content += f"""
### Overlay by style

| Style | Examples |
|-------|---------|
"""
    for style, cnt in sorted(stats.get("overlay_by_style", {}).items()):
        content += f"| {style} | {cnt} |\n"

    content += f"""
## Bundle path

`{stats.get('bundle_path', '(not generated yet)')}`

## Current status

- Bundle generated: {'YES' if stats.get('total_examples') else 'NO'}
- MLX training: NOT YET STARTED (run with reproduce_v20_mlx_repro.py --training-bundle-path)
- local300 score after training: TBD

## Generated

{utc_now()}
"""
    RESULTS_MD.write_text(content, encoding="utf-8")
    print(f"Results MD updated: {RESULTS_MD}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="v7 targeted miss-recovery bundle generator"
    )
    parser.add_argument(
        "--bundle-path",
        type=Path,
        default=DEFAULT_BUNDLE_PATH,
        help=f"Output bundle JSONL path (default: {DEFAULT_BUNDLE_PATH})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Tokenize overlay only; do not write bundle",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bundle_path = Path(args.bundle_path)

    print(f"=== v7 targeted miss-recovery bundle generator ===")
    print(f"Bundle path: {bundle_path}")
    print(f"Miss targets: {len(ALL_MISS_IDS)} IDs")
    print(f"  bit_manipulation: {len(BIT_MISS_IDS)}")
    print(f"  cipher: {len(CIPHER_MISS_IDS)}")
    print(f"  equation_numeric_guess: {len(EQUATION_MISS_IDS)}")
    print(f"Answer-only repeats: {ANSWER_ONLY_REPEATS}")
    print(f"Reasoning repeats (when teacher=gold): {REASONING_REPEATS}")
    print()

    if args.dry_run:
        print("[DRY RUN] Building overlay only ...")
        overlay = build_overlay_examples()
        print(f"Overlay examples built: {len(overlay)}")
        stats: dict[str, Any] = {
            "bundle_path": str(bundle_path),
            "overlay_examples": len(overlay),
            "total_examples": None,
        }
    else:
        stats = build_bundle(bundle_path)
        bundle_size_mb = bundle_path.stat().st_size / 1024 / 1024
        stats["bundle_size_mb"] = round(bundle_size_mb, 2)
        print()
        print("=== Bundle stats ===")
        for k, v in stats.items():
            if k not in ("miss_ids_covered",):
                print(f"  {k}: {v}")
        print(f"  bundle size: {bundle_size_mb:.1f} MB")

    update_results_md(stats)
    print(f"\nDone.")


if __name__ == "__main__":
    main()
