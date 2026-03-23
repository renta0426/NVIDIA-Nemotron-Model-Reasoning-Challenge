from __future__ import annotations

from functools import lru_cache
import importlib.util
from pathlib import Path
import sys

import pandas as pd


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


@lru_cache(maxsize=1)
def build_metadata():
    train_df = v1.pd.read_csv(v1.RAW_TRAIN_PATH)
    public_df = v1.pd.read_csv(v1.RAW_TEST_PATH)
    return v1.build_metadata_frame(train_df, public_df)


@lru_cache(maxsize=1)
def build_splits():
    return v1.build_splits_frame(build_metadata())


def test_split_frame_has_expected_columns_and_length():
    split_df = build_splits()
    required_columns = {
        'cv5_fold',
        'is_holdout_hard',
        'group_shift_split0',
        'group_shift_split1',
        'group_shift_split2',
        'is_public_test_overlap',
        'group_signature',
    }
    assert required_columns.issubset(split_df.columns)
    assert len(split_df) == 9500
    assert set(split_df['cv5_fold']) == {0, 1, 2, 3, 4}


def test_cv5_family_balance_and_unique_valid_fold():
    split_df = build_splits()
    global_family = split_df['family'].value_counts(normalize=True).sort_index()
    fold_distributions = []
    for fold_idx in range(5):
        fold_df = split_df.loc[split_df['cv5_fold'] == fold_idx]
        fold_distribution = fold_df['family'].value_counts(normalize=True).reindex(global_family.index, fill_value=0.0)
        fold_distributions.append(fold_distribution)

    for family in global_family.index:
        ratios = [distribution[family] for distribution in fold_distributions]
        assert max(ratios) - min(ratios) <= 0.0151


def test_holdout_and_group_shift_integrity():
    split_df = build_splits()

    holdout_ratio = split_df.groupby('family')['is_holdout_hard'].mean()
    assert float(holdout_ratio.min()) >= 0.15

    for split_idx in range(3):
        column = f'group_shift_split{split_idx}'
        train_groups = set(split_df.loc[split_df[column] == 'train', 'group_signature'])
        test_groups = set(split_df.loc[split_df[column] == 'test', 'group_signature'])
        assert train_groups.isdisjoint(test_groups)


def test_write_eval_packs_outputs_expected_shapes(tmp_path):
    split_df = build_splits()
    v1.write_eval_packs(split_df, tmp_path)

    shadow_128 = pd.read_csv(tmp_path / 'shadow_128.csv')
    shadow_256 = pd.read_csv(tmp_path / 'shadow_256.csv')
    hard_shadow_256 = pd.read_csv(tmp_path / 'hard_shadow_256.csv')
    holdout_hard = pd.read_csv(tmp_path / 'holdout_hard.csv')

    assert len(shadow_128) == 128
    assert len(shadow_256) == 256
    assert len(hard_shadow_256) == 256
    assert not shadow_128['is_public_test_overlap'].any()
    assert not shadow_256['is_public_test_overlap'].any()
    assert not hard_shadow_256['is_public_test_overlap'].any()
    assert holdout_hard['is_public_test_overlap'].isin([True, False]).all()

    for fold_idx in range(5):
        fold_df = pd.read_csv(tmp_path / f'cv5_fold{fold_idx}.csv')
        assert len(fold_df) == int((split_df['cv5_fold'] == fold_idx).sum())

    for split_idx in range(3):
        group_df = pd.read_csv(tmp_path / f'group_shift_split{split_idx}.csv')
        assert set(group_df['group_shift_split' + str(split_idx)]) == {'test'}
