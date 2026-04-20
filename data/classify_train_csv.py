from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


README_EXPECTED_FINAL_COUNTS = {
    "cryptarithm_guess": 164,
    "cryptarithm_deduce": 659,
    "equation_numeric_guess": 136,
    "equation_numeric_deduce": 596,
    "bit_manipulation": 1602,
    "cipher": 1576,
    "gravity": 1597,
    "unit_conversion": 1594,
    "numeral": 1576,
}

README_EXPECTED_MAJOR_COUNTS = {
    "bit_manipulation": 1602,
    "cipher": 1576,
    "gravity": 1597,
    "unit_conversion": 1594,
    "numeral": 1576,
    "equation": 1555,
}

PROMPT_PATTERNS = {
    "bit_manipulation": "a secret bit manipulation rule transforms 8-bit binary numbers",
    "cipher": "secret encryption rules are used on text",
    "gravity": "the gravitational constant has been secretly changed",
    "unit_conversion": "a secret unit conversion is applied to measurements",
    "numeral": "numbers are secretly converted into a different numeral system",
    "equation": "a secret set of transformation rules is applied to equations",
}

NUMERIC_OPERATOR_RE = re.compile(r"\d+([^\d\s])\d+")
TARGET_PREFIX = "Now, determine the result for: "


def get_default_paths() -> tuple[Path, Path, Path]:
    repo_root = Path(__file__).resolve().parent
    input_path = repo_root / "data" / "train.csv"
    output_path = repo_root / "data" / "train_with_classification.csv"
    report_path = repo_root / "train_csv_problem_type_classification_2026-04-20.md"
    return input_path, output_path, report_path


def build_parser() -> argparse.ArgumentParser:
    input_path, output_path, report_path = get_default_paths()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=input_path)
    parser.add_argument("--output", type=Path, default=output_path)
    parser.add_argument("--report", type=Path, default=report_path)
    return parser


def find_major_category(prompt: str) -> str:
    for label, pattern in PROMPT_PATTERNS.items():
        if pattern in prompt:
            return label
    raise ValueError("Unrecognized prompt pattern")


def extract_equation_parts(prompt: str) -> tuple[list[str], str]:
    lines = prompt.splitlines()
    example_lines = [line for line in lines if " = " in line]
    target_line = next(line for line in lines if line.startswith(TARGET_PREFIX))
    target_expr = target_line.split(TARGET_PREFIX, 1)[1]
    return example_lines, target_expr


def classify_equation_prompt(prompt: str) -> tuple[str, str, str, dict[str, int | str]]:
    example_lines, target_expr = extract_equation_parts(prompt)
    joined_examples = "".join(example_lines)

    if any(ch.isdigit() for ch in joined_examples):
        example_ops = []
        for line in example_lines:
            lhs = line.split(" = ", 1)[0]
            match = NUMERIC_OPERATOR_RE.search(lhs)
            if match is None:
                raise ValueError(f"Could not extract numeric operator from: {lhs}")
            example_ops.append(match.group(1))

        target_match = NUMERIC_OPERATOR_RE.search(target_expr)
        if target_match is None:
            raise ValueError(f"Could not extract numeric target operator from: {target_expr}")
        target_op = target_match.group(1)
        difficulty = "deduce" if target_op in example_ops else "guess"
        final_label = f"equation_numeric_{difficulty}"
        metadata = {
            "example_count": len(example_lines),
            "unseen_any": 0,
            "only_rhs": 0,
            "target_operator_seen": int(target_op in example_ops),
        }
        return "equation_numeric", difficulty, final_label, metadata

    lhs_chars: set[str] = set()
    rhs_chars: set[str] = set()
    all_chars: set[str] = set()
    for line in example_lines:
        lhs, rhs = line.split(" = ", 1)
        lhs_chars.update(lhs)
        rhs_chars.update(rhs)
        all_chars.update(lhs)
        all_chars.update(rhs)

    target_chars = set(target_expr)
    unseen_any = len(target_chars - all_chars)
    only_rhs = len({ch for ch in target_chars if ch in rhs_chars and ch not in lhs_chars})
    is_guess = len(example_lines) >= 4 and unseen_any == 1 and only_rhs <= 1
    difficulty = "guess" if is_guess else "deduce"
    final_label = f"cryptarithm_{difficulty}"
    metadata = {
        "example_count": len(example_lines),
        "unseen_any": unseen_any,
        "only_rhs": only_rhs,
        "target_operator_seen": 0,
    }
    return "cryptarithm", difficulty, final_label, metadata


def classify_row(row: dict[str, str]) -> dict[str, str | int]:
    prompt = row["prompt"]
    major_category = find_major_category(prompt)

    if major_category != "equation":
        return {
            **row,
            "major_category": major_category,
            "equation_family": "",
            "difficulty_split": "",
            "final_label": major_category,
            "example_count": "",
            "unseen_any": "",
            "only_rhs": "",
            "target_operator_seen": "",
        }

    equation_family, difficulty, final_label, metadata = classify_equation_prompt(prompt)
    return {
        **row,
        "major_category": major_category,
        "equation_family": equation_family,
        "difficulty_split": difficulty,
        "final_label": final_label,
        "example_count": metadata["example_count"],
        "unseen_any": metadata["unseen_any"],
        "only_rhs": metadata["only_rhs"],
        "target_operator_seen": metadata["target_operator_seen"],
    }


def validate_counts(labeled_rows: list[dict[str, str | int]]) -> tuple[Counter, Counter]:
    final_counts = Counter(str(row["final_label"]) for row in labeled_rows)
    major_counts = Counter(str(row["major_category"]) for row in labeled_rows)

    if dict(final_counts) != README_EXPECTED_FINAL_COUNTS:
        raise ValueError(
            f"Final label counts mismatch. Expected {README_EXPECTED_FINAL_COUNTS}, got {dict(final_counts)}"
        )
    if dict(major_counts) != README_EXPECTED_MAJOR_COUNTS:
        raise ValueError(
            f"Major category counts mismatch. Expected {README_EXPECTED_MAJOR_COUNTS}, got {dict(major_counts)}"
        )

    return final_counts, major_counts


def write_csv(path: Path, labeled_rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(labeled_rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(labeled_rows)


def build_report(final_counts: Counter, major_counts: Counter, output_path: Path) -> str:
    lines = [
        "# Train CSV Problem Type Classification (2026-04-20)",
        "",
        "## Input Scope",
        "",
        "- Source data: data/train.csv",
        "- Reference counts: README.md tail section and discussion/Are problem types the same for train and test?.md",
        "- Original data file was not modified",
        "",
        "## Major Categories",
        "",
    ]

    for label in ["bit_manipulation", "cipher", "gravity", "unit_conversion", "numeral", "equation"]:
        lines.append(f"- {label}: {major_counts[label]}")

    lines.extend(
        [
            "",
            "## Equation Split Rules",
            "",
            "- equation_numeric_deduce: numeric equation prompts where the target operator appears in the example equations.",
            "- equation_numeric_guess: numeric equation prompts where the target operator does not appear in the example equations.",
            "- cryptarithm_guess: symbolic equation prompts with at least 4 examples, exactly 1 target symbol unseen anywhere in the example equations, and at most 1 target symbol that appeared only on example right-hand sides.",
            "- cryptarithm_deduce: remaining symbolic equation prompts.",
            "",
            "## Final Label Counts",
            "",
        ]
    )

    for label in [
        "cryptarithm_guess",
        "cryptarithm_deduce",
        "equation_numeric_guess",
        "equation_numeric_deduce",
        "bit_manipulation",
        "cipher",
        "gravity",
        "unit_conversion",
        "numeral",
    ]:
        lines.append(f"- {label}: {final_counts[label]}")

    lines.extend(
        [
            "",
            "## Generated Artifacts",
            "",
            f"- Classification CSV: {output_path.as_posix()}",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    with args.input.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    labeled_rows = [classify_row(row) for row in rows]
    final_counts, major_counts = validate_counts(labeled_rows)
    write_csv(args.output, labeled_rows)
    write_report(args.report, build_report(final_counts, major_counts, args.output))

    print(f"wrote {args.output}")
    print(f"wrote {args.report}")
    print("major_counts", dict(major_counts))
    print("final_counts", dict(final_counts))


if __name__ == "__main__":
    main()