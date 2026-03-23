from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


VERSION_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_ROOT = VERSION_ROOT / 'outputs'
MODELS_ROOT = OUTPUTS_ROOT / 'models'
RUNTIME_ROOT = OUTPUTS_ROOT / 'runtime'

DEFAULT_MODEL_REPO_ID = 'lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit'
DEFAULT_LOCAL_MODEL_NAME = 'nemotron-3-nano-30b-a3b-mlx-6bit'
DEFAULT_ACTIVE_MODEL_PATH = RUNTIME_ROOT / 'active_model.json'
DEFAULT_MODEL_REGISTRY_PATH = RUNTIME_ROOT / 'model_registry_v2.json'


@dataclass(frozen=True)
class ModelDownloadSpec:
    repo_id: str = DEFAULT_MODEL_REPO_ID
    local_name: str = DEFAULT_LOCAL_MODEL_NAME
    revision: str | None = None
    token_env: str = 'HF_TOKEN'


def ensure_runtime_directories() -> None:
    for path in (OUTPUTS_ROOT, MODELS_ROOT, RUNTIME_ROOT):
        path.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sanitize_local_name(value: str) -> str:
    normalized = value.strip().replace('/', '--')
    if not normalized:
        raise ValueError('local model name must not be empty.')
    return normalized


def default_model_directory(spec: ModelDownloadSpec) -> Path:
    return MODELS_ROOT / sanitize_local_name(spec.local_name)


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
    active_path = Path(args.active_model_path)
    payload = load_json_file(active_path, default=None)
    if payload is None:
        raise FileNotFoundError(f'Active model manifest was not found: {active_path}')
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='v2 Mac-first model bootstrap utilities.')
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
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
