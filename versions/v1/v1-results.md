# V1 Results

## Source of truth

この `v1` 系列のローカル判定も **`README.md` の Evaluation 節**を唯一の基準にする。

- `max_lora_rank = 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `max_model_len = 8192`

metric は **`\boxed{}` 優先抽出 → heuristic fallback → last numeric fallback** を使う。

## Reproduced prompt-router-v6 bundle

- single-file main: `mac_workspace/v1/phase2_binary_dsl_mlx_v1.py`
- local reference bundle: `mac_workspace/v1/reference/`
  - `baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_hybrid_training_data.csv`
  - `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv`
  - `baseline/cot/phase0_offline_eval/artifacts/*`
  - `baseline/cot/phase2_1_2_merge_lora/artifacts/phase2_1_2_binary_specialist_training_data.csv`
  - `baseline/cot/phase2_2_merge_lora/artifacts/phase2_2_symbol_specialist_training_data.csv`
  - `cuda-train-data-analysis-v1/artifacts/` の prompt-local / symbol solver / benchmark build に必要な CSV 群
- reproduced eval outputs: `mac_workspace/v1/outputs/eval_prompt_router_v6_repro/`

## Submission compatibility

> 重要: `prompt-router-v6-repro` は **single-file multi-adapter local pipeline** の再現であり、README の Submitting 節が要求する **「1 つの rank<=32 LoRA adapter を `submission.zip` に入れて提出する形」** をそのまま満たすものではない。  
> `v1` で再現したのは **local best pipeline** であって、**submission-compatible single adapter** ではない。

## Current best local pipeline

| pipeline | local320 | gate24 | binary | gravity | roman | symbol | text | unit | note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `prompt-router-v6-repro` | **293/320 = 0.9156** | **24/24 = 1.0000** | `54/60` | `50/50` | `50/50` | `39/60` | `50/50` | `50/50` | `v1` single-file + local reference bundle から actual rerun で `v0` score を再現 |

補足:

- `v1` rerun は `v0` の 3 adapter を入力として使い、**`v0` actual と完全一致**した。
  - general: `mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_resume_v10_to_full_fusion_v40_lr1p25e6_ep0125/adapter`
  - reasoning: `mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_text_run3_lr2e5_top8_bs16ga1/adapter`
  - specialist: `mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_focus_v1_text_full_bs16ga1/adapter`
- full320 fallback は **47 行すべて solver**
  - `binary_formula_consensus_solver = 35`
  - `symbol_numeric_zero_error_solver = 12`
- binary は **`54/60`**、内訳は `bit_other = 40/46`, `bit_structured_byte_formula = 14/14`
- symbol は `numeric_2x2 = 39/40`, `glyph_len5 = 0/20`
- artifact source of truth:
  - `mac_workspace/v1/outputs/eval_prompt_router_v6_repro/gate24/phase0_offline_eval/artifacts/phase0_eval_summary.json`
  - `mac_workspace/v1/outputs/eval_prompt_router_v6_repro/full320_shard2/phase0_offline_eval/artifacts/phase0_eval_summary.json`

## Submission-compatible single-adapter track

README の提出要件を満たす本命は、**single adapter 1 本**で local score を上げること。  
`v1` ではまず、`v0` の `v110` general-support mix を土台にしつつ、`prompt-router-v6` の gain 源に近い **`bit_other` prompt-local consensus** を teacher row として追加する枝から再開した。

重要な切り分け:

- `binary_prompt_local_current_consensus_candidates_v1.csv` の **`bit_other + answer_only_keep` 52 行は、すべて現行 900-row phase2 train CSV と重複**していた
- したがって今回の新規 signal は **`bit_other + manual_audit_priority`** が中心
- first batch は `v110` adapter からの top8 continuation (`lr=1.25e-6`, `epoch=0.25`, `dataset_format=text`) で揃える

### v119-v122 prepare batch

| version | design | prepare result | status |
| --- | --- | --- | --- |
| `v119` | `v110 + bit_other prompt-local manual` conservative | `2114 rows`, `33 iters`, augmentation `8` (`boxed_only_done 8`) | gate24 実測済み |
| `v120` | `v110 + bit_other prompt-local manual` broad | `2118 rows`, `33 iters`, augmentation `12` (`boxed_only_done 12`) | gate24 実測済み |
| `v121` | `v110 + bit_other prompt-local manual` + same-row boxed twin | `2122 rows`, `33 iters`, augmentation `16` (`boxed_only_done 8 + boxed_only 8`) | prepare only |
| `v122` | `v110 + bit_other prompt-local manual` + hybrid-consensus verified | `2122 rows`, `33 iters`, augmentation `16` (`manual boxed_only_done 8 + hybrid boxed_only 8`) | prepare only |

artifact source of truth:

- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v119_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v120_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v121_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v122_lr1p25e6_ep025/prepare_manifest.json`

### v119-v122 gate24 follow-up

`v119` / `v120` を `v110` adapter から top8 continuation で学習し、OOM 回避のため **single-shard gate24** で先に評価した。  
結果は **どちらも `v110` の `21/24` を下回り、この枝は branch closure**。

| version | train | gate24 | family breakdown | decision |
| --- | --- | ---: | --- | --- |
| `v119` | `final val 0.311 -> 0.312` | `16/24` | `binary 0/4`, `gravity 4/4`, `roman 4/4`, `symbol 0/4`, `text 4/4`, `unit 4/4` | 不採用 |
| `v120` | `final val 0.311 -> 0.310` | `17/24` | `binary 1/4`, `gravity 4/4`, `roman 4/4`, `symbol 2/4`, `text 2/4`, `unit 4/4` | 不採用 |
| `v121` | prepare only | OOM 対応で train 停止 | twin 追加枝 | 打ち切り |
| `v122` | prepare only | OOM 対応で train 停止 | hybrid 混合枝 | 打ち切り |

観察:

- `bit_other` manual を足すと **binary hard prompt の boxed formatting が崩れた**。
  - `v119` binary metrics: `boxed_extraction_success_rate 0.0`, `format_failure_rate 1.0`
  - `v120` binary metrics: `boxed_extraction_success_rate 0.5`, `format_failure_rate 0.75`
- `v120` は `v119` より広い manual quota で **symbol 2/4** までは戻したが、`binary 1/4` / `text 2/4` に留まり、`v110` 改善には繋がらなかった。
- row-level では `your answer` placeholder と `last_number` fallback が再発しており、**current prompt-local manual teacher は single-adapter continuation だと出力形式安定性を壊す**。

artifact source of truth:

- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v119_lr1p25e6_ep025/training_result.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v119_lr1p25e6_ep025/phase0_offline_eval/artifacts/phase0_eval_summary.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v120_lr1p25e6_ep025/training_result.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v120_lr1p25e6_ep025/phase0_offline_eval/artifacts/phase0_eval_summary.json`

### v123-v124 verified-only follow-up

manual prompt-local branch が formatting を壊したため、次は **verified-only strong-sample** を `v110` continuation に narrow append する safer branch を切った。

| version | design | prepare result | train | gate24 | follow-up |
| --- | --- | --- | --- | ---: | --- |
| `v123` | `v110 + bit_other verified 24 + numeric_2x2 verified 8` | `2138 rows`, `33 iters`, augmentation `32` | `final val 0.311 -> 0.309` | `16/24` | branch closure |
| `v124` | `v110 + bit_other verified 48 + numeric_2x2 verified 16` | `2170 rows`, `33 iters`, augmentation `64` | `final val 0.311 -> 0.309` | `21/24` | slice triage 実施 → full320 昇格 |

`v124` は gate24 では **`v110` と同点 `21/24`** だったが、中身は単純な tie ではなかった。

- gain: `c625ba91` (`bit_other`) を `your answer` から **`11111111`** に回収
- loss: `0fdc689e` (`unit_fixed_ratio`) を **`29.56 -> 795`** の numeric fallback に悪化
- 未回収: `12e947ca` (`bit_other`), `db6a5663` (`numeric_2x2`)

そのため full320 の前に README 条件の slice を切った。

| version | slice | result | comparison vs `v110` | note |
| --- | --- | ---: | --- | --- |
| `v124` | `unit50` | `44/50 = 0.88` | `v110 unit = 42/50` より **+2** | gate24 の unit 1-loss は全体では regress ではなかった |
| `v124` | `binary60` | `4/60 = 0.0667` | `v110 binary60 = 3/60` より **+1** | `bit_other 4/46`, `bit_structured_byte_formula 0/14`, `format_failure_rate 0.9333` |

判断:

- `v123` は `16/24` で dead branch
- `v124` は **binary +1 / unit +2** と `v110` を上回る slice signal が見えたため、**separate eval root で README actual full320** へ進める

運用メモ:

- `mac_workspace/v1/phase2_binary_dsl_mlx_v1.py eval-phase0` は、`--adapter-path` 指定時に **既定では adapter run dir の `phase0_offline_eval` を上書き**する
- slice / full320 を並行管理するには **`--eval-output-root` を明示**する必要がある

### v124 full320 actual

`v124` を separate root (`eval_single_adapter_v124_full320_shard2`) で README 条件 actual full320 に流した。

| version | local320 | binary | gravity | roman | symbol | text | unit | note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `v124` | `194/320 = 0.6062` | `5/60` | `49/50` | `47/50` | `13/60` | `35/50` | `45/50` | `v110` slice-equivalent `192/320` より **+2**、ただし `v40 = 205/320` には未達 |

`v110` 比の family delta:

- `binary +2` (`3 -> 5`)
- `gravity +1` (`48 -> 49`)
- `roman ±0` (`47 -> 47`)
- `symbol +2` (`11 -> 13`)
- `text -6` (`41 -> 35`)
- `unit +3` (`42 -> 45`)

結論:

- `v124` は **`v110` からは改善**した
- ただし single-adapter の best known `v40 = 205/320` を **11 点下回る**
- したがってこのまま mainline にはせず、ユーザー懸念どおり **`0.25 epoch` undertraining 仮説**を潰すため、次は同 profile / 同条件で **epoch 比較 (`0.25 / 0.5 / 1.0 / 2.0`)** を 1 回だけ実施して、以後の実験で使う epoch を決める

#### `v40` gap audit

README actual full320 の row-level を best known single-adapter `v40` と突き合わせると、overlap 320 行の内訳は次のとおりだった。

- `both_correct = 179`
- `both_wrong = 100`
- `v40_only = 26`
- `v124_only = 15`
- net は **`-11`**

family net delta (`v124 - v40`):

- `text -6` (`gain 7 / loss 13`)
- `binary -4` (`gain 2 / loss 6`)
- `unit -3` (`gain 0 / loss 3`)
- `roman -1`
- `symbol +1`
- `gravity +2`

loss profile (`v40_only 26`):

- fallback は **`last_number 17`**, `boxed_non_empty 8`, `boxed_empty 1`
- prediction kind は `number_only 10`, `placeholder("your answer") 8`, `binary_like 7`, `empty 1`
- 特に `text` loss 13 件は `number_only 9`, `placeholder 2`, `binary_like 2`
- `binary` loss 6 件は `binary_like 5`, `placeholder 1`

gain profile (`v124_only 15`):

- `text` gain 7 件はすべて **textual final answer の回収**
- `gravity` gain 3 件は unit suffix / placeholder を落とした **plain numeric** 回収
- `symbol` gain 3 件は `numeric_2x2` 側の回収

解釈:

- `v124` の `v40` 比 **-11** は、`symbol` ではなく **`text + binary + unit`** の取りこぼしが主因
- 次枝で優先すべきなのは `numeric_2x2` の追加 gain ではなく、**text final-answer fidelity** と **binary の boxed / placeholder 崩れ抑制** である

artifact source of truth:

- `mac_workspace/v1/outputs/eval_single_adapter_v124_full320_shard2/phase0_offline_eval/artifacts/phase0_eval_summary.json`
- `mac_workspace/v1/outputs/eval_single_adapter_v124_full320_shard2/phase0_offline_eval/artifacts/phase0_eval_row_level.csv`
- `mac_workspace/v0/outputs/eval_safe_resume_v10_binarycandidates_v40_v41/full320_full_fusion_v40_lr1p25e6_ep0125_shard2/phase0_offline_eval/artifacts/phase0_eval_row_level.csv`

### epoch sweep (`v124` / `v125` / `v126` / `v127`)

`v124` と同一 profile / 同一 base / 同一 LR / 同一 batch / 同一 layers のまま、**epoch だけ**を `0.25 / 0.5 / 1.0 / 2.0` に振った 1 回限りの controlled comparison を実施した。

- control: `v124 = 0.25 epoch`
- `v125 = 0.5 epoch`
- `v126 = 1.0 epoch`
- `v127 = 2.0 epoch`

train は以下で完了した。

| version | epoch | train | note |
| --- | ---: | --- | --- |
| `v124` | `0.25` | `final val 0.311 -> 0.309`, `33 iters` | control |
| `v125` | `0.5` | `final val 0.311 -> 0.304`, `67 iters` | gate24 / slices 実測済み |
| `v126` | `1.0` | `final val 0.311 -> 0.290`, `135 iters` | gate24 実測済み |
| `v127` | `2.0` | `final val 0.311 -> 0.273`, `271 iters` | gate24 実測済み |

まず README 条件寄りの gate24 で足切りした。

| version | gate24 | family breakdown | decision |
| --- | ---: | --- | --- |
| `v124` | `21/24` | `binary 2/4`, `gravity 4/4`, `roman 4/4`, `symbol 3/4`, `text 4/4`, `unit 4/4` | control |
| `v125` | `21/24` | `binary 2/4`, `gravity 4/4`, `roman 4/4`, `symbol 3/4`, `text 4/4`, `unit 4/4` | 残留 |
| `v126` | `19/24` | `binary 2/4`, `gravity 4/4`, `roman 4/4`, `symbol 1/4`, `text 4/4`, `unit 4/4` | 脱落 |
| `v127` | `19/24` | `binary 1/4`, `gravity 4/4`, `roman 4/4`, `symbol 2/4`, `text 4/4`, `unit 4/4` | 脱落 |

したがって deeper slice は `v124` vs `v125` だけに絞った。

| slice | `v124` (`0.25`) | `v125` (`0.5`) | delta (`v125 - v124`) |
| --- | ---: | ---: | ---: |
| `general200` | `176/200` | `175/200` | `-1` |
| `binary60` | `4/60` | `5/60` | `+1` |
| `unit50` | `44/50` | `47/50` | `+3` |

`v125 general200` の内訳:

- `gravity 49/50`
- `roman 48/50`
- `text 34/50`
- `unit 44/50`

slice 時点の解釈:

- `1.0` / `2.0` は **gate24 の時点で明確に regress** したため、候補から外した
- `0.5` は `0.25` と **gate24 tie**
- deeper slice では `general200 -1` だったが、**`binary +1` と `unit +3`** がそれを上回って見えた
- 特に `unit50 = 47/50` は、`v124` の `44/50` に対して **明確な改善**だった

### v125 full320 actual

slice-based decision が README 条件 actual full320 に乗るかを確認するため、`v125` を separate root (`eval_single_adapter_v125_full320_shard2`) で実測した。

| version | full320 actual | family breakdown | delta vs `v124` |
| --- | ---: | --- | ---: |
| `v124` | `194/320` | `binary 5/60`, `gravity 49/50`, `roman 47/50`, `symbol 13/60`, `text 35/50`, `unit 45/50` | control |
| `v125` | `187/320` | `binary 4/60`, `gravity 49/50`, `roman 48/50`, `symbol 10/60`, `text 32/50`, `unit 44/50` | `-7` |

family delta (`v125 - v124`):

- `binary -1`
- `gravity ±0`
- `roman +1`
- `symbol -3`
- `text -3`
- `unit -1`

binary metric delta (`v125 - v124`):

- `boxed_extraction_success_rate`: `0.0833 -> 0.1333`
- `regex_exact_rate`: `0.2167 -> 0.0833`
- `leading_zero_retention_rate`: `0.2000 -> 0.1333`
- `format_failure_rate`: `0.9333 -> 0.9667`

解釈:

- `0.5 epoch` の slice gain は **actual full320 では再現しなかった**
- `boxed` 抽出率だけは少し上がったが、**exactness と leading-zero 保持が落ち、format failure も悪化**した
- ユーザーが重視している **`\boxed{}` 最終回答の安定性**という観点でも、`v125` は `v124` より悪い

結論:

- `1.0` / `2.0` は継続して不採用
- `0.5` は slice triage では有望だったが、**README actual full320 で棄却**
- 現在の `single-adapter-fusion-v124` 系 mainline では、**`0.25 epoch` を safer control として維持**する
- 次の枝は epoch ではなく、**`boxed_only` / `boxed_only_done` の fidelity を壊さずに binary / symbol を伸ばすデータ設計**を優先する

artifact source of truth:

- `mac_workspace/v1/outputs/eval_single_adapter_v125_gate24/phase0_offline_eval/artifacts/phase0_eval_summary.json`
- `mac_workspace/v1/outputs/eval_single_adapter_v126_gate24/phase0_offline_eval/artifacts/phase0_eval_summary.json`
- `mac_workspace/v1/outputs/eval_single_adapter_v127_gate24/phase0_offline_eval/artifacts/phase0_eval_summary.json`
- `mac_workspace/v1/outputs/eval_single_adapter_v125_general200/eval_single_adapter_v125_general200/phase0_offline_eval/artifacts/phase0_eval_summary.json`
- `mac_workspace/v1/outputs/eval_single_adapter_v125_unit50/phase0_offline_eval/artifacts/phase0_eval_summary.json`
- `mac_workspace/v1/outputs/eval_single_adapter_v125_binary60/phase0_offline_eval/artifacts/phase0_eval_summary.json`
- `mac_workspace/v1/outputs/eval_single_adapter_v125_full320_shard2/eval_single_adapter_v125_full320_shard2/phase0_offline_eval/artifacts/phase0_eval_summary.json`

### v128-v129 boxed-safe follow-up

`v125` が actual full320 で regress したため、次は epoch ではなく **boxed fidelity を崩さない narrow repair** に切り替えた。  
どちらも `v124` adapter continuation / `lr=1.25e-6` / `epoch=0.25` / `top8` / `dataset_format=text` で揃えている。

| version | design | prepare result | train | README score | decision |
| --- | --- | --- | --- | --- | --- |
| `v128` | `v124 + v67-style exact-trace-safe structured repair` | `2223 rows`, `34 iters`, augmentation `53` (`binary 35`, `symbol 4`, `text 14`) | `final val 0.309 -> 0.306`, peak mem `74.475 GB` | **未計測**（gate24 を `>12 min` で中止、1-row binary probe も `>50s`） | 不採用 |
| `v129` | `v124 + v79-style strict boxed_done structured repair` | `2224 rows`, `34 iters`, augmentation `54` (`binary 36`, `symbol 4`, `text 14`) | `final val 0.309 -> 0.306`, peak mem `74.475 GB` | **未計測**（gate24 を `>12 min` で中止、1-row binary probe も `>50s`） | 不採用 |

補足:

- `v128` は source を
  - `binary_structured_answer_only_abstract_safe 7`
  - `binary_affine_verified 12`
  - `binary_structured_answer_only 8`
  - `binary_structured_recommended 8`
  - `symbol_formula_verified 4`
  - `text_verified_anchor 14`
  に絞った conservative branch。
- `v129` は source を
  - `binary_affine_verified 12`
  - `binary_structured_answer_only 8`
  - `binary_prompt_local_current_structured_boxed_done 16`
  - `symbol_formula_verified 4`
  - `text_verified_anchor 14`
  に置いた strict `boxed_only_done` branch。
- しかし README 条件の `gate24` は、**どちらも chunk1/1 のまま 12 分以上進まず、prediction artifact も manifest 以外は生成されなかった**。
- さらに `binary` 1-row probe (`per_family_limit=1`, `max_samples=1`) でも、**どちらも 50 秒超で完了しなかった**。
- したがってこの 2 本は、「score が低い」より前に **README decoding 下で long-generation / final-format regression を起こしている** と判断し、mainline 候補から外した。

artifact source of truth:

- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v124_to_top8_fusion_v128_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v124_to_top8_fusion_v128_lr1p25e6_ep025/training_result.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v124_to_top8_fusion_v129_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v124_to_top8_fusion_v129_lr1p25e6_ep025/training_result.json`

### v130-v133 v40-base safe-aug diagnostics

`v124` の 64-row safe augmentation を **`v40` 側へ載せ替えれば、`v40` の text/unit 保持を壊さず binary/symbol を上積みできるか** を切り分けた。  
ここでは README 条件の score に入る前段として、まず **train 完走 → binary 1-row probe / gate24 の decode 健全性** を確認した。

| version | design | prepare/train | README判定 | decision |
| --- | --- | --- | --- | --- |
| `v130` | `single-adapter-fusion-v124` の recipe をそのまま使い、resume だけ `v110 -> v40` へ差し替え | `2170 rows`, `33 iters`; `final val 0.325 -> 0.322` | gate24 は **`>12 min`** でも chunk 完了 0、binary 1-row probe も **`>90s`** | 不採用 |
| `v131` | **corrected branch**: `single-adapter-fusion-v40` base + `v124` safe aug 全量 (`binary 48 + symbol 16`) | `2026 rows`, `31 iters`; `final val 0.355 -> 0.347` | binary 1-row probe が **`>90s`** | 不採用 |
| `v132` | `single-adapter-fusion-v40` base + `v124` binary safe aug のみ (`48`) | `2010 rows`, `31 iters`; prepare only | `v133` で同型 failure を確認したため未実行 | 打ち切り |
| `v133` | `single-adapter-fusion-v40` base + `v124` symbol safe aug のみ (`16`) | `1978 rows`, `30 iters`; `final val 0.355 -> 0.348` | binary 1-row probe が **`>90s`** | 不採用 |

解釈:

- `v130` により、**`v110` base recipe を抱えたまま `v40` に resume するだけ**でも README decode は長文化することが分かった。
- そのため `v131-v133` で **本当に切りたかった条件**、つまり **`v40` base に `v124` 系 short-done rows を載せる枝**を直接切り直した。
- しかし `v133` でも binary 1-row probe が **`>90s`** のままだったため、stall の主因は **`v124` binary 48 rows 単独ではなく、`v40` base に `v124` 系 `boxed_only_done` verified-short rows を混ぜる方針そのもの**だと判断した。
- したがってこの route は **gate24/full320 に進める前段で closed**。`v40` を起点にする次枝は、`v124` 系 short-done verified rows ではなく、**別 teacher style / 別 source family** で切る。

artifact source of truth:

- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v130_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v130_lr1p25e6_ep025/adapter/`
- `mac_workspace/v1/outputs/eval_single_adapter_v130_gate24/gate24_top8_fusion_v130_from_v40_lr1p25e6_ep025/phase0_offline_eval/artifacts/phase0_eval_manifest.json`
- `mac_workspace/v1/outputs/eval_single_adapter_v130_binary1/`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v131_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v131_lr1p25e6_ep025/adapter/`
- `mac_workspace/v1/outputs/eval_single_adapter_v131_binary1/`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v132_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v133_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v133_lr1p25e6_ep025/adapter/`
- `mac_workspace/v1/outputs/eval_single_adapter_v133_binary1/`

### v134-v136 pure boxed-only follow-up

`v133` でも stall したため、次は source family を変えず **teacher style だけ**を `boxed_only_done -> boxed_only` に差し替えた。  
狙いは、`Done.` が decode 長文化の trigger なら、pure boxed-only で `v40` base の binary probe が元に戻るかを切ることだった。

| version | design | prepare/train | README判定 | decision |
| --- | --- | --- | --- | --- |
| `v134` | `single-adapter-fusion-v40` base + `v124` safe aug 全量 (`binary 48 + symbol 16`), teacher=`boxed_only` | `2026 rows`, `31 iters`; prepare only | `v135` で route closure を確認したため未実行 | 打ち切り |
| `v135` | `single-adapter-fusion-v40` base + `v124` symbol safe aug のみ (`16`), teacher=`boxed_only` | `1978 rows`, `30 iters`; `final val 0.355 -> 0.347` | binary 1-row probe が **`>90s`** | 不採用 |
| `v136` | `single-adapter-fusion-v40` base + `v124` binary safe aug のみ (`48`), teacher=`boxed_only` | `2010 rows`, `31 iters`; prepare only | `v135` で route closure を確認したため未実行 | 打ち切り |

解釈:

- `v135` が **symbol-only かつ pure boxed-only** でも binary 1-row probe を **`>90s`** で返せなかったため、**`Done.` の有無は主因ではない**。
- これで `v130-v136` 全体から、`v40` 起点で **`v124` 系 verified-short rows（binary/symbol, boxed_only_done/boxed_only）を混ぜる方針そのもの**が README decode を壊すと判断した。
- したがって、次の `v40` continuation は **source family も teacher style も別物**へ切り替える。`v124` 系 short verified rows は route closed。

artifact source of truth:

- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v134_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v135_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v135_lr1p25e6_ep025/adapter/`
- `mac_workspace/v1/outputs/eval_single_adapter_v135_binary1/`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v136_lr1p25e6_ep025/prepare_manifest.json`

### v137-v138 low-dose symbol boxed-only follow-up

`v135` で `16` 行が toxic だったため、同じ `strong_sample_symbol_numeric_verified_short` family を **`4` / `8` 行**まで下げて threshold を切った。  
teacher style は `v135` と同じ **pure `boxed_only`** で、変えるのは quota だけ。

| version | design | prepare/train | README判定 | decision |
| --- | --- | --- | --- | --- |
| `v137` | `single-adapter-fusion-v40` base + `strong_sample_symbol_numeric_verified_short` `4` rows, teacher=`boxed_only` | `1966 rows`, `30 iters`; `final val 0.355 -> 0.348` | binary 1-row probe が **`>75s`** | 不採用 |
| `v138` | `single-adapter-fusion-v40` base + `strong_sample_symbol_numeric_verified_short` `8` rows, teacher=`boxed_only` | `1970 rows`, `30 iters`; `final val 0.355 -> 0.347` | binary 1-row probe が **`>75s`** | 不採用 |

解釈:

- **quota 16 だけでなく 8 / 4 でも decode stall は消えなかった**。
- したがって `strong_sample_symbol_numeric_verified_short` family は、`v40` continuation に対して **dose を下げても toxic** とみなす。
- 今後の `v40` continuation では、この family を source 候補から外す。

artifact source of truth:

- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v137_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v137_lr1p25e6_ep025/adapter/`
- `mac_workspace/v1/outputs/eval_single_adapter_v137_binary1/`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v138_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v40_to_top8_fusion_v138_lr1p25e6_ep025/adapter/`
- `mac_workspace/v1/outputs/eval_single_adapter_v138_binary1/`
