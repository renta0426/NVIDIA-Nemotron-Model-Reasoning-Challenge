from __future__ import annotations

import argparse
import os
from pathlib import Path


DEFAULT_MODEL_REPO_ID = 'mlx-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-BF16'
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / 'model'
REQUIRED_FILES = (
    'README.md',
    'config.json',
    'tokenizer.json',
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


def verify_download(output_dir: Path) -> None:
    missing = [name for name in REQUIRED_FILES if not (output_dir / name).is_file()]
    if missing:
        joined = ', '.join(missing)
        raise RuntimeError(f'Download completed but required files are missing: {joined}')


def download_model(repo_id: str, output_dir: Path, token_env: str) -> Path:
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise SystemExit(
            'huggingface_hub is required. Install dependencies first with `uv sync`.'
        ) from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = Path(
        snapshot_download(
            repo_id=repo_id,
            local_dir=str(output_dir),
            token=resolve_token(token_env),
            resume_download=True,
        )
    )
    verify_download(output_dir)
    return snapshot_path


def main() -> int:
    args = build_parser().parse_args()
    output_dir = args.output_dir.resolve()

    print(f'repo_id={args.repo_id}')
    print(f'output_dir={output_dir}')
    print(f'token_env={args.token_env}')

    if args.dry_run:
        return 0

    snapshot_path = download_model(args.repo_id, output_dir, args.token_env)
    print(f'downloaded_to={snapshot_path.resolve()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())