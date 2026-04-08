from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    while current != current.parent:
        if (current / 'README.md').exists() and (current / 'pyproject.toml').exists():
            return current
        current = current.parent
    raise RuntimeError(f'Could not locate repository root from {start}')


REPO_ROOT = find_repo_root(Path(__file__).resolve())
PLAN_ROOT = Path(__file__).resolve().parent
RESULT_ROOT = PLAN_ROOT / 'result' / 'leaderboard_proxy_v1'
ARTIFACTS_DIR = RESULT_ROOT / 'artifacts'
REPORTS_DIR = RESULT_ROOT / 'reports'

DEFAULT_V3F_PHASE0_ROW_LEVEL = (
    REPO_ROOT
    / 'baseline'
    / 'nemotron-sft-lora-with-cot-v2'
    / 'result'
    / 'v3f'
    / 'phase0_offline_eval'
    / 'artifacts'
    / 'phase0_eval_row_level.csv'
)
DEFAULT_CURRENT_PHASE0_ROW_LEVEL = (
    REPO_ROOT
    / 'cuda-train-data-analysis-v1'
    / 'proof_first_solver_factory_routing'
    / 'result'
    / 'phase0_offline_eval'
    / 'artifacts'
    / 'phase0_eval_row_level.csv'
)
DEFAULT_V3F_SPECIALIZED_ROW_LEVEL = (
    REPO_ROOT
    / 'baseline'
    / 'nemotron-sft-lora-with-cot-v2'
    / 'result'
    / 'v3f'
    / 'phase0_offline_eval_binary_bias_specialized'
    / 'artifacts'
    / 'binary_bias_specialized_eval_row_level.csv'
)
DEFAULT_CURRENT_SPECIALIZED_ROW_LEVEL = (
    REPO_ROOT
    / 'cuda-train-data-analysis-v1'
    / 'proof_first_solver_factory_routing'
    / 'result'
    / 'phase0_offline_eval_binary_bias_specialized'
    / 'artifacts'
    / 'binary_bias_specialized_eval_row_level.csv'
)
DEFAULT_PHASE0_SOURCE_SET = (
    REPO_ROOT
    / 'baseline'
    / 'nemotron-sft-lora-with-cot-v2'
    / 'result'
    / 'v3f'
    / 'phase0_offline_eval'
    / 'artifacts'
    / 'phase0_combined_eval_set.csv'
)
DEFAULT_SPECIALIZED_SOURCE_SET = (
    REPO_ROOT
    / 'baseline'
    / 'nemotron-sft-lora-with-cot-v2'
    / 'result'
    / 'v3f'
    / 'phase0_offline_eval_binary_bias_specialized'
    / 'artifacts'
    / 'binary_bias_specialized_set.csv'
)
DEFAULT_OUTPUT_DATASET_CSV = ARTIFACTS_DIR / 'leaderboard_proxy_v1_set.csv'
DEFAULT_OUTPUT_SUMMARY_JSON = ARTIFACTS_DIR / 'leaderboard_proxy_v1_summary.json'
DEFAULT_OUTPUT_MODEL_COMPARISON_CSV = ARTIFACTS_DIR / 'leaderboard_proxy_v1_model_comparison.csv'
DEFAULT_OUTPUT_REPORT_MD = REPORTS_DIR / 'leaderboard_proxy_v1_report.md'

README_EVAL_CONTRACT = {
    'metric': 'Accuracy',
    'boxed_first_extraction': True,
    'temperature': 0.0,
    'top_p': 1.0,
    'max_tokens': 7680,
    'max_num_seqs': 64,
    'max_model_len': 8192,
    'max_lora_rank': 32,
}

BIT_RE = __import__('re').compile(r'^[01]+$')


@dataclass(frozen=True)
class Candidate:
    row: dict[str, Any]
    rank_key: tuple[Any, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            'Build a leaderboard proxy dataset from existing v3f/current local row-level outputs '
            'so that the proxy reproduces the observed leaderboard gap locally.'
        )
    )
    parser.add_argument('--mode', choices=('build', 'score'), default='build')
    parser.add_argument('--v3f-phase0-row-level', type=Path, default=DEFAULT_V3F_PHASE0_ROW_LEVEL)
    parser.add_argument('--current-phase0-row-level', type=Path, default=DEFAULT_CURRENT_PHASE0_ROW_LEVEL)
    parser.add_argument('--v3f-specialized-row-level', type=Path, default=DEFAULT_V3F_SPECIALIZED_ROW_LEVEL)
    parser.add_argument('--current-specialized-row-level', type=Path, default=DEFAULT_CURRENT_SPECIALIZED_ROW_LEVEL)
    parser.add_argument('--phase0-source-set', type=Path, default=DEFAULT_PHASE0_SOURCE_SET)
    parser.add_argument('--specialized-source-set', type=Path, default=DEFAULT_SPECIALIZED_SOURCE_SET)
    parser.add_argument('--output-dataset-csv', type=Path, default=DEFAULT_OUTPUT_DATASET_CSV)
    parser.add_argument('--output-summary-json', type=Path, default=DEFAULT_OUTPUT_SUMMARY_JSON)
    parser.add_argument('--output-model-comparison-csv', type=Path, default=DEFAULT_OUTPUT_MODEL_COMPARISON_CSV)
    parser.add_argument('--output-report-md', type=Path, default=DEFAULT_OUTPUT_REPORT_MD)
    parser.add_argument('--target-v3f', type=float, default=0.715)
    parser.add_argument('--target-current', type=float, default=0.56)
    parser.add_argument('--total-rows', type=int, default=200)
    parser.add_argument('--predictions-csv', type=Path)
    parser.add_argument('--dataset-csv', type=Path, default=DEFAULT_OUTPUT_DATASET_CSV)
    return parser.parse_args()


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f'CSV header is missing: {path}')
        return [dict(row) for row in reader]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, '') for key in fieldnames})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')


def parse_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value).strip()
        if not text:
            return default
        return int(float(text))
    except (TypeError, ValueError):
        return default


def parse_float(value: Any, default: float = 0.0) -> float:
    try:
        text = str(value).strip()
        if not text:
            return default
        return float(text)
    except (TypeError, ValueError):
        return default


def corrected_is_correct(gold: str, predicted: str) -> bool:
    gold_text = str(gold).strip()
    predicted_text = str(predicted).strip()
    if BIT_RE.fullmatch(gold_text):
        return predicted_text == gold_text
    try:
        return math.isclose(float(gold_text), float(predicted_text), rel_tol=1e-2, abs_tol=1e-5)
    except (TypeError, ValueError):
        return predicted_text.lower() == gold_text.lower()


def load_row_level(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in load_csv_rows(path):
        row['_corrected_is_correct'] = corrected_is_correct(row['gold_answer'], row['prediction'])
        rows[row['id']] = row
    return rows


def load_source_sets(phase0_path: Path, specialized_path: Path) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for source_name, path, source_split in (
        ('phase0_combined_eval_set', phase0_path, 'phase0'),
        ('binary_bias_specialized_set', specialized_path, 'specialized'),
    ):
        for row in load_csv_rows(path):
            payload = dict(row)
            payload['_source_name'] = source_name
            payload['_source_split'] = source_split
            if source_split == 'phase0':
                payload.setdefault('v1_focus_bucket', '')
                payload.setdefault('v1_exposure_band', '')
                payload.setdefault('v1_bucket_note', '')
            merged[row['id']] = payload
    return merged


def role_of(v3f_correct: bool, current_correct: bool) -> str:
    if v3f_correct and current_correct:
        return 'both_correct'
    if v3f_correct and not current_correct:
        return 'v3f_only'
    if current_correct and not v3f_correct:
        return 'current_only'
    return 'both_wrong'


def focus_key(row: dict[str, Any]) -> str:
    value = str(row.get('v1_focus_bucket', '')).strip()
    if value:
        return value
    family_short = str(row.get('family_short', '')).strip() or str(row.get('family', '')).strip()
    subtype = str(row.get('template_subtype', '')).strip()
    if family_short and subtype:
        return f'{family_short}:{subtype}'
    return family_short or 'unknown'


def source_priority(row: dict[str, Any]) -> int:
    role = row['proxy_role']
    focus = str(row.get('v1_focus_bucket', '')).strip()
    family_short = str(row.get('family_short', '')).strip()
    template_subtype = str(row.get('template_subtype', '')).strip()
    solver = str(row.get('teacher_solver_candidate', '')).strip()
    if role == 'v3f_only':
        priorities = {
            'supported_bijection': 200,
            'dominant_structured_safe': 190,
            'supported_affine_xor': 180,
            'boolean_family': 170,
            'dominant_structured_abstract': 160,
            'no_solver_answer_only': 150,
            'no_solver_manual': 140,
            'rare_perm_independent': 130,
            'rare_byte_transform': 120,
        }
        return priorities.get(focus, 20 if family_short == 'binary' else 10)
    if role == 'both_correct':
        if family_short == 'gravity':
            return 200
        if family_short == 'roman':
            return 198
        if family_short == 'unit':
            return 196
        if family_short == 'text':
            return 194
        priorities = {
            'supported_bijection': 190,
            'dominant_structured_safe': 188,
            'supported_affine_xor': 186,
            'boolean_family': 184,
            'dominant_structured_abstract': 182,
            'rare_perm_independent': 180,
            'rare_byte_transform': 178,
            'no_solver_answer_only': 170,
            'numeric_2x2': 160,
        }
        return priorities.get(focus, 80 if family_short == 'symbol' else 60)
    if role == 'both_wrong':
        priorities = {
            'supported_not_structured': 220,
            'no_solver_manual': 210,
            'no_solver_answer_only': 200,
            'dominant_structured_abstract': 190,
            'boolean_family': 180,
            'supported_affine_xor': 170,
            'supported_bijection': 160,
            'dominant_structured_safe': 150,
            'glyph_len5': 140,
            'numeric_2x2': 130,
        }
        return priorities.get(focus, 120 if family_short == 'binary' else 100)
    return 0


def rank_candidate(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -source_priority(row),
        -parse_float(row.get('hard_score', 0.0), 0.0),
        -parse_int(row.get('prompt_len_chars', 0), 0),
        -parse_int(row.get('num_examples', 0), 0),
        str(row.get('id', '')),
    )


def make_candidates(rows: list[dict[str, Any]]) -> list[Candidate]:
    return [Candidate(row=row, rank_key=rank_candidate(row)) for row in rows]


def round_robin_select(
    candidates: list[Candidate],
    quota: int,
    key_fn: Callable[[Candidate], str],
) -> list[dict[str, Any]]:
    if quota <= 0:
        return []
    ordered = sorted(candidates, key=lambda item: item.rank_key)
    if len(ordered) < quota:
        raise RuntimeError(f'quota={quota} cannot be satisfied; only {len(ordered)} candidates available')
    groups: dict[str, list[Candidate]] = defaultdict(list)
    for candidate in ordered:
        groups[key_fn(candidate)].append(candidate)
    group_order = sorted(groups)
    queues = {name: deque(groups[name]) for name in group_order}
    selected: list[dict[str, Any]] = []
    while len(selected) < quota and queues:
        for group_name in list(group_order):
            queue = queues.get(group_name)
            if not queue:
                continue
            selected.append(queue.popleft().row)
            if not queue:
                queues.pop(group_name, None)
            if len(selected) >= quota:
                break
        group_order = [group_name for group_name in group_order if group_name in queues]
    if len(selected) != quota:
        raise RuntimeError(f'quota={quota} was not filled; selected={len(selected)}')
    return selected


def desired_role_counts(total_rows: int, target_v3f: float, target_current: float) -> dict[str, int]:
    v3f_correct = round(target_v3f * total_rows)
    current_correct = round(target_current * total_rows)
    if abs((v3f_correct / total_rows) - target_v3f) > 1e-9:
        raise ValueError('target_v3f * total_rows must be an integer with the current defaults')
    if abs((current_correct / total_rows) - target_current) > 1e-9:
        raise ValueError('target_current * total_rows must be an integer with the current defaults')
    counts = {
        'both_correct': current_correct,
        'v3f_only': v3f_correct - current_correct,
        'current_only': 0,
        'both_wrong': total_rows - v3f_correct,
    }
    if counts['v3f_only'] < 0 or counts['both_wrong'] < 0:
        raise ValueError('invalid target pair for the given total_rows')
    return counts


def build_proxy_rows(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_rows = load_source_sets(args.phase0_source_set, args.specialized_source_set)
    v3f_rows = {}
    v3f_rows.update(load_row_level(args.v3f_phase0_row_level))
    v3f_rows.update(load_row_level(args.v3f_specialized_row_level))
    current_rows = {}
    current_rows.update(load_row_level(args.current_phase0_row_level))
    current_rows.update(load_row_level(args.current_specialized_row_level))

    joined: list[dict[str, Any]] = []
    for row_id, source in source_rows.items():
        if row_id not in v3f_rows or row_id not in current_rows:
            continue
        v3f_row = v3f_rows[row_id]
        current_row = current_rows[row_id]
        row = dict(source)
        row['gold_answer'] = source.get('answer', '')
        row['v3f_prediction'] = v3f_row['prediction']
        row['current_prediction'] = current_row['prediction']
        row['v3f_is_correct'] = v3f_row['_corrected_is_correct']
        row['current_is_correct'] = current_row['_corrected_is_correct']
        row['proxy_role'] = role_of(v3f_row['_corrected_is_correct'], current_row['_corrected_is_correct'])
        joined.append(row)

    counts = desired_role_counts(args.total_rows, args.target_v3f, args.target_current)
    pools: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in joined:
        pools[row['proxy_role']].append(row)

    selected: list[dict[str, Any]] = []
    for role_name in ('v3f_only', 'both_correct', 'both_wrong'):
        candidates = make_candidates(pools[role_name])
        if role_name == 'both_correct':
            key_fn = lambda candidate: f"{candidate.row.get('_source_split', '')}:{candidate.row.get('family_short', '')}" or 'unknown'
        else:
            key_fn = lambda candidate: focus_key(candidate.row)
        picked = round_robin_select(candidates, counts[role_name], key_fn=key_fn)
        selected.extend(picked)

    selected.sort(
        key=lambda row: (
            {'v3f_only': 0, 'both_correct': 1, 'both_wrong': 2}.get(row['proxy_role'], 9),
            row.get('_source_split', ''),
            focus_key(row),
            -parse_float(row.get('hard_score', 0.0), 0.0),
            row.get('id', ''),
        )
    )
    for index, row in enumerate(selected, start=1):
        row['benchmark_name'] = 'leaderboard_proxy_v1_set'
        row['benchmark_role'] = 'leaderboard_proxy'
        row['benchmark_index'] = index
        row['leaderboard_proxy_bucket'] = focus_key(row)
        row['leaderboard_proxy_note'] = {
            'v3f_only': 'Rows where v3f is correct and current is wrong; concentrates suspected hidden-regression slices.',
            'both_correct': 'Rows both models solve; calibrates proxy topline upward without collapsing the gap.',
            'both_wrong': 'Rows both models miss; approximates hidden hard tail not captured by local320.',
        }[row['proxy_role']]

    summary = summarize_proxy(selected, counts)
    return selected, summary


def summarize_proxy(rows: list[dict[str, Any]], role_targets: dict[str, int]) -> dict[str, Any]:
    v3f_correct = sum(1 for row in rows if row['v3f_is_correct'])
    current_correct = sum(1 for row in rows if row['current_is_correct'])
    total = len(rows)
    by_role = Counter(str(row['proxy_role']) for row in rows)
    by_source = Counter(str(row.get('_source_split', '')) for row in rows)
    by_bucket = Counter(str(row.get('leaderboard_proxy_bucket', focus_key(row))) for row in rows)
    by_family = Counter(str(row.get('family_short', '')) for row in rows)
    return {
        'readme_eval_contract': README_EVAL_CONTRACT,
        'total_rows': total,
        'role_targets': role_targets,
        'selected_role_counts': dict(by_role),
        'selected_source_split_counts': dict(by_source),
        'selected_family_counts': dict(by_family),
        'selected_bucket_counts': dict(by_bucket),
        'proxy_scores': {
            'v3f': {
                'correct': v3f_correct,
                'rows': total,
                'accuracy': round(v3f_correct / total, 4),
            },
            'current': {
                'correct': current_correct,
                'rows': total,
                'accuracy': round(current_correct / total, 4),
            },
        },
    }


def dataset_fieldnames() -> list[str]:
    return [
        'benchmark_name',
        'benchmark_role',
        'benchmark_index',
        'id',
        'prompt',
        'answer',
        'family',
        'family_short',
        'template_subtype',
        'selection_tier',
        'teacher_solver_candidate',
        'answer_type',
        'num_examples',
        'prompt_len_chars',
        'hard_score',
        'group_signature',
        'query_raw',
        'v1_focus_bucket',
        'v1_exposure_band',
        'v1_bucket_note',
        'bit_structured_formula_name',
        'bit_structured_formula_abstract_family',
        'bit_not_structured_formula_name',
        'bit_structured_formula_safe_support',
        'bit_structured_formula_abstract_support',
        'bit_not_structured_formula_safe_support',
        'bit_no_candidate_positions',
        'bit_multi_candidate_positions',
        'query_hamming_bin',
        'audit_priority_score',
        '_source_name',
        '_source_split',
        'proxy_role',
        'leaderboard_proxy_bucket',
        'leaderboard_proxy_note',
        'v3f_prediction',
        'current_prediction',
        'v3f_is_correct',
        'current_is_correct',
    ]


def model_comparison_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        output.append(
            {
                'benchmark_index': row['benchmark_index'],
                'id': row['id'],
                'source_split': row['_source_split'],
                'proxy_role': row['proxy_role'],
                'leaderboard_proxy_bucket': row['leaderboard_proxy_bucket'],
                'family_short': row['family_short'],
                'template_subtype': row['template_subtype'],
                'selection_tier': row['selection_tier'],
                'teacher_solver_candidate': row['teacher_solver_candidate'],
                'gold_answer': row['answer'],
                'v3f_prediction': row['v3f_prediction'],
                'v3f_is_correct': row['v3f_is_correct'],
                'current_prediction': row['current_prediction'],
                'current_is_correct': row['current_is_correct'],
            }
        )
    return output


def render_report(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Leaderboard Proxy V1 Report')
    lines.append('')
    lines.append('## 1. Purpose')
    lines.append('')
    lines.append(
        'This proxy dataset is an engineered local benchmark built from existing Phase0 and specialized row-level outputs. '
        'It is not claimed to be the real leaderboard hidden half. Its purpose is narrower: reproduce the observed rank-order gap '
        'between v3f and the current proof-first route-aware run using a repository-tracked local score.'
    )
    lines.append('')
    lines.append('## 2. README-Aligned Constraints')
    lines.append('')
    lines.append('- metric: Accuracy')
    lines.append('- boxed-first extraction: True')
    lines.append('- temperature: 0.0')
    lines.append('- final artifact target: single submit-compatible LoRA in submission.zip')
    lines.append('')
    lines.append('## 3. Proxy Construction Rule')
    lines.append('')
    lines.append('The dataset is built from three disjoint row roles:')
    lines.append('')
    lines.append('- v3f_only: rows where v3f is correct and current is wrong')
    lines.append('- both_correct: rows where both models are correct')
    lines.append('- both_wrong: rows where both models are wrong')
    lines.append('')
    lines.append('Current-only rows are intentionally excluded so the proxy preserves the observed leaderboard ordering.')
    lines.append('')
    lines.append('## 4. Selected Counts')
    lines.append('')
    lines.append('| role | rows |')
    lines.append('| --- | ---: |')
    for role_name, rows in summary['selected_role_counts'].items():
        lines.append(f'| `{role_name}` | {rows} |')
    lines.append('')
    lines.append('| source_split | rows |')
    lines.append('| --- | ---: |')
    for source_name, rows in sorted(summary['selected_source_split_counts'].items()):
        lines.append(f'| `{source_name}` | {rows} |')
    lines.append('')
    lines.append('| family_short | rows |')
    lines.append('| --- | ---: |')
    for family_short, rows in sorted(summary['selected_family_counts'].items()):
        lines.append(f'| `{family_short}` | {rows} |')
    lines.append('')
    lines.append('| leaderboard_proxy_bucket | rows |')
    lines.append('| --- | ---: |')
    for bucket_name, rows in sorted(summary['selected_bucket_counts'].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f'| `{bucket_name}` | {rows} |')
    lines.append('')
    lines.append('## 5. Measured Proxy Scores')
    lines.append('')
    lines.append('| run | correct / rows | accuracy |')
    lines.append('| --- | ---: | ---: |')
    for run_name in ('v3f', 'current'):
        score = summary['proxy_scores'][run_name]
        lines.append(f"| `{run_name}` | `{score['correct']} / {score['rows']}` | `{score['accuracy']:.4f}` |")
    lines.append('')
    lines.append('## 6. Interpretation')
    lines.append('')
    lines.append(
        'If a future candidate beats the current route-aware run on this proxy while preserving Phase0 corrected accuracy, '
        'it is a stronger submit candidate than one that only improves local320 or specialized563.'
    )
    lines.append('')
    return '\n'.join(lines) + '\n'


def build_proxy(args: argparse.Namespace) -> None:
    rows, summary = build_proxy_rows(args)
    write_csv(args.output_dataset_csv, rows, dataset_fieldnames())
    write_csv(
        args.output_model_comparison_csv,
        model_comparison_rows(rows),
        [
            'benchmark_index',
            'id',
            'source_split',
            'proxy_role',
            'leaderboard_proxy_bucket',
            'family_short',
            'template_subtype',
            'selection_tier',
            'teacher_solver_candidate',
            'gold_answer',
            'v3f_prediction',
            'v3f_is_correct',
            'current_prediction',
            'current_is_correct',
        ],
    )
    write_json(args.output_summary_json, summary)
    args.output_report_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_report_md.write_text(render_report(summary), encoding='utf-8')
    print(f'wrote {args.output_dataset_csv}')
    print(f"proxy score v3f={summary['proxy_scores']['v3f']['accuracy']:.4f} current={summary['proxy_scores']['current']['accuracy']:.4f}")


def load_dataset_by_id(path: Path) -> dict[str, dict[str, str]]:
    return {row['id']: row for row in load_csv_rows(path)}


def score_proxy(args: argparse.Namespace) -> None:
    if args.predictions_csv is None:
        raise ValueError('--predictions-csv is required in score mode')
    dataset = load_dataset_by_id(args.dataset_csv)
    predictions = load_csv_rows(args.predictions_csv)
    found = 0
    correct = 0
    missing: list[str] = []
    for row_id, dataset_row in dataset.items():
        match_row = next((row for row in predictions if row.get('id') == row_id), None)
        if match_row is None:
            missing.append(row_id)
            continue
        found += 1
        gold = dataset_row['answer']
        prediction = match_row.get('prediction', match_row.get('extracted_answer', ''))
        if corrected_is_correct(gold, prediction):
            correct += 1
    accuracy = correct / len(dataset)
    payload = {
        'rows': len(dataset),
        'predictions_found': found,
        'missing_predictions': len(missing),
        'correct': correct,
        'accuracy': round(accuracy, 4),
        'missing_ids_preview': missing[:10],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))


def main() -> None:
    args = parse_args()
    if args.mode == 'build':
        build_proxy(args)
        return
    score_proxy(args)


if __name__ == '__main__':
    main()