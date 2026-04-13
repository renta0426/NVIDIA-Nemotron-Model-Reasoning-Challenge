from __future__ import annotations

from functools import lru_cache
import importlib.util
from pathlib import Path
import sys


def load_v1_module():
    module_name = 'v1_train'
    if module_name in sys.modules:
        return sys.modules[module_name]
    module_path = Path(__file__).resolve().parents[1] / 'code' / 'train.py'
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


v1 = load_v1_module()
EXPECTED_COUNTS = {
    'bit_manipulation': 1602,
    'gravity_constant': 1597,
    'unit_conversion': 1594,
    'text_decryption': 1576,
    'roman_numeral': 1576,
    'symbol_equation': 1555,
}


@lru_cache(maxsize=1)
def build_metadata():
    train_df = v1.pd.read_csv(v1.RAW_TRAIN_PATH)
    public_df = v1.pd.read_csv(v1.RAW_TEST_PATH)
    return v1.build_metadata_frame(train_df, public_df)


def test_family_count_regression_matches_expected_counts():
    metadata = build_metadata()
    counts = metadata['family'].value_counts().sort_index().to_dict()
    assert counts == EXPECTED_COUNTS


def test_metadata_contains_required_columns_and_public_overlap_flag():
    metadata = build_metadata()
    required_columns = {
        'id',
        'prompt',
        'answer',
        'family',
        'subfamily',
        'answer_type',
        'parse_ok',
        'parse_confidence',
        'num_examples',
        'query_raw',
        'group_signature',
        'hard_score',
        'risk_bin',
        'prompt_len_chars',
        'prompt_len_words',
        'answer_len',
        'contains_right_brace',
        'contains_backslash',
        'contains_backtick',
        'is_public_test_overlap',
    }
    assert required_columns.issubset(metadata.columns)
    assert len(metadata) == 9500
    assert int(metadata['is_public_test_overlap'].sum()) == 3
    assert set(metadata['risk_bin']) == {'risk_low', 'risk_mid', 'risk_high'}


def test_family_manual_audit_sampler_has_expected_shape():
    metadata = build_metadata()
    audit = v1.build_manual_audit_frame(metadata)

    assert len(audit) == 120
    assert audit['family'].value_counts().sort_index().to_dict() == {family: 20 for family in EXPECTED_COUNTS}
    assert int(audit['is_public_test_overlap'].sum()) >= 3
