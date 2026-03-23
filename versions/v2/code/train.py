from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
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
DEFAULT_SMOKE_IDENTIFIER = 'nemotron-v2-smoke'


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
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
