from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def load_v0_module():
    module_name = "v0_train"
    if module_name in sys.modules:
        return sys.modules[module_name]
    module_path = Path(__file__).resolve().parents[1] / "code" / "train.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


v0 = load_v0_module()


def test_metadata_and_splits_are_consistent_for_repo_data(tmp_path):
    public_smoke_csv = tmp_path / "test_public.csv"
    manifest_csv = tmp_path / "test_public_manifest.csv"
    metadata_path = tmp_path / "train_metadata.parquet"
    splits_path = tmp_path / "train_splits.parquet"

    v0.prepare_public_smoke(
        input_csv=v0.RAW_TEST_PATH,
        output_csv=public_smoke_csv,
        train_csv=v0.RAW_TRAIN_PATH,
        manifest_csv=manifest_csv,
    )
    metadata_df = v0.build_metadata(
        train_csv=v0.RAW_TRAIN_PATH,
        public_smoke_csv=public_smoke_csv,
        output_path=metadata_path,
    )
    splits_df = v0.build_splits(
        metadata_path=metadata_path,
        output_path=splits_path,
    )

    assert len(metadata_df) == 9500
    assert int(metadata_df["is_public_test_overlap"].sum()) == 3
    assert set(splits_df["fold_cv5"].unique()) == {0, 1, 2, 3, 4}
    assert int(splits_df["is_hard_holdout"].sum()) > 0
    assert {
        "bit",
        "gravity",
        "symbol_equation",
        "text_decrypt",
        "unit",
    }.issubset(set(splits_df["family"].unique()))


def test_unit_group_shift_signature_handles_zero_denominator():
    signature = v0.infer_group_shift_signature(
        "Convert using 12 and 0 as the example ratio",
        "unit",
        "conversion_table",
    )
    assert signature == "ratio-undefined"
