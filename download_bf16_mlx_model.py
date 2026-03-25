from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


DEFAULT_MODEL_REPO_ID = 'mlx-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-BF16'
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / 'model'
REQUIRED_FILES = (
    'README.md',
    'config.json',
    'generation_config.json',
    'tokenizer.json',
    'tokenizer_config.json',
    'model.safetensors.index.json',
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Download the BF16 MLX Nemotron model into the repository model directory.'
    )
    parser.add_argument(
        '--repo-id',
        default=DEFAULT_MODEL_REPO_ID,
        help='Hugging Face repo id to download.',
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help='Target directory for the downloaded snapshot.',
    )
    parser.add_argument(
        '--token-env',
        default='HF_TOKEN',
        help='Environment variable name that stores the Hugging Face token.',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print the resolved download settings without downloading.',
    )
    return parser


def resolve_token(token_env: str) -> str | None:
    token = os.environ.get(token_env)
    return token or None


def expected_shard_files(model_dir: Path) -> list[str]:
    index_path = model_dir / 'model.safetensors.index.json'
    payload = json.loads(index_path.read_text(encoding='utf-8'))
    weight_map = payload.get('weight_map')
    if not isinstance(weight_map, dict) or not weight_map:
        raise RuntimeError(f'Invalid or empty weight_map in {index_path}')
    return sorted({str(value) for value in weight_map.values() if value})


def stale_download_artifacts(model_dir: Path) -> list[str]:
    download_dir = model_dir / '.cache' / 'huggingface' / 'download'
    if not download_dir.exists():
        return []
    artifacts = [path.name for path in download_dir.glob('*.incomplete')]
    artifacts.extend(path.name for path in download_dir.glob('*.lock'))
    return sorted(artifacts)


def verify_download(model_dir: Path) -> None:
    missing = [name for name in REQUIRED_FILES if not (model_dir / name).is_file()]
    if missing:
        raise RuntimeError(f'Download completed but required files are missing: {", ".join(missing)}')
    shard_files = expected_shard_files(model_dir)
    missing_shards = [name for name in shard_files if not (model_dir / name).is_file()]
    stale_artifacts = stale_download_artifacts(model_dir)
    if missing_shards or stale_artifacts:
        details: list[str] = []
        if missing_shards:
            details.append(f'missing shard files: {", ".join(missing_shards)}')
        if stale_artifacts:
            details.append(f'stale download artifacts: {", ".join(stale_artifacts)}')
        raise RuntimeError(
            'BF16 model download is incomplete; rerun the same command to resume. '
            + ' | '.join(details)
        )


def clean_output_dir(output_dir: Path) -> int:
    removed_entries = 0
    if not output_dir.exists():
        return removed_entries
    for child in output_dir.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()
        removed_entries += 1
    return removed_entries


def materialize_snapshot(snapshot_path: Path, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(snapshot_path, output_dir, dirs_exist_ok=True)
    return sum(1 for path in output_dir.rglob('*') if path.is_file())


def download_model(repo_id: str, output_dir: Path, token_env: str) -> tuple[Path, int, int]:
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise SystemExit(
            'huggingface_hub is required. Install dependencies first with `uv sync`.'
        ) from exc

    snapshot_path = Path(
        snapshot_download(
            repo_id=repo_id,
            token=resolve_token(token_env),
        )
    )
    verify_download(snapshot_path)
    removed_entries = clean_output_dir(output_dir)
    copied_files = materialize_snapshot(snapshot_path, output_dir)
    verify_download(output_dir)
    return snapshot_path, removed_entries, copied_files


def main() -> int:
    args = build_parser().parse_args()
    output_dir = args.output_dir.resolve()

    print(f'repo_id={args.repo_id}')
    print(f'output_dir={output_dir}')
    print(f'token_env={args.token_env}')

    if args.dry_run:
        return 0

    snapshot_path, removed_entries, copied_files = download_model(args.repo_id, output_dir, args.token_env)
    print(f'snapshot_path={snapshot_path.resolve()}')
    print(f'cleaned_entries={removed_entries}')
    print(f'copied_files={copied_files}')
    print(f'downloaded_to={output_dir}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
