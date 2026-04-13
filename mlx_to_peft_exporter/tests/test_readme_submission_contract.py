from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "export_mlx_adapter_bundle_to_peft.py"
)
SPEC = importlib.util.spec_from_file_location("mlx_to_peft_exporter_main", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
exporter = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = exporter
SPEC.loader.exec_module(exporter)


def write_submission_contract_readme(
    tmp_path: Path,
    *,
    max_lora_rank: str = "32",
    include_adapter_config_clause: bool = True,
    include_submission_zip_clause: bool = True,
    include_single_adapter_clause: bool = True,
) -> Path:
    evaluation_line = (
        "Submissions are evaluated based on their Accuracy in solving the provided tasks. "
        "The NVIDIA Nemotron-3-Nano-30B model is loaded with your LoRA adapter"
    )
    if include_adapter_config_clause:
        evaluation_line += " (which must include an adapter_config.json)"
    evaluation_line += " using the vLLM inference engine."
    if include_single_adapter_clause:
        submitting_line = (
            "You must submit a LoRA adapter of rank at most "
            f"{max_lora_rank} for the NVIDIA Nemotron-3-Nano-30B model"
        )
    else:
        submitting_line = (
            "You must submit LoRA adapters of rank at most "
            f"{max_lora_rank} for the NVIDIA Nemotron-3-Nano-30B model"
        )
    if include_submission_zip_clause:
        submitting_line += " packaged into a submission.zip file."
    else:
        submitting_line += " packaged into an archive file."
    readme_path = tmp_path / "README.md"
    readme_path.write_text(
        "\n".join(
            [
                "Evaluation",
                evaluation_line,
                "Parameter\tValue",
                f"max_lora_rank\t{max_lora_rank}",
                "max_tokens\t7680",
                "top_p\t1.0",
                "temperature\t0.0",
                "max_num_seqs\t64",
                "gpu_memory_utilization\t0.85",
                "max_model_len\t8192",
                "Submitting",
                submitting_line,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return readme_path


def test_exporter_load_readme_submission_contract_from_readme_matches_expected(tmp_path: Path) -> None:
    original_readme_path = exporter.README_PATH
    try:
        exporter.README_PATH = write_submission_contract_readme(tmp_path)
        assert exporter.load_readme_submission_contract_from_readme() == {
            "required_files": list(exporter.README_REQUIRED_FILES),
            "max_lora_rank": exporter.README_MAX_LORA_RANK,
            "single_adapter_submission_zip": True,
            "submission_archive_name": exporter.README_SUBMISSION_ARCHIVE_NAME,
        }
    finally:
        exporter.README_PATH = original_readme_path


def test_exporter_load_readme_submission_contract_from_readme_rejects_missing_adapter_config_clause(
    tmp_path: Path,
) -> None:
    original_readme_path = exporter.README_PATH
    try:
        exporter.README_PATH = write_submission_contract_readme(
            tmp_path,
            include_adapter_config_clause=False,
        )
        try:
            exporter.load_readme_submission_contract_from_readme()
            raise AssertionError("Expected missing adapter_config clause to raise SystemExit")
        except SystemExit as exc:
            assert "adapter must include adapter_config.json" in str(exc)
    finally:
        exporter.README_PATH = original_readme_path


def test_exporter_verify_readme_submission_contract_file_rejects_missing_submission_zip_clause(
    tmp_path: Path,
) -> None:
    original_readme_path = exporter.README_PATH
    try:
        exporter.README_PATH = write_submission_contract_readme(
            tmp_path,
            include_submission_zip_clause=False,
        )
        try:
            exporter.verify_readme_submission_contract_file()
            raise AssertionError("Expected missing submission.zip clause to raise SystemExit")
        except SystemExit as exc:
            assert "submission archive is submission.zip" in str(exc)
    finally:
        exporter.README_PATH = original_readme_path


def test_exporter_verify_readme_submission_contract_file_rejects_max_rank_drift(tmp_path: Path) -> None:
    original_readme_path = exporter.README_PATH
    try:
        exporter.README_PATH = write_submission_contract_readme(tmp_path, max_lora_rank="64")
        try:
            exporter.verify_readme_submission_contract_file()
            raise AssertionError("Expected max_lora_rank drift to raise SystemExit")
        except SystemExit as exc:
            assert "submission contract mismatch for max_lora_rank" in str(exc)
    finally:
        exporter.README_PATH = original_readme_path


def test_exporter_build_target_modules_regex_includes_attention_projection_terminals() -> None:
    regex = exporter.build_target_modules_regex(
        [
            "backbone.layers.0.mixer.q_proj.lora_a",
            "backbone.layers.0.mixer.k_proj.lora_a",
            "backbone.layers.0.mixer.v_proj.lora_b",
            "backbone.layers.0.mixer.o_proj.lora_b",
        ]
    )

    assert regex == r".*\.(q_proj|k_proj|v_proj|o_proj)$"
