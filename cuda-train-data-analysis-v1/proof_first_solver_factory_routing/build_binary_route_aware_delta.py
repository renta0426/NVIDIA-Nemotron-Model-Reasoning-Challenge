from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import random
import sys
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
ARTIFACTS_DIR = PLAN_ROOT / 'artifacts'

DEFAULT_ANALYSIS_CSV = REPO_ROOT / 'cuda-train-data-analysis-v1' / 'artifacts' / 'train_row_analysis_v1.csv'
DEFAULT_BASE_DATASET_CSV = REPO_ROOT / 'baseline' / 'nemotron-sft-lora-with-cot-v2' / 'artifacts' / 'train_split_with_cot_v2.csv'
DEFAULT_HELPER_MODULE = (
    REPO_ROOT
    / 'cuda-train-data-analysis-v1'
    / 'bit_synth_exact_trace_cot_v1_1'
    / 'generate_bit_synth_exact_trace_cot_v1_1.py'
)
DEFAULT_DELTA_CSV = ARTIFACTS_DIR / 'binary_route_aware_delta.csv'
DEFAULT_MERGED_CSV = ARTIFACTS_DIR / 'train_split_with_cot_v2_plus_binary_route_aware.csv'
DEFAULT_MANIFEST_JSON = ARTIFACTS_DIR / 'binary_route_aware_delta_manifest.json'

README_EVAL_CONTRACT = {
    'metric': 'Accuracy',
    'answer_extraction': 'prioritize \\boxed{} content',
    'temperature': 0.0,
    'max_tokens': 7680,
    'max_lora_rank': 32,
    'max_model_len': 8192,
}

EXACT_SOLVER_ALLOWLIST = {
    'binary_structured_byte_formula',
    'binary_structured_byte_formula_abstract',
    'binary_structured_byte_not_formula',
    'binary_affine_xor',
    'binary_two_bit_boolean',
    'binary_three_bit_boolean',
    'binary_byte_transform',
    'binary_bit_permutation_bijection',
    'binary_bit_permutation_independent',
}

ANSWER_ONLY_ANALYSIS_ALLOWLIST = {
    'bit_prompt_local_current_consensus_answer_only',
    'bit_prompt_local_nested_support3_or_abstract_answer_only',
    'bit_prompt_local_extended_support3_answer_only',
}

CORE_OUTPUT_COLUMNS = ['id', 'prompt', 'answer', 'type', 'generated_cot']
DELTA_OUTPUT_COLUMNS = CORE_OUTPUT_COLUMNS + [
    'route_label',
    'route_granularity',
    'assistant_style',
    'source_selection_tier',
    'analysis_notes',
    'teacher_solver_candidate',
    'template_subtype',
    'num_examples',
    'source_dataset',
]


@dataclass(frozen=True)
class SelectedRow:
    row: dict[str, str]
    rank_key: tuple[Any, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            'Build a route-aware binary delta on top of train_split_with_cot_v2.csv using only '
            'binary verified exact-route rows and bounded answer-only rescue rows.'
        )
    )
    parser.add_argument('--mode', choices=('build', 'preview'), default='build')
    parser.add_argument('--analysis-csv', type=Path, default=DEFAULT_ANALYSIS_CSV)
    parser.add_argument('--base-dataset-csv', type=Path, default=DEFAULT_BASE_DATASET_CSV)
    parser.add_argument('--helper-module', type=Path, default=DEFAULT_HELPER_MODULE)
    parser.add_argument('--delta-csv', type=Path, default=DEFAULT_DELTA_CSV)
    parser.add_argument('--merged-csv', type=Path, default=DEFAULT_MERGED_CSV)
    parser.add_argument('--manifest-json', type=Path, default=DEFAULT_MANIFEST_JSON)
    parser.add_argument('--seed', type=int, default=20260407)
    parser.add_argument('--exact-quota', type=int, default=240)
    parser.add_argument('--answer-only-quota', type=int, default=80)
    parser.add_argument('--preview-rows', type=int, default=5)
    return parser.parse_args()


def load_module(module_path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Failed to import module from {module_path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


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


def solver_priority(row: dict[str, str]) -> int:
    priorities = {
        'binary_structured_byte_formula': 100,
        'binary_structured_byte_formula_abstract': 98,
        'binary_structured_byte_not_formula': 96,
        'binary_affine_xor': 94,
        'binary_two_bit_boolean': 92,
        'binary_three_bit_boolean': 90,
        'binary_bit_permutation_bijection': 88,
        'binary_bit_permutation_independent': 86,
        'binary_byte_transform': 84,
    }
    return priorities.get(row.get('teacher_solver_candidate', ''), 0)


def answer_only_priority(row: dict[str, str]) -> int:
    priorities = {
        'bit_prompt_local_current_consensus_answer_only': 100,
        'bit_prompt_local_nested_support3_or_abstract_answer_only': 94,
        'bit_prompt_local_extended_support3_answer_only': 88,
    }
    return priorities.get(row.get('analysis_notes', ''), 0)


def rank_exact_row(row: dict[str, str]) -> tuple[Any, ...]:
    return (
        -solver_priority(row),
        -parse_int(row.get('num_examples', '0'), 0),
        parse_float(row.get('audit_priority_score', '0'), 0.0),
        row.get('id', ''),
    )


def rank_answer_only_row(row: dict[str, str]) -> tuple[Any, ...]:
    return (
        -answer_only_priority(row),
        -parse_int(row.get('num_examples', '0'), 0),
        parse_float(row.get('audit_priority_score', '0'), 0.0),
        row.get('id', ''),
    )


def make_selected(rows: list[dict[str, str]], ranker: Callable[[dict[str, str]], tuple[Any, ...]]) -> list[SelectedRow]:
    return [SelectedRow(row=row, rank_key=ranker(row)) for row in rows]


def round_robin_select(
    items: list[SelectedRow],
    quota: int,
    seed: int,
    key_fn: Callable[[SelectedRow], str],
) -> list[dict[str, str]]:
    if quota <= 0:
        return []
    sorted_items = sorted(items, key=lambda item: item.rank_key)
    if len(sorted_items) <= quota:
        return [item.row for item in sorted_items]
    groups: dict[str, list[SelectedRow]] = defaultdict(list)
    for item in sorted_items:
        groups[key_fn(item)].append(item)
    order = sorted(groups)
    random.Random(seed).shuffle(order)
    queues = {group_name: deque(groups[group_name]) for group_name in order}
    selected: list[dict[str, str]] = []
    while len(selected) < quota and queues:
        for group_name in list(order):
            queue = queues.get(group_name)
            if not queue:
                continue
            selected.append(queue.popleft().row)
            if not queue:
                queues.pop(group_name, None)
            if len(selected) >= quota:
                break
        order = [group_name for group_name in order if group_name in queues]
    return selected


def inject_route_lines(generated_cot: str, route_label: str, route_granularity: str) -> str:
    prefix = f'<think>\nRoute: {route_label}\nRoute granularity: {route_granularity}'
    if generated_cot.startswith('<think>\n'):
        return generated_cot.replace('<think>\n', prefix + '\n', 1)
    if generated_cot.startswith('<think>'):
        return generated_cot.replace('<think>', prefix, 1)
    return prefix + '\n' + generated_cot


def build_answer_only_cot(route_label: str) -> str:
    lines = [
        '<think>',
        f'Route: {route_label}',
        'Route granularity: coarse',
        'Use the same hidden bit rule that is consistent with the given examples.',
        'Apply it to the query byte and keep the exact 8-bit output with leading zeros for the final box only.',
        'Constraints: exact_8bit, leading_zeros, box_only_final.',
        '</think>',
    ]
    return '\n'.join(lines)


def build_sanitized_exact_cot(
    helper_module: Any,
    analysis_module: Any,
    seed_config: Any,
    support_examples: list[tuple[str, str]],
    query_bits: str,
    answer: str,
) -> str:
    _, rule_lines, query_lines = helper_module.render_trace_segments(
        analysis_module,
        seed_config.strong_group,
        seed_config.exact_rule,
        seed_config.rule_payload,
        support_examples,
        query_bits,
    )
    lines = [
        '<think>',
        'Check ex1 and ex2: the same exact rule is verified.',
    ]
    for line in rule_lines:
        if answer not in line:
            lines.append(line)
    for line in query_lines:
        if line.startswith('Query x = '):
            break
        if answer not in line:
            lines.append(line)
    lines.append('Apply the exact rule to the query byte and keep the resulting 8-bit output for the final box only.')
    lines.append('Constraints: exact_8bit, leading_zeros, box_only_final.')
    lines.append('</think>')
    return '\n'.join(lines)


def validate_sanitized_exact_cot(
    helper_module: Any,
    analysis_module: Any,
    seed_config: Any,
    query_bits: str,
    answer: str,
    generated_cot: str,
) -> tuple[bool, str]:
    if not generated_cot.startswith('<think>') or not generated_cot.endswith('</think>'):
        return False, 'bad_think_wrapper'
    if answer in generated_cot:
        return False, 'answer_leak_in_generated_cot'
    teacher_response = f'{generated_cot}\n\n\\boxed{{{answer}}}'
    if helper_module.count_non_empty_boxed(teacher_response) != 1:
        return False, 'bad_boxed_count'
    if not teacher_response.rstrip().endswith(f'\\boxed{{{answer}}}'):
        return False, 'final_box_not_terminal'
    if helper_module.extract_final_answer(teacher_response) != answer:
        return False, 'metric_extraction_mismatch'
    if helper_module.apply_seed_rule(analysis_module, seed_config, query_bits) != answer:
        return False, 'forward_answer_mismatch'
    return True, 'accepted'


def normalize_exact_row(
    row: dict[str, str],
    helper_module: Any,
    analysis_module: Any,
    seed_config: Any,
) -> tuple[dict[str, Any] | None, str]:
    prompt = row['prompt']
    answer = row['answer']
    examples, query_bits = helper_module.parse_binary_prompt(prompt)
    if not examples:
        return None, 'parse_binary_prompt_failed'
    support_examples = examples[:2]
    canonical_cot = helper_module.render_generated_cot(
        analysis_module,
        'trace_boxed_full',
        seed_config.strong_group,
        seed_config.exact_rule,
        seed_config.rule_payload,
        support_examples,
        query_bits,
        answer,
    )
    ok, reason = helper_module.validate_seed_row(
        analysis_module,
        seed_config,
        'trace_boxed_full',
        prompt,
        examples,
        support_examples,
        query_bits,
        answer,
        canonical_cot,
        set(),
    )
    assistant_style = 'route_trace_full'
    normalized_cot = canonical_cot
    if not ok and reason == 'answer_leak_in_generated_cot':
        sanitized_cot = build_sanitized_exact_cot(
            helper_module,
            analysis_module,
            seed_config,
            support_examples,
            query_bits,
            answer,
        )
        ok, reason = validate_sanitized_exact_cot(
            helper_module,
            analysis_module,
            seed_config,
            query_bits,
            answer,
            sanitized_cot,
        )
        if ok:
            normalized_cot = sanitized_cot
            assistant_style = 'route_trace_sanitized'
    if not ok:
        return None, reason
    routed_cot = inject_route_lines(
        normalized_cot,
        route_label=f'bit_manipulation.{seed_config.strong_group}',
        route_granularity='exact',
    )
    if answer in routed_cot:
        return None, 'answer_leak_after_route_injection'
    return {
        'id': row['id'],
        'prompt': prompt,
        'answer': answer,
        'type': 'Bit Manipulation',
        'generated_cot': routed_cot,
        'route_label': f'bit_manipulation.{seed_config.strong_group}',
        'route_granularity': 'exact',
        'assistant_style': assistant_style,
        'source_selection_tier': row['selection_tier'],
        'analysis_notes': row.get('analysis_notes', ''),
        'teacher_solver_candidate': row.get('teacher_solver_candidate', ''),
        'template_subtype': row.get('template_subtype', ''),
        'num_examples': row.get('num_examples', ''),
        'source_dataset': 'train_row_analysis_v1.csv',
    }, 'accepted'


def normalize_answer_only_row(row: dict[str, str], helper_module: Any) -> tuple[dict[str, Any] | None, str]:
    prompt = row['prompt']
    answer = row['answer']
    try:
        helper_module.parse_binary_prompt(prompt)
    except Exception:
        return None, 'parse_binary_prompt_failed'
    generated_cot = build_answer_only_cot('bit_manipulation')
    if answer in generated_cot:
        return None, 'answer_leak_in_answer_only_cot'
    return {
        'id': row['id'],
        'prompt': prompt,
        'answer': answer,
        'type': 'Bit Manipulation',
        'generated_cot': generated_cot,
        'route_label': 'bit_manipulation',
        'route_granularity': 'coarse',
        'assistant_style': 'route_closure_only',
        'source_selection_tier': row['selection_tier'],
        'analysis_notes': row.get('analysis_notes', ''),
        'teacher_solver_candidate': row.get('teacher_solver_candidate', ''),
        'template_subtype': row.get('template_subtype', ''),
        'num_examples': row.get('num_examples', ''),
        'source_dataset': 'train_row_analysis_v1.csv',
    }, 'accepted'


def build_delta(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    helper_module = load_module(args.helper_module, 'bit_synth_exact_trace_cot_v1_1_helper')
    analysis_module = helper_module.load_module(helper_module.ANALYSIS_MODULE)

    source_rows = load_csv_rows(args.analysis_csv)
    base_rows = load_csv_rows(args.base_dataset_csv)
    blocked_ids = {row['id'] for row in base_rows if row.get('id')}

    seed_configs = {config.seed_row_id: config for config in helper_module.build_seed_configs(analysis_module)}

    exact_candidates = [
        row
        for row in source_rows
        if row.get('family') == 'bit_manipulation'
        and row.get('selection_tier') == 'verified_trace_ready'
        and row.get('teacher_solver_candidate') in EXACT_SOLVER_ALLOWLIST
        and row.get('id') not in blocked_ids
        and row.get('id') in seed_configs
    ]
    answer_only_candidates = [
        row
        for row in source_rows
        if row.get('family') == 'bit_manipulation'
        and row.get('selection_tier') == 'answer_only_keep'
        and row.get('analysis_notes') in ANSWER_ONLY_ANALYSIS_ALLOWLIST
        and row.get('id') not in blocked_ids
    ]

    selected_exact_rows = round_robin_select(
        make_selected(exact_candidates, rank_exact_row),
        args.exact_quota,
        args.seed,
        key_fn=lambda item: item.row.get('teacher_solver_candidate', 'unknown'),
    )
    selected_answer_only_rows = round_robin_select(
        make_selected(answer_only_candidates, rank_answer_only_row),
        args.answer_only_quota,
        args.seed + 1,
        key_fn=lambda item: item.row.get('analysis_notes', 'unknown'),
    )

    delta_rows: list[dict[str, Any]] = []
    rejected_reasons = Counter()

    for row in selected_exact_rows:
        normalized, reason = normalize_exact_row(row, helper_module, analysis_module, seed_configs[row['id']])
        if normalized is None:
            rejected_reasons[reason] += 1
            continue
        delta_rows.append(normalized)

    for row in selected_answer_only_rows:
        normalized, reason = normalize_answer_only_row(row, helper_module)
        if normalized is None:
            rejected_reasons[reason] += 1
            continue
        delta_rows.append(normalized)

    delta_rows.sort(key=lambda row: (row['route_granularity'], row['route_label'], row['id']))

    manifest = {
        'created_from': str(args.analysis_csv),
        'base_dataset_csv': str(args.base_dataset_csv),
        'helper_module': str(args.helper_module),
        'artifacts_dir': str(ARTIFACTS_DIR),
        'readme_eval_contract': README_EVAL_CONTRACT,
        'seed': args.seed,
        'requested_exact_quota': args.exact_quota,
        'requested_answer_only_quota': args.answer_only_quota,
        'available_exact_candidates': len(exact_candidates),
        'available_answer_only_candidates': len(answer_only_candidates),
        'selected_exact_before_validation': len(selected_exact_rows),
        'selected_answer_only_before_validation': len(selected_answer_only_rows),
        'accepted_delta_rows': len(delta_rows),
        'accepted_exact_rows': sum(1 for row in delta_rows if row['route_granularity'] == 'exact'),
        'accepted_answer_only_rows': sum(1 for row in delta_rows if row['route_granularity'] == 'coarse'),
        'route_label_counts': dict(Counter(row['route_label'] for row in delta_rows)),
        'assistant_style_counts': dict(Counter(row['assistant_style'] for row in delta_rows)),
        'analysis_notes_counts': dict(Counter(row['analysis_notes'] for row in delta_rows)),
        'template_subtype_counts': dict(Counter(row['template_subtype'] for row in delta_rows)),
        'rejected_reasons': dict(rejected_reasons),
        'notes': [
            'Implementation files and generated artifacts stay under proof_first_solver_factory_routing.',
            'Exact-route rows use verified_trace_ready plus canonical rule recovery from the existing bit_synth exact-trace helper.',
            'If the canonical exact trace repeats the final answer inside <think>, a sanitized exact-rule trace is emitted instead.',
            'Answer-only rows stay coarse-route only and intentionally avoid plain-text final answer leakage in generated_cot.',
            'The merged CSV keeps the baseline v2 5-column schema so the existing notebook path remains usable.',
        ],
    }
    return delta_rows, manifest


def build_merged_rows(base_rows: list[dict[str, str]], delta_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged_rows: list[dict[str, Any]] = []
    for row in base_rows:
        merged_rows.append({key: row.get(key, '') for key in CORE_OUTPUT_COLUMNS})
    for row in delta_rows:
        merged_rows.append({key: row.get(key, '') for key in CORE_OUTPUT_COLUMNS})
    return merged_rows


def preview_rows(rows: list[dict[str, Any]], limit: int) -> None:
    for row in rows[:limit]:
        print(f"[{row['route_granularity']}] {row['id']} {row['route_label']} {row['analysis_notes']}")


def main() -> None:
    args = parse_args()
    delta_rows, manifest = build_delta(args)
    base_rows = load_csv_rows(args.base_dataset_csv)
    merged_rows = build_merged_rows(base_rows, delta_rows)

    if args.mode == 'preview':
        print(json.dumps(manifest, indent=2, ensure_ascii=True))
        preview_rows(delta_rows, args.preview_rows)
        return

    write_csv(args.delta_csv, delta_rows, DELTA_OUTPUT_COLUMNS)
    write_csv(args.merged_csv, merged_rows, CORE_OUTPUT_COLUMNS)
    manifest['delta_csv'] = str(args.delta_csv)
    manifest['merged_csv'] = str(args.merged_csv)
    manifest['base_rows'] = len(base_rows)
    manifest['merged_rows'] = len(merged_rows)
    write_json(args.manifest_json, manifest)

    print(f'Wrote delta CSV: {args.delta_csv}')
    print(f'Wrote merged CSV: {args.merged_csv}')
    print(f'Wrote manifest: {args.manifest_json}')
    print(f'Accepted delta rows: {len(delta_rows)}')


if __name__ == '__main__':
    main()