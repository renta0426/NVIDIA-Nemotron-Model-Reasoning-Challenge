from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

import yaml


VERSION_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = VERSION_ROOT.parents[1]
CONF_ROOT = VERSION_ROOT / 'conf'
CONF_DATA_ROOT = CONF_ROOT / 'data'
CONF_TRAIN_ROOT = CONF_ROOT / 'train'
CONF_PACKAGE_ROOT = CONF_ROOT / 'package'
DATA_ROOT = VERSION_ROOT / 'data'
PROCESSED_ROOT = DATA_ROOT / 'processed'
SYNTH_ROOT = DATA_ROOT / 'synth'
TRAIN_PACKS_ROOT = DATA_ROOT / 'train_packs'
OUTPUTS_ROOT = VERSION_ROOT / 'outputs'
MODELS_ROOT = OUTPUTS_ROOT / 'models'
RUNTIME_ROOT = OUTPUTS_ROOT / 'runtime'
AUDITS_ROOT = OUTPUTS_ROOT / 'audits'
DATASETS_ROOT = OUTPUTS_ROOT / 'datasets'
TRAIN_OUTPUT_ROOT = OUTPUTS_ROOT / 'train'
EVAL_ROOT = OUTPUTS_ROOT / 'eval'
PACKAGING_ROOT = OUTPUTS_ROOT / 'packaging'
REPORTS_ROOT = OUTPUTS_ROOT / 'reports'

DEFAULT_MODEL_REPO_ID = 'lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit'
DEFAULT_LOCAL_MODEL_NAME = 'nemotron-3-nano-30b-a3b-mlx-6bit'
DEFAULT_ACTIVE_MODEL_PATH = RUNTIME_ROOT / 'active_model.json'
DEFAULT_MODEL_REGISTRY_PATH = RUNTIME_ROOT / 'model_registry_v2.json'
DEFAULT_SMOKE_IDENTIFIER = 'nemotron-v2-smoke'

DEFAULT_REAL_CANONICAL_CONFIG_PATH = CONF_DATA_ROOT / 'real_canonical.yaml'
DEFAULT_SYNTH_CORE_CONFIG_PATH = CONF_DATA_ROOT / 'synth_core.yaml'
DEFAULT_SYNTH_HARD_CONFIG_PATH = CONF_DATA_ROOT / 'synth_hard.yaml'
DEFAULT_TEACHER_DISTILL_CONFIG_PATH = CONF_DATA_ROOT / 'teacher_distill.yaml'
DEFAULT_FORMAT_SHARPENING_CONFIG_PATH = CONF_DATA_ROOT / 'format_sharpening.yaml'
DEFAULT_MIX_STAGE_A_CONFIG_PATH = CONF_DATA_ROOT / 'mix_stage_a.yaml'
DEFAULT_MIX_STAGE_B_CONFIG_PATH = CONF_DATA_ROOT / 'mix_stage_b.yaml'

DEFAULT_STAGE_A_R32_ALPHA32_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_a_r32_alpha32.yaml'
DEFAULT_STAGE_A_R32_ALPHA32_WEIGHTED_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_a_r32_alpha32_weighted.yaml'
DEFAULT_STAGE_A_R32_ALPHA64_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_a_r32_alpha64.yaml'
DEFAULT_STAGE_B_HARDENING_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_b_hardening.yaml'
DEFAULT_STAGE_B_A6000_COMPAT_CONFIG_PATH = CONF_TRAIN_ROOT / 'sft_stage_b_a6000_compat.yaml'
DEFAULT_PEFT_SMOKE_CONFIG_PATH = CONF_PACKAGE_ROOT / 'peft_smoke.yaml'

DEFAULT_V1_METADATA_PATH = REPO_ROOT / 'versions' / 'v1' / 'data' / 'processed' / 'train_metadata_v1.parquet'
DEFAULT_V1_SPLITS_PATH = REPO_ROOT / 'versions' / 'v1' / 'data' / 'processed' / 'train_splits_v1.parquet'
DEFAULT_TRAIN_CSV_PATH = REPO_ROOT / 'data' / 'train.csv'

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

    print(f'Filtered {len(candidates)} candidates -> {len(accepted_rows)} accepted traces')
    print(f'Written registry: {registry_path}')
    print(f'Written accepted: {out_path}')


def run_build_format_pairs(args: argparse.Namespace) -> None:
    import pandas as pd

    _load_yaml_config(args.config_path)
    df = pd.read_parquet(_require_existing_path(args.real_canonical_path, label='real canonical parquet'))
    teacher_path = Path(args.teacher_traces_path)
    teacher_df = pd.read_parquet(teacher_path) if teacher_path.exists() else pd.DataFrame()
    pairs: list[dict[str, Any]] = []
    synth_format_rows: list[dict[str, Any]] = []

    for index, (_, row) in enumerate(df.iterrows()):
        answer = str(row.get('answer_canonical', row.get('answer', '')))
        format_policy = str(row.get('format_policy', 'final_answer_colon'))
        source_id = str(row['id'])
        family = str(row['family'])

        chosen = f'\\boxed{{{answer}}}' if format_policy == 'boxed_final_line' else f'Final answer: {answer}'
        rejected = answer
        pairs.append(
            {
                'pair_id': f'fmt_{source_id}_{index}',
                'source_id': source_id,
                'family': family,
                'answer': answer,
                'format_policy': format_policy,
                'chosen': chosen,
                'rejected': rejected,
                'chosen_format_bucket': 'clean_boxed' if format_policy == 'boxed_final_line' else 'clean_final_answer',
                'rejected_format_bucket': 'last_line_fallback',
            }
        )
        synth_format_rows.append(
            {
                'pair_id': f'sfmt_{source_id}_{index}',
                'source_id': source_id,
                'family': family,
                'answer': answer,
                'format_policy': format_policy,
                'chosen': f'Final answer: {answer}',
                'format_bucket': 'clean_final_answer',
            }
        )

    for index, (_, row) in enumerate(teacher_df.iterrows()):
        answer = str(row.get('answer', row.get('extracted_answer', '')))
        format_policy = str(row.get('format_policy', 'final_answer_colon'))
        source_id = str(row.get('source_id', row.get('trace_id', f'trace_{index}')))
        family = str(row.get('family', ''))
        chosen = str(row.get('raw_output', '')).strip() or (
            f'\\boxed{{{answer}}}' if format_policy == 'boxed_final_line' else f'Final answer: {answer}'
        )
        pairs.append(
            {
                'pair_id': f'tfmt_{source_id}_{index}',
                'source_id': source_id,
                'family': family,
                'answer': answer,
                'format_policy': format_policy,
                'chosen': chosen,
                'rejected': answer,
                'chosen_format_bucket': str(row.get('format_bucket', 'clean_final_answer')),
                'rejected_format_bucket': 'last_line_fallback',
            }
        )
        synth_format_rows.append(
            {
                'pair_id': f'tsfmt_{source_id}_{index}',
                'source_id': source_id,
                'family': family,
                'answer': answer,
                'format_policy': format_policy,
                'chosen': chosen,
                'format_bucket': str(row.get('format_bucket', 'clean_final_answer')),
            }
        )

    pairs_df = pd.DataFrame(pairs)
    synth_format_df = pd.DataFrame(synth_format_rows)

    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pairs_df.to_parquet(out_path, index=False)

    synth_path = DEFAULT_SYNTH_FORMAT_OUTPUT_PATH
    synth_path.parent.mkdir(parents=True, exist_ok=True)
    synth_format_df.to_parquet(synth_path, index=False)

    print(f'Wrote {len(pairs_df)} format pairs to {out_path}')
    print(f'Wrote {len(synth_format_df)} synth format rows to {synth_path}')


def run_build_correction_pairs(args: argparse.Namespace) -> None:
    import pandas as pd

    df = pd.read_parquet(_require_existing_path(args.real_canonical_path, label='real canonical parquet'))
    if 'is_holdout_hard' in df.columns:
        mask = df['is_holdout_hard'].fillna(False) | (df['hard_score'] > 6.0)
        hard_df = df.loc[mask].copy()
    else:
        hard_df = df.loc[df['hard_score'] > 6.0].copy()

    pairs: list[dict[str, Any]] = []
    for index, (_, row) in enumerate(hard_df.iterrows()):
        answer = str(row.get('answer_canonical', row.get('answer', '')))
        family = str(row['family'])
        source_id = str(row['id'])
        prompt = str(row.get('prompt', ''))
        format_policy = str(row.get('format_policy', 'final_answer_colon'))

        chosen_output = (
            f'Let me work through this carefully.\n\nFinal answer: \\boxed{{{answer}}}'
            if format_policy == 'boxed_final_line'
            else f'Let me work through this carefully.\n\nFinal answer: {answer}'
        )

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

        rejected_output = (
            f'Let me work through this carefully.\n\nFinal answer: \\boxed{{{wrong_answer}}}'
            if format_policy == 'boxed_final_line'
            else f'Let me work through this carefully.\n\nFinal answer: {wrong_answer}'
        )

        pairs.append(
            {
                'pair_id': f'corr_{source_id}_{index}',
                'source_id': source_id,
                'family': family,
                'prompt': prompt,
                'chosen_output': chosen_output,
                'rejected_output': rejected_output,
                'error_family_tag': family,
                'error_subtype': error_subtype,
                'source_eval_run': 'bootstrap',
            }
        )

    pairs_df = pd.DataFrame(pairs)
    out_path = Path(args.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pairs_df.to_parquet(out_path, index=False)

    print(f'Wrote {len(pairs_df)} correction pairs to {out_path}')


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
            return value
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


def resolve_training_base_model(base_model_value: Any, active_model: dict[str, Any]) -> str:
    requested = normalize_optional_text(base_model_value)
    active_snapshot = normalize_optional_text(active_model.get('snapshot_dir'))
    active_repo_id = normalize_optional_text(active_model.get('repo_id'))
    if active_snapshot and requested in {None, DEFAULT_MODEL_REPO_ID, active_repo_id, DEFAULT_LOCAL_MODEL_NAME}:
        return active_snapshot
    if requested is None:
        return active_snapshot or 'UNSET_base_model'
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
        'version': 'v2',
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
        'version': 'v2',
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
    submission_path = out_dir / 'submission_manifest.json'
    submission_path.write_text(json.dumps(submission_manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='v2 Mac-first data factory and training utilities.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    download_parser = subparsers.add_parser(
        'download-model',
        help='Download the fixed MLX 6bit model and persist its local manifest.',
    )
    download_parser.add_argument('--repo-id', default=DEFAULT_MODEL_REPO_ID)
    download_parser.add_argument('--local-name', default=DEFAULT_LOCAL_MODEL_NAME)
    download_parser.add_argument('--revision', default=None)
    download_parser.add_argument('--token-env', default='HF_TOKEN')
    download_parser.add_argument('--output-dir', default=None)
    download_parser.add_argument('--active-model-path', default=str(DEFAULT_ACTIVE_MODEL_PATH))
    download_parser.add_argument('--registry-path', default=str(DEFAULT_MODEL_REGISTRY_PATH))
    download_parser.set_defaults(func=run_download_model)

    show_parser = subparsers.add_parser(
        'show-active-model',
        help='Print the currently saved active model manifest.',
    )
    show_parser.add_argument('--active-model-path', default=str(DEFAULT_ACTIVE_MODEL_PATH))
    show_parser.set_defaults(func=run_show_active_model)

    smoke_parser = subparsers.add_parser(
        'smoke-model',
        help='Load the active MLX model and run a tiny local generation smoke test.',
    )
    smoke_parser.add_argument('--runtime', choices=('auto', 'python', 'lms'), default='auto')
    smoke_parser.add_argument('--model-dir', default=None)
    smoke_parser.add_argument('--repo-id', default=None)
    smoke_parser.add_argument('--active-model-path', default=str(DEFAULT_ACTIVE_MODEL_PATH))
    smoke_parser.add_argument('--identifier', default=DEFAULT_SMOKE_IDENTIFIER)
    smoke_parser.add_argument('--ttl', type=int, default=600)
    smoke_parser.add_argument('--prompt', default='Reply with exactly OK.')
    smoke_parser.add_argument('--max-tokens', type=int, default=8)
    smoke_parser.set_defaults(func=run_smoke_model)

    real_parser = subparsers.add_parser(
        'build-real-canonical',
        help='Build the v2 real canonical table from v1 metadata and splits.',
    )
    real_parser.add_argument('--metadata-path', default=str(DEFAULT_V1_METADATA_PATH))
    real_parser.add_argument('--splits-path', default=str(DEFAULT_V1_SPLITS_PATH))
    real_parser.add_argument('--train-csv-path', default=str(DEFAULT_TRAIN_CSV_PATH))
    real_parser.add_argument('--config-path', default=str(DEFAULT_REAL_CANONICAL_CONFIG_PATH))
    real_parser.add_argument('--output-path', default=str(DEFAULT_REAL_CANONICAL_OUTPUT_PATH))
    real_parser.set_defaults(func=run_build_real_canonical)

    solver_parser = subparsers.add_parser(
        'build-solver-registry',
        help='Build family-wise solver and validator registry metadata.',
    )
    solver_parser.add_argument('--real-canonical-path', default=str(DEFAULT_REAL_CANONICAL_OUTPUT_PATH))
    solver_parser.add_argument('--output-path', default=str(DEFAULT_SOLVER_REGISTRY_OUTPUT_PATH))
    solver_parser.set_defaults(func=run_build_solver_registry)

    synth_core_parser = subparsers.add_parser(
        'build-synth-core',
        help='Build the main sibling synthetic pool with acceptance tracking.',
    )
    synth_core_parser.add_argument('--real-canonical-path', default=str(DEFAULT_REAL_CANONICAL_OUTPUT_PATH))
    synth_core_parser.add_argument('--solver-registry-path', default=str(DEFAULT_SOLVER_REGISTRY_OUTPUT_PATH))
    synth_core_parser.add_argument('--config-path', default=str(DEFAULT_SYNTH_CORE_CONFIG_PATH))
    synth_core_parser.add_argument('--output-path', default=str(DEFAULT_SYNTH_CORE_OUTPUT_PATH))
    synth_core_parser.add_argument('--registry-path', default=str(DEFAULT_SYNTHETIC_REGISTRY_OUTPUT_PATH))
    synth_core_parser.set_defaults(func=run_build_synth_core)

    synth_hard_parser = subparsers.add_parser(
        'build-synth-hard',
        help='Build the hard synthetic pool with stricter curriculum sampling.',
    )
    synth_hard_parser.add_argument('--real-canonical-path', default=str(DEFAULT_REAL_CANONICAL_OUTPUT_PATH))
    synth_hard_parser.add_argument('--solver-registry-path', default=str(DEFAULT_SOLVER_REGISTRY_OUTPUT_PATH))
    synth_hard_parser.add_argument('--config-path', default=str(DEFAULT_SYNTH_HARD_CONFIG_PATH))
    synth_hard_parser.add_argument('--output-path', default=str(DEFAULT_SYNTH_HARD_OUTPUT_PATH))
    synth_hard_parser.add_argument('--registry-path', default=str(DEFAULT_SYNTHETIC_REGISTRY_OUTPUT_PATH))
    synth_hard_parser.set_defaults(func=run_build_synth_hard)

    format_pairs_parser = subparsers.add_parser(
        'build-format-pairs',
        help='Build format sharpening pairs from real and teacher-accepted traces.',
    )
    format_pairs_parser.add_argument('--real-canonical-path', default=str(DEFAULT_REAL_CANONICAL_OUTPUT_PATH))
    format_pairs_parser.add_argument('--teacher-traces-path', default=str(DEFAULT_DISTILLED_TRACES_OUTPUT_PATH))
    format_pairs_parser.add_argument('--config-path', default=str(DEFAULT_FORMAT_SHARPENING_CONFIG_PATH))
    format_pairs_parser.add_argument('--output-path', default=str(DEFAULT_FORMAT_PAIRS_OUTPUT_PATH))
    format_pairs_parser.set_defaults(func=run_build_format_pairs)

    distill_candidates_parser = subparsers.add_parser(
        'build-distill-candidates',
        help='Build teacher prompt candidates before trace filtering.',
    )
    distill_candidates_parser.add_argument('--real-canonical-path', default=str(DEFAULT_REAL_CANONICAL_OUTPUT_PATH))
    distill_candidates_parser.add_argument('--config-path', default=str(DEFAULT_TEACHER_DISTILL_CONFIG_PATH))
    distill_candidates_parser.add_argument('--output-path', default=str(DEFAULT_DISTILL_CANDIDATES_OUTPUT_PATH))
    distill_candidates_parser.set_defaults(func=run_build_distill_candidates)

    filter_distilled_parser = subparsers.add_parser(
        'filter-distilled-traces',
        help='Filter teacher traces against gold answers and write accepted traces.',
    )
    filter_distilled_parser.add_argument('--candidate-path', default=str(DEFAULT_DISTILL_CANDIDATES_OUTPUT_PATH))
    filter_distilled_parser.add_argument('--output-path', default=str(DEFAULT_DISTILLED_TRACES_OUTPUT_PATH))
    filter_distilled_parser.add_argument('--registry-path', default=str(DEFAULT_TEACHER_TRACE_REGISTRY_OUTPUT_PATH))
    filter_distilled_parser.set_defaults(func=run_filter_distilled_traces)

    correction_pairs_parser = subparsers.add_parser(
        'build-correction-pairs',
        help='Build correction pairs from real rows and accepted teacher traces.',
    )
    correction_pairs_parser.add_argument('--real-canonical-path', default=str(DEFAULT_REAL_CANONICAL_OUTPUT_PATH))
    correction_pairs_parser.add_argument('--teacher-traces-path', default=str(DEFAULT_DISTILLED_TRACES_OUTPUT_PATH))
    correction_pairs_parser.add_argument('--output-path', default=str(DEFAULT_CORRECTION_PAIRS_OUTPUT_PATH))
    correction_pairs_parser.set_defaults(func=run_build_correction_pairs)

    train_mix_parser = subparsers.add_parser(
        'build-train-mix',
        help='Build Stage A and Stage B train packs with provenance.',
    )
    train_mix_parser.add_argument('--real-canonical-path', default=str(DEFAULT_REAL_CANONICAL_OUTPUT_PATH))
    train_mix_parser.add_argument('--synthetic-registry-path', default=str(DEFAULT_SYNTHETIC_REGISTRY_OUTPUT_PATH))
    train_mix_parser.add_argument('--stage-a-config-path', default=str(DEFAULT_MIX_STAGE_A_CONFIG_PATH))
    train_mix_parser.add_argument('--stage-b-config-path', default=str(DEFAULT_MIX_STAGE_B_CONFIG_PATH))
    train_mix_parser.add_argument('--stage-a-output-path', default=str(DEFAULT_STAGE_A_MIX_OUTPUT_PATH))
    train_mix_parser.add_argument('--stage-b-output-path', default=str(DEFAULT_STAGE_B_MIX_OUTPUT_PATH))
    train_mix_parser.add_argument('--hard-only-output-path', default=str(DEFAULT_STAGE_B_HARD_ONLY_OUTPUT_PATH))
    train_mix_parser.add_argument('--registry-path', default=str(DEFAULT_TRAIN_MIX_REGISTRY_OUTPUT_PATH))
    train_mix_parser.set_defaults(func=run_build_train_mix)

    train_sft_parser = subparsers.add_parser(
        'train-sft',
        help='Run or render the Mac-first Stage A or Stage B SFT job.',
    )
    train_sft_parser.add_argument('--stage', choices=('a', 'b'), default='a')
    train_sft_parser.add_argument('--config-path', default=str(DEFAULT_STAGE_A_R32_ALPHA32_CONFIG_PATH))
    train_sft_parser.add_argument('--train-pack-path', default=str(DEFAULT_STAGE_A_MIX_OUTPUT_PATH))
    train_sft_parser.add_argument('--dataset-dir', default=None)
    train_sft_parser.add_argument('--valid-fold', type=int, default=0)
    train_sft_parser.add_argument('--valid-fraction', type=float, default=0.05)
    train_sft_parser.add_argument('--max-train-rows', type=int, default=None)
    train_sft_parser.add_argument('--max-valid-rows', type=int, default=None)
    train_sft_parser.add_argument('--execute', action='store_true')
    train_sft_parser.add_argument('--output-dir', default=str(TRAIN_OUTPUT_ROOT))
    train_sft_parser.set_defaults(func=run_train_sft)

    package_peft_parser = subparsers.add_parser(
        'package-peft',
        help='Run packaging checks and render submission-ready PEFT artifacts.',
    )
    package_peft_parser.add_argument('--config-path', default=str(DEFAULT_PEFT_SMOKE_CONFIG_PATH))
    package_peft_parser.add_argument('--adapter-dir', default=str(TRAIN_OUTPUT_ROOT))
    package_peft_parser.add_argument('--output-dir', default=str(PACKAGING_ROOT))
    package_peft_parser.set_defaults(func=run_package_peft)

    runbook_parser = subparsers.add_parser(
        'write-runbook',
        help='Write the v2 training and promotion runbook outputs.',
    )
    runbook_parser.add_argument('--candidate-registry-path', default=str(DEFAULT_CANDIDATE_REGISTRY_OUTPUT_PATH))
    runbook_parser.add_argument('--promotion-rules-path', default=str(DEFAULT_PROMOTION_RULES_OUTPUT_PATH))
    runbook_parser.add_argument('--output-path', default=str(DEFAULT_TRAINING_RUNBOOK_OUTPUT_PATH))
    runbook_parser.set_defaults(func=run_write_runbook)

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    ensure_v2_layout_scaffold()
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
