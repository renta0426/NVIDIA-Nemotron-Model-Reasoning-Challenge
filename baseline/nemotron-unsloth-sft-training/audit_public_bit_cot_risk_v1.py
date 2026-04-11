#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import NamedTuple


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = (
    REPO_ROOT
    / "baseline"
    / "nemotron-unsloth-sft-training"
    / "artifacts"
    / "training_source_repro_public_bit_exact_original1400_v1_2026-04-11.csv"
)
DEFAULT_OUTPUT_CSV = (
    REPO_ROOT
    / "baseline"
    / "nemotron-unsloth-sft-training"
    / "artifacts"
    / "public_bit_cot_risk_audit_exact_original1400_v1.csv"
)
DEFAULT_OUTPUT_MD = (
    REPO_ROOT
    / "baseline"
    / "nemotron-unsloth-sft-training"
    / "public_bit_cot_risk_audit_exact_original1400_v1.md"
)


class BitAudit(NamedTuple):
    bit_index: int
    matching_candidates: tuple[str, ...]
    left_span: int | None
    right_span: int | None
    continuity_best: str | None
    selected: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit generated public-strategy BIT CoT rows for mechanically detectable "
            "teacher-risk patterns using the README-style final-answer contract."
        )
    )
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    return parser.parse_args()


def parse_matching_candidates(lines: list[str], start: int) -> tuple[dict[int, tuple[str, ...]], int]:
    parsed: dict[int, tuple[str, ...]] = {}
    index = start
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line == "Left / Right continuity":
            break
        parts = line.split()
        if parts and parts[0].isdigit() and len(parts[0]) == 1:
            bit_index = int(parts[0])
            parsed[bit_index] = tuple(parts[1:])
        index += 1
    return parsed, index


def parse_continuity(lines: list[str], start: int) -> tuple[dict[int, tuple[int, int, str]], int]:
    parsed: dict[int, tuple[int, int, str]] = {}
    index = start + 1
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line == "Selected":
            break
        parts = line.split()
        if len(parts) >= 4 and parts[0].isdigit():
            bit_index = int(parts[0])
            left_span = int(parts[1].split("=")[1])
            right_span = int(parts[2].split("=")[1])
            best = parts[3].split("=", 1)[1]
            parsed[bit_index] = (left_span, right_span, best)
        index += 1
    return parsed, index


def parse_selected(lines: list[str], start: int) -> dict[int, str]:
    parsed: dict[int, str] = {}
    index = start + 1
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("Applying to "):
            break
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit():
            parsed[int(parts[0])] = parts[1]
        index += 1
    return parsed


def parse_cot(cot: str) -> list[BitAudit]:
    lines = cot.splitlines()
    matching_index = next((i for i, line in enumerate(lines) if line.strip() == "Matching output"), -1)
    continuity_index = next((i for i, line in enumerate(lines) if line.strip() == "Left / Right continuity"), -1)
    selected_index = next((i for i, line in enumerate(lines) if line.strip() == "Selected"), -1)
    if matching_index < 0 or continuity_index < 0 or selected_index < 0:
        return []
    matching, _ = parse_matching_candidates(lines, matching_index + 1)
    continuity, _ = parse_continuity(lines, continuity_index)
    selected = parse_selected(lines, selected_index)

    audits: list[BitAudit] = []
    for bit_index in range(8):
        candidates = matching.get(bit_index, tuple())
        continuity_data = continuity.get(bit_index)
        if continuity_data is None:
            left_span = None
            right_span = None
            best = None
        else:
            left_span, right_span, best = continuity_data
        audits.append(
            BitAudit(
                bit_index=bit_index,
                matching_candidates=candidates,
                left_span=left_span,
                right_span=right_span,
                continuity_best=best,
                selected=selected.get(bit_index),
            )
        )
    return audits


def is_constant(token: str | None) -> bool:
    return token in {"C0", "C1"}


def summarize_row(row: dict[str, str]) -> dict[str, str]:
    audits = parse_cot(row["generated_cot"])
    flags: list[str] = []
    metrics = Counter()

    for audit in audits:
        candidates = audit.matching_candidates
        selected = audit.selected
        left_span = audit.left_span or 0
        right_span = audit.right_span or 0
        best_span = max(left_span, right_span)
        has_none = candidates == ("none",)

        if has_none:
            metrics["bits_with_none"] += 1
        if has_none and selected:
            metrics["bits_selected_after_none"] += 1
        if has_none and is_constant(selected):
            metrics["bits_constant_after_none"] += 1
        if has_none and best_span == 0 and selected:
            metrics["bits_zero_evidence_after_none"] += 1
        if has_none and best_span == 0 and is_constant(selected):
            metrics["bits_zero_evidence_constant_after_none"] += 1
        if has_none and best_span > 0 and selected:
            metrics["bits_continuity_only_after_none"] += 1
        if has_none and best_span > 0 and selected and selected != audit.continuity_best:
            metrics["bits_none_selected_not_best"] += 1
        if (
            candidates
            and candidates != ("none",)
            and selected
            and selected not in candidates
            and selected != audit.continuity_best
        ):
            metrics["bits_selected_not_in_candidates_or_best"] += 1

    if metrics["bits_zero_evidence_constant_after_none"] > 0:
        flags.append("zero_evidence_constant_fill")
    if metrics["bits_zero_evidence_after_none"] > 0:
        flags.append("zero_evidence_forced_selection")
    if metrics["bits_continuity_only_after_none"] > 0:
        flags.append("continuity_only_fill")
    if metrics["bits_selected_not_in_candidates_or_best"] > 0:
        flags.append("off_template_selection")
    if row.get("fully_supported") == "False":
        flags.append("local_partial_support")
    if int(row.get("supported_bits", "0") or 0) <= 6:
        flags.append("low_supported_bits")
    if int(row.get("total_span", "0") or 0) < 20:
        flags.append("short_total_span")

    if metrics["bits_zero_evidence_after_none"] > 0:
        risk_level = "high"
    elif metrics["bits_continuity_only_after_none"] > 0 or metrics["bits_selected_not_in_candidates_or_best"] > 0:
        risk_level = "medium"
    elif flags:
        risk_level = "low"
    else:
        risk_level = "clean"

    return {
        "id": row["id"],
        "category": row["category"],
        "source_kind": row.get("source_kind", ""),
        "answer": row["answer"],
        "supported_bits": row.get("supported_bits", ""),
        "total_span": row.get("total_span", ""),
        "fully_supported": row.get("fully_supported", ""),
        "bits_with_none": str(metrics["bits_with_none"]),
        "bits_selected_after_none": str(metrics["bits_selected_after_none"]),
        "bits_constant_after_none": str(metrics["bits_constant_after_none"]),
        "bits_zero_evidence_after_none": str(metrics["bits_zero_evidence_after_none"]),
        "bits_zero_evidence_constant_after_none": str(metrics["bits_zero_evidence_constant_after_none"]),
        "bits_continuity_only_after_none": str(metrics["bits_continuity_only_after_none"]),
        "bits_none_selected_not_best": str(metrics["bits_none_selected_not_best"]),
        "bits_selected_not_in_candidates_or_best": str(metrics["bits_selected_not_in_candidates_or_best"]),
        "risk_level": risk_level,
        "risk_flags": "|".join(flags),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, summary: dict[str, object], top_examples: list[dict[str, str]]) -> None:
    lines = [
        "# public bit CoT risk audit exact-original1400 v1",
        "",
        "## README contract",
        "",
        "- Evaluation and submission contract is taken from README.md.",
        "- Binary answers are judged by final-answer accuracy, with boxed extraction prioritized.",
        "- This audit therefore treats teacher rows as risky when the generated CoT contains mechanically detectable unsupported inference steps even if the final answer is present.",
        "",
        "## Input artifact",
        "",
        f"- source CSV: `{summary['input_csv']}`",
        f"- audited bit rows: `{summary['bit_rows']}`",
        "",
        "## Mechanical risk rules",
        "",
        "- `zero_evidence_constant_fill`: `Matching output` is `none`, `left=0`, `right=0`, and `Selected` still fixes `C0` or `C1`.",
        "- `zero_evidence_forced_selection`: `Matching output` is `none`, `left=0`, `right=0`, and `Selected` still fixes any operator.",
        "- `continuity_only_fill`: direct match is absent but `Selected` relies only on continuity extrapolation.",
        "- `off_template_selection`: `Selected` is neither in direct candidates nor equal to the stated continuity best.",
        "- `local_partial_support`: carried over from the generator metadata, used only as a secondary signal.",
        "- `low_supported_bits`: generator metadata says at most 6 of 8 bits were directly supported.",
        "- `short_total_span`: generator metadata says the continuity evidence span is short (`<20`).",
        "",
        "## Summary counts",
        "",
        f"- high risk rows: `{summary['high_risk_rows']}`",
        f"- medium risk rows: `{summary['medium_risk_rows']}`",
        f"- low risk rows: `{summary['low_risk_rows']}`",
        f"- clean rows: `{summary['clean_rows']}`",
        f"- rows with any `Matching output = none`: `{summary['rows_with_none']}`",
        f"- rows with zero-evidence forced selection: `{summary['rows_with_zero_evidence']}`",
        f"- rows with zero-evidence constant fill: `{summary['rows_with_zero_evidence_constant']}`",
        f"- rows with continuity-only fill: `{summary['rows_with_continuity_only']}`",
        f"- rows with off-template selection: `{summary['rows_with_off_template']}`",
        "",
        "## Top flagged examples",
        "",
        "| id | fully_supported | supported_bits | total_span | risk_level | risk_flags | zero_evidence_bits | continuity_only_bits |",
        "| --- | --- | ---: | ---: | --- | --- | ---: | ---: |",
    ]
    for row in top_examples:
        lines.append(
            "| {id} | {fully_supported} | {supported_bits} | {total_span} | {risk_level} | {risk_flags} | {bits_zero_evidence_after_none} | {bits_continuity_only_after_none} |".format(
                **row
            )
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- This audit is artifact-level: it judges the generated CoT text that is actually being trained on.",
        "- It does not prove that the underlying public strategy can never justify these rows under a better implementation.",
        "- It does show which rows, in the current artifact, contain mechanically detectable unsupported or weakly supported inference steps and should be down-weighted, filtered, or re-generated before SFT.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    audited_rows: list[dict[str, str]] = []
    with args.input_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("category") != "bit_manipulation":
                continue
            audited_rows.append(summarize_row(row))

    write_csv(args.output_csv, audited_rows)

    by_risk = Counter(row["risk_level"] for row in audited_rows)
    summary = {
        "input_csv": str(args.input_csv.relative_to(REPO_ROOT)),
        "bit_rows": len(audited_rows),
        "high_risk_rows": by_risk["high"],
        "medium_risk_rows": by_risk["medium"],
        "low_risk_rows": by_risk["low"],
        "clean_rows": by_risk["clean"],
        "rows_with_none": sum(int(row["bits_with_none"]) > 0 for row in audited_rows),
        "rows_with_zero_evidence": sum(int(row["bits_zero_evidence_after_none"]) > 0 for row in audited_rows),
        "rows_with_zero_evidence_constant": sum(
            int(row["bits_zero_evidence_constant_after_none"]) > 0 for row in audited_rows
        ),
        "rows_with_continuity_only": sum(int(row["bits_continuity_only_after_none"]) > 0 for row in audited_rows),
        "rows_with_off_template": sum(
            int(row["bits_selected_not_in_candidates_or_best"]) > 0 for row in audited_rows
        ),
    }

    top_examples = sorted(
        audited_rows,
        key=lambda row: (
            {"high": 0, "medium": 1, "low": 2, "clean": 3}[row["risk_level"]],
            -int(row["bits_zero_evidence_after_none"]),
            -int(row["bits_continuity_only_after_none"]),
            int(row["supported_bits"] or 0),
            row["id"],
        ),
    )[:15]
    write_markdown(args.output_md, summary, top_examples)

    print("audited_bit_rows", len(audited_rows))
    print("high_risk_rows", by_risk["high"])
    print("medium_risk_rows", by_risk["medium"])
    print("low_risk_rows", by_risk["low"])
    print("clean_rows", by_risk["clean"])
    print("rows_with_zero_evidence", summary["rows_with_zero_evidence"])
    print("rows_with_continuity_only", summary["rows_with_continuity_only"])
    print("rows_with_off_template", summary["rows_with_off_template"])
    print("output_csv", args.output_csv)
    print("output_md", args.output_md)


if __name__ == "__main__":
    main()