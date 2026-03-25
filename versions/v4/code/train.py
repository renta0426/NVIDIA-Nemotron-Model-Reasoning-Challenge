from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

import pandas as pd
import yaml


VERSION_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = VERSION_ROOT.parents[1]
CONF_ROOT = VERSION_ROOT / 'conf'
CONF_DATA_ROOT = CONF_ROOT / 'data'
CONF_TRAIN_ROOT = CONF_ROOT / 'train'
CONF_PREFERENCE_ROOT = CONF_ROOT / 'preference'
CONF_EVAL_ROOT = CONF_ROOT / 'eval'
CONF_MERGE_ROOT = CONF_ROOT / 'merge'
CONF_PACKAGE_ROOT = CONF_ROOT / 'package'
DATA_ROOT = VERSION_ROOT / 'data'
PROCESSED_ROOT = DATA_ROOT / 'processed'
SYNTH_ROOT = DATA_ROOT / 'synth'
PREFERENCE_ROOT = DATA_ROOT / 'preference'
RFT_ROOT = DATA_ROOT / 'rft'
TRAIN_PACKS_ROOT = DATA_ROOT / 'train_packs'
OUTPUTS_ROOT = VERSION_ROOT / 'outputs'
MODELS_ROOT = OUTPUTS_ROOT / 'models'
RUNTIME_ROOT = OUTPUTS_ROOT / 'runtime'
AUDITS_ROOT = OUTPUTS_ROOT / 'audits'
DATASETS_ROOT = OUTPUTS_ROOT / 'datasets'
HANDOFF_ROOT = OUTPUTS_ROOT / 'handoff'
TRAIN_OUTPUT_ROOT = OUTPUTS_ROOT / 'train'
EVAL_ROOT = OUTPUTS_ROOT / 'eval'
PACKAGING_ROOT = OUTPUTS_ROOT / 'packaging'
REPORTS_ROOT = OUTPUTS_ROOT / 'reports'

LEGACY_MODEL_REPO_ID = 'lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit'
DEFAULT_MODEL_REPO_ID = 'mlx-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-BF16'
DEFAULT_SUBMISSION_BASE_MODEL = 'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-Base-BF16'
LEGACY_LOCAL_MODEL_NAME = 'nemotron-3-nano-30b-a3b-mlx-6bit'
DEFAULT_LOCAL_MODEL_NAME = 'nemotron-3-nano-30b-a3b-mlx-bf16'
DEFAULT_LOCAL_MODEL_PATH = REPO_ROOT / 'model'
LEGACY_LOCAL_MODEL_PATH = REPO_ROOT / 'versions' / 'v2' / 'outputs' / 'models' / LEGACY_LOCAL_MODEL_NAME
DEFAULT_ACTIVE_MODEL_PATH = REPO_ROOT / 'versions' / 'v2' / 'outputs' / 'runtime' / 'active_model.json'
DEFAULT_MODEL_REGISTRY_PATH = RUNTIME_ROOT / 'model_registry_v3.json'
DEFAULT_SMOKE_IDENTIFIER = 'nemotron-v3-smoke'

DEFAULT_REAL_CANONICAL_CONFIG_PATH = CONF_DATA_ROOT / 'real_canonical.yaml'
DEFAULT_SYNTH_CORE_CONFIG_PATH = CONF_DATA_ROOT / 'synth_core.yaml'
DEFAULT_SYNTH_HARD_CONFIG_PATH = CONF_DATA_ROOT / 'synth_hard.yaml'
DEFAULT_TEACHER_DISTILL_CONFIG_PATH = CONF_DATA_ROOT / 'teacher_distill.yaml'
DEFAULT_FORMAT_SHARPENING_CONFIG_PATH = CONF_DATA_ROOT / 'format_sharpening.yaml'
DEFAULT_MIX_STAGE_A_CONFIG_PATH = CONF_DATA_ROOT / 'mix_stage_a.yaml'
DEFAULT_MIX_STAGE_B_CONFIG_PATH = CONF_DATA_ROOT / 'mix_stage_b.yaml'
DEFAULT_V3_FORMAT_POLICY_CONFIG_PATH = CONF_DATA_ROOT / 'format_policy_v3.yaml'
DEFAULT_V3_PREFERENCE_CONFIG_PATH = CONF_DATA_ROOT / 'preference_pairs.yaml'
DEFAULT_V3_RFT_CONFIG_PATH = CONF_DATA_ROOT / 'rft_accept_pool.yaml'

DEFAULT_STAGE_A_R32_ALPHA32_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_a_r32_alpha32.yaml'
DEFAULT_STAGE_A_R32_ALPHA32_WEIGHTED_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_a_r32_alpha32_weighted.yaml'
DEFAULT_STAGE_A_R32_ALPHA64_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_a_r32_alpha64.yaml'
DEFAULT_STAGE_B_HARDENING_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_b_hardening.yaml'
DEFAULT_STAGE_B_A6000_COMPAT_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_b_a6000_compat.yaml'
DEFAULT_PEFT_SMOKE_CONFIG_PATH = CONF_PACKAGE_ROOT / 'peft_smoke.yaml'
DEFAULT_V3_STAGE_A_WEIGHTED_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_a_weighted_mlx.yaml'
DEFAULT_V3_STAGE_A_ALPHA64_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_a_weighted_alpha64_mlx.yaml'
DEFAULT_V3_STAGE_B_WEIGHTED_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_b_weighted_mlx.yaml'
DEFAULT_V3_STAGE_B_ANSWER_BIAS_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_b_answer_bias_mlx.yaml'
DEFAULT_V3_STAGE_A_CUDA_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_a_cuda_bf16.yaml'
DEFAULT_V3_STAGE_B_CUDA_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_b_cuda_bf16.yaml'
DEFAULT_V3_PACKAGE_CONFIG_PATH = CONF_PACKAGE_ROOT / 'cuda_submission_smoke.yaml'

DEFAULT_V1_METADATA_PATH = REPO_ROOT / 'versions' / 'v1' / 'data' / 'processed' / 'train_metadata_v1.parquet'
DEFAULT_V1_SPLITS_PATH = REPO_ROOT / 'versions' / 'v1' / 'data' / 'processed' / 'train_splits_v1.parquet'
DEFAULT_TRAIN_CSV_PATH = REPO_ROOT / 'data' / 'train.csv'
DEFAULT_V2_REAL_CANONICAL_PATH = REPO_ROOT / 'versions' / 'v2' / 'data' / 'processed' / 'train_real_canonical_v2.parquet'
DEFAULT_V2_SYNTH_CORE_PATH = REPO_ROOT / 'versions' / 'v2' / 'data' / 'synth' / 'synth_core_v2.parquet'
DEFAULT_V2_SYNTH_HARD_PATH = REPO_ROOT / 'versions' / 'v2' / 'data' / 'synth' / 'synth_hard_v2.parquet'
DEFAULT_V2_CORRECTION_PAIRS_PATH = REPO_ROOT / 'versions' / 'v2' / 'data' / 'synth' / 'correction_pairs_v2.parquet'
DEFAULT_V2_DISTILLED_TRACES_PATH = REPO_ROOT / 'versions' / 'v2' / 'data' / 'synth' / 'distilled_traces_v2.parquet'

DEFAULT_REAL_CANONICAL_OUTPUT_PATH = PROCESSED_ROOT / 'train_real_canonical_v2.parquet'
DEFAULT_SOLVER_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'solver_registry_v2.json'
DEFAULT_SYNTHETIC_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'synthetic_registry_v2.parquet'
DEFAULT_TEACHER_TRACE_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'teacher_trace_registry_v2.parquet'
DEFAULT_TRAIN_MIX_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'train_mix_registry_v2.parquet'

DEFAULT_SYNTH_CORE_OUTPUT_PATH = SYNTH_ROOT / 'synth_core_v2.parquet'
DEFAULT_SYNTH_HARD_OUTPUT_PATH = SYNTH_ROOT / 'synth_hard_v2.parquet'
DEFAULT_SYNTH_FORMAT_OUTPUT_PATH = SYNTH_ROOT / 'synth_format_v2.parquet'
DEFAULT_DISTILL_CANDIDATES_OUTPUT_PATH = DATASETS_ROOT / 'distill_candidates_v2.jsonl'
DEFAULT_DISTILLED_TRACES_OUTPUT_PATH = SYNTH_ROOT / 'distilled_traces_v2.parquet'
DEFAULT_CORRECTION_PAIRS_OUTPUT_PATH = SYNTH_ROOT / 'correction_pairs_v2.parquet'
DEFAULT_FORMAT_PAIRS_OUTPUT_PATH = SYNTH_ROOT / 'format_pairs_v2.parquet'

DEFAULT_STAGE_A_MIX_OUTPUT_PATH = TRAIN_PACKS_ROOT / 'stage_a_mix_v2.parquet'
DEFAULT_STAGE_B_MIX_OUTPUT_PATH = TRAIN_PACKS_ROOT / 'stage_b_mix_v2.parquet'
DEFAULT_STAGE_B_HARD_ONLY_OUTPUT_PATH = TRAIN_PACKS_ROOT / 'stage_b_hard_only_v2.parquet'

DEFAULT_CANDIDATE_REGISTRY_OUTPUT_PATH = REPORTS_ROOT / 'candidate_registry_v2.csv'
DEFAULT_PROMOTION_RULES_OUTPUT_PATH = REPORTS_ROOT / 'promotion_rules_v2.txt'
DEFAULT_TRAINING_RUNBOOK_OUTPUT_PATH = REPORTS_ROOT / 'training_command_book_v2.txt'
DEFAULT_V3_TEACHER_TRACE_CANDIDATES_OUTPUT_PATH = DATASETS_ROOT / 'teacher_trace_candidates_v3.jsonl'
DEFAULT_V3_TEACHER_TRACE_GENERATIONS_OUTPUT_PATH = DATASETS_ROOT / 'teacher_trace_generations_v3.jsonl'
DEFAULT_V3_TEACHER_TRACE_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'teacher_trace_registry_v3.parquet'
DEFAULT_V3_DISTILLED_TRACES_OUTPUT_PATH = SYNTH_ROOT / 'distilled_traces_real_v3.parquet'
DEFAULT_V3_FORMAT_PAIRS_OUTPUT_PATH = SYNTH_ROOT / 'format_pairs_strict_v3.parquet'
DEFAULT_V3_CORRECTION_PAIRS_OUTPUT_PATH = SYNTH_ROOT / 'correction_pairs_strict_v3.parquet'
DEFAULT_V3_PREFERENCE_PAIRS_OUTPUT_PATH = PREFERENCE_ROOT / 'preference_pairs_v3.parquet'
DEFAULT_V3_RFT_ACCEPT_POOL_OUTPUT_PATH = PREFERENCE_ROOT / 'rft_accept_pool_v3.parquet'
DEFAULT_V3_STAGE_A_OUTPUT_PATH = TRAIN_PACKS_ROOT / 'stage_a_strong_v3.parquet'
DEFAULT_V3_STAGE_B_OUTPUT_PATH = TRAIN_PACKS_ROOT / 'stage_b_strong_v3.parquet'
DEFAULT_V3_WEIGHTED_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'weighted_train_registry_v3.parquet'
DEFAULT_V3_FORMAT_AUDIT_OUTPUT_PATH = AUDITS_ROOT / 'format_audit_v3.csv'
DEFAULT_V3_WEIGHTED_ABLATION_OUTPUT_PATH = REPORTS_ROOT / 'weighted_ablation_v3.csv'
DEFAULT_V3_CANDIDATE_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'candidate_registry_v3.csv'
DEFAULT_V3_CUDA_REPRO_SPEC_OUTPUT_PATH = HANDOFF_ROOT / 'cuda_reproduction_spec_v3.yaml'
DEFAULT_V3_CUDA_REPRO_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'cuda_reproduction_registry_v3.csv'
DEFAULT_V3_PROMOTION_RULES_OUTPUT_PATH = REPORTS_ROOT / 'promotion_rules_v3.txt'
DEFAULT_V3_TRAINING_RUNBOOK_OUTPUT_PATH = REPORTS_ROOT / 'training_command_book_v3.txt'

DEFAULT_V3_STAGE_A_MANIFEST_PATH = REPO_ROOT / 'versions' / 'v3' / 'outputs' / 'train' / 'pilot_stage_a_run1' / 'sft_a_sft_stage_a_weighted_mlx_manifest.json'
DEFAULT_V3_STAGE_B_MANIFEST_PATH = REPO_ROOT / 'versions' / 'v3' / 'outputs' / 'train' / 'pilot_stage_b_run1' / 'sft_b_sft_stage_b_weighted_mlx_manifest.json'
DEFAULT_V3_STAGE_A_ADAPTER_PATH = REPO_ROOT / 'versions' / 'v3' / 'outputs' / 'train' / 'pilot_stage_a_run1' / 'adapter_a_sft_stage_a_weighted_mlx'
DEFAULT_V3_STAGE_B_ADAPTER_PATH = REPO_ROOT / 'versions' / 'v3' / 'outputs' / 'train' / 'pilot_stage_b_run1' / 'adapter_b_sft_stage_b_weighted_mlx'
DEFAULT_V3_ACTIVE_MODEL_PATH = REPO_ROOT / 'versions' / 'v3' / 'outputs' / 'runtime' / 'active_model.json'
SOURCE_V3_PREFERENCE_PAIRS_PATH = REPO_ROOT / 'versions' / 'v3' / 'data' / 'preference' / 'preference_pairs_v3.parquet'
SOURCE_V3_STAGE_A_OUTPUT_PATH = REPO_ROOT / 'versions' / 'v3' / 'data' / 'train_packs' / 'stage_a_strong_v3.parquet'

DEFAULT_V4_EXPERIMENT_LOG_PATH = REPORTS_ROOT / 'experiment_log_v4.jsonl'
DEFAULT_V4_FORMAT_PREFERENCE_OUTPUT_PATH = PREFERENCE_ROOT / 'format_preference_pairs_v4.parquet'
DEFAULT_V4_CORRECTNESS_PREFERENCE_OUTPUT_PATH = PREFERENCE_ROOT / 'correctness_preference_pairs_v4.parquet'
DEFAULT_V4_PREFERENCE_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'stage_c_preference_registry_v4.parquet'
DEFAULT_V4_RFT_GENERATIONS_OUTPUT_PATH = RFT_ROOT / 'rft_candidate_generations_v4.jsonl'
DEFAULT_V4_RFT_ACCEPT_POOL_OUTPUT_PATH = RFT_ROOT / 'rft_accept_pool_v4.parquet'
DEFAULT_V4_RFT_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'rft_registry_v4.parquet'
DEFAULT_V4_STAGE_C_RFT_OUTPUT_PATH = TRAIN_PACKS_ROOT / 'stage_c_rft_mix_v4.parquet'
DEFAULT_V4_STAGE_C_PREFERENCE_OUTPUT_PATH = TRAIN_PACKS_ROOT / 'stage_c_preference_mix_v4.parquet'
DEFAULT_V4_LOCAL_SCOREBOARD_OUTPUT_PATH = REPORTS_ROOT / 'local_scoreboard_v4.csv'
DEFAULT_V4_FAMILY_REGRET_OUTPUT_PATH = REPORTS_ROOT / 'family_regret_report_v4.csv'
DEFAULT_V4_CANDIDATE_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'candidate_registry_v4.csv'
DEFAULT_V4_SPECIALIST_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'specialist_candidate_registry_v4.csv'
DEFAULT_V4_MERGE_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'merge_candidate_registry_v4.csv'
DEFAULT_V4_CUDA_REPRO_SPEC_OUTPUT_PATH = HANDOFF_ROOT / 'cuda_reproduction_spec_v4.yaml'
DEFAULT_V4_CUDA_REPRO_REGISTRY_OUTPUT_PATH = PROCESSED_ROOT / 'cuda_reproduction_registry_v4.csv'
DEFAULT_V4_SUBMISSION_MANIFEST_OUTPUT_PATH = HANDOFF_ROOT / 'submission_manifest_v4.json'
DEFAULT_V4_PROMOTION_RULES_OUTPUT_PATH = REPORTS_ROOT / 'promotion_rules_v4.txt'
DEFAULT_V4_TRAINING_RUNBOOK_OUTPUT_PATH = REPORTS_ROOT / 'training_command_book_v4.txt'

DEFAULT_V4_RFT_CONFIG_PATH = CONF_DATA_ROOT / 'rft_accept_pool.yaml'
DEFAULT_V4_STAGE_C_RFT_MIX_CONFIG_PATH = CONF_DATA_ROOT / 'stage_c_rft_mix.yaml'
DEFAULT_V4_STAGE_C_PREFERENCE_MIX_CONFIG_PATH = CONF_DATA_ROOT / 'stage_c_preference_mix.yaml'
DEFAULT_V4_FORMAT_PREFERENCE_CONFIG_PATH = CONF_DATA_ROOT / 'preference_format.yaml'
DEFAULT_V4_CORRECTNESS_PREFERENCE_CONFIG_PATH = CONF_DATA_ROOT / 'preference_correctness.yaml'
DEFAULT_V4_QUICK_EVAL_CONFIG_PATH = CONF_EVAL_ROOT / 'candidate_score_quick.yaml'
DEFAULT_V4_SERIOUS_EVAL_CONFIG_PATH = CONF_EVAL_ROOT / 'candidate_score_serious.yaml'
DEFAULT_V4_WEEKLY_EVAL_CONFIG_PATH = CONF_EVAL_ROOT / 'candidate_score_weekly.yaml'
DEFAULT_V4_RFT_TRAIN_CONFIG_PATH = CONF_TRAIN_ROOT / 'rft_stage_c_mlx.yaml'
DEFAULT_V4_FORMAT_DPO_CONFIG_PATH = CONF_TRAIN_ROOT / 'dpo_format_mlx.yaml'
DEFAULT_V4_CORRECTNESS_DPO_CONFIG_PATH = CONF_TRAIN_ROOT / 'dpo_correctness_mlx.yaml'
DEFAULT_V4_SPECIALIST_FORMAT_CONFIG_PATH = CONF_TRAIN_ROOT / 'specialist_format_mlx.yaml'
DEFAULT_V4_SPECIALIST_BIT_CONFIG_PATH = CONF_TRAIN_ROOT / 'specialist_bit_mlx.yaml'
DEFAULT_V4_MERGE_CONFIG_PATH = CONF_MERGE_ROOT / 'generalist_specialist_merge.yaml'
DEFAULT_V4_COMPRESS_CONFIG_PATH = CONF_MERGE_ROOT / 'rank32_compress.yaml'
DEFAULT_V4_CUDA_TRAIN_CONFIG_PATH = CONF_TRAIN_ROOT / 'stage_c_cuda_bf16.yaml'
DEFAULT_V4_PACKAGE_CONFIG_PATH = CONF_PACKAGE_ROOT / 'cuda_submission_smoke.yaml'

CLEAN_FORMAT_BUCKETS_V4 = {'clean_boxed', 'clean_final_answer'}
HARD_FAMILIES_V4 = {'bit_manipulation', 'text_decryption', 'symbol_equation'}


def _import_version_module(module_name: str, module_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to import module: {module_path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


V1_MODULE = _import_version_module('v4_import_v1_train', REPO_ROOT / 'versions' / 'v1' / 'code' / 'train.py')


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    manifest_path: Path | None
    adapter_path: Path | None
    base_model: str
    stage: str
    config_name: str
    source_version: str
    parent_candidate_id: str | None = None

PLANNED_V2_COMMANDS = (
    'download-model',
    'show-active-model',
    'smoke-model',
    'build-real-canonical',
    'build-solver-registry',
    'build-synth-core',
    'build-synth-hard',
    'build-format-pairs',
    'build-distill-candidates',
    'filter-distilled-traces',
    'build-correction-pairs',
    'build-train-mix',
    'train-sft',
    'package-peft',
    'write-runbook',
)

V2_SCAFFOLD_DIRECTORIES = (
    Path('code'),
    Path('conf'),
    Path('conf/data'),
    Path('conf/train'),
    Path('conf/package'),
    Path('data'),
    Path('data/processed'),
    Path('data/synth'),
    Path('data/train_packs'),
    Path('outputs'),
    Path('outputs/audits'),
    Path('outputs/datasets'),
    Path('outputs/models'),
    Path('outputs/runtime'),
    Path('outputs/train'),
    Path('outputs/eval'),
    Path('outputs/packaging'),
    Path('outputs/reports'),
    Path('tests'),
)

V2_SCAFFOLD_CONFIG_SPECS = (
    (Path('conf/data/real_canonical.yaml'), 'data', 'real_canonical'),
    (Path('conf/data/synth_core.yaml'), 'data', 'synth_core'),
    (Path('conf/data/synth_hard.yaml'), 'data', 'synth_hard'),
    (Path('conf/data/teacher_distill.yaml'), 'data', 'teacher_distill'),
    (Path('conf/data/format_sharpening.yaml'), 'data', 'format_sharpening'),
    (Path('conf/data/mix_stage_a.yaml'), 'data', 'mix_stage_a'),
    (Path('conf/data/mix_stage_b.yaml'), 'data', 'mix_stage_b'),
    (Path('conf/train/sft_stage_a_r32_alpha32.yaml'), 'train', 'sft_stage_a_r32_alpha32'),
    (
        Path('conf/train/sft_stage_a_r32_alpha32_weighted.yaml'),
        'train',
        'sft_stage_a_r32_alpha32_weighted',
    ),
    (Path('conf/train/sft_stage_a_r32_alpha64.yaml'), 'train', 'sft_stage_a_r32_alpha64'),
    (Path('conf/train/sft_stage_b_hardening.yaml'), 'train', 'sft_stage_b_hardening'),
    (Path('conf/train/sft_stage_b_a6000_compat.yaml'), 'train', 'sft_stage_b_a6000_compat'),
    (Path('conf/package/peft_smoke.yaml'), 'package', 'peft_smoke'),
)

V2_SCAFFOLD_MARKER_FILES = (
    Path('data/processed/.gitkeep'),
    Path('data/synth/.gitkeep'),
    Path('data/train_packs/.gitkeep'),
    Path('outputs/audits/.gitkeep'),
    Path('outputs/datasets/.gitkeep'),
    Path('outputs/train/.gitkeep'),
    Path('outputs/eval/.gitkeep'),
    Path('outputs/packaging/.gitkeep'),
    Path('outputs/reports/.gitkeep'),
)

V3_SCAFFOLD_DIRECTORIES = (
    Path('code'),
    Path('conf'),
    Path('conf/data'),
    Path('conf/train'),
    Path('conf/preference'),
    Path('conf/package'),
    Path('data'),
    Path('data/processed'),
    Path('data/synth'),
    Path('data/preference'),
    Path('data/train_packs'),
    Path('outputs'),
    Path('outputs/audits'),
    Path('outputs/datasets'),
    Path('outputs/handoff'),
    Path('outputs/models'),
    Path('outputs/runtime'),
    Path('outputs/train'),
    Path('outputs/eval'),
    Path('outputs/packaging'),
    Path('outputs/reports'),
    Path('tests'),
)

V3_SCAFFOLD_MARKER_FILES = (
    Path('data/processed/.gitkeep'),
    Path('data/synth/.gitkeep'),
    Path('data/preference/.gitkeep'),
    Path('data/train_packs/.gitkeep'),
    Path('outputs/audits/.gitkeep'),
    Path('outputs/datasets/.gitkeep'),
    Path('outputs/handoff/.gitkeep'),
    Path('outputs/train/.gitkeep'),
    Path('outputs/eval/.gitkeep'),
    Path('outputs/packaging/.gitkeep'),
    Path('outputs/reports/.gitkeep'),
)


@dataclass(frozen=True)
class ModelDownloadSpec:
    repo_id: str = DEFAULT_MODEL_REPO_ID
    local_name: str = DEFAULT_LOCAL_MODEL_NAME
    revision: str | None = None
    token_env: str = 'HF_TOKEN'


def ensure_directories(paths: Sequence[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def ensure_runtime_directories() -> None:
    ensure_directories((OUTPUTS_ROOT, MODELS_ROOT, RUNTIME_ROOT))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def render_placeholder_yaml(*, section: str, name: str) -> str:
    return (
        'version: v2\n'
        f'section: {section}\n'
        f'name: {name}\n'
        'status: scaffold\n'
        'note: "Step 1 placeholder. Populate operational fields in later v2 steps."\n'
    )


def v2_scaffold_directories(version_root: Path = VERSION_ROOT) -> tuple[Path, ...]:
    return tuple(version_root / relative_path for relative_path in V2_SCAFFOLD_DIRECTORIES)


def v2_scaffold_files(version_root: Path = VERSION_ROOT) -> dict[Path, str]:
    files: dict[Path, str] = {}
    for relative_path, section, name in V2_SCAFFOLD_CONFIG_SPECS:
        files[version_root / relative_path] = render_placeholder_yaml(section=section, name=name)
    for relative_path in V2_SCAFFOLD_MARKER_FILES:
        files[version_root / relative_path] = ''
    return files


def ensure_v2_layout_scaffold(version_root: Path = VERSION_ROOT) -> None:
    ensure_directories(v2_scaffold_directories(version_root))
    for path, contents in v2_scaffold_files(version_root).items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding='utf-8')


def render_v3_yaml_payloads() -> dict[Path, str]:
    payloads: dict[Path, str] = {
        Path('conf/data/teacher_trace_real.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'data',
                'name': 'teacher_trace_real',
                'seed': 73,
                'teacher_name': DEFAULT_MODEL_REPO_ID,
                'target_styles': ['long', 'short', 'answer_only', 'format_safe'],
                'style_samples': {'long': 1, 'short': 1, 'answer_only': 1, 'format_safe': 1},
                'hard_family_styles': ['short', 'format_safe'],
                'hard_family_sample_count': 4,
                'temperature_by_style': {'long': 0.1, 'short': 0.0, 'answer_only': 0.0, 'format_safe': 0.0},
                'top_p_by_style': {'long': 1.0, 'short': 1.0, 'answer_only': 1.0, 'format_safe': 1.0},
                'max_tokens_by_style': {'long': 384, 'short': 192, 'answer_only': 48, 'format_safe': 96},
            },
            sort_keys=False,
        ),
        Path('conf/data/format_policy_v3.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'data',
                'name': 'format_policy_v3',
                'safe_render': 'boxed',
                'unsafe_render': 'final_answer',
                'unsafe_markers': ['}', '\\', '`', '\\n', '\\r'],
                'require_single_final_marker': True,
                'require_last_non_empty_line': True,
                'reject_multiple_boxed': True,
                'reject_trailing_numbers': True,
            },
            sort_keys=False,
        ),
        Path('conf/data/preference_pairs.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'data',
                'name': 'preference_pairs',
                'brevity_margin_chars': 40,
                'pair_kinds': ['format', 'correction', 'brevity', 'consensus'],
            },
            sort_keys=False,
        ),
        Path('conf/data/rft_accept_pool.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'data',
                'name': 'rft_accept_pool',
                'max_trace_tokens_est': 96,
                'require_format_pass': True,
                'require_final_line_only': True,
            },
            sort_keys=False,
        ),
        Path('conf/data/mix_stage_a_strong.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'data',
                'name': 'stage_a_strong',
                'stage': 'a',
                'seed': 91,
                'target_total': 12000,
                'mix_ratios': {'real': 0.50, 'core_synth': 0.25, 'distill': 0.15, 'hard_synth': 0.05, 'format': 0.05},
                'family_weights': {
                    'bit_manipulation': 1.3,
                    'gravity_constant': 0.9,
                    'unit_conversion': 0.8,
                    'text_decryption': 1.4,
                    'roman_numeral': 0.6,
                    'symbol_equation': 1.6,
                },
                'weight_profile_name': 'v3_default',
                'rationale_weight': 1.0,
                'final_answer_prefix_weight': 2.0,
                'final_line_weight': 3.0,
                'answer_span_weights': {
                    'gravity_constant': 4.0,
                    'unit_conversion': 4.0,
                    'roman_numeral': 4.0,
                    'bit_manipulation': 5.0,
                    'symbol_equation': 6.0,
                    'text_decryption': 3.0,
                },
                'drop_invalid_weighted_rows': True,
            },
            sort_keys=False,
        ),
        Path('conf/data/mix_stage_b_strong.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'data',
                'name': 'stage_b_strong',
                'stage': 'b',
                'seed': 92,
                'target_total': 10000,
                'mix_ratios': {'real': 0.35, 'core_synth': 0.20, 'distill': 0.10, 'hard_synth': 0.15, 'correction': 0.10, 'format': 0.10},
                'family_weights': {
                    'bit_manipulation': 1.3,
                    'gravity_constant': 0.9,
                    'unit_conversion': 0.8,
                    'text_decryption': 1.4,
                    'roman_numeral': 0.6,
                    'symbol_equation': 1.6,
                },
                'weight_profile_name': 'v3_default',
                'rationale_weight': 1.0,
                'final_answer_prefix_weight': 2.0,
                'final_line_weight': 3.0,
                'answer_span_weights': {
                    'gravity_constant': 4.0,
                    'unit_conversion': 4.0,
                    'roman_numeral': 4.0,
                    'bit_manipulation': 5.0,
                    'symbol_equation': 6.0,
                    'text_decryption': 3.0,
                },
                'drop_invalid_weighted_rows': True,
            },
            sort_keys=False,
        ),
        Path('conf/train/sft_stage_a_weighted_mlx.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'train',
                'name': 'sft_stage_a_weighted_mlx',
                'stage': 'a',
                'train_pack_path': 'versions/v3/data/train_packs/stage_a_strong_v3.parquet',
                'base_model': DEFAULT_MODEL_REPO_ID,
                'lora_r': 32,
                'lora_alpha': 32,
                'lora_dropout': 0.0,
                'target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
                'learning_rate': 0.0001,
                'num_epochs': 2.0,
                'warmup_ratio': 0.03,
                'max_seq_len': 1024,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 8,
                'weighted_loss': True,
                'rationale_weight': 1.0,
                'final_answer_prefix_weight': 2.0,
                'final_line_weight': 3.0,
                'answer_span_weights': {
                    'gravity_constant': 4.0,
                    'unit_conversion': 4.0,
                    'roman_numeral': 4.0,
                    'bit_manipulation': 5.0,
                    'symbol_equation': 6.0,
                    'text_decryption': 3.0,
                },
            },
            sort_keys=False,
        ),
        Path('conf/train/sft_stage_a_weighted_alpha64_mlx.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'train',
                'name': 'sft_stage_a_weighted_alpha64_mlx',
                'stage': 'a',
                'train_pack_path': 'versions/v3/data/train_packs/stage_a_strong_v3.parquet',
                'base_model': DEFAULT_MODEL_REPO_ID,
                'lora_r': 32,
                'lora_alpha': 64,
                'lora_dropout': 0.0,
                'target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
                'learning_rate': 0.0001,
                'num_epochs': 2.0,
                'warmup_ratio': 0.03,
                'max_seq_len': 1024,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 8,
                'weighted_loss': True,
                'rationale_weight': 1.0,
                'final_answer_prefix_weight': 2.0,
                'final_line_weight': 3.0,
                'answer_span_weights': {
                    'gravity_constant': 4.0,
                    'unit_conversion': 4.0,
                    'roman_numeral': 4.0,
                    'bit_manipulation': 5.0,
                    'symbol_equation': 6.0,
                    'text_decryption': 3.0,
                },
            },
            sort_keys=False,
        ),
        Path('conf/train/sft_stage_b_weighted_mlx.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'train',
                'name': 'sft_stage_b_weighted_mlx',
                'stage': 'b',
                'train_pack_path': 'versions/v3/data/train_packs/stage_b_strong_v3.parquet',
                'base_model': DEFAULT_MODEL_REPO_ID,
                'lora_r': 32,
                'lora_alpha': 32,
                'lora_dropout': 0.0,
                'target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
                'learning_rate': 0.00005,
                'num_epochs': 1.0,
                'warmup_ratio': 0.03,
                'max_seq_len': 1024,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 8,
                'weighted_loss': True,
                'rationale_weight': 1.0,
                'final_answer_prefix_weight': 2.0,
                'final_line_weight': 3.0,
                'answer_span_weights': {
                    'gravity_constant': 4.0,
                    'unit_conversion': 4.0,
                    'roman_numeral': 4.0,
                    'bit_manipulation': 5.0,
                    'symbol_equation': 6.0,
                    'text_decryption': 3.0,
                },
            },
            sort_keys=False,
        ),
        Path('conf/train/sft_stage_b_answer_bias_mlx.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'train',
                'name': 'sft_stage_b_answer_bias_mlx',
                'stage': 'b',
                'train_pack_path': 'versions/v3/data/train_packs/stage_b_strong_v3.parquet',
                'base_model': DEFAULT_MODEL_REPO_ID,
                'lora_r': 32,
                'lora_alpha': 32,
                'lora_dropout': 0.0,
                'target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
                'learning_rate': 0.00005,
                'num_epochs': 0.75,
                'warmup_ratio': 0.03,
                'max_seq_len': 1024,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 8,
                'weighted_loss': True,
                'rationale_weight': 1.0,
                'final_answer_prefix_weight': 2.0,
                'final_line_weight': 3.0,
                'answer_span_weights': {
                    'gravity_constant': 4.0,
                    'unit_conversion': 4.0,
                    'roman_numeral': 4.0,
                    'bit_manipulation': 5.0,
                    'symbol_equation': 6.0,
                    'text_decryption': 3.0,
                },
            },
            sort_keys=False,
        ),
        Path('conf/train/sft_stage_a_cuda_bf16.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'train',
                'name': 'sft_stage_a_cuda_bf16',
                'stage': 'a',
                'base_model_name_or_path': DEFAULT_SUBMISSION_BASE_MODEL,
                'precision': 'bf16',
                'lora_r': 32,
                'lora_alpha': 32,
                'lora_dropout': 0.0,
                'target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
                'learning_rate': 0.0001,
                'num_epochs': 2.0,
                'max_seq_len': 1024,
                'gradient_accumulation_steps': 8,
                'per_device_train_batch_size': 1,
                'weighted_loss': True,
            },
            sort_keys=False,
        ),
        Path('conf/train/sft_stage_b_cuda_bf16.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'train',
                'name': 'sft_stage_b_cuda_bf16',
                'stage': 'b',
                'base_model_name_or_path': DEFAULT_SUBMISSION_BASE_MODEL,
                'precision': 'bf16',
                'lora_r': 32,
                'lora_alpha': 32,
                'lora_dropout': 0.0,
                'target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
                'learning_rate': 0.00005,
                'num_epochs': 1.0,
                'max_seq_len': 1024,
                'gradient_accumulation_steps': 8,
                'per_device_train_batch_size': 1,
                'weighted_loss': True,
            },
            sort_keys=False,
        ),
        Path('conf/preference/dpo_format_pairs.yaml'): yaml.safe_dump({'version': 'v3', 'section': 'preference', 'name': 'dpo_format_pairs', 'pair_kind': 'format'}, sort_keys=False),
        Path('conf/preference/dpo_correction_pairs.yaml'): yaml.safe_dump({'version': 'v3', 'section': 'preference', 'name': 'dpo_correction_pairs', 'pair_kind': 'correction'}, sort_keys=False),
        Path('conf/package/cuda_submission_smoke.yaml'): yaml.safe_dump(
            {
                'version': 'v3',
                'section': 'package',
                'name': 'cuda_submission_smoke',
                'expected_base_model_name_or_path': DEFAULT_SUBMISSION_BASE_MODEL,
                'required_files': ['adapter_config.json', 'adapter_model.safetensors'],
                'expected_target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
                'expected_rank_cap': 32,
                'required_adapter_config_keys': ['base_model_name_or_path', 'target_modules', 'r'],
                'local_base_model_path': None,
                'submission_zip_name': 'submission_v3.zip',
            },
            sort_keys=False,
        ),
    }
    for marker in V3_SCAFFOLD_MARKER_FILES:
        payloads[marker] = ''
    return payloads


def ensure_v3_layout_scaffold(version_root: Path = VERSION_ROOT) -> None:
    ensure_directories(version_root / relative_path for relative_path in V3_SCAFFOLD_DIRECTORIES)
    for relative_path, contents in render_v3_yaml_payloads().items():
        path = version_root / relative_path
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding='utf-8')
    registry_specs = {
        version_root / 'data/processed/candidate_registry_v3.csv': [
            'candidate_id',
            'parent_candidate_id',
            'runtime_lane',
            'mac_candidate_id',
            'cuda_run_id',
            'stage',
            'mix_name',
            'train_config',
            'rank',
            'alpha',
            'dropout',
            'weighted_loss',
            'overall_acc',
            'hard_shadow_acc',
            'format_fail_rate',
            'boxed_rate',
            'cuda_repro_pass',
            'packaging_pass',
            'selected_for_submit',
            'status',
            'failure_reason',
            'notes',
            'recorded_at',
        ],
        version_root / 'data/processed/cuda_reproduction_registry_v3.csv': [
            'candidate_id',
            'spec_path',
            'status',
            'manual_command_path',
            'created_at',
            'notes',
        ],
        version_root / 'outputs/reports/weighted_ablation_v3.csv': [
            'run_id',
            'config_name',
            'stage',
            'weighted_loss',
            'train_pack_path',
            'train_records',
            'valid_records',
            'status',
            'final_train_loss',
            'final_val_loss',
            'peak_memory_gb',
            'metrics_path',
            'manifest_path',
            'failure_reason',
            'notes',
            'recorded_at',
        ],
    }
    for path, header in registry_specs.items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(','.join(header) + '\n', encoding='utf-8')
    v2_active_model = REPO_ROOT / 'versions' / 'v2' / 'outputs' / 'runtime' / 'active_model.json'
    v3_active_model = version_root / 'outputs/runtime/active_model.json'
    if not v3_active_model.exists() and v2_active_model.exists():
        v3_active_model.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(v2_active_model, v3_active_model)


V4_SCAFFOLD_DIRECTORIES = (
    Path('code'),
    Path('conf'),
    Path('conf/data'),
    Path('conf/train'),
    Path('conf/eval'),
    Path('conf/merge'),
    Path('conf/package'),
    Path('data'),
    Path('data/processed'),
    Path('data/preference'),
    Path('data/rft'),
    Path('data/train_packs'),
    Path('outputs'),
    Path('outputs/audits'),
    Path('outputs/datasets'),
    Path('outputs/eval'),
    Path('outputs/handoff'),
    Path('outputs/models'),
    Path('outputs/runtime'),
    Path('outputs/packaging'),
    Path('outputs/reports'),
    Path('outputs/train'),
    Path('tests'),
)

V4_SCAFFOLD_MARKER_FILES = (
    Path('data/processed/.gitkeep'),
    Path('data/preference/.gitkeep'),
    Path('data/rft/.gitkeep'),
    Path('data/train_packs/.gitkeep'),
    Path('outputs/audits/.gitkeep'),
    Path('outputs/datasets/.gitkeep'),
    Path('outputs/eval/.gitkeep'),
    Path('outputs/handoff/.gitkeep'),
    Path('outputs/packaging/.gitkeep'),
    Path('outputs/reports/.gitkeep'),
    Path('outputs/train/.gitkeep'),
)


def render_v4_yaml_payloads() -> dict[Path, str]:
    payloads: dict[Path, str] = {
        Path('conf/data/preference_format.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'data',
                'name': 'preference_format',
                'input_path': str(SOURCE_V3_PREFERENCE_PAIRS_PATH),
                'pair_kind': 'format',
                'min_chosen_clean': True,
            },
            sort_keys=False,
        ),
        Path('conf/data/preference_correctness.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'data',
                'name': 'preference_correctness',
                'input_path': str(SOURCE_V3_PREFERENCE_PAIRS_PATH),
                'pair_kind': 'correction',
                'allowed_families': sorted(HARD_FAMILIES_V4),
            },
            sort_keys=False,
        ),
        Path('conf/data/rft_accept_pool.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'data',
                'name': 'rft_accept_pool',
                'source_path': str(DEFAULT_V2_REAL_CANONICAL_PATH),
                'allowed_families': sorted(HARD_FAMILIES_V4),
                'min_hard_score': 2.0,
                'max_rows_per_family': 96,
                'probe_config': 'sc_probe_k4',
                'require_clean_format': True,
                'require_exact_correct': True,
                'require_no_extra_numbers': True,
            },
            sort_keys=False,
        ),
        Path('conf/data/stage_c_rft_mix.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'data',
                'name': 'stage_c_rft_mix',
                'target_total': 4096,
                'rft_ratio': 0.9,
                'replay_ratio': 0.1,
                'replay_source_path': str(SOURCE_V3_STAGE_A_OUTPUT_PATH),
            },
            sort_keys=False,
        ),
        Path('conf/data/stage_c_preference_mix.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'data',
                'name': 'stage_c_preference_mix',
                'target_total_pairs': 4096,
                'format_ratio': 0.6,
                'correctness_ratio': 0.4,
            },
            sort_keys=False,
        ),
        Path('conf/train/rft_stage_c_mlx.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'train',
                'name': 'rft_stage_c_mlx',
                'recipe_type': 'stage_c_rft',
                'train_pack_path': str(DEFAULT_V4_STAGE_C_RFT_OUTPUT_PATH),
                'base_model': DEFAULT_MODEL_REPO_ID,
                'init_adapter_path': str(DEFAULT_V3_STAGE_A_ADAPTER_PATH),
                'lora_r': 32,
                'lora_alpha': 32,
                'lora_dropout': 0.0,
                'learning_rate': 5e-5,
                'num_epochs': 1.5,
                'max_seq_len': 1024,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 8,
                'weighted_loss': True,
                'rationale_weight': 1.0,
                'final_line_weight': 3.0,
                'answer_span_weights': {
                    'gravity_constant': 4.0,
                    'unit_conversion': 4.0,
                    'roman_numeral': 4.0,
                    'bit_manipulation': 5.0,
                    'symbol_equation': 6.0,
                    'text_decryption': 3.0,
                },
            },
            sort_keys=False,
        ),
        Path('conf/train/dpo_format_mlx.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'train',
                'name': 'dpo_format_mlx',
                'recipe_type': 'preference_dpo',
                'pair_data_path': str(DEFAULT_V4_STAGE_C_PREFERENCE_OUTPUT_PATH),
                'pair_kind': 'format',
                'base_model': DEFAULT_MODEL_REPO_ID,
                'init_adapter_path': str(DEFAULT_V3_STAGE_A_ADAPTER_PATH),
                'learning_rate': 2e-5,
                'num_epochs': 1.0,
                'max_seq_len': 1024,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 4,
                'dpo_beta': 0.1,
                'max_train_pairs': 3072,
            },
            sort_keys=False,
        ),
        Path('conf/train/dpo_correctness_mlx.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'train',
                'name': 'dpo_correctness_mlx',
                'recipe_type': 'preference_dpo',
                'pair_data_path': str(DEFAULT_V4_STAGE_C_PREFERENCE_OUTPUT_PATH),
                'pair_kind': 'correction',
                'base_model': DEFAULT_MODEL_REPO_ID,
                'init_adapter_path': str(DEFAULT_V3_STAGE_A_ADAPTER_PATH),
                'learning_rate': 2e-5,
                'num_epochs': 1.0,
                'max_seq_len': 1024,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 4,
                'dpo_beta': 0.1,
                'max_train_pairs': 2048,
            },
            sort_keys=False,
        ),
        Path('conf/train/specialist_format_mlx.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'train',
                'name': 'specialist_format_mlx',
                'recipe_type': 'specialist',
                'specialist_tag': 'format',
                'pair_data_path': str(DEFAULT_V4_STAGE_C_PREFERENCE_OUTPUT_PATH),
                'pair_kind': 'format',
                'base_model': DEFAULT_MODEL_REPO_ID,
                'init_adapter_path': str(DEFAULT_V3_STAGE_A_ADAPTER_PATH),
                'learning_rate': 2e-5,
                'num_epochs': 1.0,
                'max_seq_len': 1024,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 4,
                'dpo_beta': 0.1,
                'max_train_pairs': 4096,
            },
            sort_keys=False,
        ),
        Path('conf/train/specialist_bit_mlx.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'train',
                'name': 'specialist_bit_mlx',
                'recipe_type': 'specialist',
                'specialist_tag': 'bit',
                'pair_data_path': str(DEFAULT_V4_STAGE_C_PREFERENCE_OUTPUT_PATH),
                'pair_kind': 'correction',
                'family_filter': ['bit_manipulation'],
                'base_model': DEFAULT_MODEL_REPO_ID,
                'init_adapter_path': str(DEFAULT_V3_STAGE_A_ADAPTER_PATH),
                'learning_rate': 2e-5,
                'num_epochs': 1.0,
                'max_seq_len': 1024,
                'per_device_train_batch_size': 1,
                'gradient_accumulation_steps': 4,
                'dpo_beta': 0.1,
                'max_train_pairs': 2048,
            },
            sort_keys=False,
        ),
        Path('conf/train/stage_c_cuda_bf16.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'train',
                'name': 'stage_c_cuda_bf16',
                'base_model_name_or_path': DEFAULT_SUBMISSION_BASE_MODEL,
                'precision': 'bf16',
                'lora_r': 32,
                'lora_alpha': 32,
                'lora_dropout': 0.0,
                'learning_rate': 5e-5,
                'num_epochs': 1.0,
                'max_seq_len': 1024,
                'gradient_accumulation_steps': 8,
                'per_device_train_batch_size': 1,
            },
            sort_keys=False,
        ),
        Path('conf/eval/candidate_score_quick.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'eval',
                'name': 'candidate_score_quick',
                'gate_name': 'quick',
                'datasets': [
                    {
                        'dataset_name': 'shadow_128',
                        'input_path': str(REPO_ROOT / 'versions' / 'v1' / 'data' / 'eval_packs' / 'shadow_128.csv'),
                        'eval_config': 'official_lb',
                    }
                ],
            },
            sort_keys=False,
        ),
        Path('conf/eval/candidate_score_serious.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'eval',
                'name': 'candidate_score_serious',
                'gate_name': 'serious',
                'datasets': [
                    {
                        'dataset_name': 'shadow_256',
                        'input_path': str(REPO_ROOT / 'versions' / 'v1' / 'data' / 'eval_packs' / 'shadow_256.csv'),
                        'eval_config': 'official_lb',
                    },
                    {
                        'dataset_name': 'hard_shadow_256',
                        'input_path': str(REPO_ROOT / 'versions' / 'v1' / 'data' / 'eval_packs' / 'hard_shadow_256.csv'),
                        'eval_config': 'official_lb',
                    },
                ],
            },
            sort_keys=False,
        ),
        Path('conf/eval/candidate_score_weekly.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'eval',
                'name': 'candidate_score_weekly',
                'gate_name': 'weekly',
                'datasets': [
                    {
                        'dataset_name': 'group_shift_split0',
                        'input_path': str(REPO_ROOT / 'versions' / 'v1' / 'data' / 'eval_packs' / 'group_shift_split0.csv'),
                        'eval_config': 'official_lb',
                    },
                    {
                        'dataset_name': 'group_shift_split1',
                        'input_path': str(REPO_ROOT / 'versions' / 'v1' / 'data' / 'eval_packs' / 'group_shift_split1.csv'),
                        'eval_config': 'official_lb',
                    },
                    {
                        'dataset_name': 'group_shift_split2',
                        'input_path': str(REPO_ROOT / 'versions' / 'v1' / 'data' / 'eval_packs' / 'group_shift_split2.csv'),
                        'eval_config': 'official_lb',
                    },
                    {
                        'dataset_name': 'holdout_hard',
                        'input_path': str(REPO_ROOT / 'versions' / 'v1' / 'data' / 'eval_packs' / 'holdout_hard.csv'),
                        'eval_config': 'official_lb',
                    },
                ],
            },
            sort_keys=False,
        ),
        Path('conf/merge/generalist_specialist_merge.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'merge',
                'name': 'generalist_specialist_merge',
                'weights': {'generalist': 0.75, 'specialist': 0.25},
            },
            sort_keys=False,
        ),
        Path('conf/merge/rank32_compress.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'merge',
                'name': 'rank32_compress',
                'method': 'noop_same_shape_rank32',
                'rank_cap': 32,
            },
            sort_keys=False,
        ),
        Path('conf/package/cuda_submission_smoke.yaml'): yaml.safe_dump(
            {
                'version': 'v4',
                'section': 'package',
                'name': 'cuda_submission_smoke',
                'expected_base_model_name_or_path': DEFAULT_SUBMISSION_BASE_MODEL,
                'required_files': ['adapter_config.json', 'adapter_model.safetensors'],
                'expected_target_modules': ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
                'expected_rank_cap': 32,
                'required_adapter_config_keys': ['base_model_name_or_path', 'target_modules', 'r'],
                'local_base_model_path': None,
                'submission_zip_name': 'submission_v4.zip',
            },
            sort_keys=False,
        ),
    }
    for marker in V4_SCAFFOLD_MARKER_FILES:
        payloads[marker] = ''
    return payloads


def ensure_csv_header(path: Path, header: Sequence[str]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(','.join(header) + '\n', encoding='utf-8')


def upsert_csv_row(path: Path, header: Sequence[str], key_fields: Sequence[str], row: dict[str, Any]) -> None:
    rows: list[dict[str, Any]] = []
    if path.exists():
        with path.open('r', encoding='utf-8', newline='') as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
    matched = False
    for index, existing in enumerate(rows):
        if all(str(existing.get(key, '')) == str(row.get(key, '')) for key in key_fields):
            rows[index] = {column: row.get(column, '') for column in header}
            matched = True
            break
    if not matched:
        rows.append({column: row.get(column, '') for column in header})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(header))
        writer.writeheader()
        writer.writerows(rows)


def append_experiment_log(kind: str, status: str, **payload: Any) -> None:
    append_jsonl(
        Path(DEFAULT_V4_EXPERIMENT_LOG_PATH),
        {
            'created_at': utc_now(),
            'kind': kind,
            'status': status,
            **payload,
        },
    )


def load_active_model_manifest_v4() -> dict[str, Any]:
    for path in (DEFAULT_V3_ACTIVE_MODEL_PATH, DEFAULT_ACTIVE_MODEL_PATH):
        if path.exists():
            return load_json_file(path, default={})
    return {}


def resolve_active_snapshot_path_v4() -> str:
    preferred_local_model = resolve_preferred_mlx_model_path_v4()
    if preferred_local_model is not None:
        return preferred_local_model
    active_model = load_active_model_manifest_v4()
    snapshot_dir = normalize_optional_text(active_model.get('snapshot_dir'))
    fallback_model = resolve_fallback_mlx_model_path_v4(snapshot_dir)
    if fallback_model is not None:
        return fallback_model
    if snapshot_dir is None:
        return str(DEFAULT_V3_ACTIVE_MODEL_PATH)
    return snapshot_dir


def ensure_v4_layout_scaffold(version_root: Path = VERSION_ROOT) -> None:
    ensure_directories(version_root / relative_path for relative_path in V4_SCAFFOLD_DIRECTORIES)
    for relative_path, contents in render_v4_yaml_payloads().items():
        path = version_root / relative_path
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding='utf-8')
    registry_specs = {
        version_root / 'data/processed/candidate_registry_v4.csv': [
            'candidate_id',
            'parent_candidate_id',
            'candidate_kind',
            'manifest_path',
            'adapter_path',
            'runtime_lane',
            'stage',
            'recipe_type',
            'pair_kind',
            'train_pack_path',
            'overall_acc',
            'hard_shadow_acc',
            'format_fail_rate',
            'extraction_fail_rate',
            'submit_value',
            'cuda_repro_pass',
            'packaging_pass',
            'selected_for_submit',
            'status',
            'failure_reason',
            'notes',
            'recorded_at',
        ],
        version_root / 'data/processed/specialist_candidate_registry_v4.csv': [
            'candidate_id',
            'specialist_tag',
            'parent_candidate_id',
            'manifest_path',
            'adapter_path',
            'status',
            'notes',
            'recorded_at',
        ],
        version_root / 'data/processed/merge_candidate_registry_v4.csv': [
            'merge_id',
            'generalist_candidate_id',
            'specialist_candidate_id',
            'merge_weights',
            'manifest_path',
            'adapter_path',
            'compression_method',
            'rank_after_compression',
            'quick_score',
            'serious_score',
            'status',
            'notes',
            'recorded_at',
        ],
        version_root / 'outputs/reports/local_scoreboard_v4.csv': [
            'candidate_id',
            'parent_candidate_id',
            'gate_name',
            'dataset_name',
            'run_name',
            'overall_accuracy',
            'hard_split_accuracy',
            'bit_accuracy',
            'text_accuracy',
            'symbol_accuracy',
            'format_fail_rate',
            'extraction_fail_rate',
            'avg_output_len_chars',
            'boxed_rate',
            'submit_value',
            'manifest_path',
            'adapter_path',
            'recorded_at',
        ],
        version_root / 'outputs/reports/family_regret_report_v4.csv': [
            'candidate_id',
            'parent_candidate_id',
            'dataset_name',
            'family',
            'candidate_acc',
            'parent_acc',
            'delta_acc',
            'candidate_format_fail_rate',
            'parent_format_fail_rate',
            'delta_format_fail_rate',
            'recorded_at',
        ],
        version_root / 'data/processed/cuda_reproduction_registry_v4.csv': [
            'candidate_id',
            'spec_path',
            'status',
            'manual_command_path',
            'created_at',
            'notes',
        ],
    }
    for path, header in registry_specs.items():
        ensure_csv_header(path, header)
    active_model_path = version_root / 'outputs/runtime/active_model.json'
    if not active_model_path.exists():
        source_active_model = DEFAULT_V3_ACTIVE_MODEL_PATH if DEFAULT_V3_ACTIVE_MODEL_PATH.exists() else DEFAULT_ACTIVE_MODEL_PATH
        if source_active_model.exists():
            active_model_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_active_model, active_model_path)


def sanitize_local_name(value: str) -> str:
    normalized = value.strip().replace('/', '--')
    if not normalized:
        raise ValueError('local model name must not be empty.')
    return normalized


def default_model_directory(spec: ModelDownloadSpec) -> Path:
    return MODELS_ROOT / sanitize_local_name(spec.local_name)


def default_lms_models_root() -> Path:
    return Path.home() / '.lmstudio' / 'models'


def split_repo_id(repo_id: str) -> tuple[str, str]:
    publisher, _, artifact = repo_id.partition('/')
    if not publisher or not artifact:
        raise ValueError(f'repo_id must be in <publisher>/<artifact> form: {repo_id}')
    return publisher, artifact


def default_lms_model_path(repo_id: str, *, models_root: Path | None = None) -> Path:
    publisher, artifact = split_repo_id(repo_id)
    root = models_root if models_root is not None else default_lms_models_root()
    return root / publisher / artifact


def ensure_lms_model_symlink(snapshot_dir: Path, repo_id: str, *, models_root: Path | None = None) -> Path:
    link_path = default_lms_model_path(repo_id, models_root=models_root)
    link_path.parent.mkdir(parents=True, exist_ok=True)
    if link_path.is_symlink():
        if link_path.resolve() == snapshot_dir.resolve():
            return link_path
        raise ValueError(f'Existing symlink points elsewhere: {link_path} -> {link_path.resolve()}')
    if link_path.exists():
        raise ValueError(f'LM Studio model path already exists and is not a symlink: {link_path}')
    link_path.symlink_to(snapshot_dir.resolve(), target_is_directory=True)
    return link_path


def resolve_snapshot_download() -> Any:
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError(
            'huggingface_hub is required to download the fixed MLX model. '
            'Install it with `uv add huggingface_hub`.'
        ) from exc
    return snapshot_download


def download_model_snapshot(spec: ModelDownloadSpec, target_dir: Path) -> Path:
    snapshot_download = resolve_snapshot_download()
    token = os.environ.get(spec.token_env) or None
    resolved_path = snapshot_download(
        repo_id=spec.repo_id,
        revision=spec.revision,
        local_dir=str(target_dir),
        token=token,
        resume_download=True,
    )
    return Path(resolved_path)


def collect_snapshot_stats(snapshot_dir: Path) -> tuple[int, int]:
    file_count = 0
    total_size_bytes = 0
    for path in snapshot_dir.rglob('*'):
        if not path.is_file():
            continue
        file_count += 1
        total_size_bytes += path.stat().st_size
    return file_count, total_size_bytes


def build_model_manifest(spec: ModelDownloadSpec, snapshot_dir: Path) -> dict[str, Any]:
    file_count, total_size_bytes = collect_snapshot_stats(snapshot_dir)
    return {
        'repo_id': spec.repo_id,
        'local_name': sanitize_local_name(spec.local_name),
        'revision': spec.revision,
        'token_env': spec.token_env,
        'snapshot_dir': str(snapshot_dir.resolve()),
        'downloaded_at': utc_now(),
        'file_count': file_count,
        'total_size_bytes': total_size_bytes,
    }


def load_json_file(path: Path, *, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def save_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def upsert_registry_entry(entries: list[dict[str, Any]], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    key = (
        manifest.get('repo_id'),
        manifest.get('local_name'),
        manifest.get('revision'),
    )
    filtered = [
        entry
        for entry in entries
        if (
            entry.get('repo_id'),
            entry.get('local_name'),
            entry.get('revision'),
        )
        != key
    ]
    filtered.append(manifest)
    return sorted(
        filtered,
        key=lambda entry: (
            str(entry.get('local_name', '')),
            str(entry.get('repo_id', '')),
            str(entry.get('revision') or ''),
        ),
    )


def write_active_model(manifest: dict[str, Any], active_path: Path) -> None:
    save_json_file(active_path, manifest)


def update_model_registry(manifest: dict[str, Any], registry_path: Path) -> None:
    existing = load_json_file(registry_path, default=[])
    if not isinstance(existing, list):
        raise ValueError('model registry must be a JSON list.')
    updated = upsert_registry_entry(existing, manifest)
    save_json_file(registry_path, updated)


def load_active_model_manifest(active_path: Path) -> dict[str, Any]:
    payload = load_json_file(active_path, default=None)
    if payload is None:
        raise FileNotFoundError(f'Active model manifest was not found: {active_path}')
    if not isinstance(payload, dict):
        raise ValueError('Active model manifest must be a JSON object.')
    return payload


def resolve_active_model_directory(active_path: Path) -> Path:
    payload = load_active_model_manifest(active_path)
    snapshot_dir = Path(str(payload.get('snapshot_dir', '')).strip())
    if not snapshot_dir:
        raise ValueError(f'Active model manifest is missing snapshot_dir: {active_path}')
    if not snapshot_dir.exists():
        raise FileNotFoundError(f'Active model snapshot directory does not exist: {snapshot_dir}')
    return snapshot_dir


def resolve_mlx_runtime() -> tuple[Any, Any]:
    try:
        from mlx_lm import generate, load
    except ImportError as exc:
        raise RuntimeError(
            'mlx-lm and mlx are required for local model smoke tests. '
            'Install them in your Mac environment before running `smoke-model`.'
        ) from exc
    return load, generate


def resolve_lms_binary() -> str:
    binary = shutil.which('lms')
    if not binary:
        raise RuntimeError('LM Studio CLI `lms` was not found on PATH.')
    return binary


def run_lms_command(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=True, text=True, capture_output=True)


def smoke_with_lms(
    *,
    snapshot_dir: Path,
    repo_id: str,
    prompt: str,
    max_tokens: int,
    ttl_seconds: int,
    identifier: str,
) -> str:
    del max_tokens  # LM Studio CLI prompt mode does not expose max_tokens here.
    lms = resolve_lms_binary()
    model_key = repo_id
    ensure_lms_model_symlink(snapshot_dir, repo_id)
    run_lms_command([lms, 'load', model_key, '--yes', '--ttl', str(ttl_seconds), '--identifier', identifier])
    try:
        result = run_lms_command(
            [
                lms,
                'chat',
                model_key,
                '-p',
                prompt,
                '-y',
                '--ttl',
                str(ttl_seconds),
                '--dont-fetch-catalog',
            ]
        )
        return result.stdout.strip()
    finally:
        subprocess.run([lms, 'unload', identifier], check=False, text=True, capture_output=True)
        subprocess.run([lms, 'unload', model_key], check=False, text=True, capture_output=True)


def make_planned_command_placeholder(command_name: str, step_label: str) -> Callable[[argparse.Namespace], None]:
    def _run(_: argparse.Namespace) -> None:
        raise RuntimeError(
            f'`{command_name}` is scaffolded in v2 Step 1 only. '
            f'Its implementation belongs to {step_label}, so do not use it yet.'
        )

    return _run


def run_download_model(args: argparse.Namespace) -> None:
    ensure_runtime_directories()
    spec = ModelDownloadSpec(
        repo_id=args.repo_id,
        local_name=args.local_name,
        revision=args.revision,
        token_env=args.token_env,
    )
    target_dir = Path(args.output_dir) if args.output_dir else default_model_directory(spec)
    snapshot_dir = download_model_snapshot(spec, target_dir)
    manifest = build_model_manifest(spec, snapshot_dir)
    write_active_model(manifest, Path(args.active_model_path))
    update_model_registry(manifest, Path(args.registry_path))
    print(
        'Model download completed:',
        f"repo_id={manifest['repo_id']}",
        f"snapshot_dir={manifest['snapshot_dir']}",
        f"file_count={manifest['file_count']}",
        f"total_size_bytes={manifest['total_size_bytes']}",
    )


def run_show_active_model(args: argparse.Namespace) -> None:
    payload = load_active_model_manifest(Path(args.active_model_path))
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def run_smoke_model(args: argparse.Namespace) -> None:
    active_manifest = load_active_model_manifest(Path(args.active_model_path))
    model_dir = Path(args.model_dir) if args.model_dir else resolve_active_model_directory(Path(args.active_model_path))
    prompt = args.prompt.strip()
    runtime = args.runtime
    if runtime in {'auto', 'python'}:
        try:
            load, generate = resolve_mlx_runtime()
            model, tokenizer = load(str(model_dir))
            output = generate(model, tokenizer, prompt, max_tokens=args.max_tokens, verbose=False)
            resolved_runtime = 'python'
        except RuntimeError:
            if runtime == 'python':
                raise
            output = smoke_with_lms(
                snapshot_dir=model_dir,
                repo_id=args.repo_id or str(active_manifest.get('repo_id', DEFAULT_MODEL_REPO_ID)),
                prompt=prompt,
                max_tokens=args.max_tokens,
                ttl_seconds=args.ttl,
                identifier=args.identifier,
            )
            resolved_runtime = 'lms'
    else:
        output = smoke_with_lms(
            snapshot_dir=model_dir,
            repo_id=args.repo_id or str(active_manifest.get('repo_id', DEFAULT_MODEL_REPO_ID)),
            prompt=prompt,
            max_tokens=args.max_tokens,
            ttl_seconds=args.ttl,
            identifier=args.identifier,
        )
        resolved_runtime = 'lms'
    print('Model smoke completed:')
    print(f'runtime={resolved_runtime}')
    print(f'model_dir={model_dir}')
    print(f'prompt={prompt!r}')
    print('output=')
    print(output.strip())


def _load_v1_module() -> Any:
    import importlib.util as _ilu
    import sys as _sys

    module_name = 'v1_train_for_v2_pipeline'
    existing = _sys.modules.get(module_name)
    if existing is not None:
        return existing

    v1_path = Path(__file__).resolve().parents[2] / 'v1' / 'code' / 'train.py'
    spec = _ilu.spec_from_file_location(module_name, v1_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Unable to load v1 utilities from {v1_path}')
    module = _ilu.module_from_spec(spec)
    _sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def stable_hash(*values: Any, length: int = 16) -> str:
    digest = hashlib.sha256('||'.join('' if value is None else str(value) for value in values).encode('utf-8')).hexdigest()
    return digest[:length]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open('r', encoding='utf-8') as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + '\n')


def write_jsonl(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + '\n')


def _read_table(path: Path):
    import pandas as pd

    if path.suffix == '.parquet':
        return pd.read_parquet(path)
    if path.suffix == '.csv':
        return pd.read_csv(path)
    if path.suffix == '.jsonl':
        return pd.DataFrame(read_jsonl(path))
    raise ValueError(f'Unsupported table format: {path}')


def _write_table(path: Path, frame: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == '.parquet':
        frame.to_parquet(path, index=False)
        return
    if path.suffix == '.csv':
        frame.to_csv(path, index=False)
        return
    raise ValueError(f'Unsupported output format: {path}')


def select_v3_format_policy(answer: str, family: str) -> str:
    v1 = _load_v1_module()
    risk = v1.analyze_extraction_risk(answer)
    if '{' in answer:
        return 'final_answer'
    if risk['contains_right_brace'] or risk['contains_backslash'] or risk['contains_backtick'] or risk['contains_newline']:
        return 'final_answer'
    if family == 'symbol_equation' and any(marker in answer for marker in ('}', '\\', '`')):
        return 'final_answer'
    return 'boxed'


def render_v3_final_answer(answer: str, family: str) -> str:
    answer_text = answer.strip()
    if not answer_text:
        raise ValueError('answer text must not be empty')
    if select_v3_format_policy(answer_text, family) == 'boxed':
        return rf'\boxed{{{answer_text}}}'
    return f'Final answer: {answer_text}'


def build_teacher_style_prompt(raw_prompt: str, answer: str, family: str, target_style: str) -> str:
    final_rule = (
        'Put the final answer on the last line exactly as `\\boxed{ANSWER}`.'
        if select_v3_format_policy(answer, family) == 'boxed'
        else 'Put the final answer on the last line exactly as `Final answer: ANSWER`.'
    )
    style_text = {
        'long': 'Give a detailed but clean solution in at most 6 short reasoning lines.',
        'short': 'Give a concise solution in 1 to 3 reasoning lines.',
        'answer_only': 'Give only the final answer line. Do not include reasoning.',
        'format_safe': 'Optimize for extraction safety. No extra numbers, no extra boxed answers, and keep the final answer on the last line only.',
    }.get(target_style, 'Give a concise solution.')
    return f'{raw_prompt}\n\n{style_text} {final_rule} Do not add any explanation after the final answer.'


def _build_teacher_candidate_row(row: dict[str, Any], *, target_style: str, teacher_seed: int, teacher_name: str, sample_idx: int) -> dict[str, Any]:
    answer = normalize_optional_text(row.get('answer_canonical')) or normalize_optional_text(row.get('answer')) or ''
    family = normalize_optional_text(row.get('family')) or ''
    prompt = normalize_optional_text(row.get('prompt')) or ''
    return {
        'candidate_id': f"tcan_{row.get('id')}_{target_style}_{sample_idx}",
        'source_id': str(row.get('id', '')),
        'source_kind': normalize_optional_text(row.get('source_kind')) or 'real',
        'family': family,
        'answer_type': normalize_optional_text(row.get('answer_type')) or '',
        'prompt': prompt,
        'answer': answer,
        'format_policy': select_v3_format_policy(answer, family),
        'target_style': target_style,
        'teacher_name': teacher_name,
        'teacher_seed': teacher_seed,
        'sampling_profile': json.dumps({}, ensure_ascii=False, sort_keys=True),
        'generation_prompt': build_teacher_style_prompt(prompt, answer, family, target_style),
    }


def run_bootstrap_v3(args: argparse.Namespace) -> None:
    del args
    ensure_v3_layout_scaffold()
    created = sorted(str(path.relative_to(VERSION_ROOT)) for path in VERSION_ROOT.rglob('*') if path.is_file())
    print(json.dumps({'version': 'v3', 'created_at': utc_now(), 'files': created}, ensure_ascii=False, indent=2))


def run_build_teacher_trace_candidates(args: argparse.Namespace) -> None:
    import pandas as pd

    cfg = _load_yaml_config(args.config_path)
    real_path = _require_existing_path(args.input_path, label='teacher trace input parquet')
    frame = pd.read_parquet(real_path)
    max_rows = args.max_rows
    if max_rows is not None and len(frame) > max_rows:
        frame = frame.head(int(max_rows)).copy()
    target_styles = list(cfg.get('target_styles', ['long', 'short', 'answer_only', 'format_safe']))
    style_samples = dict(cfg.get('style_samples', {}))
    hard_family_styles = set(cfg.get('hard_family_styles', ['short', 'format_safe']))
    hard_family_sample_count = int(cfg.get('hard_family_sample_count', 4))
    seed = int(cfg.get('seed', 73))
    teacher_name = str(cfg.get('teacher_name', DEFAULT_MODEL_REPO_ID))

    rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    for record in frame.to_dict(orient='records'):
        family = normalize_optional_text(record.get('family')) or ''
        generated_count = 0
        for style in target_styles:
            sample_count = int(style_samples.get(style, 1))
            if family in {'bit_manipulation', 'text_decryption', 'symbol_equation'} and style in hard_family_styles:
                sample_count = max(sample_count, hard_family_sample_count)
            for sample_idx in range(sample_count):
                rows.append(
                    _build_teacher_candidate_row(
                        record,
                        target_style=style,
                        teacher_seed=seed + sample_idx,
                        teacher_name=teacher_name,
                        sample_idx=sample_idx,
                    )
                )
                generated_count += 1
        audit_rows.append({'source_id': record.get('id', ''), 'family': family, 'status': 'accepted', 'generated_candidates': generated_count})

    out_path = Path(args.output_path)
    write_jsonl(out_path, rows)
    audit_path = Path(getattr(args, 'audit_output_path', AUDITS_ROOT / 'teacher_trace_candidates_v3.csv'))
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit_rows).to_csv(audit_path, index=False)
    print(json.dumps({'version': 'v3', 'created_at': utc_now(), 'input_rows': int(len(frame)), 'output_rows': int(len(rows)), 'output_path': str(out_path), 'audit_path': str(audit_path)}, ensure_ascii=False, indent=2))


def run_generate_teacher_traces(args: argparse.Namespace) -> None:
    candidates = read_jsonl(_require_existing_path(args.input_path, label='teacher candidate jsonl'))
    if args.limit is not None:
        candidates = candidates[: int(args.limit)]
    active_manifest = load_active_model_manifest(Path(args.active_model_path))
    model_dir = Path(args.model_dir) if args.model_dir else resolve_training_base_model(DEFAULT_MODEL_REPO_ID, active_manifest)
    load, generate = resolve_mlx_runtime()
    from mlx_lm.sample_utils import make_sampler

    model, tokenizer = load(str(model_dir))
    out_path = Path(args.output_path)
    if out_path.exists() and not args.append:
        out_path.unlink()
    audit_rows: list[dict[str, Any]] = []
    sampler = make_sampler(
        temp=float(args.temp),
        top_p=float(args.top_p) if 0.0 < float(args.top_p) < 1.0 else 0.0,
    )

    for index, candidate in enumerate(candidates):
        record = dict(candidate)
        record['generated_at'] = utc_now()
        record['generation_index'] = index
        messages = [{'role': 'user', 'content': str(candidate['generation_prompt'])}]
        rendered = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_dict=False)
        try:
            raw_output = generate(
                model,
                tokenizer,
                rendered,
                verbose=False,
                max_tokens=int(args.max_tokens),
                sampler=sampler,
            )
        except Exception as exc:
            record['generation_status'] = 'error'
            record['error_type'] = type(exc).__name__
            record['error_message'] = str(exc)
            record['raw_output'] = ''
            audit_rows.append({'candidate_id': record.get('candidate_id', ''), 'status': 'error', 'reason': f"{type(exc).__name__}:{exc}"})
        else:
            record['generation_status'] = 'ok'
            record['error_type'] = ''
            record['error_message'] = ''
            record['raw_output'] = raw_output.strip()
            audit_rows.append({'candidate_id': record.get('candidate_id', ''), 'status': 'ok', 'reason': ''})
        append_jsonl(out_path, record)

    audit_path = Path(getattr(args, 'audit_output_path', AUDITS_ROOT / 'teacher_trace_generation_v3.csv'))
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit_rows).to_csv(audit_path, index=False)
    print(json.dumps({'version': 'v3', 'created_at': utc_now(), 'output_path': str(out_path), 'num_candidates': len(candidates), 'audit_path': str(audit_path)}, ensure_ascii=False, indent=2))


def _assess_teacher_trace(raw_output: str, gold_answer: str, family: str) -> dict[str, Any]:
    v1 = _load_v1_module()
    extracted_answer, extraction_source = v1.extract_final_answer_with_source(raw_output)
    is_correct = bool(v1.verify(gold_answer, extracted_answer))
    format_bucket = v1.classify_format_bucket(raw_output, extracted_answer, extraction_source)
    format_pass = format_bucket in {'clean_boxed', 'clean_final_answer'}
    expected_policy = select_v3_format_policy(gold_answer, family)
    lines = [line.strip() for line in raw_output.splitlines() if line.strip()]
    final_line = lines[-1] if lines else ''
    final_line_only = bool(final_line) and final_line == render_v3_final_answer(extracted_answer, family)
    boxed_count = v1.count_boxed_occurrences(raw_output)
    has_extra_trailing_numbers = bool(v1.detect_extra_trailing_numbers(raw_output, extracted_answer))
    rejection_reasons: list[str] = []
    if not is_correct:
        rejection_reasons.append('wrong_answer')
    if not format_pass:
        rejection_reasons.append(f'format_fail:{format_bucket}')
    if boxed_count > 1:
        rejection_reasons.append('multiple_boxed')
    if has_extra_trailing_numbers:
        rejection_reasons.append('extra_trailing_numbers')
    if expected_policy == 'boxed' and format_bucket != 'clean_boxed':
        rejection_reasons.append('expected_boxed_but_not_boxed')
    if expected_policy == 'final_answer' and format_bucket != 'clean_final_answer':
        rejection_reasons.append('unsafe_answer_boxed')
    if expected_policy == 'final_answer' and boxed_count > 0:
        rejection_reasons.append('unsafe_answer_contains_boxed')
    if not final_line_only:
        rejection_reasons.append('final_answer_not_last_line')
    rejection_reasons = list(dict.fromkeys(rejection_reasons))
    strict_pass = not rejection_reasons
    selection_reason = 'strict_pass' if strict_pass else '|'.join(rejection_reasons)

    return {
        'extracted_answer': extracted_answer,
        'extraction_source': extraction_source,
        'is_correct': is_correct,
        'format_bucket': format_bucket,
        'format_pass': format_pass,
        'boxed_policy': expected_policy,
        'boxed_count': boxed_count,
        'has_extra_trailing_numbers': has_extra_trailing_numbers,
        'trace_len_chars': len(raw_output),
        'trace_len_tokens_est': len(re.findall(r'\S+', raw_output)),
        'strict_pass': strict_pass,
        'selection_reason': selection_reason,
        'final_line_only': final_line_only,
        'rejection_reasons': rejection_reasons,
    }


def run_filter_teacher_traces(args: argparse.Namespace) -> None:
    import pandas as pd

    input_path = _require_existing_path(args.input_path, label='teacher generations input')
    if input_path.suffix in {'.parquet', '.csv'}:
        generated = _read_table(input_path).to_dict(orient='records')
    else:
        generated = read_jsonl(input_path)
    registry_rows: list[dict[str, Any]] = []
    accepted_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    for index, record in enumerate(generated):
        raw_output = str(record.get('raw_output', '')).strip()
        gold_answer = str(record.get('answer', ''))
        family = str(record.get('family', ''))
        if record.get('generation_status') != 'ok':
            row = {
                'trace_id': f"trace_{record.get('candidate_id', index)}",
                'source_id': record.get('source_id', ''),
                'source_kind': record.get('source_kind', 'real'),
                'family': family,
                'answer_type': record.get('answer_type', ''),
                'target_style': record.get('target_style', ''),
                'teacher_name': record.get('teacher_name', ''),
                'teacher_seed': record.get('teacher_seed', 0),
                'sampling_profile': record.get('sampling_profile', '{}'),
                'raw_output': raw_output,
                'extracted_answer': 'NOT_FOUND',
                'is_correct': False,
                'format_bucket': 'not_found',
                'format_pass': False,
                'boxed_policy': select_v3_format_policy(gold_answer, family),
                'trace_len_chars': 0,
                'trace_len_tokens_est': 0,
                'consensus_rate': 0.0,
                'selected_for_training': False,
                'selected_for_preference': False,
                'selected_for_rft': False,
                'selection_reason': f"generation_error:{record.get('error_type', 'unknown')}",
                'rejection_reasons': [f"generation_error:{record.get('error_type', 'unknown')}"],
                'prompt': record.get('prompt', ''),
                'answer': gold_answer,
                'format_policy': record.get('format_policy', ''),
            }
        else:
            assessed = _assess_teacher_trace(raw_output, gold_answer, family)
            row = {
                'trace_id': f"trace_{record.get('candidate_id', index)}",
                'source_id': record.get('source_id', ''),
                'source_kind': record.get('source_kind', 'real'),
                'family': family,
                'answer_type': record.get('answer_type', ''),
                'target_style': record.get('target_style', ''),
                'teacher_name': record.get('teacher_name', ''),
                'teacher_seed': record.get('teacher_seed', 0),
                'sampling_profile': record.get('sampling_profile', '{}'),
                'raw_output': raw_output,
                'extracted_answer': assessed['extracted_answer'],
                'is_correct': assessed['is_correct'],
                'format_bucket': assessed['format_bucket'],
                'format_pass': assessed['format_pass'],
                'boxed_policy': assessed['boxed_policy'],
                'boxed_count': assessed['boxed_count'],
                'has_extra_trailing_numbers': assessed['has_extra_trailing_numbers'],
                'trace_len_chars': assessed['trace_len_chars'],
                'trace_len_tokens_est': assessed['trace_len_tokens_est'],
                'consensus_rate': 1.0 if assessed['strict_pass'] else 0.0,
                'selected_for_training': assessed['strict_pass'],
                'selected_for_preference': assessed['strict_pass'],
                'selected_for_rft': assessed['strict_pass'] and assessed['trace_len_tokens_est'] <= 96,
                'selection_reason': assessed['selection_reason'],
                'rejection_reasons': assessed['rejection_reasons'],
                'prompt': record.get('prompt', ''),
                'answer': gold_answer,
                'format_policy': record.get('format_policy', ''),
            }
        registry_rows.append(row)
        audit_rows.append(
            {
                'trace_id': row['trace_id'],
                'source_id': row.get('source_id', ''),
                'family': row.get('family', ''),
                'target_style': row.get('target_style', ''),
                'is_correct': row.get('is_correct', False),
                'format_bucket': row.get('format_bucket', ''),
                'boxed_policy': row.get('boxed_policy', ''),
                'boxed_count': row.get('boxed_count', 0),
                'has_extra_trailing_numbers': row.get('has_extra_trailing_numbers', False),
                'selected_for_training': row.get('selected_for_training', False),
                'selection_reason': row.get('selection_reason', ''),
                'rejection_reason': '|'.join(row.get('rejection_reasons', [])),
                'raw_output': row.get('raw_output', ''),
                'extracted_answer': row.get('extracted_answer', ''),
                'answer': row.get('answer', ''),
            }
        )
        if row['selected_for_training']:
            accepted_rows.append(row)

    registry_df = pd.DataFrame(registry_rows)
    accepted_df = pd.DataFrame(accepted_rows)
    _write_table(Path(args.registry_path), registry_df)
    _write_table(Path(args.output_path), accepted_df)
    audit_path = Path(getattr(args, 'audit_output_path', DEFAULT_V3_FORMAT_AUDIT_OUTPUT_PATH))
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit_rows).to_csv(audit_path, index=False)
    print(json.dumps({'version': 'v3', 'created_at': utc_now(), 'registry_rows': int(len(registry_df)), 'accepted_rows': int(len(accepted_df)), 'registry_path': str(args.registry_path), 'output_path': str(args.output_path), 'audit_path': str(audit_path)}, ensure_ascii=False, indent=2))


def run_audit_format(args: argparse.Namespace) -> None:
    import pandas as pd

    input_value = getattr(args, 'input_path', None) or getattr(args, 'teacher_traces_path', None) or getattr(args, 'real_canonical_path', None)
    frame = _read_table(_require_existing_path(input_value, label='audit input table'))
    text_column = getattr(args, 'text_column', 'raw_output')
    answer_column = getattr(args, 'answer_column', 'answer')
    family_column = getattr(args, 'family_column', 'family')
    policy_column = getattr(args, 'policy_column', 'boxed_policy')
    rows: list[dict[str, Any]] = []
    for record in frame.to_dict(orient='records'):
        raw_output = normalize_optional_text(record.get(text_column))
        answer = (
            normalize_optional_text(record.get(answer_column))
            or normalize_optional_text(record.get('answer_canonical'))
            or normalize_optional_text(record.get('extracted_answer'))
            or ''
        )
        family = normalize_optional_text(record.get(family_column)) or ''
        expected_policy = normalize_optional_text(record.get(policy_column)) or select_v3_format_policy(answer, family)
        assessed = _assess_teacher_trace(raw_output or '', answer, family) if raw_output else {
            'extracted_answer': answer,
            'extraction_source': 'not_found',
            'is_correct': False,
            'format_bucket': 'not_found',
            'format_pass': False,
            'boxed_policy': expected_policy,
            'boxed_count': 0,
            'has_extra_trailing_numbers': False,
            'trace_len_chars': 0,
            'trace_len_tokens_est': 0,
            'strict_pass': False,
            'selection_reason': 'missing_raw_output',
            'final_line_only': False,
            'rejection_reasons': ['missing_raw_output'],
        }
        rows.append(
            {
                'row_id': record.get('trace_id', record.get('pair_id', record.get('id', ''))),
                'family': family,
                'target_style': record.get('target_style', ''),
                'expected_policy': expected_policy,
                'raw_output': raw_output or '',
                'answer': answer,
                'extracted_answer': assessed['extracted_answer'],
                'format_bucket': assessed['format_bucket'],
                'format_pass': assessed['format_pass'],
                'boxed_count': assessed['boxed_count'],
                'has_extra_trailing_numbers': assessed['has_extra_trailing_numbers'],
                'selection_reason': assessed['selection_reason'],
                'rejection_reason': '|'.join(assessed['rejection_reasons']),
                'strict_pass': assessed['strict_pass'],
                'trace_len_chars': assessed['trace_len_chars'],
                'trace_len_tokens_est': assessed['trace_len_tokens_est'],
            }
        )
    audit_df = pd.DataFrame(rows)
    _write_table(Path(args.output_path), audit_df)
    print(json.dumps({'version': 'v3', 'created_at': utc_now(), 'rows': int(len(audit_df)), 'output_path': str(args.output_path)}, ensure_ascii=False, indent=2))


def _load_yaml_config(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    config_path = Path(path)
    if not config_path.exists():
        return {}

    import yaml

    payload = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ValueError(f'Expected YAML mapping in {config_path}, got {type(payload).__name__}')
    return payload


def _replace_last_occurrence(text: str, old: str, new: str) -> str:
    if not old:
        return text
    index = text.rfind(old)
    if index == -1:
        return text
    return text[:index] + new + text[index + len(old) :]


def _require_existing_path(path: str | Path, *, label: str) -> Path:
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f'{label} was not found: {resolved}')
    return resolved


def _parse_bit_examples_from_prompt(prompt: str) -> list[tuple[str, str]]:
    import re

    return re.findall(r'([01]{8})\s*[-–>]+\s*([01]{8})', prompt or '')


def run_build_real_canonical(args: argparse.Namespace) -> None:
    import hashlib
    import pandas as pd

    cfg = _load_yaml_config(args.config_path)
    family_bonus = {
        'bit_manipulation': 0.10,
        'gravity_constant': 0.00,
        'unit_conversion': 0.00,
        'text_decryption': 0.10,
        'roman_numeral': 0.00,
        'symbol_equation': 0.15,
    }
    family_bonus.update(cfg.get('importance_family_bonus', {}))

    family_weight = {
        'bit_manipulation': 1.30,
        'gravity_constant': 0.90,
        'unit_conversion': 0.80,
        'text_decryption': 1.40,
        'roman_numeral': 0.60,
        'symbol_equation': 1.60,
    }
    family_weight.update(cfg.get('train_family_weight', {}))

    hard_score_normalizer = float(cfg.get('hard_score_normalizer', 9.0))
    hard_pool_threshold = float(cfg.get('hard_pool_threshold', 4.0))
    safe_risk_bins = {
        str(value).strip().lower().removeprefix('risk_')
        for value in cfg.get('format_sharpening_safe_bins', ['safe', 'low'])
    }

    splits = pd.read_parquet(_require_existing_path(args.splits_path, label='v1 splits parquet'))
    metadata = pd.read_parquet(_require_existing_path(args.metadata_path, label='v1 metadata parquet'))
    if 'id' in metadata.columns and 'id' in splits.columns and len(metadata) != len(splits):
        raise ValueError(
            'v1 metadata and split row counts differ: '
            f'metadata={len(metadata)}, splits={len(splits)}'
        )
    df = splits.copy()

    def is_missing(value: Any) -> bool:
        return bool(pd.isna(value))

    def is_true(value: Any) -> bool:
        return False if is_missing(value) else bool(value)

    def normalize_risk(value: Any) -> str:
        if is_missing(value):
            return ''
        text = str(value).strip().lower()
        return text.removeprefix('risk_')

    def normalize_answer_canonical(row: pd.Series) -> str:
        family = str(row['family'])
        answer_text = str(row['answer']).strip()

        if family == 'bit_manipulation':
            bits = answer_text[2:] if answer_text.lower().startswith('0b') else answer_text
            return bits.zfill(8)[-8:]

        if family == 'gravity_constant':
            decimals_value = row.get('answer_decimal_style', 2)
            decimals = 2 if is_missing(decimals_value) else int(decimals_value)
            try:
                return format(round(float(answer_text), decimals), f'.{decimals}f')
            except (TypeError, ValueError):
                return answer_text

        if family == 'unit_conversion':
            try:
                return f'{float(answer_text):.2f}'
            except (TypeError, ValueError):
                return answer_text

        if family == 'roman_numeral':
            return answer_text.upper()

        if family == 'text_decryption':
            return ' '.join(answer_text.split())

        return answer_text

    def compute_format_policy(row: pd.Series) -> str:
        answer_text = str(row['answer'])
        if is_true(row.get('boxed_safe')) and '\n' not in answer_text and len(answer_text) < 50:
            return 'boxed_final_line'
        return 'final_answer_colon'

    def build_rule_spec(row: pd.Series) -> str:
        family = str(row['family'])
        spec: dict[str, Any] = {'family': family, 'num_examples': int(row['num_examples'])}
        if family == 'gravity_constant':
            spec['estimated_g'] = None if is_missing(row.get('estimated_g')) else float(row['estimated_g'])
            spec['g_bin'] = None if is_missing(row.get('g_bin')) else float(row['g_bin'])
        elif family == 'unit_conversion':
            spec['estimated_ratio'] = (
                None if is_missing(row.get('estimated_ratio')) else float(row['estimated_ratio'])
            )
            spec['ratio_bin'] = None if is_missing(row.get('ratio_bin')) else str(row['ratio_bin'])
        elif family == 'roman_numeral':
            spec['roman_query_value'] = (
                None if is_missing(row.get('roman_query_value')) else int(float(row['roman_query_value']))
            )
        elif family == 'bit_manipulation':
            spec['bit_query_binary'] = (
                None if is_missing(row.get('bit_query_binary')) else str(row['bit_query_binary'])
            )
            spec['query_hamming_bin'] = (
                None if is_missing(row.get('query_hamming_bin')) else str(row['query_hamming_bin'])
            )
        return json.dumps(spec, ensure_ascii=False, sort_keys=True)

    def build_difficulty_tags(row: pd.Series) -> str:
        tags: list[str] = []
        hard_score = 0.0 if is_missing(row.get('hard_score')) else float(row['hard_score'])
        if hard_score >= 7.0:
            tags.append('very_hard')
        elif hard_score >= 4.0:
            tags.append('hard')
        elif hard_score >= 1.0:
            tags.append('medium')
        else:
            tags.append('easy')

        if is_true(row.get('near_round_boundary')):
            tags.append('near_round_boundary')

        if normalize_risk(row.get('risk_bin')) not in safe_risk_bins | {''}:
            tags.append('risky')

        if is_true(row.get('is_holdout_hard')):
            tags.append('holdout_hard')
        return json.dumps(tags, ensure_ascii=False)

    def build_format_risk_flags(row: pd.Series) -> str:
        return json.dumps(
            {
                'contains_right_brace': is_true(row.get('contains_right_brace')),
                'contains_backslash': is_true(row.get('contains_backslash')),
                'contains_backtick': is_true(row.get('contains_backtick')),
                'boxed_safe': is_true(row.get('boxed_safe')),
            },
            ensure_ascii=False,
            sort_keys=True,
        )

    def compute_generator_ready(row: pd.Series) -> bool:
        if not is_true(row.get('parse_ok')):
            return False

        family = str(row['family'])
        if family == 'roman_numeral':
            return not is_missing(row.get('roman_query_value'))
        if family == 'gravity_constant':
            return not is_missing(row.get('estimated_g'))
        if family == 'unit_conversion':
            return not is_missing(row.get('estimated_ratio'))
        if family == 'bit_manipulation':
            if is_missing(row.get('bit_query_binary')):
                return False
            return identify_bit_op(_parse_bit_examples_from_prompt(str(row.get('prompt', '')))) is not None
        return False

    def compute_eligible_pools(row: pd.Series) -> str:
        pools = ['core']
        if is_true(row.get('generator_ready')):
            pools.append('distill')
        hard_score = 0.0 if is_missing(row.get('hard_score')) else float(row['hard_score'])
        if hard_score >= hard_pool_threshold:
            pools.append('hard')
        if normalize_risk(row.get('risk_bin')) in safe_risk_bins | {''}:
            pools.append('format_sharpening')
        return json.dumps(pools, ensure_ascii=False)

    df['source_kind'] = 'real'
    df['answer_canonical'] = df.apply(normalize_answer_canonical, axis=1)
    df['format_policy'] = df.apply(compute_format_policy, axis=1)
    df['rule_spec_json'] = df.apply(build_rule_spec, axis=1)
    df['rule_spec_hash'] = df['rule_spec_json'].map(lambda value: hashlib.sha256(value.encode()).hexdigest()[:16])
    df['template_signature'] = df['group_signature'].astype(str) + '_' + df['num_examples'].astype(str)
    df['difficulty_tags'] = df.apply(build_difficulty_tags, axis=1)
    df['format_risk_flags'] = df.apply(build_format_risk_flags, axis=1)
    df['generator_ready'] = df.apply(compute_generator_ready, axis=1)
    df['eligible_pools'] = df.apply(compute_eligible_pools, axis=1)

    def raw_importance_prior(row: pd.Series) -> float:
        hard_score = 0.0 if is_missing(row.get('hard_score')) else float(row['hard_score'])
        normalized_hard = hard_score / hard_score_normalizer if hard_score_normalizer > 0 else 0.0
        risk_bonus = 0.0 if normalize_risk(row.get('risk_bin')) in safe_risk_bins | {''} else 0.1
        return (
            normalized_hard * 0.6
            + float(family_bonus.get(str(row['family']), 0.0)) * 0.2
            + risk_bonus * 0.2
        )

    df['importance_prior'] = df.apply(raw_importance_prior, axis=1)
    max_importance = float(df['importance_prior'].max()) if len(df) else 0.0
    if max_importance > 0:
        df['importance_prior'] = df['importance_prior'] / max_importance
    df['importance_prior'] = df['importance_prior'].clip(lower=0.0, upper=1.0)

    def compute_train_sample_weight(row: pd.Series) -> float:
        base = float(family_weight.get(str(row['family']), 1.0))
        return base * (0.5 + 0.5 * float(row['importance_prior']))

    df['train_sample_weight'] = df.apply(compute_train_sample_weight, axis=1)

    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)

    print(f'Wrote {len(df)} rows to {out_path}')
    print('Family counts:')
    for family, count in df['family'].value_counts().items():
        print(f'  {family}: {count}')
    print('generator_ready by family:')
    for family, count in df.loc[df['generator_ready'], 'family'].value_counts().items():
        print(f'  {family}: {count}')


def run_build_solver_registry(args: argparse.Namespace) -> None:
    import pandas as pd

    registry: dict[str, Any] = {
        'version': 'v2',
        'created_at': utc_now(),
        'families': {
            'roman_numeral': {
                'support': 'full',
                'rule_class': 'subtractive_roman',
                'range': '1-100',
                'hard_knobs': [4, 9, 40, 49, 90, 94, 99, 100],
                'generator_ready_condition': 'roman_query_value is not NaN and parse_ok',
                'note': 'Deterministic int->roman conversion',
            },
            'gravity_constant': {
                'support': 'full',
                'rule_class': 'd_equals_half_g_t_squared',
                'formula': '0.5 * g * t^2',
                'generator_ready_condition': 'estimated_g is not NaN and parse_ok',
                'note': 'Distance = 0.5 * g * t^2',
            },
            'unit_conversion': {
                'support': 'full',
                'rule_class': 'fixed_ratio',
                'decimal_style': 2,
                'generator_ready_condition': 'estimated_ratio is not NaN and parse_ok',
                'note': 'output = input * ratio, 2 decimal places',
            },
            'bit_manipulation': {
                'support': 'exact_fit',
                'rule_class': 'programmatic_8bit',
                'ops': ['NOT', 'XOR_FF', 'SHIFT_LEFT_1', 'SHIFT_RIGHT_1', 'ROTATE_LEFT_1', 'ROTATE_RIGHT_1'],
                'generator_ready_condition': 'bit_query_binary uniquely determines op from examples',
                'note': '8-bit programmatic rule where examples identify a single operation',
            },
            'text_decryption': {
                'support': 'conservative',
                'rule_class': 'validator_only',
                'generator_ready_condition': 'False - real-only preferred',
                'note': 'real-only preferred; validator checks decryption correctness',
            },
            'symbol_equation': {
                'support': 'conservative',
                'rule_class': 'validator_only',
                'generator_ready_condition': 'False - real-only preferred',
                'note': 'real-only preferred; validator checks equation solution',
            },
        },
        'family_stats': {},
    }

    canonical_path = _require_existing_path(args.real_canonical_path, label='real canonical parquet')
    df = pd.read_parquet(canonical_path)
    for family in registry['families']:
        family_df = df.loc[df['family'] == family]
        registry['family_stats'][family] = {
            'total': int(len(family_df)),
            'generator_ready': int(family_df['generator_ready'].sum()) if 'generator_ready' in family_df else 0,
        }
    print('generator_ready by family:')
    for family, stats in registry['family_stats'].items():
        print(f'  {family}: {stats["generator_ready"]}/{stats["total"]}')

    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote solver registry to {out_path}')


def int_to_roman(n: int) -> str:
    values = [
        (1000, 'M'),
        (900, 'CM'),
        (500, 'D'),
        (400, 'CD'),
        (100, 'C'),
        (90, 'XC'),
        (50, 'L'),
        (40, 'XL'),
        (10, 'X'),
        (9, 'IX'),
        (5, 'V'),
        (4, 'IV'),
        (1, 'I'),
    ]
    result = ''
    remaining = int(n)
    for value, symbol in values:
        while remaining >= value:
            result += symbol
            remaining -= value
    return result


def validate_roman(s: str) -> bool:
    import re

    return bool(
        re.fullmatch(
            r'M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})',
            (s or '').upper().strip(),
        )
    )


def solve_gravity(g: float, t: float, decimals: int = 2) -> float:
    return round(0.5 * g * (t**2), decimals)


def solve_unit(ratio: float, value: float, decimals: int = 2) -> float:
    return round(ratio * value, decimals)


def identify_bit_op(examples: list[tuple[str, str]]) -> str | None:
    if not examples:
        return None

    operations = {
        'NOT': lambda value: (~value) & 0xFF,
        'SHIFT_LEFT_1': lambda value: (value << 1) & 0xFF,
        'SHIFT_RIGHT_1': lambda value: (value >> 1) & 0xFF,
        'ROTATE_LEFT_1': lambda value: ((value << 1) & 0xFF) | ((value >> 7) & 0x01),
        'ROTATE_RIGHT_1': lambda value: ((value >> 1) & 0x7F) | ((value & 0x01) << 7),
        'IDENTITY': lambda value: value & 0xFF,
    }
    consistent = {name: True for name in operations}

    for input_bits, output_bits in examples:
        try:
            input_value = int(str(input_bits).strip(), 2)
            output_value = int(str(output_bits).strip(), 2)
        except (TypeError, ValueError):
            return None

        for op_name, op in operations.items():
            if consistent[op_name] and op(input_value) != output_value:
                consistent[op_name] = False

    matching = [op_name for op_name, ok in consistent.items() if ok]
    return matching[0] if len(matching) == 1 else None


def apply_bit_op(op: str, inp_str: str) -> str | None:
    try:
        input_value = int(str(inp_str).strip(), 2)
    except (TypeError, ValueError):
        return None

    if op == 'NOT':
        result = (~input_value) & 0xFF
    elif op == 'XOR_FF':
        result = (input_value ^ 0xFF) & 0xFF
    elif op == 'SHIFT_LEFT_1':
        result = (input_value << 1) & 0xFF
    elif op == 'SHIFT_RIGHT_1':
        result = (input_value >> 1) & 0xFF
    elif op == 'ROTATE_LEFT_1':
        result = ((input_value << 1) & 0xFF) | ((input_value >> 7) & 0x01)
    elif op == 'ROTATE_RIGHT_1':
        result = ((input_value >> 1) & 0x7F) | ((input_value & 0x01) << 7)
    elif op == 'IDENTITY':
        result = input_value & 0xFF
    else:
        return None
    return format(result, '08b')


def dedup_hash(family: str, answer: str, prompt: str) -> str:
    import hashlib

    key = f'{family}||{answer.strip()}||{prompt[:200].strip()}'
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:32]


def _build_synth_rows(
    df: Any,
    *,
    seed: int,
    max_per_parent: int,
    families_enabled: dict[str, bool],
    hard_mode: bool = False,
    existing_hashes: set[str] | None = None,
) -> list[dict[str, Any]]:
    import hashlib
    import pandas as pd
    import random

    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    seen_hashes = set(existing_hashes or set())

    def is_missing(value: Any) -> bool:
        return bool(pd.isna(value))

    def is_true(value: Any) -> bool:
        return False if is_missing(value) else bool(value)

    for _, row in df.iterrows():
        if not is_true(row.get('generator_ready')):
            continue

        family = str(row['family'])
        if not families_enabled.get(family, False):
            continue

        parent_id = str(row['id'])
        original_prompt = str(row.get('prompt', ''))
        original_query_raw = '' if is_missing(row.get('query_raw')) else str(row['query_raw'])
        generated: list[dict[str, Any]] = []

        if family == 'roman_numeral':
            if is_missing(row.get('roman_query_value')):
                continue
            original_value = int(float(row['roman_query_value']))
            candidates = [4, 9, 40, 49, 90, 94, 99, 100] if hard_mode else [i for i in range(1, 101) if i != original_value]
            candidates = [candidate for candidate in candidates if candidate != original_value]
            rng.shuffle(candidates)
            for value in candidates:
                if len(generated) >= max_per_parent:
                    break
                answer = int_to_roman(value)
                query_token = original_query_raw or str(original_value)
                prompt = _replace_last_occurrence(original_prompt, query_token, str(value))
                generated.append({'query_value': value, 'answer': answer, 'prompt': prompt})

        elif family == 'gravity_constant':
            if is_missing(row.get('estimated_g')):
                continue
            g_value = float(row['estimated_g'])
            decimals_value = row.get('answer_decimal_style', 2)
            decimals = 2 if is_missing(decimals_value) else int(decimals_value)
            used_answers = {str(row.get('answer_canonical', row.get('answer', '')))}
            if hard_mode:
                time_candidates = [float(rng.randint(1, 20)) + 0.5 for _ in range(max_per_parent * 4)]
            else:
                time_candidates = [round(rng.uniform(1.0, 10.0), 2) for _ in range(max_per_parent * 6)]
            for time_value in time_candidates:
                if len(generated) >= max_per_parent:
                    break
                answer_value = solve_gravity(g_value, time_value, decimals)
                if answer_value <= 0:
                    continue
                answer_text = format(answer_value, f'.{decimals}f')
                if answer_text in used_answers:
                    continue
                used_answers.add(answer_text)
                query_text = f'{time_value:.2f}'
                prompt = _replace_last_occurrence(original_prompt, original_query_raw, query_text)
                generated.append({'query_value': query_text, 'answer': answer_text, 'prompt': prompt})

        elif family == 'unit_conversion':
            if is_missing(row.get('estimated_ratio')):
                continue
            ratio_value = float(row['estimated_ratio'])
            used_answers = {str(row.get('answer_canonical', row.get('answer', '')))}
            if hard_mode:
                value_candidates = [0.01, 0.10, 1000.0, 10000.0] + [
                    rng.uniform(0.001, 0.1) for _ in range(max_per_parent * 4)
                ]
            else:
                value_candidates = [round(rng.uniform(0.1, 100.0), 2) for _ in range(max_per_parent * 6)]
            for source_value in value_candidates:
                if len(generated) >= max_per_parent:
                    break
                answer_value = solve_unit(ratio_value, float(source_value), 2)
                if answer_value <= 0:
                    continue
                answer_text = f'{answer_value:.2f}'
                if answer_text in used_answers:
                    continue
                used_answers.add(answer_text)
                query_text = f'{float(source_value):.2f}'
                prompt = _replace_last_occurrence(original_prompt, original_query_raw, query_text)
                generated.append({'query_value': query_text, 'answer': answer_text, 'prompt': prompt})

        elif family == 'bit_manipulation':
            examples = _parse_bit_examples_from_prompt(original_prompt)
            op = identify_bit_op(examples)
            if op is None:
                continue
            input_values = [0, 1, 2, 127, 128, 254, 255] if hard_mode else [rng.randint(0, 255) for _ in range(max_per_parent * 6)]
            used_prompts = {original_prompt}
            for input_value in input_values:
                if len(generated) >= max_per_parent:
                    break
                input_bits = format(int(input_value), '08b')
                answer_bits = apply_bit_op(op, input_bits)
                if answer_bits is None:
                    continue
                prompt = _replace_last_occurrence(original_prompt, original_query_raw, input_bits)
                if prompt in used_prompts:
                    continue
                used_prompts.add(prompt)
                generated.append({'query_value': input_bits, 'answer': answer_bits, 'prompt': prompt})

        for index, candidate in enumerate(generated):
            answer = str(candidate['answer']).strip()
            prompt = str(candidate['prompt'])
            dedup = dedup_hash(family, answer, prompt)
            rule_ok = True
            format_ok = bool(answer)
            length_ok = len(prompt) < 2000 and len(answer) < 200
            template_ok = True
            exact_ok = dedup not in seen_hashes
            near_ok = True
            accepted = rule_ok and format_ok and length_ok and template_ok and exact_ok and near_ok
            rejected_reason = '' if accepted else 'exact_duplicate'

            if accepted:
                seen_hashes.add(dedup)

            query_value = str(candidate['query_value'])
            rule_spec_json = json.dumps(
                {
                    'family': family,
                    'generator_type': 'sibling',
                    'hard_mode': hard_mode,
                    'parent_id': parent_id,
                    'query_value': query_value,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            rows.append(
                {
                    'id': f'syn_{family[:3]}_{parent_id}_{seed}_{index}',
                    'synthetic_id': f'syn_{family[:3]}_{parent_id}_{seed}_{index}',
                    'parent_real_id': parent_id,
                    'template_family': family,
                    'template_subfamily': str(row.get('subfamily', '')),
                    'prompt': prompt,
                    'answer': answer,
                    'answer_canonical': answer,
                    'answer_type': str(row.get('answer_type', '')),
                    'format_policy': str(row.get('format_policy', 'final_answer_colon')),
                    'generator_type': 'sibling',
                    'generator_version': 'v2',
                    'rule_spec_json': rule_spec_json,
                    'rule_spec_hash': hashlib.sha256(rule_spec_json.encode('utf-8')).hexdigest()[:16],
                    'difficulty_tags': str(row.get('difficulty_tags', '[]')),
                    'format_risk_flags': str(row.get('format_risk_flags', '{}')),
                    'seed': int(seed),
                    'dedup_hash': dedup,
                    'split_policy': 'train',
                    'accepted_by': 'all_gates' if accepted else '',
                    'rejected_reason': rejected_reason,
                    'source_kind': 'synthetic',
                    'rule_consistency_pass': rule_ok,
                    'format_validity_pass': format_ok,
                    'length_validity_pass': length_ok,
                    'template_validity_pass': template_ok,
                    'exact_dedup_pass': exact_ok,
                    'near_dedup_pass': near_ok,
                    'num_examples': int(row.get('num_examples', 0)),
                    'query_raw': query_value,
                    'family': family,
                    'subfamily': str(row.get('subfamily', '')),
                    'importance_prior': float(row.get('importance_prior', 0.5)),
                    'train_sample_weight': float(row.get('train_sample_weight', 1.0)),
                    'generator_ready': True,
                    'eligible_pools': str(row.get('eligible_pools', '["core"]')),
                }
            )

    return rows


def run_build_synth_core(args: argparse.Namespace) -> None:
    import pandas as pd

    cfg = _load_yaml_config(args.config_path)
    df = pd.read_parquet(_require_existing_path(args.real_canonical_path, label='real canonical parquet'))
    families_enabled = cfg.get(
        'families_enabled',
        {
            'roman_numeral': True,
            'gravity_constant': True,
            'unit_conversion': True,
            'bit_manipulation': True,
        },
    )
    seed = int(cfg.get('seed', 42))
    max_per_parent = int(cfg.get('max_per_parent', 3))

    rows = _build_synth_rows(
        df,
        seed=seed,
        max_per_parent=max_per_parent,
        families_enabled=families_enabled,
        hard_mode=False,
    )

    result_df = pd.DataFrame(rows)
    accepted_df = result_df.loc[result_df['accepted_by'] != ''].copy() if not result_df.empty else result_df.copy()

    registry_path = Path(args.registry_path)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_parquet(registry_path, index=False)

    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    accepted_df.to_parquet(out_path, index=False)

    print(f'Synth core: generated {len(result_df)} rows, accepted {len(accepted_df)}')
    if not accepted_df.empty:
        print('Accepted by family:')
        for family, count in accepted_df['family'].value_counts().items():
            print(f'  {family}: {count}')


def run_build_synth_hard(args: argparse.Namespace) -> None:
    import pandas as pd

    cfg = _load_yaml_config(args.config_path)
    df = pd.read_parquet(_require_existing_path(args.real_canonical_path, label='real canonical parquet'))
    families_enabled = cfg.get(
        'families_enabled',
        {
            'roman_numeral': True,
            'gravity_constant': True,
            'unit_conversion': True,
            'bit_manipulation': True,
        },
    )
    seed = int(cfg.get('seed', 43))
    max_per_parent = int(cfg.get('max_per_parent', 2))

    existing_hashes: set[str] = set()
    registry_path = Path(args.registry_path)
    if registry_path.exists():
        existing_registry = pd.read_parquet(registry_path)
        if 'dedup_hash' in existing_registry.columns:
            existing_hashes = set(existing_registry['dedup_hash'].astype(str).tolist())

    rows = _build_synth_rows(
        df,
        seed=seed,
        max_per_parent=max_per_parent,
        families_enabled=families_enabled,
        hard_mode=True,
        existing_hashes=existing_hashes,
    )

    result_df = pd.DataFrame(rows)
    accepted_df = result_df.loc[result_df['accepted_by'] != ''].copy() if not result_df.empty else result_df.copy()

    if registry_path.exists():
        existing_registry = pd.read_parquet(registry_path)
        combined_registry = pd.concat([existing_registry, result_df], ignore_index=True)
    else:
        combined_registry = result_df

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    combined_registry.to_parquet(registry_path, index=False)

    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    accepted_df.to_parquet(out_path, index=False)

    print(f'Synth hard: generated {len(result_df)} rows, accepted {len(accepted_df)}')
    print(f'Total registry rows: {len(combined_registry)}')


def _make_bootstrap_trace(row: dict[str, Any], style: str) -> str:
    family = str(row.get('family', ''))
    answer = str(row.get('answer_canonical', row.get('answer', '')))

    if style == 'answer_only':
        if str(row.get('format_policy', 'final_answer_colon')) == 'boxed_final_line':
            return f'\\boxed{{{answer}}}'
        return f'Final answer: {answer}'

    if style == 'format_safe':
        return f'The answer is: {answer}'

    if family == 'roman_numeral':
        reasoning = f'Converting the number to Roman numeral notation gives {answer}.'
    elif family == 'gravity_constant':
        reasoning = f'Using d = 0.5 * g * t^2 gives {answer}.'
    elif family == 'unit_conversion':
        reasoning = f'Applying the fixed conversion ratio gives {answer}.'
    elif family == 'bit_manipulation':
        reasoning = f'Applying the identified 8-bit rule gives {answer}.'
    elif family == 'text_decryption':
        reasoning = f'Decrypting the text yields {answer}.'
    else:
        reasoning = f'Solving the symbolic rule gives {answer}.'

    return f'Let me work through this step by step.\n\n{reasoning}\n\nFinal answer: {answer}'


def run_build_distill_candidates(args: argparse.Namespace) -> None:
    import pandas as pd

    cfg = _load_yaml_config(args.config_path)
    df = pd.read_parquet(_require_existing_path(args.real_canonical_path, label='real canonical parquet'))
    target_pools = list(cfg.get('target_pools', ['distill']))
    target_styles = list(cfg.get('target_styles', ['short', 'answer_only', 'format_safe']))
    teacher_seed = int(cfg.get('seed', 44))

    def has_target_pool(value: Any) -> bool:
        if value is None:
            return False
        try:
            pools = json.loads(value) if isinstance(value, str) else list(value)
        except (TypeError, json.JSONDecodeError):
            return False
        return any(pool in pools for pool in target_pools)

    eligible = df.loc[df['eligible_pools'].map(has_target_pool)].copy()

    candidates: list[dict[str, Any]] = []
    for _, row in eligible.iterrows():
        row_dict = row.to_dict()
        for style in target_styles:
            candidates.append(
                {
                    'source_id': str(row['id']),
                    'family': str(row['family']),
                    'subfamily': str(row.get('subfamily', '')),
                    'prompt': str(row['prompt']),
                    'answer': str(row.get('answer_canonical', row.get('answer', ''))),
                    'answer_type': str(row.get('answer_type', '')),
                    'format_policy': str(row.get('format_policy', 'final_answer_colon')),
                    'target_style': style,
                    'teacher_name': 'bootstrap',
                    'teacher_seed': teacher_seed,
                    'trace': _make_bootstrap_trace(row_dict, style),
                    'source_kind': 'real',
                }
            )

    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as handle:
        for candidate in candidates:
            handle.write(json.dumps(candidate, ensure_ascii=False) + '\n')

    print(f'Wrote {len(candidates)} distill candidates to {out_path}')


def run_filter_distilled_traces(args: argparse.Namespace) -> None:
    import pandas as pd

    v1_module = _load_v1_module()
    verify = v1_module.verify
    extract_final_answer_with_source = v1_module.extract_final_answer_with_source
    classify_format_bucket = v1_module.classify_format_bucket

    candidates: list[dict[str, Any]] = []
    with _require_existing_path(args.candidate_path, label='distill candidate jsonl').open('r', encoding='utf-8') as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                candidates.append(json.loads(stripped))

    registry_rows: list[dict[str, Any]] = []
    accepted_rows: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
        raw_output = str(candidate.get('trace', ''))
        gold_answer = str(candidate.get('answer', ''))
        extracted_answer, extraction_source = extract_final_answer_with_source(raw_output)
        is_correct = bool(verify(gold_answer, extracted_answer))
        format_bucket = classify_format_bucket(raw_output, extracted_answer, extraction_source)
        format_pass = format_bucket in {'clean_boxed', 'clean_final_answer'}

        registry_row = {
            'trace_id': f'trace_{candidate["source_id"]}_{candidate["target_style"]}_{index}',
            'source_id': candidate['source_id'],
            'source_kind': candidate.get('source_kind', 'real'),
            'family': candidate.get('family', ''),
            'answer_type': candidate.get('answer_type', ''),
            'target_style': candidate.get('target_style', ''),
            'teacher_name': candidate.get('teacher_name', 'bootstrap'),
            'teacher_seed': candidate.get('teacher_seed', 44),
            'raw_output': raw_output,
            'extracted_answer': extracted_answer,
            'is_correct': is_correct,
            'format_bucket': format_bucket,
            'format_pass': format_pass,
            'trace_len_chars': len(raw_output),
            'trace_len_tokens_est': len(raw_output.split()),
            'consensus_rate': 1.0 if is_correct else 0.0,
            'selected_for_training': is_correct and format_pass,
            'selection_reason': (
                'correct_and_format_ok'
                if is_correct and format_pass
                else ('format_fail' if is_correct else 'wrong_answer')
            ),
            'prompt': candidate.get('prompt', ''),
            'answer': gold_answer,
            'format_policy': candidate.get('format_policy', ''),
        }
        registry_rows.append(registry_row)
        if registry_row['selected_for_training']:
            accepted_rows.append(registry_row)

    registry_df = pd.DataFrame(registry_rows)
    accepted_df = pd.DataFrame(accepted_rows)

    registry_path = Path(args.registry_path)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_df.to_parquet(registry_path, index=False)

    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    accepted_df.to_parquet(out_path, index=False)
    audit_path = Path(getattr(args, 'audit_output_path', AUDITS_ROOT / 'preference_pairs_v3.csv'))
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit_rows).to_csv(audit_path, index=False)

    print(f'Filtered {len(generated)} candidates -> {len(accepted_rows)} accepted traces')
    print(f'Written registry: {registry_path}')
    print(f'Written accepted: {out_path}')
    print(f'Written audit: {audit_path}')


def run_build_format_pairs(args: argparse.Namespace) -> None:
    import pandas as pd

    _load_yaml_config(args.config_path)
    df = pd.read_parquet(_require_existing_path(args.real_canonical_path, label='real canonical parquet'))
    teacher_path = resolve_existing_path(args.teacher_traces_path)
    teacher_df = _read_table(teacher_path) if teacher_path.exists() else pd.DataFrame()
    pairs: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []

    def append_pair(*, source_id: str, family: str, prompt: str, answer: str, pair_kind: str, chosen_output: str, rejected_output: str, chosen_bucket: str, rejected_bucket: str) -> None:
        pairs.append(
            {
                'pair_id': f'fmt_{source_id}_{pair_kind}_{len(pairs)}',
                'source_id': source_id,
                'family': family,
                'prompt': prompt,
                'answer': answer,
                'format_policy': select_v3_format_policy(answer, family),
                'chosen_output': chosen_output,
                'rejected_output': rejected_output,
                'chosen_format_bucket': chosen_bucket,
                'rejected_format_bucket': rejected_bucket,
                'pair_kind': pair_kind,
            }
        )
        audit_rows.append(
            {
                'source_id': source_id,
                'family': family,
                'pair_kind': pair_kind,
                'status': 'accepted',
                'chosen_format_bucket': chosen_bucket,
                'rejected_format_bucket': rejected_bucket,
            }
        )

    for record in df.to_dict(orient='records'):
        answer = normalize_optional_text(record.get('answer_canonical')) or normalize_optional_text(record.get('answer')) or ''
        family = str(record.get('family', ''))
        source_id = str(record.get('id', ''))
        prompt = str(record.get('prompt', ''))
        if not prompt or not answer:
            audit_rows.append({'source_id': source_id, 'family': family, 'pair_kind': 'skipped', 'status': 'rejected', 'reason': 'missing_prompt_or_answer'})
            continue
        chosen = render_v3_final_answer(answer, family)
        format_policy = select_v3_format_policy(answer, family)
        append_pair(
            source_id=source_id,
            family=family,
            prompt=prompt,
            answer=answer,
            pair_kind='bare_answer',
            chosen_output=chosen,
            rejected_output=answer,
            chosen_bucket='clean_boxed' if format_policy == 'boxed' else 'clean_final_answer',
            rejected_bucket='last_line_fallback',
        )
        if format_policy == 'boxed':
            append_pair(
                source_id=source_id,
                family=family,
                prompt=prompt,
                answer=answer,
                pair_kind='multiple_boxed',
                chosen_output=chosen,
                rejected_output=f'{chosen}\n{chosen}',
                chosen_bucket='clean_boxed',
                rejected_bucket='boxed_multiple',
            )
        else:
            append_pair(
                source_id=source_id,
                family=family,
                prompt=prompt,
                answer=answer,
                pair_kind='unsafe_boxed',
                chosen_output=chosen,
                rejected_output=rf'\boxed{{{answer}}}',
                chosen_bucket='clean_final_answer',
                rejected_bucket='clean_boxed',
            )

    if not teacher_df.empty:
        strict_rows = teacher_df.loc[teacher_df['selected_for_training'].fillna(False)].copy()
        for record in strict_rows.to_dict(orient='records'):
            source_id = str(record.get('source_id', record.get('trace_id', '')))
            family = str(record.get('family', ''))
            prompt = str(record.get('prompt', ''))
            answer = normalize_optional_text(record.get('answer')) or normalize_optional_text(record.get('extracted_answer')) or ''
            chosen = render_v3_final_answer(answer, family)
            rejected = str(record.get('raw_output', '')).strip()
            if rejected and rejected != chosen:
                append_pair(
                    source_id=source_id,
                    family=family,
                    prompt=prompt,
                    answer=answer,
                    pair_kind='teacher_vs_clean',
                    chosen_output=chosen,
                    rejected_output=rejected,
                    chosen_bucket='clean_boxed' if select_v3_format_policy(answer, family) == 'boxed' else 'clean_final_answer',
                    rejected_bucket=str(record.get('format_bucket', 'not_found')),
                )

    pairs_df = pd.DataFrame(pairs)
    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pairs_df.to_parquet(out_path, index=False)
    audit_path = Path(getattr(args, 'audit_output_path', AUDITS_ROOT / 'rft_accept_pool_v3.csv'))
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit_rows).to_csv(audit_path, index=False)
    print(f'Wrote {len(pairs_df)} strict format pairs to {out_path}')
    print(f'Audit: {audit_path}')


def run_build_correction_pairs(args: argparse.Namespace) -> None:
    import pandas as pd

    v1_module = _load_v1_module()
    df = pd.read_parquet(_require_existing_path(args.real_canonical_path, label='real canonical parquet'))
    teacher_path = resolve_existing_path(args.teacher_traces_path)
    teacher_df = _read_table(teacher_path) if teacher_path.exists() else pd.DataFrame()
    teacher_map = {}
    if not teacher_df.empty:
        teacher_map = {
            str(record.get('source_id')): record
            for record in teacher_df.loc[teacher_df['selected_for_training'].fillna(False)].to_dict(orient='records')
        }

    bootstrap_path = resolve_existing_path(args.bootstrap_pairs_path) if getattr(args, 'bootstrap_pairs_path', None) else None
    bootstrap_df = _read_table(bootstrap_path) if bootstrap_path is not None and bootstrap_path.exists() else pd.DataFrame()
    pairs: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []

    def maybe_accept_pair(
        *,
        source_id: str,
        family: str,
        prompt: str,
        chosen_output: str,
        rejected_output: str,
        error_family_tag: str,
        error_subtype: str,
        source_eval_run: str,
        gold_answer: str,
    ) -> None:
        chosen_assessed = _assess_teacher_trace(chosen_output, gold_answer, family)
        rejected_extracted, _ = v1_module.extract_final_answer_with_source(rejected_output)
        rejected_is_correct = bool(v1_module.verify(gold_answer, rejected_extracted))
        if not chosen_assessed['strict_pass']:
            audit_rows.append(
                {
                    'source_id': source_id,
                    'family': family,
                    'status': 'rejected',
                    'reason': f"chosen_invalid:{'|'.join(chosen_assessed['rejection_reasons'])}",
                }
            )
            return
        if rejected_is_correct:
            audit_rows.append({'source_id': source_id, 'family': family, 'status': 'rejected', 'reason': 'rejected_still_correct'})
            return
        pairs.append(
            {
                'pair_id': f'corr_{source_id}_{len(pairs)}',
                'source_id': source_id,
                'family': family,
                'prompt': prompt,
                'chosen_output': chosen_output,
                'rejected_output': rejected_output,
                'chosen_extracted_answer': chosen_assessed['extracted_answer'],
                'rejected_extracted_answer': rejected_extracted,
                'error_family_tag': error_family_tag,
                'error_subtype': error_subtype,
                'source_eval_run': source_eval_run,
            }
        )
        audit_rows.append({'source_id': source_id, 'family': family, 'status': 'accepted', 'reason': error_subtype})

    if not bootstrap_df.empty:
        for record in bootstrap_df.to_dict(orient='records'):
            source_id = str(record.get('source_id', ''))
            family = str(record.get('family', ''))
            prompt = str(record.get('prompt', ''))
            chosen_answer = normalize_optional_text(record.get('chosen_extracted_answer')) or normalize_optional_text(record.get('answer'))
            if chosen_answer is None:
                matched = df.loc[df['id'].astype(str) == source_id]
                if matched.empty:
                    continue
                chosen_answer = str(matched.iloc[0].get('answer_canonical', matched.iloc[0].get('answer', '')))
            chosen_output = str(teacher_map.get(source_id, {}).get('raw_output') or render_v3_final_answer(chosen_answer, family))
            rejected_output = str(record.get('rejected_output', ''))
            maybe_accept_pair(
                source_id=source_id,
                family=family,
                prompt=prompt,
                chosen_output=chosen_output,
                rejected_output=rejected_output,
                error_family_tag=str(record.get('error_family_tag', family)),
                error_subtype=str(record.get('error_subtype', 'bootstrap_fallback')),
                source_eval_run=str(record.get('source_eval_run', 'bootstrap_fallback')),
                gold_answer=str(chosen_answer),
            )
    else:
        if 'is_holdout_hard' in df.columns:
            hard_df = df.loc[df['is_holdout_hard'].fillna(False) | (df['hard_score'] > 6.0)].copy()
        else:
            hard_df = df.loc[df['hard_score'] > 6.0].copy()
        for _, row in hard_df.iterrows():
            answer = str(row.get('answer_canonical', row.get('answer', '')))
            family = str(row['family'])
            source_id = str(row['id'])
            prompt = str(row.get('prompt', ''))
            wrong_answer = answer
            error_subtype = f'{family}:generic_wrong'
            if family == 'roman_numeral':
                try:
                    value = int(float(row.get('roman_query_value', 1)))
                    wrong_value = value + 1 if value < 100 else value - 1
                    wrong_answer = int_to_roman(wrong_value)
                    error_subtype = 'roman:off_by_one'
                except (TypeError, ValueError):
                    wrong_answer = answer + 'I'
                    error_subtype = 'roman:extra_char'
            elif family == 'gravity_constant':
                try:
                    wrong_answer = f'{float(answer) * 1.1:.2f}'
                except (TypeError, ValueError):
                    wrong_answer = answer + '0'
                error_subtype = 'gravity:rounding_miss'
            elif family == 'unit_conversion':
                try:
                    numeric_answer = float(answer)
                    wrong_answer = '0.00' if numeric_answer == 0 else f'{1.0 / numeric_answer:.2f}'
                except (TypeError, ValueError):
                    wrong_answer = answer + '0'
                error_subtype = 'unit:inverse_ratio'
            elif family == 'bit_manipulation':
                try:
                    wrong_answer = format((int(answer, 2) + 1) & 0xFF, '08b')
                except (TypeError, ValueError):
                    wrong_answer = '00000000'
                error_subtype = 'bit:shift_confusion'
            chosen_output = render_v3_final_answer(answer, family)
            rejected_output = render_v3_final_answer(wrong_answer, family)
            maybe_accept_pair(
                source_id=source_id,
                family=family,
                prompt=prompt,
                chosen_output=chosen_output,
                rejected_output=rejected_output,
                error_family_tag=family,
                error_subtype=error_subtype,
                source_eval_run='deterministic_bootstrap',
                gold_answer=answer,
            )

    pairs_df = pd.DataFrame(pairs)
    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pairs_df.to_parquet(out_path, index=False)
    audit_path = Path(getattr(args, 'audit_output_path', DEFAULT_V3_FORMAT_AUDIT_OUTPUT_PATH))
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit_rows).to_csv(audit_path, index=False)
    print(f'Wrote {len(pairs_df)} strict correction pairs to {out_path}')
    print(f'Audit: {audit_path}')


def run_build_preference_pairs(args: argparse.Namespace) -> None:
    import pandas as pd

    cfg = _load_yaml_config(args.config_path)
    format_df = _read_table(_require_existing_path(args.format_pairs_path, label='format pairs parquet'))
    correction_df = _read_table(_require_existing_path(args.correction_pairs_path, label='correction pairs parquet'))
    teacher_path = resolve_existing_path(args.teacher_traces_path)
    teacher_df = _read_table(teacher_path) if teacher_path.exists() else pd.DataFrame()
    pairs: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []

    for record in format_df.to_dict(orient='records'):
        pairs.append(
            {
                'pair_id': f"pref_format_{record.get('pair_id')}",
                'source_id': record.get('source_id', ''),
                'family': record.get('family', ''),
                'pair_kind': 'format',
                'prompt': record.get('prompt', ''),
                'chosen_output': record.get('chosen_output', ''),
                'rejected_output': record.get('rejected_output', ''),
                'chosen_is_correct': True,
                'rejected_is_correct': False,
                'chosen_format_bucket': record.get('chosen_format_bucket', ''),
                'rejected_format_bucket': record.get('rejected_format_bucket', ''),
                'preference_reason': record.get('pair_kind', 'format'),
            }
        )
    audit_rows.append({'pair_kind': 'format', 'count': len(format_df), 'status': 'accepted'})

    for record in correction_df.to_dict(orient='records'):
        pairs.append(
            {
                'pair_id': f"pref_correction_{record.get('pair_id')}",
                'source_id': record.get('source_id', ''),
                'family': record.get('family', ''),
                'pair_kind': 'correction',
                'prompt': record.get('prompt', ''),
                'chosen_output': record.get('chosen_output', ''),
                'rejected_output': record.get('rejected_output', ''),
                'chosen_is_correct': True,
                'rejected_is_correct': False,
                'chosen_format_bucket': 'clean_boxed' if '\\boxed{' in str(record.get('chosen_output', '')) else 'clean_final_answer',
                'rejected_format_bucket': 'last_line_fallback',
                'preference_reason': record.get('error_subtype', 'correction'),
            }
        )
    audit_rows.append({'pair_kind': 'correction', 'count': len(correction_df), 'status': 'accepted'})

    if not teacher_df.empty:
        brevity_margin = int(cfg.get('brevity_margin_chars', 40))
        strict_df = teacher_df.loc[teacher_df['selected_for_training'].fillna(False)].copy()
        for source_id, group in strict_df.groupby('source_id'):
            ordered = group.sort_values(['trace_len_tokens_est', 'trace_len_chars', 'trace_id']).reset_index(drop=True)
            if len(ordered) >= 2:
                chosen = ordered.iloc[0]
                rejected = ordered.iloc[-1]
                if int(rejected['trace_len_chars']) - int(chosen['trace_len_chars']) >= brevity_margin:
                    pairs.append(
                        {
                            'pair_id': f'pref_brevity_{source_id}',
                            'source_id': source_id,
                            'family': chosen.get('family', ''),
                            'pair_kind': 'brevity',
                            'prompt': chosen.get('prompt', ''),
                            'chosen_output': chosen.get('raw_output', ''),
                            'rejected_output': rejected.get('raw_output', ''),
                            'chosen_is_correct': True,
                            'rejected_is_correct': True,
                            'chosen_format_bucket': chosen.get('format_bucket', ''),
                            'rejected_format_bucket': rejected.get('format_bucket', ''),
                            'preference_reason': 'shorter_strict_pass',
                        }
                    )
                    audit_rows.append({'pair_kind': 'brevity', 'source_id': source_id, 'status': 'accepted', 'reason': 'shorter_strict_pass'})
            incorrect = teacher_df.loc[(teacher_df['source_id'].astype(str) == str(source_id)) & (~teacher_df['is_correct'].fillna(False))].copy()
            if not ordered.empty and not incorrect.empty:
                chosen = ordered.iloc[0]
                rejected = incorrect.sort_values(['trace_len_tokens_est', 'trace_len_chars']).iloc[0]
                pairs.append(
                    {
                        'pair_id': f'pref_consensus_{source_id}',
                        'source_id': source_id,
                        'family': chosen.get('family', ''),
                        'pair_kind': 'consensus',
                        'prompt': chosen.get('prompt', ''),
                        'chosen_output': chosen.get('raw_output', ''),
                        'rejected_output': rejected.get('raw_output', ''),
                        'chosen_is_correct': True,
                        'rejected_is_correct': False,
                        'chosen_format_bucket': chosen.get('format_bucket', ''),
                        'rejected_format_bucket': rejected.get('format_bucket', ''),
                            'preference_reason': 'correct_over_incorrect',
                        }
                    )
                audit_rows.append({'pair_kind': 'consensus', 'source_id': source_id, 'status': 'accepted', 'reason': 'correct_over_incorrect'})

    pairs_df = pd.DataFrame(pairs)
    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pairs_df.to_parquet(out_path, index=False)
    audit_path = Path(getattr(args, 'audit_output_path', AUDITS_ROOT / 'preference_pairs_v3.csv'))
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit_rows).to_csv(audit_path, index=False)
    print(f'Wrote {len(pairs_df)} preference pairs to {out_path}')
    print(f'Audit: {audit_path}')


def run_build_rft_accept_pool(args: argparse.Namespace) -> None:
    import pandas as pd

    cfg = _load_yaml_config(args.config_path)
    teacher_df = _read_table(_require_existing_path(args.teacher_traces_path, label='teacher registry parquet'))
    max_trace_tokens_est = int(cfg.get('max_trace_tokens_est', 96))
    audit_rows: list[dict[str, Any]] = []
    accepted = teacher_df.loc[
        teacher_df['selected_for_rft'].fillna(False)
        | (
            teacher_df['selected_for_training'].fillna(False)
            & (teacher_df['trace_len_tokens_est'].fillna(0) <= max_trace_tokens_est)
        )
    ].copy()
    accepted['accept_id'] = accepted['trace_id'].astype(str).map(lambda value: f'rft_{value}')
    accepted['chosen_output'] = accepted['raw_output']
    accepted_ids = set(accepted['trace_id'].astype(str))
    for record in teacher_df.to_dict(orient='records'):
        trace_id = str(record.get('trace_id', ''))
        accepted_flag = trace_id in accepted_ids
        reason = 'accepted' if accepted_flag else 'not_selected_or_too_long'
        audit_rows.append({'trace_id': trace_id, 'status': 'accepted' if accepted_flag else 'rejected', 'reason': reason})
    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    accepted.to_parquet(out_path, index=False)
    audit_path = Path(getattr(args, 'audit_output_path', AUDITS_ROOT / 'rft_accept_pool_v3.csv'))
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit_rows).to_csv(audit_path, index=False)
    print(f'Wrote {len(accepted)} RFT accept rows to {out_path}')
    print(f'Audit: {audit_path}')


def append_csv_row(path: Path, header: Sequence[str], row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()
    with path.open('a', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(header))
        if not file_exists:
            writer.writeheader()
        writer.writerow({column: row.get(column, '') for column in header})


def detect_final_line_span(text: str) -> tuple[int, int] | None:
    non_empty_lines = [(match.start(), match.end(), match.group(0)) for match in re.finditer(r'[^\n\r]+', text) if match.group(0).strip()]
    if not non_empty_lines:
        return None
    start, end, _ = non_empty_lines[-1]
    return (start, end)


def _prepare_v3_mix_frame(frame: Any, source_dataset: str, *, default_target_style: str) -> Any:
    import pandas as pd

    if frame.empty:
        return frame.copy()
    prepared = frame.copy()
    if 'prompt' not in prepared.columns:
        prepared['prompt'] = ''
    if 'answer' not in prepared.columns:
        if 'answer_canonical' in prepared.columns:
            prepared['answer'] = prepared['answer_canonical']
        elif 'extracted_answer' in prepared.columns:
            prepared['answer'] = prepared['extracted_answer']
        else:
            prepared['answer'] = ''
    if 'source_id' not in prepared.columns:
        if 'id' in prepared.columns:
            prepared['source_id'] = prepared['id']
        elif 'trace_id' in prepared.columns:
            prepared['source_id'] = prepared['trace_id']
        elif 'pair_id' in prepared.columns:
            prepared['source_id'] = prepared['pair_id']
        else:
            prepared['source_id'] = [f'{source_dataset}_{index}' for index in range(len(prepared))]
    if 'id' not in prepared.columns:
        prepared['id'] = prepared['source_id']
    prepared['source_dataset'] = source_dataset
    if 'target_style' not in prepared.columns:
        prepared['target_style'] = default_target_style
    prepared['format_policy'] = prepared.apply(
        lambda row: normalize_optional_text(row.get('format_policy'))
        if normalize_optional_text(row.get('format_policy')) in {'boxed', 'final_answer'}
        else select_v3_format_policy(str(row.get('answer', '')), str(row.get('family', ''))),
        axis=1,
    )
    if 'train_sample_weight' not in prepared.columns:
        prepared['train_sample_weight'] = 1.0
    if 'target_text' not in prepared.columns and 'chosen_output' in prepared.columns:
        prepared['target_text'] = prepared['chosen_output']
    return prepared


def _build_weighted_registry_entry(row: dict[str, Any], *, mix_name: str, weight_cfg: dict[str, Any]) -> dict[str, Any]:
    completion = build_training_completion(row)
    family = str(row.get('family', ''))
    final_span = detect_final_answer_span(completion, family)
    final_line_span = detect_final_line_span(completion)
    selected = final_span is not None and final_line_span is not None
    return {
        'row_id': row.get('row_id', ''),
        'source_id': row.get('source_id', row.get('id', '')),
        'mix_name': mix_name,
        'family': family,
        'target_style': row.get('target_style', 'answer_only'),
        'format_policy': row.get('format_policy', select_v3_format_policy(str(row.get('answer', '')), family)),
        'is_weighted': True,
        'final_span_start_char': final_span[0] if final_span is not None else None,
        'final_span_end_char': final_span[1] if final_span is not None else None,
        'final_line_start_char': final_line_span[0] if final_line_span is not None else None,
        'final_line_end_char': final_line_span[1] if final_line_span is not None else None,
        'weight_profile_name': str(weight_cfg.get('weight_profile_name', 'v3_default')),
        'rationale_weight': float(weight_cfg.get('rationale_weight', 1.0)),
        'final_line_weight': float(weight_cfg.get('final_line_weight', 3.0)),
        'final_span_weight': float(dict(weight_cfg.get('answer_span_weights', {})).get(family, get_answer_span_weight(family))),
        'selected_for_stage': selected,
        'rejection_reason': '' if selected else 'missing_final_span',
    }


def run_build_train_mix_v3(args: argparse.Namespace) -> None:
    import pandas as pd

    cfg_a = _load_yaml_config(args.stage_a_config_path)
    cfg_b = _load_yaml_config(args.stage_b_config_path)
    real_df = _prepare_v3_mix_frame(pd.read_parquet(_require_existing_path(args.real_canonical_path, label='real canonical parquet')), 'real', default_target_style='answer_only')
    core_df = _prepare_v3_mix_frame(pd.read_parquet(resolve_existing_path(args.core_synth_path)), 'core_synth', default_target_style='answer_only') if resolve_existing_path(args.core_synth_path).exists() else pd.DataFrame()
    hard_df = _prepare_v3_mix_frame(pd.read_parquet(resolve_existing_path(args.hard_synth_path)), 'hard_synth', default_target_style='answer_only') if resolve_existing_path(args.hard_synth_path).exists() else pd.DataFrame()
    distill_df = _prepare_v3_mix_frame(pd.read_parquet(resolve_existing_path(args.distilled_traces_path)), 'distill', default_target_style='short') if resolve_existing_path(args.distilled_traces_path).exists() else pd.DataFrame()
    format_df = _prepare_v3_mix_frame(pd.read_parquet(resolve_existing_path(args.format_pairs_path)), 'format', default_target_style='format_safe') if resolve_existing_path(args.format_pairs_path).exists() else pd.DataFrame()
    correction_df = _prepare_v3_mix_frame(pd.read_parquet(resolve_existing_path(args.correction_pairs_path)), 'correction', default_target_style='short') if resolve_existing_path(args.correction_pairs_path).exists() else pd.DataFrame()
    registry_rows: list[dict[str, Any]] = []

    def build_stage_mix(cfg: dict[str, Any]) -> pd.DataFrame:
        sources = {
            'real': real_df,
            'core_synth': core_df,
            'hard_synth': hard_df,
            'distill': distill_df,
            'format': format_df,
            'correction': correction_df,
        }
        stage_name = str(cfg.get('name', f"stage_{cfg.get('stage', 'unknown')}"))
        family_weights = dict(cfg.get('family_weights', {}))
        mixed_frames: list[pd.DataFrame] = []
        seed = int(cfg.get('seed', 0))
        target_total = int(cfg.get('target_total', 1000))
        for offset, (source_name, ratio) in enumerate(dict(cfg.get('mix_ratios', {})).items()):
            source_frame = sources.get(source_name, pd.DataFrame())
            if source_frame.empty:
                continue
            sampled = source_frame.copy()
            sampled['family_weight'] = sampled['family'].map(lambda family: float(family_weights.get(str(family), 1.0)))
            sampled['sampling_weight'] = sampled['train_sample_weight'].astype(float) * sampled['family_weight'].astype(float)
            sampled = _sample_with_weight(sampled, int(round(target_total * float(ratio))), 'sampling_weight', seed + offset)
            sampled['mix_name'] = stage_name
            sampled['stage'] = str(cfg.get('stage', 'unknown'))
            sampled['included_by'] = f'{stage_name}:{source_name}'
            sampled['sample_weight'] = sampled['sampling_weight']
            mixed_frames.append(sampled)
        if not mixed_frames:
            return pd.DataFrame()
        mix_df = pd.concat(mixed_frames, ignore_index=True)
        mix_df['row_id'] = [f"{mix_df.iloc[index].get('source_dataset', 'src')}_{stable_hash(mix_df.iloc[index].get('source_id'), stage_name, index)}" for index in range(len(mix_df))]
        valid_ids: list[str] = []
        for record in mix_df.to_dict(orient='records'):
            registry_row = _build_weighted_registry_entry(record, mix_name=stage_name, weight_cfg=cfg)
            registry_rows.append(registry_row)
            if registry_row['selected_for_stage']:
                valid_ids.append(str(registry_row['row_id']))
        if bool(cfg.get('drop_invalid_weighted_rows', True)):
            mix_df = mix_df.loc[mix_df['row_id'].astype(str).isin(valid_ids)].copy()
        return mix_df.reset_index(drop=True)

    stage_a_df = build_stage_mix(cfg_a)
    stage_b_df = build_stage_mix(cfg_b)
    registry_df = pd.DataFrame(registry_rows)
    _write_table(Path(args.stage_a_output_path), stage_a_df)
    _write_table(Path(args.stage_b_output_path), stage_b_df)
    _write_table(Path(args.registry_path), registry_df)
    print(
        json.dumps(
            {
                'version': 'v3',
                'created_at': utc_now(),
                'stage_a_rows': int(len(stage_a_df)),
                'stage_b_rows': int(len(stage_b_df)),
                'registry_rows': int(len(registry_df)),
                'stage_a_output_path': str(args.stage_a_output_path),
                'stage_b_output_path': str(args.stage_b_output_path),
                'registry_path': str(args.registry_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def _tokenizer_encode(tokenizer: Any, text: str) -> list[int]:
    try:
        return list(tokenizer.encode(text, add_special_tokens=False))
    except TypeError:
        return list(tokenizer.encode(text))


def _char_span_to_token_span(tokenizer: Any, text: str, span: tuple[int, int] | None) -> tuple[int, int] | None:
    if span is None:
        return None
    start_char, end_char = span
    return (len(_tokenizer_encode(tokenizer, text[:start_char])), len(_tokenizer_encode(tokenizer, text[:end_char])))


def _build_completion_token_weights(tokenizer: Any, completion: str, family: str, cfg: dict[str, Any]) -> list[float]:
    tokens = _tokenizer_encode(tokenizer, completion)
    weights = [float(cfg.get('rationale_weight', 1.0))] * len(tokens)
    final_line_span = _char_span_to_token_span(tokenizer, completion, detect_final_line_span(completion))
    final_answer_span = _char_span_to_token_span(tokenizer, completion, detect_final_answer_span(completion, family))
    if final_line_span is not None:
        for index in range(final_line_span[0], min(final_line_span[1], len(weights))):
            weights[index] = max(weights[index], float(cfg.get('final_line_weight', 3.0)))
    final_span_weight = float(dict(cfg.get('answer_span_weights', {})).get(family, get_answer_span_weight(family)))
    if final_answer_span is not None:
        for index in range(final_answer_span[0], min(final_answer_span[1], len(weights))):
            weights[index] = max(weights[index], final_span_weight)
    return weights


def _write_v3_result(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _weighted_training_execute(
    *,
    train_records: list[dict[str, Any]],
    valid_records: list[dict[str, Any]],
    cfg: dict[str, Any],
    base_model: str,
    output_dir: Path,
    adapter_dir: Path,
    metrics_path: Path,
) -> dict[str, Any]:
    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
    import numpy as np
    from mlx_lm import load as mlx_load
    from mlx_lm.tuner import TrainingArgs, train as tuner_train
    from mlx_lm.tuner.datasets import CacheDataset
    from mlx_lm.tuner.utils import linear_to_lora_layers, print_trainable_parameters
    from mlx_lm.utils import save_config

    class MetricsCallback:
        def __init__(self) -> None:
            self.last_train_loss: float | None = None
            self.last_val_loss: float | None = None
            self.peak_memory: float | None = None

        def on_train_loss_report(self, payload: dict[str, Any]) -> None:
            self.last_train_loss = float(payload.get('train_loss')) if payload.get('train_loss') is not None else None
            self.peak_memory = float(payload.get('peak_memory')) if payload.get('peak_memory') is not None else self.peak_memory
            append_jsonl(metrics_path, {'kind': 'train', 'created_at': utc_now(), **payload})

        def on_val_loss_report(self, payload: dict[str, Any]) -> None:
            self.last_val_loss = float(payload.get('val_loss')) if payload.get('val_loss') is not None else None
            append_jsonl(metrics_path, {'kind': 'val', 'created_at': utc_now(), **payload})

    class WeightedDataset:
        def __init__(self, data: list[dict[str, Any]], tokenizer: Any) -> None:
            self._data = data
            self.tokenizer = tokenizer
            self.mask_prompt = bool(cfg.get('mask_prompt', True))

        def __getitem__(self, index: int) -> dict[str, Any]:
            return self._data[index]

        def __len__(self) -> int:
            return len(self._data)

        def process(self, datum: dict[str, Any]) -> tuple[list[int], int, list[float]]:
            prompt = str(datum['prompt'])
            completion = str(datum['completion'])
            messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': completion}]
            tokens = list(self.tokenizer.apply_chat_template(messages, return_dict=False))
            offset = 0
            if self.mask_prompt:
                offset = len(self.tokenizer.apply_chat_template(messages[:-1], add_generation_prompt=True, return_dict=False))
            completion_weights = _build_completion_token_weights(self.tokenizer, completion, str(datum['metadata'].get('family', '')), cfg)
            token_weights = [1.0] * offset + completion_weights
            if len(token_weights) < len(tokens):
                token_weights.extend([completion_weights[-1] if completion_weights else 1.0] * (len(tokens) - len(token_weights)))
            return (tokens, offset, token_weights[: len(tokens)])

    def iterate_weighted_batches(dataset: Any, batch_size: int, max_seq_length: int, loop: bool = False, seed: int | None = None, comm_group: Any = None):
        idx = sorted(range(len(dataset)), key=lambda sample_index: len(dataset[sample_index][0]))
        if len(dataset) < batch_size:
            raise ValueError(f'Dataset must have at least batch_size={batch_size} examples but only has {len(dataset)}.')
        if comm_group is not None:
            offset = comm_group.rank()
            step = comm_group.size()
        else:
            offset = 0
            step = 1
        if batch_size % step != 0:
            raise ValueError('The batch size must be divisible by the number of workers')
        batch_idx = [idx[i + offset : i + offset + batch_size : step] for i in range(0, len(idx) - batch_size + 1, batch_size)]
        if seed is not None:
            np.random.seed(seed)
        while True:
            indices = np.random.permutation(len(batch_idx))
            for batch_index in indices:
                batch = [dataset[item_index] for item_index in batch_idx[batch_index]]
                token_lists, offsets, weight_lists = zip(*batch)
                lengths = [len(tokens) for tokens in token_lists]
                pad_to = 32
                max_length = min(1 + pad_to * ((max(lengths) + pad_to - 1) // pad_to), max_seq_length)
                batch_arr = np.zeros((batch_size // step, max_length), np.int32)
                weight_arr = np.ones((batch_size // step, max_length), np.float32)
                packed_lengths: list[tuple[int, int]] = []
                for row_index in range(batch_size // step):
                    truncated_length = min(lengths[row_index], max_seq_length)
                    batch_arr[row_index, :truncated_length] = token_lists[row_index][:truncated_length]
                    weight_arr[row_index, :truncated_length] = weight_lists[row_index][:truncated_length]
                    packed_lengths.append((int(offsets[row_index]), truncated_length))
                yield mx.array(batch_arr), mx.array(packed_lengths), mx.array(weight_arr)
            if not loop:
                break

    def weighted_loss(model: Any, batch: Any, lengths: Any, token_weights: Any) -> tuple[Any, Any]:
        inputs = batch[:, :-1]
        targets = batch[:, 1:]
        logits = model(inputs)
        steps = mx.arange(1, targets.shape[1] + 1)
        prompt_mask = mx.logical_and(steps >= lengths[:, 0:1], steps <= lengths[:, 1:])
        weights = token_weights[:, 1:] * prompt_mask.astype(token_weights.dtype)
        ntoks = weights.astype(mx.float32).sum()
        ce = nn.losses.cross_entropy(logits, targets) * weights
        denom = mx.maximum(ntoks, mx.array(1.0, dtype=mx.float32))
        ce = ce.astype(mx.float32).sum() / denom
        return ce, ntoks

    callback = MetricsCallback()
    model, tokenizer = mlx_load(base_model)
    model.freeze()
    linear_to_lora_layers(
        model,
        int(cfg.get('num_layers', 16)),
        {
            'rank': int(cfg.get('lora_r', 32)),
            'dropout': float(cfg.get('lora_dropout', 0.0)),
            'scale': float(cfg.get('lora_alpha', 32)),
        },
    )
    print_trainable_parameters(model)
    adapter_dir.mkdir(parents=True, exist_ok=True)
    save_config(
        {
            'base_model_name_or_path': base_model,
            'fine_tune_type': 'lora',
            'num_layers': int(cfg.get('num_layers', 16)),
            'lora_parameters': {'rank': int(cfg.get('lora_r', 32)), 'dropout': float(cfg.get('lora_dropout', 0.0)), 'scale': float(cfg.get('lora_alpha', 32))},
            'target_modules': list(cfg.get('target_modules', [])),
            'weighted_loss': True,
            'rationale_weight': float(cfg.get('rationale_weight', 1.0)),
            'final_line_weight': float(cfg.get('final_line_weight', 3.0)),
            'answer_span_weights': dict(cfg.get('answer_span_weights', {})),
        },
        adapter_dir / 'adapter_config.json',
    )
    learning_rate = float(cfg.get('learning_rate', 1e-4))
    optimizer = optim.Adam(learning_rate=learning_rate)
    training_args = TrainingArgs(
        batch_size=int(cfg.get('per_device_train_batch_size', 1)),
        iters=int(cfg.get('iters', 1)),
        val_batches=int(cfg.get('val_batches', -1)),
        steps_per_report=int(cfg.get('steps_per_report', 1)),
        steps_per_eval=int(cfg.get('steps_per_eval', max(1, int(cfg.get('iters', 1)) // 2))),
        steps_per_save=int(cfg.get('save_every', max(1, int(cfg.get('iters', 1))))),
        adapter_file=str(adapter_dir / 'adapters.safetensors'),
        max_seq_length=int(cfg.get('max_seq_len', 1024)),
        grad_checkpoint=bool(cfg.get('grad_checkpoint', False)),
        grad_accumulation_steps=int(cfg.get('gradient_accumulation_steps', 8)),
    )
    train_set = CacheDataset(WeightedDataset(train_records, tokenizer))
    valid_set = CacheDataset(WeightedDataset(valid_records, tokenizer)) if valid_records else None
    tuner_train(
        model=model,
        optimizer=optimizer,
        train_dataset=train_set,
        val_dataset=valid_set,
        args=training_args,
        loss=weighted_loss,
        iterate_batches=iterate_weighted_batches,
        training_callback=callback,
    )
    result = {
        'status': 'completed',
        'created_at': utc_now(),
        'metrics_path': str(metrics_path),
        'adapter_dir': str(adapter_dir),
        'final_train_loss': callback.last_train_loss,
        'final_val_loss': callback.last_val_loss,
        'peak_memory_gb': callback.peak_memory,
    }
    _write_v3_result(output_dir / f"{output_dir.name}_result.json", result)
    return result


def run_train_sft_v3(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    stage = str(cfg.get('stage', args.stage))
    config_name = str(cfg.get('name', Path(args.config_path).stem))
    out_dir = Path(args.output_dir)
    manifest_path = out_dir / f'sft_{stage}_{config_name}_manifest.json'
    result_path = out_dir / f'sft_{stage}_{config_name}_result.json'
    adapter_dir = out_dir / f'adapter_{stage}_{config_name}'
    candidate_id = getattr(args, 'candidate_id', None) or f'{stage}_{config_name}'
    candidate_registry_path = Path(getattr(args, 'candidate_registry_path', DEFAULT_V3_CANDIDATE_REGISTRY_OUTPUT_PATH))

    def append_candidate_row(*, status: str, failure_reason: str = '') -> None:
        append_csv_row(
            candidate_registry_path,
            [
                'candidate_id',
                'parent_candidate_id',
                'runtime_lane',
                'mac_candidate_id',
                'cuda_run_id',
                'stage',
                'mix_name',
                'train_config',
                'rank',
                'alpha',
                'dropout',
                'weighted_loss',
                'overall_acc',
                'hard_shadow_acc',
                'format_fail_rate',
                'boxed_rate',
                'cuda_repro_pass',
                'packaging_pass',
                'selected_for_submit',
                'status',
                'failure_reason',
                'notes',
                'recorded_at',
            ],
            {
                'candidate_id': candidate_id,
                'parent_candidate_id': '',
                'runtime_lane': 'mac_mlx',
                'mac_candidate_id': candidate_id,
                'cuda_run_id': '',
                'stage': stage,
                'mix_name': normalize_optional_text(cfg.get('mix_name')) or Path(str(cfg.get('train_pack_path', args.train_pack_path))).stem,
                'train_config': config_name,
                'rank': int(cfg.get('lora_r', 32)),
                'alpha': int(cfg.get('lora_alpha', 32)),
                'dropout': float(cfg.get('lora_dropout', 0.0)),
                'weighted_loss': bool(cfg.get('weighted_loss', False)),
                'overall_acc': '',
                'hard_shadow_acc': '',
                'format_fail_rate': '',
                'boxed_rate': '',
                'cuda_repro_pass': False,
                'packaging_pass': False,
                'selected_for_submit': False,
                'status': status,
                'failure_reason': failure_reason,
                'notes': normalize_optional_text(cfg.get('notes')) or '',
                'recorded_at': utc_now(),
            },
        )

    if not args.execute or not bool(cfg.get('weighted_loss', False)):
        try:
            run_train_sft(args)
        except Exception as exc:
            append_candidate_row(status='failed', failure_reason=f'{type(exc).__name__}:{exc}')
            raise
        if not result_path.exists():
            _write_v3_result(
                result_path,
                {'status': 'rendered_only', 'created_at': utc_now(), 'notes': 'Delegated to baseline v2-compatible runtime path.'},
            )
        append_candidate_row(status='completed' if args.execute else 'rendered_only')
        return

    import pandas as pd

    active_model = load_json_file(Path(DEFAULT_ACTIVE_MODEL_PATH), default={})
    base_model = resolve_training_base_model(cfg.get('base_model'), active_model)
    train_pack_path = resolve_existing_path(str(cfg.get('train_pack_path', args.train_pack_path)))
    train_pack_df = pd.read_parquet(train_pack_path)
    seed = int(cfg.get('seed', 0))
    batch_size = int(cfg.get('per_device_train_batch_size', 1))
    num_epochs = float(cfg.get('num_epochs', 2.0))
    train_split_df, valid_split_df, split_strategy = split_training_frame(
        train_pack_df,
        valid_fold=int(args.valid_fold),
        valid_fraction=float(args.valid_fraction),
        seed=seed,
    )
    train_split_df = maybe_limit_rows(train_split_df, max_rows=args.max_train_rows, seed=seed)
    valid_split_df = maybe_limit_rows(valid_split_df, max_rows=args.max_valid_rows, seed=seed)
    train_records, skipped_train_rows = build_training_records(train_split_df)
    valid_records, skipped_valid_rows = build_training_records(valid_split_df)
    effective_train_rows = max(len(train_records), 1)
    cfg['iters'] = max(1, int(effective_train_rows * num_epochs // max(batch_size, 1)))
    cfg['save_every'] = max(1, int(cfg.get('save_every', cfg['iters'])))
    dataset_dir = Path(args.dataset_dir) if args.dataset_dir else DATASETS_ROOT / f'sft_{stage}_{config_name}'
    dataset_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl_records(dataset_dir / 'train.jsonl', train_records)
    write_jsonl_records(dataset_dir / 'valid.jsonl', valid_records)
    write_jsonl_records(dataset_dir / 'test.jsonl', [])
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = out_dir / f'sft_{stage}_{config_name}_metrics.jsonl'
    manifest = {
        'version': 'v3',
        'created_at': utc_now(),
        'candidate_id': candidate_id,
        'stage': stage,
        'config_name': config_name,
        'model': {'base_model': base_model},
        'adapter': {
            'lora_r': int(cfg.get('lora_r', 32)),
            'lora_alpha': int(cfg.get('lora_alpha', 32)),
            'lora_dropout': float(cfg.get('lora_dropout', 0.0)),
            'target_modules': list(cfg.get('target_modules', [])),
        },
        'data': {
            'train_pack_path': str(train_pack_path),
            'dataset_dir': str(dataset_dir),
            'num_rows': len(train_pack_df),
            'train_records': len(train_records),
            'valid_records': len(valid_records),
            'skipped_rows': skipped_train_rows + skipped_valid_rows,
            'split_strategy': split_strategy,
        },
        'training': {
            'learning_rate': float(cfg.get('learning_rate', 1e-4)),
            'num_epochs': num_epochs,
            'max_seq_len': int(cfg.get('max_seq_len', 1024)),
            'per_device_train_batch_size': batch_size,
            'gradient_accumulation_steps': int(cfg.get('gradient_accumulation_steps', 8)),
            'seed': seed,
            'iters': int(cfg['iters']),
        },
        'loss': {
            'weighted': True,
            'rationale_weight': float(cfg.get('rationale_weight', 1.0)),
            'final_line_weight': float(cfg.get('final_line_weight', 3.0)),
            'answer_span_weights': dict(cfg.get('answer_span_weights', {})),
        },
        'execution': {'supports_runtime_execution': True, 'requested_execute': True, 'metrics_path': str(metrics_path), 'adapter_dir': str(adapter_dir)},
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    try:
        if str(cfg.get('runtime_backend', '')).lower() == 'mock':
            adapter_dir.mkdir(parents=True, exist_ok=True)
            (adapter_dir / 'adapters.safetensors').write_bytes(b'mock-adapters')
            _write_v3_result(
                adapter_dir / 'adapter_config.json',
                {
                    'base_model_name_or_path': base_model,
                    'target_modules': list(cfg.get('target_modules', [])),
                    'r': int(cfg.get('lora_r', 32)),
                    'weighted_loss': True,
                },
            )
            result = {
                'status': 'completed',
                'created_at': utc_now(),
                'metrics_path': str(metrics_path),
                'adapter_dir': str(adapter_dir),
                'final_train_loss': 0.0,
                'final_val_loss': 0.0,
                'peak_memory_gb': 0.0,
            }
        else:
            result = _weighted_training_execute(
                train_records=train_records,
                valid_records=valid_records,
                cfg=cfg,
                base_model=base_model,
                output_dir=out_dir,
                adapter_dir=adapter_dir,
                metrics_path=metrics_path,
            )
    except Exception as exc:
        _write_v3_result(result_path, {'status': 'failed', 'created_at': utc_now(), 'error_type': type(exc).__name__, 'error_message': str(exc), 'metrics_path': str(metrics_path), 'adapter_dir': str(adapter_dir)})
        append_candidate_row(status='failed', failure_reason=f'{type(exc).__name__}:{exc}')
        raise
    _write_v3_result(result_path, result)
    append_candidate_row(status=result.get('status', 'completed'))
    print(json.dumps({'manifest_path': str(manifest_path), 'result_path': str(result_path), 'metrics_path': str(metrics_path), 'adapter_dir': str(adapter_dir)}, ensure_ascii=False, indent=2))


def run_ablation_v3(args: argparse.Namespace) -> None:
    header = ['run_id', 'config_name', 'stage', 'weighted_loss', 'train_pack_path', 'train_records', 'valid_records', 'status', 'final_train_loss', 'final_val_loss', 'peak_memory_gb', 'metrics_path', 'manifest_path', 'failure_reason', 'notes', 'recorded_at']
    output_path = Path(args.output_path)
    config_paths = list(getattr(args, 'config_paths', []) or [])
    if config_paths:
        for config_path_value in config_paths:
            config_path = resolve_existing_path(config_path_value)
            cfg = _load_yaml_config(config_path)
            config_name = str(cfg.get('name', Path(config_path).stem))
            stage = str(cfg.get('stage', 'a'))
            output_dir = Path(args.output_root) / config_name
            run_id = args.run_id or stable_hash(config_name, args.train_pack_path, utc_now())
            row = {
                'run_id': run_id,
                'config_name': config_name,
                'stage': stage,
                'weighted_loss': bool(cfg.get('weighted_loss', False)),
                'train_pack_path': args.train_pack_path,
                'train_records': '',
                'valid_records': '',
                'status': 'failed',
                'final_train_loss': '',
                'final_val_loss': '',
                'peak_memory_gb': '',
                'metrics_path': '',
                'manifest_path': '',
                'failure_reason': '',
                'notes': args.notes or '',
                'recorded_at': utc_now(),
            }
            try:
                train_args = argparse.Namespace(
                    stage=stage,
                    config_path=str(config_path),
                    train_pack_path=str(args.train_pack_path),
                    dataset_dir=str(output_dir / 'dataset'),
                    valid_fold=args.valid_fold,
                    valid_fraction=args.valid_fraction,
                    max_train_rows=args.max_train_rows,
                    max_valid_rows=args.max_valid_rows,
                    execute=args.execute,
                    output_dir=str(output_dir),
                    candidate_id=f'ablation_{config_name}',
                    candidate_registry_path=str(getattr(args, 'candidate_registry_path', DEFAULT_V3_CANDIDATE_REGISTRY_OUTPUT_PATH)),
                )
                run_train_sft_v3(train_args)
                manifest_path = output_dir / f'sft_{stage}_{config_name}_manifest.json'
                result_path = output_dir / f'sft_{stage}_{config_name}_result.json'
                manifest = load_json_file(manifest_path, default={})
                result = load_json_file(result_path, default={})
                row.update(
                    {
                        'train_records': manifest.get('data', {}).get('train_records', ''),
                        'valid_records': manifest.get('data', {}).get('valid_records', ''),
                        'status': result.get('status', 'completed'),
                        'final_train_loss': result.get('final_train_loss', ''),
                        'final_val_loss': result.get('final_val_loss', ''),
                        'peak_memory_gb': result.get('peak_memory_gb', ''),
                        'metrics_path': result.get('metrics_path', ''),
                        'manifest_path': str(manifest_path),
                    }
                )
            except Exception as exc:
                row['failure_reason'] = f'{type(exc).__name__}:{exc}'
            append_csv_row(output_path, header, row)
        print(json.dumps({'output_path': str(output_path), 'num_runs': len(config_paths)}, ensure_ascii=False, indent=2))
        return

    manifest = load_json_file(_require_existing_path(args.manifest_path, label='train manifest json'), default={})
    result = load_json_file(resolve_existing_path(args.result_path), default={}) if args.result_path else {}
    row = {
        'run_id': args.run_id or stable_hash(manifest.get('config_name'), manifest.get('data', {}).get('train_pack_path'), utc_now()),
        'config_name': manifest.get('config_name', ''),
        'stage': manifest.get('stage', ''),
        'weighted_loss': manifest.get('loss', {}).get('weighted', ''),
        'train_pack_path': manifest.get('data', {}).get('train_pack_path', ''),
        'train_records': manifest.get('data', {}).get('train_records', ''),
        'valid_records': manifest.get('data', {}).get('valid_records', ''),
        'status': result.get('status', 'rendered_only'),
        'final_train_loss': result.get('final_train_loss', ''),
        'final_val_loss': result.get('final_val_loss', ''),
        'peak_memory_gb': result.get('peak_memory_gb', ''),
        'metrics_path': result.get('metrics_path', manifest.get('execution', {}).get('metrics_path', '')),
        'manifest_path': str(args.manifest_path),
        'failure_reason': result.get('error_message', ''),
        'notes': args.notes or '',
        'recorded_at': utc_now(),
    }
    append_csv_row(output_path, header, row)
    print(json.dumps(row, ensure_ascii=False, indent=2))


def run_render_cuda_repro_spec_v3(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    registry_path = Path(args.registry_path)
    manifest_path: Path | None = None
    candidate_id = args.candidate_id

    if getattr(args, 'train_manifest_path', None):
        manifest_path = _require_existing_path(args.train_manifest_path, label='train manifest json')
    elif candidate_id:
        candidate_registry = _read_table(_require_existing_path(args.candidate_registry_path, label='candidate registry csv'))
        matched = candidate_registry.loc[candidate_registry['candidate_id'].astype(str) == str(candidate_id)].copy()
        if matched.empty:
            append_csv_row(
                registry_path,
                ['candidate_id', 'spec_path', 'status', 'manual_command_path', 'created_at', 'notes'],
                {
                    'candidate_id': candidate_id,
                    'spec_path': str(args.output_path),
                    'status': 'failed',
                    'manual_command_path': '',
                    'created_at': utc_now(),
                    'notes': 'candidate_id_not_found',
                },
            )
            raise ValueError(f'candidate_id not found in registry: {candidate_id}')
        for candidate_manifest in sorted(TRAIN_OUTPUT_ROOT.rglob('sft_*_manifest.json')):
            payload = load_json_file(candidate_manifest, default={})
            if str(payload.get('candidate_id', '')) == str(candidate_id):
                manifest_path = candidate_manifest
                break
        if manifest_path is None:
            append_csv_row(
                registry_path,
                ['candidate_id', 'spec_path', 'status', 'manual_command_path', 'created_at', 'notes'],
                {
                    'candidate_id': candidate_id,
                    'spec_path': str(args.output_path),
                    'status': 'failed',
                    'manual_command_path': '',
                    'created_at': utc_now(),
                    'notes': 'candidate_manifest_not_found',
                },
            )
            raise FileNotFoundError(f'candidate manifest not found for candidate_id={candidate_id}')
    else:
        raise ValueError('Either --train-manifest-path or --candidate-id must be provided.')

    manifest = load_json_file(manifest_path, default={})
    candidate_id = candidate_id or manifest.get('candidate_id') or f"{manifest.get('stage', 'stage')}_{manifest.get('config_name', 'config')}_{stable_hash(manifest_path, manifest.get('created_at'))}"
    train_pack_path = _require_existing_path(manifest.get('data', {}).get('train_pack_path', cfg.get('train_pack_path', '')), label='train pack parquet')
    spec = {
        'version': 'v3',
        'created_at': utc_now(),
        'candidate_id': candidate_id,
        'manual_cuda_execution_required': True,
        'base_model_name_or_path': str(cfg.get('base_model_name_or_path', DEFAULT_SUBMISSION_BASE_MODEL)),
        'mac_manifest_path': str(manifest_path),
        'stage': manifest.get('stage', ''),
        'config_name': manifest.get('config_name', ''),
        'train_pack_path': str(train_pack_path),
        'train_pack_sha256': hashlib.sha256(train_pack_path.read_bytes()).hexdigest(),
        'train_rows': manifest.get('data', {}).get('train_records', 0),
        'valid_rows': manifest.get('data', {}).get('valid_records', 0),
        'style_ratio': manifest.get('data', {}).get('style_distribution', {}),
        'lora': {
            'r': cfg.get('lora_r', manifest.get('adapter', {}).get('lora_r', 32)),
            'alpha': cfg.get('lora_alpha', manifest.get('adapter', {}).get('lora_alpha', 32)),
            'dropout': cfg.get('lora_dropout', manifest.get('adapter', {}).get('lora_dropout', 0.0)),
            'target_modules': list(cfg.get('target_modules', manifest.get('adapter', {}).get('target_modules', []))),
        },
        'training': {
            'precision': cfg.get('precision', 'bf16'),
            'learning_rate': cfg.get('learning_rate', manifest.get('training', {}).get('learning_rate', 1e-4)),
            'num_epochs': cfg.get('num_epochs', manifest.get('training', {}).get('num_epochs', 2.0)),
            'max_seq_len': cfg.get('max_seq_len', manifest.get('training', {}).get('max_seq_len', 1024)),
            'per_device_train_batch_size': cfg.get('per_device_train_batch_size', manifest.get('training', {}).get('per_device_train_batch_size', 1)),
            'gradient_accumulation_steps': cfg.get('gradient_accumulation_steps', manifest.get('training', {}).get('gradient_accumulation_steps', 8)),
        },
        'loss': manifest.get('loss', {}),
        'cuda_output_dir_hint': args.cuda_output_dir,
    }
    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding='utf-8')
    command_path = out_path.with_suffix('.sh')
    command_path.write_text(
        '# Manual CUDA/BF16 reproduction\\n'
        f'# Source manifest: {manifest_path}\\n'
        f'# Rendered spec: {out_path}\\n'
        f'# Suggested output dir: {args.cuda_output_dir}\\n',
        encoding='utf-8',
    )
    append_csv_row(
        registry_path,
        ['candidate_id', 'spec_path', 'status', 'manual_command_path', 'created_at', 'notes'],
        {
            'candidate_id': candidate_id,
            'spec_path': str(out_path),
            'status': 'pending_manual_cuda',
            'manual_command_path': str(command_path),
            'created_at': utc_now(),
            'notes': args.notes or '',
        },
    )
    print(json.dumps({'candidate_id': candidate_id, 'output_path': str(out_path), 'command_path': str(command_path)}, ensure_ascii=False, indent=2))


def run_write_runbook_v3(args: argparse.Namespace) -> None:
    candidate_registry_path = Path(args.candidate_registry_path)
    if not candidate_registry_path.exists():
        candidate_registry_path.parent.mkdir(parents=True, exist_ok=True)
        candidate_registry_path.write_text(
            ','.join(
                [
                    'candidate_id',
                    'parent_candidate_id',
                    'runtime_lane',
                    'mac_candidate_id',
                    'cuda_run_id',
                    'stage',
                    'mix_name',
                    'train_config',
                    'rank',
                    'alpha',
                    'dropout',
                    'weighted_loss',
                    'overall_acc',
                    'hard_shadow_acc',
                    'format_fail_rate',
                    'boxed_rate',
                    'cuda_repro_pass',
                    'packaging_pass',
                    'selected_for_submit',
                    'status',
                    'failure_reason',
                    'notes',
                    'recorded_at',
                ]
            )
            + '\n',
            encoding='utf-8',
        )
    promotion_rules_path = Path(args.promotion_rules_path)
    promotion_rules_path.parent.mkdir(parents=True, exist_ok=True)
    promotion_rules_path.write_text(
        '# V3 Promotion / Submit Queue Rules\n'
        '- local best update -> queue\n'
        '- hard split / hard family improvement -> queue\n'
        '- format fail reduction -> queue\n'
        '- all failures and rejections must be logged in weighted_ablation_v3.csv, cuda_reproduction_registry_v3.csv, or candidate_registry_v3.csv\n'
        '- selected_for_submit requires cuda_repro_pass and packaging_pass\n',
        encoding='utf-8',
    )
    runbook_path = Path(args.output_path)
    runbook_path.parent.mkdir(parents=True, exist_ok=True)
    runbook_path.write_text(
        f'# V3 Training Command Book\n# Generated at {utc_now()}\n\n'
        'uv run python versions/v3/code/train.py bootstrap-v3\n'
        'uv run python versions/v3/code/train.py build-teacher-trace-candidates\n'
        'uv run python versions/v3/code/train.py generate-teacher-traces\n'
        'uv run python versions/v3/code/train.py filter-teacher-traces\n'
        'uv run python versions/v3/code/train.py build-format-pairs\n'
        'uv run python versions/v3/code/train.py build-correction-pairs\n'
        'uv run python versions/v3/code/train.py build-preference-pairs\n'
        'uv run python versions/v3/code/train.py build-rft-accept-pool\n'
        'uv run python versions/v3/code/train.py build-train-mix\n'
        'uv run python versions/v3/code/train.py train-sft --stage a --config-path versions/v3/conf/train/sft_stage_a_weighted_mlx.yaml --execute\n'
        'uv run python versions/v3/code/train.py run-ablation --config-path versions/v3/conf/train/sft_stage_a_weighted_mlx.yaml --train-pack-path versions/v3/data/train_packs/stage_a_strong_v3.parquet\n'
        'uv run python versions/v3/code/train.py render-cuda-repro-spec --candidate-id YOUR_CANDIDATE --candidate-registry-path versions/v3/data/processed/candidate_registry_v3.csv --config-path versions/v3/conf/train/sft_stage_a_cuda_bf16.yaml\n'
        'uv run python versions/v3/code/train.py package-peft --adapter-dir /kaggle/working/YOUR_CANDIDATE/adapter --config-path versions/v3/conf/package/cuda_submission_smoke.yaml\n',
        encoding='utf-8',
    )
    print(json.dumps({'candidate_registry_path': str(candidate_registry_path), 'promotion_rules_path': str(promotion_rules_path), 'runbook_path': str(runbook_path)}, ensure_ascii=False, indent=2))


def _sample_with_weight(df: Any, n: int, weight_col: str, seed: int) -> Any:
    import numpy as np

    if len(df) == 0:
        return df.copy()

    weights = df[weight_col].fillna(1.0).astype(float).to_numpy() if weight_col in df.columns else np.ones(len(df))
    weights = np.maximum(weights, 1e-6)
    weight_sum = float(weights.sum())
    if weight_sum <= 0:
        weights = np.ones(len(df)) / len(df)
    else:
        weights = weights / weight_sum
    sample_size = min(int(n), len(df))
    indices = np.random.RandomState(seed).choice(len(df), size=sample_size, replace=False, p=weights)
    return df.iloc[indices].copy()


def run_build_train_mix(args: argparse.Namespace) -> None:
    import pandas as pd

    cfg_a = _load_yaml_config(args.stage_a_config_path)
    cfg_b = _load_yaml_config(args.stage_b_config_path)

    real_df = pd.read_parquet(_require_existing_path(args.real_canonical_path, label='real canonical parquet')).copy()
    real_df['source_dataset'] = 'real'
    real_df['target_style'] = 'short'

    synthetic_registry_path = Path(args.synthetic_registry_path)
    if synthetic_registry_path.exists():
        synth_df = pd.read_parquet(synthetic_registry_path)
        if 'accepted_by' in synth_df.columns:
            synth_df = synth_df.loc[synth_df['accepted_by'] != ''].copy()
        core_df = synth_df.loc[synth_df.get('seed', pd.Series([], dtype='int64')) == 42].copy() if 'seed' in synth_df.columns else synth_df.copy()
        hard_df = synth_df.loc[synth_df.get('seed', pd.Series([], dtype='int64')) == 43].copy() if 'seed' in synth_df.columns else pd.DataFrame()
    else:
        core_df = pd.DataFrame()
        hard_df = pd.DataFrame()

    distill_path = DEFAULT_DISTILLED_TRACES_OUTPUT_PATH
    distill_df = pd.read_parquet(distill_path).copy() if distill_path.exists() else pd.DataFrame()
    if not distill_df.empty:
        distill_df['source_dataset'] = 'distill'

    synth_format_path = DEFAULT_SYNTH_FORMAT_OUTPUT_PATH
    synth_format_df = pd.read_parquet(synth_format_path).copy() if synth_format_path.exists() else pd.DataFrame()
    if not synth_format_df.empty:
        synth_format_df['source_dataset'] = 'format_synth'

    correction_path = DEFAULT_CORRECTION_PAIRS_OUTPUT_PATH
    correction_df = pd.read_parquet(correction_path).copy() if correction_path.exists() else pd.DataFrame()
    if not correction_df.empty:
        correction_df['source_dataset'] = 'correction'

    def ensure_columns(frame: pd.DataFrame, source_name: str) -> pd.DataFrame:
        if frame.empty:
            return frame.copy()
        prepared = frame.copy()
        if 'prompt' not in prepared.columns:
            prepared['prompt'] = ''
        if 'answer' not in prepared.columns:
            if 'extracted_answer' in prepared.columns:
                prepared['answer'] = prepared['extracted_answer']
            elif 'chosen' in prepared.columns:
                prepared['answer'] = prepared['chosen']
            elif 'chosen_output' in prepared.columns:
                prepared['answer'] = prepared['chosen_output']
            else:
                prepared['answer'] = ''
        if 'id' not in prepared.columns:
            if 'synthetic_id' in prepared.columns:
                prepared['id'] = prepared['synthetic_id']
            elif 'trace_id' in prepared.columns:
                prepared['id'] = prepared['trace_id']
            elif 'pair_id' in prepared.columns:
                prepared['id'] = prepared['pair_id']
            else:
                prepared['id'] = [f'{source_name}_{index}' for index in range(len(prepared))]
        if 'target_style' not in prepared.columns:
            prepared['target_style'] = 'short'
        if 'format_policy' not in prepared.columns:
            prepared['format_policy'] = 'final_answer_colon'
        if 'answer_type' not in prepared.columns:
            prepared['answer_type'] = ''
        if 'family' not in prepared.columns:
            prepared['family'] = ''
        return prepared

    sources = {
        'real': ensure_columns(real_df, 'real'),
        'core_synth': ensure_columns(core_df, 'core_synth'),
        'hard_synth': ensure_columns(hard_df, 'hard_synth'),
        'distill': ensure_columns(distill_df, 'distill'),
        'format_synth': ensure_columns(synth_format_df, 'format_synth'),
        'correction': ensure_columns(correction_df, 'correction'),
    }

    def build_stage_mix(cfg: dict[str, Any], *, seed_offset: int) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
        mix_name = str(cfg.get('name', f'stage_{cfg.get("stage", "unknown")}'))
        stage = str(cfg.get('stage', 'unknown'))
        target_total = int(cfg.get('target_total', 10000))
        ratios = {str(key): float(value) for key, value in cfg.get('mix_ratios', {}).items()}
        family_weights = {str(key): float(value) for key, value in cfg.get('family_weights', {}).items()}
        seed = int(cfg.get('seed', 46)) + seed_offset

        mix_parts: list[pd.DataFrame] = []
        registry_parts: list[dict[str, Any]] = []
        for source_name, ratio in ratios.items():
            target_n = int(target_total * ratio)
            source_frame = sources.get(source_name, pd.DataFrame()).copy()
            if source_frame.empty:
                registry_parts.append(
                    {
                        'mix_name': mix_name,
                        'stage': stage,
                        'source_dataset': source_name,
                        'target_n': target_n,
                        'actual_n': 0,
                        'ratio': ratio,
                    }
                )
                continue

            source_frame['_family_weight'] = source_frame['family'].map(lambda family: family_weights.get(str(family), 1.0))
            sampled = _sample_with_weight(source_frame, target_n, '_family_weight', seed)
            sampled['source_dataset'] = source_name
            sampled['mix_name'] = mix_name
            sampled['stage'] = stage
            sampled['included_by'] = source_name
            sampled['family_weight'] = sampled['_family_weight']
            sampled['sample_weight'] = sampled['_family_weight']
            if 'train_sample_weight' in sampled.columns:
                sampled['sample_weight'] = sampled['sample_weight'] * sampled['train_sample_weight'].fillna(1.0)
            sampled['row_id'] = [f'{mix_name}_{source_name}_{index}' for index in range(len(sampled))]
            sampled = sampled.drop(columns=['_family_weight'])
            mix_parts.append(sampled)
            registry_parts.append(
                {
                    'mix_name': mix_name,
                    'stage': stage,
                    'source_dataset': source_name,
                    'target_n': target_n,
                    'actual_n': len(sampled),
                    'ratio': ratio,
                }
            )

        mix_df = pd.concat(mix_parts, ignore_index=True) if mix_parts else pd.DataFrame()
        return mix_df, registry_parts

    stage_a_mix, stage_a_registry = build_stage_mix(cfg_a, seed_offset=0)
    stage_b_mix, stage_b_registry = build_stage_mix(cfg_b, seed_offset=1)
    stage_b_hard_only = (
        stage_b_mix.loc[stage_b_mix['source_dataset'].isin(['hard_synth', 'correction'])].copy()
        if not stage_b_mix.empty and 'source_dataset' in stage_b_mix.columns
        else pd.DataFrame()
    )

    for output_path, frame in (
        (Path(args.stage_a_output_path), stage_a_mix),
        (Path(args.stage_b_output_path), stage_b_mix),
        (Path(args.hard_only_output_path), stage_b_hard_only),
    ):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(output_path, index=False)

    registry_df = pd.DataFrame(stage_a_registry + stage_b_registry)
    registry_path = Path(args.registry_path)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_df.to_parquet(registry_path, index=False)

    print(f'Stage A mix: {len(stage_a_mix)} rows -> {args.stage_a_output_path}')
    print(f'Stage B mix: {len(stage_b_mix)} rows -> {args.stage_b_output_path}')
    print(f'Stage B hard only: {len(stage_b_hard_only)} rows -> {args.hard_only_output_path}')

    for cfg, mix_df, stage_label in ((cfg_a, stage_a_mix, 'A'), (cfg_b, stage_b_mix, 'B')):
        ratios = {str(key): float(value) for key, value in cfg.get('mix_ratios', {}).items()}
        target_total = int(cfg.get('target_total', 10000))
        if mix_df.empty:
            continue
        for source_name, ratio in ratios.items():
            expected = int(target_total * ratio)
            actual = int((mix_df['source_dataset'] == source_name).sum()) if 'source_dataset' in mix_df.columns else 0
            pct_diff = abs(actual - expected) / max(expected, 1)
            status = 'OK' if pct_diff < 0.05 else f'WARN(off by {pct_diff:.1%})'
            print(f'  Stage {stage_label} {source_name}: expected {expected}, got {actual} [{status}]')


def detect_final_answer_span(text: str, family: str) -> tuple[int, int] | None:
    import re

    del family
    boxed_matches = list(re.finditer(r'\\boxed\{([^}]*)\}', text))
    if boxed_matches:
        return boxed_matches[-1].span(1)

    final_answer_matches = list(re.finditer(r'(?:The\s+)?Final answer(?: is)?\s*[:：]?\s*(.+?)(?:\n|$)', text, re.IGNORECASE))
    if final_answer_matches:
        return final_answer_matches[-1].span(1)
    return None


def get_answer_span_weight(family: str) -> float:
    weights = {
        'gravity_constant': 4.0,
        'unit_conversion': 4.0,
        'roman_numeral': 4.0,
        'bit_manipulation': 5.0,
        'symbol_equation': 6.0,
        'text_decryption': 3.0,
    }
    return float(weights.get(family, 3.0))


def compute_loss_weights(text: str, family: str, *, weighted: bool) -> list[float]:
    import re

    tokens = list(re.finditer(r'\S+', text))
    if not weighted:
        return [1.0] * len(tokens)

    weights = [1.0] * len(tokens)
    span = detect_final_answer_span(text, family)
    if span is None:
        return weights

    start_char, end_char = span
    answer_weight = get_answer_span_weight(family)
    for index, match in enumerate(tokens):
        if match.end() > start_char and match.start() < end_char:
            weights[index] = answer_weight
    return weights


def normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if value != value:
        return None
    text = value if isinstance(value, str) else str(value)
    normalized = text.strip()
    if not normalized or normalized.lower() == 'nan':
        return None
    return normalized


KNOWN_GENERATION_WARNING_PREFIXES = (
    'Calling `python -m mlx_lm.generate...` directly is deprecated. Use `mlx_lm.generate...` or `python -m mlx_lm generate ...` instead.',
)


def strip_known_generation_warnings(text: str) -> str:
    cleaned = text.strip()
    changed = True
    while changed and cleaned:
        changed = False
        for prefix in KNOWN_GENERATION_WARNING_PREFIXES:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].lstrip()
                changed = True
    return cleaned


def estimate_trace_tokens(text: str) -> int:
    return len(re.findall(r'\S+', text))


def build_training_prompt(raw_prompt: str) -> str:
    boxed_instruction = r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
    return f'{raw_prompt}\n{boxed_instruction}'


def render_answer_completion(answer: str, format_policy: str) -> str:
    answer_text = answer.strip()
    if not answer_text:
        raise ValueError('answer text must not be empty')
    if format_policy == 'boxed':
        return rf'\boxed{{{answer_text}}}'
    if format_policy == 'final_answer':
        return f'Final answer: {answer_text}'
    return answer_text


def build_training_completion(row: dict[str, Any]) -> str:
    for key in ('chosen_output', 'raw_output', 'completion', 'target_text'):
        value = normalize_optional_text(row.get(key))
        if value is not None:
            cleaned = normalize_optional_text(strip_known_generation_warnings(value))
            if cleaned is not None:
                return cleaned
    answer = (
        normalize_optional_text(row.get('answer_canonical'))
        or normalize_optional_text(row.get('answer'))
        or normalize_optional_text(row.get('extracted_answer'))
    )
    if answer is None:
        raise ValueError('row does not contain a usable answer field')
    format_policy = normalize_optional_text(row.get('format_policy')) or 'boxed'
    return render_answer_completion(answer, format_policy)


def build_training_records(frame: Any) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    skipped = 0
    for row in frame.to_dict(orient='records'):
        prompt = normalize_optional_text(row.get('prompt'))
        if prompt is None:
            skipped += 1
            continue
        try:
            completion = build_training_completion(row)
        except ValueError:
            skipped += 1
            continue
        records.append(
            {
                'prompt': build_training_prompt(prompt),
                'completion': completion,
                'metadata': {
                    'id': normalize_optional_text(row.get('id')),
                    'family': normalize_optional_text(row.get('family')),
                    'source_dataset': normalize_optional_text(row.get('source_dataset'))
                    or normalize_optional_text(row.get('source_kind'))
                    or 'unknown',
                },
            }
        )
    return records, skipped


def split_training_frame(frame: Any, *, valid_fold: int, valid_fraction: float, seed: int) -> tuple[Any, Any, str]:
    import pandas as pd

    if frame.empty:
        return frame.copy(), frame.copy(), 'empty'

    if 'cv5_fold' in frame.columns and frame['cv5_fold'].notna().any():
        folds = pd.to_numeric(frame['cv5_fold'], errors='coerce')
        valid_mask = folds == float(valid_fold)
        train_df = frame.loc[~valid_mask].copy()
        valid_df = frame.loc[valid_mask].copy()
        if not train_df.empty and not valid_df.empty:
            return train_df, valid_df, f'cv5_fold={valid_fold}'

    shuffled = frame.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    if len(shuffled) <= 1:
        return shuffled.copy(), shuffled.iloc[0:0].copy(), 'single_row'

    valid_size = max(1, int(round(len(shuffled) * valid_fraction)))
    valid_size = min(valid_size, len(shuffled) - 1)
    valid_df = shuffled.iloc[:valid_size].copy()
    train_df = shuffled.iloc[valid_size:].copy()
    return train_df, valid_df, f'random_fraction={valid_fraction}'


def maybe_limit_rows(frame: Any, *, max_rows: int | None, seed: int) -> Any:
    if max_rows is None or len(frame) <= max_rows:
        return frame
    return frame.sample(n=max_rows, random_state=seed).reset_index(drop=True)


def write_jsonl_records(path: Path, records: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        if path.exists():
            path.unlink()
        return
    with path.open('w', encoding='utf-8') as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + '\n')


def resolve_existing_path(path_value: str | Path) -> Path:
    candidate = Path(path_value)
    if candidate.exists():
        return candidate
    repo_relative = REPO_ROOT / candidate
    if repo_relative.exists():
        return repo_relative
    version_relative = VERSION_ROOT / candidate
    if version_relative.exists():
        return version_relative
    return candidate


def has_complete_mlx_snapshot(model_dir: Path) -> bool:
    if not model_dir.exists() or not model_dir.is_dir():
        return False
    if any(model_dir.glob('model-*.safetensors')):
        return True
    single_file = model_dir / 'model.safetensors'
    if single_file.exists():
        return True
    index_path = model_dir / 'model.safetensors.index.json'
    if not index_path.exists():
        return False
    try:
        payload = json.loads(index_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return False
    weight_map = payload.get('weight_map')
    if not isinstance(weight_map, dict) or not weight_map:
        return False
    shard_names = {str(value) for value in weight_map.values() if value}
    return bool(shard_names) and all((model_dir / shard_name).exists() for shard_name in shard_names)


def huggingface_snapshot_root_for_repo(repo_id: str) -> Path:
    safe_repo = repo_id.replace('/', '--')
    return Path.home() / '.cache' / 'huggingface' / 'hub' / f'models--{safe_repo}' / 'snapshots'


def resolve_preferred_mlx_model_path_v4() -> str | None:
    candidate_paths = [DEFAULT_LOCAL_MODEL_PATH, default_lms_model_path(DEFAULT_MODEL_REPO_ID)]
    snapshot_root = huggingface_snapshot_root_for_repo(DEFAULT_MODEL_REPO_ID)
    if snapshot_root.exists():
        candidate_paths.extend(sorted(path for path in snapshot_root.iterdir() if path.is_dir()))
    active_model = load_active_model_manifest_v4()
    active_snapshot = normalize_optional_text(active_model.get('snapshot_dir'))
    active_repo_id = normalize_optional_text(active_model.get('repo_id'))
    if active_snapshot and active_repo_id == DEFAULT_MODEL_REPO_ID:
        candidate_paths.append(resolve_existing_path(active_snapshot))
    for candidate in candidate_paths:
        if has_complete_mlx_snapshot(candidate):
            return str(candidate.resolve())
    return None


def resolve_fallback_mlx_model_path_v4(active_snapshot: str | None = None) -> str | None:
    candidate_paths = [LEGACY_LOCAL_MODEL_PATH, default_lms_model_path(LEGACY_MODEL_REPO_ID)]
    if active_snapshot:
        candidate_paths.insert(0, resolve_existing_path(active_snapshot))
    for candidate in candidate_paths:
        if has_complete_mlx_snapshot(candidate):
            return str(candidate.resolve())
    return None


def is_default_mlx_model_request(requested: str | None, active_repo_id: str | None) -> bool:
    return requested in {
        None,
        DEFAULT_MODEL_REPO_ID,
        LEGACY_MODEL_REPO_ID,
        active_repo_id,
        DEFAULT_LOCAL_MODEL_NAME,
        LEGACY_LOCAL_MODEL_NAME,
        'model',
        str(DEFAULT_LOCAL_MODEL_PATH),
    }


def resolve_training_base_model(base_model_value: Any, active_model: dict[str, Any]) -> str:
    requested = normalize_optional_text(base_model_value)
    active_snapshot = normalize_optional_text(active_model.get('snapshot_dir'))
    active_repo_id = normalize_optional_text(active_model.get('repo_id'))
    preferred_local_model = resolve_preferred_mlx_model_path_v4()
    fallback_model = resolve_fallback_mlx_model_path_v4(active_snapshot)
    if preferred_local_model and is_default_mlx_model_request(requested, active_repo_id):
        return preferred_local_model
    if fallback_model and is_default_mlx_model_request(requested, active_repo_id):
        return fallback_model
    if requested is None:
        return preferred_local_model or fallback_model or 'UNSET_base_model'
    resolved = resolve_existing_path(requested)
    return str(resolved) if resolved.exists() else requested


def build_mlx_lora_config(
    *,
    model_path: str,
    dataset_dir: Path,
    adapter_output: Path,
    cfg: dict[str, Any],
    total_iters: int,
) -> dict[str, Any]:
    return {
        'model': model_path,
        'train': True,
        'data': str(dataset_dir),
        'fine_tune_type': str(cfg.get('fine_tune_type', 'lora')),
        'optimizer': str(cfg.get('optimizer', 'adam')),
        'mask_prompt': bool(cfg.get('mask_prompt', True)),
        'num_layers': int(cfg.get('num_layers', 16)),
        'batch_size': int(cfg.get('per_device_train_batch_size', 1)),
        'iters': int(total_iters),
        'val_batches': int(cfg.get('val_batches', -1)),
        'learning_rate': float(cfg.get('learning_rate', 1e-4)),
        'steps_per_report': int(cfg.get('steps_per_report', 1)),
        'steps_per_eval': int(cfg.get('steps_per_eval', max(1, total_iters // 2))),
        'grad_accumulation_steps': int(cfg.get('gradient_accumulation_steps', 8)),
        'adapter_path': str(adapter_output),
        'save_every': int(cfg.get('save_every', max(1, total_iters))),
        'max_seq_length': int(cfg.get('max_seq_len', 1024)),
        'seed': int(cfg.get('seed', 0)),
        'lora_parameters': {
            'rank': int(cfg.get('lora_r', 32)),
            'dropout': float(cfg.get('lora_dropout', 0.0)),
            'scale': float(cfg.get('lora_alpha', 32)),
        },
    }


def run_train_sft(args: argparse.Namespace) -> None:
    import pandas as pd

    cfg = _load_yaml_config(args.config_path)
    stage = str(cfg.get('stage', args.stage))
    config_name = str(cfg.get('name', Path(args.config_path).stem))

    active_model = load_json_file(Path(DEFAULT_ACTIVE_MODEL_PATH), default={})
    base_model = resolve_training_base_model(cfg.get('base_model'), active_model)

    train_pack_arg = resolve_existing_path(args.train_pack_path)
    if str(train_pack_arg) == str(DEFAULT_STAGE_A_MIX_OUTPUT_PATH) and cfg.get('train_pack_path'):
        train_pack_path = resolve_existing_path(str(cfg['train_pack_path']))
    else:
        train_pack_path = train_pack_arg

    train_pack_df = pd.read_parquet(train_pack_path) if train_pack_path.exists() else pd.DataFrame()
    num_rows = len(train_pack_df)
    batch_size = int(cfg.get('per_device_train_batch_size', 1))
    num_epochs = float(cfg.get('num_epochs', 2.0))
    seed = int(cfg.get('seed', 0))

    train_split_df, valid_split_df, split_strategy = split_training_frame(
        train_pack_df,
        valid_fold=int(args.valid_fold),
        valid_fraction=float(args.valid_fraction),
        seed=seed,
    )
    train_split_df = maybe_limit_rows(train_split_df, max_rows=args.max_train_rows, seed=seed)
    valid_split_df = maybe_limit_rows(valid_split_df, max_rows=args.max_valid_rows, seed=seed)
    train_records, skipped_train_rows = build_training_records(train_split_df)
    valid_records, skipped_valid_rows = build_training_records(valid_split_df)
    effective_train_rows = max(len(train_records), 1)
    total_iters = max(1, int(effective_train_rows * num_epochs // max(batch_size, 1)))

    dataset_dir = Path(args.dataset_dir) if args.dataset_dir else DATASETS_ROOT / f'sft_{stage}_{config_name}'
    dataset_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl_records(dataset_dir / 'train.jsonl', train_records)
    write_jsonl_records(dataset_dir / 'valid.jsonl', valid_records)
    write_jsonl_records(dataset_dir / 'test.jsonl', [])

    manifest = {
        'version': 'v2',
        'created_at': utc_now(),
        'stage': stage,
        'config_name': config_name,
        'model': {'base_model': base_model},
        'adapter': {
            'lora_r': int(cfg.get('lora_r', 32)),
            'lora_alpha': int(cfg.get('lora_alpha', 32)),
            'lora_dropout': float(cfg.get('lora_dropout', 0.0)),
            'target_modules': list(cfg.get('target_modules', [])),
        },
        'data': {
            'train_pack_path': str(train_pack_path),
            'dataset_dir': str(dataset_dir),
            'num_rows': num_rows,
            'train_records': len(train_records),
            'valid_records': len(valid_records),
            'skipped_rows': skipped_train_rows + skipped_valid_rows,
            'effective_train_rows': len(train_records),
            'split_strategy': split_strategy,
            'valid_fraction': float(args.valid_fraction),
            'valid_fold': int(args.valid_fold),
        },
        'training': {
            'learning_rate': float(cfg.get('learning_rate', 1e-4)),
            'num_epochs': num_epochs,
            'warmup_ratio': float(cfg.get('warmup_ratio', 0.03)),
            'max_seq_len': int(cfg.get('max_seq_len', 1024)),
            'per_device_train_batch_size': batch_size,
            'gradient_accumulation_steps': int(cfg.get('gradient_accumulation_steps', 8)),
            'mask_prompt': bool(cfg.get('mask_prompt', True)),
            'num_layers': int(cfg.get('num_layers', 16)),
            'seed': seed,
        },
        'loss': {
            'weighted': bool(cfg.get('weighted_loss', False)),
            'final_line_weight': float(cfg.get('final_line_weight', 1.0)),
            'answer_span_weights': dict(cfg.get('answer_span_weights', {})),
        },
        'weighted_spans': {
            'final_line_weight': float(cfg.get('final_line_weight', 1.0)),
            'answer_span_weights_by_family': dict(cfg.get('answer_span_weights', {})),
        },
        'execution': {
            'supports_runtime_execution': not bool(cfg.get('weighted_loss', False)),
            'requested_execute': bool(args.execute),
        },
    }

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / f'sft_{stage}_{config_name}_manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    adapter_output = out_dir / f'adapter_{stage}_{config_name}'
    mlx_config = build_mlx_lora_config(
        model_path=base_model,
        dataset_dir=dataset_dir,
        adapter_output=adapter_output,
        cfg=cfg,
        total_iters=total_iters,
    )
    mlx_config_path = out_dir / f'sft_{stage}_{config_name}_mlx.yaml'
    mlx_config_path.write_text(yaml.safe_dump(mlx_config, sort_keys=False), encoding='utf-8')
    command_lines = [
        '#!/bin/bash',
        '# Auto-generated by train.py train-sft',
        f'# Stage: {stage}, Config: {config_name}',
        '',
        'uv run python -m mlx_lm lora \\',
        f'  --config "{mlx_config_path}"',
    ]
    command_path = out_dir / f'sft_{stage}_{config_name}_cmd.sh'
    command_path.write_text('\n'.join(command_lines) + '\n', encoding='utf-8')

    if args.execute:
        if bool(cfg.get('weighted_loss', False)):
            raise NotImplementedError('weighted_loss execution is not supported by the current mlx_lm runtime path')
        subprocess.run(
            [sys.executable, '-m', 'mlx_lm', 'lora', '--config', str(mlx_config_path)],
            cwd=str(REPO_ROOT),
            check=True,
        )

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f'\nManifest written to: {manifest_path}')
    print(f'Command script written to: {command_path}')
    print(f'MLX config written to: {mlx_config_path}')


def _resolve_adapter_weight_path(adapter_dir: Path) -> Path:
    for filename in ('adapter_model.safetensors', 'adapter_model.bin'):
        candidate = adapter_dir / filename
        if candidate.exists():
            return candidate
    raise FileNotFoundError('adapter_model.safetensors or adapter_model.bin not found')


def package_adapter_dir(adapter_dir: Path, submission_zip: Path) -> dict[str, Any]:
    import zipfile

    adapter_dir = Path(adapter_dir)
    submission_zip = Path(submission_zip)
    submission_zip.parent.mkdir(parents=True, exist_ok=True)

    adapter_config_path = adapter_dir / 'adapter_config.json'
    if not adapter_config_path.exists():
        raise FileNotFoundError('adapter_config.json not found')

    adapter_cfg = json.loads(adapter_config_path.read_text(encoding='utf-8'))
    rank_value = adapter_cfg.get('r', adapter_cfg.get('rank'))
    if rank_value is None or int(rank_value) > 32:
        raise ValueError(f'LoRA rank must be <= 32, got {rank_value}')

    _resolve_adapter_weight_path(adapter_dir)

    with zipfile.ZipFile(submission_zip, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in adapter_dir.rglob('*'):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(adapter_dir).as_posix())

    with zipfile.ZipFile(submission_zip, 'r') as archive:
        names = archive.namelist()
        if not any(name.endswith('adapter_config.json') for name in names):
            raise RuntimeError('zip missing adapter_config.json')
        if not any(
            name.endswith('adapter_model.safetensors') or name.endswith('adapter_model.bin')
            for name in names
        ):
            raise RuntimeError('zip missing adapter weights')
        return {'adapter_config': adapter_cfg, 'zip_contents': names}


def run_package_peft(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)

    adapter_dir = Path(args.adapter_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    required_files = list(cfg.get('required_files', ['adapter_config.json', 'adapter_model.safetensors']))
    expected_modules = list(cfg.get('expected_target_modules', []))
    expected_rank_cap = int(cfg.get('expected_rank_cap', 32))
    required_keys = list(cfg.get('required_adapter_config_keys', []))
    expected_base_model = cfg.get('expected_base_model_name_or_path')
    local_base_model_path = cfg.get('local_base_model_path')
    submission_zip_name = str(cfg.get('submission_zip_name', 'submission.zip'))

    checks: dict[str, Any] = {}
    for filename in required_files:
        checks[f'file_{filename}'] = (adapter_dir / filename).exists()

    adapter_config_path = adapter_dir / 'adapter_config.json'
    adapter_config: dict[str, Any] = {}
    if adapter_config_path.exists():
        adapter_config = json.loads(adapter_config_path.read_text(encoding='utf-8'))

    for key in required_keys:
        checks[f'key_{key}'] = key in adapter_config

    rank_value = adapter_config.get('r', adapter_config.get('rank'))
    checks['rank_ok'] = rank_value is not None and int(rank_value) <= expected_rank_cap
    actual_modules = list(adapter_config.get('target_modules', []))
    checks['target_modules_ok'] = (
        set(actual_modules) == set(expected_modules) if expected_modules else True
    )
    checks['base_model_ok'] = (
        adapter_config.get('base_model_name_or_path') == expected_base_model
        if expected_base_model
        else 'base_model_name_or_path' in adapter_config
    )

    submission_zip_path = out_dir / submission_zip_name
    zip_contents: list[str] = []
    if (
        all(checks[f'file_{filename}'] for filename in required_files)
        and checks['rank_ok']
        and checks['target_modules_ok']
        and checks['base_model_ok']
    ):
        packaged = package_adapter_dir(adapter_dir, submission_zip_path)
        zip_contents = list(packaged['zip_contents'])
        checks['submission_zip_ok'] = True
    else:
        checks['submission_zip_ok'] = False

    try:
        from peft import PeftModel  # type: ignore
        from transformers import AutoModelForCausalLM  # type: ignore
    except ImportError:
        checks['peft_installed'] = False
        checks['peft_load_status'] = 'peft_not_installed'
    else:
        checks['peft_installed'] = True
        local_base_path = Path(str(local_base_model_path)) if local_base_model_path else None
        if local_base_path is None:
            checks['peft_load_status'] = 'skipped_no_local_base_model'
        elif not local_base_path.exists():
            checks['peft_load_status'] = 'skipped_missing_local_base_model'
        else:
            try:
                base_model = AutoModelForCausalLM.from_pretrained(
                    str(local_base_path),
                    trust_remote_code=True,
                    local_files_only=True,
                )
                peft_model = PeftModel.from_pretrained(base_model, str(adapter_dir))
                peft_model.eval()
            except Exception as exc:
                checks['peft_load_status'] = f'error:{type(exc).__name__}'
                checks['peft_load_error'] = str(exc)
            else:
                checks['peft_load_status'] = 'loaded'

    result = {
        'version': 'v3',
        'created_at': utc_now(),
        'adapter_dir': str(adapter_dir),
        'checks': checks,
        'all_required_files_present': all(checks[f'file_{filename}'] for filename in required_files),
        'adapter_config': adapter_config,
        'submission_zip': str(submission_zip_path),
    }
    result_path = out_dir / 'peft_smoke_result.json'
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    submission_manifest = {
        'version': 'v3',
        'created_at': utc_now(),
        'base_model_name_or_path': adapter_config.get('base_model_name_or_path', 'UNSET'),
        'adapter_dir': str(adapter_dir),
        'adapter_files': {filename: str(adapter_dir / filename) for filename in required_files},
        'lora_rank': rank_value,
        'target_modules': actual_modules,
        'smoke_checks': checks,
        'submission_zip': str(submission_zip_path),
        'submission_zip_contents': zip_contents,
    }
    submission_path = out_dir / 'submission_manifest_v3.json'
    legacy_submission_path = out_dir / 'submission_manifest.json'
    manifest_text = json.dumps(submission_manifest, ensure_ascii=False, indent=2) + '\n'
    submission_path.write_text(manifest_text, encoding='utf-8')
    legacy_submission_path.write_text(manifest_text, encoding='utf-8')

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f'\nSmoke result: {result_path}')
    print(f'Submission manifest: {submission_path}')


def run_write_runbook(args: argparse.Namespace) -> None:
    import csv

    candidate_registry_path = Path(args.candidate_registry_path)
    candidate_registry_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_columns = [
        'candidate_id',
        'model_name',
        'stage',
        'config_name',
        'train_mix',
        'shadow_256_acc',
        'hard_shadow_256_acc',
        'holdout_hard_acc',
        'group_shift_mean_acc',
        'probe_shadow128_k8_majority_acc',
        'daily_score',
        'weekly_score',
        'extraction_fail_rate',
        'format_fail_rate',
        'recorded_at',
        'status',
        'promoted',
        'notes',
    ]
    with candidate_registry_path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=candidate_columns)
        writer.writeheader()

    promotion_rules_path = Path(args.promotion_rules_path)
    promotion_rules_path.parent.mkdir(parents=True, exist_ok=True)
    promotion_rules_path.write_text(
        '# V2 Promotion Gate Rules\n'
        '# Generated by train.py write-runbook\n\n'
        '## Quick Daily Gate\n'
        '- shadow_128 + official_lb\n'
        '- shadow_128 + sc_probe_k8\n\n'
        '## Serious Gate\n'
        '- shadow_256 + official_lb\n'
        '- hard_shadow_256 + official_lb\n\n'
        '## Weekly / Pre-submit Gate\n'
        '- holdout_hard + official_lb\n'
        '- group_shift_split0 + official_lb\n'
        '- group_shift_split1 + official_lb\n'
        '- group_shift_split2 + official_lb\n\n'
        '## Daily Score\n'
        '0.50 * shadow_256_acc\n'
        '+ 0.30 * hard_shadow_256_acc\n'
        '+ 0.20 * probe_shadow128_k8_majority_acc\n\n'
        '## Weekly Score\n'
        '0.35 * shadow_256_acc\n'
        '+ 0.25 * holdout_hard_acc\n'
        '+ 0.20 * group_shift_mean_acc\n'
        '+ 0.10 * hard_shadow_256_acc\n'
        '+ 0.10 * probe_shadow128_k8_majority_acc\n\n'
        '## Candidate Promotion Conditions\n'
        '1. daily_score >= current_best_daily_score\n'
        '2. hard_shadow_256_acc is non-negative versus current best\n'
        '3. extraction_fail_rate does not worsen\n'
        '4. no family shows a catastrophic collapse\n\n'
        '## Submit Promotion Conditions\n'
        '1. weekly_score improves by at least +0.003, or hard split improves by at least +0.005\n'
        '2. bit/text/symbol shows a clear improvement in at least one of those families\n'
        '3. packaging smoke passes\n'
        '4. raw output audit is clean\n',
        encoding='utf-8',
    )

    runbook_path = Path(args.output_path)
    runbook_path.parent.mkdir(parents=True, exist_ok=True)
    runbook_path.write_text(
        f'# V2 Training Command Book\n'
        f'# Generated by train.py write-runbook at {utc_now()}\n\n'
        '## Pipeline Overview\n'
        '# Step 2: Build real canonical table\n'
        'uv run python versions/v2/code/train.py build-real-canonical\n\n'
        '# Step 3: Build solver registry\n'
        'uv run python versions/v2/code/train.py build-solver-registry\n\n'
        '# Step 4: Build synthetic pools\n'
        'uv run python versions/v2/code/train.py build-synth-core\n'
        'uv run python versions/v2/code/train.py build-synth-hard\n\n'
        '# Step 5: Build distill/format/correction pairs\n'
        'uv run python versions/v2/code/train.py build-distill-candidates\n'
        'uv run python versions/v2/code/train.py filter-distilled-traces\n'
        'uv run python versions/v2/code/train.py build-format-pairs\n'
        'uv run python versions/v2/code/train.py build-correction-pairs\n\n'
        '# Step 6: Build train mix\n'
        'uv run python versions/v2/code/train.py build-train-mix\n\n'
        '# Step 7: Train SFT (Stage A)\n'
        'uv run python versions/v2/code/train.py train-sft --stage a --config-path '
        f'{DEFAULT_STAGE_A_R32_ALPHA32_CONFIG_PATH}\n\n'
        '# Step 7: Train SFT (Stage A weighted)\n'
        'uv run python versions/v2/code/train.py train-sft --stage a --config-path '
        f'{DEFAULT_STAGE_A_R32_ALPHA32_WEIGHTED_CONFIG_PATH}\n\n'
        '# Step 7: Train SFT (Stage B)\n'
        'uv run python versions/v2/code/train.py train-sft --stage b --config-path '
        f'{DEFAULT_STAGE_B_HARDENING_CONFIG_PATH}\n\n'
        '# Step 8: Package PEFT\n'
        'uv run python versions/v2/code/train.py package-peft\n\n'
        '# Evaluation handoff\n'
        'uv run python versions/v1/code/train.py run-replay-eval --config official_lb ...\n'
        'uv run python versions/v1/code/train.py run-probe --config sc_probe_k8 ...\n\n'
        '# Step 8: Write runbook (this command)\n'
        'uv run python versions/v2/code/train.py write-runbook\n',
        encoding='utf-8',
    )

    print(f'Candidate registry: {candidate_registry_path}')
    print(f'Promotion rules: {promotion_rules_path}')
    print(f'Runbook: {runbook_path}')


def load_manifest_v4(path: Path) -> dict[str, Any]:
    return load_json_file(path, default={})


def resolve_candidate_spec_v4(
    *,
    manifest_path: str | Path | None = None,
    adapter_path: str | Path | None = None,
    candidate_id: str | None = None,
) -> CandidateSpec:
    if manifest_path is not None:
        manifest_path_obj = _require_existing_path(manifest_path, label='candidate manifest json')
        manifest = load_manifest_v4(manifest_path_obj)
        adapter_dir = normalize_optional_text(manifest.get('execution', {}).get('adapter_dir'))
        base_model = normalize_optional_text(manifest.get('model', {}).get('base_model')) or resolve_active_snapshot_path_v4()
        resolved_candidate_id = (
            candidate_id
            or normalize_optional_text(manifest.get('candidate_id'))
            or f"{normalize_optional_text(manifest.get('stage')) or 'stage'}_{normalize_optional_text(manifest.get('config_name')) or manifest_path_obj.stem}"
        )
        return CandidateSpec(
            candidate_id=resolved_candidate_id,
            manifest_path=manifest_path_obj,
            adapter_path=resolve_existing_path(adapter_dir) if adapter_dir is not None else None,
            base_model=base_model,
            stage=normalize_optional_text(manifest.get('stage')) or '',
            config_name=normalize_optional_text(manifest.get('config_name')) or manifest_path_obj.stem,
            source_version=normalize_optional_text(manifest.get('version')) or 'v4',
            parent_candidate_id=normalize_optional_text(manifest.get('parent_candidate_id')),
        )
    if adapter_path is not None:
        adapter_dir = _require_existing_path(adapter_path, label='adapter directory')
        return CandidateSpec(
            candidate_id=candidate_id or adapter_dir.name,
            manifest_path=None,
            adapter_path=adapter_dir,
            base_model=resolve_active_snapshot_path_v4(),
            stage='',
            config_name=adapter_dir.name,
            source_version='manual',
            parent_candidate_id=None,
        )
    if candidate_id in {None, ''}:
        raise ValueError('Provide at least one of --manifest-path, --adapter-path, or --candidate-id.')
    if candidate_id == 'v3_stage_a_baseline':
        return resolve_candidate_spec_v4(manifest_path=DEFAULT_V3_STAGE_A_MANIFEST_PATH, candidate_id=candidate_id)
    if candidate_id == 'v3_stage_b_baseline':
        return resolve_candidate_spec_v4(manifest_path=DEFAULT_V3_STAGE_B_MANIFEST_PATH, candidate_id=candidate_id)
    for search_root in (REPO_ROOT / 'versions' / 'v4' / 'outputs' / 'train', REPO_ROOT / 'versions' / 'v3' / 'outputs' / 'train'):
        if not search_root.exists():
            continue
        for candidate_manifest in sorted(search_root.rglob('*_manifest.json')):
            payload = load_manifest_v4(candidate_manifest)
            payload_candidate_id = normalize_optional_text(payload.get('candidate_id'))
            if payload_candidate_id == candidate_id or candidate_manifest.stem.startswith(candidate_id):
                return resolve_candidate_spec_v4(manifest_path=candidate_manifest, candidate_id=candidate_id)
    raise FileNotFoundError(f'Unable to resolve candidate_id={candidate_id}')


def read_csv_frame_v4(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def build_scoreboard_row_v4(
    *,
    candidate: CandidateSpec,
    gate_name: str,
    dataset_name: str,
    summary: pd.DataFrame,
    family_metrics: pd.DataFrame,
    submit_value: bool,
) -> dict[str, Any]:
    summary_row = summary.iloc[0].to_dict()
    family_lookup = family_metrics.set_index('family').to_dict(orient='index') if not family_metrics.empty else {}
    return {
        'candidate_id': candidate.candidate_id,
        'parent_candidate_id': candidate.parent_candidate_id or '',
        'gate_name': gate_name,
        'dataset_name': dataset_name,
        'run_name': summary_row.get('run_name', ''),
        'overall_accuracy': summary_row.get('overall_acc', ''),
        'hard_split_accuracy': summary_row.get('overall_acc', '') if dataset_name in {'hard_shadow_256', 'holdout_hard'} else '',
        'bit_accuracy': family_lookup.get('bit_manipulation', {}).get('acc', ''),
        'text_accuracy': family_lookup.get('text_decryption', {}).get('acc', ''),
        'symbol_accuracy': family_lookup.get('symbol_equation', {}).get('acc', ''),
        'format_fail_rate': summary_row.get('format_fail_rate', ''),
        'extraction_fail_rate': summary_row.get('extraction_fail_rate', ''),
        'avg_output_len_chars': summary_row.get('avg_output_len_chars', ''),
        'boxed_rate': summary_row.get('boxed_rate', ''),
        'submit_value': submit_value,
        'manifest_path': str(candidate.manifest_path) if candidate.manifest_path else '',
        'adapter_path': str(candidate.adapter_path) if candidate.adapter_path else '',
        'recorded_at': utc_now(),
    }


def lookup_parent_metrics_v4(parent_candidate_id: str | None, dataset_name: str) -> dict[str, Any]:
    if not parent_candidate_id:
        return {}
    scoreboard = read_csv_frame_v4(Path(DEFAULT_V4_LOCAL_SCOREBOARD_OUTPUT_PATH))
    if scoreboard.empty:
        return {}
    matched = scoreboard.loc[
        (scoreboard['candidate_id'].astype(str) == str(parent_candidate_id))
        & (scoreboard['dataset_name'].astype(str) == str(dataset_name))
    ].copy()
    if matched.empty:
        return {}
    return matched.sort_values('recorded_at').iloc[-1].to_dict()


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float('nan')


def evaluate_submit_value_v4(current: dict[str, Any], parent: dict[str, Any]) -> bool:
    if not parent:
        return False
    overall_gain = not math.isnan(_as_float(current.get('overall_accuracy'))) and not math.isnan(_as_float(parent.get('overall_accuracy'))) and _as_float(current.get('overall_accuracy')) - _as_float(parent.get('overall_accuracy')) >= 0.003
    hard_gain = not math.isnan(_as_float(current.get('hard_split_accuracy'))) and not math.isnan(_as_float(parent.get('hard_split_accuracy'))) and _as_float(current.get('hard_split_accuracy')) - _as_float(parent.get('hard_split_accuracy')) >= 0.005
    format_gain = not math.isnan(_as_float(current.get('format_fail_rate'))) and not math.isnan(_as_float(parent.get('format_fail_rate'))) and _as_float(parent.get('format_fail_rate')) - _as_float(current.get('format_fail_rate')) >= 0.01
    extraction_gain = not math.isnan(_as_float(current.get('extraction_fail_rate'))) and not math.isnan(_as_float(parent.get('extraction_fail_rate'))) and _as_float(parent.get('extraction_fail_rate')) - _as_float(current.get('extraction_fail_rate')) >= 0.01
    hard_family_gain = False
    for key in ('bit_accuracy', 'text_accuracy', 'symbol_accuracy'):
        if not math.isnan(_as_float(current.get(key))) and not math.isnan(_as_float(parent.get(key))) and _as_float(current.get(key)) - _as_float(parent.get(key)) >= 0.01:
            hard_family_gain = True
            break
    return bool(overall_gain or hard_gain or format_gain or extraction_gain or hard_family_gain)


def write_family_regret_rows_v4(
    *,
    candidate_id: str,
    parent_candidate_id: str | None,
    dataset_name: str,
    family_metrics: pd.DataFrame,
) -> None:
    if not parent_candidate_id:
        return
    parent_family_metrics_path = EVAL_ROOT / parent_candidate_id / dataset_name / 'family_metrics.csv'
    if not parent_family_metrics_path.exists():
        return
    parent_family_metrics = pd.read_csv(parent_family_metrics_path)
    merged = family_metrics.merge(parent_family_metrics, on='family', suffixes=('_candidate', '_parent'), how='left')
    for record in merged.to_dict(orient='records'):
        append_csv_row(
            Path(DEFAULT_V4_FAMILY_REGRET_OUTPUT_PATH),
            [
                'candidate_id',
                'parent_candidate_id',
                'dataset_name',
                'family',
                'candidate_acc',
                'parent_acc',
                'delta_acc',
                'candidate_format_fail_rate',
                'parent_format_fail_rate',
                'delta_format_fail_rate',
                'recorded_at',
            ],
            {
                'candidate_id': candidate_id,
                'parent_candidate_id': parent_candidate_id,
                'dataset_name': dataset_name,
                'family': record.get('family', ''),
                'candidate_acc': record.get('acc_candidate', ''),
                'parent_acc': record.get('acc_parent', ''),
                'delta_acc': (
                    float(record.get('acc_candidate')) - float(record.get('acc_parent'))
                    if pd.notna(record.get('acc_candidate')) and pd.notna(record.get('acc_parent'))
                    else ''
                ),
                'candidate_format_fail_rate': record.get('format_fail_rate_candidate', ''),
                'parent_format_fail_rate': record.get('format_fail_rate_parent', ''),
                'delta_format_fail_rate': (
                    float(record.get('format_fail_rate_candidate')) - float(record.get('format_fail_rate_parent'))
                    if pd.notna(record.get('format_fail_rate_candidate')) and pd.notna(record.get('format_fail_rate_parent'))
                    else ''
                ),
                'recorded_at': utc_now(),
            },
        )


def update_candidate_registry_from_score_v4(candidate: CandidateSpec, serious_shadow_row: dict[str, Any] | None, hard_shadow_row: dict[str, Any] | None) -> None:
    parent_metrics = lookup_parent_metrics_v4(candidate.parent_candidate_id, 'shadow_256')
    submit_value = evaluate_submit_value_v4(serious_shadow_row or {}, parent_metrics)
    upsert_csv_row(
        Path(DEFAULT_V4_CANDIDATE_REGISTRY_OUTPUT_PATH),
        [
            'candidate_id',
            'parent_candidate_id',
            'candidate_kind',
            'manifest_path',
            'adapter_path',
            'runtime_lane',
            'stage',
            'recipe_type',
            'pair_kind',
            'train_pack_path',
            'overall_acc',
            'hard_shadow_acc',
            'format_fail_rate',
            'extraction_fail_rate',
            'submit_value',
            'cuda_repro_pass',
            'packaging_pass',
            'selected_for_submit',
            'status',
            'failure_reason',
            'notes',
            'recorded_at',
        ],
        ['candidate_id'],
        {
            'candidate_id': candidate.candidate_id,
            'parent_candidate_id': candidate.parent_candidate_id or '',
            'candidate_kind': 'adapter',
            'manifest_path': str(candidate.manifest_path) if candidate.manifest_path else '',
            'adapter_path': str(candidate.adapter_path) if candidate.adapter_path else '',
            'runtime_lane': 'mac_mlx',
            'stage': candidate.stage,
            'recipe_type': candidate.config_name,
            'pair_kind': '',
            'train_pack_path': load_manifest_v4(candidate.manifest_path).get('data', {}).get('train_pack_path', '') if candidate.manifest_path else '',
            'overall_acc': '' if serious_shadow_row is None else serious_shadow_row.get('overall_accuracy', ''),
            'hard_shadow_acc': '' if hard_shadow_row is None else hard_shadow_row.get('overall_accuracy', hard_shadow_row.get('hard_split_accuracy', '')),
            'format_fail_rate': '' if serious_shadow_row is None else serious_shadow_row.get('format_fail_rate', ''),
            'extraction_fail_rate': '' if serious_shadow_row is None else serious_shadow_row.get('extraction_fail_rate', ''),
            'submit_value': submit_value,
            'cuda_repro_pass': False,
            'packaging_pass': False,
            'selected_for_submit': False,
            'status': 'scored',
            'failure_reason': '',
            'notes': '',
            'recorded_at': utc_now(),
        },
    )


def evaluate_dataset_to_dir_v4(candidate: CandidateSpec, dataset_cfg: dict[str, Any], *, gate_name: str, out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = V1_MODULE.load_table(_require_existing_path(dataset_cfg['input_path'], label='eval dataset'))
    eval_config = V1_MODULE.load_eval_config(str(dataset_cfg['eval_config']))
    backend = V1_MODULE.MLXBackend(
        model_path=str(candidate.base_model),
        adapter_path=str(candidate.adapter_path) if candidate.adapter_path else None,
    )
    tokenizer, tokenizer_name, tokenizer_revision = V1_MODULE.get_tokenizer(
        tokenizer_path=None,
        tokenizer_name=None,
        tokenizer_revision=None,
    )
    artifacts = V1_MODULE.evaluate_dataset(
        frame,
        backend,
        eval_config,
        out_dir,
        tokenizer=tokenizer,
        run_name=f'{candidate.candidate_id}-{dataset_cfg["dataset_name"]}-{eval_config.name}',
        dataset_name=str(dataset_cfg['dataset_name']),
    )
    if eval_config.n_samples_per_prompt > 1:
        sample_level = V1_MODULE.build_sample_level_frame(artifacts.row_level)
        probe_metrics = V1_MODULE.build_probe_metrics_frame(artifacts.row_level)
        summary = V1_MODULE.augment_summary_for_probe(artifacts.summary, probe_metrics)
        family_metrics = V1_MODULE.augment_family_metrics_for_probe(artifacts.family_metrics, probe_metrics)
        V1_MODULE.save_table(sample_level, out_dir / 'sample_level.parquet')
        V1_MODULE.save_table(probe_metrics, out_dir / 'probe_metrics.csv')
        V1_MODULE.save_table(summary, out_dir / 'summary.csv')
        V1_MODULE.save_table(family_metrics, out_dir / 'family_metrics.csv')
    V1_MODULE.save_run_manifest(
        out_dir / 'run_manifest.json',
        {
            'candidate_id': candidate.candidate_id,
            'gate_name': gate_name,
            'dataset_name': dataset_cfg['dataset_name'],
            'config': eval_config.name,
            'backend': 'mlx',
            'adapter_path': str(candidate.adapter_path) if candidate.adapter_path else '',
            'model_path': str(candidate.base_model),
            'tokenizer_name': tokenizer_name,
            'tokenizer_revision': tokenizer_revision,
            'timestamp': utc_now(),
        },
    )
    return artifacts.summary, artifacts.family_metrics, artifacts.failure_metrics


def run_bootstrap_v4(args: argparse.Namespace) -> None:
    ensure_v4_layout_scaffold()
    append_experiment_log('bootstrap_v4', 'completed', version_root=str(VERSION_ROOT))
    print(json.dumps({'version': 'v4', 'status': 'bootstrapped', 'version_root': str(VERSION_ROOT)}, ensure_ascii=False, indent=2))


def run_score_candidate_v4(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    gate_name = str(cfg.get('gate_name', Path(args.config_path).stem))
    candidate = resolve_candidate_spec_v4(
        manifest_path=getattr(args, 'manifest_path', None),
        adapter_path=getattr(args, 'adapter_path', None),
        candidate_id=getattr(args, 'candidate_id', None),
    )
    out_root = Path(args.output_root or (EVAL_ROOT / candidate.candidate_id))
    out_root.mkdir(parents=True, exist_ok=True)
    serious_shadow_row: dict[str, Any] | None = None
    hard_shadow_row: dict[str, Any] | None = None
    for dataset_cfg in list(cfg.get('datasets', [])):
        dataset_name = str(dataset_cfg['dataset_name'])
        summary, family_metrics, _ = evaluate_dataset_to_dir_v4(candidate, dataset_cfg, gate_name=gate_name, out_dir=out_root / dataset_name)
        parent_metrics = lookup_parent_metrics_v4(candidate.parent_candidate_id, dataset_name)
        score_row = build_scoreboard_row_v4(
            candidate=candidate,
            gate_name=gate_name,
            dataset_name=dataset_name,
            summary=summary,
            family_metrics=family_metrics,
            submit_value=False,
        )
        score_row['submit_value'] = evaluate_submit_value_v4(score_row, parent_metrics)
        append_csv_row(
            Path(DEFAULT_V4_LOCAL_SCOREBOARD_OUTPUT_PATH),
            [
                'candidate_id',
                'parent_candidate_id',
                'gate_name',
                'dataset_name',
                'run_name',
                'overall_accuracy',
                'hard_split_accuracy',
                'bit_accuracy',
                'text_accuracy',
                'symbol_accuracy',
                'format_fail_rate',
                'extraction_fail_rate',
                'avg_output_len_chars',
                'boxed_rate',
                'submit_value',
                'manifest_path',
                'adapter_path',
                'recorded_at',
            ],
            score_row,
        )
        write_family_regret_rows_v4(
            candidate_id=candidate.candidate_id,
            parent_candidate_id=candidate.parent_candidate_id,
            dataset_name=dataset_name,
            family_metrics=family_metrics,
        )
        if dataset_name == 'shadow_256':
            serious_shadow_row = score_row
        if dataset_name == 'hard_shadow_256':
            hard_shadow_row = score_row
    if serious_shadow_row is not None or hard_shadow_row is not None:
        update_candidate_registry_from_score_v4(candidate, serious_shadow_row, hard_shadow_row)
    append_experiment_log('score_candidate_v4', 'completed', candidate_id=candidate.candidate_id, gate_name=gate_name, output_root=str(out_root))
    print(json.dumps({'candidate_id': candidate.candidate_id, 'gate_name': gate_name, 'output_root': str(out_root)}, ensure_ascii=False, indent=2))


def run_score_candidate_batch_v4(args: argparse.Namespace) -> None:
    for manifest_path in list(getattr(args, 'manifest_paths', []) or []):
        run_score_candidate_v4(
            argparse.Namespace(
                config_path=args.config_path,
                manifest_path=manifest_path,
                adapter_path=None,
                candidate_id=None,
                output_root=None,
            )
        )
    for candidate_id in list(getattr(args, 'candidate_ids', []) or []):
        run_score_candidate_v4(
            argparse.Namespace(
                config_path=args.config_path,
                manifest_path=None,
                adapter_path=None,
                candidate_id=candidate_id,
                output_root=None,
            )
        )


def merge_v4_metadata(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or not DEFAULT_V2_REAL_CANONICAL_PATH.exists():
        return frame.copy()
    metadata = pd.read_parquet(DEFAULT_V2_REAL_CANONICAL_PATH)
    columns = [column for column in ['id', 'difficulty_tags', 'importance_prior', 'hard_score', 'cv5_fold', 'format_policy'] if column in metadata.columns]
    if 'id' not in columns:
        return frame.copy()
    prepared = metadata.loc[:, columns].rename(columns={'id': 'source_id'})
    return frame.merge(prepared, on='source_id', how='left')


def upsert_parquet_rows(path: Path, frame: pd.DataFrame, key_columns: Sequence[str]) -> None:
    if path.exists():
        existing = pd.read_parquet(path)
        combined = pd.concat([existing, frame], ignore_index=True)
        combined = combined.drop_duplicates(subset=list(key_columns), keep='last')
    else:
        combined = frame.copy()
    path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(path, index=False)


def run_build_format_preferences_v4(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    input_path = _require_existing_path(getattr(args, 'input_path', None) or cfg.get('input_path', SOURCE_V3_PREFERENCE_PAIRS_PATH), label='v3 preference parquet')
    source_df = pd.read_parquet(input_path)
    pair_df = source_df.loc[source_df['pair_kind'].astype(str) == str(cfg.get('pair_kind', 'format'))].copy()
    pair_df = merge_v4_metadata(pair_df)
    pair_df['pair_type'] = 'format'
    pair_df['chosen_text'] = pair_df['chosen_output']
    pair_df['rejected_text'] = pair_df['rejected_output']
    pair_df['chosen_format_safe'] = pair_df['chosen_format_bucket'].isin(CLEAN_FORMAT_BUCKETS_V4)
    pair_df['rejected_format_safe'] = pair_df['rejected_format_bucket'].isin(CLEAN_FORMAT_BUCKETS_V4)
    pair_df['chosen_length'] = pair_df['chosen_output'].astype(str).str.len()
    pair_df['rejected_length'] = pair_df['rejected_output'].astype(str).str.len()
    pair_df['selection_reason'] = pair_df['preference_reason']
    pair_df['acceptance_status'] = 'accepted'
    output_path = Path(args.output_path or DEFAULT_V4_FORMAT_PREFERENCE_OUTPUT_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pair_df.to_parquet(output_path, index=False)
    registry_df = pair_df.loc[
        :,
        [
            'pair_id',
            'pair_type',
            'family',
            'difficulty_tags',
            'chosen_text',
            'rejected_text',
            'chosen_is_correct',
            'rejected_is_correct',
            'chosen_format_safe',
            'rejected_format_safe',
            'chosen_length',
            'rejected_length',
            'selection_reason',
            'acceptance_status',
            'source_id',
        ],
    ].copy().rename(
        columns={
            'chosen_is_correct': 'chosen_exact',
            'rejected_is_correct': 'rejected_exact',
            'source_id': 'source_candidate_id',
        }
    )
    upsert_parquet_rows(Path(args.registry_path or DEFAULT_V4_PREFERENCE_REGISTRY_OUTPUT_PATH), registry_df, ['pair_id'])
    append_experiment_log('build_format_preferences_v4', 'completed', rows=len(pair_df), output_path=str(output_path))
    print(json.dumps({'rows': len(pair_df), 'output_path': str(output_path)}, ensure_ascii=False, indent=2))


def run_build_correctness_preferences_v4(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    input_path = _require_existing_path(getattr(args, 'input_path', None) or cfg.get('input_path', SOURCE_V3_PREFERENCE_PAIRS_PATH), label='v3 preference parquet')
    source_df = pd.read_parquet(input_path)
    pair_df = source_df.loc[source_df['pair_kind'].astype(str) == str(cfg.get('pair_kind', 'correction'))].copy()
    allowed_families = {str(family) for family in cfg.get('allowed_families', sorted(HARD_FAMILIES_V4))}
    pair_df = pair_df.loc[pair_df['family'].astype(str).isin(allowed_families)].copy()
    pair_df = merge_v4_metadata(pair_df)
    pair_df['pair_type'] = 'correction'
    pair_df['chosen_text'] = pair_df['chosen_output']
    pair_df['rejected_text'] = pair_df['rejected_output']
    pair_df['chosen_format_safe'] = pair_df['chosen_format_bucket'].isin(CLEAN_FORMAT_BUCKETS_V4)
    pair_df['rejected_format_safe'] = pair_df['rejected_format_bucket'].isin(CLEAN_FORMAT_BUCKETS_V4)
    pair_df['chosen_length'] = pair_df['chosen_output'].astype(str).str.len()
    pair_df['rejected_length'] = pair_df['rejected_output'].astype(str).str.len()
    pair_df['selection_reason'] = pair_df['preference_reason']
    pair_df['acceptance_status'] = 'accepted'
    output_path = Path(args.output_path or DEFAULT_V4_CORRECTNESS_PREFERENCE_OUTPUT_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pair_df.to_parquet(output_path, index=False)
    registry_df = pair_df.loc[
        :,
        [
            'pair_id',
            'pair_type',
            'family',
            'difficulty_tags',
            'chosen_text',
            'rejected_text',
            'chosen_is_correct',
            'rejected_is_correct',
            'chosen_format_safe',
            'rejected_format_safe',
            'chosen_length',
            'rejected_length',
            'selection_reason',
            'acceptance_status',
            'source_id',
        ],
    ].copy().rename(
        columns={
            'chosen_is_correct': 'chosen_exact',
            'rejected_is_correct': 'rejected_exact',
            'source_id': 'source_candidate_id',
        }
    )
    upsert_parquet_rows(Path(args.registry_path or DEFAULT_V4_PREFERENCE_REGISTRY_OUTPUT_PATH), registry_df, ['pair_id'])
    append_experiment_log('build_correctness_preferences_v4', 'completed', rows=len(pair_df), output_path=str(output_path))
    print(json.dumps({'rows': len(pair_df), 'output_path': str(output_path)}, ensure_ascii=False, indent=2))


def select_rft_source_frame_v4(cfg: dict[str, Any]) -> pd.DataFrame:
    source_path = _require_existing_path(cfg.get('source_path', DEFAULT_V2_REAL_CANONICAL_PATH), label='rft source parquet')
    frame = _read_table(source_path)
    allowed_families = {str(family) for family in cfg.get('allowed_families', sorted(HARD_FAMILIES_V4))}
    frame = frame.loc[frame['family'].astype(str).isin(allowed_families)].copy()
    frame['hard_score'] = pd.to_numeric(frame.get('hard_score', 0.0), errors='coerce').fillna(0.0)
    frame['importance_prior'] = pd.to_numeric(frame.get('importance_prior', 1.0), errors='coerce').fillna(1.0)
    frame = frame.loc[frame['hard_score'] >= float(cfg.get('min_hard_score', 0.0))].copy()
    frame = frame.sort_values(['family', 'hard_score', 'importance_prior'], ascending=[True, False, False]).reset_index(drop=True)
    max_rows_per_family = int(cfg.get('max_rows_per_family', 64))
    return frame.groupby('family', group_keys=False).head(max_rows_per_family).reset_index(drop=True)


def run_build_rft_candidates_v4(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    candidate = resolve_candidate_spec_v4(
        manifest_path=getattr(args, 'manifest_path', None),
        adapter_path=getattr(args, 'adapter_path', None),
        candidate_id=getattr(args, 'candidate_id', None) or 'v3_stage_a_baseline',
    )
    selected = select_rft_source_frame_v4(cfg)
    prompt_selection_path = Path(args.prompt_selection_path or (DATASETS_ROOT / f'rft_prompt_selection_{candidate.candidate_id}.parquet'))
    prompt_selection_path.parent.mkdir(parents=True, exist_ok=True)
    selected.to_parquet(prompt_selection_path, index=False)
    probe_config = str(cfg.get('probe_config', 'sc_probe_k4'))
    probe_dir = Path(args.output_dir or (EVAL_ROOT / f'rft_probe_{candidate.candidate_id}'))
    evaluate_dataset_to_dir_v4(
        candidate,
        {'dataset_name': 'rft_probe', 'input_path': str(prompt_selection_path), 'eval_config': probe_config},
        gate_name='rft_probe',
        out_dir=probe_dir,
    )
    row_level = pd.read_parquet(probe_dir / 'row_level.parquet')
    selected_cols = selected.loc[:, [column for column in ['id', 'prompt', 'answer', 'family', 'cv5_fold', 'difficulty_tags'] if column in selected.columns]].copy()
    merged = row_level.merge(selected_cols, on='id', how='left')
    for target, candidates in {
        'family': ('family', 'family_y', 'family_x'),
        'cv5_fold': ('cv5_fold', 'cv5_fold_y', 'cv5_fold_x'),
        'difficulty_tags': ('difficulty_tags', 'difficulty_tags_y', 'difficulty_tags_x'),
    }.items():
        if target in merged.columns:
            continue
        for candidate_col in candidates:
            if candidate_col in merged.columns:
                merged[target] = merged[candidate_col]
                break
    output_path = Path(args.output_path or DEFAULT_V4_RFT_GENERATIONS_OUTPUT_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as handle:
        for record in merged.to_dict(orient='records'):
            handle.write(json.dumps(record, ensure_ascii=False) + '\n')
    append_experiment_log('build_rft_candidates_v4', 'completed', candidate_id=candidate.candidate_id, prompt_rows=len(selected), sample_rows=len(merged), output_path=str(output_path))
    print(json.dumps({'candidate_id': candidate.candidate_id, 'prompt_rows': len(selected), 'sample_rows': len(merged), 'output_path': str(output_path)}, ensure_ascii=False, indent=2))


def score_rft_row_v4(record: dict[str, Any]) -> float:
    reward = 0.0
    if bool(record.get('is_correct')):
        reward += 1.0
    if str(record.get('format_bucket', '')) in CLEAN_FORMAT_BUCKETS_V4:
        reward += 0.2
    if not bool(record.get('contains_extra_numbers')):
        reward += 0.1
    if str(record.get('format_bucket', '')) == 'boxed_multiple':
        reward -= 0.5
    return reward


def _coalesce_record_value(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = record.get(key)
        if value is None:
            continue
        if isinstance(value, float) and pd.isna(value):
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def run_filter_rft_accept_pool_v4(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    max_trace_tokens_est = int(cfg.get('max_trace_tokens_est', 96))
    input_path = _require_existing_path(args.input_path or DEFAULT_V4_RFT_GENERATIONS_OUTPUT_PATH, label='rft candidate generations jsonl')
    rows = [json.loads(line) for line in input_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    frame = pd.DataFrame(rows)
    accepted_rows: list[dict[str, Any]] = []
    registry_rows: list[dict[str, Any]] = []
    if not frame.empty:
        for prompt_id, group in frame.groupby('id', sort=True):
            prepared = group.copy()
            prepared['reward'] = prepared.apply(score_rft_row_v4, axis=1)
            prepared['cleaned_output'] = prepared['raw_output'].map(lambda value: strip_known_generation_warnings(str(value or '')))
            prepared['trace_tokens_est'] = prepared['cleaned_output'].map(estimate_trace_tokens)
            clean_correct = prepared.loc[
                prepared['is_correct'].fillna(False)
                & prepared['format_bucket'].astype(str).isin(CLEAN_FORMAT_BUCKETS_V4)
                & (~prepared['contains_extra_numbers'].fillna(False))
            ].copy()
            accepted = clean_correct.loc[clean_correct['trace_tokens_est'] <= max_trace_tokens_est].copy()
            accepted = accepted.sort_values(['trace_tokens_est', 'raw_output_len_chars', 'sample_idx', 'seed']).reset_index(drop=True)
            if not accepted.empty:
                best = accepted.iloc[0].to_dict()
                answer = normalize_optional_text(_coalesce_record_value(best, 'gold_answer', 'answer')) or ''
                family = normalize_optional_text(_coalesce_record_value(best, 'family', 'family_y', 'family_x')) or ''
                cv5_fold = _coalesce_record_value(best, 'cv5_fold', 'cv5_fold_y', 'cv5_fold_x')
                cleaned_output = str(best.get('cleaned_output', ''))
                accepted_rows.append(
                    {
                        'accept_id': f'rft_{prompt_id}',
                        'source_id': str(prompt_id),
                        'prompt': best.get('prompt', ''),
                        'answer': answer,
                        'family': family,
                        'cv5_fold': '' if cv5_fold is None else cv5_fold,
                        'chosen_output': cleaned_output,
                        'extracted_answer': best.get('extracted_answer', ''),
                        'format_policy': select_v3_format_policy(answer, family),
                        'target_style': 'short',
                        'source_dataset': 'rft_accept',
                        'reward': best.get('reward', 0.0),
                        'trace_tokens_est': int(best.get('trace_tokens_est', 0)),
                    }
                )
                registry_rows.append(
                    {
                        'candidate_id': prompt_id,
                        'source_candidate_id': prompt_id,
                        'family': family,
                        'sample_k': int(len(group)),
                        'accepted_count': int(len(accepted)),
                        'accepted_rate': float(len(accepted) / len(group)),
                        'reward_mean': float(prepared['reward'].mean()),
                        'reward_max': float(prepared['reward'].max()),
                        'best_completion': cleaned_output,
                        'selection_reason': 'shortest_clean_correct',
                        'rejection_reason': '',
                        'format_bucket': best.get('format_bucket', ''),
                        'status': 'accepted',
                    }
                )
            else:
                dominant_failure = prepared['format_bucket'].astype(str).value_counts().index[0] if not prepared.empty else 'no_rows'
                rejection_reason = 'trace_too_long' if not clean_correct.empty else dominant_failure
                registry_rows.append(
                    {
                        'candidate_id': prompt_id,
                        'source_candidate_id': prompt_id,
                        'family': normalize_optional_text(
                            _coalesce_record_value(prepared.iloc[0].to_dict(), 'family', 'family_y', 'family_x')
                        )
                        if not prepared.empty
                        else '',
                        'sample_k': int(len(group)),
                        'accepted_count': 0,
                        'accepted_rate': 0.0,
                        'reward_mean': float(prepared['reward'].mean()) if not prepared.empty else 0.0,
                        'reward_max': float(prepared['reward'].max()) if not prepared.empty else 0.0,
                        'best_completion': '',
                        'selection_reason': '',
                        'rejection_reason': rejection_reason,
                        'format_bucket': dominant_failure,
                        'status': 'rejected',
                    }
                )
    accepted_df = pd.DataFrame(accepted_rows)
    registry_df = pd.DataFrame(registry_rows)
    output_path = Path(args.output_path or DEFAULT_V4_RFT_ACCEPT_POOL_OUTPUT_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    accepted_df.to_parquet(output_path, index=False)
    registry_path = Path(args.registry_path or DEFAULT_V4_RFT_REGISTRY_OUTPUT_PATH)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_df.to_parquet(registry_path, index=False)
    audit_output_path = Path(args.audit_output_path or (AUDITS_ROOT / 'rft_accept_pool_v4.csv'))
    audit_output_path.parent.mkdir(parents=True, exist_ok=True)
    registry_df.to_csv(audit_output_path, index=False)
    append_experiment_log('filter_rft_accept_pool_v4', 'completed', accepted_rows=len(accepted_df), output_path=str(output_path), registry_path=str(registry_path))
    print(json.dumps({'accepted_rows': len(accepted_df), 'output_path': str(output_path), 'registry_path': str(registry_path)}, ensure_ascii=False, indent=2))


def run_build_stage_c_mix_v4(args: argparse.Namespace) -> None:
    rft_cfg = _load_yaml_config(args.rft_config_path)
    pref_cfg = _load_yaml_config(args.preference_config_path)
    rft_df = pd.read_parquet(_require_existing_path(args.rft_accept_pool_path or DEFAULT_V4_RFT_ACCEPT_POOL_OUTPUT_PATH, label='rft accept pool parquet'))
    replay_df = pd.read_parquet(_require_existing_path(rft_cfg.get('replay_source_path', SOURCE_V3_STAGE_A_OUTPUT_PATH), label='replay source parquet'))
    target_total = int(rft_cfg.get('target_total', 4096))
    rft_target = int(round(target_total * float(rft_cfg.get('rft_ratio', 0.9))))
    replay_target = target_total - rft_target
    rft_sampled = _sample_with_weight(rft_df.assign(train_sample_weight=1.0), min(rft_target, len(rft_df)), 'train_sample_weight', 401) if not rft_df.empty else pd.DataFrame()
    replay_weight_col = 'sample_weight' if 'sample_weight' in replay_df.columns else 'train_sample_weight'
    replay_sampled = _sample_with_weight(replay_df, min(replay_target, len(replay_df)), replay_weight_col, 402) if not replay_df.empty else pd.DataFrame()
    if len(rft_sampled) < rft_target and not replay_df.empty:
        shortfall = rft_target - len(rft_sampled)
        extra_replay = _sample_with_weight(replay_df, min(shortfall, len(replay_df)), replay_weight_col, 403)
        replay_sampled = pd.concat([replay_sampled, extra_replay], ignore_index=True).drop_duplicates(subset=['row_id'] if 'row_id' in replay_sampled.columns else ['id']).reset_index(drop=True)
    rft_mix = pd.concat([rft_sampled, replay_sampled], ignore_index=True)
    if not rft_mix.empty:
        rft_mix['row_id'] = [f"rftmix_{stable_hash(index, row.get('source_id', row.get('id', '')))}" for index, row in enumerate(rft_mix.to_dict(orient='records'))]
        completions = [build_training_completion(row) for row in rft_mix.to_dict(orient='records')]
        rft_mix['chosen_output'] = completions
        rft_mix['target_text'] = completions
    rft_output_path = Path(args.rft_output_path or DEFAULT_V4_STAGE_C_RFT_OUTPUT_PATH)
    rft_output_path.parent.mkdir(parents=True, exist_ok=True)
    rft_mix.to_parquet(rft_output_path, index=False)

    format_df = pd.read_parquet(_require_existing_path(args.format_pairs_path or DEFAULT_V4_FORMAT_PREFERENCE_OUTPUT_PATH, label='format preference parquet'))
    correctness_df = pd.read_parquet(_require_existing_path(args.correctness_pairs_path or DEFAULT_V4_CORRECTNESS_PREFERENCE_OUTPUT_PATH, label='correctness preference parquet'))
    target_total_pairs = int(pref_cfg.get('target_total_pairs', 4096))
    format_target = int(round(target_total_pairs * float(pref_cfg.get('format_ratio', 0.6))))
    correctness_target = target_total_pairs - format_target
    format_sampled = _sample_with_weight(format_df.assign(pair_weight=1.0), min(format_target, len(format_df)), 'pair_weight', 501) if not format_df.empty else pd.DataFrame()
    correctness_sampled = _sample_with_weight(correctness_df.assign(pair_weight=1.0), min(correctness_target, len(correctness_df)), 'pair_weight', 502) if not correctness_df.empty else pd.DataFrame()
    preference_mix = pd.concat([format_sampled, correctness_sampled], ignore_index=True)
    preference_output_path = Path(args.preference_output_path or DEFAULT_V4_STAGE_C_PREFERENCE_OUTPUT_PATH)
    preference_output_path.parent.mkdir(parents=True, exist_ok=True)
    preference_mix.to_parquet(preference_output_path, index=False)
    append_experiment_log('build_stage_c_mix_v4', 'completed', rft_rows=len(rft_mix), preference_rows=len(preference_mix), rft_output_path=str(rft_output_path), preference_output_path=str(preference_output_path))
    print(json.dumps({'rft_rows': len(rft_mix), 'preference_rows': len(preference_mix), 'rft_output_path': str(rft_output_path), 'preference_output_path': str(preference_output_path)}, ensure_ascii=False, indent=2))


def load_adapter_config_v4(adapter_dir: Path | None) -> dict[str, Any]:
    if adapter_dir is None:
        return {}
    config_path = adapter_dir / 'adapter_config.json'
    if not config_path.exists():
        return {}
    return load_json_file(config_path, default={})


def save_json_v4(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def prepare_parent_adapter_path_v4(cfg: dict[str, Any], args: argparse.Namespace) -> Path | None:
    value = normalize_optional_text(getattr(args, 'init_adapter_path', None)) or normalize_optional_text(cfg.get('init_adapter_path'))
    if value is None:
        return None
    return _require_existing_path(value, label='initial adapter directory')


def weighted_training_execute_v4(
    *,
    train_records: list[dict[str, Any]],
    valid_records: list[dict[str, Any]],
    cfg: dict[str, Any],
    base_model: str,
    output_dir: Path,
    adapter_dir: Path,
    metrics_path: Path,
    init_adapter_path: Path | None,
) -> dict[str, Any]:
    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
    import numpy as np
    from mlx_lm import load as mlx_load
    from mlx_lm.tuner import TrainingArgs, train as tuner_train
    from mlx_lm.tuner.datasets import CacheDataset
    from mlx_lm.tuner.utils import linear_to_lora_layers, load_adapters, print_trainable_parameters
    from mlx_lm.utils import save_config

    class MetricsCallback:
        def __init__(self) -> None:
            self.last_train_loss: float | None = None
            self.last_val_loss: float | None = None
            self.peak_memory: float | None = None

        def on_train_loss_report(self, payload: dict[str, Any]) -> None:
            self.last_train_loss = float(payload.get('train_loss')) if payload.get('train_loss') is not None else None
            self.peak_memory = float(payload.get('peak_memory')) if payload.get('peak_memory') is not None else self.peak_memory
            append_jsonl(metrics_path, {'kind': 'train', 'created_at': utc_now(), **payload})

        def on_val_loss_report(self, payload: dict[str, Any]) -> None:
            self.last_val_loss = float(payload.get('val_loss')) if payload.get('val_loss') is not None else None
            append_jsonl(metrics_path, {'kind': 'val', 'created_at': utc_now(), **payload})

    class WeightedDataset:
        def __init__(self, data: list[dict[str, Any]], tokenizer: Any) -> None:
            self._data = data
            self.tokenizer = tokenizer
            self.mask_prompt = True

        def __getitem__(self, index: int) -> dict[str, Any]:
            return self._data[index]

        def __len__(self) -> int:
            return len(self._data)

        def process(self, datum: dict[str, Any]) -> tuple[list[int], int, list[float]]:
            prompt = str(datum['prompt'])
            completion = str(datum['completion'])
            messages = [{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': completion}]
            tokens = list(self.tokenizer.apply_chat_template(messages, return_dict=False))
            offset = len(self.tokenizer.apply_chat_template(messages[:-1], add_generation_prompt=True, return_dict=False))
            completion_weights = _build_completion_token_weights(self.tokenizer, completion, str(datum['metadata'].get('family', '')), cfg)
            token_weights = [1.0] * offset + completion_weights
            if len(token_weights) < len(tokens):
                token_weights.extend([completion_weights[-1] if completion_weights else 1.0] * (len(tokens) - len(token_weights)))
            return (tokens, offset, token_weights[: len(tokens)])

    def iterate_weighted_batches(dataset: Any, batch_size: int, max_seq_length: int, loop: bool = False, seed: int | None = None, comm_group: Any = None):
        idx = sorted(range(len(dataset)), key=lambda sample_index: len(dataset[sample_index][0]))
        if len(dataset) < batch_size:
            raise ValueError(f'Dataset must have at least batch_size={batch_size} examples but only has {len(dataset)}.')
        if comm_group is not None:
            offset = comm_group.rank()
            step = comm_group.size()
        else:
            offset = 0
            step = 1
        if batch_size % step != 0:
            raise ValueError('The batch size must be divisible by the number of workers')
        batch_idx = [idx[i + offset : i + offset + batch_size : step] for i in range(0, len(idx) - batch_size + 1, batch_size)]
        if seed is not None:
            np.random.seed(seed)
        while True:
            indices = np.random.permutation(len(batch_idx))
            for batch_index in indices:
                batch = [dataset[item_index] for item_index in batch_idx[batch_index]]
                token_lists, offsets, weight_lists = zip(*batch)
                lengths = [len(tokens) for tokens in token_lists]
                pad_to = 32
                max_length = min(1 + pad_to * ((max(lengths) + pad_to - 1) // pad_to), max_seq_length)
                batch_arr = np.zeros((batch_size // step, max_length), np.int32)
                weight_arr = np.ones((batch_size // step, max_length), np.float32)
                packed_lengths: list[tuple[int, int]] = []
                for row_index in range(batch_size // step):
                    truncated_length = min(lengths[row_index], max_seq_length)
                    batch_arr[row_index, :truncated_length] = token_lists[row_index][:truncated_length]
                    weight_arr[row_index, :truncated_length] = weight_lists[row_index][:truncated_length]
                    packed_lengths.append((int(offsets[row_index]), truncated_length))
                yield mx.array(batch_arr), mx.array(packed_lengths), mx.array(weight_arr)
            if not loop:
                break

    def weighted_loss(model: Any, batch: Any, lengths: Any, token_weights: Any) -> tuple[Any, Any]:
        inputs = batch[:, :-1]
        targets = batch[:, 1:]
        logits = model(inputs)
        steps = mx.arange(1, targets.shape[1] + 1)
        prompt_mask = mx.logical_and(steps >= lengths[:, 0:1], steps <= lengths[:, 1:])
        weights = token_weights[:, 1:] * prompt_mask.astype(token_weights.dtype)
        ntoks = weights.astype(mx.float32).sum()
        ce = nn.losses.cross_entropy(logits, targets) * weights
        denom = mx.maximum(ntoks, mx.array(1.0, dtype=mx.float32))
        ce = ce.astype(mx.float32).sum() / denom
        return ce, ntoks

    callback = MetricsCallback()
    model, tokenizer = mlx_load(base_model)
    model.freeze()
    if init_adapter_path is not None:
        load_adapters(model, str(init_adapter_path))
        adapter_config = load_adapter_config_v4(init_adapter_path)
    else:
        linear_to_lora_layers(
            model,
            int(cfg.get('num_layers', 16)),
            {
                'rank': int(cfg.get('lora_r', 32)),
                'dropout': float(cfg.get('lora_dropout', 0.0)),
                'scale': float(cfg.get('lora_alpha', 32)),
            },
        )
        adapter_config = {}
    print_trainable_parameters(model)
    adapter_dir.mkdir(parents=True, exist_ok=True)
    save_config(
        {
            'base_model_name_or_path': base_model,
            'fine_tune_type': adapter_config.get('fine_tune_type', 'lora'),
            'num_layers': int(adapter_config.get('num_layers', cfg.get('num_layers', 16))),
            'lora_parameters': adapter_config.get(
                'lora_parameters',
                {
                    'rank': int(cfg.get('lora_r', 32)),
                    'dropout': float(cfg.get('lora_dropout', 0.0)),
                    'scale': float(cfg.get('lora_alpha', 32)),
                },
            ),
            'target_modules': list(adapter_config.get('target_modules', cfg.get('target_modules', []))),
            'weighted_loss': True,
            'rationale_weight': float(cfg.get('rationale_weight', 1.0)),
            'final_line_weight': float(cfg.get('final_line_weight', 3.0)),
            'answer_span_weights': dict(cfg.get('answer_span_weights', {})),
            'parent_adapter_path': str(init_adapter_path) if init_adapter_path is not None else '',
        },
        adapter_dir / 'adapter_config.json',
    )
    optimizer = optim.Adam(learning_rate=float(cfg.get('learning_rate', 1e-4)))
    training_args = TrainingArgs(
        batch_size=int(cfg.get('per_device_train_batch_size', 1)),
        iters=int(cfg.get('iters', 1)),
        val_batches=int(cfg.get('val_batches', -1)),
        steps_per_report=int(cfg.get('steps_per_report', 1)),
        steps_per_eval=int(cfg.get('steps_per_eval', max(1, int(cfg.get('iters', 1)) // 2))),
        steps_per_save=int(cfg.get('save_every', max(1, int(cfg.get('iters', 1))))),
        adapter_file=str(adapter_dir / 'adapters.safetensors'),
        max_seq_length=int(cfg.get('max_seq_len', 1024)),
        grad_checkpoint=bool(cfg.get('grad_checkpoint', False)),
        grad_accumulation_steps=int(cfg.get('gradient_accumulation_steps', 8)),
    )
    train_set = CacheDataset(WeightedDataset(train_records, tokenizer))
    valid_set = CacheDataset(WeightedDataset(valid_records, tokenizer)) if valid_records else None
    tuner_train(
        model=model,
        optimizer=optimizer,
        train_dataset=train_set,
        val_dataset=valid_set,
        args=training_args,
        loss=weighted_loss,
        iterate_batches=iterate_weighted_batches,
        training_callback=callback,
    )
    result = {
        'status': 'completed',
        'created_at': utc_now(),
        'metrics_path': str(metrics_path),
        'adapter_dir': str(adapter_dir),
        'final_train_loss': callback.last_train_loss,
        'final_val_loss': callback.last_val_loss,
        'peak_memory_gb': callback.peak_memory,
    }
    save_json_v4(output_dir / f'{output_dir.name}_result.json', result)
    return result


def build_preference_records_v4(frame: pd.DataFrame) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in frame.to_dict(orient='records'):
        prompt = normalize_optional_text(row.get('prompt'))
        chosen = normalize_optional_text(row.get('chosen_output'))
        rejected = normalize_optional_text(row.get('rejected_output'))
        if prompt is None or chosen is None or rejected is None:
            continue
        records.append(
            {
                'prompt': prompt,
                'chosen_output': chosen,
                'rejected_output': rejected,
                'family': normalize_optional_text(row.get('family')) or '',
            }
        )
    return records


def dpo_training_execute_v4(
    *,
    train_pairs: list[dict[str, Any]],
    valid_pairs: list[dict[str, Any]],
    cfg: dict[str, Any],
    base_model: str,
    output_dir: Path,
    adapter_dir: Path,
    metrics_path: Path,
    init_adapter_path: Path | None,
) -> dict[str, Any]:
    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
    import numpy as np
    from mlx_lm import load as mlx_load
    from mlx_lm.tuner import TrainingArgs, train as tuner_train
    from mlx_lm.tuner.datasets import CacheDataset
    from mlx_lm.tuner.utils import linear_to_lora_layers, load_adapters, print_trainable_parameters
    from mlx_lm.utils import save_config

    class MetricsCallback:
        def __init__(self) -> None:
            self.last_train_loss: float | None = None
            self.last_val_loss: float | None = None
            self.peak_memory: float | None = None

        def on_train_loss_report(self, payload: dict[str, Any]) -> None:
            self.last_train_loss = float(payload.get('train_loss')) if payload.get('train_loss') is not None else None
            self.peak_memory = float(payload.get('peak_memory')) if payload.get('peak_memory') is not None else self.peak_memory
            append_jsonl(metrics_path, {'kind': 'train', 'created_at': utc_now(), **payload})

        def on_val_loss_report(self, payload: dict[str, Any]) -> None:
            self.last_val_loss = float(payload.get('val_loss')) if payload.get('val_loss') is not None else None
            append_jsonl(metrics_path, {'kind': 'val', 'created_at': utc_now(), **payload})

    class PreferenceDataset:
        def __init__(self, data: list[dict[str, Any]], tokenizer: Any) -> None:
            self._data = data
            self.tokenizer = tokenizer

        def __getitem__(self, index: int) -> dict[str, Any]:
            return self._data[index]

        def __len__(self) -> int:
            return len(self._data)

        def process(self, datum: dict[str, Any]) -> tuple[list[int], int, list[int], int]:
            prompt = build_training_prompt(str(datum['prompt']))
            chosen = str(datum['chosen_output'])
            rejected = str(datum['rejected_output'])
            prompt_messages = [{'role': 'user', 'content': prompt}]
            chosen_messages = prompt_messages + [{'role': 'assistant', 'content': chosen}]
            rejected_messages = prompt_messages + [{'role': 'assistant', 'content': rejected}]
            prompt_offset = len(self.tokenizer.apply_chat_template(prompt_messages, add_generation_prompt=True, return_dict=False))
            chosen_tokens = list(self.tokenizer.apply_chat_template(chosen_messages, return_dict=False))
            rejected_tokens = list(self.tokenizer.apply_chat_template(rejected_messages, return_dict=False))
            return chosen_tokens, prompt_offset, rejected_tokens, prompt_offset

    def iterate_preference_batches(dataset: Any, batch_size: int, max_seq_length: int, loop: bool = False, seed: int | None = None, comm_group: Any = None):
        idx = sorted(range(len(dataset)), key=lambda sample_index: max(len(dataset[sample_index][0]), len(dataset[sample_index][2])))
        if len(dataset) < batch_size:
            raise ValueError(f'Dataset must have at least batch_size={batch_size} examples but only has {len(dataset)}.')
        if comm_group is not None:
            offset = comm_group.rank()
            step = comm_group.size()
        else:
            offset = 0
            step = 1
        if batch_size % step != 0:
            raise ValueError('The batch size must be divisible by the number of workers')
        batch_idx = [idx[i + offset : i + offset + batch_size : step] for i in range(0, len(idx) - batch_size + 1, batch_size)]
        if seed is not None:
            np.random.seed(seed)
        while True:
            indices = np.random.permutation(len(batch_idx))
            for batch_index in indices:
                batch = [dataset[item_index] for item_index in batch_idx[batch_index]]
                chosen_tokens, chosen_offsets, rejected_tokens, rejected_offsets = zip(*batch)
                chosen_lengths = [len(tokens) for tokens in chosen_tokens]
                rejected_lengths = [len(tokens) for tokens in rejected_tokens]
                pad_to = 32
                chosen_max = min(1 + pad_to * ((max(chosen_lengths) + pad_to - 1) // pad_to), max_seq_length)
                rejected_max = min(1 + pad_to * ((max(rejected_lengths) + pad_to - 1) // pad_to), max_seq_length)
                chosen_arr = np.zeros((batch_size // step, chosen_max), np.int32)
                rejected_arr = np.zeros((batch_size // step, rejected_max), np.int32)
                chosen_len_rows: list[tuple[int, int]] = []
                rejected_len_rows: list[tuple[int, int]] = []
                for row_index in range(batch_size // step):
                    chosen_trunc = min(chosen_lengths[row_index], max_seq_length)
                    rejected_trunc = min(rejected_lengths[row_index], max_seq_length)
                    chosen_arr[row_index, :chosen_trunc] = chosen_tokens[row_index][:chosen_trunc]
                    rejected_arr[row_index, :rejected_trunc] = rejected_tokens[row_index][:rejected_trunc]
                    chosen_len_rows.append((int(chosen_offsets[row_index]), chosen_trunc))
                    rejected_len_rows.append((int(rejected_offsets[row_index]), rejected_trunc))
                yield mx.array(chosen_arr), mx.array(chosen_len_rows), mx.array(rejected_arr), mx.array(rejected_len_rows)
            if not loop:
                break

    def sequence_logp(model: Any, batch: Any, lengths: Any) -> Any:
        inputs = batch[:, :-1]
        targets = batch[:, 1:]
        logits = model(inputs)
        steps = mx.arange(1, targets.shape[1] + 1)
        mask = mx.logical_and(steps >= lengths[:, 0:1], steps <= lengths[:, 1:]).astype(mx.float32)
        token_nll = nn.losses.cross_entropy(logits, targets).astype(mx.float32)
        return -(token_nll * mask).sum(axis=1)

    policy_model, tokenizer = mlx_load(base_model)
    policy_model.freeze()
    if init_adapter_path is not None:
        load_adapters(policy_model, str(init_adapter_path))
        adapter_config = load_adapter_config_v4(init_adapter_path)
    else:
        linear_to_lora_layers(
            policy_model,
            int(cfg.get('num_layers', 16)),
            {
                'rank': int(cfg.get('lora_r', 32)),
                'dropout': float(cfg.get('lora_dropout', 0.0)),
                'scale': float(cfg.get('lora_alpha', 32)),
            },
        )
        adapter_config = {}
    reference_model, _ = mlx_load(base_model)
    reference_model.freeze()
    if init_adapter_path is not None:
        load_adapters(reference_model, str(init_adapter_path))
    print_trainable_parameters(policy_model)
    adapter_dir.mkdir(parents=True, exist_ok=True)
    save_config(
        {
            'base_model_name_or_path': base_model,
            'fine_tune_type': adapter_config.get('fine_tune_type', 'lora'),
            'num_layers': int(adapter_config.get('num_layers', cfg.get('num_layers', 16))),
            'lora_parameters': adapter_config.get(
                'lora_parameters',
                {
                    'rank': int(cfg.get('lora_r', 32)),
                    'dropout': float(cfg.get('lora_dropout', 0.0)),
                    'scale': float(cfg.get('lora_alpha', 32)),
                },
            ),
            'target_modules': list(adapter_config.get('target_modules', cfg.get('target_modules', []))),
            'preference_mode': 'dpo',
            'dpo_beta': float(cfg.get('dpo_beta', 0.1)),
            'parent_adapter_path': str(init_adapter_path) if init_adapter_path is not None else '',
        },
        adapter_dir / 'adapter_config.json',
    )
    beta = float(cfg.get('dpo_beta', 0.1))

    def dpo_loss(model: Any, chosen_batch: Any, chosen_lengths: Any, rejected_batch: Any, rejected_lengths: Any) -> tuple[Any, Any]:
        pi_chosen = sequence_logp(model, chosen_batch, chosen_lengths)
        pi_rejected = sequence_logp(model, rejected_batch, rejected_lengths)
        ref_chosen = mx.stop_gradient(sequence_logp(reference_model, chosen_batch, chosen_lengths))
        ref_rejected = mx.stop_gradient(sequence_logp(reference_model, rejected_batch, rejected_lengths))
        logits = beta * ((pi_chosen - pi_rejected) - (ref_chosen - ref_rejected))
        loss = mx.logaddexp(mx.zeros_like(logits), -logits).mean()
        return loss, mx.array(float(logits.shape[0]))

    optimizer = optim.Adam(learning_rate=float(cfg.get('learning_rate', 2e-5)))
    training_args = TrainingArgs(
        batch_size=int(cfg.get('per_device_train_batch_size', 1)),
        iters=int(cfg.get('iters', 1)),
        val_batches=int(cfg.get('val_batches', -1)),
        steps_per_report=int(cfg.get('steps_per_report', 1)),
        steps_per_eval=int(cfg.get('steps_per_eval', max(1, int(cfg.get('iters', 1)) // 2))),
        steps_per_save=int(cfg.get('save_every', max(1, int(cfg.get('iters', 1))))),
        adapter_file=str(adapter_dir / 'adapters.safetensors'),
        max_seq_length=int(cfg.get('max_seq_len', 1024)),
        grad_checkpoint=bool(cfg.get('grad_checkpoint', False)),
        grad_accumulation_steps=int(cfg.get('gradient_accumulation_steps', 4)),
    )
    train_set = CacheDataset(PreferenceDataset(train_pairs, tokenizer))
    valid_set = CacheDataset(PreferenceDataset(valid_pairs, tokenizer)) if valid_pairs else None
    callback = MetricsCallback()
    tuner_train(
        model=policy_model,
        optimizer=optimizer,
        train_dataset=train_set,
        val_dataset=valid_set,
        args=training_args,
        loss=dpo_loss,
        iterate_batches=iterate_preference_batches,
        training_callback=callback,
    )
    result = {
        'status': 'completed',
        'created_at': utc_now(),
        'metrics_path': str(metrics_path),
        'adapter_dir': str(adapter_dir),
        'final_train_loss': callback.last_train_loss,
        'final_val_loss': callback.last_val_loss,
        'peak_memory_gb': callback.peak_memory,
    }
    save_json_v4(output_dir / f'{output_dir.name}_result.json', result)
    return result


def prepare_training_manifest_v4(
    *,
    version: str,
    candidate_id: str,
    recipe_type: str,
    config_name: str,
    base_model: str,
    data_path: Path,
    train_records: int,
    valid_records: int,
    split_strategy: str,
    cfg: dict[str, Any],
    adapter_dir: Path,
    metrics_path: Path,
    parent_candidate_id: str | None,
) -> dict[str, Any]:
    return {
        'version': version,
        'created_at': utc_now(),
        'candidate_id': candidate_id,
        'parent_candidate_id': parent_candidate_id,
        'recipe_type': recipe_type,
        'config_name': config_name,
        'model': {'base_model': base_model},
        'data': {
            'train_pack_path': str(data_path),
            'train_records': train_records,
            'valid_records': valid_records,
            'split_strategy': split_strategy,
        },
        'training': {
            'learning_rate': float(cfg.get('learning_rate', 1e-4)),
            'num_epochs': float(cfg.get('num_epochs', 1.0)),
            'max_seq_len': int(cfg.get('max_seq_len', 1024)),
            'per_device_train_batch_size': int(cfg.get('per_device_train_batch_size', 1)),
            'gradient_accumulation_steps': int(cfg.get('gradient_accumulation_steps', 4)),
            'iters': int(cfg.get('iters', 1)),
        },
        'execution': {'adapter_dir': str(adapter_dir), 'metrics_path': str(metrics_path)},
    }


def run_train_stage_c_rft_v4(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    config_name = str(cfg.get('name', Path(args.config_path).stem))
    train_pack_path = _require_existing_path(getattr(args, 'train_pack_path', None) or cfg.get('train_pack_path', DEFAULT_V4_STAGE_C_RFT_OUTPUT_PATH), label='stage c rft mix parquet')
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate_id = getattr(args, 'candidate_id', None) or f'v4_rft_{config_name}'
    parent_candidate_id = normalize_optional_text(getattr(args, 'parent_candidate_id', None)) or 'v3_stage_a_baseline'
    manifest_path = output_dir / f'{candidate_id}_manifest.json'
    result_path = output_dir / f'{candidate_id}_result.json'
    adapter_dir = output_dir / f'adapter_{candidate_id}'
    metrics_path = output_dir / f'{candidate_id}_metrics.jsonl'
    init_adapter_path = prepare_parent_adapter_path_v4(cfg, args)
    train_pack_df = pd.read_parquet(train_pack_path)
    seed = int(cfg.get('seed', 0))
    train_df, valid_df, split_strategy = split_training_frame(train_pack_df, valid_fold=int(args.valid_fold), valid_fraction=float(args.valid_fraction), seed=seed)
    train_df = maybe_limit_rows(train_df, max_rows=args.max_train_rows, seed=seed)
    valid_df = maybe_limit_rows(valid_df, max_rows=args.max_valid_rows, seed=seed)
    train_records, skipped_train = build_training_records(train_df)
    valid_records, skipped_valid = build_training_records(valid_df)
    effective_train_rows = max(len(train_records), 1)
    cfg['iters'] = max(1, int(effective_train_rows * float(cfg.get('num_epochs', 1.0)) // max(int(cfg.get('per_device_train_batch_size', 1)), 1)))
    base_model = resolve_training_base_model(cfg.get('base_model'), load_active_model_manifest_v4())
    manifest = prepare_training_manifest_v4(
        version='v4',
        candidate_id=candidate_id,
        recipe_type='stage_c_rft',
        config_name=config_name,
        base_model=base_model,
        data_path=train_pack_path,
        train_records=len(train_records),
        valid_records=len(valid_records),
        split_strategy=split_strategy,
        cfg=cfg,
        adapter_dir=adapter_dir,
        metrics_path=metrics_path,
        parent_candidate_id=parent_candidate_id,
    )
    manifest['data']['skipped_rows'] = skipped_train + skipped_valid
    save_json_v4(manifest_path, manifest)
    try:
        if not args.execute or str(cfg.get('runtime_backend', '')).lower() == 'mock':
            import numpy as np
            from safetensors.numpy import save_file

            adapter_dir.mkdir(parents=True, exist_ok=True)
            save_file({'layers.0.q_proj.lora_a': np.zeros((2, 2), dtype=np.float32)}, str(adapter_dir / 'adapters.safetensors'))
            save_json_v4(
                adapter_dir / 'adapter_config.json',
                {
                    'base_model_name_or_path': base_model,
                    'target_modules': list(cfg.get('target_modules', [])),
                    'r': int(cfg.get('lora_r', 32)),
                    'parent_adapter_path': str(init_adapter_path) if init_adapter_path is not None else '',
                },
            )
            result = {
                'status': 'completed' if args.execute else 'rendered_only',
                'created_at': utc_now(),
                'metrics_path': str(metrics_path),
                'adapter_dir': str(adapter_dir),
                'final_train_loss': 0.0,
                'final_val_loss': 0.0,
                'peak_memory_gb': 0.0,
            }
        else:
            result = weighted_training_execute_v4(
                train_records=train_records,
                valid_records=valid_records,
                cfg=cfg,
                base_model=base_model,
                output_dir=output_dir,
                adapter_dir=adapter_dir,
                metrics_path=metrics_path,
                init_adapter_path=init_adapter_path,
            )
    except Exception as exc:
        result = {
            'status': 'failed',
            'created_at': utc_now(),
            'error_type': type(exc).__name__,
            'error_message': str(exc),
            'metrics_path': str(metrics_path),
            'adapter_dir': str(adapter_dir),
        }
        save_json_v4(result_path, result)
        append_experiment_log('train_stage_c_rft_v4', 'failed', candidate_id=candidate_id, error=f'{type(exc).__name__}:{exc}')
        raise
    save_json_v4(result_path, result)
    upsert_csv_row(
        Path(DEFAULT_V4_CANDIDATE_REGISTRY_OUTPUT_PATH),
        [
            'candidate_id',
            'parent_candidate_id',
            'candidate_kind',
            'manifest_path',
            'adapter_path',
            'runtime_lane',
            'stage',
            'recipe_type',
            'pair_kind',
            'train_pack_path',
            'overall_acc',
            'hard_shadow_acc',
            'format_fail_rate',
            'extraction_fail_rate',
            'submit_value',
            'cuda_repro_pass',
            'packaging_pass',
            'selected_for_submit',
            'status',
            'failure_reason',
            'notes',
            'recorded_at',
        ],
        ['candidate_id'],
        {
            'candidate_id': candidate_id,
            'parent_candidate_id': parent_candidate_id,
            'candidate_kind': 'adapter',
            'manifest_path': str(manifest_path),
            'adapter_path': str(adapter_dir),
            'runtime_lane': 'mac_mlx',
            'stage': 'c',
            'recipe_type': 'stage_c_rft',
            'pair_kind': '',
            'train_pack_path': str(train_pack_path),
            'overall_acc': '',
            'hard_shadow_acc': '',
            'format_fail_rate': '',
            'extraction_fail_rate': '',
            'submit_value': False,
            'cuda_repro_pass': False,
            'packaging_pass': False,
            'selected_for_submit': False,
            'status': result.get('status', 'completed'),
            'failure_reason': result.get('error_message', ''),
            'notes': normalize_optional_text(cfg.get('notes')) or '',
            'recorded_at': utc_now(),
        },
    )
    append_experiment_log('train_stage_c_rft_v4', result.get('status', 'completed'), candidate_id=candidate_id, manifest_path=str(manifest_path), result_path=str(result_path))
    print(json.dumps({'candidate_id': candidate_id, 'manifest_path': str(manifest_path), 'result_path': str(result_path), 'adapter_dir': str(adapter_dir)}, ensure_ascii=False, indent=2))


def run_train_stage_c_preference_v4(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    config_name = str(cfg.get('name', Path(args.config_path).stem))
    pair_data_path = _require_existing_path(getattr(args, 'pair_data_path', None) or cfg.get('pair_data_path', DEFAULT_V4_STAGE_C_PREFERENCE_OUTPUT_PATH), label='stage c preference mix parquet')
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate_id = getattr(args, 'candidate_id', None) or f'v4_pref_{config_name}'
    parent_candidate_id = normalize_optional_text(getattr(args, 'parent_candidate_id', None)) or 'v3_stage_a_baseline'
    manifest_path = output_dir / f'{candidate_id}_manifest.json'
    result_path = output_dir / f'{candidate_id}_result.json'
    adapter_dir = output_dir / f'adapter_{candidate_id}'
    metrics_path = output_dir / f'{candidate_id}_metrics.jsonl'
    init_adapter_path = prepare_parent_adapter_path_v4(cfg, args)
    pair_df = pd.read_parquet(pair_data_path)
    pair_kind = normalize_optional_text(getattr(args, 'pair_kind', None)) or normalize_optional_text(cfg.get('pair_kind'))
    if pair_kind is not None and 'pair_kind' in pair_df.columns:
        pair_df = pair_df.loc[pair_df['pair_kind'].astype(str) == pair_kind].copy()
    family_filter = list(getattr(args, 'family_filter', []) or cfg.get('family_filter', []))
    if family_filter:
        family_set = {str(item) for item in family_filter}
        pair_df = pair_df.loc[pair_df['family'].astype(str).isin(family_set)].copy()
    max_train_pairs = cfg.get('max_train_pairs')
    if max_train_pairs is not None:
        pair_df = maybe_limit_rows(pair_df, max_rows=int(max_train_pairs), seed=int(cfg.get('seed', 0)))
    train_df, valid_df, split_strategy = split_training_frame(pair_df, valid_fold=int(args.valid_fold), valid_fraction=float(args.valid_fraction), seed=int(cfg.get('seed', 0)))
    train_pairs = build_preference_records_v4(train_df)
    valid_pairs = build_preference_records_v4(valid_df)
    effective_train_rows = max(len(train_pairs), 1)
    cfg['iters'] = max(1, int(effective_train_rows * float(cfg.get('num_epochs', 1.0)) // max(int(cfg.get('per_device_train_batch_size', 1)), 1)))
    base_model = resolve_training_base_model(cfg.get('base_model'), load_active_model_manifest_v4())
    manifest = prepare_training_manifest_v4(
        version='v4',
        candidate_id=candidate_id,
        recipe_type='preference_dpo',
        config_name=config_name,
        base_model=base_model,
        data_path=pair_data_path,
        train_records=len(train_pairs),
        valid_records=len(valid_pairs),
        split_strategy=split_strategy,
        cfg=cfg,
        adapter_dir=adapter_dir,
        metrics_path=metrics_path,
        parent_candidate_id=parent_candidate_id,
    )
    manifest['pair_kind'] = pair_kind or ''
    save_json_v4(manifest_path, manifest)
    try:
        if not args.execute or str(cfg.get('runtime_backend', '')).lower() == 'mock':
            import numpy as np
            from safetensors.numpy import save_file

            adapter_dir.mkdir(parents=True, exist_ok=True)
            save_file({'layers.0.q_proj.lora_a': np.ones((2, 2), dtype=np.float32)}, str(adapter_dir / 'adapters.safetensors'))
            save_json_v4(
                adapter_dir / 'adapter_config.json',
                {
                    'base_model_name_or_path': base_model,
                    'r': 32,
                    'target_modules': list(cfg.get('target_modules', [])),
                    'preference_mode': 'dpo',
                },
            )
            result = {
                'status': 'completed' if args.execute else 'rendered_only',
                'created_at': utc_now(),
                'metrics_path': str(metrics_path),
                'adapter_dir': str(adapter_dir),
                'final_train_loss': 0.0,
                'final_val_loss': 0.0,
                'peak_memory_gb': 0.0,
            }
        else:
            result = dpo_training_execute_v4(
                train_pairs=train_pairs,
                valid_pairs=valid_pairs,
                cfg=cfg,
                base_model=base_model,
                output_dir=output_dir,
                adapter_dir=adapter_dir,
                metrics_path=metrics_path,
                init_adapter_path=init_adapter_path,
            )
    except Exception as exc:
        result = {
            'status': 'failed',
            'created_at': utc_now(),
            'error_type': type(exc).__name__,
            'error_message': str(exc),
            'metrics_path': str(metrics_path),
            'adapter_dir': str(adapter_dir),
        }
        save_json_v4(result_path, result)
        append_experiment_log('train_stage_c_preference_v4', 'failed', candidate_id=candidate_id, error=f'{type(exc).__name__}:{exc}')
        raise
    save_json_v4(result_path, result)
    upsert_csv_row(
        Path(DEFAULT_V4_CANDIDATE_REGISTRY_OUTPUT_PATH),
        [
            'candidate_id',
            'parent_candidate_id',
            'candidate_kind',
            'manifest_path',
            'adapter_path',
            'runtime_lane',
            'stage',
            'recipe_type',
            'pair_kind',
            'train_pack_path',
            'overall_acc',
            'hard_shadow_acc',
            'format_fail_rate',
            'extraction_fail_rate',
            'submit_value',
            'cuda_repro_pass',
            'packaging_pass',
            'selected_for_submit',
            'status',
            'failure_reason',
            'notes',
            'recorded_at',
        ],
        ['candidate_id'],
        {
            'candidate_id': candidate_id,
            'parent_candidate_id': parent_candidate_id,
            'candidate_kind': 'adapter',
            'manifest_path': str(manifest_path),
            'adapter_path': str(adapter_dir),
            'runtime_lane': 'mac_mlx',
            'stage': 'c',
            'recipe_type': 'preference_dpo',
            'pair_kind': pair_kind or '',
            'train_pack_path': str(pair_data_path),
            'overall_acc': '',
            'hard_shadow_acc': '',
            'format_fail_rate': '',
            'extraction_fail_rate': '',
            'submit_value': False,
            'cuda_repro_pass': False,
            'packaging_pass': False,
            'selected_for_submit': False,
            'status': result.get('status', 'completed'),
            'failure_reason': result.get('error_message', ''),
            'notes': normalize_optional_text(cfg.get('notes')) or '',
            'recorded_at': utc_now(),
        },
    )
    append_experiment_log('train_stage_c_preference_v4', result.get('status', 'completed'), candidate_id=candidate_id, manifest_path=str(manifest_path), result_path=str(result_path), pair_kind=pair_kind)
    print(json.dumps({'candidate_id': candidate_id, 'manifest_path': str(manifest_path), 'result_path': str(result_path), 'adapter_dir': str(adapter_dir)}, ensure_ascii=False, indent=2))


def run_train_specialist_v4(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    specialist_tag = normalize_optional_text(cfg.get('specialist_tag')) or normalize_optional_text(getattr(args, 'specialist_tag', None)) or 'specialist'
    candidate_id = getattr(args, 'candidate_id', None) or f'v4_{specialist_tag}_specialist'
    run_train_stage_c_preference_v4(
        argparse.Namespace(
            config_path=args.config_path,
            pair_data_path=getattr(args, 'pair_data_path', None),
            output_dir=args.output_dir,
            candidate_id=candidate_id,
            parent_candidate_id=getattr(args, 'parent_candidate_id', None) or 'v3_stage_a_baseline',
            init_adapter_path=getattr(args, 'init_adapter_path', None),
            pair_kind=getattr(args, 'pair_kind', None) or cfg.get('pair_kind'),
            family_filter=getattr(args, 'family_filter', None) or cfg.get('family_filter', []),
            valid_fold=args.valid_fold,
            valid_fraction=args.valid_fraction,
            execute=args.execute,
        )
    )
    upsert_csv_row(
        Path(DEFAULT_V4_SPECIALIST_REGISTRY_OUTPUT_PATH),
        ['candidate_id', 'specialist_tag', 'parent_candidate_id', 'manifest_path', 'adapter_path', 'status', 'notes', 'recorded_at'],
        ['candidate_id'],
        {
            'candidate_id': candidate_id,
            'specialist_tag': specialist_tag,
            'parent_candidate_id': getattr(args, 'parent_candidate_id', None) or 'v3_stage_a_baseline',
            'manifest_path': str(Path(args.output_dir) / f'{candidate_id}_manifest.json'),
            'adapter_path': str(Path(args.output_dir) / f'adapter_{candidate_id}'),
            'status': 'completed',
            'notes': normalize_optional_text(cfg.get('notes')) or '',
            'recorded_at': utc_now(),
        },
    )


def load_adapter_tensors_v4(adapter_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    from safetensors.numpy import load_file

    return load_adapter_config_v4(adapter_dir), load_file(str(adapter_dir / 'adapters.safetensors'))


def run_merge_candidates_v4(args: argparse.Namespace) -> None:
    import numpy as np
    from safetensors.numpy import save_file

    cfg = _load_yaml_config(args.config_path)
    generalist = resolve_candidate_spec_v4(
        manifest_path=getattr(args, 'generalist_manifest_path', None),
        adapter_path=getattr(args, 'generalist_adapter_path', None),
        candidate_id=getattr(args, 'generalist_candidate_id', None),
    )
    specialist = resolve_candidate_spec_v4(
        manifest_path=getattr(args, 'specialist_manifest_path', None),
        adapter_path=getattr(args, 'specialist_adapter_path', None),
        candidate_id=getattr(args, 'specialist_candidate_id', None),
    )
    merge_id = getattr(args, 'merge_id', None) or f'merge_{generalist.candidate_id}_{specialist.candidate_id}'
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    adapter_dir = output_dir / f'adapter_{merge_id}'
    adapter_dir.mkdir(parents=True, exist_ok=True)
    generalist_weight = float(cfg.get('weights', {}).get('generalist', 0.75))
    specialist_weight = float(cfg.get('weights', {}).get('specialist', 0.25))
    generalist_config, generalist_tensors = load_adapter_tensors_v4(_require_existing_path(generalist.adapter_path, label='generalist adapter dir'))
    _, specialist_tensors = load_adapter_tensors_v4(_require_existing_path(specialist.adapter_path, label='specialist adapter dir'))
    merged_tensors: dict[str, Any] = {}
    for key, tensor in generalist_tensors.items():
        specialist_value = specialist_tensors.get(key)
        if specialist_value is None:
            merged_tensors[key] = tensor
            continue
        merged_value = generalist_weight * tensor.astype(np.float32) + specialist_weight * specialist_value.astype(np.float32)
        merged_tensors[key] = merged_value.astype(tensor.dtype)
    save_file(merged_tensors, str(adapter_dir / 'adapters.safetensors'))
    merged_config = dict(generalist_config)
    merged_config['merge_sources'] = [generalist.candidate_id, specialist.candidate_id]
    merged_config['merge_weights'] = {'generalist': generalist_weight, 'specialist': specialist_weight}
    (adapter_dir / 'adapter_config.json').write_text(json.dumps(merged_config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    manifest_path = output_dir / f'{merge_id}_manifest.json'
    save_json_v4(
        manifest_path,
        {
            'version': 'v4',
            'created_at': utc_now(),
            'candidate_id': merge_id,
            'parent_candidate_id': generalist.candidate_id,
            'recipe_type': 'merge',
            'config_name': 'linear_adapter_average',
            'model': {'base_model': generalist.base_model},
            'merge': {
                'generalist_candidate_id': generalist.candidate_id,
                'specialist_candidate_id': specialist.candidate_id,
                'merge_weights': {'generalist': generalist_weight, 'specialist': specialist_weight},
            },
            'execution': {'adapter_dir': str(adapter_dir)},
        },
    )
    upsert_csv_row(
        Path(DEFAULT_V4_MERGE_REGISTRY_OUTPUT_PATH),
        ['merge_id', 'generalist_candidate_id', 'specialist_candidate_id', 'merge_weights', 'manifest_path', 'adapter_path', 'compression_method', 'rank_after_compression', 'quick_score', 'serious_score', 'status', 'notes', 'recorded_at'],
        ['merge_id'],
        {
            'merge_id': merge_id,
            'generalist_candidate_id': generalist.candidate_id,
            'specialist_candidate_id': specialist.candidate_id,
            'merge_weights': json.dumps({'generalist': generalist_weight, 'specialist': specialist_weight}, ensure_ascii=False),
            'manifest_path': str(manifest_path),
            'adapter_path': str(adapter_dir),
            'compression_method': 'not_yet_compressed',
            'rank_after_compression': int(merged_config.get('r', merged_config.get('lora_parameters', {}).get('rank', 32))),
            'quick_score': '',
            'serious_score': '',
            'status': 'merged',
            'notes': '',
            'recorded_at': utc_now(),
        },
    )
    append_experiment_log('merge_candidates_v4', 'completed', merge_id=merge_id, generalist=generalist.candidate_id, specialist=specialist.candidate_id, manifest_path=str(manifest_path))
    print(json.dumps({'merge_id': merge_id, 'manifest_path': str(manifest_path), 'adapter_dir': str(adapter_dir)}, ensure_ascii=False, indent=2))


def run_compress_merge_rank32_v4(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    source_adapter = _require_existing_path(args.adapter_path, label='merged adapter directory')
    output_dir = Path(args.output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        shutil.rmtree(output_dir)
    shutil.copytree(source_adapter, output_dir)
    adapter_config = load_adapter_config_v4(output_dir)
    rank = int(adapter_config.get('r', adapter_config.get('lora_parameters', {}).get('rank', 32)))
    manifest_path = output_dir.parent / f'{output_dir.name}_compress_manifest.json'
    save_json_v4(
        manifest_path,
        {
            'version': 'v4',
            'created_at': utc_now(),
            'compression_method': str(cfg.get('method', 'noop_same_shape_rank32')),
            'rank_cap': int(cfg.get('rank_cap', 32)),
            'rank_after_compression': rank,
            'source_adapter_path': str(source_adapter),
            'output_adapter_path': str(output_dir),
            'noop': rank <= int(cfg.get('rank_cap', 32)),
        },
    )
    append_experiment_log('compress_merge_rank32_v4', 'completed', source_adapter=str(source_adapter), output_adapter=str(output_dir), rank_after_compression=rank)
    print(json.dumps({'output_adapter_path': str(output_dir), 'rank_after_compression': rank}, ensure_ascii=False, indent=2))


def run_render_cuda_repro_spec_v4(args: argparse.Namespace) -> None:
    cfg = _load_yaml_config(args.config_path)
    candidate = resolve_candidate_spec_v4(
        manifest_path=getattr(args, 'manifest_path', None),
        adapter_path=getattr(args, 'adapter_path', None),
        candidate_id=getattr(args, 'candidate_id', None),
    )
    spec = {
        'version': 'v4',
        'created_at': utc_now(),
        'candidate_id': candidate.candidate_id,
        'manual_cuda_execution_required': True,
        'base_model_name_or_path': str(cfg.get('base_model_name_or_path', DEFAULT_SUBMISSION_BASE_MODEL)),
        'mac_manifest_path': str(candidate.manifest_path) if candidate.manifest_path else '',
        'mac_adapter_path': str(candidate.adapter_path) if candidate.adapter_path else '',
        'parent_candidate_id': candidate.parent_candidate_id or '',
        'precision': str(cfg.get('precision', 'bf16')),
        'notes': 'Render only. Submit only if local score gate is satisfied.',
    }
    output_path = Path(args.output_path or DEFAULT_V4_CUDA_REPRO_SPEC_OUTPUT_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding='utf-8')
    manual_command_path = output_path.with_suffix('.sh')
    manual_command_path.write_text(
        '# Manual CUDA/BF16 reproduction\n'
        f'# Candidate: {candidate.candidate_id}\n'
        f'# Spec: {output_path}\n',
        encoding='utf-8',
    )
    append_csv_row(
        Path(args.registry_path or DEFAULT_V4_CUDA_REPRO_REGISTRY_OUTPUT_PATH),
        ['candidate_id', 'spec_path', 'status', 'manual_command_path', 'created_at', 'notes'],
        {
            'candidate_id': candidate.candidate_id,
            'spec_path': str(output_path),
            'status': 'rendered',
            'manual_command_path': str(manual_command_path),
            'created_at': utc_now(),
            'notes': 'Awaiting local score gate and manual CUDA execution.',
        },
    )
    save_json_v4(
        Path(args.submission_manifest_path or DEFAULT_V4_SUBMISSION_MANIFEST_OUTPUT_PATH),
        {
            'version': 'v4',
            'created_at': utc_now(),
            'candidate_id': candidate.candidate_id,
            'status': 'pending_local_gate',
            'cuda_spec_path': str(output_path),
            'adapter_path': str(candidate.adapter_path) if candidate.adapter_path else '',
        },
    )
    append_experiment_log('render_cuda_repro_spec_v4', 'completed', candidate_id=candidate.candidate_id, spec_path=str(output_path))
    print(json.dumps({'candidate_id': candidate.candidate_id, 'output_path': str(output_path), 'manual_command_path': str(manual_command_path)}, ensure_ascii=False, indent=2))


def run_package_peft_v4(args: argparse.Namespace) -> None:
    run_package_peft(args)
    append_experiment_log('package_peft_v4', 'completed', adapter_dir=str(args.adapter_dir), output_dir=str(args.output_dir))


def run_write_runbook_v4(args: argparse.Namespace) -> None:
    candidate_registry_path = Path(args.candidate_registry_path or DEFAULT_V4_CANDIDATE_REGISTRY_OUTPUT_PATH)
    ensure_csv_header(
        candidate_registry_path,
        [
            'candidate_id',
            'parent_candidate_id',
            'candidate_kind',
            'manifest_path',
            'adapter_path',
            'runtime_lane',
            'stage',
            'recipe_type',
            'pair_kind',
            'train_pack_path',
            'overall_acc',
            'hard_shadow_acc',
            'format_fail_rate',
            'extraction_fail_rate',
            'submit_value',
            'cuda_repro_pass',
            'packaging_pass',
            'selected_for_submit',
            'status',
            'failure_reason',
            'notes',
            'recorded_at',
        ],
    )
    promotion_rules_path = Path(args.promotion_rules_path or DEFAULT_V4_PROMOTION_RULES_OUTPUT_PATH)
    promotion_rules_path.parent.mkdir(parents=True, exist_ok=True)
    promotion_rules_path.write_text(
        '# V4 Promotion / Submit Queue Rules\n'
        '- local overall best update -> queue\n'
        '- hard split / bit / text / symbol improvement -> queue\n'
        '- format fail or extraction fail reduction -> queue\n'
        '- no meaningful local gain -> do not submit\n'
        '- packaging smoke and CUDA handoff must both be clean before selected_for_submit=true\n',
        encoding='utf-8',
    )
    output_path = Path(args.output_path or DEFAULT_V4_TRAINING_RUNBOOK_OUTPUT_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        f'# V4 Training Command Book\n# Generated at {utc_now()}\n\n'
        'uv run python versions/v4/code/train.py bootstrap-v4\n'
        'uv run python versions/v4/code/train.py score-candidate --config-path versions/v4/conf/eval/candidate_score_serious.yaml --candidate-id v3_stage_a_baseline\n'
        'uv run python versions/v4/code/train.py build-format-preferences --config-path versions/v4/conf/data/preference_format.yaml\n'
        'uv run python versions/v4/code/train.py build-correctness-preferences --config-path versions/v4/conf/data/preference_correctness.yaml\n'
        'uv run python versions/v4/code/train.py build-rft-candidates --config-path versions/v4/conf/data/rft_accept_pool.yaml --candidate-id v3_stage_a_baseline\n'
        'uv run python versions/v4/code/train.py filter-rft-accept-pool --config-path versions/v4/conf/data/rft_accept_pool.yaml\n'
        'uv run python versions/v4/code/train.py build-stage-c-mix --rft-config-path versions/v4/conf/data/stage_c_rft_mix.yaml --preference-config-path versions/v4/conf/data/stage_c_preference_mix.yaml\n'
        'uv run python versions/v4/code/train.py train-stage-c-rft --config-path versions/v4/conf/train/rft_stage_c_mlx.yaml --output-dir versions/v4/outputs/train/rft_stage_c_run1 --execute\n'
        'uv run python versions/v4/code/train.py train-stage-c-preference --config-path versions/v4/conf/train/dpo_format_mlx.yaml --output-dir versions/v4/outputs/train/format_pref_run1 --execute\n'
        'uv run python versions/v4/code/train.py merge-candidates --config-path versions/v4/conf/merge/generalist_specialist_merge.yaml --generalist-manifest-path <manifest> --specialist-manifest-path <manifest> --output-dir versions/v4/outputs/train/merge_run1\n'
        'uv run python versions/v4/code/train.py render-cuda-repro-spec --config-path versions/v4/conf/train/stage_c_cuda_bf16.yaml --candidate-id <best_candidate>\n',
        encoding='utf-8',
    )
    append_experiment_log('write_runbook_v4', 'completed', candidate_registry_path=str(candidate_registry_path), promotion_rules_path=str(promotion_rules_path), output_path=str(output_path))
    print(json.dumps({'candidate_registry_path': str(candidate_registry_path), 'promotion_rules_path': str(promotion_rules_path), 'output_path': str(output_path)}, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='v4 Stage C experimentation and CUDA handoff utilities.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    bootstrap_parser = subparsers.add_parser('bootstrap-v4', help='Create the v4 scaffold and default configs.')
    bootstrap_parser.set_defaults(func=run_bootstrap_v4)

    show_parser = subparsers.add_parser(
        'show-active-model',
        help='Print the currently saved active model manifest.',
    )
    show_parser.add_argument('--active-model-path', default=str(DEFAULT_ACTIVE_MODEL_PATH))
    show_parser.set_defaults(func=run_show_active_model)

    teacher_candidate_parser = subparsers.add_parser('build-teacher-trace-candidates', help='Build teacher trace candidate rows from the real canonical table.')
    teacher_candidate_parser.add_argument('--config-path', default=str(DEFAULT_TEACHER_DISTILL_CONFIG_PATH))
    teacher_candidate_parser.add_argument('--input-path', default=str(DEFAULT_V2_REAL_CANONICAL_PATH))
    teacher_candidate_parser.add_argument('--output-path', default=str(DEFAULT_V3_TEACHER_TRACE_CANDIDATES_OUTPUT_PATH))
    teacher_candidate_parser.add_argument('--audit-output-path', default=str(AUDITS_ROOT / 'teacher_trace_candidates_v3.csv'))
    teacher_candidate_parser.add_argument('--max-rows', type=int, default=None)
    teacher_candidate_parser.set_defaults(func=run_build_teacher_trace_candidates)

    teacher_generate_parser = subparsers.add_parser('generate-teacher-traces', help='Run the fixed MLX teacher against candidate prompts.')
    teacher_generate_parser.add_argument('--input-path', default=str(DEFAULT_V3_TEACHER_TRACE_CANDIDATES_OUTPUT_PATH))
    teacher_generate_parser.add_argument('--output-path', default=str(DEFAULT_V3_TEACHER_TRACE_GENERATIONS_OUTPUT_PATH))
    teacher_generate_parser.add_argument('--active-model-path', default=str(DEFAULT_ACTIVE_MODEL_PATH))
    teacher_generate_parser.add_argument('--model-dir', default=None)
    teacher_generate_parser.add_argument('--limit', type=int, default=None)
    teacher_generate_parser.add_argument('--append', action='store_true')
    teacher_generate_parser.add_argument('--max-tokens', type=int, default=192)
    teacher_generate_parser.add_argument('--temp', type=float, default=0.0)
    teacher_generate_parser.add_argument('--top-p', type=float, default=1.0)
    teacher_generate_parser.add_argument('--audit-output-path', default=str(AUDITS_ROOT / 'teacher_trace_generation_v3.csv'))
    teacher_generate_parser.set_defaults(func=run_generate_teacher_traces)

    teacher_filter_parser = subparsers.add_parser('filter-teacher-traces', help='Filter raw teacher generations into strict accepted traces.')
    teacher_filter_parser.add_argument('--input-path', default=str(DEFAULT_V3_TEACHER_TRACE_GENERATIONS_OUTPUT_PATH))
    teacher_filter_parser.add_argument('--registry-path', default=str(DEFAULT_V3_TEACHER_TRACE_REGISTRY_OUTPUT_PATH))
    teacher_filter_parser.add_argument('--output-path', default=str(DEFAULT_V3_DISTILLED_TRACES_OUTPUT_PATH))
    teacher_filter_parser.add_argument('--audit-output-path', default=str(DEFAULT_V3_FORMAT_AUDIT_OUTPUT_PATH))
    teacher_filter_parser.set_defaults(func=run_filter_teacher_traces)

    audit_parser = subparsers.add_parser('audit-format', help='Audit expected and observed format behavior.')
    audit_parser.add_argument('--input-path', default=str(DEFAULT_V3_TEACHER_TRACE_REGISTRY_OUTPUT_PATH))
    audit_parser.add_argument('--real-canonical-path', default=str(DEFAULT_V2_REAL_CANONICAL_PATH))
    audit_parser.add_argument('--teacher-traces-path', default=str(DEFAULT_V3_TEACHER_TRACE_REGISTRY_OUTPUT_PATH))
    audit_parser.add_argument('--text-column', default='raw_output')
    audit_parser.add_argument('--answer-column', default='answer')
    audit_parser.add_argument('--family-column', default='family')
    audit_parser.add_argument('--policy-column', default='boxed_policy')
    audit_parser.add_argument('--output-path', default=str(DEFAULT_V3_FORMAT_AUDIT_OUTPUT_PATH))
    audit_parser.set_defaults(func=run_audit_format)

    format_pairs_parser = subparsers.add_parser(
        'build-format-pairs',
        help='Build strict format preference pairs from real rows and strict traces.',
    )
    format_pairs_parser.add_argument('--real-canonical-path', default=str(DEFAULT_V2_REAL_CANONICAL_PATH))
    format_pairs_parser.add_argument('--teacher-traces-path', default=str(DEFAULT_V3_TEACHER_TRACE_REGISTRY_OUTPUT_PATH))
    format_pairs_parser.add_argument('--config-path', default=str(DEFAULT_V3_FORMAT_POLICY_CONFIG_PATH))
    format_pairs_parser.add_argument('--output-path', default=str(DEFAULT_V3_FORMAT_PAIRS_OUTPUT_PATH))
    format_pairs_parser.add_argument('--audit-output-path', default=str(AUDITS_ROOT / 'format_pairs_v3.csv'))
    format_pairs_parser.set_defaults(func=run_build_format_pairs)

    correction_pairs_parser = subparsers.add_parser(
        'build-correction-pairs',
        help='Build strict correction pairs, using v2 fallback pairs when no student eval is provided.',
    )
    correction_pairs_parser.add_argument('--real-canonical-path', default=str(DEFAULT_V2_REAL_CANONICAL_PATH))
    correction_pairs_parser.add_argument('--teacher-traces-path', default=str(DEFAULT_V3_TEACHER_TRACE_REGISTRY_OUTPUT_PATH))
    correction_pairs_parser.add_argument('--bootstrap-pairs-path', default=str(DEFAULT_V2_CORRECTION_PAIRS_PATH))
    correction_pairs_parser.add_argument('--output-path', default=str(DEFAULT_V3_CORRECTION_PAIRS_OUTPUT_PATH))
    correction_pairs_parser.add_argument('--audit-output-path', default=str(AUDITS_ROOT / 'correction_pairs_v3.csv'))
    correction_pairs_parser.set_defaults(func=run_build_correction_pairs)

    preference_pairs_parser = subparsers.add_parser('build-preference-pairs', help='Build preference pairs for later DPO/ORPO/RFT.')
    preference_pairs_parser.add_argument('--config-path', default=str(DEFAULT_V3_PREFERENCE_CONFIG_PATH))
    preference_pairs_parser.add_argument('--format-pairs-path', default=str(DEFAULT_V3_FORMAT_PAIRS_OUTPUT_PATH))
    preference_pairs_parser.add_argument('--correction-pairs-path', default=str(DEFAULT_V3_CORRECTION_PAIRS_OUTPUT_PATH))
    preference_pairs_parser.add_argument('--teacher-traces-path', default=str(DEFAULT_V3_TEACHER_TRACE_REGISTRY_OUTPUT_PATH))
    preference_pairs_parser.add_argument('--output-path', default=str(DEFAULT_V3_PREFERENCE_PAIRS_OUTPUT_PATH))
    preference_pairs_parser.add_argument('--audit-output-path', default=str(AUDITS_ROOT / 'preference_pairs_v3.csv'))
    preference_pairs_parser.set_defaults(func=run_build_preference_pairs)

    rft_parser = subparsers.add_parser('build-rft-accept-pool', help='Build the accepted-output RFT pool.')
    rft_parser.add_argument('--config-path', default=str(DEFAULT_V3_RFT_CONFIG_PATH))
    rft_parser.add_argument('--teacher-traces-path', default=str(DEFAULT_V3_TEACHER_TRACE_REGISTRY_OUTPUT_PATH))
    rft_parser.add_argument('--output-path', default=str(DEFAULT_V3_RFT_ACCEPT_POOL_OUTPUT_PATH))
    rft_parser.add_argument('--audit-output-path', default=str(AUDITS_ROOT / 'rft_accept_pool_v3.csv'))
    rft_parser.set_defaults(func=run_build_rft_accept_pool)

    train_mix_parser = subparsers.add_parser(
        'build-train-mix',
        help='Build Stage A and Stage B strong train packs with weighted registry.',
    )
    train_mix_parser.add_argument('--real-canonical-path', default=str(DEFAULT_V2_REAL_CANONICAL_PATH))
    train_mix_parser.add_argument('--core-synth-path', default=str(DEFAULT_V2_SYNTH_CORE_PATH))
    train_mix_parser.add_argument('--hard-synth-path', default=str(DEFAULT_V2_SYNTH_HARD_PATH))
    train_mix_parser.add_argument('--distilled-traces-path', default=str(DEFAULT_V3_DISTILLED_TRACES_OUTPUT_PATH))
    train_mix_parser.add_argument('--format-pairs-path', default=str(DEFAULT_V3_FORMAT_PAIRS_OUTPUT_PATH))
    train_mix_parser.add_argument('--correction-pairs-path', default=str(DEFAULT_V3_CORRECTION_PAIRS_OUTPUT_PATH))
    train_mix_parser.add_argument('--stage-a-config-path', default=str(DEFAULT_MIX_STAGE_A_CONFIG_PATH))
    train_mix_parser.add_argument('--stage-b-config-path', default=str(DEFAULT_MIX_STAGE_B_CONFIG_PATH))
    train_mix_parser.add_argument('--stage-a-output-path', default=str(DEFAULT_V3_STAGE_A_OUTPUT_PATH))
    train_mix_parser.add_argument('--stage-b-output-path', default=str(DEFAULT_V3_STAGE_B_OUTPUT_PATH))
    train_mix_parser.add_argument('--registry-path', default=str(DEFAULT_V3_WEIGHTED_REGISTRY_OUTPUT_PATH))
    train_mix_parser.set_defaults(func=run_build_train_mix_v3)

    train_sft_parser = subparsers.add_parser(
        'train-sft',
        help='Render or execute a v3 weighted MLX SFT job.',
    )
    train_sft_parser.add_argument('--stage', choices=('a', 'b'), default='a')
    train_sft_parser.add_argument('--config-path', default=str(DEFAULT_V3_STAGE_A_WEIGHTED_CONFIG_PATH))
    train_sft_parser.add_argument('--train-pack-path', default=str(DEFAULT_V3_STAGE_A_OUTPUT_PATH))
    train_sft_parser.add_argument('--dataset-dir', default=None)
    train_sft_parser.add_argument('--valid-fold', type=int, default=0)
    train_sft_parser.add_argument('--valid-fraction', type=float, default=0.05)
    train_sft_parser.add_argument('--max-train-rows', type=int, default=None)
    train_sft_parser.add_argument('--max-valid-rows', type=int, default=None)
    train_sft_parser.add_argument('--execute', action='store_true')
    train_sft_parser.add_argument('--output-dir', default=str(TRAIN_OUTPUT_ROOT))
    train_sft_parser.add_argument('--candidate-id', default=None)
    train_sft_parser.add_argument('--candidate-registry-path', default=str(DEFAULT_V3_CANDIDATE_REGISTRY_OUTPUT_PATH))
    train_sft_parser.set_defaults(func=run_train_sft_v3)

    ablation_parser = subparsers.add_parser('run-ablation', help='Append a run result to weighted_ablation_v3.csv.')
    ablation_parser.add_argument('--manifest-path', required=False)
    ablation_parser.add_argument('--config-path', dest='config_paths', action='append', default=[])
    ablation_parser.add_argument('--train-pack-path', default=str(DEFAULT_V3_STAGE_A_OUTPUT_PATH))
    ablation_parser.add_argument('--output-root', default=str(TRAIN_OUTPUT_ROOT / 'ablation'))
    ablation_parser.add_argument('--execute', action='store_true')
    ablation_parser.add_argument('--valid-fold', type=int, default=0)
    ablation_parser.add_argument('--valid-fraction', type=float, default=0.05)
    ablation_parser.add_argument('--max-train-rows', type=int, default=None)
    ablation_parser.add_argument('--max-valid-rows', type=int, default=None)
    ablation_parser.add_argument('--candidate-registry-path', default=str(DEFAULT_V3_CANDIDATE_REGISTRY_OUTPUT_PATH))
    ablation_parser.add_argument('--result-path', default=None)
    ablation_parser.add_argument('--output-path', default=str(DEFAULT_V3_WEIGHTED_ABLATION_OUTPUT_PATH))
    ablation_parser.add_argument('--run-id', default=None)
    ablation_parser.add_argument('--notes', default='')
    ablation_parser.set_defaults(func=run_ablation_v3)

    cuda_parser = subparsers.add_parser('render-cuda-repro-spec', help='Render a manual CUDA/BF16 reproduction spec and command stub.')
    cuda_parser.add_argument('--candidate-id', default=None)
    cuda_parser.add_argument('--manifest-path', default=None)
    cuda_parser.add_argument('--adapter-path', default=None)
    cuda_parser.add_argument('--config-path', default=str(DEFAULT_V4_CUDA_TRAIN_CONFIG_PATH))
    cuda_parser.add_argument('--output-path', default=str(DEFAULT_V4_CUDA_REPRO_SPEC_OUTPUT_PATH))
    cuda_parser.add_argument('--registry-path', default=str(DEFAULT_V4_CUDA_REPRO_REGISTRY_OUTPUT_PATH))
    cuda_parser.add_argument('--submission-manifest-path', default=str(DEFAULT_V4_SUBMISSION_MANIFEST_OUTPUT_PATH))
    cuda_parser.set_defaults(func=run_render_cuda_repro_spec_v4)

    package_peft_parser = subparsers.add_parser(
        'package-peft',
        help='Validate a CUDA-generated PEFT adapter dir and package submission_v4.zip.',
    )
    package_peft_parser.add_argument('--config-path', default=str(DEFAULT_V4_PACKAGE_CONFIG_PATH))
    package_peft_parser.add_argument('--adapter-dir', default=str(HANDOFF_ROOT))
    package_peft_parser.add_argument('--output-dir', default=str(PACKAGING_ROOT))
    package_peft_parser.set_defaults(func=run_package_peft_v4)

    runbook_parser = subparsers.add_parser(
        'write-runbook',
        help='Write the v4 candidate registry, promotion rules, and command book.',
    )
    runbook_parser.add_argument('--candidate-registry-path', default=str(DEFAULT_V4_CANDIDATE_REGISTRY_OUTPUT_PATH))
    runbook_parser.add_argument('--promotion-rules-path', default=str(DEFAULT_V4_PROMOTION_RULES_OUTPUT_PATH))
    runbook_parser.add_argument('--output-path', default=str(DEFAULT_V4_TRAINING_RUNBOOK_OUTPUT_PATH))
    runbook_parser.set_defaults(func=run_write_runbook_v4)

    score_candidate_parser = subparsers.add_parser('score-candidate', help='Score one adapter candidate on a configured local gate.')
    score_candidate_parser.add_argument('--config-path', default=str(DEFAULT_V4_SERIOUS_EVAL_CONFIG_PATH))
    score_candidate_parser.add_argument('--candidate-id', default=None)
    score_candidate_parser.add_argument('--manifest-path', default=None)
    score_candidate_parser.add_argument('--adapter-path', default=None)
    score_candidate_parser.add_argument('--output-root', default=None)
    score_candidate_parser.set_defaults(func=run_score_candidate_v4)

    score_candidate_batch_parser = subparsers.add_parser('score-candidate-batch', help='Score multiple candidates on a configured local gate.')
    score_candidate_batch_parser.add_argument('--config-path', default=str(DEFAULT_V4_SERIOUS_EVAL_CONFIG_PATH))
    score_candidate_batch_parser.add_argument('--candidate-id', dest='candidate_ids', action='append', default=[])
    score_candidate_batch_parser.add_argument('--manifest-path', dest='manifest_paths', action='append', default=[])
    score_candidate_batch_parser.set_defaults(func=run_score_candidate_batch_v4)

    build_format_preferences_parser = subparsers.add_parser('build-format-preferences', help='Build v4 format preference pairs from the v3 preference pool.')
    build_format_preferences_parser.add_argument('--config-path', default=str(DEFAULT_V4_FORMAT_PREFERENCE_CONFIG_PATH))
    build_format_preferences_parser.add_argument('--input-path', default=None)
    build_format_preferences_parser.add_argument('--output-path', default=str(DEFAULT_V4_FORMAT_PREFERENCE_OUTPUT_PATH))
    build_format_preferences_parser.add_argument('--registry-path', default=str(DEFAULT_V4_PREFERENCE_REGISTRY_OUTPUT_PATH))
    build_format_preferences_parser.set_defaults(func=run_build_format_preferences_v4)

    build_correctness_preferences_parser = subparsers.add_parser('build-correctness-preferences', help='Build v4 correctness preference pairs from the v3 preference pool.')
    build_correctness_preferences_parser.add_argument('--config-path', default=str(DEFAULT_V4_CORRECTNESS_PREFERENCE_CONFIG_PATH))
    build_correctness_preferences_parser.add_argument('--input-path', default=None)
    build_correctness_preferences_parser.add_argument('--output-path', default=str(DEFAULT_V4_CORRECTNESS_PREFERENCE_OUTPUT_PATH))
    build_correctness_preferences_parser.add_argument('--registry-path', default=str(DEFAULT_V4_PREFERENCE_REGISTRY_OUTPUT_PATH))
    build_correctness_preferences_parser.set_defaults(func=run_build_correctness_preferences_v4)

    build_rft_candidates_parser = subparsers.add_parser('build-rft-candidates', help='Generate v4 probe samples for RFT mining.')
    build_rft_candidates_parser.add_argument('--config-path', default=str(DEFAULT_V4_RFT_CONFIG_PATH))
    build_rft_candidates_parser.add_argument('--candidate-id', default='v3_stage_a_baseline')
    build_rft_candidates_parser.add_argument('--manifest-path', default=None)
    build_rft_candidates_parser.add_argument('--adapter-path', default=None)
    build_rft_candidates_parser.add_argument('--prompt-selection-path', default=None)
    build_rft_candidates_parser.add_argument('--output-path', default=str(DEFAULT_V4_RFT_GENERATIONS_OUTPUT_PATH))
    build_rft_candidates_parser.add_argument('--output-dir', default=None)
    build_rft_candidates_parser.set_defaults(func=run_build_rft_candidates_v4)

    filter_rft_accept_pool_parser = subparsers.add_parser('filter-rft-accept-pool', help='Filter probe samples into the v4 RFT accept pool.')
    filter_rft_accept_pool_parser.add_argument('--config-path', default=str(DEFAULT_V4_RFT_CONFIG_PATH))
    filter_rft_accept_pool_parser.add_argument('--input-path', default=str(DEFAULT_V4_RFT_GENERATIONS_OUTPUT_PATH))
    filter_rft_accept_pool_parser.add_argument('--output-path', default=str(DEFAULT_V4_RFT_ACCEPT_POOL_OUTPUT_PATH))
    filter_rft_accept_pool_parser.add_argument('--registry-path', default=str(DEFAULT_V4_RFT_REGISTRY_OUTPUT_PATH))
    filter_rft_accept_pool_parser.add_argument('--audit-output-path', default=None)
    filter_rft_accept_pool_parser.set_defaults(func=run_filter_rft_accept_pool_v4)

    build_stage_c_mix_parser = subparsers.add_parser('build-stage-c-mix', help='Build the v4 Stage C RFT and preference training packs.')
    build_stage_c_mix_parser.add_argument('--rft-config-path', default=str(DEFAULT_V4_STAGE_C_RFT_MIX_CONFIG_PATH))
    build_stage_c_mix_parser.add_argument('--preference-config-path', default=str(DEFAULT_V4_STAGE_C_PREFERENCE_MIX_CONFIG_PATH))
    build_stage_c_mix_parser.add_argument('--rft-accept-pool-path', default=str(DEFAULT_V4_RFT_ACCEPT_POOL_OUTPUT_PATH))
    build_stage_c_mix_parser.add_argument('--format-pairs-path', default=str(DEFAULT_V4_FORMAT_PREFERENCE_OUTPUT_PATH))
    build_stage_c_mix_parser.add_argument('--correctness-pairs-path', default=str(DEFAULT_V4_CORRECTNESS_PREFERENCE_OUTPUT_PATH))
    build_stage_c_mix_parser.add_argument('--rft-output-path', default=str(DEFAULT_V4_STAGE_C_RFT_OUTPUT_PATH))
    build_stage_c_mix_parser.add_argument('--preference-output-path', default=str(DEFAULT_V4_STAGE_C_PREFERENCE_OUTPUT_PATH))
    build_stage_c_mix_parser.set_defaults(func=run_build_stage_c_mix_v4)

    train_stage_c_rft_parser = subparsers.add_parser('train-stage-c-rft', help='Render or execute the v4 Stage C RFT continuation run.')
    train_stage_c_rft_parser.add_argument('--config-path', default=str(DEFAULT_V4_RFT_TRAIN_CONFIG_PATH))
    train_stage_c_rft_parser.add_argument('--train-pack-path', default=str(DEFAULT_V4_STAGE_C_RFT_OUTPUT_PATH))
    train_stage_c_rft_parser.add_argument('--output-dir', required=True)
    train_stage_c_rft_parser.add_argument('--candidate-id', default=None)
    train_stage_c_rft_parser.add_argument('--parent-candidate-id', default='v3_stage_a_baseline')
    train_stage_c_rft_parser.add_argument('--init-adapter-path', default=None)
    train_stage_c_rft_parser.add_argument('--valid-fold', type=int, default=-1)
    train_stage_c_rft_parser.add_argument('--valid-fraction', type=float, default=0.05)
    train_stage_c_rft_parser.add_argument('--max-train-rows', type=int, default=None)
    train_stage_c_rft_parser.add_argument('--max-valid-rows', type=int, default=None)
    train_stage_c_rft_parser.add_argument('--execute', action='store_true')
    train_stage_c_rft_parser.set_defaults(func=run_train_stage_c_rft_v4)

    train_stage_c_preference_parser = subparsers.add_parser('train-stage-c-preference', help='Render or execute the v4 Stage C preference/DPO run.')
    train_stage_c_preference_parser.add_argument('--config-path', default=str(DEFAULT_V4_FORMAT_DPO_CONFIG_PATH))
    train_stage_c_preference_parser.add_argument('--pair-data-path', default=str(DEFAULT_V4_STAGE_C_PREFERENCE_OUTPUT_PATH))
    train_stage_c_preference_parser.add_argument('--output-dir', required=True)
    train_stage_c_preference_parser.add_argument('--candidate-id', default=None)
    train_stage_c_preference_parser.add_argument('--parent-candidate-id', default='v3_stage_a_baseline')
    train_stage_c_preference_parser.add_argument('--init-adapter-path', default=None)
    train_stage_c_preference_parser.add_argument('--pair-kind', default=None)
    train_stage_c_preference_parser.add_argument('--family-filter', action='append', default=[])
    train_stage_c_preference_parser.add_argument('--valid-fold', type=int, default=-1)
    train_stage_c_preference_parser.add_argument('--valid-fraction', type=float, default=0.05)
    train_stage_c_preference_parser.add_argument('--execute', action='store_true')
    train_stage_c_preference_parser.set_defaults(func=run_train_stage_c_preference_v4)

    train_specialist_parser = subparsers.add_parser('train-specialist', help='Render or execute a v4 specialist preference run.')
    train_specialist_parser.add_argument('--config-path', default=str(DEFAULT_V4_SPECIALIST_FORMAT_CONFIG_PATH))
    train_specialist_parser.add_argument('--pair-data-path', default=str(DEFAULT_V4_STAGE_C_PREFERENCE_OUTPUT_PATH))
    train_specialist_parser.add_argument('--output-dir', required=True)
    train_specialist_parser.add_argument('--candidate-id', default=None)
    train_specialist_parser.add_argument('--parent-candidate-id', default='v3_stage_a_baseline')
    train_specialist_parser.add_argument('--init-adapter-path', default=None)
    train_specialist_parser.add_argument('--pair-kind', default=None)
    train_specialist_parser.add_argument('--specialist-tag', default=None)
    train_specialist_parser.add_argument('--family-filter', action='append', default=[])
    train_specialist_parser.add_argument('--valid-fold', type=int, default=-1)
    train_specialist_parser.add_argument('--valid-fraction', type=float, default=0.05)
    train_specialist_parser.add_argument('--execute', action='store_true')
    train_specialist_parser.set_defaults(func=run_train_specialist_v4)

    merge_candidates_parser = subparsers.add_parser('merge-candidates', help='Merge a generalist and specialist LoRA adapter.')
    merge_candidates_parser.add_argument('--config-path', default=str(DEFAULT_V4_MERGE_CONFIG_PATH))
    merge_candidates_parser.add_argument('--generalist-candidate-id', default=None)
    merge_candidates_parser.add_argument('--generalist-manifest-path', default=None)
    merge_candidates_parser.add_argument('--generalist-adapter-path', default=None)
    merge_candidates_parser.add_argument('--specialist-candidate-id', default=None)
    merge_candidates_parser.add_argument('--specialist-manifest-path', default=None)
    merge_candidates_parser.add_argument('--specialist-adapter-path', default=None)
    merge_candidates_parser.add_argument('--merge-id', default=None)
    merge_candidates_parser.add_argument('--output-dir', required=True)
    merge_candidates_parser.set_defaults(func=run_merge_candidates_v4)

    compress_merge_parser = subparsers.add_parser('compress-merge-rank32', help='Validate or compress a merged adapter to rank<=32.')
    compress_merge_parser.add_argument('--config-path', default=str(DEFAULT_V4_COMPRESS_CONFIG_PATH))
    compress_merge_parser.add_argument('--adapter-path', required=True)
    compress_merge_parser.add_argument('--output-dir', required=True)
    compress_merge_parser.set_defaults(func=run_compress_merge_rank32_v4)

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    ensure_v4_layout_scaffold()
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
