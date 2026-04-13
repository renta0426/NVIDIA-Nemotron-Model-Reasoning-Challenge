#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"

DATASET_CSV = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "artifacts"
    / "train_split_with_cot_v3f_safe_plus_notformula.csv"
)
PHASE0_SUMMARY_JSON = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "result"
    / "v3f"
    / "phase0_offline_eval"
    / "artifacts"
    / "phase0_eval_summary.json"
)
PHASE0_MANIFEST_JSON = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "result"
    / "v3f"
    / "phase0_offline_eval"
    / "artifacts"
    / "phase0_eval_manifest.json"
)
SPECIALIZED_SUMMARY_JSON = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "result"
    / "v3f"
    / "phase0_offline_eval_binary_bias_specialized"
    / "artifacts"
    / "binary_bias_specialized_eval_summary.json"
)
PROXY_SUMMARY_JSON = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "result"
    / "v3f"
    / "leaderboard_proxy_eval"
    / "artifacts"
    / "leaderboard_proxy_eval_summary.json"
)
PROXY_MANIFEST_JSON = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "result"
    / "v3f"
    / "leaderboard_proxy_eval"
    / "artifacts"
    / "leaderboard_proxy_eval_manifest.json"
)
CORRECTION_MD = (
    REPO_ROOT
    / "cuda-train-data-analysis-v1"
    / "proof_first_solver_factory_routing"
    / "result"
    / "LEADERBOARD_GAP_INVESTIGATION_2026-04-09.md"
)
V3F_EFFECTS_MD = (
    REPO_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "result"
    / "v3f"
    / "v3f_effects_risks_and_next_strategy.md"
)
BUNDLE_MANIFEST_JSON = (
    REPO_ROOT
    / "baseline_mlx"
    / "outputs"
    / "nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage1_broad_v3f_union"
    / "mlx_adapter_bundle"
    / "bundle_manifest.json"
)
RESULTS_MD = REPO_ROOT / "versions" / "baseline_mlx" / "baseline_mlx-results.md"

README_CONTRACT = {
    "max_lora_rank": 32,
    "max_tokens": 7680,
    "top_p": 1.0,
    "temperature": 0.0,
    "max_num_seqs": 64,
    "gpu_memory_utilization": 0.85,
    "max_model_len": 8192,
}
SUMMARY_SCHEMA_VERSION = 2

EXPECTED_STORED_LOCAL = {"correct": 249, "rows": 320, "accuracy": 249 / 320}
EXPECTED_CORRECTED_LOCAL = {"correct": 240, "rows": 320, "accuracy": 240 / 320}
EXPECTED_CORRECTED_BINARY = {"correct": 18, "rows": 60, "accuracy": 18 / 60}
EXPECTED_PROXY_ACTUAL = {"correct": 133, "rows": 200, "accuracy": 133 / 200}
EXPECTED_SPECIALIZED = {"correct": 238, "rows": 563, "accuracy": 238 / 563}
EXPECTED_SUPPORTED_NOT_STRUCTURED = {"correct": 1, "rows": 55, "accuracy": 1 / 55}
EXPECTED_NOT_FORMULA = {"correct": 1, "rows": 25, "accuracy": 1 / 25}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def approx_equal(lhs: float, rhs: float, tol: float = 1e-6) -> bool:
    return math.isclose(lhs, rhs, rel_tol=0.0, abs_tol=tol)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def dump_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def format_inline_list(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def build_readme_contract_state(
    payload: dict[str, Any],
    *,
    max_lora_rank_required: bool,
) -> dict[str, Any]:
    expected_keys = [
        key for key in sorted(README_CONTRACT) if max_lora_rank_required or key != "max_lora_rank"
    ]
    actual_keys = sorted(payload)
    allowed_keys = expected_keys + ([] if max_lora_rank_required else ["max_lora_rank"])
    missing_keys = [key for key in expected_keys if key not in payload]
    unexpected_keys = [key for key in actual_keys if key not in allowed_keys]
    mismatched_keys = [key for key in expected_keys if key in payload and payload.get(key) != README_CONTRACT[key]]
    return {
        "expected_key_count": len(expected_keys),
        "actual_key_count": len(actual_keys),
        "expected_keys": expected_keys,
        "actual_keys": actual_keys,
        "missing_keys": missing_keys,
        "unexpected_keys": unexpected_keys,
        "mismatched_keys": mismatched_keys,
        "matches_current_readme": not missing_keys and not unexpected_keys and not mismatched_keys,
    }


def load_readme_contract_from_readme(*, max_lora_rank_required: bool) -> dict[str, Any]:
    text = README_PATH.read_text(encoding="utf-8")
    contract: dict[str, Any] = {}
    for key, expected_value in README_CONTRACT.items():
        if key == "max_lora_rank" and not max_lora_rank_required:
            continue
        needle = f"{key}\t"
        for line in text.splitlines():
            if line.startswith(needle):
                parts = line.split("\t", 1)
                require(len(parts) == 2, f"Malformed README.md evaluation row for {key}: {line!r}")
                raw_value = parts[1].strip()
                require(raw_value != "", f"Malformed README.md evaluation row for {key}: missing value")
                try:
                    if isinstance(expected_value, int) and not isinstance(expected_value, bool):
                        contract[key] = int(raw_value)
                    else:
                        contract[key] = float(raw_value)
                except ValueError as exc:
                    raise SystemExit(f"Malformed README.md evaluation value for {key}: {raw_value!r}") from exc
                break
    missing_keys = [
        key for key in README_CONTRACT if (max_lora_rank_required or key != "max_lora_rank") and key not in contract
    ]
    require(
        not missing_keys,
        f"Missing README.md evaluation rows: {', '.join(missing_keys)}",
    )
    return contract


def verify_readme_contract_file(*, max_lora_rank_required: bool) -> dict[str, Any]:
    contract = load_readme_contract_from_readme(max_lora_rank_required=max_lora_rank_required)
    for key, expected_value in README_CONTRACT.items():
        if key == "max_lora_rank" and not max_lora_rank_required:
            continue
        actual_value = contract.get(key)
        require(
            actual_value == expected_value,
            f"README.md evaluation table mismatch for {key}: expected {expected_value}, got {actual_value}",
        )
    return contract


def find_accuracy_row(rows: list[dict[str, Any]], *, key: str, expected: str) -> dict[str, Any]:
    for row in rows:
        if row.get(key) == expected:
            return row
    raise SystemExit(f"Missing row where {key}={expected!r}")


def verify_readme_contract(payload: dict[str, Any], *, max_lora_rank_required: bool) -> None:
    for key, expected_value in README_CONTRACT.items():
        if key == "max_lora_rank" and not max_lora_rank_required:
            continue
        actual_value = payload.get(key)
        require(actual_value == expected_value, f"README contract mismatch for {key}: {actual_value!r}")


def parse_metric_cell(cell: str) -> dict[str, Any]:
    match = re.fullmatch(r"(\d+)/(\d+)\s*=\s*([0-9.]+)", cell.strip())
    require(match is not None, f"Unexpected metric cell: {cell!r}")
    correct, rows, accuracy = match.groups()
    return {
        "correct": int(correct),
        "rows": int(rows),
        "accuracy": float(accuracy),
    }


def parse_correction_rows() -> tuple[dict[str, Any], dict[str, Any]]:
    text = CORRECTION_MD.read_text(encoding="utf-8")
    corrected_match = re.search(
        r"\| `v3f` \| `(?P<stored>[^`]+)` \| `(?P<corrected>[^`]+)` \| `(?P<binary>[^`]+)` \|",
        text,
    )
    require(corrected_match is not None, f"Missing corrected v3f row in {CORRECTION_MD}")
    proxy_match = re.search(
        r"\| `v3f` \| `(?P<design>143/200 = 0\.7150)` \| `(?P<actual>133/200 = 0\.6650)` \|",
        text,
    )
    require(proxy_match is not None, f"Missing proxy v3f row in {CORRECTION_MD}")
    return (
        {
            "stored_phase0_local320": parse_metric_cell(corrected_match.group("stored")),
            "corrected_phase0_local320": parse_metric_cell(corrected_match.group("corrected")),
            "corrected_binary_hard": parse_metric_cell(corrected_match.group("binary")),
        },
        {
            "proxy_design": parse_metric_cell(proxy_match.group("design")),
            "proxy_actual": parse_metric_cell(proxy_match.group("actual")),
        },
    )


def verify_expected_metric(actual: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    require(actual["correct"] == expected["correct"], f"{label} correct mismatch: {actual}")
    require(actual["rows"] == expected["rows"], f"{label} rows mismatch: {actual}")
    require(
        approx_equal(float(actual["accuracy"]), float(expected["accuracy"]), tol=1e-4),
        f"{label} accuracy mismatch: {actual}",
    )


def build_summary() -> dict[str, Any]:
    for path in (
        README_PATH,
        DATASET_CSV,
        PHASE0_SUMMARY_JSON,
        PHASE0_MANIFEST_JSON,
        SPECIALIZED_SUMMARY_JSON,
        PROXY_SUMMARY_JSON,
        PROXY_MANIFEST_JSON,
        CORRECTION_MD,
        V3F_EFFECTS_MD,
        BUNDLE_MANIFEST_JSON,
    ):
        require(path.exists(), f"Required path does not exist: {path}")

    verify_readme_contract_file(max_lora_rank_required=True)
    phase0_summary = load_json(PHASE0_SUMMARY_JSON)
    phase0_manifest = load_json(PHASE0_MANIFEST_JSON)
    specialized_summary = load_json(SPECIALIZED_SUMMARY_JSON)
    proxy_summary = load_json(PROXY_SUMMARY_JSON)
    proxy_manifest = load_json(PROXY_MANIFEST_JSON)
    bundle_manifest = load_json(BUNDLE_MANIFEST_JSON)
    phase0_readme_assumptions = phase0_manifest["manifest"]["readme_eval_assumptions"]
    proxy_readme_assumptions = proxy_manifest["manifest"]["readme_eval_assumptions"]
    specialized_readme_assumptions = specialized_summary["manifest"]["readme_eval_assumptions"]

    verify_readme_contract(phase0_readme_assumptions, max_lora_rank_required=False)
    verify_readme_contract(proxy_readme_assumptions, max_lora_rank_required=True)
    verify_readme_contract(specialized_readme_assumptions, max_lora_rank_required=False)

    stored_local = phase0_summary["overall"]["overall"]
    verify_expected_metric(stored_local, EXPECTED_STORED_LOCAL, "stored_phase0_local320")

    proxy_overall = proxy_summary["overall"]["overall"]
    verify_expected_metric(proxy_overall, EXPECTED_PROXY_ACTUAL, "proxy_actual")

    specialized_overall = specialized_summary["overall"]["overall"]
    verify_expected_metric(specialized_overall, EXPECTED_SPECIALIZED, "specialized563")

    corrected_rows, proxy_rows = parse_correction_rows()
    verify_expected_metric(
        corrected_rows["stored_phase0_local320"],
        EXPECTED_STORED_LOCAL,
        "corrected_table.stored_phase0_local320",
    )
    verify_expected_metric(
        corrected_rows["corrected_phase0_local320"],
        EXPECTED_CORRECTED_LOCAL,
        "corrected_table.corrected_phase0_local320",
    )
    verify_expected_metric(
        corrected_rows["corrected_binary_hard"],
        EXPECTED_CORRECTED_BINARY,
        "corrected_table.corrected_binary_hard",
    )
    verify_expected_metric(proxy_rows["proxy_actual"], EXPECTED_PROXY_ACTUAL, "corrected_table.proxy_actual")

    phase0_family_binary = find_accuracy_row(phase0_summary["overall"]["by_family"], key="family_short", expected="binary")
    phase0_family_symbol = find_accuracy_row(phase0_summary["overall"]["by_family"], key="family_short", expected="symbol")
    dominant_structured_safe = find_accuracy_row(
        specialized_summary["overall"]["by_focus_bucket"],
        key="v1_focus_bucket",
        expected="dominant_structured_safe",
    )
    supported_bijection = find_accuracy_row(
        specialized_summary["overall"]["by_focus_bucket"],
        key="v1_focus_bucket",
        expected="supported_bijection",
    )
    supported_not_structured = find_accuracy_row(
        specialized_summary["overall"]["by_focus_bucket"],
        key="v1_focus_bucket",
        expected="supported_not_structured",
    )
    specialized_not_formula = find_accuracy_row(
        specialized_summary["overall"]["binary_metrics"]["solver_family_accuracy"],
        key="teacher_solver_candidate",
        expected="binary_structured_byte_not_formula",
    )
    verify_expected_metric(supported_not_structured, EXPECTED_SUPPORTED_NOT_STRUCTURED, "supported_not_structured")
    verify_expected_metric(specialized_not_formula, EXPECTED_NOT_FORMULA, "binary_structured_byte_not_formula")

    bundle_note = str(bundle_manifest.get("note", ""))
    require("not claimed to be PEFT/vLLM submission-compatible" in bundle_note, bundle_note)

    return {
        "summary_schema_version": SUMMARY_SCHEMA_VERSION,
        "readme_path": str(README_PATH),
        "readme_contract_verified_from_readme_file": True,
        "single_file_hub": str(Path(__file__)),
        "dataset_csv": str(DATASET_CSV),
        "phase0_summary_json": str(PHASE0_SUMMARY_JSON),
        "proxy_summary_json": str(PROXY_SUMMARY_JSON),
        "specialized_summary_json": str(SPECIALIZED_SUMMARY_JSON),
        "correction_md": str(CORRECTION_MD),
        "strategy_md": str(V3F_EFFECTS_MD),
        "results_md": str(RESULTS_MD),
        "readme_contract": README_CONTRACT,
        "readme_contract_state": build_readme_contract_state(README_CONTRACT, max_lora_rank_required=True),
        "phase0_readme_contract_state": build_readme_contract_state(
            phase0_readme_assumptions, max_lora_rank_required=False
        ),
        "proxy_readme_contract_state": build_readme_contract_state(
            proxy_readme_assumptions, max_lora_rank_required=True
        ),
        "specialized_readme_contract_state": build_readme_contract_state(
            specialized_readme_assumptions, max_lora_rank_required=False
        ),
        "stored_phase0_local320": stored_local,
        "corrected_phase0_local320": corrected_rows["corrected_phase0_local320"],
        "stored_phase0_binary_hard": phase0_family_binary,
        "corrected_phase0_binary_hard": corrected_rows["corrected_binary_hard"],
        "stored_phase0_symbol_watch": phase0_family_symbol,
        "proxy_design": proxy_rows["proxy_design"],
        "proxy_actual": proxy_overall,
        "specialized563": specialized_overall,
        "dominant_structured_safe_bucket": dominant_structured_safe,
        "supported_bijection_bucket": supported_bijection,
        "supported_not_structured_bucket": supported_not_structured,
        "binary_structured_byte_not_formula_teacher": specialized_not_formula,
        "submission_compatibility": {
            "bundle_manifest_json": str(BUNDLE_MANIFEST_JSON),
            "bundle_note": bundle_note,
            "readme_submission_compatible": False,
        },
        "next_repair_priorities": [
            "abstract 110 phrasing cleanup",
            "binary_structured_byte_not_formula teacher redesign",
            "supported_not_structured supplement",
            "2-box closure that preserves boxed stability while improving content correctness",
        ],
    }


def render_markdown_summary(payload: dict[str, Any]) -> str:
    stored_local = payload["stored_phase0_local320"]
    corrected_local = payload["corrected_phase0_local320"]
    proxy_actual = payload["proxy_actual"]
    proxy_design = payload["proxy_design"]
    specialized = payload["specialized563"]
    corrected_binary = payload["corrected_phase0_binary_hard"]
    supported_not_structured = payload["supported_not_structured_bucket"]
    not_formula_teacher = payload["binary_structured_byte_not_formula_teacher"]
    lines = [
        "# v3f exportable audit",
        "",
        f"- single_file_hub: `{payload['single_file_hub']}`",
        f"- dataset_csv: `{payload['dataset_csv']}`",
        f"- stored_phase0_local320: `{stored_local['correct']}/{stored_local['rows']} = {stored_local['accuracy']}`",
        f"- corrected_phase0_local320: `{corrected_local['correct']}/{corrected_local['rows']} = {corrected_local['accuracy']}`",
        f"- corrected_phase0_binary_hard: `{corrected_binary['correct']}/{corrected_binary['rows']} = {corrected_binary['accuracy']}`",
        f"- proxy_design: `{proxy_design['correct']}/{proxy_design['rows']} = {proxy_design['accuracy']}`",
        f"- proxy_actual: `{proxy_actual['correct']}/{proxy_actual['rows']} = {proxy_actual['accuracy']}`",
        f"- specialized563: `{specialized['correct']}/{specialized['rows']} = {specialized['accuracy']}`",
        f"- supported_not_structured: `{supported_not_structured['correct']}/{supported_not_structured['rows']} = {supported_not_structured['accuracy']}`",
        f"- binary_structured_byte_not_formula: `{not_formula_teacher['correct']}/{not_formula_teacher['rows']} = {not_formula_teacher['accuracy']}`",
        f"- submission_compatible: `{payload['submission_compatibility']['readme_submission_compatible']}`",
        "",
        "## README contract",
        "",
        f"- max_lora_rank: `{payload['readme_contract']['max_lora_rank']}`",
        f"- max_tokens: `{payload['readme_contract']['max_tokens']}`",
        f"- top_p: `{payload['readme_contract']['top_p']}`",
        f"- temperature: `{payload['readme_contract']['temperature']}`",
        f"- max_num_seqs: `{payload['readme_contract']['max_num_seqs']}`",
        f"- gpu_memory_utilization: `{payload['readme_contract']['gpu_memory_utilization']}`",
        f"- max_model_len: `{payload['readme_contract']['max_model_len']}`",
        "",
        "## README contract state",
        "",
        f"- summary_schema_version: `{payload['summary_schema_version']}`",
        f"- verified_from_readme_file: `{payload['readme_contract_verified_from_readme_file']}`",
        f"- summary_matches_current_readme: `{payload['readme_contract_state']['matches_current_readme']}`",
        f"- summary_contract_key_count: `{payload['readme_contract_state']['actual_key_count']}/{payload['readme_contract_state']['expected_key_count']}`",
        f"- summary_missing_keys: `{format_inline_list(payload['readme_contract_state']['missing_keys'])}`",
        f"- phase0_manifest_matches_current_readme: `{payload['phase0_readme_contract_state']['matches_current_readme']}`",
        f"- proxy_manifest_matches_current_readme: `{payload['proxy_readme_contract_state']['matches_current_readme']}`",
        f"- specialized_manifest_matches_current_readme: `{payload['specialized_readme_contract_state']['matches_current_readme']}`",
        "",
        "## Compatibility gap",
        "",
        f"- bundle_note: `{payload['submission_compatibility']['bundle_note']}`",
        f"- correction_source: `{payload['correction_md']}`",
        f"- strategy_source: `{payload['strategy_md']}`",
        "",
        "## Next repair priorities",
        "",
        *[f"- {item}" for item in payload["next_repair_priorities"]],
    ]
    return "\n".join(lines)


def write_summary(output_root: Path) -> Path:
    payload = build_summary()
    summary_json = output_root / "v3f_exportable_audit_summary.json"
    summary_md = output_root / "v3f_exportable_audit_summary.md"
    dump_json(summary_json, payload)
    dump_markdown(summary_md, render_markdown_summary(payload))
    return summary_json


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the historical v3f lineage under the README contract.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("verify", help="Validate local v3f lineage artifacts and print a JSON summary.")

    write_parser = subparsers.add_parser(
        "write-summary",
        help="Validate local v3f lineage artifacts and write JSON/Markdown summaries.",
    )
    write_parser.add_argument(
        "--output-root",
        default=str(Path(__file__).resolve().parent),
        help="Directory where v3f_exportable_audit_summary.{json,md} will be written.",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    if args.command in (None, "verify"):
        print(json.dumps(build_summary(), indent=2, sort_keys=True))
        return 0
    if args.command == "write-summary":
        summary_json = write_summary(Path(args.output_root))
        print(summary_json)
        return 0
    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
