from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
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
RESULTS_MD = VERSION_ROOT / "v20_corrective_corpus_v10_mainline-results.md"

README_PATH = REPO_ROOT / "README.md"
STRATEGY_NOTE_PATH = REPO_ROOT / "versions" / "v10_bit_mainline_strategy_2026-04-23.md"

TRAINING_SFT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "training" / "sft"
BASE_SNAPSHOT_ROOT = TRAINING_SFT_ROOT / "04-08-16-14"
BASE_SNAPSHOT_CONFIG_PATH = BASE_SNAPSHOT_ROOT / "config.json"
BASE_SNAPSHOT_INDEX_PATH = BASE_SNAPSHOT_ROOT / "logprobs" / "index.jsonl"
DEFAULT_BUNDLE_PATH = TRAINING_SFT_ROOT / "v20_corrective_corpus_v10_mainline_bundle.jsonl"

MODEL_TOKENIZER_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
PROMPT_SUFFIX = (
    "\nPlease put your final answer inside `\\boxed{}`. "
    "For example: `\\boxed{your answer}`"
)
TOKEN_LIMIT = 8192
OVERLAY_TOKEN_STRATEGIES = {"reuse_base_synthetic", "retokenize_all"}

V4_OUTPUT_ROOT = REPO_ROOT / "versions" / "v20_corrective_corpus_v4_mainline" / "outputs" / "v4_mainline_default"
V6_OUTPUT_ROOT = REPO_ROOT / "versions" / "v20_corrective_corpus_v6_mainline" / "outputs" / "v6_mainline_default"

V4_REPEATED_PATH = V4_OUTPUT_ROOT / "artifacts" / "corrective_overlay_repeated.jsonl"
V6_REPEATED_PATH = V6_OUTPUT_ROOT / "artifacts" / "corrective_overlay_repeated.jsonl"

TRAIN_RECOMMENDED_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_recommended_learning_target_v1.csv"
TRAIN_MANUAL_AUDIT_PATH = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_manual_audit_priority_v1.csv"

RESULT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "result"
RESULT_SLICES = {
    "v4": {
        "validation": RESULT_ROOT / "results-v4" / "validation.csv",
        "proxy": RESULT_ROOT / "leaderboard_proxy_eval-v4" / "artifacts" / "leaderboard_proxy_eval_row_level.csv",
    },
    "v6": {
        "validation": RESULT_ROOT / "results-v6" / "validation.csv",
        "proxy": RESULT_ROOT / "leaderboard_proxy_eval-v6" / "artifacts" / "leaderboard_proxy_eval_row_level.csv",
    },
    "v7_1": {
        "validation": RESULT_ROOT / "results-v7-1" / "validation.csv",
        "proxy": RESULT_ROOT / "leaderboard_proxy_eval-v7-1" / "artifacts" / "leaderboard_proxy_eval_row_level.csv",
    },
    "v8": {
        "validation": RESULT_ROOT / "results-v8" / "validation.csv",
        "proxy": RESULT_ROOT / "leaderboard_proxy_eval-v8" / "artifacts" / "leaderboard_proxy_eval_row_level.csv",
    },
    "v9": {
        "validation": RESULT_ROOT / "results-v9" / "validation.csv",
        "proxy": RESULT_ROOT / "leaderboard_proxy_eval-v9" / "artifacts" / "leaderboard_proxy_eval_row_level.csv",
    },
}

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

PERSISTENT_HARD_CORE_IDS = {
    "012fb81b",
    "01e09228",
    "101410e4",
    "12154247",
    "12fd5b6c",
    "1532c0d1",
    "2230fad0",
    "257e7158",
    "2d790c98",
    "31966698",
    "a6192d29",
}

PUBLIC_SENSITIVE_ANCHOR_IDS = {
    "069dbaab",
    "0a50c4a8",
    "0dd5caf4",
    "13009e35",
    "13c8ae90",
    "26a70ae0",
    "6a333ed6",
    "c30a782a",
}

HARD_DEFAULT1_TARGET_IDS = {
    "0dd5caf4",
    "012fb81b",
    "01e09228",
    "0245b9bb",
    "0311b798",
    "0520a6ec",
    "0a50c4a8",
    "1126e314",
    "12fd5b6c",
    "1532c0d1",
    "172d2417",
    "17fd9612",
    "2d790c98",
    "59c78e51",
    "8e5d6fe6",
    "a6192d29",
    "c30a782a",
}

V10_NUMERAL_SURFACE_IDS = {
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

V10_SYMBOL_PREFIX_IDS = {
    "0641ef58",
    "21261dc6",
    "c541eb82",
    "d9bedb64",
}

V10_CIPHER_GUARDRAIL_IDS = {
    "0184a864",
    "018c6f61",
    "13db9692",
    "16642d10",
    "bb187775",
    "c35cbfaa",
}

V10_UNIT_GUARDRAIL_IDS = {
    "077cfc0b",
    "0a0698b2",
    "14dc1dbb",
    "5438b782",
    "626d6c5f",
    "f40d88b6",
}

V10_GRAVITY_GUARDRAIL_IDS = {
    "0fd289d8",
    "3d6a080f",
    "68d2848b",
    "80311ce2",
    "a143f146",
    "d0b20175",
}

V10_EXPLICIT_SYNTHETIC_ROWS: dict[str, dict[str, Any]] = {
    "1542039b": {
        "id": "1542039b",
        "category": "numeral",
        "bucket": "surface_numeral_boxed",
        "prompt": "In Alice's Wonderland, numbers are secretly converted into a different numeral system. Some examples are given below:\n73 -> LXXIII\n17 -> XVII\n27 -> XXVII\n19 -> XIX\n100 -> C\nNow, write the number 54 in the Wonderland numeral system.",
        "answer": "LIV",
        "completion_text": "<think>\nWrite only the final Roman numeral in the box.\nDo not add extra text after the boxed answer.\n</think>\n\\boxed{LIV}<|im_end|>",
        "assistant_style": "surface_boxed_tail",
        "supervision_role": "lane4_surface_guardrail",
        "selection_tier": "v10_numeral_surface_synth",
        "template_subtype": "roman_standard",
        "teacher_solver_candidate": "roman_surface_boxed_only",
        "source_tags": ["surface_numeral_boxed", "v10_numeral_surface_synth"],
        "source_mix": "v10_numeral_surface_synth",
        "proxy_failed": False,
        "validation_failed": True,
        "hard_score": 0.0,
        "audit_reasons": "",
        "analysis_notes": "v6_numeral_surface_backfill",
        "symbol_query_operator": "",
    },
}

FRONTIER_BUCKET_ORDER = (
    "binary_structured_exact_core",
    "binary_logic_exact",
    "binary_permutation_exact",
    "binary_prompt_local_exact",
    "binary_manual_frontier",
)

DEFAULT_FRONTIER_LIMITS = {
    "binary_structured_exact_core": 96,
    "binary_logic_exact": 40,
    "binary_permutation_exact": 24,
    "binary_prompt_local_exact": 24,
    "binary_manual_frontier": 24,
}

DEFAULT_REPEAT_COUNTS = {
    "binary_structured_exact_core": 2,
    "binary_logic_exact": 2,
    "binary_permutation_exact": 2,
    "binary_prompt_local_exact": 2,
    "binary_manual_frontier": 2,
}

PRIORITY_BINARY_FAMILIES = (
    "xor(shl,shr)",
    "choose(shl,shr,rol)",
    "choose(shl,shr,ror)",
    "majority(ror,shl,shr)",
    "majority(rol,shl,shr)",
    "xor(ror,shl)",
    "or(rol,shr)",
    "or(ror,shr)",
)

PRIORITY_BINARY_FAMILY_QUOTAS = {
    "xor(shl,shr)": 32,
    "choose(shl,shr,rol)": 12,
    "choose(shl,shr,ror)": 12,
    "majority(ror,shl,shr)": 10,
    "majority(rol,shl,shr)": 10,
    "xor(ror,shl)": 8,
    "or(rol,shr)": 6,
    "or(ror,shr)": 6,
}

STRUCTURED_SPILLOVER_SLOTS = 24
BINARY_HARD_EXTRA_VARIANTS = 1

HARDBLACKLIST_IDS = {
    "binary_structured_exact_core": {"2817d770", "06b5da9f"},
    "binary_logic_exact": {"6a333ed6"},
}

SOURCE_ROW_METADATA_FIELDS = (
    "selection_tier",
    "template_subtype",
    "teacher_solver_candidate",
    "hard_score",
    "audit_reasons",
    "analysis_notes",
    "symbol_query_operator",
    "bit_query_binary",
    "bit_structured_formula_name",
    "bit_structured_formula_prediction",
    "bit_structured_formula_abstract_family",
    "bit_structured_formula_abstract_support",
    "bit_not_structured_formula_name",
    "bit_not_structured_formula_prediction",
    "bit_not_structured_formula_abstract_family",
    "bit_not_structured_formula_abstract_support",
    "audit_priority_score",
)


@dataclass
class Candidate:
    row: dict[str, str]
    bucket: str
    source_tags: tuple[str, ...]
    source_mix: str
    proxy_failed: bool
    validation_failed: bool
    priority_key: tuple[Any, ...]


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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def relative_to_repo(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def parse_float(value: Any, default: float = 0.0) -> float:
    try:
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def parse_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        if not text:
            return default
        return int(float(text))
    except (TypeError, ValueError):
        return default


def normalize_bool(value: Any) -> bool:
    return parse_bool(value)


def normalize_tags(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass
    if "|" in text:
        return [chunk.strip() for chunk in text.split("|") if chunk.strip()]
    return [text]


def require_non_empty_string(raw: dict[str, Any], key: str, row_id: str) -> str:
    value = str(raw.get(key, "")).strip()
    if not value:
        raise SystemExit(f"Missing {key} for overlay row {row_id}")
    return value


def ensure_file_exists(path: Path, hint: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required artifact: {path}. {hint}")


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


def default_assistant_style(bucket: str) -> str:
    if bucket.startswith("surface_") or bucket == "easy_gravity_fragile":
        return "legacy_v4_surface_trace"
    return "legacy_v4_long_trace"


def default_supervision_role(bucket: str) -> str:
    if bucket.startswith("surface_") or bucket == "easy_gravity_fragile":
        return "lane0_public_surface"
    return "lane0_public_backbone"


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
    if source_mix == "v6_symbol_prefix_donor":
        return "surface_symbol_prefix_donor"
    if source_mix == "v6_cipher_guardrail_donor":
        return "surface_cipher_boxed_donor"
    if source_mix == "v6_unit_guardrail_donor":
        return "surface_unit_tail_donor"
    if source_mix == "v6_gravity_guardrail_donor":
        return "easy_gravity_fragile_donor"
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
        "bit_query_binary": str(raw.get("bit_query_binary", "")),
        "bit_structured_formula_name": str(raw.get("bit_structured_formula_name", "")),
        "bit_structured_formula_prediction": str(raw.get("bit_structured_formula_prediction", "")),
        "bit_structured_formula_abstract_family": str(raw.get("bit_structured_formula_abstract_family", "")),
        "bit_not_structured_formula_name": str(raw.get("bit_not_structured_formula_name", "")),
        "bit_not_structured_formula_prediction": str(raw.get("bit_not_structured_formula_prediction", "")),
        "bit_not_structured_formula_abstract_family": str(raw.get("bit_not_structured_formula_abstract_family", "")),
    }


def renumber_overlay_instances(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: defaultdict[str, int] = defaultdict(int)
    total_by_id = Counter(row["id"] for row in rows)
    normalized: list[dict[str, Any]] = []
    for row in rows:
        copied = dict(row)
        by_id[copied["id"]] += 1
        copied["overlay_instance"] = by_id[copied["id"]]
        copied["recommended_repeat_count"] = int(total_by_id[copied["id"]])
        normalized.append(copied)
    return normalized


def load_repeated_rows(path: Path, hint: str) -> list[dict[str, Any]]:
    ensure_file_exists(path, hint)
    return load_jsonl_rows(path)


def append_overlay_row(
    selected_rows: list[dict[str, Any]],
    existing_signatures: set[tuple[str, str, str]],
    raw: dict[str, Any],
    source_mix: str,
) -> bool:
    normalized = normalize_overlay_row(raw, source_mix)
    signature = (normalized["id"], normalized["bucket"], normalized["completion_text"])
    if signature in existing_signatures:
        return False
    selected_rows.append(normalized)
    existing_signatures.add(signature)
    return True


def build_backbone_overlay_mix() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    v4_rows = load_repeated_rows(
        V4_REPEATED_PATH,
        "Run `uv run python versions/v20_corrective_corpus_v4_mainline/reproduce_v20_corrective_corpus_v4_mainline.py --run-name v4_mainline_default` first.",
    )
    v6_rows = load_repeated_rows(V6_REPEATED_PATH, "Run v6 generation first if artifacts are missing.")

    selected_rows: list[dict[str, Any]] = []
    existing_signatures: set[tuple[str, str, str]] = set()
    source_mix_counts: Counter[str] = Counter()

    def append_base(raw: dict[str, Any], source_mix: str) -> None:
        if append_overlay_row(selected_rows, existing_signatures, raw, source_mix):
            source_mix_counts[source_mix] += 1

    def append_required(rows: list[dict[str, Any]], required_ids: set[str], bucket: str, source_mix: str) -> set[str]:
        present: set[str] = set()
        for raw in rows:
            row_id = str(raw.get("id", ""))
            if row_id not in required_ids:
                continue
            if str(raw.get("bucket", "")) != bucket:
                continue
            if append_overlay_row(selected_rows, existing_signatures, raw, source_mix):
                source_mix_counts[source_mix] += 1
                present.add(row_id)
        return present

    for raw in v4_rows:
        append_base(raw, "v4_public_base")

    binary_present: set[str] = set()
    for raw in v6_rows:
        row_id = str(raw.get("id", ""))
        bucket = str(raw.get("bucket", ""))
        if row_id not in MANUAL_BINARY_DONOR_IDS or not bucket.startswith("binary_"):
            continue
        if append_overlay_row(selected_rows, existing_signatures, raw, "v6_binary_donor"):
            source_mix_counts["v6_binary_donor"] += 1
            binary_present.add(row_id)
    missing_binary = sorted(MANUAL_BINARY_DONOR_IDS - binary_present)
    if missing_binary:
        raise SystemExit(f"Missing pinned v10 binary donor rows in v6 artifacts: {missing_binary}")

    numeral_present = append_required(v6_rows, V10_NUMERAL_SURFACE_IDS, "surface_numeral_boxed", "v6_numeral_surface_donor")
    missing_v6_numeral = sorted(V10_NUMERAL_SURFACE_IDS - numeral_present)
    synthetic_numeral_ids: list[str] = []
    for row_id in missing_v6_numeral:
        synthetic = V10_EXPLICIT_SYNTHETIC_ROWS.get(row_id)
        if synthetic is None:
            raise SystemExit(f"Missing pinned numeral donor row without synthetic replacement: {row_id}")
        if append_overlay_row(selected_rows, existing_signatures, synthetic, "v10_numeral_surface_synth"):
            source_mix_counts["v10_numeral_surface_synth"] += 1
            numeral_present.add(row_id)
            synthetic_numeral_ids.append(row_id)
    if numeral_present != V10_NUMERAL_SURFACE_IDS:
        missing_final = sorted(V10_NUMERAL_SURFACE_IDS - numeral_present)
        raise SystemExit(f"Failed to realize pinned numeral surface set: {missing_final}")

    surface_specs = [
        (V10_SYMBOL_PREFIX_IDS, "surface_symbol_prefix", "v6_symbol_prefix_donor"),
        (V10_CIPHER_GUARDRAIL_IDS, "surface_cipher_boxed", "v6_cipher_guardrail_donor"),
        (V10_UNIT_GUARDRAIL_IDS, "surface_unit_tail", "v6_unit_guardrail_donor"),
        (V10_GRAVITY_GUARDRAIL_IDS, "easy_gravity_fragile", "v6_gravity_guardrail_donor"),
    ]
    guardrail_presence: dict[str, list[str]] = {}
    for required_ids, bucket, source_mix in surface_specs:
        present = append_required(v6_rows, required_ids, bucket, source_mix)
        missing = sorted(required_ids - present)
        if missing:
            raise SystemExit(f"Missing pinned v10 surface donor rows for {bucket}: {missing}")
        guardrail_presence[source_mix] = sorted(present)

    diagnostics = {
        "source_mix_counts": dict(sorted(source_mix_counts.items())),
        "pinned_binary_donor_ids": sorted(MANUAL_BINARY_DONOR_IDS),
        "pinned_numeral_surface_ids": sorted(V10_NUMERAL_SURFACE_IDS),
        "explicit_synthetic_numeral_ids": synthetic_numeral_ids,
        "surface_guardrail_ids": {
            "v6_symbol_prefix_donor": sorted(V10_SYMBOL_PREFIX_IDS),
            "v6_cipher_guardrail_donor": sorted(V10_CIPHER_GUARDRAIL_IDS),
            "v6_unit_guardrail_donor": sorted(V10_UNIT_GUARDRAIL_IDS),
            "v6_gravity_guardrail_donor": sorted(V10_GRAVITY_GUARDRAIL_IDS),
        },
        "surface_guardrail_presence": guardrail_presence,
    }
    return renumber_overlay_instances(selected_rows), diagnostics


def binary_family_key(row: dict[str, str]) -> str:
    return (
        str(row.get("bit_structured_formula_abstract_family", "")).strip()
        or str(row.get("bit_not_structured_formula_abstract_family", "")).strip()
        or str(row.get("bit_structured_formula_name", "")).strip()
        or str(row.get("bit_not_structured_formula_name", "")).strip()
        or str(row.get("teacher_solver_candidate", "")).strip()
        or str(row.get("template_subtype", "")).strip()
        or "NONE"
    )


def build_completion_from_think_lines(lines: list[str], answer: str) -> str:
    return "\n".join(["<think>", *lines, "</think>", f"\\boxed{{{answer}}}<|im_end|>"])


def build_binary_completion(candidate: Candidate, assistant_style: str) -> str:
    row = candidate.row
    bucket = candidate.bucket
    family = binary_family_key(row)
    exact_rule = str(row.get("bit_structured_formula_name", "")).strip() or str(
        row.get("bit_not_structured_formula_name", "")
    ).strip()
    solver = str(row.get("teacher_solver_candidate", "")).strip() or "verified_binary_rule"

    if bucket == "binary_manual_frontier":
        if assistant_style == "manual_frontier_commit":
            lines = [
                "Use the audited final byte exactly as established by the prompt examples.",
                "Do not invent an unseen fallback rule or add explanation noise.",
                "Keep leading zeros and exact 8-bit closure.",
                "Return only the final byte in the box.",
            ]
        elif assistant_style == "manual_anti_default1_commit":
            lines = [
                "This is a hard binary frontier case.",
                "Do not default uncertain positions to 1 or guessed activations.",
                "If a bit is not justified by the prompt pattern, leave it off.",
                "Return only the exact final 8-bit byte in the box.",
            ]
        else:
            raise ValueError(f"Unsupported manual frontier assistant style: {assistant_style}")
        return build_completion_from_think_lines(lines, answer=row["answer"])

    if assistant_style == "exact_rule_commit":
        if bucket == "binary_structured_exact_core":
            lines = [
                f"Verified structured binary family: {family}." if family != "NONE" else "Use the verified structured binary rule from the examples.",
                f"Concrete rule: {exact_rule}." if exact_rule else f"Recovered solver pattern: {solver}.",
                "Apply the same verified transformation to the query byte.",
                "Keep the final byte exact with leading zeros and no fallback bits.",
            ]
        elif bucket == "binary_logic_exact":
            lines = [
                f"Verified bitwise rule family: {family}." if family != "NONE" else "Use the verified bitwise rule from the examples.",
                f"Concrete logic rule: {exact_rule}." if exact_rule else f"Recovered solver pattern: {solver}.",
                "Resolve every bit from the verified logic pattern.",
                "Keep the final byte exact with leading zeros.",
            ]
        elif bucket == "binary_permutation_exact":
            lines = [
                "Use the exact source-bit reordering verified in the examples.",
                f"Recovered permutation family: {solver}." if solver else "Copy each output bit from its verified source position.",
                "Preserve the exact 8-bit ordering and leading zeros.",
                "Return only the final reordered byte in the box.",
            ]
        elif bucket == "binary_prompt_local_exact":
            lines = [
                "Use the exact prompt-local binary rule verified by the examples.",
                f"Recovered exact pattern: {solver}." if solver else "Keep the query under the same prompt-local exact rule.",
                "Preserve exact 8-bit closure with leading zeros.",
                "Return only the final byte in the box.",
            ]
        else:
            raise ValueError(f"Unsupported binary bucket for exact_rule_commit: {bucket}")
    elif assistant_style == "exact_closure_commit":
        lines = [
            f"Verified binary family: {family}." if family != "NONE" else "Use the verified binary rule from the examples.",
            "Use only the bits justified by the verified rule.",
            "Keep exact 8-bit closure with leading zeros from start to finish.",
            "Only the final byte belongs in the box.",
        ]
    elif assistant_style == "anti_default1_commit":
        lines = [
            f"Verified binary family: {family}." if family != "NONE" else "Use the verified binary rule from the examples.",
            "Do not use default 1, fallback bits, or guessed activations.",
            "If a bit is not justified by the verified rule, it stays off.",
            "Return only the exact final 8-bit byte in the box.",
        ]
    else:
        raise ValueError(f"Unsupported binary assistant style: {assistant_style}")
    return build_completion_from_think_lines(lines, answer=row["answer"])


def build_supervision_variants(candidate: Candidate, base_variant_count: int) -> list[dict[str, str]]:
    row_id = candidate.row["id"]
    if candidate.bucket == "binary_manual_frontier":
        variant_styles = ["manual_frontier_commit", "manual_anti_default1_commit"]
        target_count = min(base_variant_count, len(variant_styles))
        if row_id in HARD_DEFAULT1_TARGET_IDS:
            target_count = len(variant_styles)
        role_map = {
            "manual_frontier_commit": "lane2_frontier_manual",
            "manual_anti_default1_commit": "lane3_anti_default1",
        }
        return [
            {
                "assistant_style": style,
                "supervision_role": role_map[style],
                "completion_text": build_binary_completion(candidate, style),
            }
            for style in variant_styles[:target_count]
        ]

    variant_styles = ["exact_rule_commit", "exact_closure_commit"]
    if row_id in HARD_DEFAULT1_TARGET_IDS:
        variant_styles.append("anti_default1_commit")
    target_count = base_variant_count + (
        BINARY_HARD_EXTRA_VARIANTS if row_id in HARD_DEFAULT1_TARGET_IDS else 0
    )
    target_count = min(target_count, len(variant_styles))
    role_map = {
        "exact_rule_commit": "lane1_exact_binary",
        "exact_closure_commit": "lane1_exact_binary",
        "anti_default1_commit": "lane3_anti_default1",
    }
    return [
        {
            "assistant_style": style,
            "supervision_role": role_map[style],
            "completion_text": build_binary_completion(candidate, style),
        }
        for style in variant_styles[:target_count]
    ]


def ensure_default_row_fields(merged: dict[str, str]) -> None:
    merged.setdefault("selection_tier", "")
    merged.setdefault("template_subtype", "")
    merged.setdefault("teacher_solver_candidate", "")
    merged.setdefault("hard_score", "")
    merged.setdefault("audit_reasons", "")
    merged.setdefault("analysis_notes", "")
    merged.setdefault("symbol_query_operator", "")
    merged.setdefault("bit_query_binary", "")
    merged.setdefault("bit_structured_formula_name", "")
    merged.setdefault("bit_structured_formula_prediction", "")
    merged.setdefault("bit_structured_formula_abstract_family", "")
    merged.setdefault("bit_structured_formula_abstract_support", "")
    merged.setdefault("bit_not_structured_formula_name", "")
    merged.setdefault("bit_not_structured_formula_prediction", "")
    merged.setdefault("bit_not_structured_formula_abstract_family", "")
    merged.setdefault("bit_not_structured_formula_abstract_support", "")
    merged.setdefault("audit_priority_score", "")


def measured_bucket_for_row(row: dict[str, str]) -> str | None:
    subtype = str(row.get("template_subtype", "")).strip()
    if subtype == "bit_structured_byte_formula":
        return "binary_structured_exact_core"
    if subtype == "bit_other":
        return "binary_logic_exact"
    if subtype == "bit_permutation_inversion":
        return "binary_permutation_exact"
    if subtype == "bit_prompt_local_exact_formula":
        return "binary_prompt_local_exact"
    return None


def read_csv_map(path: Path, key: str = "id") -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    return {row[key]: row for row in load_csv_rows(path)}


def load_measured_signals() -> dict[str, Any]:
    proxy_correct_by_version: dict[str, dict[str, bool]] = {}
    validation_correct_by_version: dict[str, dict[str, bool]] = {}

    for version_name, paths in RESULT_SLICES.items():
        proxy_rows = read_csv_map(paths["proxy"])
        validation_rows = read_csv_map(paths["validation"])
        proxy_correct_by_version[version_name] = {
            row_id: row.get("is_correct") == "True" for row_id, row in proxy_rows.items()
        }
        validation_correct_by_version[version_name] = {
            row_id: row.get("correct") == "True" for row_id, row in validation_rows.items()
        }

    all_ids: set[str] = set()
    for rows in proxy_correct_by_version.values():
        all_ids.update(rows)
    for rows in validation_correct_by_version.values():
        all_ids.update(rows)

    proxy_fail_count: dict[str, int] = defaultdict(int)
    validation_fail_count: dict[str, int] = defaultdict(int)
    proxy_fail_versions: dict[str, list[str]] = defaultdict(list)
    validation_fail_versions: dict[str, list[str]] = defaultdict(list)
    proxy_success_versions: dict[str, list[str]] = defaultdict(list)
    validation_success_versions: dict[str, list[str]] = defaultdict(list)

    for row_id in sorted(all_ids):
        for version_name, rows in proxy_correct_by_version.items():
            if row_id not in rows:
                continue
            if rows[row_id]:
                proxy_success_versions[row_id].append(version_name)
            else:
                proxy_fail_count[row_id] += 1
                proxy_fail_versions[row_id].append(version_name)
        for version_name, rows in validation_correct_by_version.items():
            if row_id not in rows:
                continue
            if rows[row_id]:
                validation_success_versions[row_id].append(version_name)
            else:
                validation_fail_count[row_id] += 1
                validation_fail_versions[row_id].append(version_name)

    return {
        "proxy_correct_by_version": proxy_correct_by_version,
        "validation_correct_by_version": validation_correct_by_version,
        "proxy_fail_count": proxy_fail_count,
        "validation_fail_count": validation_fail_count,
        "proxy_fail_versions": proxy_fail_versions,
        "validation_fail_versions": validation_fail_versions,
        "proxy_success_versions": proxy_success_versions,
        "validation_success_versions": validation_success_versions,
    }


def row_category(source_row: dict[str, str]) -> str:
    return str(source_row.get("family") or source_row.get("category") or "unknown").strip()


def make_candidate(
    *,
    source_row: dict[str, str],
    bucket: str,
    source_tags: set[str],
    source_mix: str,
    proxy_failed: bool,
    validation_failed: bool,
    priority_key: tuple[Any, ...],
) -> Candidate:
    merged = dict(source_row)
    merged["id"] = str(source_row["id"]).strip()
    merged["prompt"] = str(source_row["prompt"]).strip()
    merged["answer"] = str(source_row["answer"]).strip()
    merged["category"] = row_category(source_row)
    ensure_default_row_fields(merged)
    return Candidate(
        row=merged,
        bucket=bucket,
        source_tags=tuple(sorted(source_tags)),
        source_mix=source_mix,
        proxy_failed=proxy_failed,
        validation_failed=validation_failed,
        priority_key=priority_key,
    )


def is_binary_answer(answer: str) -> bool:
    text = str(answer).strip()
    return len(text) == 8 and set(text) <= {"0", "1"}


def build_verified_frontier_candidates(
    measured: dict[str, Any],
) -> tuple[list[Candidate], dict[str, Any]]:
    candidates: list[Candidate] = []
    available_watchlist_ids: set[str] = set()

    for row in load_csv_rows(TRAIN_RECOMMENDED_PATH):
        row_id = str(row["id"]).strip()
        bucket = measured_bucket_for_row(row)
        if bucket is None:
            continue
        if row_id in HARDBLACKLIST_IDS.get(bucket, set()):
            continue
        if str(row.get("selection_tier", "")).strip() != "verified_trace_ready":
            continue
        if not is_binary_answer(row.get("answer", "")):
            continue

        proxy_fail_count = int(measured["proxy_fail_count"].get(row_id, 0))
        validation_fail_count = int(measured["validation_fail_count"].get(row_id, 0))
        mandatory_watchlist = row_id in (PERSISTENT_HARD_CORE_IDS | PUBLIC_SENSITIVE_ANCHOR_IDS | MANUAL_BINARY_DONOR_IDS)
        hard_default1 = row_id in HARD_DEFAULT1_TARGET_IDS
        available_watchlist_ids.add(row_id) if mandatory_watchlist else None

        abstract_support = parse_int(row.get("bit_structured_formula_abstract_support", 0), 0)
        structured_formula_safe = parse_bool(row.get("bit_structured_formula_safe", False))
        not_structured_formula_safe = parse_bool(row.get("bit_not_structured_formula_safe", False))
        hard_score = parse_float(row.get("hard_score", 0.0), 0.0)
        num_examples = parse_int(row.get("num_examples", 0), 0)

        qualifies = mandatory_watchlist or hard_default1 or proxy_fail_count > 0 or validation_fail_count > 0
        if bucket == "binary_structured_exact_core":
            qualifies = qualifies or abstract_support >= 20 or structured_formula_safe or not_structured_formula_safe
        else:
            qualifies = qualifies or hard_score >= 5.0
        if not qualifies:
            continue

        source_tags = {"train_recommended_learning_target_v1", bucket, "verified_trace_ready"}
        if row_id in PERSISTENT_HARD_CORE_IDS:
            source_tags.add("persistent_hard_core")
        if row_id in PUBLIC_SENSITIVE_ANCHOR_IDS:
            source_tags.add("public_sensitive_anchor")
        if hard_default1:
            source_tags.add("hard_default1_target")
        for version_name in measured["proxy_fail_versions"].get(row_id, []):
            source_tags.add(f"proxy_fail_{version_name}")
        for version_name in measured["validation_fail_versions"].get(row_id, []):
            source_tags.add(f"validation_fail_{version_name}")

        priority_key = (
            -(1 if mandatory_watchlist else 0),
            -(1 if row_id in PERSISTENT_HARD_CORE_IDS else 0),
            -(1 if row_id in PUBLIC_SENSITIVE_ANCHOR_IDS else 0),
            -(1 if hard_default1 else 0),
            -proxy_fail_count,
            -validation_fail_count,
            -(1 if structured_formula_safe else 0),
            -(1 if not_structured_formula_safe else 0),
            -abstract_support,
            -hard_score,
            -num_examples,
            row_id,
        )
        candidates.append(
            make_candidate(
                source_row=row,
                bucket=bucket,
                source_tags=source_tags,
                source_mix="v10_verified_frontier",
                proxy_failed=proxy_fail_count > 0,
                validation_failed=validation_fail_count > 0,
                priority_key=priority_key,
            )
        )

    diagnostics = {
        "candidate_count": len(candidates),
        "available_watchlist_ids": sorted(available_watchlist_ids),
    }
    return candidates, diagnostics


def build_manual_frontier_candidates(measured: dict[str, Any]) -> tuple[list[Candidate], dict[str, Any]]:
    candidates: list[Candidate] = []
    available_manual_watchlist_ids: set[str] = set()

    for row in load_csv_rows(TRAIN_MANUAL_AUDIT_PATH):
        row_id = str(row["id"]).strip()
        if str(row.get("selection_tier", "")).strip() != "manual_audit_priority":
            continue
        if str(row.get("template_subtype", "")).strip() != "bit_other":
            continue
        if not is_binary_answer(row.get("answer", "")):
            continue
        if not parse_bool(row.get("parse_ok", False)):
            continue
        if not parse_bool(row.get("boxed_safe", False)):
            continue

        proxy_fail_count = int(measured["proxy_fail_count"].get(row_id, 0))
        validation_fail_count = int(measured["validation_fail_count"].get(row_id, 0))
        audit_priority = parse_float(row.get("audit_priority_score", 0.0), 0.0)
        hard_score = parse_float(row.get("hard_score", 0.0), 0.0)
        num_examples = parse_int(row.get("num_examples", 0), 0)

        watchlist = row_id in (PERSISTENT_HARD_CORE_IDS | PUBLIC_SENSITIVE_ANCHOR_IDS | HARD_DEFAULT1_TARGET_IDS)
        if watchlist:
            available_manual_watchlist_ids.add(row_id)
        if not (watchlist or audit_priority >= 13.5 or proxy_fail_count >= 2 or validation_fail_count >= 2):
            continue

        source_tags = {"train_manual_audit_priority_v1", "manual_audit_priority", "bit_other", "binary_manual_frontier"}
        if row_id in PERSISTENT_HARD_CORE_IDS:
            source_tags.add("persistent_hard_core")
        if row_id in PUBLIC_SENSITIVE_ANCHOR_IDS:
            source_tags.add("public_sensitive_anchor")
        if row_id in HARD_DEFAULT1_TARGET_IDS:
            source_tags.add("hard_default1_target")
        for version_name in measured["proxy_fail_versions"].get(row_id, []):
            source_tags.add(f"proxy_fail_{version_name}")
        for version_name in measured["validation_fail_versions"].get(row_id, []):
            source_tags.add(f"validation_fail_{version_name}")

        priority_key = (
            -(1 if watchlist else 0),
            -(1 if row_id in PERSISTENT_HARD_CORE_IDS else 0),
            -(1 if row_id in PUBLIC_SENSITIVE_ANCHOR_IDS else 0),
            -(1 if row_id in HARD_DEFAULT1_TARGET_IDS else 0),
            -proxy_fail_count,
            -validation_fail_count,
            -audit_priority,
            -hard_score,
            -num_examples,
            row_id,
        )
        candidates.append(
            make_candidate(
                source_row=row,
                bucket="binary_manual_frontier",
                source_tags=source_tags,
                source_mix="v10_manual_frontier",
                proxy_failed=proxy_fail_count > 0,
                validation_failed=validation_fail_count > 0,
                priority_key=priority_key,
            )
        )

    diagnostics = {
        "candidate_count": len(candidates),
        "available_manual_watchlist_ids": sorted(available_manual_watchlist_ids),
    }
    return candidates, diagnostics


def select_frontier_candidates(
    verified_candidates: list[Candidate],
    manual_candidates: list[Candidate],
    frontier_limits: dict[str, int],
) -> list[Candidate]:
    candidates = sorted(verified_candidates + manual_candidates, key=lambda item: (FRONTIER_BUCKET_ORDER.index(item.bucket), item.priority_key))
    selected: list[Candidate] = []
    counts = Counter()
    seen_ids: set[tuple[str, str]] = set()

    def add_candidate(candidate: Candidate) -> None:
        key = (candidate.row["id"], candidate.bucket)
        if key in seen_ids:
            return
        selected.append(candidate)
        counts[candidate.bucket] += 1
        seen_ids.add(key)

    structured_candidates = [candidate for candidate in candidates if candidate.bucket == "binary_structured_exact_core"]
    structured_priority_limit = max(
        0,
        frontier_limits["binary_structured_exact_core"] - STRUCTURED_SPILLOVER_SLOTS,
    )
    structured_family_counts: Counter[str] = Counter()
    for candidate in structured_candidates:
        row_id = candidate.row["id"]
        if row_id not in (PERSISTENT_HARD_CORE_IDS | PUBLIC_SENSITIVE_ANCHOR_IDS | MANUAL_BINARY_DONOR_IDS):
            continue
        if counts["binary_structured_exact_core"] >= frontier_limits["binary_structured_exact_core"]:
            break
        add_candidate(candidate)
        structured_family_counts[binary_family_key(candidate.row)] += 1

    family_candidates: dict[str, list[Candidate]] = defaultdict(list)
    for candidate in structured_candidates:
        key = (candidate.row["id"], candidate.bucket)
        if key in seen_ids:
            continue
        family_candidates[binary_family_key(candidate.row)].append(candidate)
    for family in PRIORITY_BINARY_FAMILIES:
        quota = PRIORITY_BINARY_FAMILY_QUOTAS[family]
        for candidate in family_candidates.get(family, []):
            if counts["binary_structured_exact_core"] >= structured_priority_limit:
                break
            if structured_family_counts[family] >= quota:
                break
            add_candidate(candidate)
            structured_family_counts[family] += 1
    for candidate in structured_candidates:
        if counts["binary_structured_exact_core"] >= frontier_limits["binary_structured_exact_core"]:
            break
        add_candidate(candidate)

    for bucket in FRONTIER_BUCKET_ORDER:
        if bucket == "binary_structured_exact_core":
            continue
        bucket_candidates = [candidate for candidate in candidates if candidate.bucket == bucket]
        for candidate in bucket_candidates:
            if counts[bucket] >= frontier_limits[bucket]:
                break
            add_candidate(candidate)
    return selected


def build_frontier_overlay_rows(
    selected: list[Candidate],
    repeat_counts: dict[str, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    unique_rows: list[dict[str, Any]] = []
    repeated_rows: list[dict[str, Any]] = []

    for candidate in selected:
        row = candidate.row
        variants = build_supervision_variants(candidate, base_variant_count=repeat_counts[candidate.bucket])
        base = {
            "id": row["id"],
            "category": row["category"],
            "bucket": candidate.bucket,
            "prompt": row["prompt"],
            "answer": row["answer"],
            "completion_text": variants[0]["completion_text"],
            "selection_tier": row.get("selection_tier", ""),
            "template_subtype": row.get("template_subtype", ""),
            "teacher_solver_candidate": row.get("teacher_solver_candidate", ""),
            "source_tags": list(candidate.source_tags),
            "source_mix": candidate.source_mix,
            "proxy_failed": candidate.proxy_failed,
            "validation_failed": candidate.validation_failed,
            "recommended_repeat_count": len(variants),
            "assistant_styles": [variant["assistant_style"] for variant in variants],
            "hard_score": parse_float(row.get("hard_score", 0.0), 0.0),
            "audit_reasons": row.get("audit_reasons", ""),
            "analysis_notes": row.get("analysis_notes", ""),
            "symbol_query_operator": row.get("symbol_query_operator", ""),
            "bit_query_binary": row.get("bit_query_binary", ""),
            "bit_structured_formula_name": row.get("bit_structured_formula_name", ""),
            "bit_structured_formula_prediction": row.get("bit_structured_formula_prediction", ""),
            "bit_structured_formula_abstract_family": row.get("bit_structured_formula_abstract_family", ""),
            "bit_not_structured_formula_name": row.get("bit_not_structured_formula_name", ""),
            "bit_not_structured_formula_prediction": row.get("bit_not_structured_formula_prediction", ""),
            "bit_not_structured_formula_abstract_family": row.get("bit_not_structured_formula_abstract_family", ""),
            "binary_family_key": binary_family_key(row),
            "audit_priority_score": row.get("audit_priority_score", ""),
        }
        unique_rows.append(base)
        for variant in variants:
            repeated = dict(base)
            repeated["completion_text"] = variant["completion_text"]
            repeated["assistant_style"] = variant["assistant_style"]
            repeated["supervision_role"] = variant["supervision_role"]
            repeated_rows.append(repeated)

    diagnostics = {
        "selected_by_bucket": dict(sorted(Counter(candidate.bucket for candidate in selected).items())),
        "selected_watchlist_hits": sorted(
            row["id"]
            for row in unique_rows
            if row["id"] in (PERSISTENT_HARD_CORE_IDS | PUBLIC_SENSITIVE_ANCHOR_IDS | MANUAL_BINARY_DONOR_IDS)
        ),
    }
    return unique_rows, renumber_overlay_instances(repeated_rows), diagnostics


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
                "selection_tier": row.get("selection_tier", ""),
                "template_subtype": row.get("template_subtype", ""),
                "teacher_solver_candidate": row.get("teacher_solver_candidate", ""),
                "recommended_repeat_count": 0,
                "assistant_styles": set(),
                "source_mixes": set(),
                "proxy_failed": False,
                "validation_failed": False,
                "hard_score": parse_float(row.get("hard_score", 0.0), 0.0),
                "source_tags": set(),
                "binary_family_key": row.get("binary_family_key", ""),
                "audit_priority_score": row.get("audit_priority_score", ""),
            }
            grouped[key] = entry
        entry["recommended_repeat_count"] += 1
        assistant_style = str(row.get("assistant_style", "")).strip()
        if assistant_style:
            entry["assistant_styles"].add(assistant_style)
        entry["source_mixes"].add(row.get("source_mix", ""))
        entry["proxy_failed"] = entry["proxy_failed"] or bool(row.get("proxy_failed", False))
        entry["validation_failed"] = entry["validation_failed"] or bool(row.get("validation_failed", False))
        entry["source_tags"].update(normalize_tags(row.get("source_tags", [])))

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
                "source_mixes": "|".join(sorted(source for source in entry["source_mixes"] if source)),
                "proxy_failed": entry["proxy_failed"],
                "validation_failed": entry["validation_failed"],
                "hard_score": entry["hard_score"],
                "source_tags": "|".join(sorted(entry["source_tags"])),
                "binary_family_key": entry["binary_family_key"],
                "audit_priority_score": entry["audit_priority_score"],
            }
        )
    return sorted(unique_rows, key=lambda row: (row["bucket"], row["id"]))


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


def build_training_bundle(
    *,
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
        "version": "v20_corrective_corpus_v10_mainline",
        "created_at": utc_now(),
        "base_snapshot_root": relative_to_repo(BASE_SNAPSHOT_ROOT),
        "base_snapshot_config": read_json(BASE_SNAPSHOT_CONFIG_PATH),
        "bundle_path": relative_to_repo(bundle_path),
        "base_excluded_problem_ids": sorted(BASE_EXCLUDED_IDS),
        "overlay_token_strategy": overlay_token_strategy,
        "overlay_reuse_scope": (
            "v4_public_base_only" if overlay_token_strategy == "reuse_base_synthetic" else "none"
        ),
        "note": (
            "Single-file training bundle for v10. Keeps the v4 public-safe backbone token-safe, "
            "adds pinned v6 BIT donors, restores narrow v6 surface guardrails, and adds a "
            "verified/manual BIT frontier pack focused on persistent hard-core and anti-default1 rows."
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


def validate_v10(
    *,
    unique_rows: list[dict[str, Any]],
    repeated_rows: list[dict[str, Any]],
    backbone_diagnostics: dict[str, Any],
    frontier_diagnostics: dict[str, Any],
    frontier_candidate_diagnostics: dict[str, Any],
    training_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    selected_ids = {row["id"] for row in unique_rows}
    requested_watchlist_ids = PERSISTENT_HARD_CORE_IDS | PUBLIC_SENSITIVE_ANCHOR_IDS | MANUAL_BINARY_DONOR_IDS
    available_watchlist_ids = set(frontier_candidate_diagnostics.get("available_watchlist_ids", [])) | set(MANUAL_BINARY_DONOR_IDS)
    missing_watchlist_ids = sorted((requested_watchlist_ids & available_watchlist_ids) - selected_ids)
    source_mix_counts = Counter(row["source_mix"] for row in repeated_rows)

    errors: list[str] = []
    if source_mix_counts.get("v4_public_base", 0) == 0:
        errors.append("v4_public_base lane が空です")
    if source_mix_counts.get("v6_binary_donor", 0) == 0:
        errors.append("v6 binary donor lane が空です")
    if source_mix_counts.get("v10_verified_frontier", 0) == 0:
        errors.append("verified frontier lane が空です")
    if source_mix_counts.get("v6_symbol_prefix_donor", 0) == 0:
        errors.append("symbol prefix guardrail が欠けています")
    if missing_watchlist_ids:
        errors.append("watchlist anchor が欠落しています")
    if training_bundle is not None:
        if int(training_bundle.get("reused_base_synthetic_problem_count", 0)) <= 0:
            errors.append("v4 token-safe reuse が効いていません")
        if int(training_bundle.get("retokenized_overlay_problem_count", 0)) <= 0:
            errors.append("overlay retokenization が発生していません")

    return {
        "passed": not errors,
        "errors": errors,
        "source_mix_counts": dict(sorted(source_mix_counts.items())),
        "missing_watchlist_ids": missing_watchlist_ids,
        "requested_watchlist_ids": sorted(requested_watchlist_ids),
        "backbone_source_mix_counts": backbone_diagnostics.get("source_mix_counts", {}),
        "frontier_selected_by_bucket": frontier_diagnostics.get("selected_by_bucket", {}),
        "frontier_watchlist_hits": frontier_diagnostics.get("selected_watchlist_hits", []),
    }


def build_summary(
    *,
    backbone_diagnostics: dict[str, Any],
    frontier_candidate_diagnostics: dict[str, Any],
    frontier_selection_diagnostics: dict[str, Any],
    unique_rows: list[dict[str, Any]],
    repeated_rows: list[dict[str, Any]],
    validation: dict[str, Any],
    training_bundle: dict[str, Any] | None,
    frontier_limits: dict[str, int],
    repeat_counts: dict[str, int],
    overlay_token_strategy: str,
) -> dict[str, Any]:
    selected_by_bucket = Counter(row["bucket"] for row in unique_rows)
    source_mix_counts = Counter()
    for row in repeated_rows:
        source_mix_counts[row["source_mix"]] += 1
    return {
        "version": "v20_corrective_corpus_v10_mainline",
        "created_at": utc_now(),
        "readme_eval_contract": verify_readme_eval_contract(),
        "strategy_note": relative_to_repo(STRATEGY_NOTE_PATH),
        "inputs": {
            "v4_repeated": relative_to_repo(V4_REPEATED_PATH),
            "v6_repeated": relative_to_repo(V6_REPEATED_PATH),
            "train_recommended_learning_target_v1": relative_to_repo(TRAIN_RECOMMENDED_PATH),
            "train_manual_audit_priority_v1": relative_to_repo(TRAIN_MANUAL_AUDIT_PATH),
        },
        "selected_unique_rows": len(unique_rows),
        "selected_repeated_rows": len(repeated_rows),
        "selected_by_bucket": dict(sorted(selected_by_bucket.items())),
        "source_mix_counts": dict(sorted(source_mix_counts.items())),
        "backbone_diagnostics": backbone_diagnostics,
        "frontier_candidate_diagnostics": frontier_candidate_diagnostics,
        "frontier_selection_diagnostics": frontier_selection_diagnostics,
        "validation": validation,
        "training_bundle": training_bundle,
        "configured_frontier_limits": dict(frontier_limits),
        "configured_repeat_counts": dict(repeat_counts),
        "overlay_token_strategy": overlay_token_strategy,
    }


def render_results_markdown(summary: dict[str, Any]) -> str:
    bundle = summary.get("training_bundle") or {}
    validation = summary["validation"]
    lines = [
        "# v20_corrective_corpus_v10_mainline",
        "",
        f"- created_at: {summary['created_at']}",
        f"- strategy note: {summary['strategy_note']}",
        "- README basis: deterministic boxed-answer evaluation, bit_manipulation primary weighting, token-aware supervision, and token-first bundle construction.",
        "- status: bundle generated; model score not yet measured.",
        "",
        "## Strategy",
        "",
        "- Keep the v4 public-safe backbone token-safe.",
        "- Reuse the pinned v6 binary donor pack narrowly, not as the mainline base.",
        "- Add a verified/manual BIT frontier pack around persistent hard-core and anti-default1 rows.",
        "- Restore v6-level symbol-prefix and easy-family guardrails without reviving broad symbol or matching lanes.",
        "",
        "## Selection",
        "",
        f"- selected_unique_rows: {summary['selected_unique_rows']}",
        f"- selected_repeated_rows: {summary['selected_repeated_rows']}",
        f"- overlay_token_strategy: {summary['overlay_token_strategy']}",
        "",
        "### Unique rows by bucket",
        "",
    ]
    for bucket, count in summary["selected_by_bucket"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend(
        [
            "",
            "### Repeated rows by source mix",
            "",
        ]
    )
    for source_mix, count in summary["source_mix_counts"].items():
        lines.append(f"- {source_mix}: {count}")
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- passed: {validation['passed']}",
            f"- errors: {validation['errors']}",
            f"- missing_watchlist_ids: {validation['missing_watchlist_ids']}",
            f"- frontier_watchlist_hits: {validation['frontier_watchlist_hits']}",
            "",
            "## Bundle",
            "",
            f"- path: {bundle.get('path', 'not_written')}",
            f"- base_examples: {bundle.get('base_examples', 0)}",
            f"- overlay_examples: {bundle.get('overlay_examples', 0)}",
            f"- total_examples: {bundle.get('total_examples', 0)}",
            f"- total_tokens: {bundle.get('total_tokens', 0)}",
            f"- max_seq_len: {bundle.get('max_seq_len', 0)}",
            f"- reused_base_synthetic_problem_count: {bundle.get('reused_base_synthetic_problem_count', 0)}",
            f"- retokenized_overlay_problem_count: {bundle.get('retokenized_overlay_problem_count', 0)}",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_frontier_limits(arg: str | None) -> dict[str, int]:
    limits = dict(DEFAULT_FRONTIER_LIMITS)
    if not arg:
        return limits
    for chunk in arg.split(","):
        text = chunk.strip()
        if not text:
            continue
        key, value = text.split("=", 1)
        if key not in limits:
            raise SystemExit(f"Unknown bucket in --frontier-limits: {key}")
        limits[key] = int(value)
    return limits


def parse_repeat_counts(arg: str | None) -> dict[str, int]:
    counts = dict(DEFAULT_REPEAT_COUNTS)
    if not arg:
        return counts
    for chunk in arg.split(","):
        text = chunk.strip()
        if not text:
            continue
        key, value = text.split("=", 1)
        if key not in counts:
            raise SystemExit(f"Unknown bucket in --repeat-counts: {key}")
        counts[key] = int(value)
    return counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the v10 BIT mainline corrective corpus. "
            "This keeps the v4 public-safe backbone token-safe, "
            "adds the pinned v6 donor pack, restores narrow v6 guardrails, "
            "and adds a verified/manual BIT frontier pack."
        )
    )
    parser.add_argument("--run-name", default="v10_mainline_default")
    parser.add_argument("--frontier-limits", default=None)
    parser.add_argument("--repeat-counts", default=None)
    parser.add_argument("--overlay-token-strategy", choices=sorted(OVERLAY_TOKEN_STRATEGIES), default="reuse_base_synthetic")
    parser.add_argument("--write-training-bundle", action="store_true")
    parser.add_argument("--bundle-path", type=Path, default=DEFAULT_BUNDLE_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frontier_limits = parse_frontier_limits(args.frontier_limits)
    repeat_counts = parse_repeat_counts(args.repeat_counts)

    backbone_rows, backbone_diagnostics = build_backbone_overlay_mix()
    measured = load_measured_signals()
    verified_candidates, verified_diagnostics = build_verified_frontier_candidates(measured)
    manual_candidates, manual_diagnostics = build_manual_frontier_candidates(measured)
    selected_frontier = select_frontier_candidates(
        verified_candidates=verified_candidates,
        manual_candidates=manual_candidates,
        frontier_limits=frontier_limits,
    )
    frontier_unique_rows, frontier_repeated_rows, frontier_selection_diagnostics = build_frontier_overlay_rows(
        selected_frontier,
        repeat_counts=repeat_counts,
    )

    combined_repeated_rows = renumber_overlay_instances(backbone_rows + frontier_repeated_rows)
    combined_unique_rows = build_unique_rows(combined_repeated_rows)

    training_bundle = None
    if args.write_training_bundle:
        training_bundle = build_training_bundle(
            repeated_rows=combined_repeated_rows,
            bundle_path=args.bundle_path.resolve(),
            overlay_token_strategy=args.overlay_token_strategy,
        )

    frontier_candidate_diagnostics = {
        "verified": verified_diagnostics,
        "manual": manual_diagnostics,
        "available_watchlist_ids": sorted(
            set(verified_diagnostics.get("available_watchlist_ids", []))
            | set(manual_diagnostics.get("available_manual_watchlist_ids", []))
        ),
    }
    validation = validate_v10(
        unique_rows=combined_unique_rows,
        repeated_rows=combined_repeated_rows,
        backbone_diagnostics=backbone_diagnostics,
        frontier_diagnostics=frontier_selection_diagnostics,
        frontier_candidate_diagnostics=frontier_candidate_diagnostics,
        training_bundle=training_bundle,
    )
    if not validation["passed"]:
        raise SystemExit("Canonical v10 validation failed: " + "; ".join(validation["errors"]))

    run_root = OUTPUT_ROOT / args.run_name
    artifacts_dir = run_root / "artifacts"
    reports_dir = run_root / "reports"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary = build_summary(
        backbone_diagnostics=backbone_diagnostics,
        frontier_candidate_diagnostics=frontier_candidate_diagnostics,
        frontier_selection_diagnostics=frontier_selection_diagnostics,
        unique_rows=combined_unique_rows,
        repeated_rows=combined_repeated_rows,
        validation=validation,
        training_bundle=training_bundle,
        frontier_limits=frontier_limits,
        repeat_counts=repeat_counts,
        overlay_token_strategy=args.overlay_token_strategy,
    )

    selection_rows = []
    for row in combined_unique_rows:
        selection_rows.append(
            {
                "id": row["id"],
                "category": row["category"],
                "bucket": row["bucket"],
                "selection_tier": row["selection_tier"],
                "template_subtype": row["template_subtype"],
                "teacher_solver_candidate": row["teacher_solver_candidate"],
                "recommended_repeat_count": row["recommended_repeat_count"],
                "assistant_styles": row["assistant_styles"],
                "source_mixes": row["source_mixes"],
                "proxy_failed": row["proxy_failed"],
                "validation_failed": row["validation_failed"],
                "hard_score": row["hard_score"],
                "binary_family_key": row.get("binary_family_key", ""),
                "audit_priority_score": row.get("audit_priority_score", ""),
                "source_tags": row["source_tags"],
            }
        )

    write_csv(
        artifacts_dir / "corrective_selection.csv",
        selection_rows,
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
            "binary_family_key",
            "audit_priority_score",
            "source_tags",
        ],
    )
    write_jsonl(artifacts_dir / "corrective_overlay_unique.jsonl", frontier_unique_rows)
    write_jsonl(artifacts_dir / "corrective_overlay_repeated.jsonl", combined_repeated_rows)
    write_json(artifacts_dir / "corrective_overlay_summary.json", summary)

    markdown = render_results_markdown(summary)
    (reports_dir / "v20_corrective_corpus_v10_mainline_summary.md").write_text(markdown, encoding="utf-8")
    RESULTS_MD.write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    main()