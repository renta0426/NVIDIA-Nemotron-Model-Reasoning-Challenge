from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_ANALYSIS_CSV = REPO_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
OUTPUT_CSV = Path(__file__).resolve().parent / "artifacts" / "binary_bias_specialized_set.csv"

QUOTAS = {
    "dominant_structured_safe": 120,
    "dominant_structured_abstract": 90,
    "supported_not_structured": 55,
    "supported_affine_xor": 60,
    "supported_bijection": 50,
    "boolean_family": 60,
    "no_solver_answer_only": 70,
    "no_solver_manual": 40,
    "rare_byte_transform": 11,
    "rare_perm_independent": 7,
}

EXPOSURE = {
    "dominant_structured_safe": "dominant",
    "dominant_structured_abstract": "dominant",
    "supported_not_structured": "supported",
    "supported_affine_xor": "supported",
    "supported_bijection": "supported",
    "boolean_family": "supported",
    "no_solver_answer_only": "underrepresented",
    "no_solver_manual": "underrepresented",
    "rare_byte_transform": "rare",
    "rare_perm_independent": "rare",
}

NOTES = {
    "dominant_structured_safe": "v1で最も厚い structured-byte exact formula 寄り slice。",
    "dominant_structured_abstract": "v1で厚い structured-byte abstract family 寄り slice。",
    "supported_not_structured": "v1では少量だが not-structured formula teacher を持つ slice。",
    "supported_affine_xor": "v1で明示的に学習量を確保した affine_xor slice。",
    "supported_bijection": "v1の rotation / bijection 系 teacher を代表する slice。",
    "boolean_family": "binary two/three-bit boolean 系で、teacher 文体転写の限界を見やすい slice。",
    "no_solver_answer_only": "teacher solver が空で answer_only_keep に寄る、v1分布の外縁 slice。",
    "no_solver_manual": "teacher solver が空で manual hard に偏る、最も壊れやすい slice。",
    "rare_byte_transform": "v1で極少量だった byte_transform 系。",
    "rare_perm_independent": "v1で極少量だった permutation_independent 系。",
}


def parse_int(value: object, default: int = 0) -> int:
    try:
        text = str(value).strip()
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


def parse_float(value: object, default: float = 0.0) -> float:
    try:
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except Exception:
        return default


def score_rank_high(row: dict[str, str]) -> tuple[object, ...]:
    hard_score = parse_float(row.get("hard_score"), -999.0)
    return (
        -hard_score,
        -parse_int(row.get("prompt_len_chars"), 0),
        -parse_int(row.get("num_examples"), 0),
        row.get("id", ""),
    )


def balanced_take(rows: list[dict[str, str]], quota: int, group_keys: tuple[str, ...]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = tuple(str(row.get(name, "") or "") for name in group_keys)
        grouped[key].append(row)
    ordered_groups = sorted(grouped.items(), key=lambda item: (item[0], len(item[1])))
    for _, group_rows in ordered_groups:
        group_rows.sort(key=score_rank_high)
    selected: list[dict[str, str]] = []
    while len(selected) < quota:
        progressed = False
        for _, group_rows in ordered_groups:
            if not group_rows:
                continue
            selected.append(group_rows.pop(0))
            progressed = True
            if len(selected) >= quota:
                break
        if not progressed:
            break
    return selected


def bucket(row: dict[str, str]) -> str | None:
    solver = (row.get("teacher_solver_candidate") or "").strip()
    tier = (row.get("selection_tier") or "").strip()
    if solver == "binary_bit_permutation_independent":
        return "rare_perm_independent"
    if solver == "binary_byte_transform":
        return "rare_byte_transform"
    if solver == "binary_affine_xor":
        return "supported_affine_xor"
    if solver == "binary_bit_permutation_bijection":
        return "supported_bijection"
    if "boolean" in solver:
        return "boolean_family"
    if row.get("template_subtype") == "bit_structured_byte_formula" and (row.get("bit_structured_formula_safe") or "").lower() == "true":
        return "dominant_structured_safe"
    if (row.get("bit_structured_formula_abstract_safe") or "").lower() == "true":
        return "dominant_structured_abstract"
    if (row.get("bit_not_structured_formula_safe") or "").lower() == "true":
        return "supported_not_structured"
    if solver == "" and tier == "answer_only_keep":
        return "no_solver_answer_only"
    if solver == "" and tier == "manual_audit_priority":
        return "no_solver_manual"
    return None


def load_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with SOURCE_ANALYSIS_CSV.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("family") != "bit_manipulation":
                continue
            if row.get("selection_tier") == "exclude_suspect":
                continue
            focus_bucket = bucket(row)
            if focus_bucket is None:
                continue
            row["v1_focus_bucket"] = focus_bucket
            row["v1_exposure_band"] = EXPOSURE[focus_bucket]
            row["v1_bucket_note"] = NOTES[focus_bucket]
            rows.append(row)
    return rows


def select_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    used_ids: set[str] = set()
    for bucket_name, quota in QUOTAS.items():
        candidates = [row for row in rows if row["v1_focus_bucket"] == bucket_name and row["id"] not in used_ids]
        picked = balanced_take(
            candidates,
            quota=quota,
            group_keys=(
                "selection_tier",
                "template_subtype",
                "teacher_solver_candidate",
                "bit_structured_formula_abstract_family",
                "group_signature",
            ),
        )
        if len(picked) != quota:
            raise RuntimeError(f"{bucket_name}: expected {quota}, got {len(picked)}")
        for row in picked:
            used_ids.add(row["id"])
            selected.append(row)
    selected.sort(
        key=lambda row: (
            row["v1_focus_bucket"],
            row.get("selection_tier", ""),
            -parse_float(row.get("hard_score"), 0.0),
            row.get("id", ""),
        )
    )
    return selected


def write_rows(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "benchmark_name",
        "benchmark_role",
        "benchmark_index",
        "id",
        "family",
        "family_short",
        "template_subtype",
        "selection_tier",
        "teacher_solver_candidate",
        "answer_type",
        "num_examples",
        "prompt_len_chars",
        "hard_score",
        "group_signature",
        "query_raw",
        "answer",
        "prompt",
        "v1_focus_bucket",
        "v1_exposure_band",
        "v1_bucket_note",
        "bit_structured_formula_name",
        "bit_structured_formula_abstract_family",
        "bit_not_structured_formula_name",
        "bit_structured_formula_safe_support",
        "bit_structured_formula_abstract_support",
        "bit_not_structured_formula_safe_support",
        "bit_no_candidate_positions",
        "bit_multi_candidate_positions",
        "query_hamming_bin",
        "audit_priority_score",
    ]
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, row in enumerate(rows, start=1):
            writer.writerow(
                {
                    "benchmark_name": "binary_bias_specialized_set",
                    "benchmark_role": "binary_bias_probe",
                    "benchmark_index": index,
                    "id": row.get("id", ""),
                    "family": row.get("family", ""),
                    "family_short": "binary",
                    "template_subtype": row.get("template_subtype", ""),
                    "selection_tier": row.get("selection_tier", ""),
                    "teacher_solver_candidate": row.get("teacher_solver_candidate", ""),
                    "answer_type": row.get("answer_type", ""),
                    "num_examples": parse_int(row.get("num_examples"), 0),
                    "prompt_len_chars": parse_int(row.get("prompt_len_chars"), 0),
                    "hard_score": parse_float(row.get("hard_score"), 0.0),
                    "group_signature": row.get("group_signature", ""),
                    "query_raw": row.get("query_raw", ""),
                    "answer": row.get("answer", ""),
                    "prompt": row.get("prompt", ""),
                    "v1_focus_bucket": row.get("v1_focus_bucket", ""),
                    "v1_exposure_band": row.get("v1_exposure_band", ""),
                    "v1_bucket_note": row.get("v1_bucket_note", ""),
                    "bit_structured_formula_name": row.get("bit_structured_formula_name", ""),
                    "bit_structured_formula_abstract_family": row.get("bit_structured_formula_abstract_family", ""),
                    "bit_not_structured_formula_name": row.get("bit_not_structured_formula_name", ""),
                    "bit_structured_formula_safe_support": parse_int(row.get("bit_structured_formula_safe_support"), 0),
                    "bit_structured_formula_abstract_support": parse_int(row.get("bit_structured_formula_abstract_support"), 0),
                    "bit_not_structured_formula_safe_support": parse_int(row.get("bit_not_structured_formula_safe_support"), 0),
                    "bit_no_candidate_positions": parse_int(row.get("bit_no_candidate_positions"), -1),
                    "bit_multi_candidate_positions": parse_int(row.get("bit_multi_candidate_positions"), -1),
                    "query_hamming_bin": parse_int(row.get("query_hamming_bin"), -1),
                    "audit_priority_score": parse_float(row.get("audit_priority_score"), 0.0),
                }
            )


def main() -> None:
    rows = load_rows()
    selected = select_rows(rows)
    write_rows(selected)
    print(f"wrote {OUTPUT_CSV}")
    print(f"rows {len(selected)}")
    print(f"bucket counts {dict(Counter(row['v1_focus_bucket'] for row in selected))}")
    print(f"tier counts {dict(Counter(row['selection_tier'] for row in selected))}")


if __name__ == "__main__":
    main()