from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any

import pandas as pd

TEMPLATE_PREFIX_TO_NAME = {
    "In Alice's Wonderland, a secret bit manipulation rule transforms 8-bit binary numbers.": "bit_manipulation",
    "In Alice's Wonderland, the gravitational constant has been secretly changed.": "gravity_constant",
    "In Alice's Wonderland, a secret unit conversion is applied to measurements.": "unit_conversion",
    "In Alice's Wonderland, secret encryption rules are used on text.": "text_decryption",
    "In Alice's Wonderland, numbers are secretly converted into a different numeral system.": "roman_numeral",
    "In Alice's Wonderland, a secret set of transformation rules is applied to equations.": "symbol_equation",
}

PROMPT_BLOCK_MARKERS = {
    "bit_manipulation": (
        "\n\nHere are some examples of input -> output:\n",
        "\n\nNow, determine the output for: ",
    ),
    "gravity_constant": (
        "Here are some example observations:\n",
        "\nNow, determine the falling distance for t = ",
    ),
    "unit_conversion": (
        "For example:\n",
        "\nNow, convert the following measurement: ",
    ),
    "text_decryption": (
        "Here are some examples:\n",
        "\nNow, decrypt the following text: ",
    ),
    "roman_numeral": (
        "Some examples are given below:\n",
        "\nNow, write the number ",
    ),
    "symbol_equation": (
        "Below are a few examples:\n",
        "\nNow, determine the result for: ",
    ),
}

GENERATOR_VERSION = "v8_prompt_order_projection_v1"
DEFAULT_SEED = 20260319
DEFAULT_COPIES_PER_ROW = 2
DEFAULT_MAX_ATTEMPTS_PER_ROW = 24
SYNTHETIC_ID_PREFIX = "synth_v8"


def detect_template(prompt: str) -> str:
    stripped = prompt.strip()
    for prefix, name in TEMPLATE_PREFIX_TO_NAME.items():
        if stripped.startswith(prefix):
            return name

    lower = stripped.lower()
    if "bit manipulation" in lower:
        return "bit_manipulation"
    if "gravitational constant" in lower:
        return "gravity_constant"
    if "unit conversion" in lower:
        return "unit_conversion"
    if "encryption rules are used on text" in lower or "decrypt the following text" in lower:
        return "text_decryption"
    if "different numeral system" in lower:
        return "roman_numeral"
    if "transformation rules is applied to equations" in lower or "determine the result for" in lower:
        return "symbol_equation"
    raise ValueError("Could not detect template family for prompt.")


def detect_answer_type(answer: Any) -> str:
    text = str(answer).strip()
    if re.fullmatch(r"[01]{8}", text):
        return "binary8"
    if re.fullmatch(r"[IVXLCDM]+", text):
        return "roman"
    if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", text):
        return "numeric"
    if " " in text:
        return "text_phrase"
    return "symbolic"


def detect_template_subfamily(template_family: str, answer_type: str) -> str:
    if template_family != "symbol_equation":
        return ""
    if answer_type == "numeric":
        return "symbol_equation_numeric"
    return "symbol_equation_symbolic"


def normalize_prompt(prompt: str) -> str:
    return "\n".join(line.rstrip() for line in prompt.strip().splitlines())


def make_prompt_hash(prompt: str) -> str:
    return hashlib.sha256(normalize_prompt(prompt).encode("utf-8")).hexdigest()


def make_dedup_hash(prompt: str, answer: Any) -> str:
    payload = f"{normalize_prompt(prompt)}\t{str(answer).strip()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_format_risk_flags(answer: Any) -> str:
    text = str(answer)
    flags: list[str] = []
    if "}" in text:
        flags.append("contains_right_brace")
    if "\\" in text:
        flags.append("contains_backslash")
    if "`" in text:
        flags.append("contains_backtick")
    return "|".join(flags)


def make_difficulty_tags(template_family: str) -> str:
    tags = ["prompt_reorder"]
    if template_family in {"bit_manipulation", "text_decryption", "symbol_equation"}:
        tags.append("hard_template")
    return "|".join(tags)


def validate_answer_format(answer_type: str, answer: Any) -> bool:
    text = str(answer).strip()
    if answer_type == "binary8":
        return re.fullmatch(r"[01]{8}", text) is not None
    if answer_type == "roman":
        return re.fullmatch(r"[IVXLCDM]+", text) is not None
    if answer_type == "numeric":
        return re.fullmatch(r"[-+]?\d+(?:\.\d+)?", text) is not None
    if answer_type == "text_phrase":
        return bool(text) and " " in text
    return bool(text)


def count_examples(prompt: str, template_family: str) -> int:
    start_marker, end_marker = PROMPT_BLOCK_MARKERS[template_family]
    _, rest = prompt.split(start_marker, 1)
    middle, _ = rest.split(end_marker, 1)
    return len([line for line in middle.splitlines() if line.strip()])


def shuffle_example_lines(prompt: str, template_family: str, seed: int) -> str:
    start_marker, end_marker = PROMPT_BLOCK_MARKERS[template_family]
    if start_marker not in prompt or end_marker not in prompt:
        raise ValueError(f"Prompt markers not found for template: {template_family}")

    prefix, rest = prompt.split(start_marker, 1)
    middle, suffix = rest.split(end_marker, 1)
    lines = [line for line in middle.splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError(f"Need at least two example lines to reorder for template: {template_family}")

    rng = random.Random(seed)
    shuffled = lines[:]
    for _ in range(5):
        rng.shuffle(shuffled)
        if shuffled != lines:
            break
    if shuffled == lines:
        return prompt
    return prefix + start_marker + "\n".join(shuffled) + end_marker + suffix


def choose_base_test_path(visible_backup_path: Path, projected_test_path: Path) -> Path:
    if visible_backup_path.exists():
        return visible_backup_path
    return projected_test_path


def load_base_visible_test(train_path: Path, base_test_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_df = pd.read_csv(train_path)
    visible_test_df = pd.read_csv(base_test_path)

    if list(visible_test_df.columns) != ["id", "prompt"]:
        visible_test_df = visible_test_df.loc[:, ["id", "prompt"]].copy()

    answer_by_id = train_df.set_index("id")["answer"]
    prompt_by_id = train_df.set_index("id")["prompt"]

    base_df = visible_test_df.copy()
    base_df["answer"] = base_df["id"].map(answer_by_id)
    base_df["train_prompt"] = base_df["id"].map(prompt_by_id)

    if base_df["answer"].isna().any():
        missing_ids = sorted(base_df.loc[base_df["answer"].isna(), "id"].tolist())
        raise ValueError(f"Could not recover answers for visible test ids: {missing_ids}")

    mismatched = base_df["prompt"] != base_df["train_prompt"]
    if mismatched.any():
        bad_ids = sorted(base_df.loc[mismatched, "id"].tolist())
        raise ValueError(f"Visible test prompt mismatch against train.csv for ids: {bad_ids}")

    base_df = base_df.drop(columns=["train_prompt"])
    return train_df, base_df


def generate_manifest(
    train_df: pd.DataFrame,
    base_df: pd.DataFrame,
    copies_per_row: int,
    seed: int,
    max_attempts_per_row: int,
) -> pd.DataFrame:
    seen_prompt_hashes = {make_prompt_hash(prompt) for prompt in train_df["prompt"]}
    seen_dedup_hashes = {
        make_dedup_hash(prompt, answer)
        for prompt, answer in zip(train_df["prompt"], train_df["answer"], strict=False)
    }

    manifest_rows: list[dict[str, Any]] = []
    for row_index, row in enumerate(base_df.to_dict("records")):
        template_family = detect_template(row["prompt"])
        answer_type = detect_answer_type(row["answer"])
        if not validate_answer_format(answer_type, row["answer"]):
            raise ValueError(f"Unexpected answer format for base row {row['id']}: {row['answer']}")

        local_prompt_hashes: set[str] = set()
        accepted = 0
        attempts = 0
        while accepted < copies_per_row and attempts < max_attempts_per_row:
            current_seed = seed + (row_index * 1000) + attempts
            attempts += 1
            augmented_prompt = shuffle_example_lines(row["prompt"], template_family, current_seed)
            prompt_hash = make_prompt_hash(augmented_prompt)
            dedup_hash = make_dedup_hash(augmented_prompt, row["answer"])
            if augmented_prompt == row["prompt"]:
                continue
            if prompt_hash in seen_prompt_hashes or prompt_hash in local_prompt_hashes:
                continue
            if dedup_hash in seen_dedup_hashes:
                continue
            if detect_template(augmented_prompt) != template_family:
                continue
            if len(augmented_prompt) != len(row["prompt"]):
                continue

            synthetic_id = f"{SYNTHETIC_ID_PREFIX}_{row['id']}_{accepted + 1:02d}"
            rule_spec = json.dumps(
                {
                    "base_id": row["id"],
                    "base_prompt_hash": make_prompt_hash(row["prompt"]),
                    "example_count": count_examples(row["prompt"], template_family),
                    "seed": current_seed,
                    "type": "prompt_example_order_permutation",
                },
                ensure_ascii=True,
                sort_keys=True,
            )

            manifest_rows.append(
                {
                    "synthetic_id": synthetic_id,
                    "source_id": row["id"],
                    "template_family": template_family,
                    "template_subfamily": detect_template_subfamily(template_family, answer_type),
                    "prompt": augmented_prompt,
                    "answer": str(row["answer"]).strip(),
                    "answer_type": answer_type,
                    "generator_type": "programmatic",
                    "generator_version": GENERATOR_VERSION,
                    "rule_spec": rule_spec,
                    "difficulty_tags": make_difficulty_tags(template_family),
                    "seed": current_seed,
                    "dedup_hash": dedup_hash,
                    "format_risk_flags": make_format_risk_flags(row["answer"]),
                    "split_policy": "train_only",
                    "accepted_by": "train_answer_lookup|template_guard|format_guard|length_guard|exact_dedup_guard|copy_cap_guard",
                }
            )
            seen_prompt_hashes.add(prompt_hash)
            seen_dedup_hashes.add(dedup_hash)
            local_prompt_hashes.add(prompt_hash)
            accepted += 1

        if accepted < copies_per_row:
            raise ValueError(
                f"Could only generate {accepted} augmentations for {row['id']} "
                f"before reaching the attempt cap of {max_attempts_per_row}."
            )

    manifest_df = pd.DataFrame(manifest_rows)
    if manifest_df.empty:
        raise ValueError("No synthetic rows were generated.")
    return manifest_df


def write_outputs(
    base_df: pd.DataFrame,
    manifest_df: pd.DataFrame,
    visible_backup_path: Path,
    projected_test_path: Path,
    manifest_path: Path,
) -> None:
    visible_backup_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    base_df.loc[:, ["id", "prompt"]].to_csv(visible_backup_path, index=False)
    manifest_df.to_csv(manifest_path, index=False)

    projected_df = pd.concat(
        [
            base_df.loc[:, ["id", "prompt"]],
            manifest_df.loc[:, ["synthetic_id", "prompt"]].rename(columns={"synthetic_id": "id"}),
        ],
        ignore_index=True,
    )
    projected_df.to_csv(projected_test_path, index=False)


def build_summary(base_df: pd.DataFrame, manifest_df: pd.DataFrame, projected_test_path: Path, manifest_path: Path) -> dict[str, Any]:
    return {
        "base_rows": int(len(base_df)),
        "synthetic_rows": int(len(manifest_df)),
        "projected_rows": int(len(base_df) + len(manifest_df)),
        "templates": manifest_df["template_family"].value_counts().sort_index().to_dict(),
        "output_test_path": str(projected_test_path),
        "output_manifest_path": str(manifest_path),
    }


def main() -> None:
    script_dir = Path(__file__).resolve()
    repo_root = script_dir.parents[3]
    data_dir = repo_root / "data"

    parser = argparse.ArgumentParser(description="Build a policy-compliant augmented prompt-only test view.")
    parser.add_argument("--train-path", type=Path, default=data_dir / "train.csv")
    parser.add_argument("--projected-test-path", type=Path, default=data_dir / "test.csv")
    parser.add_argument("--manifest-path", type=Path, default=data_dir / "test_augmented_manifest.csv")
    parser.add_argument("--visible-backup-path", type=Path, default=data_dir / "test.visible.csv")
    parser.add_argument("--copies-per-row", type=int, default=DEFAULT_COPIES_PER_ROW)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--max-attempts-per-row", type=int, default=DEFAULT_MAX_ATTEMPTS_PER_ROW)
    args = parser.parse_args()

    base_test_path = choose_base_test_path(
        visible_backup_path=args.visible_backup_path,
        projected_test_path=args.projected_test_path,
    )
    train_df, base_df = load_base_visible_test(args.train_path, base_test_path)
    manifest_df = generate_manifest(
        train_df=train_df,
        base_df=base_df,
        copies_per_row=args.copies_per_row,
        seed=args.seed,
        max_attempts_per_row=args.max_attempts_per_row,
    )
    write_outputs(
        base_df=base_df,
        manifest_df=manifest_df,
        visible_backup_path=args.visible_backup_path,
        projected_test_path=args.projected_test_path,
        manifest_path=args.manifest_path,
    )

    summary = build_summary(
        base_df=base_df,
        manifest_df=manifest_df,
        projected_test_path=args.projected_test_path,
        manifest_path=args.manifest_path,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
