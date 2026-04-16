# v20_mlx_repro_v1 results

> Repository note: canonical challenge contract lives in `README.md`.
> This version is a local MLX reproduction of A-Open v20 using `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14/` as the exact training snapshot.
> It does **not** claim submission.zip parity; it measures how closely MLX reproduces the published v20 training/eval behavior.

## Source contract

- Top-level README: `README.md`
- V20 snapshot: `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14`

## Run summary

- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1`
- shadow_model_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/shadow_model`
- adapter_dir: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/adapter`
- snapshot_contract_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/snapshot_contract.json`

## Training settings

- backend: `mlx`
- optimizer_steps: `245`
- last_train_loss: `0.00030877206662561054`
- last_lr: `8.163265306122547e-07`

## Evaluation result

- evaluation_kind: `adapter_validation`
- evaluation_name: `adapter_validation_stratified_category_300_of_950`
- overall_accuracy: `0.82` (246/300)

- source_document: `README.md`
- source_document: `A-Open-ProgressPrizePublication/README.md`
- source_document: `A-Open-ProgressPrizePublication/データ戦略を理解する.md`
- source_document: `A-Open-ProgressPrizePublication/学習SFTパイプライン.md`
- source_document: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`

- notebook_reference: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`
- validation_sample_size: `950`
- sample_selection_mode: `stratified-category-proportional`
- sample_selection_tag: `stratified_category_300_of_950`
- sample_selection_total: `300` / `950`

## Eval settings

- max_tokens: `7680`
- max_num_seqs: `4`
- prompt_chunk_size: `4`
- prefill_batch_size: `4`
- completion_batch_size: `4`
- eval_enable_thinking: `True`
- eval_shards: `4`

## Prompt policy

- append_boxed_instruction: `False`
- enable_thinking: `True`

## Eval aggregation

- mode: `sharded`
- shard_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/adapter_validation/shards`
- num_shards: `4`

| category | correct | total | accuracy | weightage | percentage | contribution |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bit_manipulation | 37 | 53 | 0.698113 | 17.7% | 69.8% | 12.3% |
| cipher | 50 | 51 | 0.980392 | 17.0% | 98.0% | 16.7% |
| cryptarithm_deduce | 0 | 23 | 0.000000 | 7.7% | 0.0% | 0.0% |
| cryptarithm_guess | 1 | 5 | 0.200000 | 1.7% | 20.0% | 0.3% |
| equation_numeric_deduce | 7 | 15 | 0.466667 | 5.0% | 46.7% | 2.3% |
| equation_numeric_guess | 0 | 2 | 0.000000 | 0.7% | 0.0% | 0.0% |
| gravity | 50 | 50 | 1.000000 | 16.7% | 100.0% | 16.7% |
| numeral | 47 | 47 | 1.000000 | 15.7% | 100.0% | 15.7% |
| unit_conversion | 54 | 54 | 1.000000 | 18.0% | 100.0% | 18.0% |

## Post-eval notes

- Final MLX reproduced run on `adapter_validation_stratified_category_300_of_950`: **`246 / 300 = 0.82`**
- Strong families:
  - `gravity = 50 / 50`
  - `numeral = 47 / 47`
  - `unit_conversion = 54 / 54`
  - `cipher = 50 / 51`
- Main loss buckets:
  - `cryptarithm_deduce = 0 / 23`
  - `equation_numeric_guess = 0 / 2`
  - `cryptarithm_guess = 1 / 5`
  - `equation_numeric_deduce = 7 / 15`
  - `bit_manipulation = 37 / 53`
- Publication deterministic reasoners benchmarked directly on the same 300-row subset reached **`257 / 300 = 0.856667`**.
- Reasoner-over-model gains were concentrated in `equation_numeric_deduce` (`7 -> 15` correct), with smaller gains in `bit_manipulation` (`37 -> 39`) and `cipher` (`50 -> 51`), while both model and reasoners remained weak on `cryptarithm_*` and `equation_numeric_guess`.
- When the published first-950 notebook ratios are projected onto this exact 300-row subset, the expected counts are roughly `gravity 50`, `numeral 47`, `unit_conversion 54`, `cipher 49.74`, `bit_manipulation 46.73`, `equation_numeric_deduce 13.12`, `cryptarithm_deduce 1.94`, `cryptarithm_guess 1.07`, `equation_numeric_guess 0`. The MLX run is therefore close on the easy families and `cipher`, while the real reproduction gap is concentrated in `bit_manipulation` and `equation_numeric_deduce`.
- All `8/8` current `equation_numeric_deduce` misses in `validation.csv` were long incomplete generations with **no** `\boxed{}` and **no** closing `</think>`, so the visible failure mode there is truncation / runaway reasoning rather than answer-extraction loss.
- However, a same-weights **no-thinking** probe on those exact `8` failed `equation_numeric_deduce` rows recovered **`0 / 8`**; outputs collapsed to short wrong answers (average `24.5` chars) instead of the long truncated traces. This means the long-thinking behavior changes how the failure appears, but turning thinking off does **not** rescue the missing skill.
- A same-weights **no-thinking** probe on the exact `16` failed `bit_manipulation` rows likewise recovered **`0 / 16`** (average `822.1` chars, median `102.5`), so the main bit losses also persist without the long-thinking path.
- On the full focus slice (`bit_manipulation + equation_numeric_deduce`, `68` rows total) the same-weights **no-thinking** ablation collapsed from baseline **`44 / 68`** to **`4 / 68`**. Category-wise that is `bit_manipulation 37 / 53 -> 3 / 53` and `equation_numeric_deduce 7 / 15 -> 1 / 15`.
- That full-slice ablation produced **`0` improved rows**, **`40` regressed rows**, and only **`28` unchanged rows**. So `enable_thinking=True` is not the reason these categories underperform; if anything it is preserving a large amount of capability that disappears when thinking is disabled.
- One nuance from the available source logs: the checked-in v20 snapshot config says `micro_batch_size = 16`, but the user's PEFT replay log with the already-matched target modules / trainable params reports `local_micro_batch_size = 1` together with `optimizer_kind = paged_adamw_8bit`. So micro-batch mismatch alone is **not** the cleanest confirmed explanation; the strongest confirmed training-side difference is now the optimizer/backend path (`paged_adamw_8bit`/PEFT or Tinker versus MLX `optim.Adam`).
- Current diagnosis: the dominant residual is more consistent with **training / weight divergence** from the original v20 path than with MLX eval extraction bugs or thinking-mode verbosity alone. Thinking still matters as a secondary inference-behavior factor for `equation_numeric_deduce`, because it turns short wrong answers into long unfinished traces, but the ablation shows it is net-helpful rather than the core cause of the gap.
- Status note: the completed full train for this version is still **`v20_mlx_repro_v1_fullrun_targetfix_mb1`**, i.e. the MLX `optim.Adam` path recorded in `run_manifest.json`. A full retrain that closes the remaining optimizer/backend gap to the available source evidence (`backend=tinker` and/or `optimizer_kind=paged_adamw_8bit`) has **not** been run yet. Under `README.md`, this gap is an open **v20 strict-reproduction** task, not a challenge-format compliance blocker.
- Short strict-reproduction probe on 2026-04-16: two initial no-bias-correction probe attempts accidentally used the script default `micro_batch_size=16` and hit Metal OOM before step 1, so they are not comparable to the successful MLX full run. After correcting to `--micro-batch-size 1`, a matched `8`-step schedule probe was run for **2 steps** with `bias_correction=False`, then compared against a matched **2-step** `bias_correction=True` control run.
- In that matched mb1 short probe, **step 1 was identical** (`loss = 0.3835325885531003`, `lr = 0.0002`, peak memory `214.8353 GB`), but **step 2 diverged materially** at the same `lr = 0.000175`: `bias_correction=False` reached `loss = 0.36575833790603657`, while `bias_correction=True` reached `loss = 0.5416443912633949` (delta `-0.17588605335735835` in favor of `bias_correction=False`), with essentially identical peak memory (`221.9410 GB` vs `221.9409 GB`).
- Interpretation of that short probe: inside the current MLX monolith, the bias-correction toggle changes the optimization path measurably by step 2 without changing memory behavior. This is **not** evidence of a final-score gain yet, but it is enough to justify treating `--no-bias-correction` as the next highest-signal full-run candidate before attempting harder optimizer/backend rewrites.
- 2026-04-16 launch decision: started a new full retrain candidate named **`v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc`** with the same exact snapshot replay and `micro_batch_size=1`, changing only the MLX optimizer flag to **`--no-bias-correction`**. This is the first full run explicitly targeting the measured optimizer-path gap while keeping the rest of the successful MLX reproduction contract fixed.
- Early monitoring snapshot for that full run: **step 1 completed successfully** with `train_loss = 0.3835325885531003`, `lr = 0.0002`, `step_tokens = 104262`, `trained_tokens = 104262`, and `peak_memory_gb = 214.8353`. Those values are identical to the first step of the completed `v20_mlx_repro_v1_fullrun_targetfix_mb1` baseline, so the new run is at least healthy through the first optimizer step and only begins to diverge later if the no-bias-correction path truly matters.
- By step 4, the no-bias-correction full run was still healthy and was tracking **lower loss than the completed baseline at the same LR on every step after step 1**:
  - step 2: baseline `0.537891700011057` vs nobc `0.3553264494481507` (delta `-0.1825652505629063`)
  - step 3: baseline `0.3002787976761552` vs nobc `0.2584564291858825` (delta `-0.041822368490272654`)
  - step 4: baseline `0.18214266110983754` vs nobc `0.16342326138546515` (delta `-0.018719399724372393`)
- Peak memory stayed unchanged versus baseline through step 4 (`221.9409 GB` after step 2+), so the observed early improvement is a training-path effect, not a memory/throughput tradeoff artifact.
- By step 8, that pattern had held for the entire first `8` optimizer steps: step 1 remained identical, and **steps 2-8 were all lower-loss than the completed baseline at the same LR**. The latest step-8 comparison was baseline `0.08271774132149194` vs nobc `0.05319287599338549` (delta `-0.02952486532810645`), with peak memory still unchanged at `221.9409 GB`.
- Operational status at the step-8 milestone: the detached **smoke watcher v2** was still alive and polling every 5 minutes for `training_result.json`, and the detached **eval300 chain watcher** was armed to archive smoke outputs and launch the 300-row 4-shard eval only if the smoke summary completes healthy (`>= 7/8`).
- The same pattern still held at **step 9**: baseline `0.07380936467549064` vs nobc `0.0484179373020636` (delta `-0.02539142737342704`). So the no-bias-correction run remained consistently ahead of baseline through the first `9` optimizer steps while keeping the same peak memory ceiling.
- By **step 16**, the run was still healthy and the early lead had persisted through the full first `16` optimizer steps. Step 1 remained identical, and **every step from 2 through 16 was lower-loss than baseline at the same LR**. The latest step-16 comparison was baseline `0.02783931793607595` vs nobc `0.011274035962362598` (delta `-0.016565281973713354`).
- The last seven step deltas before that milestone were all favorable as well: step 10 `-0.021160975163088465`, step 11 `-0.017265712553091263`, step 12 `-0.005616846187828005`, step 13 `-0.022684687865911227`, step 14 `-0.0023306986872442294`, step 15 `-0.020183764532881662`, step 16 `-0.016565281973713354`.
- Operationally, the step16 watcher completed successfully, while the detached `smoke_watch_v2` continued polling for `training_result.json` and the detached `eval300` chain watcher remained armed behind it.
- By **step 32**, the run was still healthy (`train_loss = 0.002505089915434086`, `lr = 0.00017469387755102042`, peak memory `221.9409 GB`) and remained mostly ahead of baseline, but the earlier “all steps after step 1 are lower-loss” pattern no longer held strictly. There was a small temporary regression window at steps `26-28`:
  - step 26: baseline `0.002767294444093858` vs nobc `0.002949561201867092` (delta `+0.00018226675777323386`)
  - step 27: baseline `0.0038937293759880314` vs nobc `0.004263069305825183` (delta `+0.00036933992983715193`)
  - step 28: baseline `0.0031311420987780083` vs nobc `0.00321180630144808` (delta `+0.00008066420267007152`)
- After that blip, the run returned to lower-loss values at steps `29-32`, including step 32 itself: baseline `0.0029800718671799775` vs nobc `0.002505089915434086` (delta `-0.0004749819517458915`). So the current evidence still favors the no-bias-correction path overall, but not as a monotonic per-step win.
- By **step 64**, the run was still healthy (`train_loss = 0.0012180586039128197`, `lr = 0.00014857142857142858`, peak memory `221.9409 GB`) but the comparison had become genuinely mixed. Over steps `33-64`, nobc beat baseline on `18` steps and trailed it on `14`, so the early “clear lead” had flattened into a noisy near-parity band rather than extending cleanly.
- The best mid-interval nobc advantage in that range was at **step 37**: baseline `0.00313631660629276` vs nobc `0.0022576154011858403` (delta `-0.0008787012051069197`). The largest regression was at **step 50**: baseline `0.0026276590617166137` vs nobc `0.003612740336377012` (delta `+0.0009850812746603982`).
- The latest `step 64` comparison itself was slightly unfavorable: baseline `0.0010592759516110453` vs nobc `0.0012180586039128197` (delta `+0.00015878265230177433`). The last eight observed deltas before that milestone were also mixed (`57:+0.0001754491682079949`, `58:-0.0005867738223887373`, `59:-0.00012433267955250119`, `60:-0.00024202774411651224`, `61:+0.0001650570247500756`, `62:+0.00035625744249894765`, `63:+0.00007016177498834868`, `64:+0.00015878265230177433`).
- Interpretation at the step64 milestone: `--no-bias-correction` is still a plausible strict-reproduction candidate, but it is no longer behaving like an obviously dominant improvement over the completed baseline. The decisive signal now needs to come from the full-run end state plus downstream smoke / eval300, not from early-step loss alone.
- By **step 80**, the run was still healthy (`train_loss = 0.0007953446394173183`, `lr = 0.00013551020408163265`, peak memory `221.9409 GB`) and had tilted slightly back toward nobc. Over steps `65-80`, nobc beat baseline on `10` steps and trailed it on `6`, so this segment was modestly favorable even though it still looked noisy rather than one-sided.
- The strongest nobc advantage in that `65-80` window was at **step 77**: baseline `0.002367105245976643` vs nobc `0.001418308102106525` (delta `-0.0009487971438701182`). The largest regression in the same window was at **step 74**: baseline `0.0009710000942785209` vs nobc `0.0015533340483438367` (delta `+0.0005823339540653158`).
- The latest `step 80` comparison itself was mildly favorable again: baseline `0.0009022083913014133` vs nobc `0.0007953446394173183` (delta `-0.00010686375188409503`). The last eight deltas leading into that point were `73:-0.0003810755175953622`, `74:+0.0005823339540653158`, `75:-0.00034655625623700756`, `76:-0.0005559628962582999`, `77:-0.0009487971438701182`, `78:-0.00012414714370439887`, `79:-0.00044271767959079187`, `80:-0.00010686375188409503`.
- Interpretation at the step80 milestone: the no-bias-correction path has not recovered the clean early-step dominance seen at step16, but it also has not collapsed into sustained underperformance. The live read remains “slightly promising but inconclusive,” so the end-to-end smoke / eval300 outcome is still the only trustworthy judge.
- By **step 96**, the run was still healthy (`train_loss = 0.0012050739039894977`, `lr = 0.00012244897959183676`) and the recent comparison had tilted more clearly back toward nobc. Over steps `81-96`, nobc beat baseline on `11` steps and trailed it on `5`, which is the strongest segment-level advantage since the earlier early-run lead.
- The best nobc advantage in that `81-96` window was at **step 82**: baseline `0.0017809740203809908` vs nobc `0.0008743457472648113` (delta `-0.0009066282731161794`). The largest regression in the same window was at **step 85**: baseline `0.0007089563616839647` vs nobc `0.0015287661235336798` (delta `+0.000819809761849715`).
- The latest `step 96` comparison itself was materially favorable: baseline `0.0018464949684488107` vs nobc `0.0012050739039894977` (delta `-0.000641421064459313`). The last eight deltas leading into that point were `89:-0.00012356257900182068`, `90:+0.0003048520427501969`, `91:-0.00021719316277746844`, `92:-0.0004509048896595407`, `93:-0.0002852234134241284`, `94:-0.0004236650852515204`, `95:-0.0003066646687181848`, `96:-0.000641421064459313`.
- One operational nuance changed in this interval: peak memory increased slightly from the earlier `221.9409 GB` ceiling to **`222.0017 GB`** by step `90+`. That bump is tiny relative to host RAM and does not change the current stability assessment, but it is worth noting because the run is no longer bit-for-bit matching the earlier peak-memory reading.
- Interpretation at the step96 milestone: the no-bias-correction path has regained some credibility as a better optimizer-path match than the baseline MLX Adam default, but the evidence is still intermediate rather than decisive. The important remaining question is unchanged: whether this training-side lead survives to the fully completed adapter and shows up in smoke / eval300.
- By **step 112**, the run was still healthy (`train_loss = 0.0008614265092842147`, `lr = 0.00010938775510204082`, peak memory `222.0017 GB`), but the comparison had swung back against nobc. Over steps `97-112`, nobc beat baseline on only `5` steps and trailed it on `11`, so this interval looked materially worse than the favorable `81-96` segment right before it.
- The best nobc advantage in that `97-112` window was at **step 102**: baseline `0.00130459065929844` vs nobc `0.0006213058800542113` (delta `-0.0006832847792442288`). The largest regression in the same window was at **step 109**: baseline `0.0011997043041822029` vs nobc `0.0023055241734192735` (delta `+0.0011058198692370706`).
- The latest `step 112` comparison itself was slightly unfavorable: baseline `0.0006985385784350835` vs nobc `0.0008614265092842147` (delta `+0.0001628879308491312`). The last eight deltas leading into that point were `105:+0.00003595389117819745`, `106:+0.0004291905116326261`, `107:-0.00018929230688405037`, `108:+0.00012775530052506145`, `109:+0.0011058198692370706`, `110:+0.00048133533816935217`, `111:+0.0010952521966874585`, `112:+0.0001628879308491312`.
- Interpretation at the step112 milestone: the nobc trajectory remains highly non-monotonic. It still looks like a plausible optimizer-path variant, but the training curve is now alternating between clearly favorable and clearly unfavorable windows, which reinforces that early loss snapshots alone are not reliable enough to call the final outcome.
- By **step 128**, the run was still healthy (`train_loss = 0.0004946676322156491`, `lr = 9.63265306122449e-05`, peak memory `222.0017 GB`) and the comparison had swung back toward nobc again. Over steps `113-128`, nobc beat baseline on `13` steps and trailed it on only `3`, making this the strongest favorable stretch since the earlier `81-96` recovery.
- The best nobc advantage in that `113-128` window was at **step 118**: baseline `0.001420760569371904` vs nobc `0.0008451617686346821` (delta `-0.0005755988007372219`). The largest regression in the same window was at **step 120**: baseline `0.0008822833559459257` vs nobc `0.001083334088758855` (delta `+0.0002010507328129292`).
- The latest `step 128` comparison itself was favorable: baseline `0.0006444421539807611` vs nobc `0.0004946676322156491` (delta `-0.000149774521765112`). The last eight deltas leading into that point were `121:-0.000043581580672593886`, `122:-0.00003731848643353933`, `123:-0.00024323241793203427`, `124:-0.0002669846953663506`, `125:-0.00005754472029354451`, `126:-0.00013294522571216509`, `127:-0.00029995901776641045`, `128:-0.000149774521765112`.
- Interpretation at the step128 milestone: the training trace is still oscillatory across medium windows, but nobc has now produced **two clearly favorable bands (`81-96` and `113-128`) separated by one clearly unfavorable band (`97-112`)**. That pattern still stops short of proving a final-score gain, yet it keeps the optimizer-path hypothesis alive and makes the completed smoke / eval300 results even more important.

## Important assumptions

- Training data uses the exact checked-in v20 snapshot `04-08-16-14/tokens` + `logprobs/index.jsonl`, not the current `corpus.jsonl`.
- Optimizer-step grouping uses the recorded `step` assignments from the snapshot, so the MLX run replays the actual v20 batch membership/order.
- MLX-specific assumptions not explicit in the public v20 config: `lora_alpha = 32`, `lora_dropout = 0.0`, `Adam bias_correction = True`.
