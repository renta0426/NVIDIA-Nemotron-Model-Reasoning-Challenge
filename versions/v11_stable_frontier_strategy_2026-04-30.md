# v11 stable frontier strategy 2026-04-30

> 目的: v10 の失敗を踏まえ、v4 へ戻す保守的変更ではなく、現状安定して解けていない問題を実際に解けるようにする v11 戦略を定義する。
> 一次根拠: `README.md`, `A-Open-ProgressPrizePublication/README.md`, `versions/v20_corrective_corpus_v10_mainline/v10_failure_analysis_2026-04-30.md`, `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md`, `cuda-train-data-analysis-v1/BIT_MANIPULATION_STRONG_GROUP_SYNTHESIS_REFERENCE.md`, v4-v10 local/proxy 実測。

## 1. 先に結論

v11 は **v4 rollback ではない**。また、v10 の frontier rows を増やす run でもない。

v11 の主戦略は、**BIT hard core を row overlay ではなく executable program-trace curriculum として作り直すこと**です。

v10 で分かったことは、次の 4 点です。

1. local validation total はもう promotion 指標として弱い。
   - v10 は `839/950 = 0.8832` だが official は `0.84 x3`。
   - gain の主成分は numeral / easy surface で、README が主戦場とする BIT は伸びていない。

2. BIT frontier は、単に hard row の答えを重ねても安定しない。
   - v10 proxy binary は `78/92`。
   - v4 `79/92`、v6 `80/92` を下回った。
   - `0520a6ec` は v4-v9 で正答だったのに v10 で `default 1` へ退行した。

3. `anti_default1_commit` は設計を変える必要がある。
   - v10 の anti-default 教師は本文に `default 1` という文字列を何度も含む。
   - 温度 0 の SFT では、禁止したい token を見せるだけでも出力分布へ入る。
   - v11 では「default を使うな」と書くのではなく、**全 output bit を executable rule で明示計算する trace**にする。

4. `manual_audit_priority` は mainline full-CoT 教師ではない。
   - FINAL_SUMMARY でも raw CoT 化は非推奨。
   - v10 proxy の `manual_audit_priority` は `8/18 = 0.4444`。
   - manual rows は新 solver / exact closure が立ったものだけ昇格する。

したがって v11 は、次の一文に集約する。

**既存 run の再配分ではなく、code-verifiable exact rule から合成した短い program trace で、BIT の未解決 rule-selection failure を直接潰す。**

## 2. README から外してはいけない制約

root `README.md` と A-Open README から、v11 の制約は変わらない。

- 評価は deterministic decoding。
  - `temperature = 0.0`
  - `top_p = 1.0`
  - `max_tokens = 7680`
  - `max_model_len = 8192`
- metric は `\boxed{}` を最優先で抽出する。
- A-Open の勝ち筋は SFT / deterministic CoT / min-logprob / bit manipulation。
- より上へ行くには、単なる配分調整ではなく programmatic insight が必要。
- Nemotron は spelling / splitting / concatenating symbols / character conversion が弱い。

この制約に照らすと、v11 でやってはいけないのは、local validation の easy-family 回復をもって「0.87 へ近づいた」と読むことです。v10 がそれを否定した。

## 3. 現状の未解決問題マップ

### 3.1 validation 950 の hard rows

v20, v4, v6, v7-1, v8, v9, v10 の 7 run 横断で、全 run wrong は `99` 行。

| category                  | always wrong rows |
| ------------------------- | ----------------: |
| `cryptarithm_deduce`      |              `64` |
| `bit_manipulation`        |              `12` |
| `cryptarithm_guess`       |              `11` |
| `equation_numeric_guess`  |               `7` |
| `equation_numeric_deduce` |               `5` |

validation hard BIT 12 rows:

- `000b53cf`
- `0245b9bb`
- `0311b798`
- `048cc279`
- `04d8c3e6`
- `06881e47`
- `0ec17d2e`
- `1126e314`
- `12154247`
- `132ec6ae`
- `16db2c74`
- `172d2417`

この 12 行の性質:

- exact structured / abstract structured が多い。
- `binary_prompt_local_stage2_unique_exact` も含む。
- answer-only / manual も混じる。
- つまり「未解決 = 全部 manual」ではない。**verified なのに model が実行できていない行がかなりある**。

### 3.2 proxy 200 の hard rows

v4, v6, v7-1, v8, v9, v10 の 6 run 横断で、全 run wrong は `19` 行。

| family   | always wrong rows |
| -------- | ----------------: |
| `binary` |              `11` |
| `symbol` |               `8` |

proxy hard BIT 11 rows:

- `012fb81b`
- `01e09228`
- `101410e4`
- `12154247`
- `12fd5b6c`
- `1532c0d1`
- `2230fad0`
- `257e7158`
- `2d790c98`
- `31966698`
- `a6192d29`

この 11 行は 3 群に分かれる。

| group                            | IDs                                            | current evidence                           | v11 policy                                                                                    |
| -------------------------------- | ---------------------------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------- |
| exact structured but model fails | `012fb81b`, `01e09228`, `1532c0d1`, `a6192d29` | `verified_trace_ready`, exact formulaあり  | program-trace synthesis / slot-table closure                                                  |
| prompt-local / answer-only hard  | `12fd5b6c`, `2d790c98`, `31966698`             | prompt-local exact or answer-only          | query-local trace if executable object can be exported; otherwise answer-only stabilizer only |
| manual no-solver tail            | `101410e4`, `12154247`, `2230fad0`, `257e7158` | `manual_audit_priority` / no stable solver | new solver discovery before CoT; raw manual trace禁止                                         |

### 3.3 unstable no-regression rows

v11 は hard rows だけを見ても失敗する。v10 は既に「解けていた問題を壊す」ことで公式を落とした。

必須 no-regression rows:

- `0520a6ec`: v4-v9 correct, v10 wrong。最重要。
- `069dbaab`: v4/v8 correct, v10 terminal `\boxed{0}` へ崩壊。
- `c30a782a`: v6 だけ correct。v10 は v6 donor を入れても失敗。
- `59c78e51`: v10 で良い donor transfer が起きた positive control。
- `b9500f41`, `14a72508`: v9 regression から v10 で復帰した rows。
- `13009e35`, `26a70ae0`, `6a333ed6`: structured / bit_other の public-risk anchors。

v11 の gate は、hard rows の gain と no-regression rows の維持を同時に見る。

## 4. v10 の何が間違っていたか

### 4.1 frontier を足したが、procedure を教えていない

v10 の hard row 教師は、典型的には次のような短い answer commit だった。

```text
Verified binary family: choose(shl,shr,rol).
Concrete rule: choose(shl5,shr3,rol1).
Apply the same verified transformation to the query byte.
\boxed{10100001}
```

これは exact rule name と answer は与えるが、実際には query byte に rule を実行していない。model は「rule を読む」訓練は受けるが、「8-bit を計算する」訓練を受けない。

README の設計原則は「各 token を簡単に計算できるようにする」なので、v11 は answer commit ではなく、次のような実行 trace にする。

```text
Rule = choose(shl5, shr3, rol1)
x = 11010000
shl5(x) = 00000000
shr3(x) = 00011010
rol1(x) = 10100001
choose(shl5,shr3,rol1)(x) = 10100001
Final answer = 10100001
\boxed{10100001}
```

### 4.2 anti-default が `default 1` token を含んでいた

v10 の `anti_default1_commit` は以下のような文を含む。

```text
Do not use default 1, fallback bits, or guessed activations.
```

v10 proxy raw では、binary wrong `14` 行中 `12` 行に `default 1` が出ている。これはこの文だけが原因とは断定できないが、少なくとも v11 では避けるべきです。

v11 の原則:

- positive training response に `default` という語を入れない。
- 「使うな」ではなく「全 slot を計算済みにする」。
- output bit table を必ず `o0 ... o7` まで埋める。
- uncertain slot という概念を teacher trace から消す。

### 4.3 manual frontier は答えだけでは足りない

`101410e4`, `12154247`, `2230fad0`, `257e7158` は proxy で常に wrong。v10 は answer commit / manual anti-default を入れたが、全て `default 1` 系で落ちた。

これは自然です。manual rows は FINAL_SUMMARY 上も「そのまま CoT 化してよい」ではない。ここは新 solver が必要。

## 5. FINAL_SUMMARY から使うべき資産

FINAL_SUMMARY の最重要情報は、使えるデータと使ってはいけないデータの境界です。

### 5.1 BIT ledger

`bit_manipulation` final:

- total: `1602`
- `verified_trace_ready`: `1229`
- `answer_only_keep`: `271`
- `manual_audit_priority`: `87`
- `exclude_suspect`: `15`

ただし `1229 verified` 全部が procedural CoT に向くわけではない。

`BIT_MANIPULATION_STRONG_GROUP_SYNTHESIS_REFERENCE.md` の strict base:

- solver-native synthesis seed: `1004`
- exact-trace-safe base: `817`
- strict patterns: `395`

v11 はこの `817` exact-trace-safe base を主資産にする。

### 5.2 exact-trace-safe groups

| group                                             | exact-trace-safe rows | v11 use                                       |
| ------------------------------------------------- | --------------------: | --------------------------------------------- |
| `binary_structured_byte_formula`                  |                 `446` | primary synthesis / hard structured rows      |
| `binary_structured_byte_formula_abstract`         |                 `152` | exact formula only, not abstract family label |
| `binary_structured_byte_not_formula`              |                  `25` | positive donor for `59c78e51`-type closure    |
| `binary_byte_transform`                           |                  `11` | small rule family coverage                    |
| `binary_affine_xor` exact subset                  |                 `107` | equation-style bit trace                      |
| `binary_bit_permutation_bijection` exact subset   |                  `71` | mapping-table trace                           |
| `binary_bit_permutation_independent` exact subset |                   `5` | mapping-table trace                           |

What v11 must not do:

- do not use all `binary_two_bit_boolean` / `three_bit_boolean` as exact CoT unless procedure uniqueness is exported。
- do not use `answer_only_keep` as full reasoning trace。
- do not use `manual_audit_priority` as full reasoning trace。

### 5.3 symbol ledger

`symbol_equation` final:

- `110 verified`
- `1410 answer_only`
- `26 manual`
- `9 exclude`

`glyph_len5` is essentially answer-only, not trace-ready:

- `0 verified`
- `823 answer_only`
- trace-safe promotion: `0`

So v11 can include symbol as a small final-answer / character stability lane, but it should not spend mainline budget trying to make glyph trace CoT unless a new rule source is found.

## 6. v11 Core Hypothesis

v11 の仮説:

**BIT hard core は、row-level answer overlay ではなく、exact-rule synthetic program trace と bit-slot coverage によって初めて安定して動く。**

この仮説が正しければ、v11 では次が起きる。

- proxy binary が `78/92` から少なくとも `81/92`、本命では `82/92` 以上へ上がる。
- `default 1` wrong rows が v10 の `12` から `8` 以下へ下がる。
- `0520a6ec` が再び correct になる。
- `c30a782a` が v6 型に戻る。
- proxy hard core 11 行のうち、少なくとも `2-3` 行が動く。

この仮説が誤りなら、synthetic program trace を入れても:

- proxy binary は `78-80/92` に留まる。
- `default 1` は減らない。
- hard core は row-specific な memorization 以外では動かない。

## 7. v11 Data Architecture

v11 は 6 lane 構成にする。

### Lane 1. Exact Program-Trace BIT Synthesis

主戦場。`817` exact-trace-safe base から synthetic prompt + canonical program trace を生成する。

方針:

- one prompt = one concrete hidden transform。
- abstract family ではなく exact formula を書く。
- 1-2 examples の短い rule check を入れる。
- query に対して中間 byte を実行する。
- final `\boxed{answer}` は 1 回だけ。
- positive response に `default` という語を入れない。

特に厚くする formula family:

- `choose(shl,shr,rol)`
- `choose(shl,shr,ror)`
- `choose(shl,shr,nibble_swap)`
- `majority(ror,shl,shr)`
- `majority(rol,shl,shr)`
- `or(rol,shl)`
- `or(rol,shr)`
- `xor(shl,shr)`
- `binary_structured_byte_not_formula` positive closure

理由:

- hard rows に these families が多い。
- `default 1` は structured formula の一部 bit を落としたときに出る。
- v10 の answer commit では formula execution を教えられていなかった。

### Lane 2. Hard-Row Slot-Table Closure

proxy / validation hard rows そのものには、canonical slot table trace を入れる。

対象:

- proxy exact hard: `012fb81b`, `01e09228`, `1532c0d1`, `a6192d29`
- validation exact hard: `000b53cf`, `0311b798`, `048cc279`, `1126e314`, `16db2c74`, `172d2417`
- unstable no-regression: `0520a6ec`, `c30a782a`, `59c78e51`, `13009e35`, `26a70ae0`, `6a333ed6`

Trace shape:

```text
<think>
Rule = <exact executable rule>
x = <query byte>
source_a(x) = <8-bit>
source_b(x) = <8-bit>
source_c(x) = <8-bit>
o0 = <expression> = <bit>
o1 = <expression> = <bit>
...
o7 = <expression> = <bit>
Output byte = <8-bit>
Final answer = <8-bit>
</think>
\boxed{<8-bit>}
```

Important:

- all 8 output bits are computed。
- no fallback language。
- no `default 1` phrase。
- no answer-only commit for exact rows。

### Lane 3. Manual Frontier Solver Discovery

manual rows are not training rows until solved.

対象:

- `101410e4`
- `12154247`
- `2230fad0`
- `257e7158`
- validation manual hard: `0ec17d2e`
- unstable public-risk manual: `069dbaab`

やること:

1. Existing exact libraries を拡張して one-rule scan を行う。
2. Candidate rule が examples と query gold を満たしても、複数候補なら full CoT にしない。
3. unique executable rule が立った row だけ Lane 2 に昇格。
4. 立たない row は final-answer anchor のみにする。

探索すべき solver family:

- sparse slot functions over rotated/shifted/nibble sources
- 2-source / 3-source boolean with fixed source family
- small DNF/CNF over adjacent bit windows
- conditional choose/majority variants with fixed selectors
- copy/invert/constant hybrid with at most one boolean exception
- byte-mask transforms combined with rotate/shift source

`069dbaab` は special case。

- v4/v8 では correct。
- v10 では internal `00010001` のあと final `\boxed{0}` に崩壊。
- これは content と terminal surface の両方の failure。
- unique solver が立つまでは、manual full trace ではなく `exact final byte + one boxed answer` stabilizer に留める。

### Lane 4. Answer-Only Stabilizer For Non-Trace Slices

FINAL_SUMMARY の answer-only を使うが、役割を限定する。

対象:

- BIT answer-only hard: `31966698`, `04d8c3e6`, `132ec6ae` など。
- symbol numeric / glyph answer-only。
- cipher / text minor surface errors。

形式:

```text
<think>
Use the final answer exactly.
</think>
\boxed{...}
```

ただし比率は小さくする。answer-only は model に procedure を教えないため、main investment ではない。

### Lane 5. Token / Boxed Surface Guardrail

v11 は v4 rollback ではないが、surface guardrail は必要。

対象:

- numeral: v10 の `149/149` を維持。
- unit / gravity: `100%` を維持。
- cipher: `0c2243ff` のような first-character corruption を防ぐ。
- symbol prefix / suffix: `)46`, `"42`, `01` 型を抑える。

方針:

- broad symbol CoT はしない。
- small final-answer / character preservation drills のみ。
- output の box は 1 回だけ。

### Lane 6. Public-Risk Contrast Evaluation Set

v11 の本体 corpus ではなく gate 用。

current proxy は public readiness を過大評価するので、v11 では small gate を先に作る。

必須 rows:

- hard proxy 11 BIT
- validation hard BIT 12
- no-regression anchors: `0520a6ec`, `069dbaab`, `c30a782a`, `59c78e51`, `b9500f41`, `14a72508`, `13009e35`, `26a70ae0`, `6a333ed6`
- surface anchors: numeral no-box recovered rows, `0c2243ff`, `065abaf6`, `157228d7`

Gate は training 前の data selection と training 後の eval の両方で使う。

## 8. Synthetic Data Design Details

### 8.1 Bit-slot coverage

単に random 8-bit inputs を生成するだけでは足りない。

各 exact rule について、output bit ごとに以下を満たす support examples を選ぶ。

- output bit が `0` になる例。
- output bit が `1` になる例。
- source transform の結果が分岐する例。
- hard row で `default 1` が出た slot が `0` になる例。

例: `0520a6ec` の failure slot は `bit 2` で、v10 は `default 1` に逃げた。

v11 synthetic では `choose(shl5,shr3,rol1)` の prompts に、bit 2 が `0` になる support と `1` になる support を必ず含める。

### 8.2 Formula-specific quotas

v11 では broad uniform synthesis にしない。

推奨配分:

| lane                                              |    share | note                                    |
| ------------------------------------------------- | -------: | --------------------------------------- |
| exact structured program-trace synthetic          | `45-50%` | choose/majority/or/xor/nibble families  |
| hard-row slot-table closure                       | `15-20%` | hard + no-regression anchors            |
| exact affine/permutation/byte transform synthesis | `10-15%` | broad BIT stability, but already strong |
| manual solver-discovered rows                     |  `0-10%` | only if unique executable rule found    |
| answer-only stabilizer                            |   `5-8%` | symbol/BIT non-trace tail               |
| surface guardrail                                 |  `8-12%` | numeral/unit/gravity/cipher preserve    |

重要なのは、permutation を厚くしすぎないこと。proxy `bit_permutation_inversion` は v10 で `26/26` に戻っている。主戦場は structured / bit_other hard rows。

### 8.3 Remove forbidden-token positive examples

v11 accepted responses should not contain:

- `default 1`
- `fallback`
- `guessed activations`
- `uncertain`

これらは diagnostic report には書いてよいが、training completion には入れない。

## 9. Symbol Strategy

v11 で symbol を主戦場にしない理由:

- v4-v10 proxy symbol はずっと `24/32`。
- v8 は symbol を増やしても動かなかった。
- FINAL_SUMMARY では `glyph_len5` は `0 verified / 823 answer_only`。
- trace-safe な glyph rule はまだ無い。

ただし完全に捨てない。

やること:

- `numeric_2x2` の prefix/suffix corruption を final-answer drill で抑える。
- `glyph_len5` は answer-only boxed exact を少量。
- 文字列・記号を 1 文字ずつ維持する drill を low ratio で入れる。

やらないこと:

- glyph full CoT を作らない。
- answer-only glyph を大量 repeat しない。
- symbol を BIT mainline 予算と競合させない。

## 10. v11 Evaluation Gates

v11 は local validation total で昇格させない。

### Hard minimum

- validation total: `>= 839/950`
- validation BIT: `>= 153/169`
- proxy total: `>= 181/200`
- proxy binary: `>= 82/92`
- proxy `default 1` wrong rows: `<= 8`
- proxy hard BIT 11 rows: at least `3` converted to correct
- `0520a6ec`: correct mandatory
- `069dbaab`: not worse than v4/v8; no `\boxed{0}` terminal collapse
- `c30a782a`: correct target; at minimum no new bad-format / no worse than v4
- numeral/unit/gravity: no regression from v10

### Promote-to-official condition

Before official submission, v11 must pass:

1. README-contract proxy.
2. hard-row mini gate.
3. synthetic heldout generated from exact-trace-safe formulas not used in training.
4. raw-output scan:
   - `default 1` count
   - bad binary format count
   - multiple boxed count
   - final `\boxed{0}` collapse

Official promotion only if v11 beats v4 on **both**:

- public-risk mini gate
- proxy binary

The goal is not `0.86 once`; the target is `0.87` stable. So v11 must produce a clear BIT movement before official slots are spent.

## 11. Suggested Run Plan

Because one training run is expensive, v11 should be built as one mainline plus two quick ablation branches if resources allow.

### v11-main: exact program-trace BIT synthesis

Include:

- Lane 1 exact program-trace synthesis from `817` base.
- Lane 2 hard-row slot-table closure.
- Lane 4 small answer-only stabilizer.
- Lane 5 surface guardrail.

Exclude:

- raw manual frontier full CoT.
- anti-default text containing `default 1`.
- broad matching auxiliary.
- broad symbol CoT.

This is the main candidate.

### v11-manual-solver side branch

Only if Lane 3 produces unique executable rules for manual rows.

Include newly solved manual rows such as:

- `101410e4`
- `12154247`
- `2230fad0`
- `257e7158`
- `0ec17d2e`
- `069dbaab`

If no unique rule is found, do not run this branch.

### v11-token-surface side branch

Diagnostic only.

Purpose:

- measure whether small symbol / character final-answer drill can improve public blind spot without hurting BIT.

This should never replace v11-main unless BIT gates are already met.

## 12. Implementation Requirements

When implementing v11, keep it as one file, consistent with repo instruction.

Suggested file:

- `versions/v20_corrective_corpus_v11_stable_frontier/reproduce_v20_corrective_corpus_v11_stable_frontier.py`

Required capabilities:

1. Load `train_row_analysis_v1.csv`.
2. Select exact-trace-safe `817` rows.
3. Export exact executable metadata per row.
4. Generate synthetic prompts from one exact rule at a time.
5. Render canonical program trace.
6. Quality-gate generated rows:
   - one `\boxed{}`
   - exact answer
   - exact solver re-recovers same rule
   - no forbidden tokens in completion
7. Build one single-file training bundle.
8. Emit selection CSV, summary JSON, and strategy report.

## 13. Expected Outcome

If v11 works, the first visible signs should be:

- `0520a6ec` fixed again.
- `c30a782a` becomes v6-style correct.
- at least one of `012fb81b`, `01e09228`, `1532c0d1`, `a6192d29` flips.
- `default 1` raw count falls.
- validation BIT rises above the persistent `149-150/169` ceiling.

If these do not happen, v11 should be considered falsified even if validation total stays high.

## 14. Final Decision

v11 should not be framed as a safer v10. It should be a different bet:

**teach executable BIT programs, not row answers.**

The v10 failure is valuable because it shows the current approach has hit the limit of row-level overlay. To reach stable official `0.87`, the next step must attack the actual unsolved capability: selecting and executing exact 8-bit transformations without falling back to `default 1`.

That means v11's success condition is not local validation recovery. It is hard BIT movement under raw-output inspection.
