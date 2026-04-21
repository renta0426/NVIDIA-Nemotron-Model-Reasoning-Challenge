from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    while current != current.parent:
        if (current / "README.md").exists() and (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError(f"Could not locate repository root from {start}")


REPO_ROOT = find_repo_root(Path(__file__).resolve())
VERSION_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = VERSION_ROOT / "outputs"
RESULTS_MD = VERSION_ROOT / "v20_corrective_corpus_v7_mainline-results.md"

README_PATH = REPO_ROOT / "README.md"
TRAINING_SFT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "training" / "sft"
BASE_SNAPSHOT_ROOT = TRAINING_SFT_ROOT / "04-08-16-14"
BASE_SNAPSHOT_CONFIG_PATH = BASE_SNAPSHOT_ROOT / "config.json"
BASE_SNAPSHOT_INDEX_PATH = BASE_SNAPSHOT_ROOT / "logprobs" / "index.jsonl"
DEFAULT_BUNDLE_PATH = TRAINING_SFT_ROOT / "v20_corrective_corpus_v7_mainline_bundle.jsonl"
MODEL_TOKENIZER_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
OVERLAY_TOKEN_STRATEGIES = {"reuse_base_synthetic", "retokenize_all"}
PROMPT_SUFFIX = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)
TOKEN_LIMIT = 8192

V4_OUTPUT_ROOT = REPO_ROOT / "versions" / "v20_corrective_corpus_v4_mainline" / "outputs" / "v4_mainline_default"
V6_OUTPUT_ROOT = REPO_ROOT / "versions" / "v20_corrective_corpus_v6_mainline" / "outputs" / "v6_mainline_default"

V4_REPEATED_PATH = V4_OUTPUT_ROOT / "artifacts" / "corrective_overlay_repeated.jsonl"
V4_SELECTION_PATH = V4_OUTPUT_ROOT / "artifacts" / "corrective_selection.csv"
V4_SUMMARY_PATH = V4_OUTPUT_ROOT / "artifacts" / "corrective_overlay_summary.json"
V6_REPEATED_PATH = V6_OUTPUT_ROOT / "artifacts" / "corrective_overlay_repeated.jsonl"
V6_SELECTION_PATH = V6_OUTPUT_ROOT / "artifacts" / "corrective_selection.csv"
V6_SUMMARY_PATH = V6_OUTPUT_ROOT / "artifacts" / "corrective_overlay_summary.json"

RESULT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "result"
RESULT_V20_PROXY_PATH = RESULT_ROOT / "leaderboard_proxy_eval_v20" / "artifacts" / "leaderboard_proxy_eval_row_level.csv"
RESULT_V4_PROXY_PATH = RESULT_ROOT / "leaderboard_proxy_eval-v4" / "artifacts" / "leaderboard_proxy_eval_row_level.csv"
RESULT_V6_PROXY_PATH = RESULT_ROOT / "leaderboard_proxy_eval-v6" / "artifacts" / "leaderboard_proxy_eval_row_level.csv"
RESULT_V6_NUMERAL_MISTAKES_PATH = RESULT_ROOT / "results-v6" / "mistakes" / "numeral.csv"

README_EVAL_CONTRACT = {
    "max_lora_rank": 32,
    "max_tokens": 7680,
    "top_p": 1.0,
    "temperature": 0.0,
    "max_num_seqs": 64,
    "gpu_memory_utilization": 0.85,
    "max_model_len": 8192,
}

BASE_EXCLUDED_IDS = {"ef2fe526"}
MANUAL_BINARY_DONOR_IDS = {
    "0520a6ec",
    "0a50c4a8",
    "0dd5caf4",
    "17fd9612",
    "59c78e51",
    "8e5d6fe6",
    "b9500f41",
    "c30a782a",
    "fa67da07",
}
V7_NUMERAL_SURFACE_IDS = {
    "00d9f682",
    "018d465c",
    "0aa2c5bf",
    "0b2877ce",
    "0ea93e44",
    "105255db",
    "1112ec96",
    "1542039b",
    "18840879",
    "188fe6d4",
    "18997574",
}
V7_EXPLICIT_SYNTHETIC_ROWS: dict[str, dict[str, Any]] = {
    "1542039b": {
        "id": "1542039b",
        "category": "numeral",
        "bucket": "surface_numeral_boxed_donor",
        "prompt": "In Alice's Wonderland, numbers are secretly converted into a different numeral system. Some examples are given below:\n73 -> LXXIII\n17 -> XVII\n27 -> XXVII\n19 -> XIX\n100 -> C\nNow, write the number 54 in the Wonderland numeral system.",
        "answer": "LIV",
        "completion_text": "<think>\nWrite only the final Roman numeral in the box.\nDo not add extra text after the boxed answer.\n</think>\n\\boxed{LIV}<|im_end|>",
        "assistant_style": "surface_boxed_tail",
        "supervision_role": "lane4_surface_stabilizer",
        "selection_tier": "v7_numeral_surface_synth",
        "template_subtype": "roman_standard",
        "teacher_solver_candidate": "roman_surface_boxed_only",
        "source_tags": ["surface_numeral_boxed_donor", "v7_numeral_surface_synth"],
        "source_mix": "v7_numeral_surface_synth",
        "proxy_failed": False,
        "validation_failed": True,
        "hard_score": 0.0,
        "audit_reasons": "",
        "analysis_notes": "v6_numeral_no_box_backfill",
        "symbol_query_operator": "",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"Missing CSV header: {path}")
        return [dict(row) for row in reader]


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relative_to_repo(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def normalize_tags(raw_tags: Any) -> list[str]:
    if isinstance(raw_tags, list):
        return [str(tag).strip() for tag in raw_tags if str(tag).strip()]
    if isinstance(raw_tags, str):
        return [tag.strip() for tag in raw_tags.split("|") if tag.strip()]
    return []


def verify_readme_eval_contract() -> dict[str, Any]:
    text = README_PATH.read_text(encoding="utf-8")
    contract: dict[str, Any] = {}
    for key, expected in README_EVAL_CONTRACT.items():
        needle = f"{key}\t"
        matched = False
        for line in text.splitlines():
            if not line.startswith(needle):
                continue
            raw = line.split("\t", 1)[1].strip()
            if isinstance(expected, int) and not isinstance(expected, bool):
                contract[key] = int(raw)
            elif isinstance(expected, float):
                contract[key] = float(raw)
            else:
                contract[key] = raw
            matched = True
            break
        if not matched:
            raise SystemExit(f"Missing README.md evaluation row for {key}")
        if contract[key] != expected:
            raise SystemExit(
                f"README.md evaluation mismatch for {key}: expected {expected}, got {contract[key]}"
            )
    return contract


@lru_cache(maxsize=1)
def get_chat_tokenizer() -> Any:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_TOKENIZER_NAME, trust_remote_code=True)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def tokenize_overlay_example(prompt: str, completion_text: str) -> tuple[list[int], list[int]]:
    chat_tokenizer = get_chat_tokenizer()
    prompt_ids = chat_tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt + PROMPT_SUFFIX}],
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=True,
    )
    completion_ids = chat_tokenizer.encode(completion_text, add_special_tokens=False)
    all_tokens = list(prompt_ids) + list(completion_ids)
    mask = [0] * len(prompt_ids) + [1] * len(completion_ids)
    if len(all_tokens) > TOKEN_LIMIT:
        all_tokens = all_tokens[:TOKEN_LIMIT]
        mask = mask[:TOKEN_LIMIT]
    return all_tokens, mask


def load_base_snapshot_index_rows() -> list[dict[str, Any]]:
    if not BASE_SNAPSHOT_INDEX_PATH.exists():
        raise SystemExit(f"Missing base snapshot index: {BASE_SNAPSHOT_INDEX_PATH}")
    return load_jsonl_rows(BASE_SNAPSHOT_INDEX_PATH)


def load_base_snapshot_examples() -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]], int]:
    config = read_json(BASE_SNAPSHOT_CONFIG_PATH)
    batch_size = int(config["batch_size"])
    base_rows = load_base_snapshot_index_rows()
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for row in base_rows:
        problem_id = str(row["problem_id"])
        segment = str(row["segment"])
        token_path = BASE_SNAPSHOT_ROOT / "tokens" / problem_id / f"{Path(segment).stem}.json"
        if not token_path.exists():
            raise SystemExit(f"Missing base token snapshot: {token_path}")
        payload = read_json(token_path)
        tokens = payload["tokens"]
        mask = payload["mask"]
        num_loss_tokens = int(row["num_loss_tokens"])
        if sum(mask) != num_loss_tokens:
            raise SystemExit(
                f"num_loss_tokens mismatch for base snapshot {problem_id}: {sum(mask)} != {num_loss_tokens}"
            )
        by_key[(problem_id, segment)] = {
            "row": row,
            "tokens": tokens,
            "mask": mask,
        }
    return base_rows, by_key, batch_size


def load_proxy_map(path: Path) -> dict[str, dict[str, str]]:
    return {row["id"]: row for row in load_csv_rows(path)}


def compute_binary_proxy_improvements(base_path: Path, current_path: Path) -> set[str]:
    base_rows = load_proxy_map(base_path)
    current_rows = load_proxy_map(current_path)
    improved: set[str] = set()
    for row_id in sorted(set(base_rows) & set(current_rows)):
        if current_rows[row_id].get("family_short") != "binary":
            continue
        base_correct = base_rows[row_id].get("is_correct") == "True"
        current_correct = current_rows[row_id].get("is_correct") == "True"
        if (not base_correct) and current_correct:
            improved.add(row_id)
    return improved


def load_numeral_no_box_ids() -> set[str]:
    ids: set[str] = set()
    for row in load_csv_rows(RESULT_V6_NUMERAL_MISTAKES_PATH):
        output = row.get("output", "")
        if "\\boxed{" not in output:
            ids.add(row["id"])
    return ids


def require_non_empty_string(raw: dict[str, Any], key: str, row_id: str) -> str:
    value = str(raw.get(key, "")).strip()
    if not value:
        raise SystemExit(f"Missing {key} for overlay row {row_id}")
    return value


def default_assistant_style(bucket: str) -> str:
    if bucket.startswith("surface_") or bucket == "easy_gravity_fragile":
        return "legacy_v4_surface_trace"
    return "legacy_v4_long_trace"


def default_supervision_role(bucket: str) -> str:
    if bucket.startswith("surface_") or bucket == "easy_gravity_fragile":
        return "lane4_surface_stabilizer"
    return "lane1_v4_public_base"


def resolve_assistant_style(raw: dict[str, Any], source_mix: str, raw_bucket: str, row_id: str) -> str:
    explicit = str(raw.get("assistant_style", "")).strip()
    if explicit:
        return explicit
    if source_mix == "v4_public_base":
        return default_assistant_style(raw_bucket)
    raise SystemExit(f"Missing assistant_style for overlay row {row_id}")


def resolve_supervision_role(raw: dict[str, Any], source_mix: str, raw_bucket: str, row_id: str) -> str:
    explicit = str(raw.get("supervision_role", "")).strip()
    if explicit:
        return explicit
    if source_mix == "v4_public_base":
        return default_supervision_role(raw_bucket)
    raise SystemExit(f"Missing supervision_role for overlay row {row_id}")


def normalize_bucket(bucket: str, source_mix: str) -> str:
    if source_mix == "v6_binary_donor":
        mapping = {
            "binary_structured_exact_core": "binary_structured_donor_exact",
            "binary_logic_exact": "binary_logic_donor_exact",
            "binary_permutation_exact": "binary_permutation_donor_exact",
            "binary_prompt_local_exact": "binary_prompt_local_donor_exact",
        }
        return mapping.get(bucket, bucket)
    if source_mix == "v6_numeral_surface_donor":
        return "surface_numeral_boxed_donor"
    return bucket


def normalize_overlay_row(raw: dict[str, Any], source_mix: str) -> dict[str, Any]:
    row_id = require_non_empty_string(raw, "id", "<unknown>")
    raw_bucket = require_non_empty_string(raw, "bucket", row_id)
    category = require_non_empty_string(raw, "category", row_id)
    prompt = require_non_empty_string(raw, "prompt", row_id)
    answer = require_non_empty_string(raw, "answer", row_id)
    completion_text = require_non_empty_string(raw, "completion_text", row_id)
    assistant_style = resolve_assistant_style(raw, source_mix, raw_bucket, row_id)
    supervision_role = resolve_supervision_role(raw, source_mix, raw_bucket, row_id)
    bucket = normalize_bucket(raw_bucket, source_mix)
    source_tags = normalize_tags(raw.get("source_tags", []))
    source_tags.append(source_mix)
    source_tags = sorted(set(source_tags))
    return {
        "id": row_id,
        "category": category,
        "bucket": bucket,
        "prompt": prompt,
        "answer": answer,
        "completion_text": completion_text,
        "assistant_style": assistant_style,
        "supervision_role": supervision_role,
        "selection_tier": str(raw.get("selection_tier", "")),
        "template_subtype": str(raw.get("template_subtype", "")),
        "teacher_solver_candidate": str(raw.get("teacher_solver_candidate", "")),
        "source_tags": source_tags,
        "source_mix": source_mix,
        "proxy_failed": normalize_bool(raw.get("proxy_failed", False)),
        "validation_failed": normalize_bool(raw.get("validation_failed", False)),
        "hard_score": float(raw.get("hard_score", 0.0) or 0.0),
        "audit_reasons": str(raw.get("audit_reasons", "")),
        "analysis_notes": str(raw.get("analysis_notes", "")),
        "symbol_query_operator": str(raw.get("symbol_query_operator", "")),
    }


def build_overlay_mix() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    v4_rows = load_jsonl_rows(V4_REPEATED_PATH)
    v6_rows = load_jsonl_rows(V6_REPEATED_PATH)
    v4_to_v6_binary_improved = compute_binary_proxy_improvements(RESULT_V4_PROXY_PATH, RESULT_V6_PROXY_PATH)
    v20_to_v6_binary_improved = compute_binary_proxy_improvements(RESULT_V20_PROXY_PATH, RESULT_V6_PROXY_PATH)
    measured_numeral_no_box_ids = load_numeral_no_box_ids()

    donor_binary_ids = sorted(MANUAL_BINARY_DONOR_IDS)
    requested_numeral_surface_ids = sorted(V7_NUMERAL_SURFACE_IDS)

    unexpected_numeral_ids = sorted(V7_NUMERAL_SURFACE_IDS - measured_numeral_no_box_ids)
    if unexpected_numeral_ids:
        raise SystemExit(
            "Pinned v7 numeral surface IDs are not present in the measured v6 no-box set: "
            f"{unexpected_numeral_ids}"
        )

    selected_rows: list[dict[str, Any]] = []
    existing_signatures: set[tuple[str, str, str]] = set()
    duplicate_skips: Counter[str] = Counter()
    source_mix_counts: Counter[str] = Counter()

    def append_base_row(raw: dict[str, Any], source_mix: str) -> None:
        normalized = normalize_overlay_row(raw, source_mix)
        signature = (normalized["id"], normalized["bucket"], normalized["completion_text"])
        selected_rows.append(normalized)
        existing_signatures.add(signature)
        source_mix_counts[source_mix] += 1

    def append_row(raw: dict[str, Any], source_mix: str) -> bool:
        normalized = normalize_overlay_row(raw, source_mix)
        signature = (normalized["id"], normalized["bucket"], normalized["completion_text"])
        if signature in existing_signatures:
            duplicate_skips[source_mix] += 1
            raise SystemExit(
                f"Duplicate overlay signature for {source_mix}: {normalized['id']} {normalized['bucket']}"
            )
        selected_rows.append(normalized)
        existing_signatures.add(signature)
        source_mix_counts[source_mix] += 1
        return True

    for raw in v4_rows:
        append_base_row(raw, "v4_public_base")

    donor_binary_ids_present: set[str] = set()
    for raw in v6_rows:
        row_id = str(raw["id"])
        bucket = str(raw["bucket"])
        if row_id not in donor_binary_ids:
            continue
        if not bucket.startswith("binary_"):
            continue
        if append_row(raw, "v6_binary_donor"):
            donor_binary_ids_present.add(row_id)

    missing_binary_donor_ids = sorted(set(donor_binary_ids) - donor_binary_ids_present)
    if missing_binary_donor_ids:
        raise SystemExit(f"Missing pinned v7 binary donor rows in v6 artifacts: {missing_binary_donor_ids}")

    numeral_surface_ids_present: set[str] = set()
    for raw in v6_rows:
        row_id = str(raw["id"])
        if row_id not in V7_NUMERAL_SURFACE_IDS:
            continue
        if str(raw["bucket"]) != "surface_numeral_boxed":
            continue
        if append_row(raw, "v6_numeral_surface_donor"):
            numeral_surface_ids_present.add(row_id)

    missing_v6_numeral_surface_ids = sorted(V7_NUMERAL_SURFACE_IDS - numeral_surface_ids_present)
    explicit_synthetic_numeral_ids: list[str] = []
    for row_id in missing_v6_numeral_surface_ids:
        synthetic_row = V7_EXPLICIT_SYNTHETIC_ROWS.get(row_id)
        if synthetic_row is None:
            raise SystemExit(
                "Missing pinned v7 numeral donor row without an explicitly pinned synthetic replacement: "
                f"{row_id}"
            )
        if append_row(synthetic_row, "v7_numeral_surface_synth"):
            numeral_surface_ids_present.add(row_id)
            explicit_synthetic_numeral_ids.append(row_id)

    remaining_missing_numeral_surface_ids = sorted(V7_NUMERAL_SURFACE_IDS - numeral_surface_ids_present)
    if remaining_missing_numeral_surface_ids:
        raise SystemExit(
            f"Failed to realize the pinned v7 numeral surface set: {remaining_missing_numeral_surface_ids}"
        )

    if set(V7_EXPLICIT_SYNTHETIC_ROWS) - V7_NUMERAL_SURFACE_IDS:
        raise SystemExit("Synthetic v7 numeral rows must be a subset of the pinned numeral surface IDs")

    overlay_instance_by_id: defaultdict[str, int] = defaultdict(int)
    for row in selected_rows:
        overlay_instance_by_id[row["id"]] += 1
        row["overlay_instance"] = overlay_instance_by_id[row["id"]]
    repeat_counts_by_id = dict(overlay_instance_by_id)
    for row in selected_rows:
        row["recommended_repeat_count"] = repeat_counts_by_id[row["id"]]

    diagnostics = {
        "v4_to_v6_binary_proxy_improved_ids": sorted(v4_to_v6_binary_improved),
        "v20_to_v6_binary_proxy_improved_ids": sorted(v20_to_v6_binary_improved),
        "manual_binary_donor_ids": sorted(MANUAL_BINARY_DONOR_IDS),
        "selected_binary_donor_ids": sorted(donor_binary_ids_present),
        "requested_binary_donor_ids": donor_binary_ids,
        "selected_numeral_surface_ids": sorted(numeral_surface_ids_present),
        "requested_numeral_surface_ids": requested_numeral_surface_ids,
        "measured_v6_numeral_no_box_ids": sorted(measured_numeral_no_box_ids),
        "missing_v6_numeral_surface_ids": missing_v6_numeral_surface_ids,
        "explicit_synthetic_numeral_ids": explicit_synthetic_numeral_ids,
        "source_mix_counts": dict(sorted(source_mix_counts.items())),
        "duplicate_skips": dict(sorted(duplicate_skips.items())),
    }
    return selected_rows, diagnostics


def build_unique_rows(repeated_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in repeated_rows:
        key = (row["id"], row["bucket"])
        entry = grouped.get(key)
        if entry is None:
            entry = {
                "id": row["id"],
                "category": row["category"],
                "bucket": row["bucket"],
                "selection_tier": row["selection_tier"],
                "template_subtype": row["template_subtype"],
                "teacher_solver_candidate": row["teacher_solver_candidate"],
                "recommended_repeat_count": 0,
                "assistant_styles": set(),
                "source_mixes": set(),
                "proxy_failed": False,
                "validation_failed": False,
                "hard_score": row["hard_score"],
                "source_tags": set(),
            }
            grouped[key] = entry
        entry["recommended_repeat_count"] += 1
        entry["assistant_styles"].add(row["assistant_style"])
        entry["source_mixes"].add(row["source_mix"])
        entry["proxy_failed"] = entry["proxy_failed"] or bool(row["proxy_failed"])
        entry["validation_failed"] = entry["validation_failed"] or bool(row["validation_failed"])
        entry["source_tags"].update(row["source_tags"])

    unique_rows: list[dict[str, Any]] = []
    for entry in grouped.values():
        unique_rows.append(
            {
                "id": entry["id"],
                "category": entry["category"],
                "bucket": entry["bucket"],
                "selection_tier": entry["selection_tier"],
                "template_subtype": entry["template_subtype"],
                "teacher_solver_candidate": entry["teacher_solver_candidate"],
                "recommended_repeat_count": entry["recommended_repeat_count"],
                "assistant_styles": "|".join(sorted(entry["assistant_styles"])),
                "source_mixes": "|".join(sorted(entry["source_mixes"])),
                "proxy_failed": entry["proxy_failed"],
                "validation_failed": entry["validation_failed"],
                "hard_score": entry["hard_score"],
                "source_tags": "|".join(sorted(entry["source_tags"])),
            }
        )
    return sorted(unique_rows, key=lambda row: (row["bucket"], row["id"]))


def build_markdown_report(summary: dict[str, Any]) -> str:
    lines = [
        "# v20 corrective corpus v7 mainline overlay report",
        "",
        "## Strategy",
        "",
        "- Keep the v4 public-safe overlay as the base.",
        "- Borrow only the pinned binary donor rows from v6.",
        "- Add only the pinned numeral boxed-surface reinforcement set.",
        "- The only allowed synthetic backfill is the explicitly pinned row 1542039b.",
        "- Avoid broad new symbol or cryptarithm expansion.",
        "- Fail fast if source artifacts drift from the pinned v7 definition.",
        "",
        "## Overlay mix",
        "",
    ]
    for source_mix, count in sorted(summary["source_mix_counts"].items()):
        lines.append(f"- {source_mix}: {count}")
    lines.extend([
        "",
        "## Donor binary IDs",
        "",
        f"- selected: {', '.join(summary['diagnostics']['selected_binary_donor_ids']) if summary['diagnostics']['selected_binary_donor_ids'] else '(none)'}",
        "",
        "## Numeral boxed-surface IDs",
        "",
        f"- selected: {', '.join(summary['diagnostics']['selected_numeral_surface_ids']) if summary['diagnostics']['selected_numeral_surface_ids'] else '(none)'}",
        "",
        "## Footprint",
        "",
        f"- overlay token strategy: {summary['training_bundle'].get('overlay_token_strategy', 'unknown')}",
        f"- overlay reuse scope: {summary['training_bundle'].get('overlay_reuse_scope', 'unknown')}",
        f"- reused base synthetic examples: {summary['training_bundle'].get('reused_base_synthetic_example_count', 0)}",
        f"- retokenized overlay examples: {summary['training_bundle'].get('retokenized_overlay_example_count', 0)}",
        f"- unique rows: {summary['selected_unique_rows']}",
        f"- repeated rows: {summary['selected_repeated_rows']}",
        f"- total tokens: {summary['training_bundle']['total_tokens']}",
        f"- total steps: {summary['training_bundle']['total_steps']}",
        f"- max seq len: {summary['training_bundle']['max_seq_len']}",
    ])
    return "\n".join(lines) + "\n"


def build_training_bundle(
    repeated_rows: list[dict[str, Any]],
    bundle_path: Path,
    overlay_token_strategy: str,
) -> dict[str, Any]:
    if overlay_token_strategy not in OVERLAY_TOKEN_STRATEGIES:
        raise SystemExit(
            f"Unsupported overlay token strategy: {overlay_token_strategy}. "
            f"Expected one of {sorted(OVERLAY_TOKEN_STRATEGIES)}"
        )
    base_rows, base_examples, batch_size = load_base_snapshot_examples()
    filtered_base_rows = [
        row for row in base_rows if str(row["problem_id"]).split("-p")[0] not in BASE_EXCLUDED_IDS
    ]
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    existing_steps = [int(row["step"]) for row in filtered_base_rows]
    base_step_count = max(existing_steps) + 1 if existing_steps else 0

    total_examples = 0
    total_tokens = 0
    total_masked_tokens = 0
    total_unmasked_tokens = 0
    max_seq_len = 0
    category_counts: Counter[str] = Counter()
    overlay_by_bucket: Counter[str] = Counter()
    overlay_tokens_by_bucket: Counter[str] = Counter()
    overlay_examples_by_style: Counter[str] = Counter()
    source_mix_counts: Counter[str] = Counter()
    reused_base_synthetic_ids: set[str] = set()
    reused_base_synthetic_by_source_mix: Counter[str] = Counter()
    reused_base_synthetic_example_count = 0
    retokenized_overlay_ids: set[str] = set()
    retokenized_overlay_by_source_mix: Counter[str] = Counter()
    retokenized_overlay_example_count = 0
    synthetic_cache: dict[tuple[str, str], tuple[list[int], list[int], int]] = {}

    manifest = {
        "record_type": "manifest",
        "bundle_format": "nemotron_single_file_training_bundle_v1",
        "version": "v20_corrective_corpus_v7_mainline",
        "created_at": utc_now(),
        "base_snapshot_root": relative_to_repo(BASE_SNAPSHOT_ROOT),
        "base_snapshot_config": read_json(BASE_SNAPSHOT_CONFIG_PATH),
        "bundle_path": relative_to_repo(bundle_path),
        "base_excluded_problem_ids": sorted(BASE_EXCLUDED_IDS),
        "pinned_binary_donor_ids": sorted(MANUAL_BINARY_DONOR_IDS),
        "pinned_numeral_surface_ids": sorted(V7_NUMERAL_SURFACE_IDS),
        "explicit_synthetic_numeral_ids": sorted(V7_EXPLICIT_SYNTHETIC_ROWS),
        "overlay_token_strategy": overlay_token_strategy,
        "overlay_reuse_scope": (
            "v4_public_base_only" if overlay_token_strategy == "reuse_base_synthetic" else "none"
        ),
        "note": (
            "Single-file training bundle for Kaggle upload. "
            "Starts from the v4 public-safe overlay, adds a pinned v6 binary donor pack, "
            "and realizes the pinned v7 numeral boxed-surface set without dynamic donor discovery."
        ),
    }

    with bundle_path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(manifest, ensure_ascii=False) + "\n")

        for row in filtered_base_rows:
            problem_id = str(row["problem_id"])
            segment = str(row["segment"])
            entry = base_examples[(problem_id, segment)]
            tokens = entry["tokens"]
            mask = entry["mask"]
            category = str(row["category"])
            payload = {
                "record_type": "example",
                "example_id": problem_id,
                "source_problem_id": problem_id,
                "source": "base_snapshot",
                "segment": segment,
                "category": category,
                "step": int(row["step"]),
                "num_loss_tokens": int(row["num_loss_tokens"]),
                "tokens": tokens,
                "mask": mask,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            total_examples += 1
            total_tokens += len(tokens)
            total_masked_tokens += sum(1 for value in mask if value == 0)
            total_unmasked_tokens += sum(1 for value in mask if value == 1)
            max_seq_len = max(max_seq_len, len(tokens))
            category_counts[category] += 1

        for overlay_offset, row in enumerate(repeated_rows):
            problem_id = str(row["id"])
            segment = "synthetic.jsonl"
            key = (problem_id, segment)
            source_mix = str(row["source_mix"])
            should_reuse_base_synthetic = (
                overlay_token_strategy == "reuse_base_synthetic"
                and source_mix == "v4_public_base"
                and key in base_examples
            )
            if should_reuse_base_synthetic:
                entry = base_examples[key]
                base_row = entry["row"]
                tokens = entry["tokens"]
                mask = entry["mask"]
                category = str(base_row["category"])
                num_loss_tokens = int(base_row["num_loss_tokens"])
                reused_base_synthetic_ids.add(problem_id)
                reused_base_synthetic_by_source_mix[source_mix] += 1
                reused_base_synthetic_example_count += 1
            else:
                cache_key = (problem_id, str(row["completion_text"]))
                if cache_key not in synthetic_cache:
                    tokens, mask = tokenize_overlay_example(
                        prompt=str(row["prompt"]),
                        completion_text=str(row["completion_text"]),
                    )
                    synthetic_cache[cache_key] = (tokens, mask, sum(mask))
                tokens, mask, num_loss_tokens = synthetic_cache[cache_key]
                category = str(row["category"])
                retokenized_overlay_ids.add(problem_id)
                retokenized_overlay_by_source_mix[source_mix] += 1
                retokenized_overlay_example_count += 1
            overlay_step = base_step_count + (overlay_offset // batch_size)
            payload = {
                "record_type": "example",
                "example_id": f"{problem_id}#overlay-{row['overlay_instance']}",
                "source_problem_id": problem_id,
                "source": "corrective_overlay",
                "segment": segment,
                "category": category,
                "step": overlay_step,
                "num_loss_tokens": num_loss_tokens,
                "bucket": row["bucket"],
                "overlay_instance": int(row["overlay_instance"]),
                "assistant_style": row["assistant_style"],
                "supervision_role": row["supervision_role"],
                "recommended_repeat_count": int(row["recommended_repeat_count"]),
                "proxy_failed": bool(row["proxy_failed"]),
                "validation_failed": bool(row["validation_failed"]),
                "source_tags": row["source_tags"],
                "source_mix": source_mix,
                "tokens": tokens,
                "mask": mask,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
            total_examples += 1
            total_tokens += len(tokens)
            total_masked_tokens += sum(1 for value in mask if value == 0)
            total_unmasked_tokens += sum(1 for value in mask if value == 1)
            max_seq_len = max(max_seq_len, len(tokens))
            category_counts[category] += 1
            overlay_by_bucket[row["bucket"]] += 1
            overlay_tokens_by_bucket[row["bucket"]] += len(tokens)
            overlay_examples_by_style[row["assistant_style"]] += 1
            source_mix_counts[source_mix] += 1

    total_steps = base_step_count + ((len(repeated_rows) + batch_size - 1) // batch_size)
    return {
        "path": relative_to_repo(bundle_path),
        "base_snapshot_root": relative_to_repo(BASE_SNAPSHOT_ROOT),
        "format": "nemotron_single_file_training_bundle_v1",
        "base_examples": len(filtered_base_rows),
        "base_excluded_problem_ids": sorted(BASE_EXCLUDED_IDS),
        "overlay_examples": len(repeated_rows),
        "total_examples": total_examples,
        "batch_size": batch_size,
        "total_steps": total_steps,
        "overlay_token_strategy": overlay_token_strategy,
        "overlay_reuse_scope": (
            "v4_public_base_only" if overlay_token_strategy == "reuse_base_synthetic" else "none"
        ),
        "total_tokens": total_tokens,
        "total_masked_tokens": total_masked_tokens,
        "total_unmasked_tokens": total_unmasked_tokens,
        "max_seq_len": max_seq_len,
        "overlay_by_bucket": dict(sorted(overlay_by_bucket.items())),
        "overlay_tokens_by_bucket": dict(sorted(overlay_tokens_by_bucket.items())),
        "overlay_examples_by_style": dict(sorted(overlay_examples_by_style.items())),
        "source_mix_counts": dict(sorted(source_mix_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "reused_base_synthetic_problem_ids": sorted(reused_base_synthetic_ids),
        "reused_base_synthetic_problem_count": len(reused_base_synthetic_ids),
        "reused_base_synthetic_by_source_mix": dict(sorted(reused_base_synthetic_by_source_mix.items())),
        "reused_base_synthetic_example_count": reused_base_synthetic_example_count,
        "retokenized_overlay_problem_ids": sorted(retokenized_overlay_ids),
        "retokenized_overlay_problem_count": len(retokenized_overlay_ids),
        "retokenized_overlay_by_source_mix": dict(sorted(retokenized_overlay_by_source_mix.items())),
        "retokenized_overlay_example_count": retokenized_overlay_example_count,
    }


def build_summary(
    run_name: str,
    repeated_rows: list[dict[str, Any]],
    unique_rows: list[dict[str, Any]],
    diagnostics: dict[str, Any],
    training_bundle: dict[str, Any],
) -> dict[str, Any]:
    selected_by_bucket = Counter(row["bucket"] for row in unique_rows)
    repeated_by_bucket = Counter(row["bucket"] for row in repeated_rows)
    source_mix_counts = Counter(row["source_mix"] for row in repeated_rows)
    return {
        "version": "v20_corrective_corpus_v7_mainline",
        "run_name": run_name,
        "created_at": utc_now(),
        "readme_eval_contract": verify_readme_eval_contract(),
        "strategy_source": "versions/v20_to_088_reassessment_2026-04-18.md + v4/v6 measured results",
        "parents": {
            "v4_public": "0.85-0.86",
            "v6_public": "0.83-0.85",
            "v4_validation": "813/950",
            "v6_validation": "829/950",
            "v4_proxy": "179/200",
            "v6_proxy": "180/200",
        },
        "inputs": {
            "v4_repeated_overlay": relative_to_repo(V4_REPEATED_PATH),
            "v4_selection": relative_to_repo(V4_SELECTION_PATH),
            "v4_summary": relative_to_repo(V4_SUMMARY_PATH),
            "v6_repeated_overlay": relative_to_repo(V6_REPEATED_PATH),
            "v6_selection": relative_to_repo(V6_SELECTION_PATH),
            "v6_summary": relative_to_repo(V6_SUMMARY_PATH),
            "v20_proxy_row_level": relative_to_repo(RESULT_V20_PROXY_PATH),
            "v4_proxy_row_level": relative_to_repo(RESULT_V4_PROXY_PATH),
            "v6_proxy_row_level": relative_to_repo(RESULT_V6_PROXY_PATH),
            "v6_numeral_mistakes": relative_to_repo(RESULT_V6_NUMERAL_MISTAKES_PATH),
        },
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(selected_by_bucket.items())),
        "repeated_by_bucket": dict(sorted(repeated_by_bucket.items())),
        "source_mix_counts": dict(sorted(source_mix_counts.items())),
        "diagnostics": diagnostics,
        "training_bundle": training_bundle,
    }


def write_report_files(run_root: Path, repeated_rows: list[dict[str, Any]], unique_rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    artifacts_dir = run_root / "artifacts"
    reports_dir = run_root / "reports"
    write_jsonl(artifacts_dir / "corrective_overlay_repeated.jsonl", repeated_rows)
    write_jsonl(artifacts_dir / "corrective_overlay_unique.jsonl", unique_rows)
    write_csv(
        artifacts_dir / "corrective_selection.csv",
        unique_rows,
        fieldnames=[
            "id",
            "category",
            "bucket",
            "selection_tier",
            "template_subtype",
            "teacher_solver_candidate",
            "recommended_repeat_count",
            "assistant_styles",
            "source_mixes",
            "proxy_failed",
            "validation_failed",
            "hard_score",
            "source_tags",
        ],
    )
    write_json(artifacts_dir / "corrective_overlay_summary.json", summary)
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "corrective_overlay_report.md").write_text(build_markdown_report(summary), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build v7 mixed overlay from v4 public base and v6 donors.")
    parser.add_argument("--run-name", default="v7_mainline_default")
    parser.add_argument("--write-training-bundle", action="store_true")
    parser.add_argument("--bundle-path", default=str(DEFAULT_BUNDLE_PATH))
    parser.add_argument(
        "--overlay-token-strategy",
        choices=sorted(OVERLAY_TOKEN_STRATEGIES),
        default="reuse_base_synthetic",
        help=(
            "How to construct overlay token streams. Historical broken v7 behavior was effectively "
            "retokenize_all; corrected reproduction should use reuse_base_synthetic, which only "
            "reuses base-backed token streams for v4_public_base rows and retokenizes donor/synth rows "
            "from their own text."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_root = OUTPUT_ROOT / args.run_name
    repeated_rows, diagnostics = build_overlay_mix()
    unique_rows = build_unique_rows(repeated_rows)
    training_bundle = {
        "path": relative_to_repo(Path(args.bundle_path)),
        "status": "skipped",
        "overlay_token_strategy": args.overlay_token_strategy,
    }
    if args.write_training_bundle:
        training_bundle = build_training_bundle(
            repeated_rows,
            Path(args.bundle_path),
            args.overlay_token_strategy,
        )
    summary = build_summary(args.run_name, repeated_rows, unique_rows, diagnostics, training_bundle)
    write_report_files(run_root, repeated_rows, unique_rows, summary)
    print(json.dumps({
        "run_root": relative_to_repo(run_root),
        "selected_unique_rows": summary["selected_unique_rows"],
        "selected_repeated_rows": summary["selected_repeated_rows"],
        "source_mix_counts": summary["source_mix_counts"],
        "bundle": training_bundle,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()