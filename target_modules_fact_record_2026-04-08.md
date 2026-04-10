# target_modules Fact Record 2026-04-08

この文書は、LoRA の target_modules に関して、この会話で確認した内容を出典ごとに事実のみで整理した記録である。推奨、評価、解釈、優先順位づけは含めない。

## 1. 競技 README にある事実

出典: README.md

- 参加者は、LoRA アダプタを作成するために任意の training framework、tooling、workflow を使用できる。
- NVIDIA 提供レシピは optional starting points とされている。
- 最終提出物に対する要件は、Nemotron-3-Nano-30B base model と互換な LoRA adapter を生成することである。
- 提出物は submission.zip に格納された LoRA adapter である必要がある。
- 評価時の制約として max_lora_rank は 32 である。
- README 内で target_modules の具体値は規定されていない。

該当箇所の抜粋:

> Participants may use any training framework, tooling, or workflow to produce their LoRA adapter.

> The only requirement is that the final submission produces a compatible LoRA adapter for the Nemotron-3-Nano-30B base model.

> max_lora_rank 32

## 2. リポジトリ内ノートブックにある事実

### 2.1 baseline 単発SFTノートブック

出典: baseline/nemotron-sft-lora-with-cot-v2/nemotron-sft-lora-with-cot-v2-original.ipynb

- LoRA 設定は LoraConfig で定義されている。
- r は 32 である。
- lora_alpha は 32 である。
- target_modules は正規表現文字列 r".*\.(in_proj|out_proj|up_proj|down_proj)$" である。
- lora_dropout は 0.05 である。
- bias は "none" である。

該当コード:

```python
lora_config = LoraConfig(
    r=LORA_RANK,
    lora_alpha=LORA_ALPHA,
    target_modules=r".*\.(in_proj|out_proj|up_proj|down_proj)$",
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)
```

### 2.2 ルールベース CoT baseline ノートブック

出典: baseline/cot/train_rule_based_cot_baseline.ipynb

- target_modules は "all-linear" である。

該当行:

```python
target_modules="all-linear",
```

### 2.3 NVIDIA submission demo ノートブック

出典: baseline/nvidia-nemotron-submission-demo.ipynb

- target_modules は正規表現文字列 r".*\.(in_proj|out_proj|up_proj|down_proj)$" である。

該当行:

```python
target_modules=r".*\.(in_proj|out_proj|up_proj|down_proj)$",
```

## 3. リポジトリ内 Nemotron 向け補助資料にある事実

出典: how-to-get-started-transformers.md

- この資料では、Nemotron 側の target_modules 名として次を列挙している。
- attention: q_proj, k_proj, v_proj, o_proj
- MLP/MoE: up_proj, down_proj
- Mamba: in_proj, out_proj
- 同資料では gate_proj は見当たらないとしている。
- 同資料では、target_modules は Nemotron 実装に合わせる必要があるとしている。
- 同資料のレシピでは q_proj, k_proj, v_proj, o_proj, up_proj, down_proj, in_proj, out_proj のみを使い、gate_proj は使わないとしている。

該当箇所の抜粋:

> attention: q_proj, k_proj, v_proj, o_proj

> MLP/MoE: up_proj, down_proj

> Mamba: in_proj, out_proj

> gate_proj は見当たりません

> target_modules は Nemotron 実装に合わせる必要があります。このレシピでは q_proj/k_proj/v_proj/o_proj/up_proj/down_proj/in_proj/out_proj のみを使い、gate_proj は使いません。

## 4. PEFT 公式 LoRAConfig ドキュメントにある事実

出典: https://huggingface.co/docs/peft/package_reference/lora

- LoraConfig の target_modules は Optional[Union[List[str], str]] である。
- target_modules に文字列を渡した場合、regex match が行われる。
- target_modules に文字列リストを渡した場合、exact match または suffix match が行われる。
- target_modules を all-linear とした場合、PreTrainedModel では output layer を除く全 linear/Conv1D modules が選択される。
- target_modules が未指定の場合、モデルアーキテクチャに応じて自動選択される。アーキテクチャが既知でない場合は error が発生し、この場合は手動指定が必要とされる。
- exclude_modules という別指定が存在する。
- bias は none、all、lora_only を取り得る。
- use_dora という設定項目が存在する。
- target_parameters という別設定項目が存在する。
- 公式ドキュメントには、many mixture of expert layers in HF Transformers では nn.Linear ではなく nn.Parameter が使われる場合があり、その場合は target_modules ではなく target_parameters を使う必要があると記載されている。

該当箇所の抜粋:

> When passing a string, a regex match will be performed.

> When passing a list of strings, either an exact match will be performed or it is checked if the name of the module ends with any of the passed strings.

> If this is specified as 'all-linear', then all linear/Conv1D modules are chosen (if the model is a PreTrainedModel, the output layer excluded).

> In many mixture of expert (MoE) layers in HF Transformers, instead of using nn.Linear, an nn.Parameter is used.

## 5. Nemotron-3-Nano-30B-A3B-BF16 公式モデルカードにある事実

出典: https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16

- モデル名は NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 である。
- モデルは unified model for both reasoning and non-reasoning tasks と記載されている。
- reasoning capabilities は chat template の flag により設定可能と記載されている。
- モデルは hybrid Mixture-of-Experts architecture と記載されている。
- モデルカードには、23 Mamba-2 layers、23 MoE layers、6 Attention layers、合計 52 layers と記載されている。
- 各 MoE layer は 128 routed experts plus 1 shared expert を含み、6 experts activated per token と記載されている。
- モデルは total 30B parameters、active 3.5B parameters と記載されている。
- Quick Start Guide では Transformers で trust_remote_code=True を使う例が記載されている。
- Quick Start Guide では vLLM 利用例も記載されている。
- model card の Quick Start Guide では、デフォルト context size は Hugging Face configuration では 256k、model support は up to 1M context size と記載されている。

該当箇所の抜粋:

> The model employs a hybrid Mixture-of-Experts (MoE) architecture, consisting of 23 Mamba-2 and MoE layers, along with 6 Attention layers.

> The model has 3.5B active parameters and 30B parameters in total.

> There are a total of 52 layers, of which there are 23 of each MoE and Mamba-2 and the remaining 6 layers use grouped query attention (GQA) with 2 groups.

## 6. Transformers の Nemotron ドキュメントにある事実

出典: https://huggingface.co/docs/transformers/model_doc/nemotron

- Transformers docs には NemotronConfig が存在する。
- NemotronConfig には attention_bias と mlp_bias という設定項目がある。
- attention_bias は query, key, value, output projection layers に対する bias の有無として説明されている。
- mlp_bias は up_proj, down_proj, gate_proj layers に対する bias の有無として説明されている。

該当箇所の抜粋:

> attention_bias: Whether to use a bias in the query, key, value and output projection layers during self-attention.

> mlp_bias: Whether to use a bias in up_proj, down_proj and gate_proj layers in the MLP layers.

## 7. この記録で確認できる比較対象

この会話で確認した target_modules の指定パターンは次の 3 つである。

- 4 層限定: in_proj, out_proj, up_proj, down_proj
- Nemotron 向け明示 8 層: q_proj, k_proj, v_proj, o_proj, up_proj, down_proj, in_proj, out_proj
- all-linear

このうち、リポジトリ内で実際に確認した指定は次のとおりである。

- 4 層限定は baseline/nemotron-sft-lora-with-cot-v2/nemotron-sft-lora-with-cot-v2-original.ipynb と baseline/nvidia-nemotron-submission-demo.ipynb に存在する。
- 8 層明示は how-to-get-started-transformers.md の記述として存在する。
- all-linear は baseline/cot/train_rule_based_cot_baseline.ipynb に存在する。

## 8. この記録に含めていない内容

- 3 つの target_modules 指定に関する精度比較結果
- 3 つの target_modules 指定に関する trainable parameter 数の実測値
- 3 つの target_modules 指定に関する VRAM 使用量の実測値
- 3 つの target_modules 指定に関する学習時間の実測値

上記 4 点は、この文書作成時点では、この会話で Web 取得またはローカル読取により確認した事実としては追加していない。
