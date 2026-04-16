"""v3 corrective corpus: remove 'default 1' contaminated training examples.

Root cause analysis (v3 strategy review) showed that 92 token snapshots
(66 unique problem IDs, 648K tokens) contain teacher reasoning with
'default 1' fallback that produces WRONG answers.  Proxy binary accuracy
with 'default 1' in model output is 11-17%; without it, 96-100%.

This script:
  1. Loads the v20 base snapshot (7830 token dirs)
  2. Identifies and excludes the 92 'default 1' contaminated dirs
  3. Writes a clean bundle for Kaggle training

No overlay is added — this is a pure signal-cleaning experiment.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    while current != current.parent:
        if (current / "README.md").exists() and (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError(f"Could not locate repository root from {start}")


REPO_ROOT = find_repo_root(Path(__file__).resolve())
VERSION_ROOT = Path(__file__).resolve().parent

REASONING_DIR = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "reasoning"
TRAINING_SFT_ROOT = REPO_ROOT / "A-Open-ProgressPrizePublication" / "nemotron" / "training" / "sft"
BASE_SNAPSHOT_ROOT = TRAINING_SFT_ROOT / "04-08-16-14"
BASE_SNAPSHOT_CONFIG_PATH = BASE_SNAPSHOT_ROOT / "config.json"
BASE_SNAPSHOT_INDEX_PATH = BASE_SNAPSHOT_ROOT / "logprobs" / "index.jsonl"
DEFAULT_BUNDLE_PATH = TRAINING_SFT_ROOT / "v20_corrective_corpus_v3_bundle.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relative_to_repo(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(path)


def identify_default1_problems() -> set[str]:
    """Scan reasoning files and return problem IDs whose teacher trace uses 'default 1'."""
    d1_ids: set[str] = set()
    binary_keywords = ["AND(", "OR(", "XOR(", "NOT(", "bit column", "Output bit"]
    for f in sorted(REASONING_DIR.glob("*.txt")):
        text = f.read_text(encoding="utf-8")
        is_binary = any(kw in text for kw in binary_keywords)
        if is_binary and "default 1" in text:
            d1_ids.add(f.stem)
    return d1_ids


def load_base_snapshot_index() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with BASE_SNAPSHOT_INDEX_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_clean_bundle(
    bundle_path: Path,
    d1_problem_ids: set[str],
    dry_run: bool = False,
) -> dict[str, Any]:
    """Build v20 bundle with default-1 examples removed."""
    config = read_json(BASE_SNAPSHOT_CONFIG_PATH)
    batch_size = int(config["batch_size"])
    base_rows = load_base_snapshot_index()

    # Partition into keep vs exclude (handle -p0 suffixed IDs)
    keep_rows: list[dict[str, Any]] = []
    excluded_rows: list[dict[str, Any]] = []
    for row in base_rows:
        pid = str(row["problem_id"])
        base_pid = pid.split("-p")[0] if "-p" in pid else pid
        if base_pid in d1_problem_ids:
            excluded_rows.append(row)
        else:
            keep_rows.append(row)

    print(f"Base snapshot rows: {len(base_rows)}")
    print(f"  Keeping: {len(keep_rows)}")
    print(f"  Excluding (default 1): {len(excluded_rows)}")

    if dry_run:
        return {
            "dry_run": True,
            "base_rows": len(base_rows),
            "keep_rows": len(keep_rows),
            "excluded_rows": len(excluded_rows),
        }

    bundle_path.parent.mkdir(parents=True, exist_ok=True)

    total_examples = 0
    total_tokens = 0
    total_loss_tokens = 0
    max_seq_len = 0
    category_counts: Counter[str] = Counter()
    excluded_tokens = 0
    excluded_loss_tokens = 0

    manifest = {
        "record_type": "manifest",
        "type": "manifest",
        "bundle_format": "nemotron_single_file_training_bundle_v1",
        "version": "v20_corrective_corpus_v3",
        "created_at": utc_now(),
        "base_snapshot_root": relative_to_repo(BASE_SNAPSHOT_ROOT),
        "base_snapshot_config": config,
        "bundle_path": relative_to_repo(bundle_path),
        "d1_excluded_problem_count": len(d1_problem_ids),
        "d1_excluded_row_count": len(excluded_rows),
        "note": (
            "v3 signal-cleaning bundle: v20 base minus 'default 1' contaminated "
            "teacher examples. No overlay added — pure subtractive experiment."
        ),
    }

    with bundle_path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(manifest, ensure_ascii=False) + "\n")

        for row in keep_rows:
            problem_id = str(row["problem_id"])
            segment = str(row["segment"])
            token_path = BASE_SNAPSHOT_ROOT / "tokens" / problem_id / f"{Path(segment).stem}.json"
            if not token_path.exists():
                raise SystemExit(f"Missing token snapshot: {token_path}")

            payload_data = read_json(token_path)
            tokens = payload_data["tokens"]
            mask = payload_data["mask"]
            category = str(row["category"])
            num_loss_tokens = int(row["num_loss_tokens"])

            record = {
                "record_type": "example",
                "example_id": problem_id,
                "source_problem_id": problem_id,
                "source": "base_snapshot",
                "segment": segment,
                "category": category,
                "step": int(row["step"]),
                "num_loss_tokens": num_loss_tokens,
                "tokens": tokens,
                "mask": mask,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            total_examples += 1
            total_tokens += len(tokens)
            total_loss_tokens += sum(mask)
            max_seq_len = max(max_seq_len, len(tokens))
            category_counts[category] += 1

    # Compute excluded token counts for reporting
    for row in excluded_rows:
        problem_id = str(row["problem_id"])
        segment = str(row["segment"])
        token_path = BASE_SNAPSHOT_ROOT / "tokens" / problem_id / f"{Path(segment).stem}.json"
        if token_path.exists():
            payload_data = read_json(token_path)
            excluded_tokens += len(payload_data["tokens"])
            excluded_loss_tokens += sum(payload_data["mask"])

    existing_steps = [int(r["step"]) for r in keep_rows]
    total_steps = max(existing_steps) + 1 if existing_steps else 0

    return {
        "path": relative_to_repo(bundle_path),
        "format": "nemotron_single_file_training_bundle_v1",
        "version": "v20_corrective_corpus_v3",
        "base_rows_total": len(base_rows),
        "base_rows_kept": len(keep_rows),
        "base_rows_excluded": len(excluded_rows),
        "d1_problem_ids_excluded": len(d1_problem_ids),
        "total_examples": total_examples,
        "batch_size": batch_size,
        "total_steps": total_steps,
        "total_tokens": total_tokens,
        "total_loss_tokens": total_loss_tokens,
        "excluded_tokens": excluded_tokens,
        "excluded_loss_tokens": excluded_loss_tokens,
        "max_seq_len": max_seq_len,
        "category_counts": dict(sorted(category_counts.items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="v3 corrective corpus: remove default-1 examples")
    parser.add_argument(
        "--bundle-path",
        type=Path,
        default=DEFAULT_BUNDLE_PATH,
        help="Output bundle JSONL path",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print stats without writing")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print("=" * 60)
    print("v3 corrective corpus: default-1 signal cleaning")
    print("=" * 60)

    # Step 1: identify default-1 problem IDs
    print("\n[1/3] Scanning reasoning files for 'default 1' traces...")
    d1_ids = identify_default1_problems()
    print(f"  Found {len(d1_ids)} problem IDs with 'default 1' in teacher reasoning")

    # Step 2: build the clean bundle
    print(f"\n[2/3] Building clean bundle at {args.bundle_path}")
    stats = build_clean_bundle(
        bundle_path=args.bundle_path,
        d1_problem_ids=d1_ids,
        dry_run=args.dry_run,
    )

    # Step 3: save summary
    summary_path = VERSION_ROOT / "v3_bundle_summary.json"
    summary_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n")
    print(f"\n[3/3] Summary saved to {summary_path}")

    print("\n" + "=" * 60)
    print("Bundle statistics:")
    print("=" * 60)
    for k, v in stats.items():
        if k == "category_counts":
            print(f"  {k}:")
            for cat, cnt in sorted(v.items()):
                print(f"    {cat}: {cnt}")
        else:
            print(f"  {k}: {v}")

    if not args.dry_run:
        # Verify bundle
        line_count = 0
        with open(args.bundle_path) as fh:
            for _ in fh:
                line_count += 1
        expected = stats["total_examples"] + 1  # +1 for manifest
        assert line_count == expected, f"Line count {line_count} != expected {expected}"
        size_mb = args.bundle_path.stat().st_size / (1024 * 1024)
        print(f"\n  Bundle verified: {line_count} lines, {size_mb:.1f} MB")
        print("  ✓ Ready for Kaggle upload")


if __name__ == "__main__":
    main()
