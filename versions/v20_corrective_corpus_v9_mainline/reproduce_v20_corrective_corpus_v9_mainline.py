from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
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
README_PATH = REPO_ROOT / "README.md"
RESULTS_MD = VERSION_ROOT / "v20_corrective_corpus_v9_mainline-results.md"

TRAINING_SFT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "training" / "sft"
BASE_SNAPSHOT_ROOT = TRAINING_SFT_ROOT / "04-08-16-14"
BASE_SNAPSHOT_CONFIG_PATH = BASE_SNAPSHOT_ROOT / "config.json"
BASE_SNAPSHOT_INDEX_PATH = BASE_SNAPSHOT_ROOT / "logprobs" / "index.jsonl"
DEFAULT_BUNDLE_PATH = TRAINING_SFT_ROOT / "v20_corrective_corpus_v9_mainline_bundle.jsonl"

V7_OUTPUT_ROOT = REPO_ROOT / "versions" / "v20_corrective_corpus_v7_mainline" / "outputs" / "v7_mainline_default"
V7_REPEATED_PATH = V7_OUTPUT_ROOT / "artifacts" / "corrective_overlay_repeated.jsonl"
V7_UNIQUE_PATH = V7_OUTPUT_ROOT / "artifacts" / "corrective_overlay_unique.jsonl"
V7_SUMMARY_PATH = V7_OUTPUT_ROOT / "artifacts" / "corrective_overlay_summary.json"

REASONING_DIR = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "reasoning"
MODEL_TOKENIZER_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"

PROMPT_SUFFIX = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)
TOKEN_LIMIT = 8192
OVERLAY_TOKEN_STRATEGIES = {"reuse_base_synthetic", "retokenize_all"}
PROMPT_SUFFIX_MODES = {"boxed_final_answer", "none"}
BASE_EXCLUDED_IDS = {"ef2fe526"}

MATCHING_SECTION_NAMES = [
    "Identity",
    "NOT",
    "Constant",
    "AND",
    "OR",
    "XOR",
    "AND-NOT",
    "OR-NOT",
    "XOR-NOT",
]
MATCHING_BEST_PREFIX = {
    "Identity": "I",
    "NOT": "NOT",
    "Constant": "C",
    "AND": "AND",
    "OR": "OR",
    "XOR": "XOR",
    "AND-NOT": "AND-NOT",
    "OR-NOT": "OR-NOT",
    "XOR-NOT": "XOR-NOT",
}
MATCHING_PROMPT_PREFIX = (
    "In Alice's Wonderland, secret processing rules are used on text.\n\n"
    "x: not matched anywhere\n"
    "y: matched but wrong position\n\n"
)
MATCHING_SOURCE_MIX = "v9_bit_matching_aux"
MATCHING_ASSISTANT_STYLE = "aopen_matching_aux"
MATCHING_SUPERVISION_ROLE = "lane0_bit_matching_aux"
MATCHING_SELECTION_TIER = "v9_matching_aux"
MATCHING_TEMPLATE_SUBTYPE = "matching_section"
MATCHING_TEACHER_SOLVER = "aopen_matching_section"
EXPECTED_V7_SOURCE_MIX_COUNTS = {
    "v4_public_base": 808,
    "v6_binary_donor": 27,
    "v6_numeral_surface_donor": 10,
    "v7_numeral_surface_synth": 1,
}
EXPECTED_V7_BINARY_UNIQUE_IDS = 240

README_EVAL_CONTRACT = {
    "max_lora_rank": 32,
    "max_tokens": 7680,
    "top_p": 1.0,
    "temperature": 0.0,
    "max_num_seqs": 64,
    "gpu_memory_utilization": 0.85,
    "max_model_len": 8192,
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


def require_non_empty_string(raw: dict[str, Any], key: str, row_id: str) -> str:
    value = str(raw.get(key, "")).strip()
    if not value:
        raise SystemExit(f"Missing {key} for overlay row {row_id}")
    return value


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


def tokenize_overlay_example(
    prompt: str,
    completion_text: str,
    prompt_suffix_mode: str,
) -> tuple[list[int], list[int]]:
    if prompt_suffix_mode not in PROMPT_SUFFIX_MODES:
        raise SystemExit(f"Unsupported prompt suffix mode: {prompt_suffix_mode}")
    chat_tokenizer = get_chat_tokenizer()
    suffix = PROMPT_SUFFIX if prompt_suffix_mode == "boxed_final_answer" else ""
    prompt_ids = chat_tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt + suffix}],
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


def normalize_overlay_row(raw: dict[str, Any], source_mix_override: str | None = None) -> dict[str, Any]:
    row_id = require_non_empty_string(raw, "id", "<unknown>")
    category = require_non_empty_string(raw, "category", row_id)
    bucket = require_non_empty_string(raw, "bucket", row_id)
    prompt = require_non_empty_string(raw, "prompt", row_id)
    answer = require_non_empty_string(raw, "answer", row_id)
    completion_text = require_non_empty_string(raw, "completion_text", row_id)
    source_mix = source_mix_override or require_non_empty_string(raw, "source_mix", row_id)
    prompt_suffix_mode = str(raw.get("prompt_suffix_mode", "boxed_final_answer")).strip() or "boxed_final_answer"
    if prompt_suffix_mode not in PROMPT_SUFFIX_MODES:
        raise SystemExit(f"Unsupported prompt_suffix_mode for {row_id}: {prompt_suffix_mode}")
    source_tags = normalize_tags(raw.get("source_tags", []))
    source_tags.append(source_mix)
    origin_problem_id = str(raw.get("origin_problem_id", row_id)).strip() or row_id
    return {
        "id": row_id,
        "origin_problem_id": origin_problem_id,
        "category": category,
        "bucket": bucket,
        "prompt": prompt,
        "answer": answer,
        "completion_text": completion_text,
        "assistant_style": require_non_empty_string(raw, "assistant_style", row_id),
        "supervision_role": require_non_empty_string(raw, "supervision_role", row_id),
        "selection_tier": str(raw.get("selection_tier", "")),
        "template_subtype": str(raw.get("template_subtype", "")),
        "teacher_solver_candidate": str(raw.get("teacher_solver_candidate", "")),
        "source_tags": sorted(set(source_tags)),
        "source_mix": source_mix,
        "prompt_suffix_mode": prompt_suffix_mode,
        "proxy_failed": normalize_bool(raw.get("proxy_failed", False)),
        "validation_failed": normalize_bool(raw.get("validation_failed", False)),
        "hard_score": float(raw.get("hard_score", 0.0) or 0.0),
        "audit_reasons": str(raw.get("audit_reasons", "")),
        "analysis_notes": str(raw.get("analysis_notes", "")),
        "symbol_query_operator": str(raw.get("symbol_query_operator", "")),
    }


def slugify_section(section_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", section_name.lower()).strip("_")


def extract_matching_section_block(lines: list[str], start: int, end: int) -> dict[str, Any] | None:
    mo_idx = None
    for idx in range(start, end):
        if lines[idx].strip() == "Matching output":
            mo_idx = idx
            break
    if mo_idx is None:
        return None

    mo_lines: list[str] = []
    for idx in range(mo_idx + 1, end):
        stripped = lines[idx].strip()
        if stripped == "" or stripped == "Left":
            break
        mo_lines.append(lines[idx])

    left_idx = None
    for idx in range(mo_idx + 1, end):
        if lines[idx].strip() == "Left":
            left_idx = idx
            break
    if left_idx is None:
        return None

    left_chain: list[str] = []
    best_left = ""
    for idx in range(left_idx + 1, end):
        stripped = lines[idx].strip()
        if stripped.startswith("Best:"):
            best_left = lines[idx]
            break
        if stripped == "":
            break
        left_chain.append(lines[idx])

    right_idx = None
    for idx in range(left_idx + 1, end):
        if lines[idx].strip() == "Right":
            right_idx = idx
            break
    if right_idx is None:
        return None

    right_chain: list[str] = []
    best_right = ""
    for idx in range(right_idx + 1, end):
        stripped = lines[idx].strip()
        if stripped.startswith("Best:"):
            best_right = lines[idx]
            break
        if stripped == "":
            break
        right_chain.append(lines[idx])

    return {
        "mo_lines": mo_lines,
        "left_chain": left_chain,
        "best_left": best_left,
        "right_chain": right_chain,
        "best_right": best_right,
    }


def keep_matching_section(origin_problem_id: str, section_name: str, n_matches: int, left_chain: list[str], right_chain: list[str]) -> bool:
    all_absent = n_matches == 0
    both_none = left_chain == ["none"] and right_chain == ["none"]
    few_matches = n_matches < 4
    digest = int(hashlib.sha256(f"{origin_problem_id}_{section_name}".encode()).hexdigest(), 16)
    if all_absent:
        return (digest % 100) == 0
    if both_none:
        return (digest % 10) == 0
    if few_matches:
        return (digest % 5) < 1
    return True


def build_matching_aux_rows(binary_origin_ids: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected_rows: list[dict[str, Any]] = []
    kept_by_section: Counter[str] = Counter()
    all_by_section: Counter[str] = Counter()
    missing_reasoning_ids: list[str] = []
    all_sections = 0
    kept_sections = 0
    informative_sections = 0
    all_absent_sections = 0
    both_none_sections = 0
    few_match_sections = 0

    for origin_problem_id in binary_origin_ids:
        reasoning_path = REASONING_DIR / f"{origin_problem_id}.txt"
        if not reasoning_path.exists():
            missing_reasoning_ids.append(origin_problem_id)
            continue
        lines = reasoning_path.read_text(encoding="utf-8").split("\n")

        obc_idx = None
        for idx, line in enumerate(lines):
            if line.strip() == "Output bit columns (with bitsum as hash)":
                obc_idx = idx
                break
        if obc_idx is None:
            continue

        selecting_idx = len(lines)
        for idx in range(obc_idx, len(lines)):
            if lines[idx].strip() == "Selecting":
                selecting_idx = idx
                break

        output_bit_column_block = lines[obc_idx + 1 : obc_idx + 9]
        section_positions: list[tuple[str, int]] = []
        for idx in range(obc_idx, selecting_idx):
            stripped = lines[idx].strip()
            if stripped in MATCHING_SECTION_NAMES:
                section_positions.append((stripped, idx))

        for position, (section_name, section_start) in enumerate(section_positions):
            section_end = (
                section_positions[position + 1][1] if position + 1 < len(section_positions) else selecting_idx
            )
            data_lines: list[str] = []
            for idx in range(section_start + 1, section_end):
                if lines[idx].strip() == "Matching output":
                    break
                data_lines.append(lines[idx])
            while data_lines and data_lines[-1].strip() == "":
                data_lines.pop()

            block = extract_matching_section_block(lines, section_start, section_end)
            if block is None:
                continue

            left_chain = list(block["left_chain"])
            right_chain = list(block["right_chain"])
            all_sections += 1
            all_by_section[section_name] += 1

            all_chain_text = " ".join(left_chain + right_chain)
            has_x = bool(re.search(r"\dx", all_chain_text))
            has_y = bool(re.search(r"\dy", all_chain_text))
            n_matches = sum(1 for line in data_lines if "match" in line)
            all_absent = n_matches == 0
            both_none = left_chain == ["none"] and right_chain == ["none"]
            few_matches = n_matches < 4
            if all_absent:
                all_absent_sections += 1
            if both_none:
                both_none_sections += 1
            if few_matches:
                few_match_sections += 1
            if has_x or has_y or (not all_absent and not both_none):
                informative_sections += 1

            if not keep_matching_section(origin_problem_id, section_name, n_matches, left_chain, right_chain):
                continue

            prefix = MATCHING_BEST_PREFIX.get(section_name, section_name)
            best_left = re.sub(rf"^(Best: ){re.escape(prefix)}", r"\1", str(block["best_left"]))
            best_right = re.sub(rf"^(Best: ){re.escape(prefix)}", r"\1", str(block["best_right"]))
            input_text = "\n".join(output_bit_column_block) + "\n\n" + "\n".join(data_lines)
            output_parts = (
                list(block["mo_lines"])
                + ["", "Left"]
                + left_chain
                + [best_left]
                + ["", "Right"]
                + right_chain
                + [best_right]
            )
            output_text = "\n".join(output_parts)
            section_slug = slugify_section(section_name)
            row_id = f"{origin_problem_id}_matching_{section_slug}"
            selected_rows.append(
                {
                    "id": row_id,
                    "origin_problem_id": origin_problem_id,
                    "category": "matching",
                    "bucket": f"matching_aux_{section_slug}",
                    "prompt": MATCHING_PROMPT_PREFIX + input_text,
                    "answer": output_text,
                    "completion_text": f"{output_text}\n</think><|im_end|>",
                    "assistant_style": MATCHING_ASSISTANT_STYLE,
                    "supervision_role": MATCHING_SUPERVISION_ROLE,
                    "selection_tier": MATCHING_SELECTION_TIER,
                    "template_subtype": MATCHING_TEMPLATE_SUBTYPE,
                    "teacher_solver_candidate": MATCHING_TEACHER_SOLVER,
                    "source_tags": [
                        "aopen_matching_style",
                        "bit_matching_aux",
                        f"origin_{origin_problem_id}",
                        f"section_{section_slug}",
                    ],
                    "source_mix": MATCHING_SOURCE_MIX,
                    "prompt_suffix_mode": "none",
                    "proxy_failed": False,
                    "validation_failed": False,
                    "hard_score": 0.0,
                    "audit_reasons": "",
                    "analysis_notes": f"matching_extracted_from_{origin_problem_id}",
                    "symbol_query_operator": "",
                }
            )
            kept_sections += 1
            kept_by_section[section_name] += 1

    diagnostics = {
        "binary_origin_problem_ids": binary_origin_ids,
        "binary_origin_problem_count": len(binary_origin_ids),
        "missing_reasoning_ids": missing_reasoning_ids,
        "missing_reasoning_count": len(missing_reasoning_ids),
        "all_sections": all_sections,
        "kept_sections": kept_sections,
        "informative_sections": informative_sections,
        "all_absent_sections": all_absent_sections,
        "both_none_sections": both_none_sections,
        "few_match_sections": few_match_sections,
        "all_by_section": dict(sorted(all_by_section.items())),
        "kept_by_section": dict(sorted(kept_by_section.items())),
    }
    return selected_rows, diagnostics


def build_overlay_mix() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not V7_REPEATED_PATH.exists():
        raise SystemExit(f"Missing v7 repeated overlay artifact: {V7_REPEATED_PATH}")

    v7_repeated_rows = [normalize_overlay_row(raw) for raw in load_jsonl_rows(V7_REPEATED_PATH)]
    v7_source_mix_counts = Counter(str(row["source_mix"]) for row in v7_repeated_rows)
    if dict(sorted(v7_source_mix_counts.items())) != EXPECTED_V7_SOURCE_MIX_COUNTS:
        raise SystemExit(
            "v7 repeated overlay drifted from the expected token-safe mix: "
            f"{dict(sorted(v7_source_mix_counts.items()))}"
        )

    binary_origin_ids = sorted(
        {
            str(row["origin_problem_id"])
            for row in v7_repeated_rows
            if str(row["category"]) == "bit_manipulation"
        }
    )
    if len(binary_origin_ids) != EXPECTED_V7_BINARY_UNIQUE_IDS:
        raise SystemExit(
            "Unexpected v7 binary unique-id count: "
            f"expected {EXPECTED_V7_BINARY_UNIQUE_IDS}, got {len(binary_origin_ids)}"
        )

    matching_rows, matching_diagnostics = build_matching_aux_rows(binary_origin_ids)
    selected_rows = list(v7_repeated_rows) + matching_rows

    overlay_instance_by_id: defaultdict[str, int] = defaultdict(int)
    for row in selected_rows:
        overlay_instance_by_id[str(row["id"])] += 1
        row["overlay_instance"] = overlay_instance_by_id[str(row["id"])]

    repeat_counts_by_id = dict(overlay_instance_by_id)
    for row in selected_rows:
        row["recommended_repeat_count"] = repeat_counts_by_id[str(row["id"])]

    diagnostics = {
        "v7_source_mix_counts": dict(sorted(v7_source_mix_counts.items())),
        "matching": matching_diagnostics,
        "selected_binary_origin_problem_ids": binary_origin_ids,
        "selected_binary_origin_problem_count": len(binary_origin_ids),
    }
    return selected_rows, diagnostics


def build_unique_rows(repeated_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in repeated_rows:
        key = (str(row["id"]), str(row["bucket"]))
        entry = grouped.get(key)
        if entry is None:
            entry = {
                "id": row["id"],
                "origin_problem_id": row["origin_problem_id"],
                "category": row["category"],
                "bucket": row["bucket"],
                "selection_tier": row["selection_tier"],
                "template_subtype": row["template_subtype"],
                "teacher_solver_candidate": row["teacher_solver_candidate"],
                "recommended_repeat_count": 0,
                "assistant_styles": set(),
                "source_mixes": set(),
                "prompt_suffix_modes": set(),
                "proxy_failed": False,
                "validation_failed": False,
                "hard_score": row["hard_score"],
                "source_tags": set(),
            }
            grouped[key] = entry
        entry["recommended_repeat_count"] += 1
        entry["assistant_styles"].add(row["assistant_style"])
        entry["source_mixes"].add(row["source_mix"])
        entry["prompt_suffix_modes"].add(row["prompt_suffix_mode"])
        entry["proxy_failed"] = entry["proxy_failed"] or bool(row["proxy_failed"])
        entry["validation_failed"] = entry["validation_failed"] or bool(row["validation_failed"])
        entry["source_tags"].update(row["source_tags"])

    unique_rows: list[dict[str, Any]] = []
    for entry in grouped.values():
        unique_rows.append(
            {
                "id": entry["id"],
                "origin_problem_id": entry["origin_problem_id"],
                "category": entry["category"],
                "bucket": entry["bucket"],
                "selection_tier": entry["selection_tier"],
                "template_subtype": entry["template_subtype"],
                "teacher_solver_candidate": entry["teacher_solver_candidate"],
                "recommended_repeat_count": entry["recommended_repeat_count"],
                "assistant_styles": "|".join(sorted(entry["assistant_styles"])),
                "source_mixes": "|".join(sorted(entry["source_mixes"])),
                "prompt_suffix_modes": "|".join(sorted(entry["prompt_suffix_modes"])),
                "proxy_failed": entry["proxy_failed"],
                "validation_failed": entry["validation_failed"],
                "hard_score": entry["hard_score"],
                "source_tags": "|".join(sorted(entry["source_tags"])),
            }
        )
    return sorted(unique_rows, key=lambda row: (str(row["bucket"]), str(row["id"])))


def build_markdown_report(summary: dict[str, Any]) -> str:
    matching_diag = summary["diagnostics"]["matching"]
    lines = [
        "# v20 corrective corpus v9 mainline overlay report",
        "",
        "## Strategy",
        "",
        "- Keep the token-safe v7 donor backbone exactly as the public-safe base overlay.",
        "- Do not add any new broad BIT exact lane beyond the audited v7 donor pack.",
        "- Do not add any new symbol exact lane in the mainline branch.",
        "- Reintroduce only the A-Open-style matching auxiliary curriculum that is absent from the local 04-08-16-14 base snapshot.",
        "- Extract matching sections only from the 240 binary origin IDs already carried by the v7 token-safe overlay.",
        "- Reuse base synthetic token streams only for v4_public_base rows; retokenize donor rows and all matching auxiliaries from their own text.",
        "",
        "## Source mix",
        "",
    ]
    for source_mix, count in sorted(summary["source_mix_counts"].items()):
        lines.append(f"- {source_mix}: {count}")
    lines.extend([
        "",
        "## Matching auxiliary lane",
        "",
        f"- binary origin IDs: {matching_diag['binary_origin_problem_count']}",
        f"- all extracted sections: {matching_diag['all_sections']}",
        f"- informative sections: {matching_diag['informative_sections']}",
        f"- kept sections after A-Open downsampling: {matching_diag['kept_sections']}",
        f"- missing reasoning files: {matching_diag['missing_reasoning_count']}",
        "",
        "### Kept by section",
        "",
    ])
    for section_name, count in sorted(matching_diag["kept_by_section"].items()):
        lines.append(f"- {section_name}: {count}")
    lines.extend([
        "",
        "## Footprint",
        "",
        f"- overlay token strategy: {summary['training_bundle'].get('overlay_token_strategy', 'unknown')}",
        f"- overlay reuse scope: {summary['training_bundle'].get('overlay_reuse_scope', 'unknown')}",
        f"- reused base synthetic examples: {summary['training_bundle'].get('reused_base_synthetic_example_count', 0)}",
        f"- retokenized overlay examples: {summary['training_bundle'].get('retokenized_overlay_example_count', 0)}",
        f"- unique rows: {summary['selected_unique_rows']}",
        f"- repeated rows: {summary['selected_repeated_rows']}",
        f"- total tokens: {summary['training_bundle'].get('total_tokens', 0)}",
        f"- total steps: {summary['training_bundle'].get('total_steps', 0)}",
        f"- max seq len: {summary['training_bundle'].get('max_seq_len', 0)}",
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
    synthetic_cache: dict[tuple[str, str, str], tuple[list[int], list[int], int]] = {}

    manifest = {
        "record_type": "manifest",
        "bundle_format": "nemotron_single_file_training_bundle_v1",
        "version": "v20_corrective_corpus_v9_mainline",
        "created_at": utc_now(),
        "base_snapshot_root": relative_to_repo(BASE_SNAPSHOT_ROOT),
        "base_snapshot_config": read_json(BASE_SNAPSHOT_CONFIG_PATH),
        "bundle_path": relative_to_repo(bundle_path),
        "base_excluded_problem_ids": sorted(BASE_EXCLUDED_IDS),
        "overlay_token_strategy": overlay_token_strategy,
        "overlay_reuse_scope": (
            "v4_public_base_only" if overlay_token_strategy == "reuse_base_synthetic" else "none"
        ),
        "v7_repeated_overlay": relative_to_repo(V7_REPEATED_PATH),
        "note": (
            "Single-file training bundle for Kaggle upload. Inherits the token-safe v7 donor overlay "
            "and adds only A-Open-style matching auxiliary rows, because the local 04-08-16-14 base snapshot "
            "contains competition categories only and does not include matching/spelling/concatenation/splitting/lstrip."
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
            source_problem_id = str(row.get("origin_problem_id", problem_id))
            segment = "synthetic.jsonl"
            source_mix = str(row["source_mix"])
            prompt_suffix_mode = str(row["prompt_suffix_mode"])
            key = (problem_id, segment)
            should_reuse_base_synthetic = (
                overlay_token_strategy == "reuse_base_synthetic"
                and source_mix == "v4_public_base"
                and prompt_suffix_mode == "boxed_final_answer"
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
                cache_key = (problem_id, str(row["completion_text"]), prompt_suffix_mode)
                if cache_key not in synthetic_cache:
                    tokens, mask = tokenize_overlay_example(
                        prompt=str(row["prompt"]),
                        completion_text=str(row["completion_text"]),
                        prompt_suffix_mode=prompt_suffix_mode,
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
                "source_problem_id": source_problem_id,
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
                "prompt_suffix_mode": prompt_suffix_mode,
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
            overlay_by_bucket[str(row["bucket"])] += 1
            overlay_tokens_by_bucket[str(row["bucket"])] += len(tokens)
            overlay_examples_by_style[str(row["assistant_style"])] += 1
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
    selected_by_bucket = Counter(str(row["bucket"]) for row in unique_rows)
    repeated_by_bucket = Counter(str(row["bucket"]) for row in repeated_rows)
    source_mix_counts = Counter(str(row["source_mix"]) for row in repeated_rows)
    category_counts = Counter(str(row["category"]) for row in repeated_rows)
    return {
        "version": "v20_corrective_corpus_v9_mainline",
        "run_name": run_name,
        "created_at": utc_now(),
        "readme_eval_contract": verify_readme_eval_contract(),
        "strategy_source": (
            "A-Open-ProgressPrizePublication/README.md + "
            "cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md + "
            "data/symbol_rule_analysis_2026-04-20/analysis_report.md + "
            "versions/v20_corrective_corpus_v8_mainline/v20_corrective_corpus_v8_mainline_reassessment_2026-04-23.md"
        ),
        "parents": {
            "v4_public": "0.85-0.86",
            "v6_public": "0.83-0.85",
            "v7_1_public": "0.84",
            "v8_public": "0.83-0.84",
            "v4_proxy": "179/200",
            "v6_proxy": "180/200",
            "v7_1_proxy": "178/200",
            "v8_proxy": "178/200",
        },
        "inputs": {
            "v7_repeated_overlay": relative_to_repo(V7_REPEATED_PATH),
            "v7_unique_overlay": relative_to_repo(V7_UNIQUE_PATH),
            "v7_summary": relative_to_repo(V7_SUMMARY_PATH),
            "base_snapshot_root": relative_to_repo(BASE_SNAPSHOT_ROOT),
            "reasoning_dir": relative_to_repo(REASONING_DIR),
        },
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(selected_by_bucket.items())),
        "repeated_by_bucket": dict(sorted(repeated_by_bucket.items())),
        "source_mix_counts": dict(sorted(source_mix_counts.items())),
        "overlay_category_counts": dict(sorted(category_counts.items())),
        "diagnostics": diagnostics,
        "training_bundle": training_bundle,
    }


def write_report_files(
    run_root: Path,
    repeated_rows: list[dict[str, Any]],
    unique_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    artifacts_dir = run_root / "artifacts"
    reports_dir = run_root / "reports"
    write_jsonl(artifacts_dir / "corrective_overlay_repeated.jsonl", repeated_rows)
    write_jsonl(artifacts_dir / "corrective_overlay_unique.jsonl", unique_rows)
    write_csv(
        artifacts_dir / "corrective_selection.csv",
        unique_rows,
        fieldnames=[
            "id",
            "origin_problem_id",
            "category",
            "bucket",
            "selection_tier",
            "template_subtype",
            "teacher_solver_candidate",
            "recommended_repeat_count",
            "assistant_styles",
            "source_mixes",
            "prompt_suffix_modes",
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
    parser = argparse.ArgumentParser(
        description="Build v9 by keeping the token-safe v7 overlay and adding only A-Open-style matching auxiliaries."
    )
    parser.add_argument("--run-name", default="v9_mainline_default")
    parser.add_argument("--write-training-bundle", action="store_true")
    parser.add_argument("--bundle-path", default=str(DEFAULT_BUNDLE_PATH))
    parser.add_argument(
        "--overlay-token-strategy",
        choices=sorted(OVERLAY_TOKEN_STRATEGIES),
        default="reuse_base_synthetic",
        help=(
            "Reuse base-backed token streams only for v4_public_base rows inherited through v7. "
            "All matching auxiliaries and donor rows are retokenized from their own text."
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
    print(
        json.dumps(
            {
                "run_root": relative_to_repo(run_root),
                "selected_unique_rows": summary["selected_unique_rows"],
                "selected_repeated_rows": summary["selected_repeated_rows"],
                "source_mix_counts": summary["source_mix_counts"],
                "overlay_category_counts": summary["overlay_category_counts"],
                "matching_kept_sections": diagnostics["matching"]["kept_sections"],
                "bundle": training_bundle,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()