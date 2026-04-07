from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata as importlib_metadata
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any, Sequence

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_ROOT = Path(__file__).resolve().parent
REFERENCE_ROOT = WORK_ROOT / "reference"

DEFAULT_MODEL_ROOT = Path(
    "/Users/mac-studio/.cache/huggingface/hub/models--mlx-community--NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-BF16"
)
DEFAULT_TRAIN_CSV = (
    REFERENCE_ROOT
    / "baseline"
    / "cot"
    / "phase2_binary_dsl"
    / "artifacts"
    / "phase2_binary_hybrid_training_data.csv"
)
DEFAULT_STRONG_BASELINE_COT_CSV = (
    REFERENCE_ROOT
    / "baseline"
    / "nemotron-sft-lora-with-cot-v2"
    / "artifacts"
    / "train_split_with_cot.csv"
)
DEFAULT_PHASE0_PREBUILT_ROOT = REFERENCE_ROOT / "baseline" / "cot" / "phase0_offline_eval" / "artifacts"
DEFAULT_PHASE0_ANALYSIS_CSV = (
    REFERENCE_ROOT / "cuda-train-data-analysis-v1" / "artifacts" / "train_row_analysis_v1.csv"
)
DEFAULT_OUTPUT_ROOT = WORK_ROOT / "outputs"
DEFAULT_RUN_NAME = "phase2_binary_hybrid_mlx_v1"
PHASE0_ROUTER_PROFILE_PROMPT_V1 = "prompt-router-v1"
PHASE0_ROUTER_PROFILE_PROMPT_V2 = "prompt-router-v2"
PHASE0_ROUTER_PROFILE_PROMPT_V3 = "prompt-router-v3"
PHASE0_ROUTER_PROFILE_PROMPT_V4 = "prompt-router-v4"
PHASE0_ROUTER_PROFILE_PROMPT_V5 = "prompt-router-v5"
PHASE0_ROUTER_PROFILE_PROMPT_V6 = "prompt-router-v6"
PHASE0_ROUTER_PROFILE_CHOICES = (
    PHASE0_ROUTER_PROFILE_PROMPT_V1,
    PHASE0_ROUTER_PROFILE_PROMPT_V2,
    PHASE0_ROUTER_PROFILE_PROMPT_V3,
    PHASE0_ROUTER_PROFILE_PROMPT_V4,
    PHASE0_ROUTER_PROFILE_PROMPT_V5,
    PHASE0_ROUTER_PROFILE_PROMPT_V6,
)
PHASE0_ROUTER_SLOT_BY_FAMILY: dict[str, dict[str, str]] = {
    PHASE0_ROUTER_PROFILE_PROMPT_V1: {
        "binary": "specialist",
        "symbol": "specialist",
        "unit": "specialist",
        "gravity": "reasoning",
        "roman": "reasoning",
        "text": "general",
    },
    PHASE0_ROUTER_PROFILE_PROMPT_V2: {
        "binary": "specialist",
        "symbol": "specialist",
        "unit": "specialist",
        "gravity": "reasoning",
        "roman": "reasoning",
        "text": "general",
    },
    PHASE0_ROUTER_PROFILE_PROMPT_V3: {
        "binary": "specialist",
        "symbol": "specialist",
        "unit": "solver",
        "gravity": "solver",
        "roman": "solver",
        "text": "solver",
    },
    PHASE0_ROUTER_PROFILE_PROMPT_V4: {
        "binary": "specialist",
        "symbol": "specialist",
        "unit": "solver",
        "gravity": "solver",
        "roman": "solver",
        "text": "solver",
    },
    PHASE0_ROUTER_PROFILE_PROMPT_V5: {
        "binary": "specialist",
        "symbol": "specialist",
        "unit": "solver",
        "gravity": "solver",
        "roman": "solver",
        "text": "solver",
    },
    PHASE0_ROUTER_PROFILE_PROMPT_V6: {
        "binary": "specialist",
        "symbol": "specialist",
        "unit": "solver",
        "gravity": "solver",
        "roman": "solver",
        "text": "solver",
    },
}
AUGMENT_ARTIFACT_ROOT = REFERENCE_ROOT / "cuda-train-data-analysis-v1" / "artifacts"
AUGMENT_SYMBOL_OPERATOR_SPECIFIC_SUPPORT_CSV = (
    AUGMENT_ARTIFACT_ROOT / "symbol_operator_specific_formula_support_v1.csv"
)
AUGMENT_SYMBOL_REVERSE_OPERATOR_SUPPORT_CSV = (
    AUGMENT_ARTIFACT_ROOT / "symbol_reverse_operator_formula_support_v1.csv"
)
AUGMENT_SYMBOL_MINUS_PREFIX_SUPPORT_CSV = (
    AUGMENT_ARTIFACT_ROOT / "symbol_minus_prefix_subfamily_support_v1.csv"
)
AUGMENT_SYMBOL_MINUS_DIRECT_SUPPORT_CSV = (
    AUGMENT_ARTIFACT_ROOT / "symbol_minus_direct_plain_support_v1.csv"
)
AUGMENT_SYMBOL_STAR_PREFIX_SUPPORT_CSV = (
    AUGMENT_ARTIFACT_ROOT / "symbol_star_prefix_if_negative_support_v1.csv"
)
AUGMENT_SYMBOL_THIN_SUPPORT2_SUPPORT_CSV = (
    AUGMENT_ARTIFACT_ROOT / "symbol_thin_support2_subfamily_support_v1.csv"
)
AUGMENT_BINARY_STRUCTURED_CSV = AUGMENT_ARTIFACT_ROOT / "binary_structured_byte_formula_candidates_v1.csv"
AUGMENT_VERIFIED_TRACE_CSV = AUGMENT_ARTIFACT_ROOT / "train_verified_trace_ready_v1.csv"
AUGMENT_ANSWER_ONLY_CSV = AUGMENT_ARTIFACT_ROOT / "train_answer_only_keep_v1.csv"
AUGMENT_BINARY_MANUAL_CSV = AUGMENT_ARTIFACT_ROOT / "binary_manual_audit_queue_v1.csv"
AUGMENT_SYMBOL_MANUAL_CSV = AUGMENT_ARTIFACT_ROOT / "symbol_manual_audit_queue_v1.csv"
AUGMENT_BINARY_PROMPT_LOCAL_CURRENT_CONSENSUS_CSV = (
    AUGMENT_ARTIFACT_ROOT / "binary_prompt_local_current_consensus_candidates_v1.csv"
)
AUGMENT_BINARY_HYBRID_CONSENSUS_CSV = (
    AUGMENT_ARTIFACT_ROOT / "binary_hybrid_consensus_candidates_v1.csv"
)
AUGMENT_TRAIN_RECOMMENDED_CSV = (
    AUGMENT_ARTIFACT_ROOT / "train_recommended_learning_target_v1.csv"
)
PHASE2_BINARY_SPECIALIST_CSV = (
    REFERENCE_ROOT
    / "baseline"
    / "cot"
    / "phase2_1_2_merge_lora"
    / "artifacts"
    / "phase2_1_2_binary_specialist_training_data.csv"
)
PHASE2_SYMBOL_SPECIALIST_CSV = (
    REFERENCE_ROOT
    / "baseline"
    / "cot"
    / "phase2_2_merge_lora"
    / "artifacts"
    / "phase2_2_symbol_specialist_training_data.csv"
)
TRAIN_PROFILE_CHOICES = (
    "baseline",
    "strong-baseline-cot-v2",
    "strong-baseline-cot-v2-structured-anchor-v1",
    "strong-baseline-cot-v2-structured-anchor-v2",
    "single-adapter-focus-v1",
    "single-adapter-focus-v2",
    "single-adapter-fusion-v1",
    "single-adapter-fusion-v2",
    "single-adapter-fusion-v3",
    "single-adapter-fusion-v4",
    "single-adapter-fusion-v5",
    "single-adapter-fusion-v6",
    "single-adapter-fusion-v7",
    "single-adapter-fusion-v8",
    "single-adapter-fusion-v9",
    "single-adapter-fusion-v10",
    "single-adapter-fusion-v11",
    "single-adapter-fusion-v12",
    "single-adapter-fusion-v13",
    "single-adapter-fusion-v14",
    "single-adapter-fusion-v15",
    "single-adapter-fusion-v16",
    "single-adapter-fusion-v17",
    "single-adapter-fusion-v18",
    "single-adapter-fusion-v19",
    "single-adapter-fusion-v20",
    "single-adapter-fusion-v21",
    "single-adapter-fusion-v22",
    "single-adapter-fusion-v23",
    "single-adapter-fusion-v24",
    "single-adapter-fusion-v25",
    "single-adapter-fusion-v26",
    "single-adapter-fusion-v27",
    "single-adapter-fusion-v28",
    "single-adapter-fusion-v29",
    "single-adapter-fusion-v30",
    "single-adapter-fusion-v31",
    "single-adapter-fusion-v32",
    "single-adapter-fusion-v33",
    "single-adapter-fusion-v34",
    "single-adapter-fusion-v35",
    "single-adapter-fusion-v36",
    "single-adapter-fusion-v37",
    "single-adapter-fusion-v38",
    "single-adapter-fusion-v39",
    "single-adapter-fusion-v40",
    "single-adapter-fusion-v41",
    "single-adapter-fusion-v42",
    "single-adapter-fusion-v43",
    "single-adapter-fusion-v44",
    "single-adapter-fusion-v45",
    "single-adapter-fusion-v46",
    "single-adapter-fusion-v47",
    "single-adapter-fusion-v48",
    "single-adapter-fusion-v49",
    "single-adapter-fusion-v50",
    "single-adapter-fusion-v51",
    "single-adapter-fusion-v52",
    "single-adapter-fusion-v53",
    "single-adapter-fusion-v54",
    "single-adapter-fusion-v55",
    "single-adapter-fusion-v56",
    "single-adapter-fusion-v57",
    "single-adapter-fusion-v58",
    "single-adapter-fusion-v59",
    "single-adapter-fusion-v60",
    "single-adapter-fusion-v61",
    "single-adapter-fusion-v62",
    "single-adapter-fusion-v63",
    "single-adapter-fusion-v64",
    "single-adapter-fusion-v65",
    "single-adapter-fusion-v66",
    "single-adapter-fusion-v67",
    "single-adapter-fusion-v68",
    "single-adapter-fusion-v69",
    "single-adapter-fusion-v70",
    "single-adapter-fusion-v71",
    "single-adapter-fusion-v72",
    "single-adapter-fusion-v73",
    "single-adapter-fusion-v74",
    "single-adapter-fusion-v75",
    "single-adapter-fusion-v76",
    "single-adapter-fusion-v77",
    "single-adapter-fusion-v78",
    "single-adapter-fusion-v79",
    "single-adapter-fusion-v80",
    "single-adapter-fusion-v81",
    "single-adapter-fusion-v82",
    "single-adapter-fusion-v83",
    "single-adapter-fusion-v84",
    "single-adapter-fusion-v88",
    "single-adapter-fusion-v89",
    "single-adapter-fusion-v90",
    "single-adapter-fusion-v91",
    "single-adapter-fusion-v92",
    "single-adapter-fusion-v93",
    "single-adapter-fusion-v94",
    "single-adapter-fusion-v95",
    "single-adapter-fusion-v96",
    "single-adapter-fusion-v97",
    "single-adapter-fusion-v98",
    "single-adapter-fusion-v99",
    "single-adapter-fusion-v100",
    "single-adapter-fusion-v101",
    "single-adapter-fusion-v102",
    "single-adapter-fusion-v103",
    "single-adapter-fusion-v104",
    "single-adapter-fusion-v105",
    "single-adapter-fusion-v106",
    "single-adapter-fusion-v107",
    "single-adapter-fusion-v108",
    "single-adapter-fusion-v109",
    "single-adapter-fusion-v110",
    "single-adapter-fusion-v111",
    "single-adapter-fusion-v112",
    "single-adapter-fusion-v113",
    "single-adapter-fusion-v114",
    "single-adapter-fusion-v115",
    "single-adapter-fusion-v116",
    "single-adapter-fusion-v117",
    "single-adapter-fusion-v118",
    "single-adapter-fusion-v119",
    "single-adapter-fusion-v120",
    "single-adapter-fusion-v121",
    "single-adapter-fusion-v122",
    "single-adapter-fusion-v123",
    "single-adapter-fusion-v124",
    "single-adapter-fusion-v128",
    "single-adapter-fusion-v129",
    "single-adapter-fusion-v131",
    "single-adapter-fusion-v132",
    "single-adapter-fusion-v133",
    "single-adapter-fusion-v134",
    "single-adapter-fusion-v135",
    "single-adapter-fusion-v136",
    "single-adapter-fusion-v137",
    "single-adapter-fusion-v138",
    "single-adapter-fusion-v140",
    "single-adapter-fusion-v141",
    "single-adapter-fusion-v142",
    "general-stable-focus-v1",
    "general-stable-focus-v2",
    "general-stable-focus-v3",
)

BOXED_INSTRUCTION = r"Please put your final answer inside `\boxed{}`. For example: `\boxed{your answer}`"
BINARY_STRICT_BOXED_SUFFIX = (
    r"For this binary task, the content inside `\boxed{}` must be exactly 8 binary digits, "
    r'for example `\boxed{01010101}`. Do not write extra digits, words, or repeated bits. '
    r"Stop immediately after the boxed answer."
)
STRICT_BARE_BOXED_SUFFIX = (
    r"For this task, the content inside `\boxed{}` must be only the bare final answer itself. "
    r"Do not include units, labels, variable names, equations, or extra words. "
    r'For example write `\boxed{38.89}` instead of `\boxed{38.89 \text{ m}}`. '
    r"Stop immediately after the boxed answer."
)
EXPECTED_PHASE2_COLUMNS = [
    "id",
    "prompt",
    "answer",
    "generated_cot",
    "label",
    "assistant_style",
    "source_selection_tier",
]
EXPECTED_PHASE2_ROWS = 900
EXPECTED_STRONG_BASELINE_COLUMNS = [
    "id",
    "prompt",
    "answer",
    "type",
    "generated_cot",
]
STRONG_BASELINE_TYPE_TO_LABEL = {
    "Bit Manipulation": "bit_manipulation",
    "Equation Transformation": "symbol_equation",
    "Gravitational Constant": "gravity_constant",
    "Numeral Conversion": "roman_numeral",
    "Text Encryption": "text_decryption",
    "Unit Conversion": "unit_conversion",
}
STRONG_BASELINE_V2_TYPE_SAMPLES = {
    "Numeral Conversion": 300,
    "Gravitational Constant": 400,
    "Unit Conversion": 700,
    "Text Encryption": 700,
    "Bit Manipulation": 607,
    "Equation Transformation": 200,
}
STRONG_BASELINE_V2_SEED = 123
STRONG_BASELINE_V2_STRUCTURED_ANCHOR_V1_SPECS = (
    {
        "source_name": "recommended_binary_formula_verified",
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_structured_byte_formula",
        "allowed_tiers": ("verified_trace_ready",),
    },
    {
        "source_name": "recommended_binary_formula_answer_only",
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_structured_byte_formula",
        "allowed_tiers": ("answer_only_keep",),
    },
    {
        "source_name": "recommended_symbol_numeric_verified",
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("verified_trace_ready",),
    },
)
STRONG_BASELINE_V2_STRUCTURED_ANCHOR_V2_SPECS = (
    *STRONG_BASELINE_V2_STRUCTURED_ANCHOR_V1_SPECS,
    {
        "source_name": "recommended_symbol_numeric_answer_only",
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("answer_only_keep",),
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V88_SPECS = (
    {
        "source_name": "strong_sample_binary_formula_verified",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_structured_byte_formula",
        "allowed_tiers": ("verified_trace_ready",),
    },
    {
        "source_name": "strong_sample_binary_formula_answer_only",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_structured_byte_formula",
        "allowed_tiers": ("answer_only_keep",),
    },
    {
        "source_name": "strong_sample_binary_other_verified",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_other",
        "allowed_tiers": ("verified_trace_ready",),
    },
    {
        "source_name": "strong_sample_binary_other_answer_only",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_other",
        "allowed_tiers": ("answer_only_keep",),
    },
    {
        "source_name": "strong_sample_symbol_numeric_verified",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("verified_trace_ready",),
    },
    {
        "source_name": "strong_sample_symbol_numeric_answer_only",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("answer_only_keep",),
    },
    {
        "source_name": "strong_sample_symbol_glyph_answer_only",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "glyph_len5",
        "allowed_tiers": ("answer_only_keep",),
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V89_SPECS = (
    *STRONG_BASELINE_V2_SAMPLE_FUSION_V88_SPECS,
    {
        "source_name": "strong_sample_text_verified_anchor",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "text_decryption",
        "label": "text",
        "template_subtype": "text_monoalphabetic",
        "allowed_tiers": ("verified_trace_ready",),
        "quota": 64,
        "group_keys": ("selection_tier",),
    },
    {
        "source_name": "strong_sample_text_answer_only_anchor",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "text_decryption",
        "label": "text",
        "template_subtype": "text_monoalphabetic",
        "allowed_tiers": ("answer_only_keep",),
        "quota": 64,
        "group_keys": ("selection_tier",),
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V90_SPECS = (
    {
        "source_name": "strong_sample_binary_formula_verified_short_done",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_structured_byte_formula",
        "allowed_tiers": ("verified_trace_ready",),
        "assistant_style": "boxed_only_done",
        "quota": 48,
        "group_keys": ("selection_tier", "bit_no_candidate_positions", "num_examples"),
    },
    {
        "source_name": "strong_sample_binary_formula_answer_only_short_done",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_structured_byte_formula",
        "allowed_tiers": ("answer_only_keep",),
        "assistant_style": "boxed_only_done",
        "quota": 16,
        "group_keys": ("selection_tier", "bit_no_candidate_positions", "num_examples"),
    },
    {
        "source_name": "strong_sample_binary_other_verified_short_done",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_other",
        "allowed_tiers": ("verified_trace_ready",),
        "assistant_style": "boxed_only_done",
        "quota": 48,
        "group_keys": ("selection_tier", "teacher_solver_candidate", "num_examples"),
    },
    {
        "source_name": "strong_sample_binary_other_answer_only_short_done",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_other",
        "allowed_tiers": ("answer_only_keep",),
        "assistant_style": "boxed_only_done",
        "quota": 16,
        "group_keys": ("selection_tier", "teacher_solver_candidate", "num_examples"),
    },
    {
        "source_name": "strong_sample_symbol_numeric_verified_short_done",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("verified_trace_ready",),
        "assistant_style": "boxed_only_done",
        "quota": 16,
        "group_keys": ("selection_tier", "num_examples"),
    },
    {
        "source_name": "strong_sample_symbol_numeric_answer_only_short_done",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("answer_only_keep",),
        "assistant_style": "boxed_only_done",
        "quota": 16,
        "group_keys": ("selection_tier", "num_examples"),
    },
    {
        "source_name": "strong_sample_symbol_glyph_answer_only_short_done",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "glyph_len5",
        "allowed_tiers": ("answer_only_keep",),
        "assistant_style": "boxed_only_done",
        "quota": 8,
        "group_keys": ("selection_tier", "num_examples"),
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V91_SPECS = (
    {
        "source_name": "strong_sample_binary_formula_verified_short_boxed",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_structured_byte_formula",
        "allowed_tiers": ("verified_trace_ready",),
        "assistant_style": "boxed_only",
        "quota": 48,
        "group_keys": ("selection_tier", "bit_no_candidate_positions", "num_examples"),
    },
    {
        "source_name": "strong_sample_binary_formula_answer_only_short_boxed",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_structured_byte_formula",
        "allowed_tiers": ("answer_only_keep",),
        "assistant_style": "boxed_only",
        "quota": 16,
        "group_keys": ("selection_tier", "bit_no_candidate_positions", "num_examples"),
    },
    {
        "source_name": "strong_sample_binary_other_verified_short_boxed",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_other",
        "allowed_tiers": ("verified_trace_ready",),
        "assistant_style": "boxed_only",
        "quota": 48,
        "group_keys": ("selection_tier", "teacher_solver_candidate", "num_examples"),
    },
    {
        "source_name": "strong_sample_binary_other_answer_only_short_boxed",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_other",
        "allowed_tiers": ("answer_only_keep",),
        "assistant_style": "boxed_only",
        "quota": 16,
        "group_keys": ("selection_tier", "teacher_solver_candidate", "num_examples"),
    },
    {
        "source_name": "strong_sample_symbol_numeric_verified_short_boxed",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("verified_trace_ready",),
        "assistant_style": "boxed_only",
        "quota": 16,
        "group_keys": ("selection_tier", "num_examples"),
    },
    {
        "source_name": "strong_sample_symbol_numeric_answer_only_short_boxed",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("answer_only_keep",),
        "assistant_style": "boxed_only",
        "quota": 16,
        "group_keys": ("selection_tier", "num_examples"),
    },
    {
        "source_name": "strong_sample_symbol_glyph_answer_only_short_boxed",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "glyph_len5",
        "allowed_tiers": ("answer_only_keep",),
        "assistant_style": "boxed_only",
        "quota": 8,
        "group_keys": ("selection_tier", "num_examples"),
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V123_SPECS = (
    {
        "source_name": "strong_sample_binary_other_verified_short_done_v123",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_other",
        "allowed_tiers": ("verified_trace_ready",),
        "assistant_style": "boxed_only_done",
        "quota": 24,
        "group_keys": ("selection_tier", "teacher_solver_candidate", "num_examples"),
    },
    {
        "source_name": "strong_sample_symbol_numeric_verified_short_done_v123",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("verified_trace_ready",),
        "assistant_style": "boxed_only_done",
        "quota": 8,
        "group_keys": ("selection_tier", "num_examples"),
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V124_SPECS = (
    {
        "source_name": "strong_sample_binary_other_verified_short_done_v124",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "bit_manipulation",
        "label": "binary",
        "template_subtype": "bit_other",
        "allowed_tiers": ("verified_trace_ready",),
        "assistant_style": "boxed_only_done",
        "quota": 48,
        "group_keys": ("selection_tier", "teacher_solver_candidate", "num_examples"),
    },
    {
        "source_name": "strong_sample_symbol_numeric_verified_short_done_v124",
        "metadata_path": AUGMENT_TRAIN_RECOMMENDED_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("verified_trace_ready",),
        "assistant_style": "boxed_only_done",
        "quota": 16,
        "group_keys": ("selection_tier", "num_examples"),
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V131_SPECS = STRONG_BASELINE_V2_SAMPLE_FUSION_V124_SPECS
STRONG_BASELINE_V2_SAMPLE_FUSION_V132_SPECS = (
    STRONG_BASELINE_V2_SAMPLE_FUSION_V124_SPECS[0],
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V133_SPECS = (
    STRONG_BASELINE_V2_SAMPLE_FUSION_V124_SPECS[1],
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V134_SPECS = (
    {
        **STRONG_BASELINE_V2_SAMPLE_FUSION_V124_SPECS[0],
        "assistant_style": "boxed_only",
        "source_name": "strong_sample_binary_other_verified_short_boxed_v134",
    },
    {
        **STRONG_BASELINE_V2_SAMPLE_FUSION_V124_SPECS[1],
        "assistant_style": "boxed_only",
        "source_name": "strong_sample_symbol_numeric_verified_short_boxed_v134",
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V135_SPECS = (
    {
        **STRONG_BASELINE_V2_SAMPLE_FUSION_V124_SPECS[1],
        "assistant_style": "boxed_only",
        "source_name": "strong_sample_symbol_numeric_verified_short_boxed_v135",
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V136_SPECS = (
    {
        **STRONG_BASELINE_V2_SAMPLE_FUSION_V124_SPECS[0],
        "assistant_style": "boxed_only",
        "source_name": "strong_sample_binary_other_verified_short_boxed_v136",
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V137_SPECS = (
    {
        **STRONG_BASELINE_V2_SAMPLE_FUSION_V124_SPECS[1],
        "assistant_style": "boxed_only",
        "source_name": "strong_sample_symbol_numeric_verified_short_boxed_v137",
        "quota": 4,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V138_SPECS = (
    {
        **STRONG_BASELINE_V2_SAMPLE_FUSION_V124_SPECS[1],
        "assistant_style": "boxed_only",
        "source_name": "strong_sample_symbol_numeric_verified_short_boxed_v138",
        "quota": 8,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V92_SPECS = (
    {
        "source_name": "strong_sample_text_general_short_done",
        "baseline_source_type": "Text Encryption",
        "label": "text",
        "assistant_style": "boxed_only_done",
        "quota": 96,
        "group_keys": ("prompt_len_bucket", "answer_word_count"),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_unit_general_short_done",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only_done",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_general_short_done",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only_done",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_general_short_done",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only_done",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_general_short_done",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only_done",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V93_SPECS = (
    {
        "source_name": "strong_sample_text_general_short_boxed",
        "baseline_source_type": "Text Encryption",
        "label": "text",
        "assistant_style": "boxed_only",
        "quota": 96,
        "group_keys": ("prompt_len_bucket", "answer_word_count"),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_unit_general_short_boxed",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_general_short_boxed",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_general_short_boxed",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_general_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V94_SPECS = (
    *STRONG_BASELINE_V2_SAMPLE_FUSION_V92_SPECS,
    {
        "source_name": "strong_sample_bit_general_short_done",
        "baseline_source_type": "Bit Manipulation",
        "label": "binary",
        "assistant_style": "boxed_only_done",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V95_SPECS = (
    *STRONG_BASELINE_V2_SAMPLE_FUSION_V93_SPECS,
    {
        "source_name": "strong_sample_bit_general_short_boxed",
        "baseline_source_type": "Bit Manipulation",
        "label": "binary",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V96_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_done",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only_done",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_done",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only_done",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_notext_short_done",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only_done",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_done",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only_done",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V97_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_boxed",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_notext_short_boxed",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V98_SPECS = (
    {
        "source_name": "strong_sample_unit_numeric_short_done",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only_done",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_numeric_short_done",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only_done",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_numeric_short_done",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only_done",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V116_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed_strict",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "prompt_style": "strict_bare_boxed",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_boxed_strict",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "prompt_style": "strict_bare_boxed",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_notext_short_boxed",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V117_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed_strict",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "prompt_style": "strict_bare_boxed",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_boxed_strict",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "prompt_style": "strict_bare_boxed",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_notext_short_boxed",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed_strict",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "prompt_style": "strict_bare_boxed",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V118_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed_strict",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "prompt_style": "strict_bare_boxed",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_boxed_strict",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "prompt_style": "strict_bare_boxed",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_notext_short_boxed_strict",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "prompt_style": "strict_bare_boxed",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed_strict",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "prompt_style": "strict_bare_boxed",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V99_SPECS = (
    {
        "source_name": "strong_sample_symbol_only_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V100_SPECS = (
    {
        "source_name": "strong_sample_symbol_only_short_done",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only_done",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V101_SPECS = (
    {
        "source_name": "strong_sample_symbol_numeric_verified_joined_boxed",
        "metadata_path": AUGMENT_VERIFIED_TRACE_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("verified_trace_ready",),
        "assistant_style": "boxed_only",
        "quota": 16,
        "group_keys": ("answer_type",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_numeric_answer_only_joined_boxed",
        "metadata_path": AUGMENT_ANSWER_ONLY_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "numeric_2x2",
        "allowed_tiers": ("answer_only_keep",),
        "assistant_style": "boxed_only",
        "quota": 8,
        "group_keys": ("answer_type",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_glyph_answer_only_joined_boxed",
        "metadata_path": AUGMENT_ANSWER_ONLY_CSV,
        "family": "symbol_equation",
        "label": "symbol",
        "template_subtype": "glyph_len5",
        "allowed_tiers": ("answer_only_keep",),
        "assistant_style": "boxed_only",
        "quota": 8,
        "group_keys": ("answer_type",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V102_SPECS = (
    {
        "source_name": "strong_sample_roman_only_short_boxed",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_only_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V103_SPECS = (
    {
        "source_name": "strong_sample_roman_only_short_done",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only_done",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_only_short_done",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only_done",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V104_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_boxed",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V105_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V106_SPECS = (
    {
        "source_name": "strong_sample_gravity_notext_short_boxed",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V107_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_boxed",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "quota": 16,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_notext_short_boxed",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V108_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_boxed",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_notext_short_boxed",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V109_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_boxed",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "quota": 16,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_notext_short_boxed",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V110_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "quota": 64,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_boxed",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_notext_short_boxed",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V111_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "quota": 48,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_boxed",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_notext_short_boxed",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)
STRONG_BASELINE_V2_SAMPLE_FUSION_V112_SPECS = (
    {
        "source_name": "strong_sample_unit_notext_short_boxed",
        "baseline_source_type": "Unit Conversion",
        "label": "unit",
        "assistant_style": "boxed_only",
        "quota": 48,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_gravity_notext_short_boxed",
        "baseline_source_type": "Gravitational Constant",
        "label": "gravity",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_roman_notext_short_boxed",
        "baseline_source_type": "Numeral Conversion",
        "label": "roman",
        "assistant_style": "boxed_only",
        "quota": 32,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
    {
        "source_name": "strong_sample_symbol_notext_short_boxed",
        "baseline_source_type": "Equation Transformation",
        "label": "symbol",
        "assistant_style": "boxed_only",
        "quota": 24,
        "group_keys": ("prompt_len_bucket",),
        "hard_first": False,
    },
)

README_MAX_LORA_RANK = 32
README_MAX_TOKENS = 7680
README_TOP_P = 1.0
README_TEMPERATURE = 0.0
README_MAX_NUM_SEQS = 64
README_MAX_MODEL_LEN = 8192

GENERAL_STABLE_QUOTAS = {
    "gravity_constant": 50,
    "unit_conversion": 50,
    "roman_numeral": 50,
    "text_decryption": 50,
}
BINARY_HARD_TIER_QUOTAS = {
    "verified_trace_ready": 20,
    "answer_only_keep": 20,
    "manual_audit_priority": 20,
}
SYMBOL_WATCH_TARGETS = [
    ("numeric_2x2", "verified_trace_ready", 15),
    ("numeric_2x2", "answer_only_keep", 15),
    ("numeric_2x2", "manual_audit_priority", 10),
    ("glyph_len5", "manual_audit_priority", 20),
]
FUSION_V15_AUGMENT_QUOTAS = {
    "binary_candidates": 240,
    "symbol_verified": 32,
    "symbol_answer_only": 64,
    "symbol_manual": 26,
}
FUSION_V16_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "symbol_verified": 32,
    "symbol_answer_only": 64,
    "symbol_manual": 26,
    "symbol_glyph_answer_only": 0,
}
FUSION_V17_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 96,
}
FUSION_V18_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 32,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 32,
}
FUSION_V19_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 32,
}
FUSION_V20_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 16,
    "symbol_answer_only": 48,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 48,
}
FUSION_V21_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 16,
    "symbol_verified": 16,
    "symbol_answer_only": 48,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 48,
}
FUSION_V22_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 32,
    "symbol_answer_only": 64,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
}
FUSION_V23_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 32,
    "symbol_answer_only": 64,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 16,
}
FUSION_V24_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 24,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 0,
    "symbol_formula_answer_only": 0,
}
FUSION_V25_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 24,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 0,
}
FUSION_V26_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 16,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 8,
}
FUSION_V27_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 24,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 2,
    "unit_verified_anchor_mod": 2,
}
FUSION_V28_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 24,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 2,
    "unit_verified_anchor_mod": 2,
}
FUSION_V29_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 24,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 4,
    "unit_verified_anchor_mod": 0,
}
FUSION_V30_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 24,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 0,
    "unit_verified_anchor_mod": 4,
}
FUSION_V31_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "binary_manual_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 24,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 4,
    "unit_verified_anchor_mod": 4,
}
FUSION_V32_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 16,
    "binary_manual_bit_other": 16,
    "symbol_verified": 0,
    "symbol_answer_only": 16,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 24,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 0,
}
FUSION_V33_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 24,
    "binary_manual_bit_other": 24,
    "symbol_verified": 0,
    "symbol_answer_only": 16,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 24,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 0,
}
FUSION_V34_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 16,
    "binary_manual_bit_other": 16,
    "symbol_verified": 0,
    "symbol_answer_only": 24,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 24,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 8,
}
FUSION_V35_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 16,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 8,
}
FUSION_V36_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 24,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 4,
}
FUSION_V37_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 20,
    "binary_structured_answer_only": 16,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 0,
}
FUSION_V38_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V39_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
    "unit_verified_anchor_mod": 8,
}
FUSION_V40_AUGMENT_QUOTAS = {
    "binary_candidates": 16,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V41_AUGMENT_QUOTAS = {
    "binary_candidates": 24,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V42_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 24,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V43_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 48,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V44_AUGMENT_QUOTAS = {
    "binary_candidates": 16,
    "binary_answer_only_bit_other": 8,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V45_AUGMENT_QUOTAS = {
    "binary_candidates": 16,
    "binary_answer_only_bit_other": 16,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V46_AUGMENT_QUOTAS = {
    "binary_candidates": 16,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
    "unit_verified_anchor_mod": 8,
}
FUSION_V47_AUGMENT_QUOTAS = {
    "binary_candidates": 16,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 8,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V48_AUGMENT_QUOTAS = {
    "binary_candidates": 16,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 4,
    "text_verified_anchor_mod": 8,
}
FUSION_V49_AUGMENT_QUOTAS = {
    "binary_candidates": 12,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 12,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V50_AUGMENT_QUOTAS = {
    "binary_candidates": 16,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "gravity_verified_anchor_mod": 8,
    "text_verified_anchor_mod": 8,
}
FUSION_V51_AUGMENT_QUOTAS = {
    "binary_candidates": 12,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 12,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "gravity_verified_anchor_mod": 8,
    "text_verified_anchor_mod": 8,
}
FUSION_V52_AUGMENT_QUOTAS = {
    "binary_candidates": 16,
    "binary_candidates_template_subtype": "bit_structured_byte_formula",
    "binary_candidates_allowed_tiers": ("verified_trace_ready",),
    "binary_candidate_min_fields": {"bit_no_candidate_positions": 4},
    "binary_candidate_exact_fields": {"bit_multi_candidate_positions": 0},
    "binary_candidate_group_keys": ("bit_structured_formula_abstract_family", "num_examples"),
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V53_AUGMENT_QUOTAS = {
    "binary_candidates": 16,
    "binary_candidates_template_subtype": "bit_structured_byte_formula",
    "binary_candidates_allowed_tiers": ("verified_trace_ready",),
    "binary_candidate_min_fields": {"bit_no_candidate_positions": 3},
    "binary_candidate_max_fields": {"bit_no_candidate_positions": 5},
    "binary_candidate_group_keys": ("bit_structured_formula_abstract_family", "num_examples"),
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V54_AUGMENT_QUOTAS = {
    "binary_candidates": 12,
    "binary_candidates_template_subtype": "bit_structured_byte_formula",
    "binary_candidates_allowed_tiers": ("verified_trace_ready",),
    "binary_candidate_min_fields": {
        "bit_no_candidate_positions": 4,
        "bit_multi_candidate_positions": 1,
    },
    "binary_candidate_group_keys": ("bit_structured_formula_abstract_family", "teacher_solver_candidate"),
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V55_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_prompt_local_current_structured_answer_only": 16,
    "binary_prompt_local_current_structured_answer_only_min_fields": {
        "bit_no_candidate_positions": 6,
        "num_examples": 8,
    },
    "binary_prompt_local_current_structured_answer_only_exact_fields": {
        "safe_prediction_count": 1,
        "safe_formula_count": 1,
        "bit_multi_candidate_positions": 0,
    },
    "binary_prompt_local_current_structured_answer_only_group_keys": ("safe_formulas", "num_examples"),
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V56_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_prompt_local_current_structured_answer_only": 16,
    "binary_prompt_local_current_structured_answer_only_min_fields": {
        "bit_no_candidate_positions": 6,
        "num_examples": 8,
    },
    "binary_prompt_local_current_structured_answer_only_max_fields": {
        "safe_formula_count": 2,
    },
    "binary_prompt_local_current_structured_answer_only_exact_fields": {
        "safe_prediction_count": 1,
        "bit_multi_candidate_positions": 0,
    },
    "binary_prompt_local_current_structured_answer_only_group_keys": ("safe_formulas", "num_examples"),
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V57_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_prompt_local_current_structured_answer_only": 12,
    "binary_prompt_local_current_structured_answer_only_min_fields": {
        "bit_no_candidate_positions": 3,
        "num_examples": 8,
    },
    "binary_prompt_local_current_structured_answer_only_max_fields": {
        "bit_no_candidate_positions": 5,
        "safe_formula_count": 2,
    },
    "binary_prompt_local_current_structured_answer_only_exact_fields": {
        "safe_prediction_count": 1,
        "bit_multi_candidate_positions": 0,
    },
    "binary_prompt_local_current_structured_answer_only_group_keys": ("safe_formulas", "num_examples"),
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V58_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 0,
    "binary_structured_leading_zero_answer_only": 16,
    "binary_structured_leading_zero_answer_only_min_fields": {
        "bit_no_candidate_positions": 6,
        "num_examples": 8,
    },
    "binary_structured_leading_zero_answer_only_startswith_fields": {
        "answer": "0",
    },
    "binary_structured_leading_zero_answer_only_group_keys": (
        "num_examples",
        "bit_no_candidate_positions",
    ),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V59_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 0,
    "binary_structured_leading_zero_answer_only": 12,
    "binary_structured_leading_zero_answer_only_min_fields": {
        "bit_no_candidate_positions": 6,
        "num_examples": 9,
    },
    "binary_structured_leading_zero_answer_only_startswith_fields": {
        "answer": "0",
    },
    "binary_structured_leading_zero_answer_only_group_keys": (
        "num_examples",
        "bit_no_candidate_positions",
    ),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V60_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 0,
    "binary_structured_leading_zero_answer_only": 12,
    "binary_structured_leading_zero_answer_only_min_fields": {
        "bit_no_candidate_positions": 3,
        "num_examples": 8,
    },
    "binary_structured_leading_zero_answer_only_max_fields": {
        "bit_no_candidate_positions": 5,
    },
    "binary_structured_leading_zero_answer_only_startswith_fields": {
        "answer": "0",
    },
    "binary_structured_leading_zero_answer_only_group_keys": (
        "num_examples",
        "bit_no_candidate_positions",
    ),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V61_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 0,
    "binary_structured_leading_zero_answer_only": 13,
    "binary_structured_leading_zero_answer_only_min_fields": {
        "bit_no_candidate_positions": 7,
        "num_examples": 8,
    },
    "binary_structured_leading_zero_answer_only_exact_fields": {
        "bit_structured_formula_safe_support": "0",
    },
    "binary_structured_leading_zero_answer_only_startswith_fields": {
        "answer": "0",
    },
    "binary_structured_leading_zero_answer_only_group_keys": (
        "num_examples",
        "bit_no_candidate_positions",
        "bit_structured_formula_safe_support",
    ),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V62_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 0,
    "binary_structured_leading_zero_answer_only": 16,
    "binary_structured_leading_zero_answer_only_min_fields": {
        "bit_no_candidate_positions": 6,
        "num_examples": 8,
    },
    "binary_structured_leading_zero_answer_only_exact_fields": {
        "bit_structured_formula_safe_support": "0",
    },
    "binary_structured_leading_zero_answer_only_startswith_fields": {
        "answer": "0",
    },
    "binary_structured_leading_zero_answer_only_group_keys": (
        "num_examples",
        "bit_no_candidate_positions",
        "bit_structured_formula_safe_support",
    ),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V63_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 0,
    "binary_structured_exact_zero_answer_only": 4,
    "binary_structured_exact_zero_answer_only_min_fields": {
        "bit_no_candidate_positions": 7,
        "num_examples": 8,
    },
    "binary_structured_exact_zero_answer_only_exact_fields": {
        "answer": "00000000",
        "bit_structured_formula_safe_support": "0",
    },
    "binary_structured_exact_zero_answer_only_group_keys": (
        "num_examples",
        "bit_no_candidate_positions",
        "bit_structured_formula_safe_support",
    ),
    "binary_structured_leading_zero_answer_only": 9,
    "binary_structured_leading_zero_answer_only_min_fields": {
        "bit_no_candidate_positions": 7,
        "num_examples": 8,
    },
    "binary_structured_leading_zero_answer_only_exact_fields": {
        "bit_structured_formula_safe_support": "0",
    },
    "binary_structured_leading_zero_answer_only_startswith_fields": {
        "answer": "0",
    },
    "binary_structured_leading_zero_answer_only_group_keys": (
        "num_examples",
        "bit_no_candidate_positions",
        "bit_structured_formula_safe_support",
    ),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V64_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_hybrid_consensus": 8,
    "binary_hybrid_consensus_allowed_tiers": (
        "verified_trace_ready",
        "answer_only_keep",
    ),
    "binary_hybrid_consensus_group_keys": (
        "teacher_solver_candidate",
        "selection_tier",
        "num_examples",
    ),
    "binary_hybrid_consensus_exact_fields": {
        "bit_hybrid_consensus_ready": "True",
        "auto_solver_match": "True",
    },
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_structured_recommended": 16,
    "binary_structured_recommended_group_keys": (
        "bit_structured_formula_abstract_family",
        "num_examples",
        "bit_no_candidate_positions",
    ),
    "binary_structured_recommended_min_fields": {
        "bit_no_candidate_positions": 4,
        "bit_structured_formula_safe_support": 3,
    },
    "binary_structured_recommended_exact_fields": {
        "teacher_solver_candidate": "binary_structured_byte_formula",
        "bit_structured_formula_safe": "True",
        "bit_multi_candidate_positions": 0,
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V65_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_hybrid_consensus": 8,
    "binary_hybrid_consensus_allowed_tiers": (
        "verified_trace_ready",
        "answer_only_keep",
    ),
    "binary_hybrid_consensus_group_keys": (
        "teacher_solver_candidate",
        "selection_tier",
        "num_examples",
    ),
    "binary_hybrid_consensus_exact_fields": {
        "bit_hybrid_consensus_ready": "True",
        "auto_solver_match": "True",
    },
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_structured_recommended": 24,
    "binary_structured_recommended_group_keys": (
        "bit_structured_formula_abstract_family",
        "num_examples",
        "bit_no_candidate_positions",
    ),
    "binary_structured_recommended_min_fields": {
        "bit_no_candidate_positions": 3,
        "bit_structured_formula_safe_support": 2,
    },
    "binary_structured_recommended_exact_fields": {
        "teacher_solver_candidate": "binary_structured_byte_formula",
        "bit_structured_formula_safe": "True",
        "bit_multi_candidate_positions": 0,
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V66_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_hybrid_consensus": 16,
    "binary_hybrid_consensus_allowed_tiers": (
        "verified_trace_ready",
        "answer_only_keep",
    ),
    "binary_hybrid_consensus_group_keys": (
        "teacher_solver_candidate",
        "selection_tier",
        "num_examples",
    ),
    "binary_hybrid_consensus_exact_fields": {
        "bit_hybrid_consensus_ready": "True",
        "auto_solver_match": "True",
    },
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_structured_recommended": 16,
    "binary_structured_recommended_group_keys": (
        "bit_structured_formula_abstract_family",
        "num_examples",
        "bit_no_candidate_positions",
    ),
    "binary_structured_recommended_min_fields": {
        "bit_no_candidate_positions": 4,
        "bit_structured_formula_safe_support": 3,
    },
    "binary_structured_recommended_exact_fields": {
        "teacher_solver_candidate": "binary_structured_byte_formula",
        "bit_structured_formula_safe": "True",
        "bit_multi_candidate_positions": 0,
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V67_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_hybrid_consensus": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_structured_recommended": 8,
    "binary_structured_recommended_group_keys": (
        "bit_structured_formula_abstract_family",
        "num_examples",
        "bit_no_candidate_positions",
    ),
    "binary_structured_recommended_min_fields": {
        "bit_no_candidate_positions": 5,
        "bit_structured_formula_safe_support": 10,
    },
    "binary_structured_recommended_exact_fields": {
        "teacher_solver_candidate": "binary_structured_byte_formula",
        "bit_structured_formula_safe": "True",
        "bit_multi_candidate_positions": "0",
    },
    "binary_structured_answer_only_abstract_safe": 8,
    "binary_structured_answer_only_abstract_safe_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_no_candidate_positions",
        "num_examples",
    ),
    "binary_structured_answer_only_abstract_safe_min_fields": {
        "bit_no_candidate_positions": 6,
    },
    "binary_structured_answer_only_abstract_safe_exact_fields": {
        "boxed_safe": "True",
        "answer_only_ready": "True",
        "bit_structured_formula_abstract_safe": "True",
        "bit_structured_formula_abstract_error_rows": "0",
        "bit_multi_candidate_positions": "0",
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V68_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_hybrid_consensus": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_structured_recommended": 8,
    "binary_structured_recommended_group_keys": (
        "bit_structured_formula_abstract_family",
        "num_examples",
        "bit_no_candidate_positions",
    ),
    "binary_structured_recommended_min_fields": {
        "bit_no_candidate_positions": 5,
        "bit_structured_formula_safe_support": 4,
    },
    "binary_structured_recommended_exact_fields": {
        "teacher_solver_candidate": "binary_structured_byte_formula",
        "bit_structured_formula_safe": "True",
        "bit_multi_candidate_positions": "0",
    },
    "binary_structured_answer_only_abstract_safe": 12,
    "binary_structured_answer_only_abstract_safe_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_no_candidate_positions",
        "num_examples",
    ),
    "binary_structured_answer_only_abstract_safe_min_fields": {
        "bit_no_candidate_positions": 5,
    },
    "binary_structured_answer_only_abstract_safe_exact_fields": {
        "boxed_safe": "True",
        "answer_only_ready": "True",
        "bit_structured_formula_abstract_safe": "True",
        "bit_structured_formula_abstract_error_rows": "0",
        "bit_multi_candidate_positions": "0",
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V69_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_hybrid_consensus": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_structured_answer_only_abstract_safe": 16,
    "binary_structured_answer_only_abstract_safe_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_no_candidate_positions",
        "num_examples",
    ),
    "binary_structured_answer_only_abstract_safe_min_fields": {
        "bit_no_candidate_positions": 5,
    },
    "binary_structured_answer_only_abstract_safe_exact_fields": {
        "boxed_safe": "True",
        "answer_only_ready": "True",
        "bit_structured_formula_abstract_safe": "True",
        "bit_structured_formula_abstract_error_rows": "0",
        "bit_multi_candidate_positions": "0",
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V70_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_exact_trace_formula": 16,
    "binary_exact_trace_formula_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_formula_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_exact_trace_formula_startswith_fields": {
        "answer": "0",
    },
    "binary_exact_trace_abstract": 8,
    "binary_exact_trace_abstract_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_abstract_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_exact_trace_abstract_startswith_fields": {
        "answer": "0",
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V71_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_exact_trace_formula": 16,
    "binary_exact_trace_formula_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_formula_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_exact_trace_abstract": 8,
    "binary_exact_trace_abstract_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_abstract_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V72_AUGMENT_QUOTAS = {
    "binary_candidates": 8,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_exact_trace_formula": 12,
    "binary_exact_trace_formula_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_formula_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_exact_trace_abstract": 8,
    "binary_exact_trace_abstract_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_abstract_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_exact_trace_not_formula": 4,
    "binary_exact_trace_not_formula_group_keys": (
        "bit_not_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_not_formula_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V73_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_exact_trace_formula": 16,
    "binary_exact_trace_formula_boxed_twin": 16,
    "binary_exact_trace_formula_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_formula_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_exact_trace_abstract": 8,
    "binary_exact_trace_abstract_boxed_twin": 8,
    "binary_exact_trace_abstract_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_abstract_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V74_AUGMENT_QUOTAS = {
    "binary_candidates": 8,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_exact_trace_formula": 12,
    "binary_exact_trace_formula_boxed_twin": 12,
    "binary_exact_trace_formula_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_formula_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_exact_trace_abstract": 8,
    "binary_exact_trace_abstract_boxed_twin": 8,
    "binary_exact_trace_abstract_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_abstract_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_exact_trace_not_formula": 4,
    "binary_exact_trace_not_formula_boxed_twin": 4,
    "binary_exact_trace_not_formula_group_keys": (
        "bit_not_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_not_formula_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V75_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_exact_trace_formula": 16,
    "binary_exact_trace_formula_boxed_twin": 16,
    "binary_exact_trace_formula_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_formula_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_exact_trace_formula_startswith_fields": {
        "answer": "0",
    },
    "binary_exact_trace_abstract": 8,
    "binary_exact_trace_abstract_boxed_twin": 8,
    "binary_exact_trace_abstract_group_keys": (
        "bit_structured_formula_abstract_family",
        "bit_structured_formula_name",
        "bit_no_candidate_positions",
    ),
    "binary_exact_trace_abstract_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_exact_trace_abstract_startswith_fields": {
        "answer": "0",
    },
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V76_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_prompt_local_current_structured_closure": 16,
    "binary_prompt_local_current_structured_closure_min_fields": {
        "bit_no_candidate_positions": 6,
        "num_examples": 8,
    },
    "binary_prompt_local_current_structured_closure_exact_fields": {
        "safe_prediction_count": 1,
        "safe_formula_count": 1,
        "bit_multi_candidate_positions": 0,
    },
    "binary_prompt_local_current_structured_closure_group_keys": ("safe_formulas", "num_examples"),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V77_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_prompt_local_current_structured_closure": 16,
    "binary_prompt_local_current_structured_closure_boxed_done_twin": 16,
    "binary_prompt_local_current_structured_closure_min_fields": {
        "bit_no_candidate_positions": 6,
        "num_examples": 8,
    },
    "binary_prompt_local_current_structured_closure_max_fields": {
        "safe_formula_count": 2,
    },
    "binary_prompt_local_current_structured_closure_exact_fields": {
        "safe_prediction_count": 1,
        "bit_multi_candidate_positions": 0,
    },
    "binary_prompt_local_current_structured_closure_group_keys": ("safe_formulas", "num_examples"),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V78_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_prompt_local_current_structured_closure": 16,
    "binary_prompt_local_current_structured_closure_boxed_done_twin": 16,
    "binary_prompt_local_current_structured_closure_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_prompt_local_current_structured_closure_max_fields": {
        "safe_formula_count": 2,
    },
    "binary_prompt_local_current_structured_closure_exact_fields": {
        "safe_prediction_count": 1,
        "bit_multi_candidate_positions": 0,
    },
    "binary_prompt_local_current_structured_closure_startswith_fields": {
        "answer": "0",
    },
    "binary_prompt_local_current_structured_closure_group_keys": ("safe_formulas", "num_examples"),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V79_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_prompt_local_current_structured_boxed_done": 16,
    "binary_prompt_local_current_structured_boxed_done_min_fields": {
        "bit_no_candidate_positions": 6,
        "num_examples": 8,
    },
    "binary_prompt_local_current_structured_boxed_done_max_fields": {
        "safe_formula_count": 2,
    },
    "binary_prompt_local_current_structured_boxed_done_exact_fields": {
        "safe_prediction_count": 1,
        "bit_multi_candidate_positions": 0,
    },
    "binary_prompt_local_current_structured_boxed_done_group_keys": ("safe_formulas", "num_examples"),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V80_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_prompt_local_current_structured_boxed_done": 16,
    "binary_prompt_local_current_structured_boxed_done_min_fields": {
        "bit_no_candidate_positions": 5,
        "num_examples": 8,
    },
    "binary_prompt_local_current_structured_boxed_done_max_fields": {
        "safe_formula_count": 2,
    },
    "binary_prompt_local_current_structured_boxed_done_exact_fields": {
        "safe_prediction_count": 1,
        "bit_multi_candidate_positions": 0,
    },
    "binary_prompt_local_current_structured_boxed_done_startswith_fields": {
        "answer": "0",
    },
    "binary_prompt_local_current_structured_boxed_done_group_keys": ("safe_formulas", "num_examples"),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V81_AUGMENT_QUOTAS = {
    "binary_candidates": 0,
    "binary_answer_only_bit_other": 0,
    "symbol_verified": 0,
    "symbol_answer_only": 0,
    "symbol_manual": 0,
    "symbol_glyph_answer_only": 0,
    "binary_affine_verified": 12,
    "binary_structured_answer_only": 8,
    "binary_prompt_local_current_structured_strict_boxed_only": 16,
    "binary_prompt_local_current_structured_strict_boxed_only_min_fields": {
        "bit_no_candidate_positions": 6,
        "num_examples": 8,
    },
    "binary_prompt_local_current_structured_strict_boxed_only_max_fields": {
        "safe_formula_count": 2,
    },
    "binary_prompt_local_current_structured_strict_boxed_only_exact_fields": {
        "safe_prediction_count": 1,
        "bit_multi_candidate_positions": 0,
    },
    "binary_prompt_local_current_structured_strict_boxed_only_group_keys": ("safe_formulas", "num_examples"),
    "symbol_formula_verified": 4,
    "symbol_formula_answer_only": 0,
    "text_verified_anchor_mod": 8,
}
FUSION_V82_AUGMENT_QUOTAS = {
    **FUSION_V79_AUGMENT_QUOTAS,
    "binary_prompt_local_current_structured_boxed_only_twin": 16,
}
FUSION_V83_AUGMENT_QUOTAS = {
    **FUSION_V79_AUGMENT_QUOTAS,
    "binary_prompt_local_current_structured_boxed_done": 32,
}
FUSION_V84_AUGMENT_QUOTAS = {
    **FUSION_V79_AUGMENT_QUOTAS,
    "binary_structured_answer_only": 24,
}
FUSION_V113_AUGMENT_QUOTAS = dict(FUSION_V79_AUGMENT_QUOTAS)
FUSION_V114_AUGMENT_QUOTAS = dict(FUSION_V67_AUGMENT_QUOTAS)
FUSION_V115_AUGMENT_QUOTAS = {
    **FUSION_V79_AUGMENT_QUOTAS,
    "binary_structured_recommended": FUSION_V67_AUGMENT_QUOTAS["binary_structured_recommended"],
    "binary_structured_recommended_group_keys": FUSION_V67_AUGMENT_QUOTAS[
        "binary_structured_recommended_group_keys"
    ],
    "binary_structured_recommended_min_fields": FUSION_V67_AUGMENT_QUOTAS[
        "binary_structured_recommended_min_fields"
    ],
    "binary_structured_recommended_exact_fields": FUSION_V67_AUGMENT_QUOTAS[
        "binary_structured_recommended_exact_fields"
    ],
    "binary_structured_answer_only_abstract_safe": FUSION_V67_AUGMENT_QUOTAS[
        "binary_structured_answer_only_abstract_safe"
    ],
    "binary_structured_answer_only_abstract_safe_group_keys": FUSION_V67_AUGMENT_QUOTAS[
        "binary_structured_answer_only_abstract_safe_group_keys"
    ],
    "binary_structured_answer_only_abstract_safe_min_fields": FUSION_V67_AUGMENT_QUOTAS[
        "binary_structured_answer_only_abstract_safe_min_fields"
    ],
    "binary_structured_answer_only_abstract_safe_exact_fields": FUSION_V67_AUGMENT_QUOTAS[
        "binary_structured_answer_only_abstract_safe_exact_fields"
    ],
}
FUSION_V119_AUGMENT_QUOTAS = {
    "binary_prompt_local_current_bit_other_manual_boxed_done": 8,
    "binary_prompt_local_current_bit_other_manual_boxed_done_group_keys": (
        "safe_formulas",
        "num_examples",
    ),
    "binary_prompt_local_current_bit_other_manual_boxed_done_min_fields": {
        "num_examples": 9,
    },
    "binary_prompt_local_current_bit_other_manual_boxed_done_max_fields": {
        "safe_formula_count": 4,
    },
    "binary_prompt_local_current_bit_other_manual_boxed_done_exact_fields": {
        "safe_prediction_count": 1,
    },
}
FUSION_V120_AUGMENT_QUOTAS = {
    **FUSION_V119_AUGMENT_QUOTAS,
    "binary_prompt_local_current_bit_other_manual_boxed_done_min_fields": {
        "num_examples": 8,
    },
    "binary_prompt_local_current_bit_other_manual_boxed_done": 12,
}
FUSION_V121_AUGMENT_QUOTAS = {
    **FUSION_V119_AUGMENT_QUOTAS,
    "binary_prompt_local_current_bit_other_manual_boxed_only_twin": 8,
}
FUSION_V122_AUGMENT_QUOTAS = {
    **FUSION_V119_AUGMENT_QUOTAS,
    "binary_hybrid_consensus": 8,
    "binary_hybrid_consensus_allowed_tiers": ("verified_trace_ready",),
    "binary_hybrid_consensus_group_keys": (
        "teacher_solver_candidate",
        "num_examples",
    ),
    "binary_hybrid_consensus_exact_fields": {
        "bit_hybrid_consensus_ready": "True",
        "auto_solver_match": "True",
    },
}
FUSION_V128_AUGMENT_QUOTAS = dict(FUSION_V67_AUGMENT_QUOTAS)
FUSION_V129_AUGMENT_QUOTAS = dict(FUSION_V79_AUGMENT_QUOTAS)
HOLDOUT_FOLDS = 5
BOXED_PATTERN = __import__("re").compile(r"\\boxed\{([^}]*)(?:\}|$)")
FINAL_ANSWER_PATTERNS = (
    r"The final answer is:\s*([^\n]+)",
    r"Final answer is:\s*([^\n]+)",
    r"Final answer\s*[:：]\s*([^\n]+)",
    r"final answer\s*[:：]\s*([^\n]+)",
)
NUMBER_PATTERN = __import__("re").compile(r"-?\d+(?:\.\d+)?")
BIT8_PATTERN = __import__("re").compile(r"^[01]{8}$")
PHASE0_BINARY_EXAMPLE_PATTERN = __import__("re").compile(r"^([01]{8}) -> ([01]{8})$")
PHASE0_BINARY_QUERY_PATTERN = __import__("re").compile(r"Now, determine the output for: ([01]{8})")
PHASE0_BINARY_STRUCTURED_BYTE_BINARY_OPERATIONS = {
    "xor": lambda a, b: a ^ b,
    "and": lambda a, b: a & b,
    "or": lambda a, b: a | b,
}
PHASE0_BINARY_STRUCTURED_BYTE_TERNARY_OPERATIONS = {
    "choose": lambda selector, when_true, when_false: (selector & when_true) | (((~selector) & 0xFF) & when_false),
    "majority": lambda a, b, c: (a & b) | (a & c) | (b & c),
}
PHASE0_SYMBOL_NUMERIC_EXAMPLE_PATTERN = __import__("re").compile(r"^(\d{2})(.)(\d{2}) = (.+)$")
PHASE0_SYMBOL_NUMERIC_QUERY_PATTERN = __import__("re").compile(
    r"^Now, determine the result for: (\d{2})(.)(\d{2})$"
)
PHASE0_SYMBOL_NUMERIC_REVERSE_SUFFIX = "__rev_in1_rev_out1"
PHASE0_SYMBOL_NUMERIC_REVERSE_OUTPUT_ONLY_SUFFIX = "__rev_in0_rev_out1"
PHASE0_SYMBOL_NUMERIC_REVERSE_INPUT_ONLY_SUFFIX = "__rev_in1_rev_out0"
FAMILY_SHORT = {
    "gravity_constant": "gravity",
    "unit_conversion": "unit",
    "roman_numeral": "roman",
    "text_decryption": "text",
    "bit_manipulation": "binary",
    "symbol_equation": "symbol",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, *, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {path}")
        return [dict(row) for row in reader]


def write_csv_rows(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_jsonl_records(path: Path, records: Sequence[dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def parse_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        if not text:
            return default
        return int(float(text))
    except (TypeError, ValueError):
        return default


def matches_numeric_field_filters(
    row: dict[str, str],
    *,
    min_int_fields: dict[str, int] | None = None,
    max_int_fields: dict[str, int] | None = None,
    exact_fields: dict[str, Any] | None = None,
    startswith_fields: dict[str, str] | None = None,
) -> bool:
    if min_int_fields:
        for key, minimum in min_int_fields.items():
            if parse_int(row.get(key), minimum - 1) < minimum:
                return False
    if max_int_fields:
        for key, maximum in max_int_fields.items():
            if parse_int(row.get(key), maximum + 1) > maximum:
                return False
    if exact_fields:
        for key, expected in exact_fields.items():
            if isinstance(expected, int):
                if parse_int(row.get(key), expected - 1) != expected:
                    return False
            elif str(row.get(key, "")).strip() != str(expected).strip():
                return False
    if startswith_fields:
        for key, expected_prefix in startswith_fields.items():
            if not str(row.get(key, "")).strip().startswith(str(expected_prefix).strip()):
                return False
    return True


def parse_float(value: Any, default: float | None = None) -> float | None:
    try:
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def stable_mod(text: str, mod: int) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) % mod


def prompt_len_bucket(length: int) -> str:
    if length < 300:
        return "<300"
    if length < 400:
        return "300-399"
    if length < 500:
        return "400-499"
    if length < 600:
        return "500-599"
    return "600+"


def load_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in ("mlx-lm", "mlx", "transformers", "pyyaml"):
        try:
            versions[name] = importlib_metadata.version(name)
        except importlib_metadata.PackageNotFoundError:
            versions[name] = "not-installed"
    return versions


def resolve_hf_snapshot(model_root: Path) -> Path:
    model_root = model_root.expanduser().resolve()
    if (model_root / "config.json").exists():
        return model_root
    snapshots_dir = model_root / "snapshots"
    if not snapshots_dir.exists():
        raise FileNotFoundError(
            f"Model root must contain config.json or snapshots/: {model_root}"
        )
    main_ref = model_root / "refs" / "main"
    if main_ref.exists():
        snapshot_name = main_ref.read_text(encoding="utf-8").strip()
        candidate = snapshots_dir / snapshot_name
        if candidate.exists():
            return candidate
    snapshots = sorted(path for path in snapshots_dir.iterdir() if path.is_dir())
    if not snapshots:
        raise FileNotFoundError(f"No snapshots found under: {snapshots_dir}")
    return snapshots[-1]


def build_shadow_model_dir(model_root: Path, shadow_dir: Path, *, force: bool = False) -> Path:
    source_snapshot = resolve_hf_snapshot(model_root)
    manifest_path = shadow_dir / "shadow_manifest.json"
    current_manifest = load_json(manifest_path, default={}) or {}
    tokenizer_config_path = shadow_dir / "tokenizer_config.json"
    rebuild = force
    if not shadow_dir.exists():
        rebuild = True
    elif current_manifest.get("source_snapshot") != str(source_snapshot):
        rebuild = True
    elif not tokenizer_config_path.exists():
        rebuild = True
    else:
        try:
            tokenizer_config = json.loads(tokenizer_config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rebuild = True
        else:
            rebuild = tokenizer_config.get("tokenizer_class") != "PreTrainedTokenizerFast"

    if rebuild:
        if shadow_dir.exists():
            shutil.rmtree(shadow_dir)
        ensure_dir(shadow_dir)
        for child in source_snapshot.iterdir():
            if child.name == "tokenizer_config.json":
                continue
            (shadow_dir / child.name).symlink_to(child)
        tokenizer_config = json.loads(
            (source_snapshot / "tokenizer_config.json").read_text(encoding="utf-8")
        )
        tokenizer_config["tokenizer_class"] = "PreTrainedTokenizerFast"
        tokenizer_config.setdefault("clean_up_tokenization_spaces", False)
        write_json(tokenizer_config_path, tokenizer_config)
        write_json(
            manifest_path,
            {
                "created_at": utc_now(),
                "source_snapshot": str(source_snapshot),
                "tokenizer_class_patch": "PreTrainedTokenizerFast",
            },
        )
    return shadow_dir


def load_phase2_training_rows(path: Path) -> list[dict[str, str]]:
    rows = load_csv_rows(path)
    if len(rows) != EXPECTED_PHASE2_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_PHASE2_ROWS} rows in {path}, found {len(rows)}"
        )
    validate_phase2_columns(path, rows)
    return rows


def load_strong_baseline_cot_rows(path: Path) -> list[dict[str, str]]:
    rows = load_csv_rows(path)
    validate_strong_baseline_columns(path, rows)
    normalized_rows: list[dict[str, str]] = []
    for raw_row in rows:
        row = {str(key): "" if value is None else str(value) for key, value in raw_row.items()}
        row_id = str(row.get("id", "")).strip()
        prompt = str(row.get("prompt", "")).strip()
        answer = str(row.get("answer", "")).strip()
        source_type = str(row.get("type", "")).strip()
        generated_cot = str(row.get("generated_cot", "")).strip()
        if not row_id:
            raise ValueError(f"Strong baseline row is missing id in {path}")
        if not prompt:
            raise ValueError(f"Strong baseline row {row_id} is missing prompt")
        if not answer:
            raise ValueError(f"Strong baseline row {row_id} is missing answer")
        if not generated_cot or generated_cot.lower() == "nan":
            raise ValueError(f"Strong baseline row {row_id} is missing generated_cot")
        label = STRONG_BASELINE_TYPE_TO_LABEL.get(source_type, "")
        if not label:
            raise ValueError(f"Unsupported strong baseline type for row {row_id}: {source_type!r}")
        normalized_rows.append(
            {
                "id": row_id,
                "prompt": prompt,
                "answer": answer,
                "generated_cot": generated_cot,
                "label": label,
                "assistant_style": "cot_boxed_notebook",
                "source_selection_tier": "verified_trace_ready",
                "baseline_source_type": source_type,
            }
        )
    return normalized_rows


def load_training_source_rows(path: Path, *, profile: str) -> list[dict[str, str]]:
    normalized_profile = str(profile).strip().lower() or "baseline"
    if normalized_profile.startswith("strong-baseline-cot-v2"):
        return load_strong_baseline_cot_rows(path)
    return load_phase2_training_rows(path)


@lru_cache(maxsize=1)
def load_strong_baseline_cot_v2_sample_index() -> dict[str, dict[str, str]]:
    sampled_rows, _ = build_strong_baseline_cot_v2_rows(
        load_strong_baseline_cot_rows(DEFAULT_STRONG_BASELINE_COT_CSV)
    )
    return {
        str(row.get("id", "")).strip(): {
            str(key): "" if value is None else str(value) for key, value in row.items()
        }
        for row in sampled_rows
        if str(row.get("id", "")).strip()
    }


@lru_cache(maxsize=1)
def load_strong_baseline_cot_v2_sample_rows() -> tuple[dict[str, str], ...]:
    return tuple(load_strong_baseline_cot_v2_sample_index().values())


def validate_phase2_columns(path: Path, rows: Sequence[dict[str, str]]) -> None:
    if rows:
        actual_columns = list(rows[0].keys())
        if actual_columns != EXPECTED_PHASE2_COLUMNS:
            raise ValueError(
                f"Unexpected CSV columns in {path}: {actual_columns} "
                f"(expected {EXPECTED_PHASE2_COLUMNS})"
            )


def validate_strong_baseline_columns(path: Path, rows: Sequence[dict[str, str]]) -> None:
    if rows:
        actual_columns = list(rows[0].keys())
        if actual_columns != EXPECTED_STRONG_BASELINE_COLUMNS:
            raise ValueError(
                f"Unexpected CSV columns in {path}: {actual_columns} "
                f"(expected {EXPECTED_STRONG_BASELINE_COLUMNS})"
            )


@lru_cache(maxsize=1)
def load_phase0_analysis_index() -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for raw_row in load_csv_rows(DEFAULT_PHASE0_ANALYSIS_CSV):
        row = {str(key): "" if value is None else str(value) for key, value in raw_row.items()}
        row_id = str(row.get("id", "")).strip()
        if row_id:
            index[row_id] = row
    return index


def parse_family_payload(row: dict[str, str]) -> dict[str, Any]:
    text = str(row.get("family_analysis_json", "")).strip()
    if not text:
        return {}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


@dataclass(frozen=True)
class ExprNode:
    name: str
    args: tuple["ExprNode", ...] = ()


def split_top_level_args(text: str) -> list[str]:
    args: list[str] = []
    depth = 0
    current: list[str] = []
    for char in text:
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError(f"Unbalanced expression: {text}")
        current.append(char)
    if depth != 0:
        raise ValueError(f"Unbalanced expression: {text}")
    tail = "".join(current).strip()
    if tail:
        args.append(tail)
    return args


def parse_expr(text: str) -> ExprNode:
    expr = text.strip()
    if not expr:
        raise ValueError("Expression is empty")
    if "(" not in expr:
        return ExprNode(name=expr, args=())
    if not expr.endswith(")"):
        raise ValueError(f"Malformed expression: {expr}")
    name, rest = expr.split("(", 1)
    inner = rest[:-1]
    args = tuple(parse_expr(part) for part in split_top_level_args(inner))
    return ExprNode(name=name.strip(), args=args)


def expr_to_text(node: ExprNode) -> str:
    if not node.args:
        return node.name
    return f"{node.name}({','.join(expr_to_text(arg) for arg in node.args)})"


def format_byte(value: int) -> str:
    return format(value & 0xFF, "08b")


def rotate_left(value: int, shift: int) -> int:
    shift %= 8
    value &= 0xFF
    return ((value << shift) | (value >> (8 - shift))) & 0xFF


def rotate_right(value: int, shift: int) -> int:
    shift %= 8
    value &= 0xFF
    return ((value >> shift) | (value << (8 - shift))) & 0xFF


def nibble_swap(value: int) -> int:
    value &= 0xFF
    return ((value & 0x0F) << 4) | ((value & 0xF0) >> 4)


def eval_atom(name: str, query_value: int) -> int:
    token = name.strip()
    if token in {"x", "query"}:
        return query_value & 0xFF
    if token == "nibble_swap":
        return nibble_swap(query_value)
    if token in {"rshift", "shr"}:
        return (query_value >> 1) & 0xFF
    if token in {"lshift", "shl"}:
        return (query_value << 1) & 0xFF
    if token in {"rol", "lrot"}:
        return rotate_left(query_value, 1)
    if token in {"ror", "rrot"}:
        return rotate_right(query_value, 1)
    match = re.fullmatch(r"(shl|shr|rol|ror|lrot|rrot)(\d+)", token)
    if match:
        op = match.group(1)
        shift = int(match.group(2))
        if op == "shl":
            return (query_value << shift) & 0xFF
        if op == "shr":
            return (query_value >> shift) & 0xFF
        if op in {"rol", "lrot"}:
            return rotate_left(query_value, shift)
        if op in {"ror", "rrot"}:
            return rotate_right(query_value, shift)
    raise ValueError(f"Unsupported atom: {token}")


def eval_expr(node: ExprNode, query_value: int) -> int:
    if not node.args:
        return eval_atom(node.name, query_value)
    values = [eval_expr(arg, query_value) for arg in node.args]
    name = node.name
    if name == "not":
        if len(values) != 1:
            raise ValueError("not() expects one arg")
        return (~values[0]) & 0xFF
    if name == "xor":
        if len(values) != 2:
            raise ValueError("xor() expects two args")
        return (values[0] ^ values[1]) & 0xFF
    if name == "and":
        if len(values) != 2:
            raise ValueError("and() expects two args")
        return (values[0] & values[1]) & 0xFF
    if name == "or":
        if len(values) != 2:
            raise ValueError("or() expects two args")
        return (values[0] | values[1]) & 0xFF
    if name == "majority":
        if len(values) != 3:
            raise ValueError("majority() expects three args")
        return ((values[0] & values[1]) | (values[0] & values[2]) | (values[1] & values[2])) & 0xFF
    if name == "choose":
        if len(values) != 3:
            raise ValueError("choose() expects three args")
        a, b, c = values
        return ((a & b) | ((~a) & c)) & 0xFF
    raise ValueError(f"Unsupported function: {name}")


def resolve_binary_rule(row: dict[str, str], payload: dict[str, Any]) -> tuple[str, str] | None:
    direct_candidates = [
        str(row.get("bit_structured_formula_name", "")).strip(),
        str(payload.get("structured_formula_name", "")).strip(),
        str(row.get("bit_not_structured_formula_name", "")).strip(),
        str(payload.get("not_structured_formula_name", "")).strip(),
    ]
    for candidate in direct_candidates:
        if candidate:
            return candidate, "exact_formula"
    names = str(row.get("bit_byte_transform_names", "")).strip()
    if names:
        split_names = [name.strip() for name in names.split("|") if name.strip()]
        if len(split_names) == 1:
            return split_names[0], "byte_transform"
    payload_names = payload.get("byte_transform_names", [])
    if isinstance(payload_names, list):
        cleaned = [str(item).strip() for item in payload_names if str(item).strip()]
        if len(cleaned) == 1:
            return cleaned[0], "byte_transform"
    return None


def extract_binary_example_pairs(prompt: str) -> list[tuple[str, str]]:
    pairs = re.findall(r"([01]{8})\s*->\s*([01]{8})", prompt)
    if not pairs:
        raise ValueError("Binary prompt did not contain any example input/output pairs")
    return [(left, right) for left, right in pairs]


def collect_expr_nodes(node: ExprNode, steps: list[ExprNode], seen: set[str]) -> None:
    for child in node.args:
        collect_expr_nodes(child, steps, seen)
    text = expr_to_text(node)
    if text in {"x", "query"} or text in seen:
        return
    seen.add(text)
    steps.append(node)


def support_step_label(node: ExprNode, root_text: str) -> str:
    text = expr_to_text(node)
    if text == root_text and node.args:
        return node.name
    return text


def expr_to_query_text(node: ExprNode) -> str:
    if not node.args:
        if node.name in {"x", "query"}:
            return "x"
        return f"{node.name}(x)"
    return f"{node.name}({','.join(expr_to_query_text(arg) for arg in node.args)})"


def render_binary_support_steps(rule_text: str, input_bits: str) -> tuple[list[str], str]:
    if not re.fullmatch(r"[01]{8}", input_bits):
        raise ValueError(f"Binary support input is not an exact 8-bit string: {input_bits}")
    root = parse_expr(rule_text)
    root_text = expr_to_text(root)
    query_value = int(input_bits, 2)
    steps: list[ExprNode] = []
    collect_expr_nodes(root, steps, set())
    rendered_steps = [
        f"{support_step_label(node, root_text)}={format_byte(eval_expr(node, query_value))}"
        for node in steps
    ]
    return rendered_steps, format_byte(eval_expr(root, query_value))


def build_exact_binary_program_trace(row: dict[str, str]) -> str:
    query_text = str(row.get("query_raw") or row.get("bit_query_binary") or "").strip()
    answer = str(row.get("answer", "")).strip()
    if not re.fullmatch(r"[01]{8}", query_text):
        raise ValueError(f"Binary query is not an exact 8-bit string: {row.get('id', '')}")
    if not re.fullmatch(r"[01]{8}", answer):
        raise ValueError(f"Binary answer is not an exact 8-bit string: {row.get('id', '')}")
    payload = parse_family_payload(row)
    resolved = resolve_binary_rule(row, payload)
    if resolved is None:
        raise ValueError(f"Unable to resolve an exact binary rule for {row.get('id', '')}")
    rule_text, _rule_source = resolved
    support_pairs = extract_binary_example_pairs(str(row.get("prompt", "")))[:2]
    support_lines: list[str] = []
    for input_bits, output_bits in support_pairs:
        rendered_steps, recomputed = render_binary_support_steps(rule_text, input_bits)
        if recomputed != output_bits:
            raise ValueError(
                f"Resolved rule {rule_text} does not reproduce support example for {row.get('id', '')}: "
                f"{input_bits} -> {output_bits} vs {recomputed}"
            )
        support_lines.append(f"- {input_bits} -> {output_bits} because {', '.join(rendered_steps)}")
    root = parse_expr(rule_text)
    root_value = format_byte(eval_expr(root, int(query_text, 2)))
    if root_value != answer:
        raise ValueError(
            f"Resolved rule {rule_text} does not reproduce query answer for {row.get('id', '')}: "
            f"{root_value} vs {answer}"
        )
    query_steps: list[ExprNode] = []
    collect_expr_nodes(root, query_steps, set())
    query_lines = [
        f"{expr_to_query_text(node)} = {format_byte(eval_expr(node, int(query_text, 2)))}"
        for node in query_steps
    ]
    lines = [
        "<think>",
        "Check examples:",
        *support_lines,
        f"So the rule is {rule_text}.",
        f"Query x = {query_text}",
        *query_lines,
        f"Final answer = {answer}",
        "</think>",
    ]
    return "\n".join(lines)


def infer_candidate_selection_tier(row: dict[str, str]) -> str:
    tier = str(row.get("selection_tier", "")).strip().lower()
    if tier:
        return tier
    if parse_bool(row.get("verified_trace_ready")):
        return "verified_trace_ready"
    if parse_bool(row.get("answer_only_ready")):
        return "answer_only_keep"
    return ""


def make_phase2_row_from_candidate(
    row: dict[str, str],
    *,
    label: str | None = None,
    assistant_style: str = "boxed_only",
    source_selection_tier: str | None = None,
    generated_cot: str = "",
    prompt_override: str | None = None,
) -> dict[str, str]:
    row_id = str(row.get("id", "")).strip()
    prompt = str(prompt_override if prompt_override is not None else row.get("prompt", "")).strip()
    answer = str(row.get("answer", "")).strip()
    if not row_id:
        raise ValueError("Augmentation row is missing id")
    if not prompt:
        raise ValueError(f"Augmentation row {row_id} is missing prompt")
    if not answer:
        raise ValueError(f"Augmentation row {row_id} is missing answer")
    resolved_label = str(label or FAMILY_SHORT.get(str(row.get("family", "")).strip(), "")).strip()
    if not resolved_label:
        raise ValueError(f"Unable to infer phase2 label for augmentation row {row_id}")
    resolved_tier = str(source_selection_tier or infer_candidate_selection_tier(row)).strip().lower()
    if not resolved_tier:
        raise ValueError(f"Unable to infer selection tier for augmentation row {row_id}")
    resolved_generated_cot = str(generated_cot).strip()
    if assistant_style == "trace_boxed" and not resolved_generated_cot:
        raise ValueError(f"trace_boxed augmentation row {row_id} is missing generated_cot")
    return {
        "id": row_id,
        "prompt": prompt,
        "answer": answer,
        "generated_cot": resolved_generated_cot,
        "label": resolved_label,
        "assistant_style": assistant_style,
        "source_selection_tier": resolved_tier,
    }


def build_user_message(prompt: str) -> str:
    return f"{prompt}\n{BOXED_INSTRUCTION}"


def clean_notebook_cot_text(generated_cot: str) -> str:
    cleaned = re.sub(r"\\boxed\{[^}]*\}", "", str(generated_cot)).rstrip()
    cleaned = re.sub(r"</think>\s*$", "", cleaned).rstrip()
    return cleaned


def build_binary_strict_boxed_prompt(prompt: str) -> str:
    prompt_text = str(prompt).strip()
    if not prompt_text:
        raise ValueError("Binary strict boxed prompt cannot be empty.")
    return f"{prompt_text}\n{BINARY_STRICT_BOXED_SUFFIX}"


def build_strict_bare_boxed_prompt(prompt: str) -> str:
    prompt_text = str(prompt).strip()
    if not prompt_text:
        raise ValueError("Strict bare boxed prompt cannot be empty.")
    return f"{prompt_text}\n{STRICT_BARE_BOXED_SUFFIX}"


def build_binary_final_answer_closure(row: dict[str, str]) -> str:
    answer = str(row.get("answer", "")).strip()
    if not answer:
        raise ValueError("Binary closure row is missing answer.")
    return f"Final answer = {answer}."


def apply_chat_template_safe(
    tokenizer: Any,
    messages: Sequence[dict[str, str]],
    *,
    add_generation_prompt: bool,
    enable_thinking: bool,
) -> str:
    try:
        return tokenizer.apply_chat_template(
            list(messages),
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
            enable_thinking=enable_thinking,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            list(messages),
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
        )
    except Exception:
        rendered: list[str] = []
        for message in messages:
            rendered.append(f"<|{message['role']}|>\n{message['content']}")
        if add_generation_prompt:
            rendered.append("<|assistant|>\n<think>")
        return "\n".join(rendered)


def find_token_index_for_text_span(tokenizer: Any, full_text: str, target_text: str) -> int:
    if not target_text:
        raise ValueError("Cannot compute token offset for empty target text.")
    char_start = full_text.find(target_text)
    if char_start < 0:
        preview = full_text[:200].replace("\n", "\\n")
        target_preview = target_text[:120].replace("\n", "\\n")
        raise ValueError(
            f"Target text span was not found in rendered chat. target={target_preview!r} rendered_prefix={preview!r}"
        )
    offset_tokenizer = tokenizer if callable(tokenizer) else getattr(tokenizer, "_tokenizer", None)
    if offset_tokenizer is None or not callable(offset_tokenizer):
        raise TypeError(f"Tokenizer does not support text encoding for offset mapping: {type(tokenizer)!r}")
    encoded = offset_tokenizer(
        full_text,
        add_special_tokens=False,
        return_offsets_mapping=True,
    )
    for token_index, (start, end) in enumerate(encoded["offset_mapping"]):
        if start <= char_start < end or (start == end == char_start):
            return token_index
    raise ValueError(f"Unable to map assistant char offset {char_start} to a token offset.")


def maybe_patch_mlx_chat_dataset_enable_thinking() -> None:
    import mlx_lm.tuner.datasets as tuner_datasets

    if getattr(tuner_datasets, "_nemotron_enable_thinking_patch", False):
        return

    original_chat_init = tuner_datasets.ChatDataset.__init__
    original_completions_init = tuner_datasets.CompletionsDataset.__init__

    def patched_chat_init(
        self: Any,
        data: list[dict[str, Any]],
        tokenizer: Any,
        chat_key: str = "messages",
        mask_prompt: bool = False,
        enable_thinking: bool = False,
    ) -> None:
        original_chat_init(
            self,
            data=data,
            tokenizer=tokenizer,
            chat_key=chat_key,
            mask_prompt=mask_prompt,
        )
        self.enable_thinking = bool(enable_thinking)

    def patched_chat_process(self: Any, row: dict[str, Any]) -> tuple[list[int], int]:
        messages = row[self.chat_key]
        tools = row.get("tools", None)
        try:
            tokens = self.tokenizer.apply_chat_template(
                messages,
                tools=tools,
                enable_thinking=self.enable_thinking,
            )
        except TypeError:
            tokens = self.tokenizer.apply_chat_template(messages, tools=tools)
        if not self.mask_prompt:
            return (tokens, 0)
        if messages[-1].get("role") != "assistant":
            raise ValueError("mask_prompt=True requires the last chat message to have role='assistant'.")
        full_text = apply_chat_template_safe(
            self.tokenizer,
            messages,
            add_generation_prompt=False,
            enable_thinking=self.enable_thinking,
        )
        offset = find_token_index_for_text_span(
            self.tokenizer,
            full_text,
            str(messages[-1].get("content", "")),
        )
        return (tokens, offset)

    def patched_completions_init(
        self: Any,
        data: list[dict[str, Any]],
        tokenizer: Any,
        prompt_key: str,
        completion_key: str,
        mask_prompt: bool,
        enable_thinking: bool = False,
    ) -> None:
        original_completions_init(
            self,
            data=data,
            tokenizer=tokenizer,
            prompt_key=prompt_key,
            completion_key=completion_key,
            mask_prompt=mask_prompt,
        )
        self.enable_thinking = bool(enable_thinking)

    def patched_completions_process(self: Any, row: dict[str, Any]) -> tuple[list[int], int]:
        tools = row.get("tools", None)
        messages = [
            {"role": "user", "content": row[self.prompt_key]},
            {"role": "assistant", "content": row[self.completion_key]},
        ]
        try:
            tokens = self.tokenizer.apply_chat_template(
                messages,
                tools=tools,
                enable_thinking=self.enable_thinking,
            )
        except TypeError:
            tokens = self.tokenizer.apply_chat_template(messages, tools=tools)
        if not self.mask_prompt:
            return (tokens, 0)
        full_text = apply_chat_template_safe(
            self.tokenizer,
            messages,
            add_generation_prompt=False,
            enable_thinking=self.enable_thinking,
        )
        offset = find_token_index_for_text_span(
            self.tokenizer,
            full_text,
            str(row[self.completion_key]),
        )
        return (tokens, offset)

    def patched_create_dataset(data: Any, tokenizer: Any, config: Any) -> Any:
        mask_prompt = getattr(config, "mask_prompt", False)
        prompt_feature = getattr(config, "prompt_feature", "prompt")
        text_feature = getattr(config, "text_feature", "text")
        completion_feature = getattr(config, "completion_feature", "completion")
        chat_feature = getattr(config, "chat_feature", "messages")
        enable_thinking = getattr(config, "enable_thinking", False)
        sample = data[0]
        if prompt_feature in sample and completion_feature in sample:
            return tuner_datasets.CompletionsDataset(
                data,
                tokenizer,
                prompt_feature,
                completion_feature,
                mask_prompt,
                enable_thinking,
            )
        if chat_feature in sample:
            return tuner_datasets.ChatDataset(
                data,
                tokenizer,
                chat_key=chat_feature,
                mask_prompt=mask_prompt,
                enable_thinking=enable_thinking,
            )
        if text_feature in sample:
            if mask_prompt:
                raise ValueError("Prompt masking not supported for text dataset.")
            return tuner_datasets.TextDataset(data, tokenizer, text_key=text_feature)
        raise ValueError(
            "Unsupported data format, check the supported formats here:\n"
            "https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md#Data."
        )

    tuner_datasets.ChatDataset.__init__ = patched_chat_init
    tuner_datasets.ChatDataset.process = patched_chat_process
    tuner_datasets.CompletionsDataset.__init__ = patched_completions_init
    tuner_datasets.CompletionsDataset.process = patched_completions_process
    tuner_datasets.create_dataset = patched_create_dataset
    tuner_datasets._nemotron_enable_thinking_patch = True


def render_assistant_message(row: dict[str, str]) -> str:
    style = str(row.get("assistant_style", "")).strip()
    answer = str(row.get("answer", "")).strip()
    generated_cot = str(row.get("generated_cot", "")).strip()
    if style == "cot_boxed_notebook":
        if not generated_cot or generated_cot.lower() == "nan":
            raise ValueError(f"cot_boxed_notebook row {row.get('id', '')} is missing generated_cot")
        cot_cleaned = clean_notebook_cot_text(generated_cot)
        if cot_cleaned:
            return f"{cot_cleaned}\n</think>\n\\boxed{{{answer}}}"
        return f"</think>\n\\boxed{{{answer}}}"
    if style == "trace_boxed":
        if not generated_cot:
            raise ValueError(f"trace_boxed row {row.get('id', '')} is missing generated_cot")
        return f"{generated_cot}\n\n\\boxed{{{answer}}}"
    if style == "trace_boxed_done":
        if not generated_cot:
            raise ValueError(f"trace_boxed_done row {row.get('id', '')} is missing generated_cot")
        return f"{generated_cot}\n\n\\boxed{{{answer}}}\nDone."
    if style == "boxed_only":
        return f"\\boxed{{{answer}}}"
    if style == "boxed_only_done":
        return f"\\boxed{{{answer}}}\nDone."
    raise ValueError(f"Unsupported assistant_style: {style}")


def clone_phase2_row(row: dict[str, str]) -> dict[str, str]:
    return {str(key): "" if value is None else str(value) for key, value in row.items()}


def summarize_phase2_rows(rows: Sequence[dict[str, str]]) -> dict[str, Any]:
    by_label = Counter(str(row.get("label", "")).strip() or "unknown" for row in rows)
    by_label_and_style = Counter(
        (
            str(row.get("label", "")).strip() or "unknown",
            str(row.get("assistant_style", "")).strip() or "unknown",
        )
        for row in rows
    )
    by_label_and_tier = Counter(
        (
            str(row.get("label", "")).strip() or "unknown",
            str(row.get("source_selection_tier", "")).strip() or "unknown",
        )
        for row in rows
    )
    return {
        "rows": len(rows),
        "by_label": {label: count for label, count in sorted(by_label.items())},
        "by_label_and_style": {
            f"{label}|{style}": count
            for (label, style), count in sorted(by_label_and_style.items())
        },
        "by_label_and_tier": {
            f"{label}|{tier}": count
            for (label, tier), count in sorted(by_label_and_tier.items())
        },
    }


def select_augmentation_candidates(
    path: Path,
    *,
    existing_ids: set[str],
    family: str | None = None,
    template_subtype: str | None = None,
    allowed_tiers: set[str] | None = None,
    quota: int = 0,
    group_keys: Sequence[str] = (),
    hard_first: bool = True,
    min_int_fields: dict[str, int] | None = None,
    max_int_fields: dict[str, int] | None = None,
    exact_fields: dict[str, Any] | None = None,
    startswith_fields: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for raw_row in load_csv_rows(path):
        row = {str(key): "" if value is None else str(value) for key, value in raw_row.items()}
        row_id = str(row.get("id", "")).strip()
        if not row_id or row_id in existing_ids:
            continue
        if family and str(row.get("family", "")).strip() != family:
            continue
        if template_subtype and str(row.get("template_subtype", "")).strip() != template_subtype:
            continue
        if not str(row.get("prompt", "")).strip() or not str(row.get("answer", "")).strip():
            continue
        tier = infer_candidate_selection_tier(row)
        row["selection_tier"] = tier
        if allowed_tiers and tier not in allowed_tiers:
            continue
        if not matches_numeric_field_filters(
            row,
            min_int_fields=min_int_fields,
            max_int_fields=max_int_fields,
            exact_fields=exact_fields,
            startswith_fields=startswith_fields,
        ):
            continue
        candidates.append(row)
    if quota > 0 and len(candidates) > quota:
        selection_group_keys = tuple(group_keys) or ("template_subtype", "teacher_solver_candidate")
        return balanced_take(
            candidates,
            quota=quota,
            group_keys=selection_group_keys,
            hard_first=hard_first,
        )
    rank_fn = score_rank_high if hard_first else score_rank_low
    candidates.sort(key=rank_fn)
    return candidates


def select_joined_augmentation_candidates(
    base_path: Path,
    candidate_path: Path,
    *,
    existing_ids: set[str],
    family: str | None = None,
    template_subtype: str | None = None,
    allowed_tiers: set[str] | None = None,
    quota: int = 0,
    group_keys: Sequence[str] = (),
    hard_first: bool = True,
    min_int_fields: dict[str, int] | None = None,
    max_int_fields: dict[str, int] | None = None,
    exact_fields: dict[str, Any] | None = None,
    startswith_fields: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    base_index = {
        str(row.get("id", "")).strip(): {str(key): "" if value is None else str(value) for key, value in row.items()}
        for row in load_csv_rows(base_path)
        if str(row.get("id", "")).strip()
    }
    candidates: list[dict[str, str]] = []
    for raw_row in load_csv_rows(candidate_path):
        candidate_row = {str(key): "" if value is None else str(value) for key, value in raw_row.items()}
        row_id = str(candidate_row.get("id", "")).strip()
        if not row_id or row_id in existing_ids:
            continue
        base_row = base_index.get(row_id)
        if base_row is None:
            continue
        row = {**base_row, **candidate_row}
        if family and str(row.get("family", "")).strip() != family:
            continue
        if template_subtype and str(row.get("template_subtype", "")).strip() != template_subtype:
            continue
        if not str(row.get("prompt", "")).strip() or not str(row.get("answer", "")).strip():
            continue
        tier = infer_candidate_selection_tier(row)
        row["selection_tier"] = tier
        if allowed_tiers and tier not in allowed_tiers:
            continue
        if not matches_numeric_field_filters(
            row,
            min_int_fields=min_int_fields,
            max_int_fields=max_int_fields,
            exact_fields=exact_fields,
            startswith_fields=startswith_fields,
        ):
            continue
        candidates.append(row)
    if quota > 0 and len(candidates) > quota:
        selection_group_keys = tuple(group_keys) or ("template_subtype", "teacher_solver_candidate")
        return balanced_take(
            candidates,
            quota=quota,
            group_keys=selection_group_keys,
            hard_first=hard_first,
        )
    rank_fn = score_rank_high if hard_first else score_rank_low
    candidates.sort(key=rank_fn)
    return candidates


def select_joined_strong_baseline_candidates(
    metadata_path: Path,
    *,
    existing_ids: set[str],
    family: str | None = None,
    template_subtype: str | None = None,
    allowed_tiers: set[str] | None = None,
    quota: int = 0,
    group_keys: Sequence[str] = (),
    hard_first: bool = True,
    min_int_fields: dict[str, int] | None = None,
    max_int_fields: dict[str, int] | None = None,
    exact_fields: dict[str, Any] | None = None,
    startswith_fields: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    strong_index = load_strong_baseline_cot_v2_sample_index()
    candidates: list[dict[str, str]] = []
    for raw_row in load_csv_rows(metadata_path):
        metadata_row = {str(key): "" if value is None else str(value) for key, value in raw_row.items()}
        row_id = str(metadata_row.get("id", "")).strip()
        if not row_id or row_id in existing_ids:
            continue
        strong_row = strong_index.get(row_id)
        if strong_row is None:
            continue
        row = {**strong_row, **metadata_row}
        if family and str(row.get("family", "")).strip() != family:
            continue
        if template_subtype and str(row.get("template_subtype", "")).strip() != template_subtype:
            continue
        if not str(row.get("prompt", "")).strip() or not str(row.get("answer", "")).strip():
            continue
        if not str(row.get("generated_cot", "")).strip():
            continue
        tier = infer_candidate_selection_tier(row)
        row["selection_tier"] = tier
        if allowed_tiers and tier not in allowed_tiers:
            continue
        if not matches_numeric_field_filters(
            row,
            min_int_fields=min_int_fields,
            max_int_fields=max_int_fields,
            exact_fields=exact_fields,
            startswith_fields=startswith_fields,
        ):
            continue
        candidates.append(row)
    if quota > 0 and len(candidates) > quota:
        selection_group_keys = tuple(group_keys) or ("template_subtype", "selection_tier")
        return balanced_take(
            candidates,
            quota=quota,
            group_keys=selection_group_keys,
            hard_first=hard_first,
        )
    rank_fn = score_rank_high if hard_first else score_rank_low
    candidates.sort(key=rank_fn)
    return candidates


def select_direct_strong_baseline_candidates(
    *,
    existing_ids: set[str],
    baseline_source_type: str | None = None,
    label: str | None = None,
    quota: int = 0,
    group_keys: Sequence[str] = (),
    hard_first: bool = False,
    min_int_fields: dict[str, int] | None = None,
    max_int_fields: dict[str, int] | None = None,
    exact_fields: dict[str, Any] | None = None,
    startswith_fields: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for raw_row in load_strong_baseline_cot_v2_sample_rows():
        row = {str(key): "" if value is None else str(value) for key, value in raw_row.items()}
        row_id = str(row.get("id", "")).strip()
        if not row_id or row_id in existing_ids:
            continue
        if baseline_source_type and str(row.get("baseline_source_type", "")).strip() != baseline_source_type:
            continue
        if label and normalize_family_label(row) != label:
            continue
        prompt_text = str(row.get("prompt", "")).strip()
        answer_text = str(row.get("answer", "")).strip()
        if not prompt_text or not answer_text:
            continue
        prompt_chars = len(prompt_text)
        row["prompt_len_chars"] = str(prompt_chars)
        row["prompt_len_bucket"] = prompt_len_bucket(prompt_chars)
        row["answer_word_count"] = str(len(answer_text.split()))
        row["selection_tier"] = str(row.get("source_selection_tier", "")).strip().lower()
        if not matches_numeric_field_filters(
            row,
            min_int_fields=min_int_fields,
            max_int_fields=max_int_fields,
            exact_fields=exact_fields,
            startswith_fields=startswith_fields,
        ):
            continue
        candidates.append(row)
    if quota > 0 and len(candidates) > quota:
        selection_group_keys = tuple(group_keys) or ("prompt_len_bucket",)
        return balanced_take(
            candidates,
            quota=quota,
            group_keys=selection_group_keys,
            hard_first=hard_first,
        )
    rank_fn = score_rank_high if hard_first else score_rank_low
    candidates.sort(key=rank_fn)
    return candidates


def select_phase2_specialist_rows(
    path: Path,
    *,
    existing_ids: set[str],
    label: str | None = None,
    allowed_tiers: set[str] | None = None,
    template_subtype: str | None = None,
    teacher_solver_candidate: str | None = None,
    quota: int = 0,
    group_keys: Sequence[str] = (),
    hard_first: bool = True,
) -> list[dict[str, str]]:
    rows = load_csv_rows(path)
    validate_phase2_columns(path, rows)
    analysis_index = load_phase0_analysis_index()
    candidates: list[dict[str, str]] = []
    for raw_row in rows:
        phase2_row = clone_phase2_row(raw_row)
        row_id = str(phase2_row.get("id", "")).strip()
        if not row_id or row_id in existing_ids:
            continue
        if label and str(phase2_row.get("label", "")).strip() != label:
            continue
        tier = str(phase2_row.get("source_selection_tier", "")).strip().lower()
        if allowed_tiers and tier not in allowed_tiers:
            continue
        analysis_row = analysis_index.get(row_id)
        if analysis_row is None:
            continue
        if template_subtype and str(analysis_row.get("template_subtype", "")).strip() != template_subtype:
            continue
        if (
            teacher_solver_candidate is not None
            and str(analysis_row.get("teacher_solver_candidate", "")).strip()
            != teacher_solver_candidate
        ):
            continue
        candidates.append({**analysis_row, **phase2_row})
    if quota > 0 and len(candidates) > quota:
        selection_group_keys = tuple(group_keys) or ("template_subtype", "teacher_solver_candidate")
        return balanced_take(
            candidates,
            quota=quota,
            group_keys=selection_group_keys,
            hard_first=hard_first,
        )
    rank_fn = score_rank_high if hard_first else score_rank_low
    candidates.sort(key=rank_fn)
    return candidates


def build_single_adapter_fusion_external_rows(
    rows: Sequence[dict[str, str]],
    *,
    profile_name: str,
    quotas: dict[str, int],
    base_profile: str = "single-adapter-fusion-v10",
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    base_rows, base_summary = apply_phase2_train_profile(rows, profile=base_profile)
    input_rows = [clone_phase2_row(row) for row in rows]
    existing_ids = {
        str(row.get("id", "")).strip()
        for row in input_rows
        if str(row.get("id", "")).strip()
    }
    transform_counts = Counter(base_summary.get("transform_counts", {}))
    augmentation_rows: list[dict[str, str]] = []
    source_summaries: dict[str, Any] = {}

    def append_candidates(
        source_name: str,
        candidates: Sequence[dict[str, str]],
        *,
        label: str,
    ) -> None:
        appended_rows: list[dict[str, str]] = []
        for candidate in candidates:
            phase2_row = make_phase2_row_from_candidate(candidate, label=label, assistant_style="boxed_only")
            row_id = phase2_row["id"]
            if row_id in existing_ids:
                continue
            existing_ids.add(row_id)
            augmentation_rows.append(phase2_row)
            appended_rows.append(phase2_row)
            transform_counts[
                f"append_aug:{source_name}:{phase2_row['label']}:{phase2_row['source_selection_tier']}"
            ] += 1
        source_summaries[source_name] = {
            "selected": len(appended_rows),
            "summary": summarize_phase2_rows(appended_rows),
        }

    def append_binary_trace_candidates(
        source_name: str,
        candidates: Sequence[dict[str, str]],
    ) -> None:
        appended_rows: list[dict[str, str]] = []
        for candidate in candidates:
            phase2_row = make_phase2_row_from_candidate(
                candidate,
                label="binary",
                assistant_style="trace_boxed",
                generated_cot=build_exact_binary_program_trace(candidate),
            )
            row_id = phase2_row["id"]
            if row_id in existing_ids:
                continue
            existing_ids.add(row_id)
            augmentation_rows.append(phase2_row)
            appended_rows.append(phase2_row)
            transform_counts[
                f"append_aug:{source_name}:{phase2_row['label']}:{phase2_row['source_selection_tier']}"
            ] += 1
        source_summaries[source_name] = {
            "selected": len(appended_rows),
            "summary": summarize_phase2_rows(appended_rows),
        }

    def append_duplicate_candidate_rows(
        source_name: str,
        candidates: Sequence[dict[str, str]],
        *,
        label: str,
        assistant_style: str = "boxed_only",
    ) -> None:
        appended_rows: list[dict[str, str]] = []
        for candidate in candidates:
            phase2_row = make_phase2_row_from_candidate(
                candidate,
                label=label,
                assistant_style=assistant_style,
            )
            augmentation_rows.append(phase2_row)
            appended_rows.append(phase2_row)
            transform_counts[
                f"append_anchor:{source_name}:{phase2_row['label']}:{phase2_row['source_selection_tier']}"
            ] += 1
        source_summaries[source_name] = {
            "selected": len(appended_rows),
            "summary": summarize_phase2_rows(appended_rows),
        }

    def append_binary_closure_candidates(
        source_name: str,
        candidates: Sequence[dict[str, str]],
        *,
        assistant_style: str = "trace_boxed_done",
        duplicate_ok: bool = False,
    ) -> None:
        appended_rows: list[dict[str, str]] = []
        for candidate in candidates:
            phase2_row = make_phase2_row_from_candidate(
                candidate,
                label="binary",
                assistant_style=assistant_style,
                generated_cot=(
                    build_binary_final_answer_closure(candidate)
                    if assistant_style == "trace_boxed_done"
                    else ""
                ),
                prompt_override=build_binary_strict_boxed_prompt(str(candidate.get("prompt", ""))),
            )
            row_id = phase2_row["id"]
            if not duplicate_ok:
                if row_id in existing_ids:
                    continue
                existing_ids.add(row_id)
            augmentation_rows.append(phase2_row)
            appended_rows.append(phase2_row)
            counter_prefix = "append_anchor" if duplicate_ok else "append_aug"
            transform_counts[
                f"{counter_prefix}:{source_name}:{phase2_row['label']}:{phase2_row['source_selection_tier']}"
            ] += 1
        source_summaries[source_name] = {
            "selected": len(appended_rows),
            "summary": summarize_phase2_rows(appended_rows),
        }

    def append_phase2_rows(source_name: str, candidates: Sequence[dict[str, str]]) -> None:
        appended_rows: list[dict[str, str]] = []
        for candidate in candidates:
            phase2_row = {
                key: "" if candidate.get(key) is None else str(candidate.get(key, ""))
                for key in EXPECTED_PHASE2_COLUMNS
            }
            row_id = str(phase2_row.get("id", "")).strip()
            if not row_id or row_id in existing_ids:
                continue
            existing_ids.add(row_id)
            augmentation_rows.append(phase2_row)
            appended_rows.append(phase2_row)
            transform_counts[
                f"append_aug:{source_name}:{phase2_row['label']}:{phase2_row['source_selection_tier']}"
            ] += 1
        source_summaries[source_name] = {
            "selected": len(appended_rows),
            "summary": summarize_phase2_rows(appended_rows),
        }

    def append_duplicate_phase2_rows(
        source_name: str,
        candidates: Sequence[dict[str, str]],
    ) -> None:
        appended_rows: list[dict[str, str]] = []
        for candidate in candidates:
            phase2_row = {
                key: "" if candidate.get(key) is None else str(candidate.get(key, ""))
                for key in EXPECTED_PHASE2_COLUMNS
            }
            augmentation_rows.append(phase2_row)
            appended_rows.append(phase2_row)
            transform_counts[
                f"append_anchor:{source_name}:{phase2_row['label']}:{phase2_row['source_selection_tier']}"
            ] += 1
        source_summaries[source_name] = {
            "selected": len(appended_rows),
            "summary": summarize_phase2_rows(appended_rows),
        }

    def select_phase2_anchor_rows(
        *,
        label: str,
        allowed_tiers: set[str],
        mod: int,
    ) -> list[dict[str, str]]:
        if mod <= 0:
            return []
        selected: list[dict[str, str]] = []
        for raw_row in input_rows:
            phase2_row = clone_phase2_row(raw_row)
            if str(phase2_row.get("label", "")).strip().lower() != label:
                continue
            tier = str(phase2_row.get("source_selection_tier", "")).strip().lower()
            if tier not in allowed_tiers:
                continue
            row_key = str(phase2_row.get("id") or phase2_row.get("prompt") or "")
            if mod > 1 and stable_mod(row_key, mod) != 0:
                continue
            selected.append(phase2_row)
        return selected

    if quotas.get("binary_candidates", 0) > 0:
        binary_candidate_template_subtype = str(
            quotas.get("binary_candidates_template_subtype", "")
        ).strip() or None
        binary_candidate_allowed_tiers = set(
            quotas.get("binary_candidates_allowed_tiers", ("verified_trace_ready", "answer_only_keep"))
        )
        binary_candidate_group_keys = tuple(
            quotas.get(
                "binary_candidate_group_keys",
                ("template_subtype", "teacher_solver_candidate", "bit_structured_formula_abstract_family"),
            )
        )
        append_candidates(
            "binary_candidates",
            select_augmentation_candidates(
                AUGMENT_BINARY_STRUCTURED_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype=binary_candidate_template_subtype,
                allowed_tiers=binary_candidate_allowed_tiers,
                quota=quotas["binary_candidates"],
                group_keys=binary_candidate_group_keys,
                hard_first=True,
                min_int_fields=quotas.get("binary_candidate_min_fields"),
                max_int_fields=quotas.get("binary_candidate_max_fields"),
                exact_fields=quotas.get("binary_candidate_exact_fields"),
            ),
            label="binary",
        )
    if quotas.get("binary_hybrid_consensus", 0) > 0:
        append_candidates(
            "binary_hybrid_consensus",
            select_augmentation_candidates(
                AUGMENT_BINARY_HYBRID_CONSENSUS_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_other",
                allowed_tiers=set(
                    quotas.get(
                        "binary_hybrid_consensus_allowed_tiers",
                        ("verified_trace_ready", "answer_only_keep"),
                    )
                ),
                quota=quotas["binary_hybrid_consensus"],
                group_keys=tuple(
                    quotas.get(
                        "binary_hybrid_consensus_group_keys",
                        ("teacher_solver_candidate", "selection_tier", "num_examples"),
                    )
                ),
                hard_first=True,
                min_int_fields=quotas.get("binary_hybrid_consensus_min_fields"),
                max_int_fields=quotas.get("binary_hybrid_consensus_max_fields"),
                exact_fields=quotas.get("binary_hybrid_consensus_exact_fields"),
            ),
            label="binary",
        )
    if quotas.get("binary_structured_answer_only_abstract_safe", 0) > 0:
        append_candidates(
            "binary_structured_answer_only_abstract_safe",
            select_augmentation_candidates(
                AUGMENT_ANSWER_ONLY_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_structured_byte_formula",
                allowed_tiers={"answer_only_keep"},
                quota=quotas["binary_structured_answer_only_abstract_safe"],
                group_keys=tuple(
                    quotas.get(
                        "binary_structured_answer_only_abstract_safe_group_keys",
                        (
                            "bit_structured_formula_abstract_family",
                            "bit_no_candidate_positions",
                            "num_examples",
                        ),
                    )
                ),
                hard_first=True,
                min_int_fields=quotas.get(
                    "binary_structured_answer_only_abstract_safe_min_fields"
                ),
                max_int_fields=quotas.get(
                    "binary_structured_answer_only_abstract_safe_max_fields"
                ),
                exact_fields=quotas.get(
                    "binary_structured_answer_only_abstract_safe_exact_fields"
                ),
                startswith_fields=quotas.get(
                    "binary_structured_answer_only_abstract_safe_startswith_fields"
                ),
            ),
            label="binary",
        )
    selected_binary_exact_trace_formula: list[dict[str, str]] = []
    if quotas.get("binary_exact_trace_formula", 0) > 0:
        selected_binary_exact_trace_formula = select_augmentation_candidates(
            DEFAULT_PHASE0_ANALYSIS_CSV,
            existing_ids=existing_ids,
            family="bit_manipulation",
            allowed_tiers={"verified_trace_ready"},
            quota=quotas["binary_exact_trace_formula"],
            group_keys=tuple(
                quotas.get(
                    "binary_exact_trace_formula_group_keys",
                    (
                        "bit_structured_formula_abstract_family",
                        "bit_structured_formula_name",
                        "bit_no_candidate_positions",
                    ),
                )
            ),
            hard_first=True,
            min_int_fields=quotas.get("binary_exact_trace_formula_min_fields"),
            max_int_fields=quotas.get("binary_exact_trace_formula_max_fields"),
            exact_fields={
                "teacher_solver_candidate": "binary_structured_byte_formula",
                **dict(quotas.get("binary_exact_trace_formula_exact_fields", {})),
            },
            startswith_fields=quotas.get("binary_exact_trace_formula_startswith_fields"),
        )
        append_binary_trace_candidates(
            "binary_exact_trace_formula",
            selected_binary_exact_trace_formula,
        )
    if quotas.get("binary_exact_trace_formula_boxed_twin", 0) > 0:
        append_duplicate_candidate_rows(
            "binary_exact_trace_formula_boxed_twin",
            selected_binary_exact_trace_formula[: quotas["binary_exact_trace_formula_boxed_twin"]],
            label="binary",
        )
    selected_binary_exact_trace_abstract: list[dict[str, str]] = []
    if quotas.get("binary_exact_trace_abstract", 0) > 0:
        selected_binary_exact_trace_abstract = select_augmentation_candidates(
            DEFAULT_PHASE0_ANALYSIS_CSV,
            existing_ids=existing_ids,
            family="bit_manipulation",
            allowed_tiers={"verified_trace_ready"},
            quota=quotas["binary_exact_trace_abstract"],
            group_keys=tuple(
                quotas.get(
                    "binary_exact_trace_abstract_group_keys",
                    (
                        "bit_structured_formula_abstract_family",
                        "bit_structured_formula_name",
                        "bit_no_candidate_positions",
                    ),
                )
            ),
            hard_first=True,
            min_int_fields=quotas.get("binary_exact_trace_abstract_min_fields"),
            max_int_fields=quotas.get("binary_exact_trace_abstract_max_fields"),
            exact_fields={
                "teacher_solver_candidate": "binary_structured_byte_formula_abstract",
                **dict(quotas.get("binary_exact_trace_abstract_exact_fields", {})),
            },
            startswith_fields=quotas.get("binary_exact_trace_abstract_startswith_fields"),
        )
        append_binary_trace_candidates(
            "binary_exact_trace_abstract",
            selected_binary_exact_trace_abstract,
        )
    if quotas.get("binary_exact_trace_abstract_boxed_twin", 0) > 0:
        append_duplicate_candidate_rows(
            "binary_exact_trace_abstract_boxed_twin",
            selected_binary_exact_trace_abstract[: quotas["binary_exact_trace_abstract_boxed_twin"]],
            label="binary",
        )
    selected_binary_exact_trace_not_formula: list[dict[str, str]] = []
    if quotas.get("binary_exact_trace_not_formula", 0) > 0:
        selected_binary_exact_trace_not_formula = select_augmentation_candidates(
            DEFAULT_PHASE0_ANALYSIS_CSV,
            existing_ids=existing_ids,
            family="bit_manipulation",
            allowed_tiers={"verified_trace_ready"},
            quota=quotas["binary_exact_trace_not_formula"],
            group_keys=tuple(
                quotas.get(
                    "binary_exact_trace_not_formula_group_keys",
                    (
                        "bit_not_structured_formula_name",
                        "bit_no_candidate_positions",
                    ),
                )
            ),
            hard_first=True,
            min_int_fields=quotas.get("binary_exact_trace_not_formula_min_fields"),
            max_int_fields=quotas.get("binary_exact_trace_not_formula_max_fields"),
            exact_fields={
                "teacher_solver_candidate": "binary_structured_byte_not_formula",
                **dict(quotas.get("binary_exact_trace_not_formula_exact_fields", {})),
            },
            startswith_fields=quotas.get("binary_exact_trace_not_formula_startswith_fields"),
        )
        append_binary_trace_candidates(
            "binary_exact_trace_not_formula",
            selected_binary_exact_trace_not_formula,
        )
    if quotas.get("binary_exact_trace_not_formula_boxed_twin", 0) > 0:
        append_duplicate_candidate_rows(
            "binary_exact_trace_not_formula_boxed_twin",
            selected_binary_exact_trace_not_formula[: quotas["binary_exact_trace_not_formula_boxed_twin"]],
            label="binary",
        )
    if quotas.get("binary_answer_only_bit_other", 0) > 0:
        append_candidates(
            "binary_answer_only_bit_other",
            select_augmentation_candidates(
                AUGMENT_ANSWER_ONLY_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_other",
                allowed_tiers={"answer_only_keep"},
                quota=quotas["binary_answer_only_bit_other"],
                group_keys=("template_subtype", "group_signature"),
                hard_first=True,
            ),
            label="binary",
        )
    if quotas.get("binary_manual_bit_other", 0) > 0:
        append_candidates(
            "binary_manual_bit_other",
            select_augmentation_candidates(
                AUGMENT_BINARY_MANUAL_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_other",
                allowed_tiers={"manual_audit_priority"},
                quota=quotas["binary_manual_bit_other"],
                group_keys=("template_subtype", "group_signature"),
                hard_first=True,
            ),
            label="binary",
        )
    if quotas.get("symbol_verified", 0) > 0:
        append_candidates(
            "symbol_verified",
            select_augmentation_candidates(
                AUGMENT_VERIFIED_TRACE_CSV,
                existing_ids=existing_ids,
                family="symbol_equation",
                allowed_tiers={"verified_trace_ready"},
                quota=quotas["symbol_verified"],
                group_keys=("template_subtype", "symbol_query_operator"),
                hard_first=True,
            ),
            label="symbol",
        )
    if quotas.get("symbol_answer_only", 0) > 0:
        append_candidates(
            "symbol_answer_only",
            select_augmentation_candidates(
                AUGMENT_ANSWER_ONLY_CSV,
                existing_ids=existing_ids,
                family="symbol_equation",
                template_subtype="numeric_2x2",
                allowed_tiers={"answer_only_keep"},
                quota=quotas["symbol_answer_only"],
                group_keys=("template_subtype", "symbol_query_operator"),
                hard_first=True,
            ),
            label="symbol",
        )
    if quotas.get("symbol_manual", 0) > 0:
        append_candidates(
            "symbol_manual",
            select_augmentation_candidates(
                AUGMENT_SYMBOL_MANUAL_CSV,
                existing_ids=existing_ids,
                family="symbol_equation",
                template_subtype="numeric_2x2",
                allowed_tiers={"manual_audit_priority"},
                quota=quotas["symbol_manual"],
                group_keys=("template_subtype", "symbol_query_operator"),
                hard_first=True,
            ),
            label="symbol",
        )
    if quotas.get("symbol_glyph_answer_only", 0) > 0:
        append_candidates(
            "symbol_glyph_answer_only",
            select_augmentation_candidates(
                AUGMENT_ANSWER_ONLY_CSV,
                existing_ids=existing_ids,
                family="symbol_equation",
                template_subtype="glyph_len5",
                allowed_tiers={"answer_only_keep"},
                quota=quotas["symbol_glyph_answer_only"],
                hard_first=True,
            ),
            label="symbol",
        )
    if quotas.get("binary_affine_verified", 0) > 0:
        append_phase2_rows(
            "binary_affine_verified",
            select_phase2_specialist_rows(
                PHASE2_BINARY_SPECIALIST_CSV,
                existing_ids=existing_ids,
                label="binary",
                allowed_tiers={"verified_trace_ready"},
                template_subtype="bit_other",
                teacher_solver_candidate="binary_affine_xor",
                quota=quotas["binary_affine_verified"],
                group_keys=("teacher_solver_candidate", "group_signature"),
                hard_first=True,
            ),
        )
    if quotas.get("binary_structured_answer_only", 0) > 0:
        append_candidates(
            "binary_structured_answer_only",
            select_augmentation_candidates(
                AUGMENT_ANSWER_ONLY_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_structured_byte_formula",
                allowed_tiers={"answer_only_keep"},
                quota=quotas["binary_structured_answer_only"],
                group_keys=(
                    "template_subtype",
                    "bit_structured_formula_abstract_family",
                ),
                hard_first=True,
            ),
            label="binary",
        )
    if quotas.get("binary_structured_recommended", 0) > 0:
        append_candidates(
            "binary_structured_recommended",
            select_augmentation_candidates(
                AUGMENT_TRAIN_RECOMMENDED_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_structured_byte_formula",
                allowed_tiers={"verified_trace_ready"},
                quota=quotas["binary_structured_recommended"],
                group_keys=tuple(
                    quotas.get(
                        "binary_structured_recommended_group_keys",
                        (
                            "bit_structured_formula_abstract_family",
                            "num_examples",
                            "bit_no_candidate_positions",
                        ),
                    )
                ),
                hard_first=True,
                min_int_fields=quotas.get("binary_structured_recommended_min_fields"),
                max_int_fields=quotas.get("binary_structured_recommended_max_fields"),
                exact_fields=quotas.get("binary_structured_recommended_exact_fields"),
                startswith_fields=quotas.get("binary_structured_recommended_startswith_fields"),
            ),
            label="binary",
        )
    if quotas.get("binary_structured_exact_zero_answer_only", 0) > 0:
        append_candidates(
            "binary_structured_exact_zero_answer_only",
            select_augmentation_candidates(
                AUGMENT_ANSWER_ONLY_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_structured_byte_formula",
                allowed_tiers={"answer_only_keep"},
                quota=quotas["binary_structured_exact_zero_answer_only"],
                group_keys=tuple(
                    quotas.get(
                        "binary_structured_exact_zero_answer_only_group_keys",
                        ("num_examples", "bit_no_candidate_positions"),
                    )
                ),
                hard_first=True,
                min_int_fields=quotas.get("binary_structured_exact_zero_answer_only_min_fields"),
                max_int_fields=quotas.get("binary_structured_exact_zero_answer_only_max_fields"),
                exact_fields=quotas.get("binary_structured_exact_zero_answer_only_exact_fields"),
            ),
            label="binary",
        )
    if quotas.get("binary_structured_leading_zero_answer_only", 0) > 0:
        append_candidates(
            "binary_structured_leading_zero_answer_only",
            select_augmentation_candidates(
                AUGMENT_ANSWER_ONLY_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_structured_byte_formula",
                allowed_tiers={"answer_only_keep"},
                quota=quotas["binary_structured_leading_zero_answer_only"],
                group_keys=tuple(
                    quotas.get(
                        "binary_structured_leading_zero_answer_only_group_keys",
                        ("num_examples", "bit_no_candidate_positions"),
                    )
                ),
                hard_first=True,
                min_int_fields=quotas.get("binary_structured_leading_zero_answer_only_min_fields"),
                max_int_fields=quotas.get("binary_structured_leading_zero_answer_only_max_fields"),
                exact_fields=quotas.get("binary_structured_leading_zero_answer_only_exact_fields"),
                startswith_fields=quotas.get(
                    "binary_structured_leading_zero_answer_only_startswith_fields"
                ),
            ),
            label="binary",
        )
    if quotas.get("binary_prompt_local_current_structured_answer_only", 0) > 0:
        append_candidates(
            "binary_prompt_local_current_structured_answer_only",
            select_joined_augmentation_candidates(
                AUGMENT_ANSWER_ONLY_CSV,
                AUGMENT_BINARY_PROMPT_LOCAL_CURRENT_CONSENSUS_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_structured_byte_formula",
                allowed_tiers={"answer_only_keep"},
                quota=quotas["binary_prompt_local_current_structured_answer_only"],
                group_keys=tuple(
                    quotas.get(
                        "binary_prompt_local_current_structured_answer_only_group_keys",
                        ("safe_formulas", "num_examples"),
                    )
                ),
                hard_first=True,
                min_int_fields=quotas.get(
                    "binary_prompt_local_current_structured_answer_only_min_fields"
                ),
                max_int_fields=quotas.get(
                    "binary_prompt_local_current_structured_answer_only_max_fields"
                ),
                exact_fields=quotas.get(
                    "binary_prompt_local_current_structured_answer_only_exact_fields"
                ),
            ),
            label="binary",
        )
    selected_binary_prompt_local_current_structured_closure: list[dict[str, str]] = []
    if quotas.get("binary_prompt_local_current_structured_closure", 0) > 0:
        selected_binary_prompt_local_current_structured_closure = select_joined_augmentation_candidates(
            AUGMENT_ANSWER_ONLY_CSV,
            AUGMENT_BINARY_PROMPT_LOCAL_CURRENT_CONSENSUS_CSV,
            existing_ids=existing_ids,
            family="bit_manipulation",
            template_subtype="bit_structured_byte_formula",
            allowed_tiers={"answer_only_keep"},
            quota=quotas["binary_prompt_local_current_structured_closure"],
            group_keys=tuple(
                quotas.get(
                    "binary_prompt_local_current_structured_closure_group_keys",
                    ("safe_formulas", "num_examples"),
                )
            ),
            hard_first=True,
            min_int_fields=quotas.get("binary_prompt_local_current_structured_closure_min_fields"),
            max_int_fields=quotas.get("binary_prompt_local_current_structured_closure_max_fields"),
            exact_fields=quotas.get("binary_prompt_local_current_structured_closure_exact_fields"),
            startswith_fields=quotas.get(
                "binary_prompt_local_current_structured_closure_startswith_fields"
            ),
        )
        append_binary_closure_candidates(
            "binary_prompt_local_current_structured_closure",
            selected_binary_prompt_local_current_structured_closure,
        )
    if quotas.get("binary_prompt_local_current_structured_closure_boxed_done_twin", 0) > 0:
        append_binary_closure_candidates(
            "binary_prompt_local_current_structured_closure_boxed_done_twin",
            selected_binary_prompt_local_current_structured_closure[
                : quotas["binary_prompt_local_current_structured_closure_boxed_done_twin"]
            ],
            assistant_style="boxed_only_done",
            duplicate_ok=True,
        )
    selected_binary_prompt_local_current_structured_boxed_done: list[dict[str, str]] = []
    if quotas.get("binary_prompt_local_current_structured_boxed_done", 0) > 0:
        selected_binary_prompt_local_current_structured_boxed_done = select_joined_augmentation_candidates(
            AUGMENT_ANSWER_ONLY_CSV,
            AUGMENT_BINARY_PROMPT_LOCAL_CURRENT_CONSENSUS_CSV,
            existing_ids=existing_ids,
            family="bit_manipulation",
            template_subtype="bit_structured_byte_formula",
            allowed_tiers={"answer_only_keep"},
            quota=quotas["binary_prompt_local_current_structured_boxed_done"],
            group_keys=tuple(
                quotas.get(
                    "binary_prompt_local_current_structured_boxed_done_group_keys",
                    ("safe_formulas", "num_examples"),
                )
            ),
            hard_first=True,
            min_int_fields=quotas.get(
                "binary_prompt_local_current_structured_boxed_done_min_fields"
            ),
            max_int_fields=quotas.get(
                "binary_prompt_local_current_structured_boxed_done_max_fields"
            ),
            exact_fields=quotas.get(
                "binary_prompt_local_current_structured_boxed_done_exact_fields"
            ),
            startswith_fields=quotas.get(
                "binary_prompt_local_current_structured_boxed_done_startswith_fields"
            ),
        )
        append_binary_closure_candidates(
            "binary_prompt_local_current_structured_boxed_done",
            selected_binary_prompt_local_current_structured_boxed_done,
            assistant_style="boxed_only_done",
        )
    if quotas.get("binary_prompt_local_current_structured_boxed_only_twin", 0) > 0:
        append_binary_closure_candidates(
            "binary_prompt_local_current_structured_boxed_only_twin",
            selected_binary_prompt_local_current_structured_boxed_done[
                : quotas["binary_prompt_local_current_structured_boxed_only_twin"]
            ],
            assistant_style="boxed_only",
            duplicate_ok=True,
        )
    if quotas.get("binary_prompt_local_current_structured_strict_boxed_only", 0) > 0:
        append_binary_closure_candidates(
            "binary_prompt_local_current_structured_strict_boxed_only",
            select_joined_augmentation_candidates(
                AUGMENT_ANSWER_ONLY_CSV,
                AUGMENT_BINARY_PROMPT_LOCAL_CURRENT_CONSENSUS_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_structured_byte_formula",
                allowed_tiers={"answer_only_keep"},
                quota=quotas["binary_prompt_local_current_structured_strict_boxed_only"],
                group_keys=tuple(
                    quotas.get(
                        "binary_prompt_local_current_structured_strict_boxed_only_group_keys",
                        ("safe_formulas", "num_examples"),
                    )
                ),
                hard_first=True,
                min_int_fields=quotas.get(
                    "binary_prompt_local_current_structured_strict_boxed_only_min_fields"
                ),
                max_int_fields=quotas.get(
                    "binary_prompt_local_current_structured_strict_boxed_only_max_fields"
                ),
                exact_fields=quotas.get(
                    "binary_prompt_local_current_structured_strict_boxed_only_exact_fields"
                ),
            ),
            assistant_style="boxed_only",
        )
    selected_binary_prompt_local_current_bit_other_answer_only_boxed_done: list[dict[str, str]] = []
    if quotas.get("binary_prompt_local_current_bit_other_answer_only_boxed_done", 0) > 0:
        selected_binary_prompt_local_current_bit_other_answer_only_boxed_done = (
            select_joined_augmentation_candidates(
                AUGMENT_ANSWER_ONLY_CSV,
                AUGMENT_BINARY_PROMPT_LOCAL_CURRENT_CONSENSUS_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_other",
                allowed_tiers={"answer_only_keep"},
                quota=quotas["binary_prompt_local_current_bit_other_answer_only_boxed_done"],
                group_keys=tuple(
                    quotas.get(
                        "binary_prompt_local_current_bit_other_answer_only_boxed_done_group_keys",
                        ("safe_formulas", "num_examples"),
                    )
                ),
                hard_first=True,
                min_int_fields=quotas.get(
                    "binary_prompt_local_current_bit_other_answer_only_boxed_done_min_fields"
                ),
                max_int_fields=quotas.get(
                    "binary_prompt_local_current_bit_other_answer_only_boxed_done_max_fields"
                ),
                exact_fields=quotas.get(
                    "binary_prompt_local_current_bit_other_answer_only_boxed_done_exact_fields"
                ),
                startswith_fields=quotas.get(
                    "binary_prompt_local_current_bit_other_answer_only_boxed_done_startswith_fields"
                ),
            )
        )
        append_binary_closure_candidates(
            "binary_prompt_local_current_bit_other_answer_only_boxed_done",
            selected_binary_prompt_local_current_bit_other_answer_only_boxed_done,
            assistant_style="boxed_only_done",
        )
    if quotas.get("binary_prompt_local_current_bit_other_answer_only_boxed_only_twin", 0) > 0:
        append_binary_closure_candidates(
            "binary_prompt_local_current_bit_other_answer_only_boxed_only_twin",
            selected_binary_prompt_local_current_bit_other_answer_only_boxed_done[
                : quotas["binary_prompt_local_current_bit_other_answer_only_boxed_only_twin"]
            ],
            assistant_style="boxed_only",
            duplicate_ok=True,
        )
    selected_binary_prompt_local_current_bit_other_manual_boxed_done: list[dict[str, str]] = []
    if quotas.get("binary_prompt_local_current_bit_other_manual_boxed_done", 0) > 0:
        selected_binary_prompt_local_current_bit_other_manual_boxed_done = (
            select_joined_augmentation_candidates(
                AUGMENT_ANSWER_ONLY_CSV,
                AUGMENT_BINARY_PROMPT_LOCAL_CURRENT_CONSENSUS_CSV,
                existing_ids=existing_ids,
                family="bit_manipulation",
                template_subtype="bit_other",
                allowed_tiers={"manual_audit_priority"},
                quota=quotas["binary_prompt_local_current_bit_other_manual_boxed_done"],
                group_keys=tuple(
                    quotas.get(
                        "binary_prompt_local_current_bit_other_manual_boxed_done_group_keys",
                        ("safe_formulas", "num_examples"),
                    )
                ),
                hard_first=True,
                min_int_fields=quotas.get(
                    "binary_prompt_local_current_bit_other_manual_boxed_done_min_fields"
                ),
                max_int_fields=quotas.get(
                    "binary_prompt_local_current_bit_other_manual_boxed_done_max_fields"
                ),
                exact_fields=quotas.get(
                    "binary_prompt_local_current_bit_other_manual_boxed_done_exact_fields"
                ),
                startswith_fields=quotas.get(
                    "binary_prompt_local_current_bit_other_manual_boxed_done_startswith_fields"
                ),
            )
        )
        append_binary_closure_candidates(
            "binary_prompt_local_current_bit_other_manual_boxed_done",
            selected_binary_prompt_local_current_bit_other_manual_boxed_done,
            assistant_style="boxed_only_done",
        )
    if quotas.get("binary_prompt_local_current_bit_other_manual_boxed_only_twin", 0) > 0:
        append_binary_closure_candidates(
            "binary_prompt_local_current_bit_other_manual_boxed_only_twin",
            selected_binary_prompt_local_current_bit_other_manual_boxed_done[
                : quotas["binary_prompt_local_current_bit_other_manual_boxed_only_twin"]
            ],
            assistant_style="boxed_only",
            duplicate_ok=True,
        )
    if quotas.get("symbol_formula_verified", 0) > 0:
        append_phase2_rows(
            "symbol_formula_verified",
            select_phase2_specialist_rows(
                PHASE2_SYMBOL_SPECIALIST_CSV,
                existing_ids=existing_ids,
                label="symbol",
                allowed_tiers={"verified_trace_ready"},
                template_subtype="numeric_2x2",
                teacher_solver_candidate="symbol_numeric_operator_formula",
                quota=quotas["symbol_formula_verified"],
                group_keys=("teacher_solver_candidate", "symbol_query_operator"),
                hard_first=True,
            ),
        )
    if quotas.get("symbol_formula_answer_only", 0) > 0:
        append_phase2_rows(
            "symbol_formula_answer_only",
            select_phase2_specialist_rows(
                PHASE2_SYMBOL_SPECIALIST_CSV,
                existing_ids=existing_ids,
                label="symbol",
                allowed_tiers={"answer_only_keep"},
                template_subtype="numeric_2x2",
                teacher_solver_candidate="symbol_numeric_operator_formula",
                quota=quotas["symbol_formula_answer_only"],
                group_keys=("teacher_solver_candidate", "symbol_query_operator"),
                hard_first=True,
            ),
        )
    if quotas.get("gravity_verified_anchor_mod", 0) > 0:
        append_duplicate_phase2_rows(
            "gravity_verified_anchor",
            select_phase2_anchor_rows(
                label="gravity",
                allowed_tiers={"verified_trace_ready"},
                mod=quotas["gravity_verified_anchor_mod"],
            ),
        )
    if quotas.get("text_verified_anchor_mod", 0) > 0:
        append_duplicate_phase2_rows(
            "text_verified_anchor",
            select_phase2_anchor_rows(
                label="text",
                allowed_tiers={"verified_trace_ready"},
                mod=quotas["text_verified_anchor_mod"],
            ),
        )
    if quotas.get("unit_verified_anchor_mod", 0) > 0:
        append_duplicate_phase2_rows(
            "unit_verified_anchor",
            select_phase2_anchor_rows(
                label="unit",
                allowed_tiers={"verified_trace_ready"},
                mod=quotas["unit_verified_anchor_mod"],
            ),
        )

    profiled_rows = [*base_rows, *augmentation_rows]
    return profiled_rows, {
        "profile": profile_name,
        "input": summarize_phase2_rows(input_rows),
        "output": summarize_phase2_rows(profiled_rows),
        "transform_counts": {
            name: count for name, count in sorted(transform_counts.items())
        },
        "base_profile": {
            "profile": base_summary.get("profile", "single-adapter-fusion-v10"),
            "output": base_summary.get("output", {}),
        },
        "augmentation": {
            "rows": len(augmentation_rows),
            "summary": summarize_phase2_rows(augmentation_rows),
            "sources": source_summaries,
        },
    }


def build_single_adapter_fusion_v15_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v15",
        quotas=FUSION_V15_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v16_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v16",
        quotas=FUSION_V16_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v17_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v17",
        quotas=FUSION_V17_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v18_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v18",
        quotas=FUSION_V18_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v19_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v19",
        quotas=FUSION_V19_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v20_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v20",
        quotas=FUSION_V20_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v21_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v21",
        quotas=FUSION_V21_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v22_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v22",
        quotas=FUSION_V22_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v23_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v23",
        quotas=FUSION_V23_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v24_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v24",
        quotas=FUSION_V24_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v25_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v25",
        quotas=FUSION_V25_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v26_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v26",
        quotas=FUSION_V26_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v27_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v27",
        quotas=FUSION_V27_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v28_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v28",
        quotas=FUSION_V28_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v29_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v29",
        quotas=FUSION_V29_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v30_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v30",
        quotas=FUSION_V30_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v31_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v31",
        quotas=FUSION_V31_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v140_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v140",
        quotas=FUSION_V31_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v40",
    )


def build_single_adapter_fusion_v141_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v141",
        quotas=FUSION_V29_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v40",
    )


def build_single_adapter_fusion_v142_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v142",
        quotas=FUSION_V30_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v40",
    )


def build_single_adapter_fusion_v32_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v32",
        quotas=FUSION_V32_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v33_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v33",
        quotas=FUSION_V33_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v34_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v34",
        quotas=FUSION_V34_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v35_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v35",
        quotas=FUSION_V35_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v36_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v36",
        quotas=FUSION_V36_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v37_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v37",
        quotas=FUSION_V37_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v38_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v38",
        quotas=FUSION_V38_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v39_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v39",
        quotas=FUSION_V39_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v40_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v40",
        quotas=FUSION_V40_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v41_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v41",
        quotas=FUSION_V41_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v42_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v42",
        quotas=FUSION_V42_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v43_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v43",
        quotas=FUSION_V43_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v44_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v44",
        quotas=FUSION_V44_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v45_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v45",
        quotas=FUSION_V45_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v46_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v46",
        quotas=FUSION_V46_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v47_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v47",
        quotas=FUSION_V47_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v48_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v48",
        quotas=FUSION_V48_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v49_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v49",
        quotas=FUSION_V49_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v50_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v50",
        quotas=FUSION_V50_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v51_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v51",
        quotas=FUSION_V51_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v52_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v52",
        quotas=FUSION_V52_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v53_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v53",
        quotas=FUSION_V53_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v54_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v54",
        quotas=FUSION_V54_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v55_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v55",
        quotas=FUSION_V55_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v56_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v56",
        quotas=FUSION_V56_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v57_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v57",
        quotas=FUSION_V57_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v58_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v58",
        quotas=FUSION_V58_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v59_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v59",
        quotas=FUSION_V59_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v60_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v60",
        quotas=FUSION_V60_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v61_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v61",
        quotas=FUSION_V61_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v62_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v62",
        quotas=FUSION_V62_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v63_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v63",
        quotas=FUSION_V63_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v64_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v64",
        quotas=FUSION_V64_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v65_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v65",
        quotas=FUSION_V65_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v66_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v66",
        quotas=FUSION_V66_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v67_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v67",
        quotas=FUSION_V67_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v68_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v68",
        quotas=FUSION_V68_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v69_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v69",
        quotas=FUSION_V69_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v70_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v70",
        quotas=FUSION_V70_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v71_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v71",
        quotas=FUSION_V71_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v72_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v72",
        quotas=FUSION_V72_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v73_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v73",
        quotas=FUSION_V73_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v74_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v74",
        quotas=FUSION_V74_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v75_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v75",
        quotas=FUSION_V75_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v76_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v76",
        quotas=FUSION_V76_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v77_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v77",
        quotas=FUSION_V77_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v78_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v78",
        quotas=FUSION_V78_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v79_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v79",
        quotas=FUSION_V79_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v80_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v80",
        quotas=FUSION_V80_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v81_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v81",
        quotas=FUSION_V81_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v82_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v82",
        quotas=FUSION_V82_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v83_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v83",
        quotas=FUSION_V83_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_v84_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v84",
        quotas=FUSION_V84_AUGMENT_QUOTAS,
    )


def build_single_adapter_fusion_strong_sample_rows(
    rows: Sequence[dict[str, str]],
    *,
    profile_name: str,
    augmentation_specs: Sequence[dict[str, Any]],
    base_profile: str = "single-adapter-fusion-v40",
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    base_rows, base_summary = apply_phase2_train_profile(rows, profile=base_profile)
    profiled_rows = [clone_phase2_row(row) for row in base_rows]
    existing_ids = {
        str(row.get("id", "")).strip()
        for row in profiled_rows
        if str(row.get("id", "")).strip()
    }
    augmentation_rows: list[dict[str, str]] = []
    source_summaries: dict[str, Any] = {}
    transform_counts = Counter(base_summary.get("transform_counts", {}))

    for spec in augmentation_specs:
        source_name = str(spec.get("source_name", "")).strip()
        baseline_source_type = str(spec.get("baseline_source_type", "")).strip()
        family = str(spec.get("family", "")).strip()
        label = str(spec.get("label", "")).strip()
        template_subtype = str(spec.get("template_subtype", "")).strip()
        metadata_path_value = spec.get("metadata_path")
        metadata_path = (
            Path(metadata_path_value)
            if metadata_path_value
            else AUGMENT_TRAIN_RECOMMENDED_CSV
        )
        if not source_name or not label:
            raise ValueError(f"{profile_name} has an invalid augmentation spec: {spec!r}")
        allowed_tiers = {
            str(value).strip().lower()
            for value in spec.get("allowed_tiers", ())
            if str(value).strip()
        }
        if baseline_source_type:
            candidates = select_direct_strong_baseline_candidates(
                existing_ids=existing_ids,
                baseline_source_type=baseline_source_type,
                label=label,
                quota=int(spec.get("quota", 0)),
                group_keys=tuple(spec.get("group_keys", ("prompt_len_bucket",))),
                hard_first=bool(spec.get("hard_first", False)),
                min_int_fields=spec.get("min_int_fields"),
                max_int_fields=spec.get("max_int_fields"),
                exact_fields=spec.get("exact_fields"),
                startswith_fields=spec.get("startswith_fields"),
            )
        else:
            if not family or not template_subtype:
                raise ValueError(f"{profile_name} has an invalid joined augmentation spec: {spec!r}")
            candidates = select_joined_strong_baseline_candidates(
                metadata_path=metadata_path,
                existing_ids=existing_ids,
                family=family,
                template_subtype=template_subtype,
                allowed_tiers=allowed_tiers or None,
                quota=int(spec.get("quota", 0)),
                group_keys=tuple(spec.get("group_keys", ("template_subtype", "selection_tier"))),
                hard_first=bool(spec.get("hard_first", True)),
                min_int_fields=spec.get("min_int_fields"),
                max_int_fields=spec.get("max_int_fields"),
                exact_fields=spec.get("exact_fields"),
                startswith_fields=spec.get("startswith_fields"),
            )
        appended_rows: list[dict[str, str]] = []
        assistant_style = str(spec.get("assistant_style", "cot_boxed_notebook")).strip() or "cot_boxed_notebook"
        prompt_style = str(spec.get("prompt_style", "")).strip().lower()
        for candidate in candidates:
            prompt_override: str | None = None
            if prompt_style == "strict_bare_boxed":
                prompt_override = build_strict_bare_boxed_prompt(str(candidate.get("prompt", "")))
            phase2_row = make_phase2_row_from_candidate(
                candidate,
                label=label,
                assistant_style=assistant_style,
                source_selection_tier=str(candidate.get("selection_tier", "")).strip().lower(),
                generated_cot=str(candidate.get("generated_cot", "")),
                prompt_override=prompt_override,
            )
            row_id = phase2_row["id"]
            if row_id in existing_ids:
                continue
            existing_ids.add(row_id)
            augmentation_rows.append(phase2_row)
            appended_rows.append(phase2_row)
            transform_counts[
                f"append_aug:{source_name}:{phase2_row['label']}:{phase2_row['source_selection_tier']}"
            ] += 1
        source_summaries[source_name] = {
            "selected": len(appended_rows),
            "summary": summarize_phase2_rows(appended_rows),
        }

    profiled_rows.extend(augmentation_rows)
    return profiled_rows, {
        "profile": profile_name,
        "input": base_summary.get("input", summarize_phase2_rows(rows)),
        "base_profile": {
            "profile": base_summary.get("profile", base_profile),
            "output": base_summary.get("output", summarize_phase2_rows(base_rows)),
        },
        "base": base_summary.get("output", summarize_phase2_rows(base_rows)),
        "output": summarize_phase2_rows(profiled_rows),
        "transform_counts": {
            name: count for name, count in sorted(transform_counts.items())
        },
        "augmentation": {
            "rows": len(augmentation_rows),
            "summary": summarize_phase2_rows(augmentation_rows),
            "sources": source_summaries,
        },
    }


def build_single_adapter_fusion_v88_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v88",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V88_SPECS,
    )


def build_single_adapter_fusion_v89_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v89",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V89_SPECS,
    )


def build_single_adapter_fusion_v90_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v90",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V90_SPECS,
    )


def build_single_adapter_fusion_v91_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v91",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V91_SPECS,
    )


def build_single_adapter_fusion_v92_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v92",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V92_SPECS,
    )


def build_single_adapter_fusion_v93_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v93",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V93_SPECS,
    )


def build_single_adapter_fusion_v94_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v94",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V94_SPECS,
    )


def build_single_adapter_fusion_v95_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v95",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V95_SPECS,
    )


def build_single_adapter_fusion_v96_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v96",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V96_SPECS,
    )


def build_single_adapter_fusion_v97_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v97",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V97_SPECS,
    )


def build_single_adapter_fusion_v98_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v98",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V98_SPECS,
    )


def build_single_adapter_fusion_v99_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v99",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V99_SPECS,
    )


def build_single_adapter_fusion_v100_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v100",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V100_SPECS,
    )


def build_single_adapter_fusion_v101_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v101",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V101_SPECS,
    )


def build_single_adapter_fusion_v102_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v102",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V102_SPECS,
    )


def build_single_adapter_fusion_v103_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v103",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V103_SPECS,
    )


def build_single_adapter_fusion_v104_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v104",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V104_SPECS,
    )


def build_single_adapter_fusion_v105_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v105",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V105_SPECS,
    )


def build_single_adapter_fusion_v106_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v106",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V106_SPECS,
    )


def build_single_adapter_fusion_v107_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v107",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V107_SPECS,
    )


def build_single_adapter_fusion_v108_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v108",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V108_SPECS,
    )


def build_single_adapter_fusion_v109_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v109",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V109_SPECS,
    )


def build_single_adapter_fusion_v110_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v110",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V110_SPECS,
    )


def build_single_adapter_fusion_v111_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v111",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V111_SPECS,
    )


def build_single_adapter_fusion_v112_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v112",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V112_SPECS,
    )


def build_single_adapter_fusion_v113_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v113",
        quotas=FUSION_V113_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v110",
    )


def build_single_adapter_fusion_v114_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v114",
        quotas=FUSION_V114_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v110",
    )


def build_single_adapter_fusion_v115_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v115",
        quotas=FUSION_V115_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v110",
    )


def build_single_adapter_fusion_v116_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v116",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V116_SPECS,
    )


def build_single_adapter_fusion_v117_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v117",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V117_SPECS,
    )


def build_single_adapter_fusion_v118_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v118",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V118_SPECS,
    )


def build_single_adapter_fusion_v119_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v119",
        quotas=FUSION_V119_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v110",
    )


def build_single_adapter_fusion_v120_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v120",
        quotas=FUSION_V120_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v110",
    )


def build_single_adapter_fusion_v121_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v121",
        quotas=FUSION_V121_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v110",
    )


def build_single_adapter_fusion_v122_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v122",
        quotas=FUSION_V122_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v110",
    )


def build_single_adapter_fusion_v123_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v123",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V123_SPECS,
        base_profile="single-adapter-fusion-v110",
    )


def build_single_adapter_fusion_v124_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v124",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V124_SPECS,
        base_profile="single-adapter-fusion-v110",
    )


def build_single_adapter_fusion_v128_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v128",
        quotas=FUSION_V128_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v124",
    )


def build_single_adapter_fusion_v129_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_external_rows(
        rows,
        profile_name="single-adapter-fusion-v129",
        quotas=FUSION_V129_AUGMENT_QUOTAS,
        base_profile="single-adapter-fusion-v124",
    )


def build_single_adapter_fusion_v131_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v131",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V131_SPECS,
        base_profile="single-adapter-fusion-v40",
    )


def build_single_adapter_fusion_v132_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v132",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V132_SPECS,
        base_profile="single-adapter-fusion-v40",
    )


def build_single_adapter_fusion_v133_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v133",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V133_SPECS,
        base_profile="single-adapter-fusion-v40",
    )


def build_single_adapter_fusion_v134_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v134",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V134_SPECS,
        base_profile="single-adapter-fusion-v40",
    )


def build_single_adapter_fusion_v135_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v135",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V135_SPECS,
        base_profile="single-adapter-fusion-v40",
    )


def build_single_adapter_fusion_v136_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v136",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V136_SPECS,
        base_profile="single-adapter-fusion-v40",
    )


def build_single_adapter_fusion_v137_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v137",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V137_SPECS,
        base_profile="single-adapter-fusion-v40",
    )


def build_single_adapter_fusion_v138_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_single_adapter_fusion_strong_sample_rows(
        rows,
        profile_name="single-adapter-fusion-v138",
        augmentation_specs=STRONG_BASELINE_V2_SAMPLE_FUSION_V138_SPECS,
        base_profile="single-adapter-fusion-v40",
    )


def build_strong_baseline_cot_v2_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    grouped_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        source_type = str(row.get("baseline_source_type", "")).strip()
        if source_type:
            grouped_rows[source_type].append(clone_phase2_row(row))

    sampled_rows: list[dict[str, str]] = []
    transform_counts: Counter[str] = Counter()
    rng = random.Random(STRONG_BASELINE_V2_SEED)
    for source_type, target_count in STRONG_BASELINE_V2_TYPE_SAMPLES.items():
        source_rows = grouped_rows.get(source_type, [])
        if not source_rows:
            raise ValueError(f"Strong baseline source is missing rows for type {source_type!r}")
        if target_count >= len(source_rows):
            selected_rows = [clone_phase2_row(row) for row in source_rows]
            transform_counts[f"keep_all:{source_type}"] += len(selected_rows)
        else:
            selected_rows = [clone_phase2_row(row) for row in rng.sample(source_rows, target_count)]
            transform_counts[f"sample:{source_type}"] += len(selected_rows)
        sampled_rows.extend(selected_rows)
    rng.shuffle(sampled_rows)
    return sampled_rows, {
        "profile": "strong-baseline-cot-v2",
        "input": summarize_phase2_rows(rows),
        "output": summarize_phase2_rows(sampled_rows),
        "transform_counts": {
            name: count for name, count in sorted(transform_counts.items())
        },
    }


def build_strong_baseline_cot_v2_structured_anchor_rows(
    rows: Sequence[dict[str, str]],
    *,
    profile_name: str,
    augmentation_specs: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    base_rows, base_summary = build_strong_baseline_cot_v2_rows(rows)
    profiled_rows = [clone_phase2_row(row) for row in base_rows]
    existing_ids = {
        str(row.get("id", "")).strip()
        for row in profiled_rows
        if str(row.get("id", "")).strip()
    }
    augmentation_rows: list[dict[str, str]] = []
    source_summaries: dict[str, Any] = {}
    transform_counts = Counter(base_summary.get("transform_counts", {}))

    for spec in augmentation_specs:
        source_name = str(spec.get("source_name", "")).strip()
        family = str(spec.get("family", "")).strip()
        label = str(spec.get("label", "")).strip()
        template_subtype = str(spec.get("template_subtype", "")).strip()
        if not source_name or not family or not label or not template_subtype:
            raise ValueError(f"{profile_name} has an invalid augmentation spec: {spec!r}")
        allowed_tiers = {str(value).strip().lower() for value in spec.get("allowed_tiers", ()) if str(value).strip()}
        candidates = select_joined_augmentation_candidates(
            base_path=DEFAULT_PHASE0_ANALYSIS_CSV,
            candidate_path=AUGMENT_TRAIN_RECOMMENDED_CSV,
            existing_ids=existing_ids,
            family=family,
            template_subtype=template_subtype,
            allowed_tiers=allowed_tiers or None,
            quota=int(spec.get("quota", 0)),
            group_keys=tuple(
                spec.get(
                    "group_keys",
                    ("template_subtype", "selection_tier", "teacher_solver_candidate"),
                )
            ),
            hard_first=bool(spec.get("hard_first", True)),
        )
        appended_rows: list[dict[str, str]] = []
        assistant_style = str(spec.get("assistant_style", "boxed_only")).strip() or "boxed_only"
        for candidate in candidates:
            phase2_row = make_phase2_row_from_candidate(
                candidate,
                label=label,
                assistant_style=assistant_style,
            )
            row_id = phase2_row["id"]
            if row_id in existing_ids:
                continue
            existing_ids.add(row_id)
            augmentation_rows.append(phase2_row)
            appended_rows.append(phase2_row)
            transform_counts[
                f"append_aug:{source_name}:{phase2_row['label']}:{phase2_row['source_selection_tier']}"
            ] += 1
        source_summaries[source_name] = {
            "selected": len(appended_rows),
            "summary": summarize_phase2_rows(appended_rows),
        }

    profiled_rows.extend(augmentation_rows)
    return profiled_rows, {
        "profile": profile_name,
        "input": base_summary.get("input", summarize_phase2_rows(rows)),
        "base": base_summary.get("output", summarize_phase2_rows(base_rows)),
        "output": summarize_phase2_rows(profiled_rows),
        "transform_counts": {
            name: count for name, count in sorted(transform_counts.items())
        },
        "augmentation": {
            "rows": len(augmentation_rows),
            "summary": summarize_phase2_rows(augmentation_rows),
            "sources": source_summaries,
        },
    }


def build_strong_baseline_cot_v2_structured_anchor_v1_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_strong_baseline_cot_v2_structured_anchor_rows(
        rows,
        profile_name="strong-baseline-cot-v2-structured-anchor-v1",
        augmentation_specs=STRONG_BASELINE_V2_STRUCTURED_ANCHOR_V1_SPECS,
    )


def build_strong_baseline_cot_v2_structured_anchor_v2_rows(
    rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    return build_strong_baseline_cot_v2_structured_anchor_rows(
        rows,
        profile_name="strong-baseline-cot-v2-structured-anchor-v2",
        augmentation_specs=STRONG_BASELINE_V2_STRUCTURED_ANCHOR_V2_SPECS,
    )


def apply_phase2_train_profile(
    rows: Sequence[dict[str, str]],
    *,
    profile: str,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    normalized_profile = str(profile).strip().lower() or "baseline"
    input_rows = [clone_phase2_row(row) for row in rows]
    if normalized_profile == "baseline":
        summary = summarize_phase2_rows(input_rows)
        return input_rows, {
            "profile": normalized_profile,
            "input": summary,
            "output": summary,
            "transform_counts": {},
        }
    if normalized_profile == "strong-baseline-cot-v2":
        return build_strong_baseline_cot_v2_rows(input_rows)
    if normalized_profile == "strong-baseline-cot-v2-structured-anchor-v1":
        return build_strong_baseline_cot_v2_structured_anchor_v1_rows(input_rows)
    if normalized_profile == "strong-baseline-cot-v2-structured-anchor-v2":
        return build_strong_baseline_cot_v2_structured_anchor_v2_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v15":
        return build_single_adapter_fusion_v15_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v16":
        return build_single_adapter_fusion_v16_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v17":
        return build_single_adapter_fusion_v17_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v18":
        return build_single_adapter_fusion_v18_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v19":
        return build_single_adapter_fusion_v19_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v20":
        return build_single_adapter_fusion_v20_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v21":
        return build_single_adapter_fusion_v21_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v22":
        return build_single_adapter_fusion_v22_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v23":
        return build_single_adapter_fusion_v23_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v24":
        return build_single_adapter_fusion_v24_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v25":
        return build_single_adapter_fusion_v25_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v26":
        return build_single_adapter_fusion_v26_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v27":
        return build_single_adapter_fusion_v27_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v28":
        return build_single_adapter_fusion_v28_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v29":
        return build_single_adapter_fusion_v29_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v30":
        return build_single_adapter_fusion_v30_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v31":
        return build_single_adapter_fusion_v31_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v140":
        return build_single_adapter_fusion_v140_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v141":
        return build_single_adapter_fusion_v141_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v142":
        return build_single_adapter_fusion_v142_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v32":
        return build_single_adapter_fusion_v32_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v33":
        return build_single_adapter_fusion_v33_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v34":
        return build_single_adapter_fusion_v34_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v35":
        return build_single_adapter_fusion_v35_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v36":
        return build_single_adapter_fusion_v36_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v37":
        return build_single_adapter_fusion_v37_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v38":
        return build_single_adapter_fusion_v38_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v39":
        return build_single_adapter_fusion_v39_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v40":
        return build_single_adapter_fusion_v40_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v41":
        return build_single_adapter_fusion_v41_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v42":
        return build_single_adapter_fusion_v42_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v43":
        return build_single_adapter_fusion_v43_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v44":
        return build_single_adapter_fusion_v44_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v45":
        return build_single_adapter_fusion_v45_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v46":
        return build_single_adapter_fusion_v46_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v47":
        return build_single_adapter_fusion_v47_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v48":
        return build_single_adapter_fusion_v48_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v49":
        return build_single_adapter_fusion_v49_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v50":
        return build_single_adapter_fusion_v50_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v51":
        return build_single_adapter_fusion_v51_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v52":
        return build_single_adapter_fusion_v52_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v53":
        return build_single_adapter_fusion_v53_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v54":
        return build_single_adapter_fusion_v54_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v55":
        return build_single_adapter_fusion_v55_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v56":
        return build_single_adapter_fusion_v56_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v57":
        return build_single_adapter_fusion_v57_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v58":
        return build_single_adapter_fusion_v58_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v59":
        return build_single_adapter_fusion_v59_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v60":
        return build_single_adapter_fusion_v60_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v61":
        return build_single_adapter_fusion_v61_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v62":
        return build_single_adapter_fusion_v62_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v63":
        return build_single_adapter_fusion_v63_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v64":
        return build_single_adapter_fusion_v64_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v65":
        return build_single_adapter_fusion_v65_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v66":
        return build_single_adapter_fusion_v66_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v67":
        return build_single_adapter_fusion_v67_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v68":
        return build_single_adapter_fusion_v68_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v69":
        return build_single_adapter_fusion_v69_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v70":
        return build_single_adapter_fusion_v70_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v71":
        return build_single_adapter_fusion_v71_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v72":
        return build_single_adapter_fusion_v72_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v73":
        return build_single_adapter_fusion_v73_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v74":
        return build_single_adapter_fusion_v74_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v75":
        return build_single_adapter_fusion_v75_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v76":
        return build_single_adapter_fusion_v76_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v77":
        return build_single_adapter_fusion_v77_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v78":
        return build_single_adapter_fusion_v78_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v79":
        return build_single_adapter_fusion_v79_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v80":
        return build_single_adapter_fusion_v80_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v81":
        return build_single_adapter_fusion_v81_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v82":
        return build_single_adapter_fusion_v82_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v83":
        return build_single_adapter_fusion_v83_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v84":
        return build_single_adapter_fusion_v84_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v88":
        return build_single_adapter_fusion_v88_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v89":
        return build_single_adapter_fusion_v89_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v90":
        return build_single_adapter_fusion_v90_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v91":
        return build_single_adapter_fusion_v91_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v92":
        return build_single_adapter_fusion_v92_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v93":
        return build_single_adapter_fusion_v93_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v94":
        return build_single_adapter_fusion_v94_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v95":
        return build_single_adapter_fusion_v95_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v96":
        return build_single_adapter_fusion_v96_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v97":
        return build_single_adapter_fusion_v97_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v98":
        return build_single_adapter_fusion_v98_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v99":
        return build_single_adapter_fusion_v99_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v100":
        return build_single_adapter_fusion_v100_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v101":
        return build_single_adapter_fusion_v101_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v102":
        return build_single_adapter_fusion_v102_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v103":
        return build_single_adapter_fusion_v103_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v104":
        return build_single_adapter_fusion_v104_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v105":
        return build_single_adapter_fusion_v105_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v106":
        return build_single_adapter_fusion_v106_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v107":
        return build_single_adapter_fusion_v107_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v108":
        return build_single_adapter_fusion_v108_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v109":
        return build_single_adapter_fusion_v109_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v110":
        return build_single_adapter_fusion_v110_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v111":
        return build_single_adapter_fusion_v111_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v112":
        return build_single_adapter_fusion_v112_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v113":
        return build_single_adapter_fusion_v113_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v114":
        return build_single_adapter_fusion_v114_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v115":
        return build_single_adapter_fusion_v115_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v116":
        return build_single_adapter_fusion_v116_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v117":
        return build_single_adapter_fusion_v117_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v118":
        return build_single_adapter_fusion_v118_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v119":
        return build_single_adapter_fusion_v119_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v120":
        return build_single_adapter_fusion_v120_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v121":
        return build_single_adapter_fusion_v121_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v122":
        return build_single_adapter_fusion_v122_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v123":
        return build_single_adapter_fusion_v123_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v124":
        return build_single_adapter_fusion_v124_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v128":
        return build_single_adapter_fusion_v128_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v129":
        return build_single_adapter_fusion_v129_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v131":
        return build_single_adapter_fusion_v131_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v132":
        return build_single_adapter_fusion_v132_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v133":
        return build_single_adapter_fusion_v133_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v134":
        return build_single_adapter_fusion_v134_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v135":
        return build_single_adapter_fusion_v135_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v136":
        return build_single_adapter_fusion_v136_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v137":
        return build_single_adapter_fusion_v137_rows(input_rows)
    if normalized_profile == "single-adapter-fusion-v138":
        return build_single_adapter_fusion_v138_rows(input_rows)
    if normalized_profile not in TRAIN_PROFILE_CHOICES:
        raise ValueError(f"Unsupported train profile: {profile}")

    profiled_rows: list[dict[str, str]] = []
    transform_counts: Counter[str] = Counter()
    for original_row in input_rows:
        row = clone_phase2_row(original_row)
        label = str(row.get("label", "")).strip().lower()
        tier = str(row.get("source_selection_tier", "")).strip().lower()
        style = str(row.get("assistant_style", "")).strip().lower()
        if normalized_profile.startswith("single-adapter-focus"):
            if label in {"roman", "text"}:
                transform_counts[f"drop:{label}"] += 1
                continue
            if label in {"binary", "symbol"}:
                if style != "boxed_only":
                    row["assistant_style"] = "boxed_only"
                    transform_counts[f"force_boxed_only:{label}:{tier or 'unknown'}"] += 1
                else:
                    transform_counts[f"keep_boxed_only:{label}:{tier or 'unknown'}"] += 1
            else:
                transform_counts[f"keep:{label}:{style or 'unknown'}"] += 1
            profiled_rows.append(row)
            if (
                normalized_profile == "single-adapter-focus-v2"
                and label in {"binary", "symbol"}
                and tier == "answer_only_keep"
            ):
                profiled_rows.append(clone_phase2_row(row))
                transform_counts[f"repeat:{label}:{tier}"] += 1
            continue

        if normalized_profile in {
            "single-adapter-fusion-v1",
            "single-adapter-fusion-v2",
            "single-adapter-fusion-v3",
            "single-adapter-fusion-v4",
            "single-adapter-fusion-v5",
            "single-adapter-fusion-v6",
            "single-adapter-fusion-v7",
            "single-adapter-fusion-v8",
            "single-adapter-fusion-v9",
            "single-adapter-fusion-v10",
            "single-adapter-fusion-v11",
            "single-adapter-fusion-v12",
            "single-adapter-fusion-v13",
            "single-adapter-fusion-v14",
        }:
            if normalized_profile in {
                "single-adapter-fusion-v7",
                "single-adapter-fusion-v8",
                "single-adapter-fusion-v9",
                "single-adapter-fusion-v10",
                "single-adapter-fusion-v11",
                "single-adapter-fusion-v12",
                "single-adapter-fusion-v13",
                "single-adapter-fusion-v14",
            }:
                row_key = str(row.get("id") or row.get("prompt") or "")
                fusion_settings = {
                    "single-adapter-fusion-v7": {
                        "binary_repeats": 1,
                        "symbol_repeats": 2,
                        "unit_mod": 2,
                        "text_repeats": 1,
                        "roman_mod": 0,
                        "tier_aware_boxing": False,
                    },
                    "single-adapter-fusion-v8": {
                        "binary_repeats": 1,
                        "symbol_repeats": 1,
                        "unit_mod": 3,
                        "text_repeats": 1,
                        "roman_mod": 0,
                        "tier_aware_boxing": False,
                    },
                    "single-adapter-fusion-v9": {
                        "binary_repeats": 2,
                        "symbol_repeats": 2,
                        "unit_mod": 2,
                        "text_repeats": 1,
                        "roman_mod": 0,
                        "tier_aware_boxing": False,
                    },
                    "single-adapter-fusion-v10": {
                        "binary_repeats": 1,
                        "symbol_repeats": 2,
                        "unit_mod": 2,
                        "text_repeats": 1,
                        "roman_mod": 2,
                        "tier_aware_boxing": True,
                    },
                    "single-adapter-fusion-v11": {
                        "binary_repeats": 1,
                        "symbol_repeats": 2,
                        "binary_repeats_by_tier": {
                            "answer_only_keep": 3,
                            "manual_audit_priority": 2,
                        },
                        "symbol_repeats_by_tier": {
                            "answer_only_keep": 4,
                            "manual_audit_priority": 0,
                        },
                        "trace_repeats_by_tier": {},
                        "unit_mod": 2,
                        "text_repeats": 2,
                        "roman_mod": 2,
                        "tier_aware_boxing": True,
                    },
                    "single-adapter-fusion-v12": {
                        "binary_repeats": 1,
                        "symbol_repeats": 2,
                        "binary_repeats_by_tier": {
                            "verified_trace_ready": 2,
                            "answer_only_keep": 3,
                            "manual_audit_priority": 2,
                        },
                        "symbol_repeats_by_tier": {
                            "answer_only_keep": 4,
                            "manual_audit_priority": 0,
                        },
                        "trace_repeats_by_tier": {
                            "binary:verified_trace_ready": 1,
                            "symbol:verified_trace_ready": 1,
                        },
                        "unit_mod": 2,
                        "text_repeats": 2,
                        "roman_mod": 2,
                        "tier_aware_boxing": True,
                    },
                    "single-adapter-fusion-v13": {
                        "binary_repeats": 1,
                        "symbol_repeats": 2,
                        "binary_repeats_by_tier": {
                            "answer_only_keep": 1,
                        },
                        "symbol_repeats_by_tier": {
                            "answer_only_keep": 3,
                        },
                        "trace_repeats_by_tier": {},
                        "unit_mod": 2,
                        "text_repeats": 1,
                        "roman_mod": 2,
                        "tier_aware_boxing": True,
                    },
                    "single-adapter-fusion-v14": {
                        "binary_repeats": 1,
                        "symbol_repeats": 2,
                        "binary_repeats_by_tier": {
                            "answer_only_keep": 2,
                        },
                        "symbol_repeats_by_tier": {
                            "answer_only_keep": 3,
                        },
                        "trace_repeats_by_tier": {},
                        "unit_mod": 2,
                        "text_repeats": 1,
                        "roman_mod": 2,
                        "tier_aware_boxing": True,
                    },
                }[normalized_profile]
                if label in {"binary", "symbol"}:
                    use_boxed_primary = True
                    if fusion_settings["tier_aware_boxing"]:
                        use_boxed_primary = tier == "answer_only_keep"
                    repeat_count = (
                        fusion_settings.get(f"{label}_repeats_by_tier", {}).get(
                            tier,
                            fusion_settings["binary_repeats"]
                            if label == "binary"
                            else fusion_settings["symbol_repeats"],
                        )
                    )
                    trace_repeat_count = fusion_settings.get(
                        "trace_repeats_by_tier", {}
                    ).get(f"{label}:{tier}", 0)
                    if use_boxed_primary:
                        specialist_row = clone_phase2_row(row)
                        if style != "boxed_only":
                            specialist_row["assistant_style"] = "boxed_only"
                            transform_counts[f"force_boxed_primary:{label}:{tier or 'unknown'}"] += 1
                        else:
                            transform_counts[f"keep_boxed_primary:{label}:{tier or 'unknown'}"] += 1
                        profiled_rows.append(specialist_row)
                        specialist_style = "boxed_only"
                    else:
                        profiled_rows.append(row)
                        transform_counts[f"keep:{label}:{style or 'unknown'}"] += 1
                        for _ in range(trace_repeat_count):
                            profiled_rows.append(clone_phase2_row(row))
                            transform_counts[f"repeat_trace:{label}:{tier or 'unknown'}"] += 1
                        specialist_row = clone_phase2_row(row)
                        if style != "boxed_only":
                            specialist_row["assistant_style"] = "boxed_only"
                            transform_counts[f"add_boxed_anchor:{label}:{tier or 'unknown'}"] += 1
                        else:
                            transform_counts[f"reuse_boxed_anchor:{label}:{tier or 'unknown'}"] += 1
                        profiled_rows.append(specialist_row)
                        specialist_style = str(specialist_row.get("assistant_style", "")).strip().lower()
                    for _ in range(repeat_count):
                        if specialist_style == "boxed_only":
                            transform_counts[f"repeat_boxed:{label}:{tier or 'unknown'}"] += 1
                        else:
                            transform_counts[f"repeat:{label}:{tier or 'unknown'}"] += 1
                        profiled_rows.append(clone_phase2_row(specialist_row))
                    continue

                profiled_rows.append(row)
                transform_counts[f"keep:{label}:{style or 'unknown'}"] += 1
                if label == "text":
                    for _ in range(fusion_settings["text_repeats"]):
                        profiled_rows.append(clone_phase2_row(row))
                        transform_counts[f"repeat:{label}:{tier or 'unknown'}"] += 1
                elif label == "unit":
                    unit_mod = fusion_settings["unit_mod"]
                    if unit_mod > 0 and stable_mod(row_key, unit_mod) == 0:
                        profiled_rows.append(clone_phase2_row(row))
                        if unit_mod == 2:
                            transform_counts[f"repeat_half:{label}:{tier or 'unknown'}"] += 1
                        elif unit_mod == 3:
                            transform_counts[f"repeat_third:{label}:{tier or 'unknown'}"] += 1
                        else:
                            transform_counts[f"repeat_mod{unit_mod}:{label}:{tier or 'unknown'}"] += 1
                elif label == "roman":
                    roman_mod = fusion_settings["roman_mod"]
                    if roman_mod > 0 and stable_mod(row_key, roman_mod) == 0:
                        profiled_rows.append(clone_phase2_row(row))
                        if roman_mod == 2:
                            transform_counts[f"repeat_half:{label}:{tier or 'unknown'}"] += 1
                        else:
                            transform_counts[f"repeat_mod{roman_mod}:{label}:{tier or 'unknown'}"] += 1
                continue

            if normalized_profile == "single-adapter-fusion-v3" and label == "binary":
                boxed_binary = clone_phase2_row(row)
                if style != "boxed_only":
                    boxed_binary["assistant_style"] = "boxed_only"
                    transform_counts[f"force_boxed_primary:{label}:{tier or 'unknown'}"] += 1
                else:
                    transform_counts[f"keep_boxed_primary:{label}:{tier or 'unknown'}"] += 1
                profiled_rows.append(boxed_binary)
                for _ in range(2):
                    profiled_rows.append(clone_phase2_row(boxed_binary))
                    transform_counts[f"repeat_boxed:{label}:{tier or 'unknown'}"] += 1
                continue
            profiled_rows.append(row)
            if label in {"binary", "symbol"}:
                boxed_clone_repeats = 1
                if normalized_profile in {
                    "single-adapter-fusion-v2",
                    "single-adapter-fusion-v3",
                    "single-adapter-fusion-v4",
                    "single-adapter-fusion-v5",
                    "single-adapter-fusion-v6",
                } and label == "symbol":
                    boxed_clone_repeats = 2
                for repeat_index in range(boxed_clone_repeats):
                    if style == "boxed_only":
                        transform_counts[f"repeat_boxed:{label}:{tier or 'unknown'}"] += 1
                        profiled_rows.append(clone_phase2_row(row))
                    else:
                        transform_counts[f"add_boxed_clone:{label}:{tier or 'unknown'}"] += 1
                        boxed_clone = clone_phase2_row(row)
                        boxed_clone["assistant_style"] = "boxed_only"
                        profiled_rows.append(boxed_clone)
            elif (
                normalized_profile
                in {
                    "single-adapter-fusion-v4",
                    "single-adapter-fusion-v5",
                    "single-adapter-fusion-v6",
                }
                and label == "unit"
            ):
                row_key = str(row.get("id") or row.get("prompt") or "")
                repeat_unit = normalized_profile == "single-adapter-fusion-v4"
                if normalized_profile == "single-adapter-fusion-v5":
                    repeat_unit = stable_mod(row_key, 2) == 0
                elif normalized_profile == "single-adapter-fusion-v6":
                    repeat_unit = stable_mod(row_key, 3) == 0
                if repeat_unit:
                    profiled_rows.append(clone_phase2_row(row))
                    if normalized_profile == "single-adapter-fusion-v4":
                        transform_counts[f"repeat:{label}:{tier or 'unknown'}"] += 1
                    elif normalized_profile == "single-adapter-fusion-v5":
                        transform_counts[f"repeat_half:{label}:{tier or 'unknown'}"] += 1
                    else:
                        transform_counts[f"repeat_third:{label}:{tier or 'unknown'}"] += 1
                else:
                    transform_counts[f"keep:{label}:{style or 'unknown'}"] += 1
            else:
                transform_counts[f"keep:{label}:{style or 'unknown'}"] += 1
            continue

        if normalized_profile.startswith("general-stable-focus"):
            if label in {"binary", "symbol"}:
                transform_counts[f"drop:{label}"] += 1
                continue
            if normalized_profile == "general-stable-focus-v3" and label == "text" and style != "boxed_only":
                row["assistant_style"] = "boxed_only"
                transform_counts[f"force_boxed_only:{label}:{tier or 'unknown'}"] += 1
            else:
                transform_counts[f"keep:{label}:{style or 'unknown'}"] += 1
            profiled_rows.append(row)
            if normalized_profile in {"general-stable-focus-v2", "general-stable-focus-v3"} and label == "text":
                profiled_rows.append(clone_phase2_row(row))
                transform_counts[f"repeat:{label}:{tier or 'unknown'}"] += 1
            continue

        raise ValueError(f"Unsupported train profile: {profile}")
    if not profiled_rows:
        raise ValueError(f"Train profile {profile} removed all training rows.")
    return profiled_rows, {
        "profile": normalized_profile,
        "input": summarize_phase2_rows(input_rows),
        "output": summarize_phase2_rows(profiled_rows),
        "transform_counts": {
            name: count for name, count in sorted(transform_counts.items())
        },
    }


def build_phase2_chat_records(rows: Sequence[dict[str, str]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        prompt = str(row.get("prompt", "")).strip()
        if not prompt:
            raise ValueError(f"Row {row.get('id', '')} is missing prompt")
        assistant_content = render_assistant_message(row)
        records.append(
            {
                "messages": [
                    {"role": "user", "content": build_user_message(prompt)},
                    {"role": "assistant", "content": assistant_content},
                ],
                "metadata": {
                    "id": row.get("id", ""),
                    "answer": row.get("answer", ""),
                    "label": row.get("label", ""),
                    "assistant_style": row.get("assistant_style", ""),
                    "source_selection_tier": row.get("source_selection_tier", ""),
                },
            }
        )
    return records


def build_phase2_completion_records(rows: Sequence[dict[str, str]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        prompt = str(row.get("prompt", "")).strip()
        if not prompt:
            raise ValueError(f"Row {row.get('id', '')} is missing prompt")
        records.append(
            {
                "prompt": build_user_message(prompt),
                "completion": render_assistant_message(row),
                "metadata": {
                    "id": row.get("id", ""),
                    "answer": row.get("answer", ""),
                    "label": row.get("label", ""),
                    "assistant_style": row.get("assistant_style", ""),
                    "source_selection_tier": row.get("source_selection_tier", ""),
                },
            }
        )
    return records


def build_phase2_text_records(rows: Sequence[dict[str, str]], *, tokenizer: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        prompt = str(row.get("prompt", "")).strip()
        if not prompt:
            raise ValueError(f"Row {row.get('id', '')} is missing prompt")
        user_message = build_user_message(prompt)
        assistant_message = render_assistant_message(row)
        full_text = apply_chat_template_safe(
            tokenizer,
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message},
            ],
            add_generation_prompt=False,
            enable_thinking=True,
        )
        records.append(
            {
                "text": full_text,
                "metadata": {
                    "id": row.get("id", ""),
                    "answer": row.get("answer", ""),
                    "label": row.get("label", ""),
                    "assistant_style": row.get("assistant_style", ""),
                    "source_selection_tier": row.get("source_selection_tier", ""),
                },
            }
        )
    return records


def select_shadow_validation_records(
    records: Sequence[dict[str, Any]],
    *,
    valid_rows: int,
    minimum_rows: int,
    seed: int,
) -> list[dict[str, Any]]:
    if not records:
        raise ValueError("Training records are empty")
    valid_rows = max(1, valid_rows, minimum_rows)
    valid_rows = min(valid_rows, len(records))
    rng = random.Random(seed)
    chosen = sorted(rng.sample(range(len(records)), valid_rows))
    return [records[index] for index in chosen]


def compute_total_iters(num_rows: int, num_epochs: float, batch_size: int) -> int:
    effective_rows = max(1, num_rows)
    return max(1, int(effective_rows * num_epochs // max(batch_size, 1)))


def build_mlx_lora_config(
    *,
    model_path: Path,
    dataset_dir: Path,
    adapter_dir: Path,
    resume_adapter_file: Path | None,
    mask_prompt: bool,
    enable_thinking: bool,
    batch_size: int,
    num_epochs: float,
    learning_rate: float,
    max_seq_length: int,
    grad_accumulation_steps: int,
    lora_rank: int,
    lora_scale: float,
    lora_dropout: float,
    num_layers: int,
    steps_per_report: int,
    steps_per_eval: int,
    seed: int,
    lr_schedule_name: str | None,
    lr_schedule_end: float,
    lr_warmup_ratio: float,
) -> dict[str, Any]:
    total_iters = compute_total_iters(
        num_rows=sum(1 for _ in (dataset_dir / "train.jsonl").open("r", encoding="utf-8")),
        num_epochs=num_epochs,
        batch_size=batch_size,
    )
    schedule_name = str(lr_schedule_name or "").strip()
    if lr_warmup_ratio < 0.0 or lr_warmup_ratio >= 1.0:
        raise ValueError(f"lr_warmup_ratio must be in [0, 1), got {lr_warmup_ratio}")
    config: dict[str, Any] = {
        "model": str(model_path),
        "train": True,
        "data": str(dataset_dir),
        "fine_tune_type": "lora",
        "optimizer": "adamw",
        "mask_prompt": mask_prompt,
        "enable_thinking": enable_thinking,
        "num_layers": num_layers,
        "batch_size": batch_size,
        "iters": total_iters,
        "val_batches": -1,
        "learning_rate": learning_rate,
        "steps_per_report": steps_per_report,
        "steps_per_eval": steps_per_eval,
        "grad_accumulation_steps": grad_accumulation_steps,
        "adapter_path": str(adapter_dir),
        "save_every": total_iters,
        "max_seq_length": max_seq_length,
        "grad_checkpoint": True,
        "seed": seed,
        "lora_parameters": {
            "rank": lora_rank,
            "dropout": lora_dropout,
            "scale": lora_scale,
        },
    }
    if resume_adapter_file is not None:
        config["resume_adapter_file"] = str(resume_adapter_file)
    if schedule_name:
        if schedule_name != "cosine_decay":
            raise ValueError(f"Unsupported lr_schedule_name: {schedule_name}")
        schedule_config: dict[str, Any] = {
            "name": schedule_name,
            "arguments": [learning_rate, total_iters, float(lr_schedule_end)],
        }
        warmup_steps = int(total_iters * lr_warmup_ratio)
        if warmup_steps > 0:
            schedule_config["warmup"] = warmup_steps
        config["lr_schedule"] = schedule_config
    return config


def render_train_command(config_path: Path) -> str:
    return "\n".join(
        [
            "#!/bin/bash",
            "set -euo pipefail",
            f'"{sys.executable}" "{Path(__file__).resolve()}" train-mlx-config --config "{config_path}"',
            "",
        ]
    )


def summarize_directory(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for child in sorted(path.iterdir()):
        rows.append(
            {
                "name": child.name,
                "is_dir": child.is_dir(),
                "size_bytes": child.stat().st_size if child.is_file() else 0,
            }
        )
    return rows


def prepare_training_run(args: argparse.Namespace) -> dict[str, Any]:
    run_root = Path(args.output_root).resolve() / args.run_name
    ensure_dir(run_root)
    shadow_model_dir = build_shadow_model_dir(
        Path(args.model_root),
        run_root / "shadow_model",
        force=bool(args.force_shadow_model),
    )
    source_rows = load_training_source_rows(
        Path(args.train_csv),
        profile=str(args.train_profile),
    )
    profiled_rows, profile_summary = apply_phase2_train_profile(
        source_rows,
        profile=str(args.train_profile),
    )
    dataset_format = str(args.dataset_format).strip().lower()
    if dataset_format == "completions":
        dataset_format = "completion"
    if dataset_format not in {"chat", "completion", "text"}:
        raise ValueError(f"Unsupported dataset_format: {dataset_format}")
    if dataset_format == "chat":
        train_records = build_phase2_chat_records(profiled_rows)
        mask_prompt = True
        enable_thinking = True
    elif dataset_format == "completion":
        train_records = build_phase2_completion_records(profiled_rows)
        mask_prompt = True
        enable_thinking = True
        completion_thinking = str(getattr(args, "completion_thinking", "auto")).strip().lower()
        if completion_thinking not in {"auto", "on", "off"}:
            raise ValueError(f"Unsupported completion_thinking: {completion_thinking}")
        if completion_thinking == "on":
            enable_thinking = True
        elif completion_thinking == "off":
            enable_thinking = False
    else:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(str(shadow_model_dir), trust_remote_code=True)
        if tokenizer.pad_token is None and tokenizer.eos_token is not None:
            tokenizer.pad_token = tokenizer.eos_token
        train_records = build_phase2_text_records(profiled_rows, tokenizer=tokenizer)
        mask_prompt = False
        enable_thinking = False
    valid_records = select_shadow_validation_records(
        train_records,
        valid_rows=int(args.valid_shadow_rows),
        minimum_rows=int(args.batch_size),
        seed=int(args.seed),
    )

    dataset_dir = run_root / "dataset"
    adapter_dir = run_root / "adapter"
    write_jsonl_records(dataset_dir / "train.jsonl", train_records)
    write_jsonl_records(dataset_dir / "valid.jsonl", valid_records)
    test_path = dataset_dir / "test.jsonl"
    if test_path.exists():
        test_path.unlink()

    config = build_mlx_lora_config(
        model_path=shadow_model_dir,
        dataset_dir=dataset_dir,
        adapter_dir=adapter_dir,
        resume_adapter_file=(
            Path(args.resume_adapter_file).resolve()
            if getattr(args, "resume_adapter_file", None)
            else None
        ),
        mask_prompt=mask_prompt,
        enable_thinking=enable_thinking,
        batch_size=int(args.batch_size),
        num_epochs=float(args.num_epochs),
        learning_rate=float(args.learning_rate),
        max_seq_length=int(args.max_seq_length),
        grad_accumulation_steps=int(args.grad_accumulation_steps),
        lora_rank=int(args.lora_rank),
        lora_scale=float(args.lora_alpha),
        lora_dropout=float(args.lora_dropout),
        num_layers=int(args.num_layers),
        steps_per_report=int(args.steps_per_report),
        steps_per_eval=int(args.steps_per_eval),
        seed=int(args.seed),
        lr_schedule_name=getattr(args, "lr_schedule_name", None),
        lr_schedule_end=float(getattr(args, "lr_schedule_end", 0.0)),
        lr_warmup_ratio=float(getattr(args, "lr_warmup_ratio", 0.0)),
    )

    config_path = run_root / "mlx_lora_config.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    command_path = run_root / "train_cmd.sh"
    command_path.write_text(render_train_command(config_path), encoding="utf-8")

    manifest = {
        "created_at": utc_now(),
        "repo_root": str(REPO_ROOT),
        "run_root": str(run_root),
        "model_root": str(Path(args.model_root).resolve()),
        "shadow_model_dir": str(shadow_model_dir),
        "train_csv": str(Path(args.train_csv).resolve()),
        "source_rows": len(source_rows),
        "training_profile": profile_summary,
        "dataset": {
            "dataset_dir": str(dataset_dir),
            "dataset_format": dataset_format,
            "enable_thinking": enable_thinking,
            "completion_thinking": str(getattr(args, "completion_thinking", "auto")).strip().lower(),
            "train_rows": len(train_records),
            "valid_rows": len(valid_records),
            "valid_strategy": f"shadow_sample={int(args.valid_shadow_rows)}",
        },
        "training": {
            "mask_prompt": mask_prompt,
            "resume_adapter_file": (
                str(Path(args.resume_adapter_file).resolve())
                if getattr(args, "resume_adapter_file", None)
                else ""
            ),
            "batch_size": int(args.batch_size),
            "grad_accumulation_steps": int(args.grad_accumulation_steps),
            "num_epochs": float(args.num_epochs),
            "learning_rate": float(args.learning_rate),
            "lr_schedule_name": str(getattr(args, "lr_schedule_name", "") or ""),
            "lr_schedule_end": float(getattr(args, "lr_schedule_end", 0.0)),
            "lr_warmup_ratio": float(getattr(args, "lr_warmup_ratio", 0.0)),
            "max_seq_length": int(args.max_seq_length),
            "lora_rank": int(args.lora_rank),
            "lora_alpha": float(args.lora_alpha),
            "lora_dropout": float(args.lora_dropout),
            "num_layers": int(args.num_layers),
            "steps_per_report": int(args.steps_per_report),
            "steps_per_eval": int(args.steps_per_eval),
            "total_iters": int(config["iters"]),
        },
        "versions": load_versions(),
        "artifacts": {
            "config_path": str(config_path),
            "command_path": str(command_path),
            "adapter_dir": str(adapter_dir),
        },
    }
    write_json(run_root / "prepare_manifest.json", manifest)
    return manifest


def verify_training_outputs(adapter_dir: Path) -> None:
    required = [
        adapter_dir / "adapter_config.json",
        adapter_dir / "adapters.safetensors",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "MLX training did not produce expected adapter files: " + ", ".join(missing)
        )


def normalize_adapter_config_for_merge(config: dict[str, Any]) -> dict[str, Any]:
    fine_tune_type = str(config.get("fine_tune_type", "lora"))
    if fine_tune_type == "full":
        raise ValueError("Full fine-tune checkpoints are not supported by merge-adapters.")
    lora_parameters = dict(config.get("lora_parameters") or {})
    if not lora_parameters:
        raise ValueError("Adapter config is missing lora_parameters.")
    rank = int(lora_parameters.get("rank", 0))
    if rank <= 0:
        raise ValueError(f"Invalid LoRA rank in adapter config: {rank}")
    if rank > README_MAX_LORA_RANK:
        raise ValueError(
            f"LoRA rank {rank} exceeds README max_lora_rank={README_MAX_LORA_RANK}."
        )
    return {
        "fine_tune_type": fine_tune_type,
        "num_layers": int(config.get("num_layers", -1)),
        "lora_parameters": lora_parameters,
    }


def load_adapter_tensors(adapter_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    from safetensors.numpy import load_file

    verify_training_outputs(adapter_dir)
    config = load_json(adapter_dir / "adapter_config.json", default=None)
    if not isinstance(config, dict):
        raise ValueError(f"Invalid adapter_config.json: {adapter_dir / 'adapter_config.json'}")
    tensors = load_file(str(adapter_dir / "adapters.safetensors"))
    return config, tensors


def resolve_merged_num_layers(*, generalist_layers: int, specialist_layers: int) -> int:
    if generalist_layers < 0 or specialist_layers < 0:
        return -1
    return max(generalist_layers, specialist_layers)


def merge_adapter_configs(
    *,
    generalist_config: dict[str, Any],
    specialist_config: dict[str, Any],
    generalist_source: str,
    specialist_source: str,
    generalist_weight: float,
    specialist_weight: float,
) -> dict[str, Any]:
    generalist = normalize_adapter_config_for_merge(generalist_config)
    specialist = normalize_adapter_config_for_merge(specialist_config)
    if generalist["fine_tune_type"] != specialist["fine_tune_type"]:
        raise ValueError(
            "Cannot merge adapters with different fine_tune_type values: "
            f"{generalist['fine_tune_type']} vs {specialist['fine_tune_type']}"
        )
    if generalist["lora_parameters"] != specialist["lora_parameters"]:
        raise ValueError(
            "Cannot merge adapters with different lora_parameters. "
            f"generalist={generalist['lora_parameters']} specialist={specialist['lora_parameters']}"
        )
    return {
        "created_at": utc_now(),
        "fine_tune_type": generalist["fine_tune_type"],
        "num_layers": resolve_merged_num_layers(
            generalist_layers=int(generalist["num_layers"]),
            specialist_layers=int(specialist["num_layers"]),
        ),
        "lora_parameters": generalist["lora_parameters"],
        "merge_sources": {
            "generalist": str(generalist_source),
            "specialist": str(specialist_source),
        },
        "merge_weights": {
            "generalist": float(generalist_weight),
            "specialist": float(specialist_weight),
        },
        "merge_strategy": "weighted_union_zero_fill",
    }


def merge_adapter_tensors(
    *,
    generalist_tensors: dict[str, Any],
    specialist_tensors: dict[str, Any],
    generalist_weight: float,
    specialist_weight: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    merged_tensors: dict[str, Any] = {}
    overlap_keys = 0
    generalist_only_keys = 0
    specialist_only_keys = 0
    for key in sorted(set(generalist_tensors) | set(specialist_tensors)):
        generalist_value = generalist_tensors.get(key)
        specialist_value = specialist_tensors.get(key)
        if generalist_value is not None and specialist_value is not None:
            if tuple(generalist_value.shape) != tuple(specialist_value.shape):
                raise ValueError(
                    f"Shape mismatch for tensor '{key}': "
                    f"{tuple(generalist_value.shape)} vs {tuple(specialist_value.shape)}"
                )
            merged_value = (
                float(generalist_weight) * generalist_value.astype("float32")
                + float(specialist_weight) * specialist_value.astype("float32")
            )
            merged_tensors[key] = merged_value.astype(generalist_value.dtype)
            overlap_keys += 1
        elif generalist_value is not None:
            merged_tensors[key] = (
                float(generalist_weight) * generalist_value.astype("float32")
            ).astype(generalist_value.dtype)
            generalist_only_keys += 1
        elif specialist_value is not None:
            merged_tensors[key] = (
                float(specialist_weight) * specialist_value.astype("float32")
            ).astype(specialist_value.dtype)
            specialist_only_keys += 1
    stats = {
        "merged_tensor_count": len(merged_tensors),
        "overlap_tensor_count": overlap_keys,
        "generalist_only_tensor_count": generalist_only_keys,
        "specialist_only_tensor_count": specialist_only_keys,
    }
    return merged_tensors, stats


def run_merge_adapters(args: argparse.Namespace) -> None:
    from safetensors.numpy import save_file

    generalist_adapter_dir = Path(args.generalist_adapter).resolve()
    specialist_adapter_dir = Path(args.specialist_adapter).resolve()
    run_root = Path(args.output_root).resolve() / str(args.merge_name)
    adapter_dir = run_root / "adapter"
    ensure_dir(adapter_dir)

    generalist_config, generalist_tensors = load_adapter_tensors(generalist_adapter_dir)
    specialist_config, specialist_tensors = load_adapter_tensors(specialist_adapter_dir)
    merged_config = merge_adapter_configs(
        generalist_config=generalist_config,
        specialist_config=specialist_config,
        generalist_source=str(generalist_adapter_dir),
        specialist_source=str(specialist_adapter_dir),
        generalist_weight=float(args.generalist_weight),
        specialist_weight=float(args.specialist_weight),
    )
    merged_tensors, merge_stats = merge_adapter_tensors(
        generalist_tensors=generalist_tensors,
        specialist_tensors=specialist_tensors,
        generalist_weight=float(args.generalist_weight),
        specialist_weight=float(args.specialist_weight),
    )
    save_file(merged_tensors, str(adapter_dir / "adapters.safetensors"))
    write_json(adapter_dir / "adapter_config.json", merged_config)
    manifest = {
        "created_at": utc_now(),
        "run_root": str(run_root),
        "adapter_dir": str(adapter_dir),
        "generalist_adapter_dir": str(generalist_adapter_dir),
        "specialist_adapter_dir": str(specialist_adapter_dir),
        "generalist_weight": float(args.generalist_weight),
        "specialist_weight": float(args.specialist_weight),
        "adapter_config": merged_config,
        "merge_stats": merge_stats,
    }
    write_json(run_root / "merge_manifest.json", manifest)
    verify_training_outputs(adapter_dir)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def benchmark_columns() -> list[str]:
    return [
        "benchmark_name",
        "benchmark_role",
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
    ]


def normalize_family_label(row: dict[str, str]) -> str:
    family = row.get("family", "")
    if family in FAMILY_SHORT:
        return FAMILY_SHORT[family]
    label = row.get("label", "")
    if label in FAMILY_SHORT:
        return FAMILY_SHORT[label]
    if label:
        return label
    return family


def to_benchmark_row(
    row: dict[str, str],
    *,
    benchmark_name: str,
    benchmark_role: str,
) -> dict[str, Any]:
    return {
        "benchmark_name": benchmark_name,
        "benchmark_role": benchmark_role,
        "id": row.get("id", ""),
        "family": row.get("family", ""),
        "family_short": normalize_family_label(row),
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
    }


def score_rank_low(row: dict[str, str]) -> tuple[Any, ...]:
    hard_score = parse_float(row.get("hard_score"), 999.0)
    if hard_score is None:
        hard_score = 999.0
    return (
        hard_score,
        parse_int(row.get("prompt_len_chars"), 99999),
        -parse_int(row.get("num_examples"), 0),
        row.get("id", ""),
    )


def score_rank_high(row: dict[str, str]) -> tuple[Any, ...]:
    hard_score = parse_float(row.get("hard_score"), -999.0)
    if hard_score is None:
        hard_score = -999.0
    return (
        -hard_score,
        -parse_int(row.get("prompt_len_chars"), 0),
        -parse_int(row.get("num_examples"), 0),
        row.get("id", ""),
    )


def balanced_take(
    rows: list[dict[str, str]],
    *,
    quota: int,
    group_keys: Sequence[str],
    hard_first: bool,
) -> list[dict[str, str]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = tuple(str(row.get(name, "") or "") for name in group_keys)
        grouped[key].append(row)
    rank_fn = score_rank_high if hard_first else score_rank_low
    ordered_groups = sorted(grouped.items(), key=lambda item: (item[0], len(item[1])))
    for _, group_rows in ordered_groups:
        group_rows.sort(key=rank_fn)
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


def build_general_stable_set(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for family, quota in GENERAL_STABLE_QUOTAS.items():
        candidates = [
            row
            for row in rows
            if row.get("family") == family
            and row.get("selection_tier") == "verified_trace_ready"
            and parse_bool(row.get("verified_trace_ready", "true"))
        ]
        family_rows = balanced_take(
            candidates,
            quota=quota,
            group_keys=("template_subtype", "teacher_solver_candidate"),
            hard_first=False,
        )
        selected.extend(
            to_benchmark_row(
                row,
                benchmark_name="general_stable_set",
                benchmark_role="stable_replay",
            )
            for row in family_rows
        )
    return selected


def build_binary_hard_set(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    binary_rows = [row for row in rows if row.get("family") == "bit_manipulation"]
    for tier, quota in BINARY_HARD_TIER_QUOTAS.items():
        candidates = [row for row in binary_rows if row.get("selection_tier") == tier]
        tier_rows = balanced_take(
            candidates,
            quota=quota,
            group_keys=(
                "teacher_solver_candidate",
                "bit_structured_formula_abstract_family",
                "group_signature",
            ),
            hard_first=True,
        )
        selected.extend(
            to_benchmark_row(
                row,
                benchmark_name="binary_hard_set",
                benchmark_role="hard_binary_watch",
            )
            for row in tier_rows
        )
    return selected


def fill_symbol_watch_candidates(
    rows: list[dict[str, str]],
    already_selected_ids: set[str],
) -> list[dict[str, Any]]:
    remaining = [
        row
        for row in rows
        if row.get("family") == "symbol_equation" and row.get("id", "") not in already_selected_ids
    ]
    remaining.sort(key=score_rank_high)
    filler: list[dict[str, Any]] = []
    for row in remaining:
        filler.append(
            to_benchmark_row(
                row,
                benchmark_name="symbol_watch_set",
                benchmark_role="symbol_watch",
            )
        )
        if len(filler) >= 60:
            break
    return filler


def build_symbol_watch_set(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    symbol_rows = [row for row in rows if row.get("family") == "symbol_equation"]
    for template_subtype, tier, quota in SYMBOL_WATCH_TARGETS:
        candidates = [
            row
            for row in symbol_rows
            if row.get("template_subtype") == template_subtype and row.get("selection_tier") == tier
        ]
        watch_rows = balanced_take(
            candidates,
            quota=quota,
            group_keys=("symbol_query_operator", "teacher_solver_candidate"),
            hard_first=True,
        )
        for row in watch_rows:
            row_id = row.get("id", "")
            if row_id in selected_ids:
                continue
            selected.append(
                to_benchmark_row(
                    row,
                    benchmark_name="symbol_watch_set",
                    benchmark_role="symbol_watch",
                )
            )
            selected_ids.add(row_id)
    if len(selected) < 60:
        for row in fill_symbol_watch_candidates(rows, selected_ids):
            row_id = row["id"]
            if row_id in selected_ids:
                continue
            selected.append(row)
            selected_ids.add(row_id)
            if len(selected) >= 60:
                break
    return selected


def holdout_key_structured_family(row: dict[str, str]) -> str:
    value = str(row.get("bit_structured_formula_abstract_family", "")).strip()
    return value or "__none__"


def holdout_key_solver(row: dict[str, str]) -> str:
    value = str(row.get("teacher_solver_candidate", "")).strip()
    return value or "__none__"


def holdout_key_gap(row: dict[str, str]) -> str:
    num_examples = parse_int(row.get("num_examples"), 0)
    no_candidate = parse_int(row.get("bit_no_candidate_positions"), -1)
    multi_candidate = parse_int(row.get("bit_multi_candidate_positions"), -1)
    return f"ex{num_examples}__no{no_candidate}__multi{multi_candidate}"


def holdout_key_prompt_signature(row: dict[str, str]) -> str:
    group_signature = str(row.get("group_signature", "")).strip()
    if group_signature:
        return group_signature
    prompt = str(row.get("prompt", ""))
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def assign_balanced_group_folds(keys: list[str], num_folds: int) -> dict[str, int]:
    group_counts = Counter(keys)
    fold_loads = [0 for _ in range(num_folds)]
    assignments: dict[str, int] = {}
    ordered_groups = sorted(group_counts.items(), key=lambda item: (-item[1], item[0]))
    for group_key, group_size in ordered_groups:
        preferred = stable_mod(group_key, num_folds)
        best_fold = min(
            range(num_folds),
            key=lambda fold: (fold_loads[fold], abs(fold - preferred), fold),
        )
        assignments[group_key] = best_fold
        fold_loads[best_fold] += group_size
    return assignments


def build_binary_holdout_assignments(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    binary_rows = [row for row in rows if row.get("family") == "bit_manipulation"]
    key_builders = {
        "structured_family": holdout_key_structured_family,
        "solver_family": holdout_key_solver,
        "gap_signature": holdout_key_gap,
        "prompt_signature": holdout_key_prompt_signature,
    }
    fold_maps = {
        holdout_kind: assign_balanced_group_folds(
            [key_builder(row) for row in binary_rows],
            HOLDOUT_FOLDS,
        )
        for holdout_kind, key_builder in key_builders.items()
    }
    assignments: list[dict[str, Any]] = []
    for row in binary_rows:
        for holdout_kind, key_builder in key_builders.items():
            holdout_key = key_builder(row)
            fold = fold_maps[holdout_kind][holdout_key]
            assignments.append(
                {
                    "id": row.get("id", ""),
                    "family": row.get("family", ""),
                    "selection_tier": row.get("selection_tier", ""),
                    "template_subtype": row.get("template_subtype", ""),
                    "teacher_solver_candidate": row.get("teacher_solver_candidate", ""),
                    "holdout_kind": holdout_kind,
                    "holdout_key": holdout_key,
                    "fold": fold,
                    "num_examples": parse_int(row.get("num_examples"), 0),
                    "bit_no_candidate_positions": parse_int(row.get("bit_no_candidate_positions"), -1),
                    "bit_multi_candidate_positions": parse_int(row.get("bit_multi_candidate_positions"), -1),
                    "group_signature": row.get("group_signature", ""),
                }
            )
    return assignments


def summarize_benchmark(rows: list[dict[str, Any]]) -> dict[str, Any]:
    family_counts = Counter(row["family_short"] for row in rows)
    tier_counts = Counter(row["selection_tier"] for row in rows)
    template_counts = Counter(row["template_subtype"] for row in rows)
    return {
        "rows": len(rows),
        "family_counts": dict(sorted(family_counts.items())),
        "selection_tier_counts": dict(sorted(tier_counts.items())),
        "template_subtype_counts": dict(sorted(template_counts.items())),
    }


def build_phase0_manifest(
    *,
    analysis_csv: Path,
    general_rows: list[dict[str, Any]],
    binary_rows: list[dict[str, Any]],
    symbol_rows: list[dict[str, Any]],
    holdouts: list[dict[str, Any]],
) -> dict[str, Any]:
    holdout_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in holdouts:
        holdout_counts[row["holdout_kind"]][str(row["fold"])] += 1
    return {
        "phase": "phase0_offline_eval",
        "source_analysis_csv": str(analysis_csv),
        "readme_eval_assumptions": {
            "metric": "accuracy",
            "temperature": README_TEMPERATURE,
            "top_p": README_TOP_P,
            "max_tokens": README_MAX_TOKENS,
            "max_num_seqs": README_MAX_NUM_SEQS,
            "max_model_len": README_MAX_MODEL_LEN,
            "boxed_first_extraction": True,
            "numeric_relative_tolerance": 1e-2,
        },
        "benchmark_sets": {
            "general_stable_set": summarize_benchmark(general_rows),
            "binary_hard_set": summarize_benchmark(binary_rows),
            "symbol_watch_set": summarize_benchmark(symbol_rows),
        },
        "binary_holdouts": {
            holdout_kind: dict(sorted(folds.items()))
            for holdout_kind, folds in sorted(holdout_counts.items())
        },
    }


def render_phase0_report(manifest: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Phase 0 Offline Eval Manifest")
    lines.append("")
    lines.append("## README-aligned evaluation assumptions")
    lines.append("")
    for key, value in manifest["readme_eval_assumptions"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Benchmark sets")
    lines.append("")
    lines.append("| set | rows | family_counts | selection_tier_counts |")
    lines.append("| --- | ---: | --- | --- |")
    for set_name, payload in manifest["benchmark_sets"].items():
        lines.append(
            f"| `{set_name}` | {payload['rows']} | "
            f"`{json.dumps(payload['family_counts'], ensure_ascii=False)}` | "
            f"`{json.dumps(payload['selection_tier_counts'], ensure_ascii=False)}` |"
        )
    lines.append("")
    lines.append("## Binary holdout fold counts")
    lines.append("")
    lines.append("| holdout_kind | fold_counts |")
    lines.append("| --- | --- |")
    for holdout_kind, fold_counts in manifest["binary_holdouts"].items():
        lines.append(f"| `{holdout_kind}` | `{json.dumps(fold_counts, ensure_ascii=False)}` |")
    lines.append("")
    return "\n".join(lines)


def mark_status_rows(rows: Sequence[dict[str, Any]], benchmark_name: str) -> list[dict[str, Any]]:
    marked: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        new_row = dict(row)
        new_row["benchmark_index"] = index
        new_row["benchmark_name"] = benchmark_name
        marked.append(new_row)
    return marked


def extract_final_answer(text: str | None) -> str:
    if text is None:
        return "NOT_FOUND"
    matches = BOXED_PATTERN.findall(text)
    if matches:
        non_empty = [match.strip() for match in matches if match.strip()]
        if non_empty:
            return non_empty[-1]
        return matches[-1].strip()
    for pattern in FINAL_ANSWER_PATTERNS:
        matched = __import__("re").findall(pattern, text, __import__("re").IGNORECASE)
        if matched:
            return matched[-1].strip()
    numeric_matches = NUMBER_PATTERN.findall(text)
    if numeric_matches:
        return numeric_matches[-1]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else "NOT_FOUND"


def verify_answer(gold: str, predicted: str) -> bool:
    gold = str(gold).strip()
    predicted = str(predicted).strip()
    try:
        gold_num = float(gold)
        pred_num = float(predicted)
        return math.isclose(gold_num, pred_num, rel_tol=1e-2, abs_tol=1e-5)
    except Exception:
        return predicted.lower() == gold.lower()


def analyze_raw_output(text: str | None) -> dict[str, Any]:
    if text is None:
        return {
            "extracted_answer": "NOT_FOUND",
            "fallback_type": "not_found",
            "format_bucket": "not_found",
            "has_boxed": False,
            "boxed_count": 0,
        }
    boxed_matches = BOXED_PATTERN.findall(text)
    numeric_matches = NUMBER_PATTERN.findall(text)
    if boxed_matches:
        non_empty = [match.strip() for match in boxed_matches if match.strip()]
        if non_empty:
            return {
                "extracted_answer": non_empty[-1],
                "fallback_type": "boxed_non_empty",
                "format_bucket": "boxed",
                "has_boxed": True,
                "boxed_count": len(boxed_matches),
            }
        return {
            "extracted_answer": boxed_matches[-1].strip(),
            "fallback_type": "boxed_empty",
            "format_bucket": "boxed_empty",
            "has_boxed": True,
            "boxed_count": len(boxed_matches),
        }
    for pattern in FINAL_ANSWER_PATTERNS:
        matched = __import__("re").findall(pattern, text, __import__("re").IGNORECASE)
        if matched:
            return {
                "extracted_answer": matched[-1].strip(),
                "fallback_type": "final_answer_phrase",
                "format_bucket": "final_answer",
                "has_boxed": False,
                "boxed_count": 0,
            }
    if numeric_matches:
        return {
            "extracted_answer": numeric_matches[-1],
            "fallback_type": "last_number",
            "format_bucket": "numeric_fallback",
            "has_boxed": False,
            "boxed_count": 0,
        }
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return {
        "extracted_answer": lines[-1] if lines else "NOT_FOUND",
        "fallback_type": "last_line" if lines else "not_found",
        "format_bucket": "line_fallback" if lines else "not_found",
        "has_boxed": False,
        "boxed_count": 0,
    }


def safe_div(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def aggregate_counts(rows: Sequence[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"rows": 0, "correct": 0})
    for row in rows:
        bucket_key = str(row.get(key, ""))
        buckets[bucket_key]["rows"] += 1
        buckets[bucket_key]["correct"] += int(bool(row.get("is_correct")))
    summary: list[dict[str, Any]] = []
    for bucket_key, stats in sorted(buckets.items()):
        summary.append(
            {
                key: bucket_key,
                "rows": stats["rows"],
                "correct": stats["correct"],
                "accuracy": round(safe_div(stats["correct"], stats["rows"]), 4),
            }
        )
    return summary


def build_binary_metrics(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    binary_rows = [
        row
        for row in rows
        if row.get("family") == "bit_manipulation" or row.get("family_short") == "binary"
    ]
    regex_ok = [row for row in binary_rows if BIT8_PATTERN.fullmatch(str(row.get("prediction", "")))]
    gold_leading_zero_rows = [
        row for row in binary_rows if str(row.get("gold_answer", "")).startswith("0")
    ]
    leading_zero_ok = [
        row
        for row in gold_leading_zero_rows
        if BIT8_PATTERN.fullmatch(str(row.get("prediction", "")))
        and str(row.get("prediction", "")).startswith("0")
    ]
    format_ok = [
        row
        for row in binary_rows
        if row.get("has_boxed") and BIT8_PATTERN.fullmatch(str(row.get("prediction", "")))
    ]
    format_fail = [row for row in binary_rows if row not in format_ok]
    format_ok_but_wrong = [row for row in format_ok if not row.get("is_correct")]
    return {
        "rows": len(binary_rows),
        "boxed_extraction_success_rate": round(
            safe_div(
                sum(int(row.get("fallback_type") == "boxed_non_empty") for row in binary_rows),
                len(binary_rows),
            ),
            4,
        ),
        "regex_exact_rate": round(safe_div(len(regex_ok), len(binary_rows)), 4),
        "leading_zero_retention_rate": round(
            safe_div(len(leading_zero_ok), len(gold_leading_zero_rows)),
            4,
        ),
        "format_failure_rate": round(safe_div(len(format_fail), len(binary_rows)), 4),
        "format_ok_content_wrong_rate": round(safe_div(len(format_ok_but_wrong), len(format_ok)), 4),
        "solver_family_accuracy": aggregate_counts(binary_rows, "teacher_solver_candidate"),
    }


def summarize_scored_rows(row_level: Sequence[dict[str, Any]]) -> dict[str, Any]:
    return {
        "overall": {
            "rows": len(row_level),
            "correct": sum(int(row["is_correct"]) for row in row_level),
            "accuracy": round(
                safe_div(sum(int(row["is_correct"]) for row in row_level), len(row_level)),
                4,
            ),
        },
        "by_family": aggregate_counts(row_level, "family_short"),
        "by_template_subtype": aggregate_counts(row_level, "template_subtype"),
        "by_answer_type": aggregate_counts(row_level, "answer_type"),
        "by_prompt_len_bucket": aggregate_counts(row_level, "prompt_len_bucket"),
        "by_num_examples": aggregate_counts(row_level, "num_examples"),
        "by_selection_tier": aggregate_counts(row_level, "selection_tier"),
        "binary_metrics": build_binary_metrics(row_level),
    }


def render_markdown_summary(name: str, summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {name}")
    lines.append("")
    overall = summary["overall"]
    lines.append("## Overall")
    lines.append("")
    lines.append(f"- rows: `{overall['rows']}`")
    lines.append(f"- correct: `{overall['correct']}`")
    lines.append(f"- accuracy: `{overall['accuracy']:.4f}`")
    lines.append("")

    def add_table(title: str, rows: Sequence[dict[str, Any]], key_name: str) -> None:
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"| {key_name} | rows | correct | accuracy |")
        lines.append("| --- | ---: | ---: | ---: |")
        for row in rows:
            lines.append(
                f"| `{row[key_name]}` | {row['rows']} | {row['correct']} | {row['accuracy']:.4f} |"
            )
        lines.append("")

    add_table("Family accuracy", summary["by_family"], "family_short")
    add_table("Template subtype accuracy", summary["by_template_subtype"], "template_subtype")
    add_table("Answer type accuracy", summary["by_answer_type"], "answer_type")
    add_table("Prompt length buckets", summary["by_prompt_len_bucket"], "prompt_len_bucket")
    add_table("Num examples", summary["by_num_examples"], "num_examples")
    add_table("Selection tier accuracy", summary["by_selection_tier"], "selection_tier")

    binary_metrics = summary["binary_metrics"]
    lines.append("## Binary metrics")
    lines.append("")
    for key in (
        "rows",
        "boxed_extraction_success_rate",
        "regex_exact_rate",
        "leading_zero_retention_rate",
        "format_failure_rate",
        "format_ok_content_wrong_rate",
    ):
        lines.append(f"- {key}: `{binary_metrics[key]}`")
    lines.append("")
    lines.append("### Binary solver-family accuracy")
    lines.append("")
    lines.append("| teacher_solver_candidate | rows | correct | accuracy |")
    lines.append("| --- | ---: | ---: | ---: |")
    for row in binary_metrics["solver_family_accuracy"]:
        lines.append(
            f"| `{row['teacher_solver_candidate']}` | {row['rows']} | {row['correct']} | {row['accuracy']:.4f} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_binary_holdout_accuracy_rows(
    scored_rows: Sequence[dict[str, Any]],
    holdout_rows: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    binary_by_id = {
        row["id"]: row
        for row in scored_rows
        if row.get("family") == "bit_manipulation" or row.get("family_short") == "binary"
    }
    joined: list[dict[str, Any]] = []
    for holdout in holdout_rows:
        scored = binary_by_id.get(holdout.get("id", ""))
        if scored is None:
            continue
        joined.append(
            {
                "holdout_kind": holdout.get("holdout_kind", ""),
                "fold": str(holdout.get("fold", "")),
                "rows": 1,
                "correct": int(bool(scored.get("is_correct"))),
            }
        )
    buckets: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"rows": 0, "correct": 0})
    for row in joined:
        key = (row["holdout_kind"], row["fold"])
        buckets[key]["rows"] += row["rows"]
        buckets[key]["correct"] += row["correct"]
    summary: list[dict[str, Any]] = []
    for (holdout_kind, fold), stats in sorted(buckets.items()):
        summary.append(
            {
                "holdout_kind": holdout_kind,
                "fold": fold,
                "rows": stats["rows"],
                "correct": stats["correct"],
                "accuracy": round(safe_div(stats["correct"], stats["rows"]), 4),
            }
        )
    return summary


def prepare_phase0_benchmark_artifacts(
    *,
    prebuilt_root: Path,
    analysis_csv: Path,
    artifact_root: Path,
    report_root: Path,
    rebuild: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    ensure_dir(artifact_root)
    ensure_dir(report_root)
    prebuilt_general = prebuilt_root / "general_stable_set.csv"
    prebuilt_binary = prebuilt_root / "binary_hard_set.csv"
    prebuilt_symbol = prebuilt_root / "symbol_watch_set.csv"
    prebuilt_holdouts = prebuilt_root / "binary_holdout_assignments.csv"
    prebuilt_manifest = prebuilt_root / "phase0_eval_manifest.json"
    prebuilt_ready = (
        not rebuild
        and prebuilt_general.exists()
        and prebuilt_binary.exists()
        and prebuilt_symbol.exists()
    )

    if prebuilt_ready:
        general_rows = load_csv_rows(prebuilt_general)
        binary_rows = load_csv_rows(prebuilt_binary)
        symbol_rows = load_csv_rows(prebuilt_symbol)
        holdout_rows = load_csv_rows(prebuilt_holdouts) if prebuilt_holdouts.exists() else []
        manifest = load_json(prebuilt_manifest, default=None)
        if manifest is None:
            manifest = build_phase0_manifest(
                analysis_csv=analysis_csv,
                general_rows=general_rows,
                binary_rows=binary_rows,
                symbol_rows=symbol_rows,
                holdouts=holdout_rows,
            )
    else:
        analysis_rows = load_csv_rows(analysis_csv)
        general_rows = build_general_stable_set(analysis_rows)
        binary_rows = build_binary_hard_set(analysis_rows)
        symbol_rows = build_symbol_watch_set(analysis_rows)
        holdout_rows = build_binary_holdout_assignments(analysis_rows)
        manifest = build_phase0_manifest(
            analysis_csv=analysis_csv,
            general_rows=general_rows,
            binary_rows=binary_rows,
            symbol_rows=symbol_rows,
            holdouts=holdout_rows,
        )

    general_rows = mark_status_rows(general_rows, "general_stable_set")
    binary_rows = mark_status_rows(binary_rows, "binary_hard_set")
    symbol_rows = mark_status_rows(symbol_rows, "symbol_watch_set")
    benchmark_rows = general_rows + binary_rows + symbol_rows

    benchmark_fieldnames = benchmark_columns() + ["benchmark_index"]
    write_csv_rows(artifact_root / "general_stable_set.csv", general_rows, benchmark_fieldnames)
    write_csv_rows(artifact_root / "binary_hard_set.csv", binary_rows, benchmark_fieldnames)
    write_csv_rows(artifact_root / "symbol_watch_set.csv", symbol_rows, benchmark_fieldnames)
    if holdout_rows:
        write_csv_rows(
            artifact_root / "binary_holdout_assignments.csv",
            holdout_rows,
            [
                "id",
                "family",
                "selection_tier",
                "template_subtype",
                "teacher_solver_candidate",
                "holdout_kind",
                "holdout_key",
                "fold",
                "num_examples",
                "bit_no_candidate_positions",
                "bit_multi_candidate_positions",
                "group_signature",
            ],
        )
    write_csv_rows(artifact_root / "phase0_combined_eval_set.csv", benchmark_rows, benchmark_fieldnames)
    write_json(artifact_root / "phase0_eval_manifest.json", manifest)
    write_text(report_root / "phase0_eval_manifest.md", render_phase0_report(manifest))
    return benchmark_rows, holdout_rows, manifest


def build_prompts(tokenizer: Any, prompt_series: Sequence[str], *, enable_thinking: bool = True) -> list[str]:
    prompts: list[str] = []
    for prompt_text in prompt_series:
        user_content = f"{prompt_text}\n{BOXED_INSTRUCTION}"
        try:
            rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": user_content}],
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=enable_thinking,
            )
        except TypeError:
            rendered = tokenizer.apply_chat_template(
                [{"role": "user", "content": user_content}],
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            rendered = user_content
        prompts.append(rendered)
    return prompts


def load_jsonl_records(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            rows.append(json.loads(stripped))
    return rows


def tail_text(path: Path, max_chars: int = 6000) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def clamp_eval_batch_size(value: int | None, *, default: int, max_num_seqs: int) -> int:
    candidate = default if value is None or int(value) <= 0 else int(value)
    return max(1, min(candidate, int(max_num_seqs)))


def resolve_phase0_eval_num_shards(
    *,
    requested_shards: int,
    total_rows: int,
    memory_budget_gb: float,
    estimated_worker_memory_gb: float,
) -> int:
    if total_rows <= 0:
        return 1
    if requested_shards > 0:
        return max(1, min(requested_shards, total_rows))
    auto = int(float(memory_budget_gb) // max(float(estimated_worker_memory_gb), 1.0))
    auto = max(1, auto)
    return min(auto, total_rows)


def parse_comma_separated_set(raw: str) -> set[str]:
    return {part.strip() for part in str(raw).split(",") if part.strip()}


def filter_phase0_benchmark_rows(
    benchmark_rows: Sequence[dict[str, Any]],
    *,
    family_short_filter: str,
    per_family_limit: int,
) -> list[dict[str, Any]]:
    filtered = list(benchmark_rows)
    allowed_family_short = parse_comma_separated_set(family_short_filter)
    if allowed_family_short:
        filtered = [
            row
            for row in filtered
            if str(row.get("family_short", "")).strip() in allowed_family_short
        ]
    if per_family_limit > 0:
        counts: Counter[str] = Counter()
        limited: list[dict[str, Any]] = []
        for row in filtered:
            family_short = str(row.get("family_short", "")).strip()
            if counts[family_short] >= int(per_family_limit):
                continue
            counts[family_short] += 1
            limited.append(row)
        filtered = limited
    return filtered


def maybe_patch_batch_generator_stats(mx: Any) -> None:
    from mlx_lm.generate import BatchGenerator

    if getattr(BatchGenerator.stats, "_copilot_zero_time_safe", False):
        return

    def _safe_batch_generator_stats(self: Any) -> Any:
        stats = self._stats
        prompt_time = float(getattr(stats, "prompt_time", 0.0) or 0.0)
        generation_time = float(getattr(stats, "generation_time", 0.0) or 0.0)
        stats.prompt_tps = (
            float(getattr(stats, "prompt_tokens", 0) or 0) / prompt_time
            if prompt_time > 0.0
            else 0.0
        )
        stats.generation_tps = (
            float(getattr(stats, "generation_tokens", 0) or 0) / generation_time
            if generation_time > 0.0
            else 0.0
        )
        stats.peak_memory = mx.get_peak_memory() / 1e9
        return stats

    setattr(_safe_batch_generator_stats, "_copilot_zero_time_safe", True)
    BatchGenerator.stats = _safe_batch_generator_stats


def maybe_patch_mamba_cache_extract() -> None:
    import mlx.core as mx  # type: ignore
    from mlx_lm.models.cache import MambaCache  # type: ignore

    if hasattr(MambaCache, "extract") and getattr(MambaCache.extract, "_copilot_enabled", False):
        return
    if hasattr(MambaCache, "extract") and not getattr(MambaCache.extract, "_copilot_enabled", False):
        return

    def _extract(self: Any, idx: int) -> Any:
        cache = MambaCache()
        cache.cache = [
            None if state is None else mx.contiguous(state[idx : idx + 1])
            for state in self.cache
        ]
        cache.left_padding = None
        return cache

    setattr(_extract, "_copilot_enabled", True)
    MambaCache.extract = _extract


def encode_prompt(tokenizer: Any, prompt: str) -> list[int]:
    bos_token = getattr(tokenizer, "bos_token", None)
    add_special_tokens = bos_token is None or not prompt.startswith(str(bos_token))
    encoded = tokenizer.encode(prompt, add_special_tokens=add_special_tokens)
    return list(encoded)


def maybe_fix_tokenizer_eos_ids(tokenizer: Any) -> None:
    eos_token_id = getattr(tokenizer, "eos_token_id", None)
    eos_token = getattr(tokenizer, "eos_token", None)
    eos_token_ids = getattr(tokenizer, "eos_token_ids", None)
    if eos_token_id is None or eos_token != "<|im_end|>":
        return
    normalized_ids: set[int] = set()
    if eos_token_ids is not None:
        try:
            normalized_ids = {int(token_id) for token_id in eos_token_ids}
        except TypeError:
            normalized_ids = {int(eos_token_ids)}
    expected_id = int(eos_token_id)
    if normalized_ids == {expected_id}:
        return
    tokenizer.eos_token_ids = {expected_id}


def normalize_prompt_text(prompt: str) -> str:
    return " ".join(str(prompt).strip().lower().split())


def classify_phase0_prompt_family(prompt: str) -> str:
    normalized_prompt = normalize_prompt_text(prompt)
    if (
        "secret bit manipulation rule transforms 8-bit binary numbers" in normalized_prompt
        or "8-bit binary numbers" in normalized_prompt
    ):
        return "binary"
    if (
        "secret set of transformation rules is applied to equations" in normalized_prompt
        or (
            "determine the result for:" in normalized_prompt
            and any(symbol in str(prompt) for symbol in ("!", "^", "<", ">", "&", "@", "%"))
        )
    ):
        return "symbol"
    if (
        "secret encryption rules are used on text" in normalized_prompt
        or "decrypt the following text" in normalized_prompt
    ):
        return "text"
    if (
        "secret unit conversion is applied to measurements" in normalized_prompt
        or "convert the following measurement" in normalized_prompt
    ):
        return "unit"
    if (
        "gravitational constant has been secretly changed" in normalized_prompt
        or "determine the falling distance" in normalized_prompt
    ):
        return "gravity"
    if (
        "different numeral system" in normalized_prompt
        or "wonderland numeral system" in normalized_prompt
    ):
        return "roman"
    raise ValueError(f"Unable to classify benchmark prompt family: {prompt[:200]}")


def resolve_phase0_router_slot_map(profile: str) -> dict[str, str]:
    slot_map = PHASE0_ROUTER_SLOT_BY_FAMILY.get(str(profile).strip())
    if slot_map is None:
        raise ValueError(f"Unsupported phase0 router profile: {profile}")
    return dict(slot_map)


def build_phase0_router_summary(
    *,
    router_profile: str,
    assignments: Sequence[dict[str, Any]],
    slot_adapter_dirs: dict[str, Path | None],
    fallback_assignments: Sequence[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    slot_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    slot_family_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in assignments:
        slot = str(row.get("router_slot", "")).strip()
        family_short = str(row.get("router_family", "")).strip()
        slot_counts[slot] += 1
        family_counts[family_short] += 1
        slot_family_counts[slot][family_short] += 1
    summary = {
        "router_profile": router_profile,
        "slot_counts": dict(sorted(slot_counts.items())),
        "family_counts": dict(sorted(family_counts.items())),
        "slot_family_counts": {
            slot: dict(sorted(counter.items()))
            for slot, counter in sorted(slot_family_counts.items())
        },
        "slot_adapter_paths": {
            slot: (str(path.resolve()) if path is not None else "")
            for slot, path in sorted(slot_adapter_dirs.items())
        },
    }
    fallback_assignments = list(fallback_assignments or [])
    if fallback_assignments:
        fallback_target_counts: Counter[str] = Counter()
        fallback_family_counts: Counter[str] = Counter()
        fallback_reason_counts: Counter[str] = Counter()
        for row in fallback_assignments:
            fallback_target_counts[str(row.get("fallback_target", "")).strip()] += 1
            fallback_family_counts[str(row.get("family_short", "")).strip()] += 1
            fallback_reason_counts[str(row.get("fallback_reason", "")).strip()] += 1
        summary["fallback_count"] = len(fallback_assignments)
        summary["fallback_target_counts"] = dict(sorted(fallback_target_counts.items()))
        summary["fallback_family_counts"] = dict(sorted(fallback_family_counts.items()))
        summary["fallback_reason_counts"] = dict(sorted(fallback_reason_counts.items()))
    return summary


def is_phase0_router_numeric_like(text: str) -> bool:
    return bool(re.fullmatch(r"[-+]?\d+(?:\.\d+)?", str(text).strip()))


def resolve_phase0_router_fallback_target(
    *,
    router_profile: str,
    scored_row: dict[str, Any],
    benchmark_row: dict[str, Any] | None = None,
) -> tuple[str, str] | None:
    profile = str(router_profile).strip()
    if profile in {
        PHASE0_ROUTER_PROFILE_PROMPT_V4,
        PHASE0_ROUTER_PROFILE_PROMPT_V5,
        PHASE0_ROUTER_PROFILE_PROMPT_V6,
    }:
        family_short = str(scored_row.get("family_short", "")).strip()
        template_subtype = str(scored_row.get("template_subtype", "")).strip()
        if profile == PHASE0_ROUTER_PROFILE_PROMPT_V6 and family_short == "binary" and benchmark_row is not None:
            solver_prediction = maybe_solve_phase0_binary_formula_prompt(str(benchmark_row.get("prompt", "")))
            if solver_prediction is not None and solver_prediction != str(scored_row.get("prediction", "")).strip():
                return ("solver", "binary_formula_consensus_solver")
        if family_short == "symbol" and template_subtype == "numeric_2x2" and benchmark_row is not None:
            prompt_text = str(benchmark_row.get("prompt", ""))
            if profile == PHASE0_ROUTER_PROFILE_PROMPT_V4:
                solver_prediction = maybe_solve_phase0_symbol_numeric_prompt(prompt_text)
                fallback_reason = "symbol_numeric_safe_solver"
            else:
                solver_prediction = maybe_solve_phase0_symbol_numeric_zero_error_prompt(prompt_text)
                fallback_reason = "symbol_numeric_zero_error_solver"
            if solver_prediction is not None and solver_prediction != str(scored_row.get("prediction", "")).strip():
                return ("solver", fallback_reason)
        return None
    if profile != PHASE0_ROUTER_PROFILE_PROMPT_V2:
        return None
    family_short = str(scored_row.get("family_short", "")).strip()
    prediction = str(scored_row.get("prediction", "")).strip()
    prediction_lower = prediction.lower()
    format_bucket = str(scored_row.get("format_bucket", "")).strip()
    if family_short == "text":
        if format_bucket in {"numeric_fallback", "boxed_empty"}:
            return ("base", "text_format_fallback")
        if prediction_lower in {"", "your answer", "answer"}:
            return ("base", "text_placeholder_fallback")
        if is_phase0_router_numeric_like(prediction):
            return ("base", "text_numeric_fallback")
        return None
    if family_short == "roman":
        if format_bucket == "numeric_fallback" or is_phase0_router_numeric_like(prediction):
            return ("base", "roman_numeric_fallback")
    return None


def format_phase0_solver_numeric(value: float) -> str:
    rounded = round(float(value), 2)
    return f"{rounded:.2f}".rstrip("0").rstrip(".")


def parse_phase0_prompt_lines(prompt: str) -> list[str]:
    return [line.strip() for line in str(prompt).splitlines() if line.strip()]


def phase0_rotate_left_byte(value: int, shift: int) -> int:
    masked = value & 0xFF
    return ((masked << shift) & 0xFF) | (masked >> (8 - shift))


def phase0_rotate_right_byte(value: int, shift: int) -> int:
    masked = value & 0xFF
    return (masked >> shift) | ((masked << (8 - shift)) & 0xFF)


def phase0_reverse_byte_bits(value: int) -> int:
    return int(format(value & 0xFF, "08b")[::-1], 2)


def phase0_nibble_swap_byte(value: int) -> int:
    bits = format(value & 0xFF, "08b")
    return int(bits[4:] + bits[:4], 2)


@lru_cache(maxsize=1)
def build_phase0_binary_structured_byte_formulas() -> tuple[tuple[str, tuple[int, ...]], ...]:
    raw_sources = [
        ("x", lambda value: value & 0xFF),
        ("reverse", phase0_reverse_byte_bits),
        ("nibble_swap", phase0_nibble_swap_byte),
    ]
    for shift in range(1, 8):
        raw_sources.append((f"rol{shift}", lambda value, shift=shift: phase0_rotate_left_byte(value, shift)))
        raw_sources.append((f"ror{shift}", lambda value, shift=shift: phase0_rotate_right_byte(value, shift)))
    for shift in range(1, 8):
        raw_sources.append((f"shl{shift}", lambda value, shift=shift: ((value & 0xFF) << shift) & 0xFF))
        raw_sources.append((f"shr{shift}", lambda value, shift=shift: (value & 0xFF) >> shift))

    canonical_sources: dict[tuple[int, ...], str] = {}
    for name, function in raw_sources:
        signature = tuple(function(value) & 0xFF for value in range(256))
        canonical_sources.setdefault(signature, name)
    sources = [(name, signature) for signature, name in sorted(canonical_sources.items(), key=lambda item: item[1])]

    formulas: dict[tuple[int, ...], str] = {}
    for name, signature in sources:
        formulas.setdefault(signature, name)
    for (name_a, signature_a), (name_b, signature_b) in combinations_with_replacement(sources, 2):
        for op_name, operation in PHASE0_BINARY_STRUCTURED_BYTE_BINARY_OPERATIONS.items():
            signature = tuple(operation(signature_a[value], signature_b[value]) & 0xFF for value in range(256))
            formulas.setdefault(signature, f"{op_name}({name_a},{name_b})")
    for selector_name, selector_signature in sources:
        for true_name, true_signature in sources:
            for false_name, false_signature in sources:
                signature = tuple(
                    PHASE0_BINARY_STRUCTURED_BYTE_TERNARY_OPERATIONS["choose"](
                        selector_signature[value],
                        true_signature[value],
                        false_signature[value],
                    )
                    & 0xFF
                    for value in range(256)
                )
                formulas.setdefault(signature, f"choose({selector_name},{true_name},{false_name})")
    for (name_a, signature_a), (name_b, signature_b), (name_c, signature_c) in combinations_with_replacement(sources, 3):
        signature = tuple(
            PHASE0_BINARY_STRUCTURED_BYTE_TERNARY_OPERATIONS["majority"](
                signature_a[value],
                signature_b[value],
                signature_c[value],
            )
            & 0xFF
            for value in range(256)
        )
        formulas.setdefault(signature, f"majority({name_a},{name_b},{name_c})")
    return tuple((name, signature) for signature, name in sorted(formulas.items(), key=lambda item: item[1]))


@lru_cache(maxsize=1)
def build_phase0_binary_structured_byte_not_formulas() -> tuple[tuple[str, tuple[int, ...]], ...]:
    raw_sources = [
        ("x", lambda value: value & 0xFF),
        ("reverse", phase0_reverse_byte_bits),
        ("nibble_swap", phase0_nibble_swap_byte),
    ]
    for shift in range(1, 8):
        raw_sources.append((f"rol{shift}", lambda value, shift=shift: phase0_rotate_left_byte(value, shift)))
        raw_sources.append((f"ror{shift}", lambda value, shift=shift: phase0_rotate_right_byte(value, shift)))
    for shift in range(1, 8):
        raw_sources.append((f"shl{shift}", lambda value, shift=shift: ((value & 0xFF) << shift) & 0xFF))
        raw_sources.append((f"shr{shift}", lambda value, shift=shift: (value & 0xFF) >> shift))
    extended_sources = list(raw_sources)
    for name, function in raw_sources:
        extended_sources.append((f"not({name})", lambda value, function=function: (~function(value)) & 0xFF))

    canonical_sources: dict[tuple[int, ...], str] = {}
    for name, function in extended_sources:
        signature = tuple(function(value) & 0xFF for value in range(256))
        canonical_sources.setdefault(signature, name)
    sources = [(name, signature) for signature, name in sorted(canonical_sources.items(), key=lambda item: item[1])]

    formulas: dict[tuple[int, ...], str] = {}
    for name, signature in sources:
        formulas.setdefault(signature, name)
    for (name_a, signature_a), (name_b, signature_b) in combinations_with_replacement(sources, 2):
        for op_name, operation in PHASE0_BINARY_STRUCTURED_BYTE_BINARY_OPERATIONS.items():
            signature = tuple(operation(signature_a[value], signature_b[value]) & 0xFF for value in range(256))
            formulas.setdefault(signature, f"{op_name}({name_a},{name_b})")
    for selector_name, selector_signature in sources:
        for true_name, true_signature in sources:
            for false_name, false_signature in sources:
                signature = tuple(
                    PHASE0_BINARY_STRUCTURED_BYTE_TERNARY_OPERATIONS["choose"](
                        selector_signature[value],
                        true_signature[value],
                        false_signature[value],
                    )
                    & 0xFF
                    for value in range(256)
                )
                formulas.setdefault(signature, f"choose({selector_name},{true_name},{false_name})")
    for (name_a, signature_a), (name_b, signature_b), (name_c, signature_c) in combinations_with_replacement(sources, 3):
        signature = tuple(
            PHASE0_BINARY_STRUCTURED_BYTE_TERNARY_OPERATIONS["majority"](
                signature_a[value],
                signature_b[value],
                signature_c[value],
            )
            & 0xFF
            for value in range(256)
        )
        formulas.setdefault(signature, f"majority({name_a},{name_b},{name_c})")
    return tuple((name, signature) for signature, name in sorted(formulas.items(), key=lambda item: item[1]))


@lru_cache(maxsize=1)
def build_phase0_binary_prompt_local_extended_sources() -> tuple[tuple[str, tuple[int, ...]], ...]:
    raw_sources = [
        ("x", lambda value: value & 0xFF),
        ("reverse", phase0_reverse_byte_bits),
        ("nibble_swap", phase0_nibble_swap_byte),
        ("zero", lambda value: 0),
        ("ones", lambda value: 0xFF),
    ]
    for shift in range(1, 8):
        raw_sources.append((f"rol{shift}", lambda value, shift=shift: phase0_rotate_left_byte(value, shift)))
        raw_sources.append((f"ror{shift}", lambda value, shift=shift: phase0_rotate_right_byte(value, shift)))
    for shift in range(1, 8):
        raw_sources.append((f"shl{shift}", lambda value, shift=shift: ((value & 0xFF) << shift) & 0xFF))
        raw_sources.append((f"shr{shift}", lambda value, shift=shift: (value & 0xFF) >> shift))

    extended_sources = list(raw_sources)
    for name, function in raw_sources:
        if name in {"zero", "ones"}:
            continue
        extended_sources.append((f"not({name})", lambda value, function=function: (~function(value)) & 0xFF))
    for bit in range(8):
        mask = 1 << bit
        extended_sources.append((f"const_{mask:08b}", lambda value, mask=mask: mask))
        extended_sources.append((f"const_not_{mask:08b}", lambda value, mask=mask: (~mask) & 0xFF))

    canonical_sources: dict[tuple[int, ...], str] = {}
    for name, function in extended_sources:
        signature = tuple(function(value) & 0xFF for value in range(256))
        canonical_sources.setdefault(signature, name)
    return tuple((name, signature) for signature, name in sorted(canonical_sources.items(), key=lambda item: item[1]))


@lru_cache(maxsize=1)
def build_phase0_binary_prompt_local_stage1_formulas() -> tuple[tuple[str, tuple[int, ...]], ...]:
    sources = build_phase0_binary_prompt_local_extended_sources()
    formulas: dict[tuple[int, ...], str] = {}
    for name, signature in sources:
        formulas.setdefault(signature, name)
    for (name_a, signature_a), (name_b, signature_b) in combinations_with_replacement(sources, 2):
        for op_name, operation in PHASE0_BINARY_STRUCTURED_BYTE_BINARY_OPERATIONS.items():
            signature = tuple(operation(signature_a[value], signature_b[value]) & 0xFF for value in range(256))
            formulas.setdefault(signature, f"{op_name}({name_a},{name_b})")
    return tuple((name, signature) for signature, name in sorted(formulas.items(), key=lambda item: item[1]))


@lru_cache(maxsize=1)
def build_phase0_binary_prompt_local_stage2_formulas() -> tuple[tuple[str, tuple[int, ...]], ...]:
    sources = build_phase0_binary_prompt_local_extended_sources()
    stage1_formulas = build_phase0_binary_prompt_local_stage1_formulas()
    formulas: dict[tuple[int, ...], str] = {}
    for name, signature in stage1_formulas:
        formulas.setdefault(signature, name)
    for source_name, source_signature in sources:
        for formula_name, formula_signature in stage1_formulas:
            for op_name, operation in PHASE0_BINARY_STRUCTURED_BYTE_BINARY_OPERATIONS.items():
                signature = tuple(
                    operation(source_signature[value], formula_signature[value]) & 0xFF for value in range(256)
                )
                formulas.setdefault(signature, f"{op_name}({source_name},{formula_name})")
    return tuple((name, signature) for signature, name in sorted(formulas.items(), key=lambda item: item[1]))


def infer_phase0_binary_formula_matches(
    formulas: tuple[tuple[str, tuple[int, ...]], ...],
    examples: list[tuple[str, str]],
    query_bits: str,
) -> list[tuple[str, str]]:
    if len(query_bits) != 8 or not examples:
        return []
    pairs = [(int(input_bits, 2), int(output_bits, 2)) for input_bits, output_bits in examples]
    query_value = int(query_bits, 2)
    matches: list[tuple[str, str]] = []
    for formula_name, signature in formulas:
        if all(signature[input_value] == output_value for input_value, output_value in pairs):
            matches.append((formula_name, format(signature[query_value] & 0xFF, "08b")))
    return matches


def infer_phase0_binary_structured_formula_matches(
    examples: list[tuple[str, str]],
    query_bits: str,
) -> list[tuple[str, str]]:
    return infer_phase0_binary_formula_matches(build_phase0_binary_structured_byte_formulas(), examples, query_bits)


def infer_phase0_binary_structured_not_formula_matches(
    examples: list[tuple[str, str]],
    query_bits: str,
) -> list[tuple[str, str]]:
    return infer_phase0_binary_formula_matches(build_phase0_binary_structured_byte_not_formulas(), examples, query_bits)


def infer_phase0_binary_prompt_local_stage2_formula_matches(
    examples: list[tuple[str, str]],
    query_bits: str,
) -> list[tuple[str, str]]:
    return infer_phase0_binary_formula_matches(build_phase0_binary_prompt_local_stage2_formulas(), examples, query_bits)


def parse_phase0_binary_prompt(prompt: str) -> tuple[list[tuple[str, str]], str | None]:
    examples: list[tuple[str, str]] = []
    query_bits: str | None = None
    for line in parse_phase0_prompt_lines(prompt):
        example_match = PHASE0_BINARY_EXAMPLE_PATTERN.match(line)
        if example_match is not None:
            examples.append((example_match.group(1), example_match.group(2)))
            continue
        query_match = PHASE0_BINARY_QUERY_PATTERN.search(line)
        if query_match is not None:
            query_bits = query_match.group(1)
    return examples, query_bits


def collect_phase0_binary_formula_predictions(prompt: str) -> list[str]:
    examples, query_bits = parse_phase0_binary_prompt(prompt)
    if query_bits is None or not examples:
        return []
    predictions: set[str] = set()
    for matches in (
        infer_phase0_binary_structured_formula_matches(examples, query_bits),
        infer_phase0_binary_structured_not_formula_matches(examples, query_bits),
        infer_phase0_binary_prompt_local_stage2_formula_matches(examples, query_bits),
    ):
        unique_predictions = sorted({prediction for _, prediction in matches})
        if len(unique_predictions) == 1:
            predictions.add(unique_predictions[0])
    return sorted(predictions)


def maybe_solve_phase0_binary_formula_prompt(prompt: str) -> str | None:
    predictions = collect_phase0_binary_formula_predictions(prompt)
    if len(predictions) == 1:
        return predictions[0]
    return None


def normalize_phase0_symbol_query_operator(query_operator: str) -> str:
    normalized = str(query_operator).strip()
    if normalized == '""""':
        return '"'
    return normalized


@lru_cache(maxsize=1)
def load_phase0_symbol_numeric_safe_specs() -> dict[str, tuple[tuple[str, str, str], ...]]:
    grouped_specs: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    for row in load_csv_rows(AUGMENT_SYMBOL_OPERATOR_SPECIFIC_SUPPORT_CSV):
        if str(row.get("safe_operator_spec", "")).strip() == "True":
            grouped_specs[normalize_phase0_symbol_query_operator(row.get("query_operator", ""))].add(
                ("formula", str(row.get("formula_name", "")).strip(), str(row.get("format_name", "")).strip())
            )
    for row in load_csv_rows(AUGMENT_SYMBOL_REVERSE_OPERATOR_SUPPORT_CSV):
        if str(row.get("safe_operator_spec", "")).strip() == "True":
            grouped_specs[normalize_phase0_symbol_query_operator(row.get("query_operator", ""))].add(
                ("formula", str(row.get("formula_name", "")).strip(), str(row.get("format_name", "")).strip())
            )
    for row in load_csv_rows(AUGMENT_SYMBOL_MINUS_PREFIX_SUPPORT_CSV):
        if str(row.get("safe_subfamily", "")).strip() == "True":
            grouped_specs["-"].add(("subfamily", str(row.get("subfamily_name", "")).strip(), ""))
    for row in load_csv_rows(AUGMENT_SYMBOL_MINUS_DIRECT_SUPPORT_CSV):
        if str(row.get("safe_subfamily", "")).strip() == "True":
            grouped_specs["-"].add(("subfamily", str(row.get("subfamily_name", "")).strip(), ""))
    for row in load_csv_rows(AUGMENT_SYMBOL_STAR_PREFIX_SUPPORT_CSV):
        if str(row.get("safe_subfamily", "")).strip() == "True":
            grouped_specs["*"].add(("subfamily", str(row.get("subfamily_name", "")).strip(), ""))
    for row in load_csv_rows(AUGMENT_SYMBOL_THIN_SUPPORT2_SUPPORT_CSV):
        if str(row.get("safe_subfamily", "")).strip() == "True":
            grouped_specs[normalize_phase0_symbol_query_operator(row.get("query_operator", ""))].add(
                ("subfamily", str(row.get("subfamily_name", "")).strip(), "")
            )
    return {
        query_operator: tuple(sorted(specs))
        for query_operator, specs in sorted(grouped_specs.items())
    }


@lru_cache(maxsize=1)
def load_phase0_symbol_numeric_zero_error_formula_specs() -> dict[str, tuple[tuple[str, str], ...]]:
    grouped_specs: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for support_csv in (
        AUGMENT_SYMBOL_OPERATOR_SPECIFIC_SUPPORT_CSV,
        AUGMENT_SYMBOL_REVERSE_OPERATOR_SUPPORT_CSV,
    ):
        for row in load_csv_rows(support_csv):
            if str(row.get("error_rows", "")).strip() != "0":
                continue
            grouped_specs[normalize_phase0_symbol_query_operator(row.get("query_operator", ""))].add(
                (str(row.get("formula_name", "")).strip(), str(row.get("format_name", "")).strip())
            )
    return {
        query_operator: tuple(sorted(specs))
        for query_operator, specs in sorted(grouped_specs.items())
    }


def parse_phase0_symbol_numeric_prompt(
    prompt: str,
) -> tuple[list[tuple[str, str, str, str]], tuple[str, str, str]]:
    examples: list[tuple[str, str, str, str]] = []
    query: tuple[str, str, str] | None = None
    for line in parse_phase0_prompt_lines(prompt):
        example_match = PHASE0_SYMBOL_NUMERIC_EXAMPLE_PATTERN.match(line)
        if example_match is not None:
            examples.append(
                (
                    example_match.group(1),
                    example_match.group(2),
                    example_match.group(3),
                    example_match.group(4),
                )
            )
            continue
        query_match = PHASE0_SYMBOL_NUMERIC_QUERY_PATTERN.match(line)
        if query_match is not None:
            query = (query_match.group(1), query_match.group(2), query_match.group(3))
    if query is None:
        raise ValueError("Numeric symbol prompt is missing query line.")
    return examples, query


def format_phase0_symbol_numeric_value(operator: str, value: int, format_name: str) -> str:
    if format_name == "plain":
        return str(value)
    if format_name == "abs_plain":
        return str(abs(value))
    if format_name == "prefix_if_negative":
        if value < 0:
            return f"{operator}{abs(value)}"
        return str(value)
    if format_name == "prefix_always_abs":
        return f"{operator}{abs(value)}"
    if format_name == "prefix_abs_zpad2":
        return f"{operator}{str(abs(value)).zfill(2)}"
    if format_name == "string_template":
        return str(value)
    raise ValueError(f"Unsupported numeric symbol format: {format_name}")


def apply_phase0_symbol_numeric_formula_spec(
    operator: str,
    formula_name: str,
    format_name: str,
    x_text: str,
    y_text: str,
) -> str:
    reverse_inputs = False
    reverse_output = False
    if formula_name.endswith(PHASE0_SYMBOL_NUMERIC_REVERSE_SUFFIX):
        reverse_inputs = True
        reverse_output = True
        formula_name = formula_name[: -len(PHASE0_SYMBOL_NUMERIC_REVERSE_SUFFIX)]
    elif formula_name.endswith(PHASE0_SYMBOL_NUMERIC_REVERSE_OUTPUT_ONLY_SUFFIX):
        reverse_output = True
        formula_name = formula_name[: -len(PHASE0_SYMBOL_NUMERIC_REVERSE_OUTPUT_ONLY_SUFFIX)]
    elif formula_name.endswith(PHASE0_SYMBOL_NUMERIC_REVERSE_INPUT_ONLY_SUFFIX):
        reverse_inputs = True
        formula_name = formula_name[: -len(PHASE0_SYMBOL_NUMERIC_REVERSE_INPUT_ONLY_SUFFIX)]
    resolved_x_text = x_text[::-1] if reverse_inputs else x_text
    resolved_y_text = y_text[::-1] if reverse_inputs else y_text
    x_value = int(resolved_x_text)
    y_value = int(resolved_y_text)
    if formula_name == "concat_xy":
        output = resolved_x_text + resolved_y_text
    elif formula_name == "concat_yx":
        output = resolved_y_text + resolved_x_text
    elif formula_name == "x_plus_y":
        output = format_phase0_symbol_numeric_value(operator, x_value + y_value, format_name)
    elif formula_name == "x_plus_y_plus1":
        output = format_phase0_symbol_numeric_value(operator, x_value + y_value + 1, format_name)
    elif formula_name == "x_plus_y_minus1":
        output = format_phase0_symbol_numeric_value(operator, x_value + y_value - 1, format_name)
    elif formula_name == "x_mul_y":
        output = format_phase0_symbol_numeric_value(operator, x_value * y_value, format_name)
    elif formula_name == "x_mul_y_plus1":
        output = format_phase0_symbol_numeric_value(operator, x_value * y_value + 1, format_name)
    elif formula_name == "x_mul_y_minus1":
        output = format_phase0_symbol_numeric_value(operator, x_value * y_value - 1, format_name)
    elif formula_name == "x_minus_y":
        output = format_phase0_symbol_numeric_value(operator, x_value - y_value, format_name)
    elif formula_name == "y_minus_x":
        output = format_phase0_symbol_numeric_value(operator, y_value - x_value, format_name)
    elif formula_name in {"abs_diff", "abs_diff_2d"}:
        output = format_phase0_symbol_numeric_value(operator, abs(x_value - y_value), format_name)
    elif formula_name == "max_mod_min":
        output = format_phase0_symbol_numeric_value(operator, max(x_value, y_value) % min(x_value, y_value), format_name)
    elif formula_name == "x_mod_y":
        output = format_phase0_symbol_numeric_value(operator, x_value % y_value, format_name)
    elif formula_name == "y_mod_x":
        output = format_phase0_symbol_numeric_value(operator, y_value % x_value, format_name)
    elif formula_name == "abs_diff_2d_op_suffix":
        output = f"{operator}{abs(x_value - y_value)}"
    else:
        raise ValueError(f"Unsupported numeric symbol formula: {formula_name}")
    if reverse_output:
        if formula_name == "abs_diff_2d_op_suffix":
            return f"{operator}{output[len(operator):][::-1]}"
        if output.startswith(operator):
            return f"{operator}{output[len(operator):][::-1]}"
        return output[::-1]
    return output


def apply_phase0_symbol_numeric_subfamily(
    operator: str,
    subfamily_name: str,
    same_operator_examples: Sequence[tuple[str, str, str]],
    query_x_text: str,
    query_y_text: str,
) -> str | None:
    query_x_value = int(query_x_text)
    query_y_value = int(query_y_text)
    query_x_tens, query_x_ones = int(query_x_text[0]), int(query_x_text[1])
    query_y_tens, query_y_ones = int(query_y_text[0]), int(query_y_text[1])
    if subfamily_name == "star_prefix_if_negative_same_bucket1":
        if len(same_operator_examples) != 1:
            return None
        example_x_text, example_y_text, example_answer = same_operator_examples[0]
        if (
            apply_phase0_symbol_numeric_formula_spec(
                operator,
                "x_minus_y",
                "prefix_if_negative",
                example_x_text,
                example_y_text,
            )
            != example_answer
        ):
            return None
        return apply_phase0_symbol_numeric_formula_spec(
            operator,
            "x_minus_y",
            "prefix_if_negative",
            query_x_text,
            query_y_text,
        )
    if subfamily_name in {"minus_prefix_reverse_no_borrow_zpad2", "minus_prefix_reverse_no_borrow_trim_zero"}:
        if any(
            apply_phase0_symbol_numeric_formula_spec(
                operator,
                "abs_diff_2d_op_suffix__rev_in1_rev_out1",
                "string_template",
                example_x_text,
                example_y_text,
            )
            != example_answer
            for example_x_text, example_y_text, example_answer in same_operator_examples
        ):
            return None
        if not (query_x_tens <= query_y_tens and query_x_ones < query_y_ones):
            return None
        raw_prediction = apply_phase0_symbol_numeric_formula_spec(
            operator,
            "abs_diff_2d_op_suffix__rev_in1_rev_out1",
            "string_template",
            query_x_text,
            query_y_text,
        )
        digits = raw_prediction[len(operator) :]
        if subfamily_name.endswith("zpad2"):
            digits = digits.zfill(2)
        else:
            digits = digits.lstrip("0") or "0"
        return f"{operator}{digits}"
    if subfamily_name == "minus_signed_plain_both_lt":
        if any(
            apply_phase0_symbol_numeric_formula_spec(operator, "x_minus_y", "plain", example_x_text, example_y_text)
            != example_answer
            for example_x_text, example_y_text, example_answer in same_operator_examples
        ):
            return None
        if query_x_tens < query_y_tens and query_x_ones < query_y_ones:
            return str(query_x_value - query_y_value)
        return None
    if subfamily_name == "minus_signed_plain_both_gt":
        if any(
            apply_phase0_symbol_numeric_formula_spec(operator, "x_minus_y", "plain", example_x_text, example_y_text)
            != example_answer
            for example_x_text, example_y_text, example_answer in same_operator_examples
        ):
            return None
        if query_x_tens > query_y_tens and query_x_ones > query_y_ones:
            return str(query_x_value - query_y_value)
        return None
    if subfamily_name == "minus_abs_plain_both_gt":
        if any(
            apply_phase0_symbol_numeric_formula_spec(operator, "abs_diff", "plain", example_x_text, example_y_text)
            != example_answer
            for example_x_text, example_y_text, example_answer in same_operator_examples
        ):
            return None
        if query_x_tens > query_y_tens and query_x_ones > query_y_ones:
            return str(abs(query_x_value - query_y_value))
        return None
    if subfamily_name == "exclamation_abs_diff_2d_both_lt":
        if any(
            apply_phase0_symbol_numeric_formula_spec(operator, "abs_diff_2d", "plain", example_x_text, example_y_text)
            != example_answer
            for example_x_text, example_y_text, example_answer in same_operator_examples
        ):
            return None
        if query_x_tens < query_y_tens and query_x_ones < query_y_ones:
            return str(abs(query_x_value - query_y_value))
        return None
    if subfamily_name == "quote_prefix_if_negative_large_positive":
        if any(
            apply_phase0_symbol_numeric_formula_spec(
                operator,
                "x_minus_y",
                "prefix_if_negative",
                example_x_text,
                example_y_text,
            )
            != example_answer
            for example_x_text, example_y_text, example_answer in same_operator_examples
        ):
            return None
        if query_x_value > query_y_value and abs(query_x_value - query_y_value) >= 40:
            return str(query_x_value - query_y_value)
        return None
    return None


def collect_phase0_symbol_numeric_safe_predictions(prompt: str) -> list[str]:
    examples, (query_x_text, operator, query_y_text) = parse_phase0_symbol_numeric_prompt(prompt)
    same_operator_examples = [
        (example_x_text, example_y_text, example_answer)
        for example_x_text, example_operator, example_y_text, example_answer in examples
        if example_operator == operator
    ]
    if not same_operator_examples:
        return []
    predictions: set[str] = set()
    for spec_kind, spec_name, format_name in load_phase0_symbol_numeric_safe_specs().get(operator, ()):
        if spec_kind == "formula":
            try:
                if all(
                    apply_phase0_symbol_numeric_formula_spec(
                        operator,
                        spec_name,
                        format_name,
                        example_x_text,
                        example_y_text,
                    )
                    == example_answer
                    for example_x_text, example_y_text, example_answer in same_operator_examples
                ):
                    predictions.add(
                        apply_phase0_symbol_numeric_formula_spec(
                            operator,
                            spec_name,
                            format_name,
                            query_x_text,
                            query_y_text,
                        )
                    )
            except (ValueError, ZeroDivisionError):
                continue
            continue
        predicted_answer = apply_phase0_symbol_numeric_subfamily(
            operator,
            spec_name,
            same_operator_examples,
            query_x_text,
            query_y_text,
        )
        if predicted_answer is not None:
            predictions.add(predicted_answer)
    return sorted(predictions)


def collect_phase0_symbol_numeric_zero_error_predictions(prompt: str) -> list[str]:
    examples, (query_x_text, operator, query_y_text) = parse_phase0_symbol_numeric_prompt(prompt)
    same_operator_examples = [
        (example_x_text, example_y_text, example_answer)
        for example_x_text, example_operator, example_y_text, example_answer in examples
        if example_operator == operator
    ]
    if not same_operator_examples:
        return []
    predictions: set[str] = set()
    for formula_name, format_name in load_phase0_symbol_numeric_zero_error_formula_specs().get(operator, ()):
        try:
            if all(
                apply_phase0_symbol_numeric_formula_spec(
                    operator,
                    formula_name,
                    format_name,
                    example_x_text,
                    example_y_text,
                )
                == example_answer
                for example_x_text, example_y_text, example_answer in same_operator_examples
            ):
                predictions.add(
                    apply_phase0_symbol_numeric_formula_spec(
                        operator,
                        formula_name,
                        format_name,
                        query_x_text,
                        query_y_text,
                    )
                )
        except (ValueError, ZeroDivisionError):
            continue
    for spec_kind, spec_name, _ in load_phase0_symbol_numeric_safe_specs().get(operator, ()):
        if spec_kind != "subfamily":
            continue
        predicted_answer = apply_phase0_symbol_numeric_subfamily(
            operator,
            spec_name,
            same_operator_examples,
            query_x_text,
            query_y_text,
        )
        if predicted_answer is not None:
            predictions.add(predicted_answer)
    return sorted(predictions)


def maybe_solve_phase0_symbol_numeric_prompt(prompt: str) -> str | None:
    predictions = collect_phase0_symbol_numeric_safe_predictions(prompt)
    if len(predictions) == 1:
        return predictions[0]
    return None


def maybe_solve_phase0_symbol_numeric_zero_error_prompt(prompt: str) -> str | None:
    predictions = collect_phase0_symbol_numeric_zero_error_predictions(prompt)
    if len(predictions) == 1:
        return predictions[0]
    return None


def solve_phase0_binary_prompt(row: dict[str, Any]) -> str:
    solver_mode = str(row.get("router_solver_mode", "")).strip()
    if solver_mode not in {"", "binary_formula_consensus"}:
        raise ValueError(f"Unsupported binary solver mode: {solver_mode}")
    predicted_answer = maybe_solve_phase0_binary_formula_prompt(str(row.get("prompt", "")))
    if predicted_answer is None:
        raise ValueError(f"Unable to derive a unique binary formula consensus prediction for id={row.get('id')}")
    return predicted_answer


def solve_phase0_symbol_prompt(row: dict[str, Any]) -> str:
    if str(row.get("template_subtype", "")).strip() != "numeric_2x2":
        raise ValueError(f"Unsupported symbol solver subtype: {row.get('template_subtype')}")
    solver_mode = str(row.get("router_solver_mode", "")).strip()
    if solver_mode == "symbol_numeric_zero_error":
        predicted_answer = maybe_solve_phase0_symbol_numeric_zero_error_prompt(str(row.get("prompt", "")))
    else:
        predicted_answer = maybe_solve_phase0_symbol_numeric_prompt(str(row.get("prompt", "")))
    if predicted_answer is None:
        raise ValueError(f"Unable to derive a unique safe numeric symbol prediction for id={row.get('id')}")
    return predicted_answer


def solve_phase0_gravity_prompt(prompt: str) -> str:
    inferred_g: list[float] = []
    query_time: float | None = None
    for line in parse_phase0_prompt_lines(prompt):
        if line.startswith("For t = "):
            values = NUMBER_PATTERN.findall(line)
            if len(values) < 2:
                raise ValueError(f"Unable to parse gravity example line: {line}")
            time_value = float(values[0])
            distance_value = float(values[1])
            inferred_g.append((2.0 * distance_value) / (time_value * time_value))
        elif line.startswith("Now, determine the falling distance"):
            values = NUMBER_PATTERN.findall(line)
            if not values:
                raise ValueError(f"Unable to parse gravity query line: {line}")
            query_time = float(values[0])
    if not inferred_g or query_time is None:
        raise ValueError("Gravity prompt is missing examples or query time.")
    return format_phase0_solver_numeric(0.5 * (sum(inferred_g) / len(inferred_g)) * query_time * query_time)


def solve_phase0_unit_prompt(prompt: str) -> str:
    inferred_ratios: list[float] = []
    query_value: float | None = None
    for line in parse_phase0_prompt_lines(prompt):
        if "becomes" in line:
            values = NUMBER_PATTERN.findall(line)
            if len(values) < 2:
                raise ValueError(f"Unable to parse unit example line: {line}")
            source_value = float(values[0])
            target_value = float(values[1])
            inferred_ratios.append(target_value / source_value)
        elif line.startswith("Now, convert the following measurement:"):
            values = NUMBER_PATTERN.findall(line)
            if not values:
                raise ValueError(f"Unable to parse unit query line: {line}")
            query_value = float(values[0])
    if not inferred_ratios or query_value is None:
        raise ValueError("Unit prompt is missing examples or query value.")
    return format_phase0_solver_numeric(query_value * (sum(inferred_ratios) / len(inferred_ratios)))


def int_to_phase0_roman(value: int) -> str:
    numerals = (
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    )
    remaining = int(value)
    output: list[str] = []
    for numeral_value, symbol in numerals:
        while remaining >= numeral_value:
            output.append(symbol)
            remaining -= numeral_value
    return "".join(output)


def solve_phase0_roman_prompt(prompt: str) -> str:
    lines = parse_phase0_prompt_lines(prompt)
    query_value: int | None = None
    for line in lines:
        if "->" in line:
            left, right = [part.strip() for part in line.split("->", 1)]
            if not left.isdigit():
                raise ValueError(f"Unable to parse roman example line: {line}")
            expected = int_to_phase0_roman(int(left))
            if expected != right:
                raise ValueError(f"Roman example does not match standard roman mapping: {line}")
        elif line.startswith("Now, write the number "):
            values = NUMBER_PATTERN.findall(line)
            if not values:
                raise ValueError(f"Unable to parse roman query line: {line}")
            query_value = int(float(values[0]))
    if query_value is None:
        raise ValueError("Roman prompt is missing query value.")
    return int_to_phase0_roman(query_value)


def solve_phase0_text_prompt(prompt: str) -> str:
    mapping: dict[str, str] = {}
    query_text: str | None = None
    for line in [line.rstrip() for line in str(prompt).splitlines() if line.strip()]:
        if " -> " in line:
            encrypted_text, decrypted_text = line.split(" -> ", 1)
            if len(encrypted_text) != len(decrypted_text):
                raise ValueError(f"Text example length mismatch: {line}")
            for encrypted_char, decrypted_char in zip(encrypted_text, decrypted_text):
                if encrypted_char == " ":
                    continue
                previous = mapping.get(encrypted_char)
                if previous is not None and previous != decrypted_char:
                    raise ValueError(f"Inconsistent text substitution mapping for char={encrypted_char!r}")
                mapping[encrypted_char] = decrypted_char
        elif line.startswith("Now, decrypt the following text: "):
            query_text = line.split(": ", 1)[1]
    if query_text is None:
        raise ValueError("Text prompt is missing query text.")
    decoded: list[str] = []
    for char in query_text:
        if char == " ":
            decoded.append(" ")
            continue
        if char not in mapping:
            raise ValueError(f"Missing text substitution mapping for char={char!r}")
        decoded.append(mapping[char])
    return "".join(decoded)


def solve_phase0_router_prompt(row: dict[str, Any]) -> str:
    family_short = str(row.get("family_short", "")).strip()
    prompt_text = str(row.get("prompt", ""))
    if family_short == "binary":
        return solve_phase0_binary_prompt(row)
    if family_short == "gravity":
        return solve_phase0_gravity_prompt(prompt_text)
    if family_short == "symbol":
        return solve_phase0_symbol_prompt(row)
    if family_short == "unit":
        return solve_phase0_unit_prompt(prompt_text)
    if family_short == "roman":
        return solve_phase0_roman_prompt(prompt_text)
    if family_short == "text":
        return solve_phase0_text_prompt(prompt_text)
    raise ValueError(f"Unsupported solver family: {family_short}")


def generate_phase0_solver_records(*, benchmark_rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in benchmark_rows:
        predicted_answer = solve_phase0_router_prompt(row)
        records.append(
            {
                "benchmark_name": row["benchmark_name"],
                "benchmark_role": row["benchmark_role"],
                "benchmark_index": row["benchmark_index"],
                "family": row["family"],
                "family_short": row["family_short"],
                "template_subtype": row["template_subtype"],
                "selection_tier": row["selection_tier"],
                "teacher_solver_candidate": row["teacher_solver_candidate"],
                "answer_type": row["answer_type"],
                "num_examples": row["num_examples"],
                "prompt_len_chars": row["prompt_len_chars"],
                "id": row["id"],
                "expected_answer": row["answer"],
                "rendered_prompt": row["prompt"],
                "raw_output": f"\\\\boxed{{{predicted_answer}}}",
                "extracted_answer": predicted_answer,
            }
        )
    return records


def generate_phase0_records_batched(
    *,
    benchmark_rows: Sequence[dict[str, Any]],
    model_path: Path,
    adapter_dir: Path | None,
    max_tokens: int,
    top_p: float,
    temperature: float,
    max_num_seqs: int,
    prompt_chunk_size: int,
    prefill_batch_size: int,
    completion_batch_size: int,
    lazy_load: bool,
    progress_every: int,
    worker_label: str,
    eval_thinking: str,
) -> list[dict[str, Any]]:
    import mlx.core as mx  # type: ignore
    from mlx_lm import batch_generate, generate, load  # type: ignore
    from mlx_lm.sample_utils import make_sampler  # type: ignore

    maybe_patch_batch_generator_stats(mx)
    maybe_patch_mamba_cache_extract()
    load_kwargs: dict[str, Any] = {"lazy": lazy_load}
    if adapter_dir is not None:
        load_kwargs["adapter_path"] = str(adapter_dir)
    model, tokenizer = load(str(model_path), **load_kwargs)
    maybe_fix_tokenizer_eos_ids(tokenizer)
    eval_thinking_value = str(eval_thinking).strip().lower()
    if eval_thinking_value not in {"auto", "on", "off"}:
        raise ValueError(f"Unsupported eval_thinking: {eval_thinking_value}")
    prompt_enable_thinking = eval_thinking_value != "off"
    prompts = build_prompts(
        tokenizer,
        [str(row["prompt"]) for row in benchmark_rows],
        enable_thinking=prompt_enable_thinking,
    )
    prompt_tokens = [encode_prompt(tokenizer, prompt) for prompt in prompts]
    sampler = make_sampler(
        temp=float(temperature),
        top_p=float(top_p) if 0.0 < float(top_p) < 1.0 else 0.0,
    )

    chunk_size = clamp_eval_batch_size(
        prompt_chunk_size,
        default=max_num_seqs,
        max_num_seqs=max_num_seqs,
    )
    prefill_size = clamp_eval_batch_size(
        prefill_batch_size,
        default=min(max_num_seqs, 32),
        max_num_seqs=max_num_seqs,
    )
    completion_size = clamp_eval_batch_size(
        completion_batch_size,
        default=min(max_num_seqs, 32),
        max_num_seqs=max_num_seqs,
    )

    records: list[dict[str, Any]] = []
    total_prompts = len(prompt_tokens)
    total_chunks = max(1, math.ceil(total_prompts / chunk_size))
    run_started_at = time.perf_counter()
    heartbeat_sec = 60.0

    for chunk_start in range(0, total_prompts, chunk_size):
        chunk_prompts = prompt_tokens[chunk_start : chunk_start + chunk_size]
        chunk_rows = benchmark_rows[chunk_start : chunk_start + len(chunk_prompts)]
        chunk_rendered_prompts = prompts[chunk_start : chunk_start + len(chunk_prompts)]
        chunk_index = (chunk_start // chunk_size) + 1
        chunk_end = chunk_start + len(chunk_prompts)
        chunk_started_at = time.perf_counter()
        print(
            f"[phase0-eval:{worker_label}] "
            f"chunk={chunk_index}/{total_chunks} prompts={chunk_start + 1}-{chunk_end}/{total_prompts} status=started",
            flush=True,
        )

        heartbeat_stop = threading.Event()
        heartbeat_thread: threading.Thread | None = None
        if heartbeat_sec > 0:
            def emit_heartbeat() -> None:
                while not heartbeat_stop.wait(heartbeat_sec):
                    chunk_elapsed = time.perf_counter() - chunk_started_at
                    total_elapsed = time.perf_counter() - run_started_at
                    print(
                        f"[phase0-eval:{worker_label}] "
                        f"chunk={chunk_index}/{total_chunks} status=running "
                        f"chunk_elapsed_sec={chunk_elapsed:.1f} total_elapsed_sec={total_elapsed:.1f}",
                        flush=True,
                    )

            heartbeat_thread = threading.Thread(target=emit_heartbeat, daemon=True)
            heartbeat_thread.start()

        try:
            try:
                batch_response = batch_generate(
                    model,
                    tokenizer,
                    chunk_prompts,
                    max_tokens=max_tokens,
                    sampler=sampler,
                    verbose=False,
                    prefill_batch_size=min(prefill_size, len(chunk_prompts)),
                    completion_batch_size=min(completion_size, len(chunk_prompts)),
                )
                chunk_outputs = list(batch_response.texts)
            except AttributeError as exc:
                error_text = f"{type(exc).__name__}: {exc}"
                if "MambaCache" not in error_text or "extract" not in error_text:
                    raise
                print(
                    f"[phase0-eval:{worker_label}] "
                    f"chunk={chunk_index}/{total_chunks} status=batch_generate_fallback "
                    f"reason={error_text}",
                    flush=True,
                )
                chunk_outputs = [
                    generate(
                        model,
                        tokenizer,
                        prompt=prompt_tokens_single,
                        verbose=False,
                        max_tokens=max_tokens,
                        sampler=sampler,
                    )
                    for prompt_tokens_single in chunk_prompts
                ]
                batch_response = None
        finally:
            if heartbeat_thread is not None:
                heartbeat_stop.set()
                heartbeat_thread.join()

        for row, rendered_prompt, raw_output in zip(
            chunk_rows,
            chunk_rendered_prompts,
            chunk_outputs,
        ):
            records.append(
                {
                    "benchmark_name": row["benchmark_name"],
                    "benchmark_role": row["benchmark_role"],
                    "benchmark_index": row["benchmark_index"],
                    "family": row["family"],
                    "family_short": row["family_short"],
                    "template_subtype": row["template_subtype"],
                    "selection_tier": row["selection_tier"],
                    "teacher_solver_candidate": row["teacher_solver_candidate"],
                    "answer_type": row["answer_type"],
                    "num_examples": row["num_examples"],
                    "prompt_len_chars": row["prompt_len_chars"],
                    "id": row["id"],
                    "expected_answer": row["answer"],
                    "rendered_prompt": rendered_prompt,
                    "raw_output": raw_output,
                    "extracted_answer": extract_final_answer(raw_output),
                }
            )

        chunk_elapsed = time.perf_counter() - chunk_started_at
        total_elapsed = time.perf_counter() - run_started_at
        stats = getattr(batch_response, "stats", None) if batch_response is not None else None
        stats_suffix = ""
        if stats is not None:
            stats_suffix = (
                f" prompt_tps={getattr(stats, 'prompt_tps', 0.0):.2f}"
                f" generation_tps={getattr(stats, 'generation_tps', 0.0):.2f}"
                f" peak_memory_gb={getattr(stats, 'peak_memory', 0.0):.2f}"
            )
        print(
            f"[phase0-eval:{worker_label}] "
            f"chunk={chunk_index}/{total_chunks} prompts={chunk_start + 1}-{chunk_end}/{total_prompts} "
            f"status=completed chunk_elapsed_sec={chunk_elapsed:.1f} total_elapsed_sec={total_elapsed:.1f}"
            f"{stats_suffix}",
            flush=True,
        )
        if progress_every > 0 and (
            chunk_end == total_prompts
            or chunk_end % progress_every == 0
        ):
            print(
                f"[phase0-eval:{worker_label}] completed {chunk_end}/{total_prompts} rows",
                flush=True,
            )
        mx.clear_cache()

    return records


def score_phase0_records(
    *,
    records: Sequence[dict[str, Any]],
    holdout_rows: Sequence[dict[str, Any]],
    manifest: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scored_rows: list[dict[str, Any]] = []
    for row in records:
        derived = analyze_raw_output(str(row["raw_output"]))
        prediction = derived["extracted_answer"]
        scored_rows.append(
            {
                "benchmark_name": row["benchmark_name"],
                "benchmark_role": row["benchmark_role"],
                "benchmark_index": row["benchmark_index"],
                "id": row["id"],
                "gold_answer": row["expected_answer"],
                "prediction": prediction,
                "is_correct": verify_answer(str(row["expected_answer"]), str(prediction)),
                "family": row["family"],
                "family_short": row["family_short"],
                "template_subtype": row["template_subtype"],
                "answer_type": row["answer_type"],
                "teacher_solver_candidate": row["teacher_solver_candidate"],
                "selection_tier": row["selection_tier"],
                "num_examples": row["num_examples"],
                "prompt_len_chars": row["prompt_len_chars"],
                "prompt_len_bucket": prompt_len_bucket(parse_int(row["prompt_len_chars"], 0)),
                "fallback_type": derived["fallback_type"],
                "format_bucket": derived["format_bucket"],
                "has_boxed": derived["has_boxed"],
                "boxed_count": derived["boxed_count"],
                "raw_output": row["raw_output"],
            }
        )

    overall_summary = summarize_scored_rows(scored_rows)
    by_benchmark_summary = {
        benchmark_name: summarize_scored_rows(
            [row for row in scored_rows if row["benchmark_name"] == benchmark_name]
        )
        for benchmark_name in ("general_stable_set", "binary_hard_set", "symbol_watch_set")
    }
    binary_holdout_accuracy = build_binary_holdout_accuracy_rows(scored_rows, holdout_rows)
    summary_payload = {
        "manifest": manifest,
        "overall": overall_summary,
        "by_benchmark": by_benchmark_summary,
        "binary_holdout_accuracy": binary_holdout_accuracy,
    }
    return scored_rows, summary_payload


def write_phase0_eval_outputs(
    *,
    artifact_root: Path,
    report_root: Path,
    records: Sequence[dict[str, Any]],
    scored_rows: Sequence[dict[str, Any]],
    summary_payload: dict[str, Any],
) -> None:
    write_csv_rows(
        artifact_root / "phase0_eval_raw_outputs.csv",
        records,
        [
            "benchmark_name",
            "benchmark_role",
            "benchmark_index",
            "family",
            "family_short",
            "template_subtype",
            "selection_tier",
            "teacher_solver_candidate",
            "answer_type",
            "num_examples",
            "prompt_len_chars",
            "id",
            "expected_answer",
            "rendered_prompt",
            "raw_output",
            "extracted_answer",
        ],
    )
    write_csv_rows(
        artifact_root / "phase0_eval_row_level.csv",
        scored_rows,
        [
            "benchmark_name",
            "benchmark_role",
            "benchmark_index",
            "id",
            "gold_answer",
            "prediction",
            "is_correct",
            "family",
            "family_short",
            "template_subtype",
            "answer_type",
            "teacher_solver_candidate",
            "selection_tier",
            "num_examples",
            "prompt_len_chars",
            "prompt_len_bucket",
            "fallback_type",
            "format_bucket",
            "has_boxed",
            "boxed_count",
            "raw_output",
        ],
    )
    write_json(artifact_root / "phase0_eval_summary.json", summary_payload)
    write_text(
        report_root / "phase0_eval_summary.md",
        render_markdown_summary("phase0_eval_overall", summary_payload["overall"]),
    )
    binary_holdout_accuracy = summary_payload["binary_holdout_accuracy"]
    if binary_holdout_accuracy:
        write_csv_rows(
            artifact_root / "phase0_binary_holdout_accuracy.csv",
            binary_holdout_accuracy,
            ["holdout_kind", "fold", "rows", "correct", "accuracy"],
        )
    for benchmark_name, payload in summary_payload["by_benchmark"].items():
        write_json(artifact_root / f"{benchmark_name}_summary.json", payload)
        write_text(report_root / f"{benchmark_name}_summary.md", render_markdown_summary(benchmark_name, payload))


def run_phase0_eval_parallel(
    *,
    benchmark_rows: Sequence[dict[str, Any]],
    model_path: Path,
    adapter_dir: Path | None,
    eval_root: Path,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    num_shards = resolve_phase0_eval_num_shards(
        requested_shards=int(args.num_shards),
        total_rows=len(benchmark_rows),
        memory_budget_gb=float(args.memory_budget_gb),
        estimated_worker_memory_gb=float(args.estimated_worker_memory_gb),
    )
    if num_shards <= 1:
        return generate_phase0_records_batched(
            benchmark_rows=benchmark_rows,
            model_path=model_path,
            adapter_dir=adapter_dir,
            max_tokens=int(args.max_tokens),
            top_p=float(args.top_p),
            temperature=float(args.temperature),
            max_num_seqs=int(args.max_num_seqs),
            prompt_chunk_size=int(args.prompt_chunk_size),
            prefill_batch_size=int(args.prefill_batch_size),
            completion_batch_size=int(args.completion_batch_size),
            lazy_load=bool(args.lazy_load),
            progress_every=int(args.progress_every),
            worker_label="main",
            eval_thinking=str(getattr(args, "eval_thinking", "auto")),
        )

    shard_root = eval_root / "_parallel"
    ensure_dir(shard_root)
    shard_rows = [
        list(benchmark_rows[shard_index::num_shards])
        for shard_index in range(num_shards)
    ]
    launched_processes: list[tuple[int, Path, Path, subprocess.Popen[Any], Any]] = []

    print(
        f"[phase0-eval] launching {num_shards} shard workers "
        f"(memory_budget_gb={float(args.memory_budget_gb):.1f}, "
        f"estimated_worker_memory_gb={float(args.estimated_worker_memory_gb):.1f})",
        flush=True,
    )

    try:
        for shard_index, rows in enumerate(shard_rows):
            shard_input_path = shard_root / f"shard_{shard_index:02d}.jsonl"
            shard_output_path = shard_root / f"shard_{shard_index:02d}_records.jsonl"
            shard_log_path = shard_root / f"shard_{shard_index:02d}.log"
            write_jsonl_records(shard_input_path, rows)
            command = [
                sys.executable,
                str(Path(__file__).resolve()),
                "eval-phase0-worker",
                "--model-path",
                str(model_path),
                "--input-jsonl",
                str(shard_input_path),
                "--output-jsonl",
                str(shard_output_path),
                "--max-tokens",
                str(int(args.max_tokens)),
                "--temperature",
                str(float(args.temperature)),
                "--top-p",
                str(float(args.top_p)),
                "--max-num-seqs",
                str(int(args.max_num_seqs)),
                "--prompt-chunk-size",
                str(int(args.prompt_chunk_size)),
                "--prefill-batch-size",
                str(int(args.prefill_batch_size)),
                "--completion-batch-size",
                str(int(args.completion_batch_size)),
                "--progress-every",
                str(int(args.progress_every)),
                "--worker-label",
                f"shard{shard_index + 1}of{num_shards}",
                "--eval-thinking",
                str(getattr(args, "eval_thinking", "auto")),
            ]
            if adapter_dir is not None:
                command.extend(["--adapter-path", str(adapter_dir)])
            if args.lazy_load:
                command.append("--lazy-load")
            log_handle = shard_log_path.open("w", encoding="utf-8")
            process = subprocess.Popen(
                command,
                cwd=str(REPO_ROOT),
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
                stdout=log_handle,
                stderr=subprocess.STDOUT,
            )
            launched_processes.append(
                (shard_index, shard_output_path, shard_log_path, process, log_handle)
            )
            print(
                f"[phase0-eval] launched shard={shard_index + 1}/{num_shards} "
                f"rows={len(rows)} log={shard_log_path}",
                flush=True,
            )

        for shard_index, shard_output_path, shard_log_path, process, log_handle in launched_processes:
            return_code = process.wait()
            log_handle.close()
            if return_code != 0:
                raise RuntimeError(
                    f"phase0 worker failed: shard={shard_index + 1}/{num_shards} "
                    f"return_code={return_code} log={shard_log_path}\n{tail_text(shard_log_path)}"
                )
            if not shard_output_path.exists():
                raise FileNotFoundError(
                    f"phase0 worker did not produce output: shard={shard_index + 1}/{num_shards} "
                    f"path={shard_output_path}"
                )
            print(
                f"[phase0-eval] completed shard={shard_index + 1}/{num_shards} log={shard_log_path}",
                flush=True,
            )
    finally:
        for _, _, _, process, log_handle in launched_processes:
            if not log_handle.closed:
                log_handle.close()
            if process.poll() is None:
                process.kill()
                process.wait()

    records: list[dict[str, Any]] = []
    for _, shard_output_path, _, _, _ in launched_processes:
        records.extend(load_jsonl_records(shard_output_path))
    records.sort(
        key=lambda row: (
            str(row.get("benchmark_name", "")),
            int(row.get("benchmark_index", 0)),
            str(row.get("id", "")),
        )
    )
    return records


def run_prepare_train(args: argparse.Namespace) -> None:
    manifest = prepare_training_run(args)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def run_mlx_lora_training_from_config(config_path: Path) -> None:
    import mlx_lm.lora as mlx_lora

    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    maybe_patch_mlx_chat_dataset_enable_thinking()
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.load(handle, Loader=mlx_lora.yaml_loader) or {}
    for key, value in mlx_lora.CONFIG_DEFAULTS.items():
        config.setdefault(key, value)
    mlx_lora.run(argparse.Namespace(**config))


def load_existing_prepare_manifest(run_root: Path) -> dict[str, Any] | None:
    manifest_path = run_root / "prepare_manifest.json"
    if not manifest_path.exists():
        return None
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_train(args: argparse.Namespace) -> None:
    run_root = Path(args.output_root).resolve() / str(args.run_name)
    manifest = load_existing_prepare_manifest(run_root)
    if manifest is not None:
        config_path = Path(manifest["artifacts"]["config_path"]).resolve()
        adapter_dir = Path(manifest["artifacts"]["adapter_dir"]).resolve()
        if not config_path.exists():
            manifest = None
        else:
            print(f"Using existing prepared training artifacts from {run_root}")
            print("To change train settings for this run name, rerun prepare-train first.")
    if manifest is None:
        manifest = prepare_training_run(args)
        run_root = Path(manifest["run_root"])
        adapter_dir = Path(manifest["artifacts"]["adapter_dir"])
        config_path = Path(manifest["artifacts"]["config_path"])
    command = [sys.executable, str(Path(__file__).resolve()), "train-mlx-config", "--config", str(config_path)]
    print("Running MLX LoRA training:")
    print(" ".join(command))
    run_mlx_lora_training_from_config(config_path)
    verify_training_outputs(adapter_dir)
    training_result = {
        "created_at": utc_now(),
        "run_root": str(run_root),
        "adapter_dir": str(adapter_dir),
        "adapter_files": summarize_directory(adapter_dir),
    }
    write_json(run_root / "training_result.json", training_result)
    print(json.dumps(training_result, ensure_ascii=False, indent=2))


def run_train_mlx_config(args: argparse.Namespace) -> None:
    run_mlx_lora_training_from_config(Path(args.config).resolve())


def run_phase0_eval(args: argparse.Namespace) -> None:
    adapter_dir = None
    if args.adapter_path is not None:
        adapter_dir = Path(args.adapter_path).resolve()
        if not adapter_dir.exists():
            raise FileNotFoundError(f"Adapter directory does not exist: {adapter_dir}")
        verify_training_outputs(adapter_dir)

    separate_eval_output_root = None
    if getattr(args, "eval_output_root", None):
        separate_eval_output_root = Path(args.eval_output_root).resolve()

    if adapter_dir is not None:
        shadow_run_root = adapter_dir.parent
        if separate_eval_output_root is None:
            run_root = shadow_run_root
        else:
            run_root = separate_eval_output_root / str(args.eval_name)
            ensure_dir(run_root)
    else:
        run_root = Path(args.output_root).resolve() / str(args.eval_name)
        ensure_dir(run_root)
        shadow_run_root = run_root
    shadow_model_dir = build_shadow_model_dir(
        Path(args.model_root),
        shadow_run_root / "shadow_model",
        force=bool(args.force_shadow_model),
    )

    eval_root = run_root / "phase0_offline_eval"
    artifact_root = eval_root / "artifacts"
    report_root = eval_root / "reports"
    benchmark_rows, holdout_rows, manifest = prepare_phase0_benchmark_artifacts(
        prebuilt_root=Path(args.phase0_prebuilt_root),
        analysis_csv=Path(args.phase0_analysis_csv),
        artifact_root=artifact_root,
        report_root=report_root,
        rebuild=bool(args.rebuild_phase0),
    )
    benchmark_rows = filter_phase0_benchmark_rows(
        benchmark_rows,
        family_short_filter=str(getattr(args, "family_short_filter", "")),
        per_family_limit=int(getattr(args, "per_family_limit", 0)),
    )
    if args.max_samples is not None:
        benchmark_rows = benchmark_rows[: int(args.max_samples)]
    records = run_phase0_eval_parallel(
        benchmark_rows=benchmark_rows,
        model_path=shadow_model_dir,
        adapter_dir=adapter_dir,
        eval_root=eval_root,
        args=args,
    )
    scored_rows, summary_payload = score_phase0_records(
        records=records,
        holdout_rows=holdout_rows,
        manifest=manifest,
    )
    write_phase0_eval_outputs(
        artifact_root=artifact_root,
        report_root=report_root,
        records=records,
        scored_rows=scored_rows,
        summary_payload=summary_payload,
    )
    print(json.dumps(summary_payload["overall"], ensure_ascii=False, indent=2))


def run_phase0_eval_router(args: argparse.Namespace) -> None:
    slot_adapter_dirs = {
        "general": Path(args.general_adapter_path).resolve(),
        "reasoning": Path(args.reasoning_adapter_path).resolve(),
        "specialist": Path(args.specialist_adapter_path).resolve(),
        "solver": None,
    }
    for slot, adapter_dir in slot_adapter_dirs.items():
        if adapter_dir is None:
            continue
        if not adapter_dir.exists():
            raise FileNotFoundError(f"Router adapter directory does not exist for slot={slot}: {adapter_dir}")
        verify_training_outputs(adapter_dir)

    if getattr(args, "eval_output_root", None):
        run_root = Path(args.eval_output_root).resolve() / str(args.eval_name)
    else:
        run_root = Path(args.output_root).resolve() / str(args.eval_name)
    ensure_dir(run_root)

    shadow_model_dir = build_shadow_model_dir(
        Path(args.model_root),
        run_root / "shadow_model",
        force=bool(args.force_shadow_model),
    )

    eval_root = run_root / "phase0_offline_eval"
    artifact_root = eval_root / "artifacts"
    report_root = eval_root / "reports"
    benchmark_rows, holdout_rows, manifest = prepare_phase0_benchmark_artifacts(
        prebuilt_root=Path(args.phase0_prebuilt_root),
        analysis_csv=Path(args.phase0_analysis_csv),
        artifact_root=artifact_root,
        report_root=report_root,
        rebuild=bool(args.rebuild_phase0),
    )
    benchmark_rows = filter_phase0_benchmark_rows(
        benchmark_rows,
        family_short_filter=str(getattr(args, "family_short_filter", "")),
        per_family_limit=int(getattr(args, "per_family_limit", 0)),
    )
    if args.max_samples is not None:
        benchmark_rows = benchmark_rows[: int(args.max_samples)]

    slot_by_family = resolve_phase0_router_slot_map(str(args.router_profile))
    routed_rows_by_slot: dict[str, list[dict[str, Any]]] = defaultdict(list)
    benchmark_row_by_id: dict[str, dict[str, Any]] = {}
    router_assignments: list[dict[str, Any]] = []
    for row in benchmark_rows:
        prompt_text = str(row.get("prompt", ""))
        predicted_family = classify_phase0_prompt_family(prompt_text)
        expected_family = str(row.get("family_short", "")).strip()
        if expected_family and predicted_family != expected_family:
            raise ValueError(
                f"Prompt router family mismatch for id={row.get('id')}: "
                f"predicted={predicted_family} expected={expected_family}"
            )
        slot = slot_by_family[predicted_family]
        routed_row = dict(row)
        routed_row["router_family_pred"] = predicted_family
        routed_row["router_slot"] = slot
        benchmark_row_by_id[str(row["id"])] = routed_row
        routed_rows_by_slot[slot].append(routed_row)
        router_assignments.append(
            {
                "id": row["id"],
                "benchmark_name": row["benchmark_name"],
                "benchmark_index": row["benchmark_index"],
                "family_short": expected_family,
                "router_family": predicted_family,
                "router_slot": slot,
                "router_adapter_path": (
                    str(slot_adapter_dirs[slot].resolve())
                    if slot_adapter_dirs[slot] is not None
                    else ""
                ),
            }
        )

    records: list[dict[str, Any]] = []
    for slot in ("general", "reasoning", "specialist", "solver"):
        slot_rows = routed_rows_by_slot.get(slot, [])
        if not slot_rows:
            continue
        if slot == "solver":
            slot_records = generate_phase0_solver_records(benchmark_rows=slot_rows)
        else:
            slot_eval_root = eval_root / f"route_{slot}"
            ensure_dir(slot_eval_root)
            slot_records = run_phase0_eval_parallel(
                benchmark_rows=slot_rows,
                model_path=shadow_model_dir,
                adapter_dir=slot_adapter_dirs[slot],
                eval_root=slot_eval_root,
                args=args,
            )
        slot_meta = {str(row["id"]): row for row in slot_rows}
        for record in slot_records:
            meta = slot_meta.get(str(record.get("id", "")), {})
            record["router_slot"] = slot
            record["router_family_pred"] = str(meta.get("router_family_pred", ""))
        records.extend(slot_records)

    provisional_scored_rows, _ = score_phase0_records(
        records=records,
        holdout_rows=holdout_rows,
        manifest=manifest,
    )
    fallback_assignments: list[dict[str, Any]] = []
    fallback_rows_by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for scored_row in provisional_scored_rows:
        row_id = str(scored_row["id"])
        fallback_row = benchmark_row_by_id.get(row_id)
        if fallback_row is None:
            raise KeyError(f"Missing benchmark row for router fallback id={row_id}")
        resolved_fallback = resolve_phase0_router_fallback_target(
            router_profile=str(args.router_profile),
            scored_row=scored_row,
            benchmark_row=fallback_row,
        )
        if resolved_fallback is None:
            continue
        fallback_target, fallback_reason = resolved_fallback
        if fallback_reason == "symbol_numeric_zero_error_solver":
            fallback_row = dict(fallback_row)
            fallback_row["router_solver_mode"] = "symbol_numeric_zero_error"
        elif fallback_reason == "binary_formula_consensus_solver":
            fallback_row = dict(fallback_row)
            fallback_row["router_solver_mode"] = "binary_formula_consensus"
        fallback_rows_by_target[fallback_target].append(fallback_row)
        fallback_assignments.append(
            {
                "id": row_id,
                "family_short": scored_row["family_short"],
                "primary_slot": str(fallback_row.get("router_slot", "")),
                "fallback_target": fallback_target,
                "fallback_reason": fallback_reason,
                "primary_prediction": scored_row["prediction"],
                "primary_format_bucket": scored_row["format_bucket"],
                "primary_is_correct": scored_row["is_correct"],
            }
        )

    if fallback_rows_by_target:
        assignment_by_id = {str(row["id"]): row for row in fallback_assignments}
        record_by_id = {str(row["id"]): row for row in records}
        for fallback_target, fallback_rows in sorted(fallback_rows_by_target.items()):
            fallback_eval_root = eval_root / f"fallback_{fallback_target}"
            ensure_dir(fallback_eval_root)
            if fallback_target == "base":
                fallback_records = run_phase0_eval_parallel(
                    benchmark_rows=fallback_rows,
                    model_path=shadow_model_dir,
                    adapter_dir=None,
                    eval_root=fallback_eval_root,
                    args=args,
                )
            elif fallback_target == "solver":
                fallback_records = generate_phase0_solver_records(benchmark_rows=fallback_rows)
            else:
                raise ValueError(f"Unsupported router fallback target: {fallback_target}")
            fallback_scored_rows, _ = score_phase0_records(
                records=fallback_records,
                holdout_rows=holdout_rows,
                manifest=manifest,
            )
            fallback_scored_by_id = {str(row["id"]): row for row in fallback_scored_rows}
            for fallback_record in fallback_records:
                row_id = str(fallback_record["id"])
                meta = benchmark_row_by_id.get(row_id, {})
                fallback_record["router_slot"] = str(meta.get("router_slot", ""))
                fallback_record["router_family_pred"] = str(meta.get("router_family_pred", ""))
                fallback_record["router_fallback_target"] = fallback_target
                fallback_row = fallback_scored_by_id.get(row_id)
                if fallback_row is None:
                    raise KeyError(f"Missing scored fallback row for id={row_id}")
                assignment = assignment_by_id.get(row_id)
                if assignment is None:
                    raise KeyError(f"Missing fallback assignment for id={row_id}")
                assignment["fallback_prediction"] = fallback_row["prediction"]
                assignment["fallback_format_bucket"] = fallback_row["format_bucket"]
                assignment["fallback_is_correct"] = fallback_row["is_correct"]
                record_by_id[row_id] = fallback_record
        records = list(record_by_id.values())

    records.sort(
        key=lambda row: (
            str(row.get("benchmark_name", "")),
            int(row.get("benchmark_index", 0)),
            str(row.get("id", "")),
        )
    )
    scored_rows, summary_payload = score_phase0_records(
        records=records,
        holdout_rows=holdout_rows,
        manifest=manifest,
    )
    summary_payload["router"] = build_phase0_router_summary(
        router_profile=str(args.router_profile),
        assignments=router_assignments,
        slot_adapter_dirs=slot_adapter_dirs,
        fallback_assignments=fallback_assignments,
    )
    write_phase0_eval_outputs(
        artifact_root=artifact_root,
        report_root=report_root,
        records=records,
        scored_rows=scored_rows,
        summary_payload=summary_payload,
    )
    write_csv_rows(
        artifact_root / "phase0_router_assignments.csv",
        router_assignments,
        [
            "id",
            "benchmark_name",
            "benchmark_index",
            "family_short",
            "router_family",
            "router_slot",
            "router_adapter_path",
        ],
    )
    if fallback_assignments:
        write_csv_rows(
            artifact_root / "phase0_router_fallbacks.csv",
            fallback_assignments,
            [
                "id",
                "family_short",
                "primary_slot",
                "fallback_target",
                "fallback_reason",
                "primary_prediction",
                "primary_format_bucket",
                "primary_is_correct",
                "fallback_prediction",
                "fallback_format_bucket",
                "fallback_is_correct",
            ],
        )
    print(json.dumps(summary_payload["overall"], ensure_ascii=False, indent=2))
    print(json.dumps(summary_payload["router"], ensure_ascii=False, indent=2))


def run_phase0_eval_worker(args: argparse.Namespace) -> None:
    adapter_dir = None
    if args.adapter_path is not None:
        adapter_dir = Path(args.adapter_path).resolve()
        verify_training_outputs(adapter_dir)
    benchmark_rows = load_jsonl_records(Path(args.input_jsonl))
    records = generate_phase0_records_batched(
        benchmark_rows=benchmark_rows,
        model_path=Path(args.model_path).resolve(),
        adapter_dir=adapter_dir,
        max_tokens=int(args.max_tokens),
        top_p=float(args.top_p),
        temperature=float(args.temperature),
        max_num_seqs=int(args.max_num_seqs),
        prompt_chunk_size=int(args.prompt_chunk_size),
        prefill_batch_size=int(args.prefill_batch_size),
        completion_batch_size=int(args.completion_batch_size),
        lazy_load=bool(args.lazy_load),
        progress_every=int(args.progress_every),
        worker_label=str(args.worker_label),
        eval_thinking=str(getattr(args, "eval_thinking", "auto")),
    )
    write_jsonl_records(Path(args.output_jsonl), records)
    print(
        json.dumps(
            {
                "created_at": utc_now(),
                "worker_label": str(args.worker_label),
                "rows": len(records),
                "output_jsonl": str(Path(args.output_jsonl).resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def add_common_train_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    parser.add_argument("--train-csv", type=Path, default=DEFAULT_TRAIN_CSV)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--run-name", type=str, default=DEFAULT_RUN_NAME)
    parser.add_argument("--train-profile", type=str, choices=TRAIN_PROFILE_CHOICES, default="baseline")
    parser.add_argument(
        "--dataset-format",
        type=str,
        choices=("chat", "completion", "completions", "text"),
        default="chat",
    )
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accumulation-steps", type=int, default=4)
    parser.add_argument("--num-epochs", type=float, default=2.0)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--completion-thinking", type=str, default="auto")
    parser.add_argument("--lr-schedule-name", type=str, default="")
    parser.add_argument("--lr-schedule-end", type=float, default=0.0)
    parser.add_argument("--lr-warmup-ratio", type=float, default=0.0)
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--lora-rank", type=int, default=32)
    parser.add_argument("--lora-alpha", type=float, default=32.0)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--num-layers", type=int, default=-1)
    parser.add_argument("--resume-adapter-file", type=Path, default=None)
    parser.add_argument("--valid-shadow-rows", type=int, default=32)
    parser.add_argument("--steps-per-report", type=int, default=5)
    parser.add_argument("--steps-per-eval", type=int, default=900)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force-shadow-model", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Single-file mac_workspace/v0 pipeline for reproducing "
            "baseline/cot/phase2_binary_dsl with MLX LoRA and running a phase0-style offline eval."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_train = subparsers.add_parser("prepare-train", help="Build shadow model, dataset jsonl, and MLX config.")
    add_common_train_args(prepare_train)
    prepare_train.set_defaults(func=run_prepare_train)

    train = subparsers.add_parser("train", help="Prepare artifacts and launch mlx_lm.lora training.")
    add_common_train_args(train)
    train.set_defaults(func=run_train)

    train_mlx_config = subparsers.add_parser(
        "train-mlx-config",
        help="Internal helper: run mlx_lm.lora in-process so local dataset patches apply.",
    )
    train_mlx_config.add_argument("--config", type=Path, required=True)
    train_mlx_config.set_defaults(func=run_train_mlx_config)

    merge_adapters = subparsers.add_parser(
        "merge-adapters",
        help="Merge two MLX LoRA adapters into a single weighted adapter.",
    )
    merge_adapters.add_argument("--generalist-adapter", type=Path, required=True)
    merge_adapters.add_argument("--specialist-adapter", type=Path, required=True)
    merge_adapters.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    merge_adapters.add_argument("--merge-name", type=str, required=True)
    merge_adapters.add_argument("--generalist-weight", type=float, default=1.0)
    merge_adapters.add_argument("--specialist-weight", type=float, default=1.0)
    merge_adapters.set_defaults(func=run_merge_adapters)

    phase0_eval = subparsers.add_parser("eval-phase0", help="Run phase0-style offline evaluation with MLX generation.")
    phase0_eval.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    phase0_eval.add_argument("--adapter-path", type=Path, default=None)
    phase0_eval.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    phase0_eval.add_argument("--eval-name", type=str, default="phase0_base_model_mlx_eval")
    phase0_eval.add_argument("--phase0-prebuilt-root", type=Path, default=DEFAULT_PHASE0_PREBUILT_ROOT)
    phase0_eval.add_argument("--phase0-analysis-csv", type=Path, default=DEFAULT_PHASE0_ANALYSIS_CSV)
    phase0_eval.add_argument("--rebuild-phase0", action="store_true")
    phase0_eval.add_argument("--max-samples", type=int, default=None)
    phase0_eval.add_argument("--max-tokens", type=int, default=README_MAX_TOKENS)
    phase0_eval.add_argument("--temperature", type=float, default=README_TEMPERATURE)
    phase0_eval.add_argument("--top-p", type=float, default=README_TOP_P)
    phase0_eval.add_argument("--max-num-seqs", type=int, default=README_MAX_NUM_SEQS)
    phase0_eval.add_argument("--num-shards", type=int, default=0)
    phase0_eval.add_argument("--memory-budget-gb", type=float, default=420.0)
    phase0_eval.add_argument("--estimated-worker-memory-gb", type=float, default=100.0)
    phase0_eval.add_argument("--eval-output-root", type=Path, default=None)
    phase0_eval.add_argument("--family-short-filter", type=str, default="")
    phase0_eval.add_argument("--per-family-limit", type=int, default=0)
    phase0_eval.add_argument("--prompt-chunk-size", type=int, default=README_MAX_NUM_SEQS)
    phase0_eval.add_argument("--prefill-batch-size", type=int, default=32)
    phase0_eval.add_argument("--completion-batch-size", type=int, default=32)
    phase0_eval.add_argument("--progress-every", type=int, default=10)
    phase0_eval.add_argument("--eval-thinking", type=str, default="auto")
    phase0_eval.add_argument("--lazy-load", action="store_true")
    phase0_eval.add_argument("--force-shadow-model", action="store_true")
    phase0_eval.set_defaults(func=run_phase0_eval)

    phase0_router_eval = subparsers.add_parser(
        "eval-phase0-router",
        help="Run phase0-style offline evaluation with prompt-routed adapters.",
    )
    phase0_router_eval.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    phase0_router_eval.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    phase0_router_eval.add_argument("--eval-name", type=str, default="phase0_prompt_router_eval")
    phase0_router_eval.add_argument("--phase0-prebuilt-root", type=Path, default=DEFAULT_PHASE0_PREBUILT_ROOT)
    phase0_router_eval.add_argument("--phase0-analysis-csv", type=Path, default=DEFAULT_PHASE0_ANALYSIS_CSV)
    phase0_router_eval.add_argument("--rebuild-phase0", action="store_true")
    phase0_router_eval.add_argument("--max-samples", type=int, default=None)
    phase0_router_eval.add_argument("--max-tokens", type=int, default=README_MAX_TOKENS)
    phase0_router_eval.add_argument("--temperature", type=float, default=README_TEMPERATURE)
    phase0_router_eval.add_argument("--top-p", type=float, default=README_TOP_P)
    phase0_router_eval.add_argument("--max-num-seqs", type=int, default=README_MAX_NUM_SEQS)
    phase0_router_eval.add_argument("--num-shards", type=int, default=0)
    phase0_router_eval.add_argument("--memory-budget-gb", type=float, default=420.0)
    phase0_router_eval.add_argument("--estimated-worker-memory-gb", type=float, default=100.0)
    phase0_router_eval.add_argument("--eval-output-root", type=Path, default=None)
    phase0_router_eval.add_argument("--family-short-filter", type=str, default="")
    phase0_router_eval.add_argument("--per-family-limit", type=int, default=0)
    phase0_router_eval.add_argument("--prompt-chunk-size", type=int, default=README_MAX_NUM_SEQS)
    phase0_router_eval.add_argument("--prefill-batch-size", type=int, default=32)
    phase0_router_eval.add_argument("--completion-batch-size", type=int, default=32)
    phase0_router_eval.add_argument("--progress-every", type=int, default=10)
    phase0_router_eval.add_argument("--eval-thinking", type=str, default="auto")
    phase0_router_eval.add_argument("--lazy-load", action="store_true")
    phase0_router_eval.add_argument("--force-shadow-model", action="store_true")
    phase0_router_eval.add_argument(
        "--router-profile",
        type=str,
        choices=PHASE0_ROUTER_PROFILE_CHOICES,
        default=PHASE0_ROUTER_PROFILE_PROMPT_V1,
    )
    phase0_router_eval.add_argument("--general-adapter-path", type=Path, required=True)
    phase0_router_eval.add_argument("--reasoning-adapter-path", type=Path, required=True)
    phase0_router_eval.add_argument("--specialist-adapter-path", type=Path, required=True)
    phase0_router_eval.set_defaults(func=run_phase0_eval_router)

    phase0_eval_worker = subparsers.add_parser(
        "eval-phase0-worker",
        help="Internal worker for sharded phase0 MLX evaluation.",
    )
    phase0_eval_worker.add_argument("--model-path", type=Path, required=True)
    phase0_eval_worker.add_argument("--adapter-path", type=Path, default=None)
    phase0_eval_worker.add_argument("--input-jsonl", type=Path, required=True)
    phase0_eval_worker.add_argument("--output-jsonl", type=Path, required=True)
    phase0_eval_worker.add_argument("--max-tokens", type=int, default=README_MAX_TOKENS)
    phase0_eval_worker.add_argument("--temperature", type=float, default=README_TEMPERATURE)
    phase0_eval_worker.add_argument("--top-p", type=float, default=README_TOP_P)
    phase0_eval_worker.add_argument("--max-num-seqs", type=int, default=README_MAX_NUM_SEQS)
    phase0_eval_worker.add_argument("--prompt-chunk-size", type=int, default=README_MAX_NUM_SEQS)
    phase0_eval_worker.add_argument("--prefill-batch-size", type=int, default=32)
    phase0_eval_worker.add_argument("--completion-batch-size", type=int, default=32)
    phase0_eval_worker.add_argument("--progress-every", type=int, default=10)
    phase0_eval_worker.add_argument("--worker-label", type=str, default="worker")
    phase0_eval_worker.add_argument("--eval-thinking", type=str, default="auto")
    phase0_eval_worker.add_argument("--lazy-load", action="store_true")
    phase0_eval_worker.set_defaults(func=run_phase0_eval_worker)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
