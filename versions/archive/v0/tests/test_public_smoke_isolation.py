from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pandas as pd


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


def test_prepare_public_smoke_copies_input_and_writes_manifest(tmp_path):
    train_csv = tmp_path / "train.csv"
    test_csv = tmp_path / "test.csv"
    output_csv = tmp_path / "public_smoke" / "test_public.csv"
    manifest_csv = tmp_path / "public_smoke" / "test_public_manifest.csv"

    pd.DataFrame(
        [
            {"id": "a", "prompt": "bit prompt", "answer": "10101010"},
            {"id": "b", "prompt": "roman prompt", "answer": "XIV"},
        ]
    ).to_csv(train_csv, index=False)
    pd.DataFrame(
        [
            {"id": "a", "prompt": "bit prompt"},
            {"id": "c", "prompt": "new prompt"},
        ]
    ).to_csv(test_csv, index=False)

    manifest_df = v0.prepare_public_smoke(
        input_csv=test_csv,
        output_csv=output_csv,
        train_csv=train_csv,
        manifest_csv=manifest_csv,
    )

    written_df = pd.read_csv(output_csv)
    assert output_csv.exists()
    assert manifest_csv.exists()
    assert output_csv != test_csv
    assert written_df.to_dict("records") == [
        {"id": "a", "prompt": "bit prompt"},
        {"id": "c", "prompt": "new prompt"},
    ]
    assert int(manifest_df["exact_row_match"].sum()) == 1
    assert manifest_df["overlap_type"].tolist() == ["exact_row_match", ""]
