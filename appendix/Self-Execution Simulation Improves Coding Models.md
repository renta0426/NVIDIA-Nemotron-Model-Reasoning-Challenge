Sections:
Abstract
1 Introduction
2 Boosting Execution Simulation
    2.1 Natural Language Execution Tracing ( NLEX )
    2.2 Output Prediction Environment
3 Self-Execution For Verification
4 Self-Execution For Fixing
5 Experimental Setup
    5.1 Datasets
        5.1.1 Training datasets
        5.1.2 Evaluation datasets
    5.2 Trained Models
6 Results
    6.1 Output Prediction
    6.2 Self-Execution for Competitive Programming
        Self-verification.
        Self-RLEF.
    6.3 Ablations
    6.4 Beyond Self -Verification
7 Related Work
    Code Simulation & Verification.
    Learning from Feedback.
8 Discussion
9 Conclusion
Impact Statement
References
Appendix A Appendix.
    A.1 Additional Results
        A.1.1 Supervised fine-tuning.
        A.1.2 The effect of RL on output prediction
        A.1.3 Self-Verification
        A.1.4 Self-RLEF
        A.1.5 Beyond Self -Verification
    A.2 Self-RLEF Example Inference
    A.3 Hyper-Parameters
        Supervised Fine-Tuning.
        Reinforcement Learning.
    A.4 Prompts
    A.5 Data Samples

Files Content:

## Contents
- 1 Introduction
- 2 Boosting Execution Simulation
  - 2.1 Natural Language Execution Tracing ( NLEX )
  - 2.2 Output Prediction Environment
- 3 Self-Execution For Verification
- 4 Self-Execution For Fixing
- 5 Experimental Setup
  - 5.1 Datasets
    - 5.1.1 Training datasets
    - 5.1.2 Evaluation datasets
  - 5.2 Trained Models
- 6 Results
  - 6.1 Output Prediction
  - 6.2 Self-Execution for Competitive Programming
    - Self-verification.
    - Self-RLEF.
  - 6.3 Ablations
  - 6.4 Beyond Self -Verification
- 7 Related Work
  - Code Simulation & Verification.
  - Learning from Feedback.
- 8 Discussion
- 9 Conclusion
- Impact Statement
- References
- Appendix A Appendix.
  - A.1 Additional Results
    - A.1.1 Supervised fine-tuning.
    - A.1.2 The effect of RL on output prediction
    - A.1.3 Self-Verification
    - A.1.4 Self-RLEF
    - A.1.5 Beyond Self -Verification
  - A.2 Self-RLEF Example Inference
  - A.3 Hyper-Parameters
    - Supervised Fine-Tuning.
    - Reinforcement Learning.
  - A.4 Prompts
  - A.5 Data Samples

## Abstract

Abstract A promising research direction in enabling LLMs to generate consistently correct code involves addressing their inability to properly estimate program execution, particularly for code they generate. In this work, we demonstrate that code LLMs can be trained to simulate program execution in a step-by-step manner and that this capability can be leveraged to improve competitive programming performance. Our approach combines supervised fine-tuning on natural language execution traces, textual explanations grounded in true execution, with reinforcement learning using verifiable rewards. We introduce two complementary objectives: output prediction given code and inputs, and solving competitive programming tasks with either ground-truth or self-predicted execution feedback. These objectives enable models to perform self-verification over multiple candidate solutions, and iterative self-fixing by simulating test execution. Across multiple competitive programming benchmarks, our method yields consistent improvements over standard reasoning approaches. We further present ablations and analysis to elucidate the role of execution simulation and its limitations.

## 1 Introduction

Going beyond treating code as a static text block holds great promise in advancing code LLMs. This involves jointly modelling program syntax and execution dynamics, similar to how developers reason during debugging and development (Armengol-Estapé et al., 2025; Li et al., 2025; Thimmaiah et al., 2025; Copet et al., 2025; Beck et al., 2026).
Despite its promise, translating execution prediction capabilities into consistent gains on practical programming tasks remains an open challenge. Moreover, Gu et al. (2024a); Olausson et al. (2024); Kamoi et al. (2024) indicate that current models often fail to faithfully simulate runtime behaviour or to consistently identify and explain errors in code they generate.

Code execution is widely used in various parts of training and inference of code LLMs. This includes feedback from code execution (Gehring et al., 2025; Peng et al., 2025) or rich tool-based signals in agentic settings (Xia et al., 2025). However, executing code at scale for training or inference poses practical challenges, such as environment setup (Bogin et al., 2024), managing code dependencies (Jimenez et al., 2023), handling partial or non-executable code, and sandboxing. In broader settings, program execution can also be computationally expensive and time-consuming; for example, runs of MLE-Bench can take up to $9$ hours (Chan et al., 2024; Zheng et al., 2026). Predicting execution outcomes could mitigate these challenges by enabling large rollouts and policy optimisation without code execution (MiniMax, 2026; Kimi et al., 2025). More broadly, using execution prediction to support reasoning and planning in coding tasks can be viewed as a form of world modelling in the code domain (Ha and Schmidhuber, 2018; Ding et al., 2025).

Figure: Figure 1: A conceptual outline of how one can use *self-execution simulation* of a generated code solution (or solutions) on public or generated test cases to improve coding performance. The simulation can be used as feedback to select the best solution from a few candidates (best@k) or to iteratively fix the code as needed (self-RLEF). See Section [3](#S3) for details.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x1.png

In this work, we take a step in this direction. We show LLMs can learn to simulate program execution step-by-step, including code they generated, and use this capability to improve competitive programming performance. We start by training models on natural-language execution traces – text explanations grounded in real program executions – and then further refining them using single-turn reinforcement learning for code output prediction. Equipped with this capability, we empirically demonstrate how models can perform *self-verification* over parallel solutions based on simulated execution (best@k). Inspired by Gehring et al. (2025), we also design a multi-turn reinforcement learning pipeline that enables iterative *self-fixing* through code proposal, execution simulation, and refinement. [Figure 1](#S1.F1) provides a conceptual overview of the proposed methods.

Results suggest the proposed training recipe leads to significant improvements in output prediction on CruxEval (Gu et al., 2024b) (up to $43\%$) and competitive programming solutions (Li et al., 2022; Jain et al., 2024) (up to $39\%$) relative to the evaluated baseline. This applies to both external and self-generated code solutions. Under the best@k setting, using the model’s output prediction to verify its own candidate solutions improves code correctness by up to $5.5\%$ absolute points on competitive programming tasks. In the multi-turn setting, we observe consistent gains across all evaluated configurations. Compared to ground-truth execution, both best@k and multi-turn variants show a relatively small degradation. Finally, we conduct analysis to highlight the strengths and limitations of the proposed approach.

Our Contributions: We provide a training recipe, showing that code LLMs are capable of simulating the program execution for both external and self-generated code. With that in mind, we introduce a practical framework for leveraging this behaviour by filtering code solutions based on predicted output (i.e., self-verification). Lastly, we present a multi-turn training and inference process to perform iterative self-fixing of the model’s generated code.

Figure: Figure 2: The two parts of our training pipeline. 1) Supervised fine tuning on natural language execution traces (NLEX), 2) Multi-task reinforcement learning on output prediction and competitive programming (optionally with multi-turn feedback and fixing).
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x2.png

## 2 Boosting Execution Simulation

Following Copet et al. (2025), we collect executable Python programs with input–output pairs and record their line-by-line execution. Next, we convert these execution traces into natural-language explanations and use the resulting data for supervised fine-tuning. We then further train the model using verifiable rewards on an output prediction task. The next sections describe these post-training steps in detail.

### 2.1 Natural Language Execution Tracing ( NLEX )

We collect Python functions from public repositories and automatically synthesise suitable inputs using a combination of LLM prompting and lightweight fuzzing techniques. In addition, we collect LLM-generated solutions to competitive programming problems from CodeContests (Li et al., 2022), and keep their provided tests as inputs. Although this portion of the data is smaller in scale, it involves substantially more complex programs. We then record execution traces for each program–input pair, capturing intermediate variable states throughout execution. Following Copet et al. (2025), we exclude traces exceeding $10\text{k}$ events or requiring more than $1\text{MB}$ of storage. The resulting dataset comprises ${\sim}30\text{M}$ functions from basic code sources and $35\text{k}$ from competitive programming problems. For all of the above, we use Llama3-70B-Instruct (Grattafiori et al., 2024).

While CWM (Copet et al., 2025) focused primarily on a structured, JSON-like format to describe the step-by-step execution, we wish to focus on natural language description of this data. Relative to the structured format, a free-form variant holds several benefits. First, as based on natural language, it closely matches the reasoning-style data already used by LLMs. It also enables adding semantic context to operations, e.g., explaining an update to an array in the scope of a dynamic programming code. Finally, it naturally abstracts away unnecessary details, such as summarising a long loop that reverses strings character by character.

To this end, we prompt Qwen3-32B-FP8 (without thinking) (Yang et al., 2025) to “translate” execution traces from raw structured format to a natural language explanation. See Appendix [A.4](#A1.SS4) for the exact prompt. We discard instances where the model’s predicted output does not match the ground truth, resulting in ${\sim}80$ M execution descriptions for general Python functions and $115$ k for competitive programming solutions (notice, each traced function may contain several io-pairs). The resulting data is formatted as instruction-following examples and used for model fine-tuning during the SFT phase. In which, the user requests a step-by-step explanation of a program’s execution for a given input, and the assistant provides the translated explanation. Sample instances are provided in Appendix [A.5](#A1.SS5).

### 2.2 Output Prediction Environment

Following standard practice in reasoning models, we post-train our model using Reinforcement Learning with Verifiable Rewards (RLVR). We define an output prediction environment, based on coding tasks, where the model reasons over a given (code, stdin) pair to predict the resulting stdout. We employ a terminal binary reward, scoring $+1$ if the prediction matches the true stdout, and $-1$ otherwise, allowing $1e-5$ tolerance in float comparisons.

The intended downstream use of the output prediction ability is simulating the execution of model generated solutions to competitive programming questions. To that end, we construct the output prediction environment on precisely such data. We collect solutions from strong LLMs to competitive programming questions and use the stdin of the matching public tests. Moreover, the higher difficulty of competitive programming problems makes them particularly well suited for post-training. [Figure 2](#S1.F2) depicts the optimisation pipeline.

## 3 Self-Execution For Verification

Given models with increased ability to simulate code execution, we ask *“How can this ability be used to boost programming abilities?”* Arguably, the simplest and most straightforward approach to leverage such capability is through post-hoc solution filtering. In this approach, candidate solutions are simulated on public or generated tests and retained only if their predicted outputs align with the expected ones.

For that, we adopt a best-of-$k$ (best@$k$) evaluation setup, where the model independently samples $k$ candidate solutions and selects the final one based on predefined criteria. In our setup, selection is based on the model’s execution prediction. In other words, for each candidate, the model simulates its execution on public test cases and checks whether the predicted outputs match the expected ones. The candidate predicted to pass the greatest number of public tests is selected for submission. In case of a tie we randomly select a solution among the ones that passed the maximum number of tests. We denote this approach best@k simulate. Notice, during inference we do not access any private tests nor ground-truth verification.

Formally, given a set of solutions $\mathcal{S}$, with public input-output pairs $(in_{t},out_{t})\in\mathcal{T}$, we use a model to simulate execution, predict the output $\mathcal{M}_{\text{sim}}(s,in_{t})$, and select:

$$ $\mathrm{Best}(\mathcal{S})\coloneqq\operatorname*{arg\,max}_{s\in\mathcal{S}}\sum_{(in_{t},out_{t})\in\mathcal{T}}\mathbf{1}\!\left[\mathcal{M}_{\text{sim}}(s,in_{t})=out_{t}\right].$ $$

We use rank_score_at_k (Hassid et al., 2024) to provide an unbiased accuracy estimate for generating $k$ solutions and selecting the one with the highest score under the proposed heuristic. Specifically, we use $20$ generated solutions per task and $5$ output-prediction attempts per test.

Recall, the primary focus of this work is *self*-simulation. In which, the same LLM is used to both generate candidate solutions and simulate their execution. That said, the same method can also be applied to solutions produced by other models. In [Section 6](#S6), we present empirical evidence demonstrating the efficacy of this approach in both setups.

## 4 Self-Execution For Fixing

Another approach to leveraging execution feedback is through multi-turn interaction with a computational environment to perform code fixing. Gehring et al. (2025) demonstrated that exposing LLMs to environmental feedback can enhance programming performance by allowing models to iteratively refine solutions based on information from failed test cases. However, as mentioned above, this may introduce practical challenges such as environment configuration, code dependencies, and non-executable code.

Motivated by this paradigm, we introduce an approach that uses predicted execution outputs as feedback instead of actual program execution. Note, unlike the method presented in [Section 3](#S3), that verifies multiple solutions via self-execution, the multi-turn setup refines solutions sequentially based on predicted feedback. Ideally, this approach can leverage richer signals, such as past solutions and execution details.
While similar world-modelling approaches have been explored in vision, recent work shows limited gains from such signals (Qian et al., 2026). In contrast, we show that using execution simulation can improve performance.

Figure: Algorithm 1 Multi-Turn Self-RLEF Rollout

Specifically, we propose a multi-turn environment with explicit context switching, i.e. where each interaction step is represented as an independent single-turn prompt containing only the relevant information (see details in the bullets below). This design enables fine-grained control over information flow. For instance, ensuring that execution simulation is isolated from solution reasoning and from access to the correct outputs. Moreover, it mitigates long-context challenges commonly associated with multi-turn reasoning (Yao et al., 2022). Finally, this context switching also naturally allows one to extend the number of fix turns at inference as each fix turn is independent. A formal description of the rollout procedure is provided in Algorithm [1](#alg1), and an example inference of our model in Appendix [A.2](#A1.SS2).
In words, the multi-turn setup is designed as follows:

- •
Turn 1 - Solve - Given a question, provide a code solution to solve the provided question.
- •
Turn 2 - Simulate - Given a code snippet and a test input, simulate the execution and predict the output that will be printed to the standard output. This step is performed independently for each public test.
- •
Turn 3 - Submit or Fix - Given a question, a candidate solution and feedback about each test (input, expected output, predicted output), decide whether the code is correct or not. If correct, submit the code solution, otherwise, fix the code to provide a new solution.
- •
Optional - Repeat turns 2 and 3 until a code solution is submitted or the maximum turns are reached.

Since the model’s ability to accurately predict execution outcomes may be weak at the start of RL training, relying solely on self-predicted feedback could lead the model to disregard this noisy signal. To mitigate this, we initially provide ground-truth execution feedback during training. As training progresses, one might switch from true execution signals to model-predicted execution outputs (Bengio et al., 2015). Alternatively, transition can also be deferred entirely to inference time. Our preliminary results showed no noticeable gap between the approaches, so we use the latter for simplicity. We denote the following approach *Self-RLEF*.

## 5 Experimental Setup

### 5.1 Datasets

We describe all datasets and configurations used to train and evaluate our models and baselines below. Note that each problem in competitive programming usually includes between one and four public test cases, typically provided in the problem description. These serve as basic checks for correctness and output formatting. In addition, a larger set of private tests, unavailable to the model, is used to better assess solution correctness, including coverage of edge cases and compliance with runtime constraints.

#### 5.1.1 Training datasets

The NLEX dataset, as presented in [Section 2.1](#S2.SS1), was used for supervised fine-tuning, together with OpenMathReasoning (Moshkov et al., 2025) and OpenCodeReasoning (Ahmad et al., 2025) datasets, to bootstrap reasoning abilities.

During RL, models were optimised for both solving and predicting the output of competitive programming solutions. For that, we use the training split derived from CodeContests (Li et al., 2022), after heuristically filtering malformed instances, which results in ${\sim}12.2$k problems. For output prediction, we sample $10$ candidate solutions and retain up to four correct ones per model, since all correct submissions yield identical outputs. We then pair each retained solution with all of its public test cases, treating each as an output prediction instance, resulting in a total of ${\sim}143k$ code–input–output examples. All solutions were generated using CWM and Qwen2.5-7B (Qwen et al., 2025).

Figure: Figure 3: CruxEval-O performance compared to model active parameters. Arrows demonstrate the benefit from training on NLEX data. We also compare to open models.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x3.png

#### 5.1.2 Evaluation datasets

We present evaluation datasets for competitive programming questions (first two), and output prediction (last two).

LCB-IO. We curate a subset from LiveCodeBench-v6 (Jain et al., 2024) containing only problems evaluated via stdio tests, which we refer to as LCB-IO. This restriction simplifies output prediction, as the task reduces to determining the content written to stdout given a specific stdin. The resulting set includes $287$ problems.

DMC. We follow Gehring et al. (2025) and use the validation and test splits of CodeContests (Li et al., 2022), yielding an additional evaluation set with a different distribution, denoted DMC, and consisting of $282$ problems.

CruxEval-O (Gu et al., 2024b) is a widely adopted benchmark consisting of short Python functions paired with input–output examples. The task requires the model to infer the function’s return value given the code and its input.

Output prediction for competitive programming. We generate $20$ solutions per-question from both DMC and LCB-IO using the same LLMs as mentioned above, without filtering or de-duplicating solutions, to perfectly match the real distribution of generated solutions. Such data is also used for best@k type metric calculations.

### 5.2 Trained Models

We post-train Qwen2.5-Base models of sizes $3$B and $7$B, together with CWM-base using the datasets described in [Section 5.1.1](#S5.SS1.SSS1). For RL we use an asynchronous RL infrastructure, adopting the same RL algorithm as in CWM, with different hyperparameters. When performing multi-task training we employ sample-level weighting. Furthermore, we apply reward scaling, following Ruan et al. (2025), assigning a weight of $0.8$ to the output prediction objective. For all multi-turn repair environments, including self-RLEF, we allow a maximum of one repair attempt during training (two solution turns in total, including the initial attempt), and $9$ at inference (overall $10$ turns). Full training configurations, including hyperparameters, are provided in Appendix [A.3](#A1.SS3).

Figure: Figure 4: Best@k performance of *self-verification* with *self-simulation*. Solutions and output predictions are produced by the same model - based on Qwen2.5-7B or CWM, trained for both solving and output prediction. Even though the tests used for filtering are in the solve prompt, there is still room for notable gains from simulating them.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x4.png

**Table 1: Output prediction performance of Qwen models trained with RLVR for output prediction, with and without NLEX data.**
| Base Model | LCB-IO-Out | DMC-Test-Out |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  | pass@1 | @5 | @10 | @1 | @5 | @10 |
| Qwen-7B (ours) | 79.7 | 89.4 | 91.1 | 77.3 | 89.3 | 91.6 |
| w.o NLEX | 75.7 | 87.8 | 89.7 | 71.8 | 87.0 | 89.9 |
| Qwen-3B (ours) | 66.4 | 80.6 | 83.9 | 59.4 | 78.2 | 82.8 |
| w.o NLEX | 57.1 | 74.2 | 78.3 | 45.9 | 66.2 | 72.4 |

## 6 Results

### 6.1 Output Prediction

CruxEval-O. We start by evaluating performance considering CruxEval-O. Results are presented in [Figure 3](#S5.F3). We evaluate both Qwen2.5-3B and Qwen2.5-7B (after SFT only), trained with and without the NLEX data. For reference we provide pass@1 scores of common open-weights LLMs. Results show a clear superiority of the NLEX data as part of the training mix, achieving comparable performance to significantly larger models, with Qwen2.5-3B increasing from $37.5$ to $68.0$ and Qwen2.5-7B improving $48.5$ to $75.5$ pass@1 scores. We provide results for standard coding metrics in Appendix [A.1](#A1.SS1), showing no regression in performance considering other benchmarks and tasks.

Competitive programming. Next, we evaluate output prediction performance on LLM solutions to competitive programming questions from LCB-IO and DMC (test split). Compared to CruxEval-O, these functions are often more complex and challenging. For that, we consider post-trained Qwen2.5 models (3B and 7B) on the task of output-prediction. Similarly to before, we consider models trained with and without NLEX data as part of the mix. Results presented in Table [1](#S5.T1) suggest that including NLEX data as part of the mix boosts output-prediction capabilities also after RL. While RL on output prediction with a standard reasoning SFT data (i.e., OMR and OCR) shows impressive performance, mixing them with NLEX provides superior results across both model sizes. To understand the effect of the RL phase, we additionally evaluate CWM on output prediction with and without RL. As expected, the RL phase significantly improves results on output prediction, see Appendix [A.1.2](#A1.SS1.SSS2) and Table [8](#A1.T8) for more details.

Self-execution prediction. So far we evaluated output-prediction capabilities on code generated by external models. We now turn to evaluate *self-execution*, i.e. models perform output-prediction on their own generated solutions. For that we post-train CWM and Qwen2.5-7B on both output prediction and competitive problems solving. We report results for questions derived from both LCB-IO and DMC in Table [2](#S6.T2) and compare performance to models trained to perform output-prediction only (as a topline) and to the official CWM model (as a baseline). As expected, results suggest that jointly training both models for solving competitive programming questions and output prediction perform worse than output prediction only. For instance, CWM reaches $80.2$ and $86.5$ pass@1 scores in joint training compared to $85.0$ and $88.6$ scores when trained for output prediction only. However, both are significantly superior to the official CWM model, that reaches $57.7$ pass@1. Interestingly, these results suggest that unlike previous findings (Gu et al., 2024a) models can reliably perform self-execution.

**Table 2: Output prediction performance for models trained on standard code solving, jointly with output prediction (Joint), on their own solutions. We compare this to a model trained for output prediction only, models from Tab. [1](#S5.T1), (Out Pred), and official CWM.**
| Model | RL obj. | DMC-Out | LCB-IO-Out |  |  |
| --- | --- | --- | --- | --- | --- |
|  |  | @1 | @5 | @1 | @5 |
| CWM | official | 57.7 | 80.4 | 68.6 | 87.9 |
|  | Joint | 80.2 | 87.2 | 86.5 | 91.0 |
|  | Out Pred | 85.0 | 89.8 | 88.6 | 92.7 |
| Qwen-7B | Joint | 68.4 | 83.1 | 76.5 | 87.1 |
|  | Out Pred | 74.6 | 86.8 | 80.1 | 89.2 |

### 6.2 Self-Execution for Competitive Programming

**Table 3: Solve rates for training and evaluating with a standard reasoning approach vs using real or simulated execution feedback.**
|  | DMC | LCB-IO |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | pass@1 | pass@5 | pass@10 | public | pass@1 | pass@5 | pass@10 | public |
| Execution RLEF (Oracle) | 65.3 | 77.6 | 80.6 | 86.1 | 63.8 | 70.9 | 72.8 | 88.5 |
| CWM (official) | 49.0 | 63.7 | 67.9 | 60.8 | 57.4 | 67.3 | 70.1 | 71.4 |
| CWM RL | 60.8 | 72.8 | 76.0 | 74.7 | 61.0 | 67.6 | 69.2 | 82.9 |
| Self-RLEF (Ours) | 63.2 | 76.8 | 80.2 | 82.5 | 62.3 | 70.0 | 71.9 | 87.1 |

##### Self-verification.

Given a model’s prediction of the execution output of its own code on public tests, one can use this to self-verify the solutions. Specifically, following the best@k simulate approach described in [Section 3](#S3), we select and submit the solution predicted to pass most tests. To better estimate the effectiveness of the proposed method, we compare it to short1@k (Hassid et al., 2025), which selects the shortest response among the $k$ solutions, and pass@k (for reference). To directly assess the quality of execution simulation, we also compare against an oracle that executes the public tests, following the same filtering procedure (denoted best@k exec). This comparison will provide us with the *simulation gap*, i.e., the performance gap between fully executing the code vs. simulating it with the model.
Our results provided in Fig. [4](#S5.F4) show that self-verification provides a large boost in performance under the best@k setup, ($2-8$ points compared to standard solving), *despite the tests used for filtering being provided when generating the solution*. This also outperforms short1@k. Notably, for Qwen2.5-7B the simulation gap is larger than CWM perhaps implying the need for larger or stronger models to learn to both solve and simulate execution effectively. Further results in Fig. [9](#A1.F9) show that using Qwen2.5-7B trained for output prediction only to filter the same solutions leads to a smaller gap.

##### Self-RLEF.

We train our model using the procedure described in [Section 4](#S4). We report pass@k scores for $k\in\{1,5,10\}$ on both LCB-IO and DMC, along with public-test pass rates. We evaluate three variants: the official CWM model, CWM post-trained specifically for competitive programming (CWM-RL), and CWM jointly optimised for output prediction and competitive programming with execution feedback. The latter is evaluated under the proposed self-RLEF framework, using either simulated execution or real execution as an oracle. In both settings, the model is allowed up to $10$ coding turns (initial solution + $9$ fix), although in practice, it uses $3.33$ turns on average (Appendix [A.1.4](#A1.SS1.SSS4) provides additional results with less turns). Results in [Table 3](#S6.T3) show that self-RLEF consistently outperforms both the official CWM and CWM-RL across all settings, improving pass rates on both public and private tests. Compared to the oracle, a performance gap remains, particularly for pass@1, indicating room for improvement in execution prediction. Interestingly, pass@1 scores (with 10 turns) are lower than the corresponding best@10 results shown in [Figure 4](#S5.F4). We hypothesise that this gap arises from limited exploration, as the model tends to iteratively fix a solution rather than explore alternative ones. In addition, the model frequently does not use all turns as seen by the average number of turns. For certain settings where an ”early exit” is preferred this approach can provide a better tradeoff considering compute.

### 6.3 Ablations

**Table 4: Comparing performance of using the self-RLEF scaffold at inference only with open source reasoning models.**
|  | DMC | LCB-IO |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Model \ Pass | @1 | @5 | @10 | @1 | @5 | @10 |
| Qwen3-32B | 44.7 | 61.4 | 66.0 | 58.6 | 68.9 | 72.2 |
| + SRLEF ($\Delta$) | -10.6 | -2.2 | -1.4 | -20.1 | -1.0 | -0.1 |
| CWM | 49.0 | 63.7 | 67.9 | 57.4 | 67.3 | 70.1 |
| + SRLEF ($\Delta$) | -4.8 | +0.5 | +0.9 | -7.4 | +0.1 | +0.2 |

Self-RLEF scaffold. One may wonder to what extent the self-refinement pipeline itself leads to the inference performance gain irrespective of model training. Hence, we investigate inference using the Self-RLEF approach with public open-weights models, specifically Qwen3-32B and CWM. We compare these results to using these models in a standard single turn inference procedure.
Results provided in [Table 4](#S6.T4) show no noticeable improvement from using the proposed self-RLEF approach, and even a decrease in performance across both models over all metrics and datasets. By manual analysis, we observe the model struggles to correctly predict the output, and ignores the feedback.

Figure: Figure 5: Comparing best@k when ranking Qwen3-32B solutions, using CWM post-trained only for output prediction as a verifier.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x5.png

Knowing when to submit or fix. To better identify the source of performance gains from self-RLEF, we analyse model behaviour during inference time. We measure how often the model successfully fixes a solution, i.e., cases where the initial solution fails the tests but the final solution passes, as well as how often it breaks a solution, i.e., where an initially passing solution fails after revision. For completeness, we also report cases where both the initial and final solutions either pass or fail the tests. [Table 5](#S6.T5) reports results for CWM on DMC using both public and private tests. Results suggest the model rarely degrades correct solutions, breaking only $1.2\%$ of cases on public tests and $5.0\%$ on private tests. In contrast, when the initial solution fails, the model frequently produces effective fixes, succeeding in $17.0\%$ of public-tests and $10.4\%$ of private-tests. These improvements increase the pass rate from $57.8\%$ for the initial solutions to $63.2\%$ for the final submissions.

**Table 5: Pass rates of the initial generated solution (Init), compared to the final submitted solution (Sub) in *Self-RLEF* inference on DMC considering both public and private tests.**
| Init\Sub | Fail | Pass |
| --- | --- | --- |
| Fail | 16.3% | 17.0% |
| Pass | 1.2% | 65.5% |

### 6.4 Beyond Self -Verification

While the focus of this work is *self*-execution, one could imagine use cases for building a model as a code simulator only. As an initial analysis, we measure public test pass rates for multiple models on LCB-IO and DMC to assess the potential of the best@k approach. [Table 6](#S6.T6) reports public pass@1 and pass@10 results for Qwen and CWM. While models can generate solutions which pass the public tests (as evidenced in pass@10), they often submit solutions which do not pass them *even though they are provided in the question*. This suggests that standard reasoning approaches under-utilise such test information. This observation motivates the use of solution verification.

We next assess the ability of our trained CWM model to predict execution outputs for solutions generated by Qwen3-32B. CWM achieves pass@1 and pass@5 scores of $86.1$ and $91.4$, respectively, on public test output prediction. Based on this, we apply the best@k evaluation on both LCB-IO and DMC, as shown in [Figure 5](#S6.F5). The results indicate that using CWM with this filtering strategy is very effective and can correctly filter solutions generated by external models. Furthermore, compared to real execution, we observe only a minor *simulation gap*. This again highlights the efficacy of the output prediction method to alleviate the need for execution, and further shows generalisation to other models’ solutions. Results for this setup using Qwen3-4B and CWM-RL are provided in Appendix [A.1](#A1.SS1), showing similar trends.

**Table 6: Public pass@1 and 10 of different models. The large gap of standard reasoning models can suggest that they under-utilise provided test information.**
|  | DMC | LCB-IO |  |  |
| --- | --- | --- | --- | --- |
| Model \ Public Pass | @1 | @10 | @1 | @10 |
| Qwen3-4B | 42.5 | 65.4 | 64.4 | 80.9 |
| Qwen3-32B | 56.3 | 79.0 | 72.3 | 88.8 |
| Qwen2.5-7B RL | 55.1 | 76.5 | 68.0 | 84.7 |
| CWM RL | 73.4 | 87.6 | 81.7 | 90.6 |

## 7 Related Work

##### Code Simulation & Verification.

Several works ask how well LLMs can simulate or predict the output of a given code snippet (Hora, 2024; Li et al., 2025; Gu et al., 2024b; Xu et al., 2025; Copet et al., 2025; Armengol-Estapé et al., 2025). Others suggest that models struggle to simulate their own code, as they are blind to its flaws (Gu et al., 2024a). Some works use models to simulate tool execution as part of a synthetic data generation (Kimi et al., 2025). Furthermore, some studies explicitly train a model as a verifier of solutions (Le et al., 2022). Many report challenges in verification performance (Ruan et al., 2025; Wang et al., 2025).

##### Learning from Feedback.

Gehring et al. (2025) showed that models can learn to utilise feedback about the execution of their generated code.
Providing models with access to interpreters is a popular approach that has been used to improve performance in maths (Chen et al., 2023b; Gao et al., 2023), code generation (Liu et al., 2023b; Shinn et al., 2023), competitive programming (Zheng et al., 2025), and agentic coding (Yang et al., 2024; Xia et al., 2025). Several prompting approaches were suggested for non-reasoning models to elicit self-improvement, often joint with external verification signals (Chen et al., 2023c; Renze and Guven, 2024; Madaan et al., 2023; Kumar et al., 2024). Chen et al. (2023a) further showed that training with human written feedback on code can improve performance.

## 8 Discussion

Limitations.
The main limitation of simulating program execution is estimating complex computational operations (e.g., multiplying large numbers, compute logarithms, etc.). Yet, while execution simulation is imperfect and can introduce noise, our findings suggest that it provides a useful inductive bias for reasoning about program behaviour, particularly in settings where direct execution is expensive or infeasible. Furthermore, while our approach showed promising results, it is currently limited to single file competitive programming questions. Generalising this to full repository SWE tasks poses an interesting future research direction.

Future Work. We believe our work opens several directions for future research. The most interesting direction in our opinion is using the full rich execution simulation, and not only the final output as feedback for iterative code fixing. Such feedback can convey richer information than the output alone (*even beyond real execution*), capturing not just what output is produced, but why it arises. Such explanations can reveal cases where a test appears to pass for incidental reasons, as well as provide insight into the underlying causes of failures. In preliminary results we observe that training with rich textual feedback presents challenges to training stability. We hypothesise this is due to both inability to train with teacher forcing and unclear definition of the verifiable reward of the simulation. We leave such exploration for future work.

## 9 Conclusion

In this work we investigated if LLMs can be trained to simulate code execution and whether this capability can be used to improve code generation. By combining SFT on NLEX with RLVR, we showed that models can acquire the ability to predict execution outcomes for general programs as well as code they generate. Leveraging this ability, we introduced *self-verification* and iterative *self-fix* strategies using predicted execution signals to select or refine candidate solutions without relying on external execution. Our empirical results on competitive programming tasks demonstrate consistent improvements over standard baselines considering both output prediction and question solving. Compared with real execution we show a relatively small *simulation gap*, demonstrating the usability of the proposed approach compared to the top-line of code execution. More broadly, our results suggest that enabling models to reason about the outcomes of the code they generate may be a key for building more reliable programming agents.

## Impact Statement

This paper presents work whose goal is to advance the field of Machine Learning. There are many potential societal consequences of our work, none which we feel must be specifically highlighted here.

## References

- W. U. Ahmad, S. Narenthiran, S. Majumdar, A. Ficek, S. Jain, J. Huang, V. Noroozi, and B. Ginsburg (2025)
Opencodereasoning: advancing data distillation for competitive coding.
arXiv preprint arXiv:2504.01943.
Cited by: [§5.1.1](#S5.SS1.SSS1.p1.1).
- J. Armengol-Estapé, Q. Carbonneaux, T. Zhang, A. H. Markosyan, V. Seeker, C. Cummins, M. Kambadur, M. F. O’Boyle, S. Wang, G. Synnaeve, et al. (2025)
What i cannot execute, i do not understand: training and evaluating llms on program execution traces.
arXiv preprint arXiv:2503.05703.
Cited by: [§1](#S1.p1.1),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- J. Austin, A. Odena, M. Nye, M. Bosma, H. Michalewski, D. Dohan, E. Jiang, C. Cai, M. Terry, Q. Le, et al. (2021)
Program synthesis with large language models.
Note: arXiv:2108.07732
External Links: [Link](https://arxiv.org/abs/2108.07732)
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1).
- M. Beck, J. Gehring, J. Kossen, and G. Synnaeve (2026)
Towards a neural debugger for python.
External Links: 2603.09951,
[Link](https://arxiv.org/abs/2603.09951)
Cited by: [§1](#S1.p1.1).
- S. Bengio, O. Vinyals, N. Jaitly, and N. Shazeer (2015)
Scheduled sampling for sequence prediction with recurrent neural networks.
Advances in neural information processing systems 28.
Cited by: [§4](#S4.p5.1).
- B. Bogin, K. Yang, S. Gupta, K. Richardson, E. Bransom, P. Clark, A. Sabharwal, and T. Khot (2024)
Super: evaluating agents on setting up and executing tasks from research repositories.
arXiv preprint arXiv:2409.07440.
Cited by: [§1](#S1.p2.1).
- J. S. Chan, N. Chowdhury, O. Jaffe, J. Aung, D. Sherburn, E. Mays, G. Starace, K. Liu, L. Maksin, T. Patwardhan, et al. (2024)
Mle-bench: evaluating machine learning agents on machine learning engineering.
arXiv preprint arXiv:2410.07095.
Cited by: [§1](#S1.p2.1).
- A. Chen, J. Scheurer, T. Korbak, J. A. Campos, J. S. Chan, S. R. Bowman, K. Cho, and E. Perez (2023a)
Improving code generation by training with natural language feedback.
arXiv preprint arXiv:2303.16749.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- W. Chen, X. Ma, X. Wang, and W. W. Cohen (2023b)
Program of thoughts prompting: disentangling computation from reasoning for numerical reasoning tasks.
Transactions on Machine Learning Research.
Note:
External Links: ISSN 2835-8856,
[Link](https://openreview.net/forum?id=YfZ4ZPt8zd)
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- X. Chen, M. Lin, N. Schärli, and D. Zhou (2023c)
Teaching large language models to self-debug.
arXiv preprint arXiv:2304.05128.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- K. Cobbe, V. Kosaraju, M. Bavarian, M. Chen, H. Jun, L. Kaiser, M. Plappert, J. Tworek, J. Hilton, R. Nakano, C. Hesse, and J. Schulman (2021)
Training verifiers to solve math word problems.
arXiv preprint arXiv:2110.14168.
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1).
- J. Copet, Q. Carbonneaux, G. Cohen, J. Gehring, J. Kahn, J. Kossen, F. Kreuk, E. McMilin, M. Meyer, Y. Wei, et al. (2025)
Cwm: an open-weights llm for research on code generation with world models.
arXiv preprint arXiv:2510.02387.
Cited by: [§1](#S1.p1.1),
[§2.1](#S2.SS1.p1.4),
[§2.1](#S2.SS1.p2.1),
[§2](#S2.p1.1),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- J. Ding, Y. Zhang, Y. Shang, Y. Zhang, Z. Zong, J. Feng, Y. Yuan, H. Su, N. Li, N. Sukiennik, et al. (2025)
Understanding world or predicting future? a comprehensive survey of world models.
ACM Computing Surveys 58 (3), pp. 1–38.
Cited by: [§1](#S1.p2.1).
- L. Gao, A. Madaan, S. Zhou, U. Alon, P. Liu, Y. Yang, J. Callan, and G. Neubig (2023)
PAL: program-aided language models.
In Proceedings of the 40th International Conference on Machine LearningProceedings of the 41st International Conference on Machine LearningForty-second International Conference on Machine Learning2025 IEEE/ACM Second International Conference on AI Foundation Models and Software Engineering (Forge)The Twelfth International Conference on Learning RepresentationsProceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE)Findings of the Association for Computational Linguistics ACL 2024Findings of the Association for Computational Linguistics: EMNLP 2024The eleventh international conference on learning representationsThirty-seventh Conference on Neural Information Processing SystemsForty-second International Conference on Machine LearningCompanion Proceedings of the 32nd ACM International Conference on the Foundations of Software Engineering, A. Krause, E. Brunskill, K. Cho, B. Engelhardt, S. Sabato, J. Scarlett, R. Salakhutdinov, Z. Kolter, K. Heller, A. Weller, N. Oliver, J. Scarlett, F. Berkenkamp, W. Che, J. Nabende, E. Shutova, and M. T. Pilehvar (Eds.),
Proceedings of Machine Learning ResearchProceedings of Machine Learning Research, Vol. 202235, pp. 10764–10799.
External Links: [Link](https://proceedings.mlr.press/v202/gao23f.html)
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- J. Gehring, K. Zheng, J. Copet, V. Mella, T. Cohen, and G. Synnaeve (2025)
RLEF: grounding code LLMs in execution feedback with reinforcement learning.
External Links: [Link](https://openreview.net/forum?id=PzSG5nKe1q)
Cited by: [§1](#S1.p2.1),
[§1](#S1.p3.1),
[§4](#S4.p1.1),
[§5.1.2](#S5.SS1.SSS2.p3.1),
[§7](#S7.SS0.SSS0.Px2.p1.1).
- A. Grattafiori, A. Dubey, A. Jauhri, A. Pandey, A. Kadian, A. Al-Dahle, A. Letman, A. Mathur, A. Schelten, A. Vaughan, et al. (2024)
The llama 3 herd of models.
arXiv preprint arXiv:2407.21783.
Cited by: [§2.1](#S2.SS1.p1.4).
- A. Gu, W. Li, N. Jain, T. Olausson, C. Lee, K. Sen, and A. Solar-Lezama (2024a)
The counterfeit conundrum: can code language models grasp the nuances of their incorrect generations?.
pp. 74–117.
Cited by: [§1](#S1.p1.1),
[§6.1](#S6.SS1.p3.5),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- A. Gu, B. Roziere, H. J. Leather, A. Solar-Lezama, G. Synnaeve, and S. Wang (2024b)
CRUXEval: a benchmark for code reasoning, understanding and execution.
pp. 16568–16621.
External Links: [Link](https://proceedings.mlr.press/v235/gu24c.html)
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1),
[§1](#S1.p4.3),
[§5.1.2](#S5.SS1.SSS2.p4.1),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- D. Ha and J. Schmidhuber (2018)
World models.
arXiv preprint arXiv:1803.10122 2 (3).
Cited by: [§1](#S1.p2.1).
- M. Hassid, T. Remez, J. Gehring, R. Schwartz, and Y. Adi (2024)
The larger the better? improved llm code-generation via budget reallocation.
arXiv preprint arXiv:2404.00725.
Cited by: [§3](#S3.p5.3).
- M. Hassid, G. Synnaeve, Y. Adi, and R. Schwartz (2025)
Don’t overthink it. preferring shorter thinking chains for improved llm reasoning.
arXiv preprint arXiv:2505.17813.
Cited by: [§6.2](#S6.SS2.SSS0.Px1.p1.2).
- A. Hora (2024)
Predicting test results without execution.
pp. 542–546.
Cited by: [§7](#S7.SS0.SSS0.Px1.p1.1).
- N. Jain, K. Han, A. Gu, W. Li, F. Yan, T. Zhang, S. Wang, A. Solar-Lezama, K. Sen, and I. Stoica (2024)
Livecodebench: holistic and contamination free evaluation of large language models for code.
arXiv preprint arXiv:2403.07974.
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1),
[§1](#S1.p4.3),
[§5.1.2](#S5.SS1.SSS2.p2.1).
- C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan (2023)
Swe-bench: can language models resolve real-world github issues?.
arXiv preprint arXiv:2310.06770.
Cited by: [§1](#S1.p2.1).
- R. Kamoi, Y. Zhang, N. Zhang, J. Han, and R. Zhang (2024)
When can llms actually correct their own mistakes? a critical survey of self-correction of llms.
Transactions of the Association for Computational Linguistics 12, pp. 1417–1440.
Cited by: [§1](#S1.p1.1).
- T. Kimi, Y. Bai, Y. Bao, G. Chen, J. Chen, N. Chen, R. Chen, Y. Chen, Y. Chen, Y. Chen, et al. (2025)
Kimi k2: open agentic intelligence.
arXiv preprint arXiv:2507.20534.
Cited by: [§1](#S1.p2.1),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- A. Kumar, V. Zhuang, R. Agarwal, Y. Su, J. D. Co-Reyes, A. Singh, K. Baumli, S. Iqbal, C. Bishop, R. Roelofs, et al. (2024)
Training language models to self-correct via reinforcement learning.
arXiv preprint arXiv:2409.12917.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- H. Le, Y. Wang, A. D. Gotmare, S. Savarese, and S. C. H. Hoi (2022)
Coderl: mastering code generation through pretrained models and deep reinforcement learning.
Advances in Neural Information Processing Systems 35, pp. 21314–21328.
Cited by: [§7](#S7.SS0.SSS0.Px1.p1.1).
- J. Li, D. Guo, D. Yang, R. Xu, Y. Wu, and J. He (2025)
CodeIO: condensing reasoning patterns via code input-output prediction.
External Links: [Link](https://openreview.net/forum?id=feIaF6vYFl)
Cited by: [§1](#S1.p1.1),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- Y. Li, D. Choi, J. Chung, N. Kushman, J. Schrittwieser, R. Leblond, T. Eccles, J. Keeling, F. Gimeno, A. Dal Lago, et al. (2022)
Competition-level code generation with alphacode.
Science 378 (6624), pp. 1092–1097.
Cited by: [§1](#S1.p4.3),
[§2.1](#S2.SS1.p1.4),
[§5.1.1](#S5.SS1.SSS1.p2.3),
[§5.1.2](#S5.SS1.SSS2.p3.1).
- H. Lightman, V. Kosaraju, Y. Burda, H. Edwards, B. Baker, T. Lee, J. Leike, J. Schulman, I. Sutskever, and K. Cobbe (2023)
Let’s verify step by step.
arXiv preprint arXiv:2305.20050.
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1).
- J. Liu, C. S. Xia, Y. Wang, and L. Zhang (2023a)
Is your code generated by chatGPT really correct? rigorous evaluation of large language models for code generation.
External Links: [Link](https://openreview.net/forum?id=1qvx610Cu7)
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1).
- Z. Liu, Y. Zhang, P. Li, Y. Liu, and D. Yang (2023b)
Dynamic llm-agent network: an llm-agent collaboration framework with agent team optimization.
External Links: 2310.02170
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- A. Madaan, N. Tandon, P. Gupta, S. Hallinan, L. Gao, S. Wiegreffe, U. Alon, N. Dziri, S. Prabhumoye, Y. Yang, et al. (2023)
Self-refine: iterative refinement with self-feedback.
Advances in Neural Information Processing Systems 36, pp. 46534–46594.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- MiniMax (2026)
M2.1: multilingual and multi-task coding with strong generalization.
Note: [https://x.com/MiniMax__AI/status/2007843119832695114](https://x.com/MiniMax__AI/status/2007843119832695114)
Cited by: [§1](#S1.p2.1).
- I. Moshkov, D. Hanley, I. Sorokin, S. Toshniwal, C. Henkel, B. Schifferer, W. Du, and I. Gitman (2025)
Aimo-2 winning solution: building state-of-the-art mathematical reasoning models with openmathreasoning dataset.
arXiv preprint arXiv:2504.16891.
Cited by: [§5.1.1](#S5.SS1.SSS1.p1.1).
- T. X. Olausson, J. P. Inala, C. Wang, J. Gao, and A. Solar-Lezama (2024)
Is self-repair a silver bullet for code generation?.
External Links: [Link](https://openreview.net/forum?id=y0GJXRungR)
Cited by: [§1](#S1.p1.1).
- Y. Peng, A. D. Gotmare, M. R. Lyu, C. Xiong, S. Savarese, and D. Sahoo (2025)
PerfCodeGen: improving performance of llm generated code with execution feedback.
pp. 1–13.
External Links: [Document](https://dx.doi.org/10.1109/Forge66646.2025.00008)
Cited by: [§1](#S1.p2.1).
- C. Qian, E. C. Acikgoz, B. Li, X. Chen, Y. Zhang, B. He, Q. Luo, D. Hakkani-Tür, G. Tur, Y. Li, et al. (2026)
Current agents fail to leverage world model as tool for foresight.
arXiv preprint arXiv:2601.03905.
Cited by: [§4](#S4.p2.1).
- Qwen, :, A. Yang, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Li, D. Liu, F. Huang, H. Wei, H. Lin, J. Yang, J. Tu, J. Zhang, J. Yang, J. Yang, J. Zhou, J. Lin, K. Dang, K. Lu, K. Bao, K. Yang, L. Yu, M. Li, M. Xue, P. Zhang, Q. Zhu, R. Men, R. Lin, T. Li, T. Tang, T. Xia, X. Ren, X. Ren, Y. Fan, Y. Su, Y. Zhang, Y. Wan, Y. Liu, Z. Cui, Z. Zhang, and Z. Qiu (2025)
Qwen2.5 technical report.
External Links: 2412.15115,
[Link](https://arxiv.org/abs/2412.15115)
Cited by: [§5.1.1](#S5.SS1.SSS1.p2.3).
- M. Renze and E. Guven (2024)
Self-reflection in llm agents: effects on problem-solving performance.
arXiv preprint arXiv:2405.06682.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- C. Ruan, D. Jiang, Y. Wang, and W. Chen (2025)
Critique-coder: enhancing coder models by critique reinforcement learning.
arXiv preprint arXiv:2509.22824.
Cited by: [§5.2](#S5.SS2.p1.5),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- N. Shinn, F. Cassano, A. Gopinath, K. R. Narasimhan, and S. Yao (2023)
Reflexion: language agents with verbal reinforcement learning.
In Thirty-seventh Conference on Neural Information Processing Systems,
External Links: [Link](https://openreview.net/forum?id=vAElhFcKW6)
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- J. Su, M. Ahmed, Y. Lu, S. Pan, W. Bo, and Y. Liu (2024)
Roformer: enhanced transformer with rotary position embedding.
Neurocomputing 568, pp. 127063.
Cited by: [§A.3](#A1.SS3.SSS0.Px1.p1.10).
- A. Thimmaiah, J. Zhang, J. Srinivasa, J. J. Li, and M. Gligoric (2025)
PLSemanticsBench: large language models as programming language interpreters.
arXiv preprint arXiv:2510.03415.
Cited by: [§1](#S1.p1.1).
- Y. Wang, X. Yue, and W. Chen (2025)
Critique fine-tuning: learning to critique is more effective than learning to imitate.
arXiv preprint arXiv:2501.17703.
Cited by: [§7](#S7.SS0.SSS0.Px1.p1.1).
- C. S. Xia, Z. Wang, Y. Yang, Y. Wei, and L. Zhang (2025)
Live-swe-agent: can software engineering agents self-evolve on the fly?.
arXiv preprint arXiv:2511.13646.
Cited by: [§1](#S1.p2.1),
[§7](#S7.SS0.SSS0.Px2.p1.1).
- R. Xu, J. Cao, Y. Lu, M. Wen, H. Lin, X. Han, B. He, S. Cheung, and L. Sun (2025)
CRUXEVAL-X: a benchmark for multilingual code reasoning, understanding and execution.
Vienna, Austria, pp. 23762–23779.
External Links: [Link](https://aclanthology.org/2025.acl-long.1158/),
[Document](https://dx.doi.org/10.18653/v1/2025.acl-long.1158),
ISBN 979-8-89176-251-0
Cited by: [§7](#S7.SS0.SSS0.Px1.p1.1).
- A. Yang, A. Li, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Gao, C. Huang, C. Lv, et al. (2025)
Qwen3 technical report.
arXiv preprint arXiv:2505.09388.
Cited by: [§2.1](#S2.SS1.p3.2).
- J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan, and O. Press (2024)
Swe-agent: agent-computer interfaces enable automated software engineering.
Advances in Neural Information Processing Systems 37, pp. 50528–50652.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. R. Narasimhan, and Y. Cao (2022)
React: synergizing reasoning and acting in language models.
Cited by: [§4](#S4.p3.1).
- J. Zheng, J. Zhang, Y. Luo, Y. Mao, Y. Gao, L. Du, H. Chen, and N. Zhang (2026)
Can we predict before executing machine learning agents?.
arXiv preprint arXiv:2601.05930.
Cited by: [§1](#S1.p2.1).
- K. Zheng, J. Decugis, J. Gehring, T. Cohen, benjamin negrevergne, and G. Synnaeve (2025)
What makes large language models reason in (multi-turn) code generation?.
In The Thirteenth International Conference on Learning Representations,
External Links: [Link](https://openreview.net/forum?id=Zk9guOl9NS)
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).

## Appendix A Appendix.

### A.1 Additional Results

#### A.1.1 Supervised fine-tuning.

To confirm that our NLEX data mix does not negatively impact the performance of the model on general tasks at the expense of boosting output prediction, we look at several standard coding and maths benchmarks. Specifically we consider CruxEval-Input (Gu et al., 2024b), MBPP (Austin et al., 2021), HumanEval Plus (Liu et al., 2023a), LiveCodeBench v5 (Jain et al., 2024), GSM8k (Cobbe et al., 2021), and Math 500 (Lightman et al., 2023). As reported in Table [7](#A1.T7), using the NLEX data mix does not notably harm any metric, and even improves output prediction abilities as noted by CruxEval-Input.

**Table 7: Investigating the impact of the NLEX data mix compared to a standard reasoning and instruction following mix on various standard coding and maths benchmarks. All models are trained with supervised fine tuning for the same budget only changing the data.**
| Model | CruxEval-In | MBPP | HumanEval+ | LCBv5 | GSM8k | Math 500 |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-7B regular mix | 0.469 | 0.634 | 0.652 | 0.414 | 0.842 | 0.518 |
| + NLEX | 0.505 | 0.632 | 0.659 | 0.413 | 0.826 | 0.528 |
| Qwen2.5-3B regular mix | 0.361 | 0.522 | 0.543 | 0.195 | 0.748 | 0.398 |
| + NLEX | 0.445 | 0.524 | 0.537 | 0.203 | 0.729 | 0.406 |

#### A.1.2 The effect of RL on output prediction

To better evaluate the effect of additional RL phase on top of the SFT, we evaluate CWM model, trained with and without RL considering output prediction only. For a reference, we additionally include results for the official post-trained CWM model. Results are reported in [Table 8](#A1.T8). As expected, results suggest that the RL phase significantly improve results on output prediction over competitive programming questions. We omit Qwen results as without RL, their performance was significantly lower.

**Table 8: Output prediction performance of the CWM with and without RL. For reference we additionally report results for the official CWM model.**
| Base Model | LCB-IO-Out | DMC-Test-Out |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  | pass@1 | @5 | @10 | @1 | @5 | @10 |
| CWM (Official) | 60.4 | 79.3 | 82.0 | 68.9 | 85.8 | 87.8 |
| CWM (wo. RL) | 30.3 | 55.6 | 62.1 | 38.4 | 67.5 | 73.5 |
| CWM (w. RL) | 89.6 | 93.4 | 94.2 | 89.2 | 93.3 | 94.0 |

#### A.1.3 Self-Verification

To further analyse the impact if self-verification using self-execution simulation, we wanted to study a setup where the tests used for verification were not present at the time of generating the solutions. To that end, we generate solutions using a model trained jointly for output prediction and competitive programming solving, but without tests in the question description for training and inference. This represents a case where the tests for verification contain completely new information unseen when generating the solution. Results are provided in Figure [6](#A1.F6). These suggest that while removing the tests from the description has a negative notable impact on performance, much of the performance can be gained by filtering solutions using these tests. It can also suggest that tests not used for generating the solution could have a higher positive impact for verification, motivating future investigation of test generation.

Figure: Figure 6: Comparing best@k when ranking solutions generated by CWM post-trained jointly for solving and output prediction, using the same model as a verifier. The model here was trained and evaluated without the public tests as part of the description.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x6.png

#### A.1.4 Self-RLEF

By default we allow a maximum of $10$ turns for execution RLEF, and *Self-RLEF*. However in practice the model often submits its solution prior leading to an average of $3.33$ turns. We wish to consider the performance of *Self-RLEF* when limiting the number of solve turns to a maximum of $3$. We provide results in Table [9](#A1.T9). In practice the model uses an average of $2.38$ turns.

**Table 9: Solve rates when using real or simulated execution feedback, but limiting to $3$ turns. This extends Table [3](#S6.T3) under a more compute constraint setup.**
|  | DMC | LCB-IO |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | pass@1 | pass@5 | pass@10 | public | pass@1 | pass@5 | pass@10 | public |
| Self-RLEF (Ours) | 61.5 | 75.6 | 79.6 | 79.0 | 61.5 | 69.2 | 71.1 | 84.2 |
| Execution RLEF (Oracle) | 62.7 | 75.8 | 78.8 | 81.5 | 63.3 | 70.3 | 72.2 | 86.3 |

#### A.1.5 Beyond Self -Verification

We provide results for using a dedicated output prediction model as a tool for verifying solutions of other models in a best@k setup. Results provided in Figures [7](#A1.F7) and [8](#A1.F8) show consistent improvements from this approach, for both Qwen3-4B and CWM Solve-RL, with only a slight degradation compared to ground truth execution of these tests. Like the results for Qwen3-32B in the main paper this further demonstrates the efficacy of this approach.

Figure: Figure 7: Comparing best@k when ranking Qwen3-4B solutions, using CWM post-trained only for output prediction as a verifier.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x7.png

Figure: Figure 8: Comparing best@k when ranking solutions by CWM post-trained only for competitive programming solving (denoted SOLVE-RL in Table [3](#S6.T3)), using CWM post-trained only for output prediction as a verifier.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x8.png

We also provide results of using a dedicated verifier based on a smaller model (Qwen2.5-7B), on solutions generated by a model starting from the same base model. Results provided in Figure [9](#A1.F9) show that this method is also effective with models at this scale. This outperforms the performance in Figure [4](#S5.F4) which suggests that the constraint of having the same model for solving and verification does impose challenges especially with models with limited capacity.

Figure: Figure 9: Comparing best@k when ranking solutions by Qwen-7B post-trained for competitive programming solving, using Qwen-7B post-trained only for output prediction as a verifier. This mirrors the results for Qwen in Figure [4](#S5.F4), but when each model has a dedicated role.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x9.png

### A.2 Self-RLEF Example Inference

To demonstrate how the iterative self-fixing and self verification looks in practice in *Self-RLEF* we provide the (abbreviated) multi-turn inference for a successful LCB-IO solution using our model.

### A.3 Hyper-Parameters

##### Supervised Fine-Tuning.

All Qwen supervised fine-tuning use a sequence length of $65,536$ by applying scaled RoPE (Su et al., 2024) with a factor of two relative to the base models to support longer context. CWM uses a context length of $131,072$ like in the original paper. Models were trained for $15.5$k steps, with a batch size of $4$M tokens per-update step, for a total of $65$B tokens. They were trained using a peak learning rate of $8e-6$ after a warmup of $1$k steps.
The estimated compute per-training run is $7.9e21$ FLOPs for 7B, and $5.0e21$ for 3B. Both models were trained for ${\sim}20$ hours on 128 and 64 NVIDIA H100 GPUs respectively.

##### Reinforcement Learning.

We train the models on NVIDIA H100
GPUs, with a standard configuration of $192$ GPUs for a single training run of CWM, and $86$ for Qwen 7B and 3B. Typically 1/3 of the GPUs are used as trainers and the rest for rollouts. By default, we employ the maximum context of the model from SFT for generation, packing training sequences by maximum of 131,072
tokens, use a global batch size of 1M tokens, a group size of 8, discarding rollouts with a staleness of more than 8 off-policy steps. We train the CWM models for 10k update steps, and the Qwen models for 4k, as we noted loops and collapses with longer training. This corresponds to roughly 9B and 3.2B tokens respectively. We use the last checkpoint for CWM, as training was stable, and the best checkpoint based on pass@1 by DMCValidation for Qwen (at 200 step increments) as the training was more prone to degradation in the end of training. We use 400 steps of linear learning rate warmup to a peak $1.4e-7$, with gradient clipping at $0.1$.
For single turn solving jointly with output prediction we sample output prediction at $15\%$ of the time while the rest is for solving. For Self-RLEF we increase this ratio to $25\%$.

For sampling in evaluation we compare temperature $0.6$ and $1.0$, with top-p $0.95$ as these were common values for Qwen and CWM. We select the best per-model based on DMC pass@1 rates. For CWM results didn’t change notably for all training setups, and yet for Qwen with temperature of $0.6$ there were many loops leading to not finishing rollouts, this could be to the smaller model size. Thus for all Qwen models we use temperature $1.0$, as well as for all CWM models except of the results with two fixing turns which performed slightly better with $0.6$.

### A.4 Prompts

As mentioned in Section [2.1](#S2.SS1) the data is created by converting raw traces to natural language by prompting an LLM, followed by a verification procedure. Below we provide the prompt used for the conversion.

### A.5 Data Samples

We provide examples from our NLEX data below.

### A.3 Hyper-Parameters

##### Supervised Fine-Tuning.

All Qwen supervised fine-tuning use a sequence length of $65,536$ by applying scaled RoPE (Su et al., 2024) with a factor of two relative to the base models to support longer context. CWM uses a context length of $131,072$ like in the original paper. Models were trained for $15.5$k steps, with a batch size of $4$M tokens per-update step, for a total of $65$B tokens. They were trained using a peak learning rate of $8e-6$ after a warmup of $1$k steps.
The estimated compute per-training run is $7.9e21$ FLOPs for 7B, and $5.0e21$ for 3B. Both models were trained for ${\sim}20$ hours on 128 and 64 NVIDIA H100 GPUs respectively.

##### Reinforcement Learning.

We train the models on NVIDIA H100
GPUs, with a standard configuration of $192$ GPUs for a single training run of CWM, and $86$ for Qwen 7B and 3B. Typically 1/3 of the GPUs are used as trainers and the rest for rollouts. By default, we employ the maximum context of the model from SFT for generation, packing training sequences by maximum of 131,072
tokens, use a global batch size of 1M tokens, a group size of 8, discarding rollouts with a staleness of more than 8 off-policy steps. We train the CWM models for 10k update steps, and the Qwen models for 4k, as we noted loops and collapses with longer training. This corresponds to roughly 9B and 3.2B tokens respectively. We use the last checkpoint for CWM, as training was stable, and the best checkpoint based on pass@1 by DMCValidation for Qwen (at 200 step increments) as the training was more prone to degradation in the end of training. We use 400 steps of linear learning rate warmup to a peak $1.4e-7$, with gradient clipping at $0.1$.
For single turn solving jointly with output prediction we sample output prediction at $15\%$ of the time while the rest is for solving. For Self-RLEF we increase this ratio to $25\%$.

For sampling in evaluation we compare temperature $0.6$ and $1.0$, with top-p $0.95$ as these were common values for Qwen and CWM. We select the best per-model based on DMC pass@1 rates. For CWM results didn’t change notably for all training setups, and yet for Qwen with temperature of $0.6$ there were many loops leading to not finishing rollouts, this could be to the smaller model size. Thus for all Qwen models we use temperature $1.0$, as well as for all CWM models except of the results with two fixing turns which performed slightly better with $0.6$.

### A.4 Prompts

As mentioned in Section [2.1](#S2.SS1) the data is created by converting raw traces to natural language by prompting an LLM, followed by a verification procedure. Below we provide the prompt used for the conversion.

### A.5 Data Samples

We provide examples from our NLEX data below.

### A.5 Data Samples

We provide examples from our NLEX data below.

Sections:
Abstract
1 Introduction
2 Boosting Execution Simulation
    2.1 Natural Language Execution Tracing ( NLEX )
    2.2 Output Prediction Environment
3 Self-Execution For Verification
4 Self-Execution For Fixing
5 Experimental Setup
    5.1 Datasets
        5.1.1 Training datasets
        5.1.2 Evaluation datasets
    5.2 Trained Models
6 Results
    6.1 Output Prediction
    6.2 Self-Execution for Competitive Programming
        Self-verification.
        Self-RLEF.
    6.3 Ablations
    6.4 Beyond Self -Verification
7 Related Work
    Code Simulation & Verification.
    Learning from Feedback.
8 Discussion
9 Conclusion
Impact Statement
References
Appendix A Appendix.
    A.1 Additional Results
        A.1.1 Supervised fine-tuning.
        A.1.2 The effect of RL on output prediction
        A.1.3 Self-Verification
        A.1.4 Self-RLEF
        A.1.5 Beyond Self -Verification
    A.2 Self-RLEF Example Inference
    A.3 Hyper-Parameters
        Supervised Fine-Tuning.
        Reinforcement Learning.
    A.4 Prompts
    A.5 Data Samples

## Contents
- 1 Introduction
- 2 Boosting Execution Simulation
  - 2.1 Natural Language Execution Tracing ( NLEX )
  - 2.2 Output Prediction Environment
- 3 Self-Execution For Verification
- 4 Self-Execution For Fixing
- 5 Experimental Setup
  - 5.1 Datasets
    - 5.1.1 Training datasets
    - 5.1.2 Evaluation datasets
  - 5.2 Trained Models
- 6 Results
  - 6.1 Output Prediction
  - 6.2 Self-Execution for Competitive Programming
    - Self-verification.
    - Self-RLEF.
  - 6.3 Ablations
  - 6.4 Beyond Self -Verification
- 7 Related Work
  - Code Simulation & Verification.
  - Learning from Feedback.
- 8 Discussion
- 9 Conclusion
- Impact Statement
- References
- Appendix A Appendix.
  - A.1 Additional Results
    - A.1.1 Supervised fine-tuning.
    - A.1.2 The effect of RL on output prediction
    - A.1.3 Self-Verification
    - A.1.4 Self-RLEF
    - A.1.5 Beyond Self -Verification
  - A.2 Self-RLEF Example Inference
  - A.3 Hyper-Parameters
    - Supervised Fine-Tuning.
    - Reinforcement Learning.
  - A.4 Prompts
  - A.5 Data Samples

## Abstract

Abstract A promising research direction in enabling LLMs to generate consistently correct code involves addressing their inability to properly estimate program execution, particularly for code they generate. In this work, we demonstrate that code LLMs can be trained to simulate program execution in a step-by-step manner and that this capability can be leveraged to improve competitive programming performance. Our approach combines supervised fine-tuning on natural language execution traces, textual explanations grounded in true execution, with reinforcement learning using verifiable rewards. We introduce two complementary objectives: output prediction given code and inputs, and solving competitive programming tasks with either ground-truth or self-predicted execution feedback. These objectives enable models to perform self-verification over multiple candidate solutions, and iterative self-fixing by simulating test execution. Across multiple competitive programming benchmarks, our method yields consistent improvements over standard reasoning approaches. We further present ablations and analysis to elucidate the role of execution simulation and its limitations.

## 1 Introduction

Going beyond treating code as a static text block holds great promise in advancing code LLMs. This involves jointly modelling program syntax and execution dynamics, similar to how developers reason during debugging and development (Armengol-Estapé et al., 2025; Li et al., 2025; Thimmaiah et al., 2025; Copet et al., 2025; Beck et al., 2026).
Despite its promise, translating execution prediction capabilities into consistent gains on practical programming tasks remains an open challenge. Moreover, Gu et al. (2024a); Olausson et al. (2024); Kamoi et al. (2024) indicate that current models often fail to faithfully simulate runtime behaviour or to consistently identify and explain errors in code they generate.

Code execution is widely used in various parts of training and inference of code LLMs. This includes feedback from code execution (Gehring et al., 2025; Peng et al., 2025) or rich tool-based signals in agentic settings (Xia et al., 2025). However, executing code at scale for training or inference poses practical challenges, such as environment setup (Bogin et al., 2024), managing code dependencies (Jimenez et al., 2023), handling partial or non-executable code, and sandboxing. In broader settings, program execution can also be computationally expensive and time-consuming; for example, runs of MLE-Bench can take up to $9$ hours (Chan et al., 2024; Zheng et al., 2026). Predicting execution outcomes could mitigate these challenges by enabling large rollouts and policy optimisation without code execution (MiniMax, 2026; Kimi et al., 2025). More broadly, using execution prediction to support reasoning and planning in coding tasks can be viewed as a form of world modelling in the code domain (Ha and Schmidhuber, 2018; Ding et al., 2025).

Figure: Figure 1: A conceptual outline of how one can use *self-execution simulation* of a generated code solution (or solutions) on public or generated test cases to improve coding performance. The simulation can be used as feedback to select the best solution from a few candidates (best@k) or to iteratively fix the code as needed (self-RLEF). See Section [3](#S3) for details.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x1.png

In this work, we take a step in this direction. We show LLMs can learn to simulate program execution step-by-step, including code they generated, and use this capability to improve competitive programming performance. We start by training models on natural-language execution traces – text explanations grounded in real program executions – and then further refining them using single-turn reinforcement learning for code output prediction. Equipped with this capability, we empirically demonstrate how models can perform *self-verification* over parallel solutions based on simulated execution (best@k). Inspired by Gehring et al. (2025), we also design a multi-turn reinforcement learning pipeline that enables iterative *self-fixing* through code proposal, execution simulation, and refinement. [Figure 1](#S1.F1) provides a conceptual overview of the proposed methods.

Results suggest the proposed training recipe leads to significant improvements in output prediction on CruxEval (Gu et al., 2024b) (up to $43\%$) and competitive programming solutions (Li et al., 2022; Jain et al., 2024) (up to $39\%$) relative to the evaluated baseline. This applies to both external and self-generated code solutions. Under the best@k setting, using the model’s output prediction to verify its own candidate solutions improves code correctness by up to $5.5\%$ absolute points on competitive programming tasks. In the multi-turn setting, we observe consistent gains across all evaluated configurations. Compared to ground-truth execution, both best@k and multi-turn variants show a relatively small degradation. Finally, we conduct analysis to highlight the strengths and limitations of the proposed approach.

Our Contributions: We provide a training recipe, showing that code LLMs are capable of simulating the program execution for both external and self-generated code. With that in mind, we introduce a practical framework for leveraging this behaviour by filtering code solutions based on predicted output (i.e., self-verification). Lastly, we present a multi-turn training and inference process to perform iterative self-fixing of the model’s generated code.

Figure: Figure 2: The two parts of our training pipeline. 1) Supervised fine tuning on natural language execution traces (NLEX), 2) Multi-task reinforcement learning on output prediction and competitive programming (optionally with multi-turn feedback and fixing).
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x2.png

## 2 Boosting Execution Simulation

Following Copet et al. (2025), we collect executable Python programs with input–output pairs and record their line-by-line execution. Next, we convert these execution traces into natural-language explanations and use the resulting data for supervised fine-tuning. We then further train the model using verifiable rewards on an output prediction task. The next sections describe these post-training steps in detail.

### 2.1 Natural Language Execution Tracing ( NLEX )

We collect Python functions from public repositories and automatically synthesise suitable inputs using a combination of LLM prompting and lightweight fuzzing techniques. In addition, we collect LLM-generated solutions to competitive programming problems from CodeContests (Li et al., 2022), and keep their provided tests as inputs. Although this portion of the data is smaller in scale, it involves substantially more complex programs. We then record execution traces for each program–input pair, capturing intermediate variable states throughout execution. Following Copet et al. (2025), we exclude traces exceeding $10\text{k}$ events or requiring more than $1\text{MB}$ of storage. The resulting dataset comprises ${\sim}30\text{M}$ functions from basic code sources and $35\text{k}$ from competitive programming problems. For all of the above, we use Llama3-70B-Instruct (Grattafiori et al., 2024).

While CWM (Copet et al., 2025) focused primarily on a structured, JSON-like format to describe the step-by-step execution, we wish to focus on natural language description of this data. Relative to the structured format, a free-form variant holds several benefits. First, as based on natural language, it closely matches the reasoning-style data already used by LLMs. It also enables adding semantic context to operations, e.g., explaining an update to an array in the scope of a dynamic programming code. Finally, it naturally abstracts away unnecessary details, such as summarising a long loop that reverses strings character by character.

To this end, we prompt Qwen3-32B-FP8 (without thinking) (Yang et al., 2025) to “translate” execution traces from raw structured format to a natural language explanation. See Appendix [A.4](#A1.SS4) for the exact prompt. We discard instances where the model’s predicted output does not match the ground truth, resulting in ${\sim}80$ M execution descriptions for general Python functions and $115$ k for competitive programming solutions (notice, each traced function may contain several io-pairs). The resulting data is formatted as instruction-following examples and used for model fine-tuning during the SFT phase. In which, the user requests a step-by-step explanation of a program’s execution for a given input, and the assistant provides the translated explanation. Sample instances are provided in Appendix [A.5](#A1.SS5).

### 2.2 Output Prediction Environment

Following standard practice in reasoning models, we post-train our model using Reinforcement Learning with Verifiable Rewards (RLVR). We define an output prediction environment, based on coding tasks, where the model reasons over a given (code, stdin) pair to predict the resulting stdout. We employ a terminal binary reward, scoring $+1$ if the prediction matches the true stdout, and $-1$ otherwise, allowing $1e-5$ tolerance in float comparisons.

The intended downstream use of the output prediction ability is simulating the execution of model generated solutions to competitive programming questions. To that end, we construct the output prediction environment on precisely such data. We collect solutions from strong LLMs to competitive programming questions and use the stdin of the matching public tests. Moreover, the higher difficulty of competitive programming problems makes them particularly well suited for post-training. [Figure 2](#S1.F2) depicts the optimisation pipeline.

## 3 Self-Execution For Verification

Given models with increased ability to simulate code execution, we ask *“How can this ability be used to boost programming abilities?”* Arguably, the simplest and most straightforward approach to leverage such capability is through post-hoc solution filtering. In this approach, candidate solutions are simulated on public or generated tests and retained only if their predicted outputs align with the expected ones.

For that, we adopt a best-of-$k$ (best@$k$) evaluation setup, where the model independently samples $k$ candidate solutions and selects the final one based on predefined criteria. In our setup, selection is based on the model’s execution prediction. In other words, for each candidate, the model simulates its execution on public test cases and checks whether the predicted outputs match the expected ones. The candidate predicted to pass the greatest number of public tests is selected for submission. In case of a tie we randomly select a solution among the ones that passed the maximum number of tests. We denote this approach best@k simulate. Notice, during inference we do not access any private tests nor ground-truth verification.

Formally, given a set of solutions $\mathcal{S}$, with public input-output pairs $(in_{t},out_{t})\in\mathcal{T}$, we use a model to simulate execution, predict the output $\mathcal{M}_{\text{sim}}(s,in_{t})$, and select:

$$ $\mathrm{Best}(\mathcal{S})\coloneqq\operatorname*{arg\,max}_{s\in\mathcal{S}}\sum_{(in_{t},out_{t})\in\mathcal{T}}\mathbf{1}\!\left[\mathcal{M}_{\text{sim}}(s,in_{t})=out_{t}\right].$ $$

We use rank_score_at_k (Hassid et al., 2024) to provide an unbiased accuracy estimate for generating $k$ solutions and selecting the one with the highest score under the proposed heuristic. Specifically, we use $20$ generated solutions per task and $5$ output-prediction attempts per test.

Recall, the primary focus of this work is *self*-simulation. In which, the same LLM is used to both generate candidate solutions and simulate their execution. That said, the same method can also be applied to solutions produced by other models. In [Section 6](#S6), we present empirical evidence demonstrating the efficacy of this approach in both setups.

## 4 Self-Execution For Fixing

Another approach to leveraging execution feedback is through multi-turn interaction with a computational environment to perform code fixing. Gehring et al. (2025) demonstrated that exposing LLMs to environmental feedback can enhance programming performance by allowing models to iteratively refine solutions based on information from failed test cases. However, as mentioned above, this may introduce practical challenges such as environment configuration, code dependencies, and non-executable code.

Motivated by this paradigm, we introduce an approach that uses predicted execution outputs as feedback instead of actual program execution. Note, unlike the method presented in [Section 3](#S3), that verifies multiple solutions via self-execution, the multi-turn setup refines solutions sequentially based on predicted feedback. Ideally, this approach can leverage richer signals, such as past solutions and execution details.
While similar world-modelling approaches have been explored in vision, recent work shows limited gains from such signals (Qian et al., 2026). In contrast, we show that using execution simulation can improve performance.

Figure: Algorithm 1 Multi-Turn Self-RLEF Rollout

Specifically, we propose a multi-turn environment with explicit context switching, i.e. where each interaction step is represented as an independent single-turn prompt containing only the relevant information (see details in the bullets below). This design enables fine-grained control over information flow. For instance, ensuring that execution simulation is isolated from solution reasoning and from access to the correct outputs. Moreover, it mitigates long-context challenges commonly associated with multi-turn reasoning (Yao et al., 2022). Finally, this context switching also naturally allows one to extend the number of fix turns at inference as each fix turn is independent. A formal description of the rollout procedure is provided in Algorithm [1](#alg1), and an example inference of our model in Appendix [A.2](#A1.SS2).
In words, the multi-turn setup is designed as follows:

- •
Turn 1 - Solve - Given a question, provide a code solution to solve the provided question.
- •
Turn 2 - Simulate - Given a code snippet and a test input, simulate the execution and predict the output that will be printed to the standard output. This step is performed independently for each public test.
- •
Turn 3 - Submit or Fix - Given a question, a candidate solution and feedback about each test (input, expected output, predicted output), decide whether the code is correct or not. If correct, submit the code solution, otherwise, fix the code to provide a new solution.
- •
Optional - Repeat turns 2 and 3 until a code solution is submitted or the maximum turns are reached.

Since the model’s ability to accurately predict execution outcomes may be weak at the start of RL training, relying solely on self-predicted feedback could lead the model to disregard this noisy signal. To mitigate this, we initially provide ground-truth execution feedback during training. As training progresses, one might switch from true execution signals to model-predicted execution outputs (Bengio et al., 2015). Alternatively, transition can also be deferred entirely to inference time. Our preliminary results showed no noticeable gap between the approaches, so we use the latter for simplicity. We denote the following approach *Self-RLEF*.

## 5 Experimental Setup

### 5.1 Datasets

We describe all datasets and configurations used to train and evaluate our models and baselines below. Note that each problem in competitive programming usually includes between one and four public test cases, typically provided in the problem description. These serve as basic checks for correctness and output formatting. In addition, a larger set of private tests, unavailable to the model, is used to better assess solution correctness, including coverage of edge cases and compliance with runtime constraints.

#### 5.1.1 Training datasets

The NLEX dataset, as presented in [Section 2.1](#S2.SS1), was used for supervised fine-tuning, together with OpenMathReasoning (Moshkov et al., 2025) and OpenCodeReasoning (Ahmad et al., 2025) datasets, to bootstrap reasoning abilities.

During RL, models were optimised for both solving and predicting the output of competitive programming solutions. For that, we use the training split derived from CodeContests (Li et al., 2022), after heuristically filtering malformed instances, which results in ${\sim}12.2$k problems. For output prediction, we sample $10$ candidate solutions and retain up to four correct ones per model, since all correct submissions yield identical outputs. We then pair each retained solution with all of its public test cases, treating each as an output prediction instance, resulting in a total of ${\sim}143k$ code–input–output examples. All solutions were generated using CWM and Qwen2.5-7B (Qwen et al., 2025).

Figure: Figure 3: CruxEval-O performance compared to model active parameters. Arrows demonstrate the benefit from training on NLEX data. We also compare to open models.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x3.png

#### 5.1.2 Evaluation datasets

We present evaluation datasets for competitive programming questions (first two), and output prediction (last two).

LCB-IO. We curate a subset from LiveCodeBench-v6 (Jain et al., 2024) containing only problems evaluated via stdio tests, which we refer to as LCB-IO. This restriction simplifies output prediction, as the task reduces to determining the content written to stdout given a specific stdin. The resulting set includes $287$ problems.

DMC. We follow Gehring et al. (2025) and use the validation and test splits of CodeContests (Li et al., 2022), yielding an additional evaluation set with a different distribution, denoted DMC, and consisting of $282$ problems.

CruxEval-O (Gu et al., 2024b) is a widely adopted benchmark consisting of short Python functions paired with input–output examples. The task requires the model to infer the function’s return value given the code and its input.

Output prediction for competitive programming. We generate $20$ solutions per-question from both DMC and LCB-IO using the same LLMs as mentioned above, without filtering or de-duplicating solutions, to perfectly match the real distribution of generated solutions. Such data is also used for best@k type metric calculations.

### 5.2 Trained Models

We post-train Qwen2.5-Base models of sizes $3$B and $7$B, together with CWM-base using the datasets described in [Section 5.1.1](#S5.SS1.SSS1). For RL we use an asynchronous RL infrastructure, adopting the same RL algorithm as in CWM, with different hyperparameters. When performing multi-task training we employ sample-level weighting. Furthermore, we apply reward scaling, following Ruan et al. (2025), assigning a weight of $0.8$ to the output prediction objective. For all multi-turn repair environments, including self-RLEF, we allow a maximum of one repair attempt during training (two solution turns in total, including the initial attempt), and $9$ at inference (overall $10$ turns). Full training configurations, including hyperparameters, are provided in Appendix [A.3](#A1.SS3).

Figure: Figure 4: Best@k performance of *self-verification* with *self-simulation*. Solutions and output predictions are produced by the same model - based on Qwen2.5-7B or CWM, trained for both solving and output prediction. Even though the tests used for filtering are in the solve prompt, there is still room for notable gains from simulating them.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x4.png

**Table 1: Output prediction performance of Qwen models trained with RLVR for output prediction, with and without NLEX data.**
| Base Model | LCB-IO-Out | DMC-Test-Out |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  | pass@1 | @5 | @10 | @1 | @5 | @10 |
| Qwen-7B (ours) | 79.7 | 89.4 | 91.1 | 77.3 | 89.3 | 91.6 |
| w.o NLEX | 75.7 | 87.8 | 89.7 | 71.8 | 87.0 | 89.9 |
| Qwen-3B (ours) | 66.4 | 80.6 | 83.9 | 59.4 | 78.2 | 82.8 |
| w.o NLEX | 57.1 | 74.2 | 78.3 | 45.9 | 66.2 | 72.4 |

## 6 Results

### 6.1 Output Prediction

CruxEval-O. We start by evaluating performance considering CruxEval-O. Results are presented in [Figure 3](#S5.F3). We evaluate both Qwen2.5-3B and Qwen2.5-7B (after SFT only), trained with and without the NLEX data. For reference we provide pass@1 scores of common open-weights LLMs. Results show a clear superiority of the NLEX data as part of the training mix, achieving comparable performance to significantly larger models, with Qwen2.5-3B increasing from $37.5$ to $68.0$ and Qwen2.5-7B improving $48.5$ to $75.5$ pass@1 scores. We provide results for standard coding metrics in Appendix [A.1](#A1.SS1), showing no regression in performance considering other benchmarks and tasks.

Competitive programming. Next, we evaluate output prediction performance on LLM solutions to competitive programming questions from LCB-IO and DMC (test split). Compared to CruxEval-O, these functions are often more complex and challenging. For that, we consider post-trained Qwen2.5 models (3B and 7B) on the task of output-prediction. Similarly to before, we consider models trained with and without NLEX data as part of the mix. Results presented in Table [1](#S5.T1) suggest that including NLEX data as part of the mix boosts output-prediction capabilities also after RL. While RL on output prediction with a standard reasoning SFT data (i.e., OMR and OCR) shows impressive performance, mixing them with NLEX provides superior results across both model sizes. To understand the effect of the RL phase, we additionally evaluate CWM on output prediction with and without RL. As expected, the RL phase significantly improves results on output prediction, see Appendix [A.1.2](#A1.SS1.SSS2) and Table [8](#A1.T8) for more details.

Self-execution prediction. So far we evaluated output-prediction capabilities on code generated by external models. We now turn to evaluate *self-execution*, i.e. models perform output-prediction on their own generated solutions. For that we post-train CWM and Qwen2.5-7B on both output prediction and competitive problems solving. We report results for questions derived from both LCB-IO and DMC in Table [2](#S6.T2) and compare performance to models trained to perform output-prediction only (as a topline) and to the official CWM model (as a baseline). As expected, results suggest that jointly training both models for solving competitive programming questions and output prediction perform worse than output prediction only. For instance, CWM reaches $80.2$ and $86.5$ pass@1 scores in joint training compared to $85.0$ and $88.6$ scores when trained for output prediction only. However, both are significantly superior to the official CWM model, that reaches $57.7$ pass@1. Interestingly, these results suggest that unlike previous findings (Gu et al., 2024a) models can reliably perform self-execution.

**Table 2: Output prediction performance for models trained on standard code solving, jointly with output prediction (Joint), on their own solutions. We compare this to a model trained for output prediction only, models from Tab. [1](#S5.T1), (Out Pred), and official CWM.**
| Model | RL obj. | DMC-Out | LCB-IO-Out |  |  |
| --- | --- | --- | --- | --- | --- |
|  |  | @1 | @5 | @1 | @5 |
| CWM | official | 57.7 | 80.4 | 68.6 | 87.9 |
|  | Joint | 80.2 | 87.2 | 86.5 | 91.0 |
|  | Out Pred | 85.0 | 89.8 | 88.6 | 92.7 |
| Qwen-7B | Joint | 68.4 | 83.1 | 76.5 | 87.1 |
|  | Out Pred | 74.6 | 86.8 | 80.1 | 89.2 |

### 6.2 Self-Execution for Competitive Programming

**Table 3: Solve rates for training and evaluating with a standard reasoning approach vs using real or simulated execution feedback.**
|  | DMC | LCB-IO |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | pass@1 | pass@5 | pass@10 | public | pass@1 | pass@5 | pass@10 | public |
| Execution RLEF (Oracle) | 65.3 | 77.6 | 80.6 | 86.1 | 63.8 | 70.9 | 72.8 | 88.5 |
| CWM (official) | 49.0 | 63.7 | 67.9 | 60.8 | 57.4 | 67.3 | 70.1 | 71.4 |
| CWM RL | 60.8 | 72.8 | 76.0 | 74.7 | 61.0 | 67.6 | 69.2 | 82.9 |
| Self-RLEF (Ours) | 63.2 | 76.8 | 80.2 | 82.5 | 62.3 | 70.0 | 71.9 | 87.1 |

##### Self-verification.

Given a model’s prediction of the execution output of its own code on public tests, one can use this to self-verify the solutions. Specifically, following the best@k simulate approach described in [Section 3](#S3), we select and submit the solution predicted to pass most tests. To better estimate the effectiveness of the proposed method, we compare it to short1@k (Hassid et al., 2025), which selects the shortest response among the $k$ solutions, and pass@k (for reference). To directly assess the quality of execution simulation, we also compare against an oracle that executes the public tests, following the same filtering procedure (denoted best@k exec). This comparison will provide us with the *simulation gap*, i.e., the performance gap between fully executing the code vs. simulating it with the model.
Our results provided in Fig. [4](#S5.F4) show that self-verification provides a large boost in performance under the best@k setup, ($2-8$ points compared to standard solving), *despite the tests used for filtering being provided when generating the solution*. This also outperforms short1@k. Notably, for Qwen2.5-7B the simulation gap is larger than CWM perhaps implying the need for larger or stronger models to learn to both solve and simulate execution effectively. Further results in Fig. [9](#A1.F9) show that using Qwen2.5-7B trained for output prediction only to filter the same solutions leads to a smaller gap.

##### Self-RLEF.

We train our model using the procedure described in [Section 4](#S4). We report pass@k scores for $k\in\{1,5,10\}$ on both LCB-IO and DMC, along with public-test pass rates. We evaluate three variants: the official CWM model, CWM post-trained specifically for competitive programming (CWM-RL), and CWM jointly optimised for output prediction and competitive programming with execution feedback. The latter is evaluated under the proposed self-RLEF framework, using either simulated execution or real execution as an oracle. In both settings, the model is allowed up to $10$ coding turns (initial solution + $9$ fix), although in practice, it uses $3.33$ turns on average (Appendix [A.1.4](#A1.SS1.SSS4) provides additional results with less turns). Results in [Table 3](#S6.T3) show that self-RLEF consistently outperforms both the official CWM and CWM-RL across all settings, improving pass rates on both public and private tests. Compared to the oracle, a performance gap remains, particularly for pass@1, indicating room for improvement in execution prediction. Interestingly, pass@1 scores (with 10 turns) are lower than the corresponding best@10 results shown in [Figure 4](#S5.F4). We hypothesise that this gap arises from limited exploration, as the model tends to iteratively fix a solution rather than explore alternative ones. In addition, the model frequently does not use all turns as seen by the average number of turns. For certain settings where an ”early exit” is preferred this approach can provide a better tradeoff considering compute.

### 6.3 Ablations

**Table 4: Comparing performance of using the self-RLEF scaffold at inference only with open source reasoning models.**
|  | DMC | LCB-IO |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Model \ Pass | @1 | @5 | @10 | @1 | @5 | @10 |
| Qwen3-32B | 44.7 | 61.4 | 66.0 | 58.6 | 68.9 | 72.2 |
| + SRLEF ($\Delta$) | -10.6 | -2.2 | -1.4 | -20.1 | -1.0 | -0.1 |
| CWM | 49.0 | 63.7 | 67.9 | 57.4 | 67.3 | 70.1 |
| + SRLEF ($\Delta$) | -4.8 | +0.5 | +0.9 | -7.4 | +0.1 | +0.2 |

Self-RLEF scaffold. One may wonder to what extent the self-refinement pipeline itself leads to the inference performance gain irrespective of model training. Hence, we investigate inference using the Self-RLEF approach with public open-weights models, specifically Qwen3-32B and CWM. We compare these results to using these models in a standard single turn inference procedure.
Results provided in [Table 4](#S6.T4) show no noticeable improvement from using the proposed self-RLEF approach, and even a decrease in performance across both models over all metrics and datasets. By manual analysis, we observe the model struggles to correctly predict the output, and ignores the feedback.

Figure: Figure 5: Comparing best@k when ranking Qwen3-32B solutions, using CWM post-trained only for output prediction as a verifier.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x5.png

Knowing when to submit or fix. To better identify the source of performance gains from self-RLEF, we analyse model behaviour during inference time. We measure how often the model successfully fixes a solution, i.e., cases where the initial solution fails the tests but the final solution passes, as well as how often it breaks a solution, i.e., where an initially passing solution fails after revision. For completeness, we also report cases where both the initial and final solutions either pass or fail the tests. [Table 5](#S6.T5) reports results for CWM on DMC using both public and private tests. Results suggest the model rarely degrades correct solutions, breaking only $1.2\%$ of cases on public tests and $5.0\%$ on private tests. In contrast, when the initial solution fails, the model frequently produces effective fixes, succeeding in $17.0\%$ of public-tests and $10.4\%$ of private-tests. These improvements increase the pass rate from $57.8\%$ for the initial solutions to $63.2\%$ for the final submissions.

**Table 5: Pass rates of the initial generated solution (Init), compared to the final submitted solution (Sub) in *Self-RLEF* inference on DMC considering both public and private tests.**
| Init\Sub | Fail | Pass |
| --- | --- | --- |
| Fail | 16.3% | 17.0% |
| Pass | 1.2% | 65.5% |

### 6.4 Beyond Self -Verification

While the focus of this work is *self*-execution, one could imagine use cases for building a model as a code simulator only. As an initial analysis, we measure public test pass rates for multiple models on LCB-IO and DMC to assess the potential of the best@k approach. [Table 6](#S6.T6) reports public pass@1 and pass@10 results for Qwen and CWM. While models can generate solutions which pass the public tests (as evidenced in pass@10), they often submit solutions which do not pass them *even though they are provided in the question*. This suggests that standard reasoning approaches under-utilise such test information. This observation motivates the use of solution verification.

We next assess the ability of our trained CWM model to predict execution outputs for solutions generated by Qwen3-32B. CWM achieves pass@1 and pass@5 scores of $86.1$ and $91.4$, respectively, on public test output prediction. Based on this, we apply the best@k evaluation on both LCB-IO and DMC, as shown in [Figure 5](#S6.F5). The results indicate that using CWM with this filtering strategy is very effective and can correctly filter solutions generated by external models. Furthermore, compared to real execution, we observe only a minor *simulation gap*. This again highlights the efficacy of the output prediction method to alleviate the need for execution, and further shows generalisation to other models’ solutions. Results for this setup using Qwen3-4B and CWM-RL are provided in Appendix [A.1](#A1.SS1), showing similar trends.

**Table 6: Public pass@1 and 10 of different models. The large gap of standard reasoning models can suggest that they under-utilise provided test information.**
|  | DMC | LCB-IO |  |  |
| --- | --- | --- | --- | --- |
| Model \ Public Pass | @1 | @10 | @1 | @10 |
| Qwen3-4B | 42.5 | 65.4 | 64.4 | 80.9 |
| Qwen3-32B | 56.3 | 79.0 | 72.3 | 88.8 |
| Qwen2.5-7B RL | 55.1 | 76.5 | 68.0 | 84.7 |
| CWM RL | 73.4 | 87.6 | 81.7 | 90.6 |

## 7 Related Work

##### Code Simulation & Verification.

Several works ask how well LLMs can simulate or predict the output of a given code snippet (Hora, 2024; Li et al., 2025; Gu et al., 2024b; Xu et al., 2025; Copet et al., 2025; Armengol-Estapé et al., 2025). Others suggest that models struggle to simulate their own code, as they are blind to its flaws (Gu et al., 2024a). Some works use models to simulate tool execution as part of a synthetic data generation (Kimi et al., 2025). Furthermore, some studies explicitly train a model as a verifier of solutions (Le et al., 2022). Many report challenges in verification performance (Ruan et al., 2025; Wang et al., 2025).

##### Learning from Feedback.

Gehring et al. (2025) showed that models can learn to utilise feedback about the execution of their generated code.
Providing models with access to interpreters is a popular approach that has been used to improve performance in maths (Chen et al., 2023b; Gao et al., 2023), code generation (Liu et al., 2023b; Shinn et al., 2023), competitive programming (Zheng et al., 2025), and agentic coding (Yang et al., 2024; Xia et al., 2025). Several prompting approaches were suggested for non-reasoning models to elicit self-improvement, often joint with external verification signals (Chen et al., 2023c; Renze and Guven, 2024; Madaan et al., 2023; Kumar et al., 2024). Chen et al. (2023a) further showed that training with human written feedback on code can improve performance.

## 8 Discussion

Limitations.
The main limitation of simulating program execution is estimating complex computational operations (e.g., multiplying large numbers, compute logarithms, etc.). Yet, while execution simulation is imperfect and can introduce noise, our findings suggest that it provides a useful inductive bias for reasoning about program behaviour, particularly in settings where direct execution is expensive or infeasible. Furthermore, while our approach showed promising results, it is currently limited to single file competitive programming questions. Generalising this to full repository SWE tasks poses an interesting future research direction.

Future Work. We believe our work opens several directions for future research. The most interesting direction in our opinion is using the full rich execution simulation, and not only the final output as feedback for iterative code fixing. Such feedback can convey richer information than the output alone (*even beyond real execution*), capturing not just what output is produced, but why it arises. Such explanations can reveal cases where a test appears to pass for incidental reasons, as well as provide insight into the underlying causes of failures. In preliminary results we observe that training with rich textual feedback presents challenges to training stability. We hypothesise this is due to both inability to train with teacher forcing and unclear definition of the verifiable reward of the simulation. We leave such exploration for future work.

## 9 Conclusion

In this work we investigated if LLMs can be trained to simulate code execution and whether this capability can be used to improve code generation. By combining SFT on NLEX with RLVR, we showed that models can acquire the ability to predict execution outcomes for general programs as well as code they generate. Leveraging this ability, we introduced *self-verification* and iterative *self-fix* strategies using predicted execution signals to select or refine candidate solutions without relying on external execution. Our empirical results on competitive programming tasks demonstrate consistent improvements over standard baselines considering both output prediction and question solving. Compared with real execution we show a relatively small *simulation gap*, demonstrating the usability of the proposed approach compared to the top-line of code execution. More broadly, our results suggest that enabling models to reason about the outcomes of the code they generate may be a key for building more reliable programming agents.

## Impact Statement

This paper presents work whose goal is to advance the field of Machine Learning. There are many potential societal consequences of our work, none which we feel must be specifically highlighted here.

## References

- W. U. Ahmad, S. Narenthiran, S. Majumdar, A. Ficek, S. Jain, J. Huang, V. Noroozi, and B. Ginsburg (2025)
Opencodereasoning: advancing data distillation for competitive coding.
arXiv preprint arXiv:2504.01943.
Cited by: [§5.1.1](#S5.SS1.SSS1.p1.1).
- J. Armengol-Estapé, Q. Carbonneaux, T. Zhang, A. H. Markosyan, V. Seeker, C. Cummins, M. Kambadur, M. F. O’Boyle, S. Wang, G. Synnaeve, et al. (2025)
What i cannot execute, i do not understand: training and evaluating llms on program execution traces.
arXiv preprint arXiv:2503.05703.
Cited by: [§1](#S1.p1.1),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- J. Austin, A. Odena, M. Nye, M. Bosma, H. Michalewski, D. Dohan, E. Jiang, C. Cai, M. Terry, Q. Le, et al. (2021)
Program synthesis with large language models.
Note: arXiv:2108.07732
External Links: [Link](https://arxiv.org/abs/2108.07732)
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1).
- M. Beck, J. Gehring, J. Kossen, and G. Synnaeve (2026)
Towards a neural debugger for python.
External Links: 2603.09951,
[Link](https://arxiv.org/abs/2603.09951)
Cited by: [§1](#S1.p1.1).
- S. Bengio, O. Vinyals, N. Jaitly, and N. Shazeer (2015)
Scheduled sampling for sequence prediction with recurrent neural networks.
Advances in neural information processing systems 28.
Cited by: [§4](#S4.p5.1).
- B. Bogin, K. Yang, S. Gupta, K. Richardson, E. Bransom, P. Clark, A. Sabharwal, and T. Khot (2024)
Super: evaluating agents on setting up and executing tasks from research repositories.
arXiv preprint arXiv:2409.07440.
Cited by: [§1](#S1.p2.1).
- J. S. Chan, N. Chowdhury, O. Jaffe, J. Aung, D. Sherburn, E. Mays, G. Starace, K. Liu, L. Maksin, T. Patwardhan, et al. (2024)
Mle-bench: evaluating machine learning agents on machine learning engineering.
arXiv preprint arXiv:2410.07095.
Cited by: [§1](#S1.p2.1).
- A. Chen, J. Scheurer, T. Korbak, J. A. Campos, J. S. Chan, S. R. Bowman, K. Cho, and E. Perez (2023a)
Improving code generation by training with natural language feedback.
arXiv preprint arXiv:2303.16749.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- W. Chen, X. Ma, X. Wang, and W. W. Cohen (2023b)
Program of thoughts prompting: disentangling computation from reasoning for numerical reasoning tasks.
Transactions on Machine Learning Research.
Note:
External Links: ISSN 2835-8856,
[Link](https://openreview.net/forum?id=YfZ4ZPt8zd)
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- X. Chen, M. Lin, N. Schärli, and D. Zhou (2023c)
Teaching large language models to self-debug.
arXiv preprint arXiv:2304.05128.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- K. Cobbe, V. Kosaraju, M. Bavarian, M. Chen, H. Jun, L. Kaiser, M. Plappert, J. Tworek, J. Hilton, R. Nakano, C. Hesse, and J. Schulman (2021)
Training verifiers to solve math word problems.
arXiv preprint arXiv:2110.14168.
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1).
- J. Copet, Q. Carbonneaux, G. Cohen, J. Gehring, J. Kahn, J. Kossen, F. Kreuk, E. McMilin, M. Meyer, Y. Wei, et al. (2025)
Cwm: an open-weights llm for research on code generation with world models.
arXiv preprint arXiv:2510.02387.
Cited by: [§1](#S1.p1.1),
[§2.1](#S2.SS1.p1.4),
[§2.1](#S2.SS1.p2.1),
[§2](#S2.p1.1),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- J. Ding, Y. Zhang, Y. Shang, Y. Zhang, Z. Zong, J. Feng, Y. Yuan, H. Su, N. Li, N. Sukiennik, et al. (2025)
Understanding world or predicting future? a comprehensive survey of world models.
ACM Computing Surveys 58 (3), pp. 1–38.
Cited by: [§1](#S1.p2.1).
- L. Gao, A. Madaan, S. Zhou, U. Alon, P. Liu, Y. Yang, J. Callan, and G. Neubig (2023)
PAL: program-aided language models.
In Proceedings of the 40th International Conference on Machine LearningProceedings of the 41st International Conference on Machine LearningForty-second International Conference on Machine Learning2025 IEEE/ACM Second International Conference on AI Foundation Models and Software Engineering (Forge)The Twelfth International Conference on Learning RepresentationsProceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE)Findings of the Association for Computational Linguistics ACL 2024Findings of the Association for Computational Linguistics: EMNLP 2024The eleventh international conference on learning representationsThirty-seventh Conference on Neural Information Processing SystemsForty-second International Conference on Machine LearningCompanion Proceedings of the 32nd ACM International Conference on the Foundations of Software Engineering, A. Krause, E. Brunskill, K. Cho, B. Engelhardt, S. Sabato, J. Scarlett, R. Salakhutdinov, Z. Kolter, K. Heller, A. Weller, N. Oliver, J. Scarlett, F. Berkenkamp, W. Che, J. Nabende, E. Shutova, and M. T. Pilehvar (Eds.),
Proceedings of Machine Learning ResearchProceedings of Machine Learning Research, Vol. 202235, pp. 10764–10799.
External Links: [Link](https://proceedings.mlr.press/v202/gao23f.html)
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- J. Gehring, K. Zheng, J. Copet, V. Mella, T. Cohen, and G. Synnaeve (2025)
RLEF: grounding code LLMs in execution feedback with reinforcement learning.
External Links: [Link](https://openreview.net/forum?id=PzSG5nKe1q)
Cited by: [§1](#S1.p2.1),
[§1](#S1.p3.1),
[§4](#S4.p1.1),
[§5.1.2](#S5.SS1.SSS2.p3.1),
[§7](#S7.SS0.SSS0.Px2.p1.1).
- A. Grattafiori, A. Dubey, A. Jauhri, A. Pandey, A. Kadian, A. Al-Dahle, A. Letman, A. Mathur, A. Schelten, A. Vaughan, et al. (2024)
The llama 3 herd of models.
arXiv preprint arXiv:2407.21783.
Cited by: [§2.1](#S2.SS1.p1.4).
- A. Gu, W. Li, N. Jain, T. Olausson, C. Lee, K. Sen, and A. Solar-Lezama (2024a)
The counterfeit conundrum: can code language models grasp the nuances of their incorrect generations?.
pp. 74–117.
Cited by: [§1](#S1.p1.1),
[§6.1](#S6.SS1.p3.5),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- A. Gu, B. Roziere, H. J. Leather, A. Solar-Lezama, G. Synnaeve, and S. Wang (2024b)
CRUXEval: a benchmark for code reasoning, understanding and execution.
pp. 16568–16621.
External Links: [Link](https://proceedings.mlr.press/v235/gu24c.html)
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1),
[§1](#S1.p4.3),
[§5.1.2](#S5.SS1.SSS2.p4.1),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- D. Ha and J. Schmidhuber (2018)
World models.
arXiv preprint arXiv:1803.10122 2 (3).
Cited by: [§1](#S1.p2.1).
- M. Hassid, T. Remez, J. Gehring, R. Schwartz, and Y. Adi (2024)
The larger the better? improved llm code-generation via budget reallocation.
arXiv preprint arXiv:2404.00725.
Cited by: [§3](#S3.p5.3).
- M. Hassid, G. Synnaeve, Y. Adi, and R. Schwartz (2025)
Don’t overthink it. preferring shorter thinking chains for improved llm reasoning.
arXiv preprint arXiv:2505.17813.
Cited by: [§6.2](#S6.SS2.SSS0.Px1.p1.2).
- A. Hora (2024)
Predicting test results without execution.
pp. 542–546.
Cited by: [§7](#S7.SS0.SSS0.Px1.p1.1).
- N. Jain, K. Han, A. Gu, W. Li, F. Yan, T. Zhang, S. Wang, A. Solar-Lezama, K. Sen, and I. Stoica (2024)
Livecodebench: holistic and contamination free evaluation of large language models for code.
arXiv preprint arXiv:2403.07974.
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1),
[§1](#S1.p4.3),
[§5.1.2](#S5.SS1.SSS2.p2.1).
- C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan (2023)
Swe-bench: can language models resolve real-world github issues?.
arXiv preprint arXiv:2310.06770.
Cited by: [§1](#S1.p2.1).
- R. Kamoi, Y. Zhang, N. Zhang, J. Han, and R. Zhang (2024)
When can llms actually correct their own mistakes? a critical survey of self-correction of llms.
Transactions of the Association for Computational Linguistics 12, pp. 1417–1440.
Cited by: [§1](#S1.p1.1).
- T. Kimi, Y. Bai, Y. Bao, G. Chen, J. Chen, N. Chen, R. Chen, Y. Chen, Y. Chen, Y. Chen, et al. (2025)
Kimi k2: open agentic intelligence.
arXiv preprint arXiv:2507.20534.
Cited by: [§1](#S1.p2.1),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- A. Kumar, V. Zhuang, R. Agarwal, Y. Su, J. D. Co-Reyes, A. Singh, K. Baumli, S. Iqbal, C. Bishop, R. Roelofs, et al. (2024)
Training language models to self-correct via reinforcement learning.
arXiv preprint arXiv:2409.12917.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- H. Le, Y. Wang, A. D. Gotmare, S. Savarese, and S. C. H. Hoi (2022)
Coderl: mastering code generation through pretrained models and deep reinforcement learning.
Advances in Neural Information Processing Systems 35, pp. 21314–21328.
Cited by: [§7](#S7.SS0.SSS0.Px1.p1.1).
- J. Li, D. Guo, D. Yang, R. Xu, Y. Wu, and J. He (2025)
CodeIO: condensing reasoning patterns via code input-output prediction.
External Links: [Link](https://openreview.net/forum?id=feIaF6vYFl)
Cited by: [§1](#S1.p1.1),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- Y. Li, D. Choi, J. Chung, N. Kushman, J. Schrittwieser, R. Leblond, T. Eccles, J. Keeling, F. Gimeno, A. Dal Lago, et al. (2022)
Competition-level code generation with alphacode.
Science 378 (6624), pp. 1092–1097.
Cited by: [§1](#S1.p4.3),
[§2.1](#S2.SS1.p1.4),
[§5.1.1](#S5.SS1.SSS1.p2.3),
[§5.1.2](#S5.SS1.SSS2.p3.1).
- H. Lightman, V. Kosaraju, Y. Burda, H. Edwards, B. Baker, T. Lee, J. Leike, J. Schulman, I. Sutskever, and K. Cobbe (2023)
Let’s verify step by step.
arXiv preprint arXiv:2305.20050.
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1).
- J. Liu, C. S. Xia, Y. Wang, and L. Zhang (2023a)
Is your code generated by chatGPT really correct? rigorous evaluation of large language models for code generation.
External Links: [Link](https://openreview.net/forum?id=1qvx610Cu7)
Cited by: [§A.1.1](#A1.SS1.SSS1.p1.1).
- Z. Liu, Y. Zhang, P. Li, Y. Liu, and D. Yang (2023b)
Dynamic llm-agent network: an llm-agent collaboration framework with agent team optimization.
External Links: 2310.02170
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- A. Madaan, N. Tandon, P. Gupta, S. Hallinan, L. Gao, S. Wiegreffe, U. Alon, N. Dziri, S. Prabhumoye, Y. Yang, et al. (2023)
Self-refine: iterative refinement with self-feedback.
Advances in Neural Information Processing Systems 36, pp. 46534–46594.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- MiniMax (2026)
M2.1: multilingual and multi-task coding with strong generalization.
Note: [https://x.com/MiniMax__AI/status/2007843119832695114](https://x.com/MiniMax__AI/status/2007843119832695114)
Cited by: [§1](#S1.p2.1).
- I. Moshkov, D. Hanley, I. Sorokin, S. Toshniwal, C. Henkel, B. Schifferer, W. Du, and I. Gitman (2025)
Aimo-2 winning solution: building state-of-the-art mathematical reasoning models with openmathreasoning dataset.
arXiv preprint arXiv:2504.16891.
Cited by: [§5.1.1](#S5.SS1.SSS1.p1.1).
- T. X. Olausson, J. P. Inala, C. Wang, J. Gao, and A. Solar-Lezama (2024)
Is self-repair a silver bullet for code generation?.
External Links: [Link](https://openreview.net/forum?id=y0GJXRungR)
Cited by: [§1](#S1.p1.1).
- Y. Peng, A. D. Gotmare, M. R. Lyu, C. Xiong, S. Savarese, and D. Sahoo (2025)
PerfCodeGen: improving performance of llm generated code with execution feedback.
pp. 1–13.
External Links: [Document](https://dx.doi.org/10.1109/Forge66646.2025.00008)
Cited by: [§1](#S1.p2.1).
- C. Qian, E. C. Acikgoz, B. Li, X. Chen, Y. Zhang, B. He, Q. Luo, D. Hakkani-Tür, G. Tur, Y. Li, et al. (2026)
Current agents fail to leverage world model as tool for foresight.
arXiv preprint arXiv:2601.03905.
Cited by: [§4](#S4.p2.1).
- Qwen, :, A. Yang, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Li, D. Liu, F. Huang, H. Wei, H. Lin, J. Yang, J. Tu, J. Zhang, J. Yang, J. Yang, J. Zhou, J. Lin, K. Dang, K. Lu, K. Bao, K. Yang, L. Yu, M. Li, M. Xue, P. Zhang, Q. Zhu, R. Men, R. Lin, T. Li, T. Tang, T. Xia, X. Ren, X. Ren, Y. Fan, Y. Su, Y. Zhang, Y. Wan, Y. Liu, Z. Cui, Z. Zhang, and Z. Qiu (2025)
Qwen2.5 technical report.
External Links: 2412.15115,
[Link](https://arxiv.org/abs/2412.15115)
Cited by: [§5.1.1](#S5.SS1.SSS1.p2.3).
- M. Renze and E. Guven (2024)
Self-reflection in llm agents: effects on problem-solving performance.
arXiv preprint arXiv:2405.06682.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- C. Ruan, D. Jiang, Y. Wang, and W. Chen (2025)
Critique-coder: enhancing coder models by critique reinforcement learning.
arXiv preprint arXiv:2509.22824.
Cited by: [§5.2](#S5.SS2.p1.5),
[§7](#S7.SS0.SSS0.Px1.p1.1).
- N. Shinn, F. Cassano, A. Gopinath, K. R. Narasimhan, and S. Yao (2023)
Reflexion: language agents with verbal reinforcement learning.
In Thirty-seventh Conference on Neural Information Processing Systems,
External Links: [Link](https://openreview.net/forum?id=vAElhFcKW6)
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- J. Su, M. Ahmed, Y. Lu, S. Pan, W. Bo, and Y. Liu (2024)
Roformer: enhanced transformer with rotary position embedding.
Neurocomputing 568, pp. 127063.
Cited by: [§A.3](#A1.SS3.SSS0.Px1.p1.10).
- A. Thimmaiah, J. Zhang, J. Srinivasa, J. J. Li, and M. Gligoric (2025)
PLSemanticsBench: large language models as programming language interpreters.
arXiv preprint arXiv:2510.03415.
Cited by: [§1](#S1.p1.1).
- Y. Wang, X. Yue, and W. Chen (2025)
Critique fine-tuning: learning to critique is more effective than learning to imitate.
arXiv preprint arXiv:2501.17703.
Cited by: [§7](#S7.SS0.SSS0.Px1.p1.1).
- C. S. Xia, Z. Wang, Y. Yang, Y. Wei, and L. Zhang (2025)
Live-swe-agent: can software engineering agents self-evolve on the fly?.
arXiv preprint arXiv:2511.13646.
Cited by: [§1](#S1.p2.1),
[§7](#S7.SS0.SSS0.Px2.p1.1).
- R. Xu, J. Cao, Y. Lu, M. Wen, H. Lin, X. Han, B. He, S. Cheung, and L. Sun (2025)
CRUXEVAL-X: a benchmark for multilingual code reasoning, understanding and execution.
Vienna, Austria, pp. 23762–23779.
External Links: [Link](https://aclanthology.org/2025.acl-long.1158/),
[Document](https://dx.doi.org/10.18653/v1/2025.acl-long.1158),
ISBN 979-8-89176-251-0
Cited by: [§7](#S7.SS0.SSS0.Px1.p1.1).
- A. Yang, A. Li, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Gao, C. Huang, C. Lv, et al. (2025)
Qwen3 technical report.
arXiv preprint arXiv:2505.09388.
Cited by: [§2.1](#S2.SS1.p3.2).
- J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan, and O. Press (2024)
Swe-agent: agent-computer interfaces enable automated software engineering.
Advances in Neural Information Processing Systems 37, pp. 50528–50652.
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).
- S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. R. Narasimhan, and Y. Cao (2022)
React: synergizing reasoning and acting in language models.
Cited by: [§4](#S4.p3.1).
- J. Zheng, J. Zhang, Y. Luo, Y. Mao, Y. Gao, L. Du, H. Chen, and N. Zhang (2026)
Can we predict before executing machine learning agents?.
arXiv preprint arXiv:2601.05930.
Cited by: [§1](#S1.p2.1).
- K. Zheng, J. Decugis, J. Gehring, T. Cohen, benjamin negrevergne, and G. Synnaeve (2025)
What makes large language models reason in (multi-turn) code generation?.
In The Thirteenth International Conference on Learning Representations,
External Links: [Link](https://openreview.net/forum?id=Zk9guOl9NS)
Cited by: [§7](#S7.SS0.SSS0.Px2.p1.1).

## Appendix A Appendix.

### A.1 Additional Results

#### A.1.1 Supervised fine-tuning.

To confirm that our NLEX data mix does not negatively impact the performance of the model on general tasks at the expense of boosting output prediction, we look at several standard coding and maths benchmarks. Specifically we consider CruxEval-Input (Gu et al., 2024b), MBPP (Austin et al., 2021), HumanEval Plus (Liu et al., 2023a), LiveCodeBench v5 (Jain et al., 2024), GSM8k (Cobbe et al., 2021), and Math 500 (Lightman et al., 2023). As reported in Table [7](#A1.T7), using the NLEX data mix does not notably harm any metric, and even improves output prediction abilities as noted by CruxEval-Input.

**Table 7: Investigating the impact of the NLEX data mix compared to a standard reasoning and instruction following mix on various standard coding and maths benchmarks. All models are trained with supervised fine tuning for the same budget only changing the data.**
| Model | CruxEval-In | MBPP | HumanEval+ | LCBv5 | GSM8k | Math 500 |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-7B regular mix | 0.469 | 0.634 | 0.652 | 0.414 | 0.842 | 0.518 |
| + NLEX | 0.505 | 0.632 | 0.659 | 0.413 | 0.826 | 0.528 |
| Qwen2.5-3B regular mix | 0.361 | 0.522 | 0.543 | 0.195 | 0.748 | 0.398 |
| + NLEX | 0.445 | 0.524 | 0.537 | 0.203 | 0.729 | 0.406 |

#### A.1.2 The effect of RL on output prediction

To better evaluate the effect of additional RL phase on top of the SFT, we evaluate CWM model, trained with and without RL considering output prediction only. For a reference, we additionally include results for the official post-trained CWM model. Results are reported in [Table 8](#A1.T8). As expected, results suggest that the RL phase significantly improve results on output prediction over competitive programming questions. We omit Qwen results as without RL, their performance was significantly lower.

**Table 8: Output prediction performance of the CWM with and without RL. For reference we additionally report results for the official CWM model.**
| Base Model | LCB-IO-Out | DMC-Test-Out |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  | pass@1 | @5 | @10 | @1 | @5 | @10 |
| CWM (Official) | 60.4 | 79.3 | 82.0 | 68.9 | 85.8 | 87.8 |
| CWM (wo. RL) | 30.3 | 55.6 | 62.1 | 38.4 | 67.5 | 73.5 |
| CWM (w. RL) | 89.6 | 93.4 | 94.2 | 89.2 | 93.3 | 94.0 |

#### A.1.3 Self-Verification

To further analyse the impact if self-verification using self-execution simulation, we wanted to study a setup where the tests used for verification were not present at the time of generating the solutions. To that end, we generate solutions using a model trained jointly for output prediction and competitive programming solving, but without tests in the question description for training and inference. This represents a case where the tests for verification contain completely new information unseen when generating the solution. Results are provided in Figure [6](#A1.F6). These suggest that while removing the tests from the description has a negative notable impact on performance, much of the performance can be gained by filtering solutions using these tests. It can also suggest that tests not used for generating the solution could have a higher positive impact for verification, motivating future investigation of test generation.

Figure: Figure 6: Comparing best@k when ranking solutions generated by CWM post-trained jointly for solving and output prediction, using the same model as a verifier. The model here was trained and evaluated without the public tests as part of the description.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x6.png

#### A.1.4 Self-RLEF

By default we allow a maximum of $10$ turns for execution RLEF, and *Self-RLEF*. However in practice the model often submits its solution prior leading to an average of $3.33$ turns. We wish to consider the performance of *Self-RLEF* when limiting the number of solve turns to a maximum of $3$. We provide results in Table [9](#A1.T9). In practice the model uses an average of $2.38$ turns.

**Table 9: Solve rates when using real or simulated execution feedback, but limiting to $3$ turns. This extends Table [3](#S6.T3) under a more compute constraint setup.**
|  | DMC | LCB-IO |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | pass@1 | pass@5 | pass@10 | public | pass@1 | pass@5 | pass@10 | public |
| Self-RLEF (Ours) | 61.5 | 75.6 | 79.6 | 79.0 | 61.5 | 69.2 | 71.1 | 84.2 |
| Execution RLEF (Oracle) | 62.7 | 75.8 | 78.8 | 81.5 | 63.3 | 70.3 | 72.2 | 86.3 |

#### A.1.5 Beyond Self -Verification

We provide results for using a dedicated output prediction model as a tool for verifying solutions of other models in a best@k setup. Results provided in Figures [7](#A1.F7) and [8](#A1.F8) show consistent improvements from this approach, for both Qwen3-4B and CWM Solve-RL, with only a slight degradation compared to ground truth execution of these tests. Like the results for Qwen3-32B in the main paper this further demonstrates the efficacy of this approach.

Figure: Figure 7: Comparing best@k when ranking Qwen3-4B solutions, using CWM post-trained only for output prediction as a verifier.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x7.png

Figure: Figure 8: Comparing best@k when ranking solutions by CWM post-trained only for competitive programming solving (denoted SOLVE-RL in Table [3](#S6.T3)), using CWM post-trained only for output prediction as a verifier.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x8.png

We also provide results of using a dedicated verifier based on a smaller model (Qwen2.5-7B), on solutions generated by a model starting from the same base model. Results provided in Figure [9](#A1.F9) show that this method is also effective with models at this scale. This outperforms the performance in Figure [4](#S5.F4) which suggests that the constraint of having the same model for solving and verification does impose challenges especially with models with limited capacity.

Figure: Figure 9: Comparing best@k when ranking solutions by Qwen-7B post-trained for competitive programming solving, using Qwen-7B post-trained only for output prediction as a verifier. This mirrors the results for Qwen in Figure [4](#S5.F4), but when each model has a dedicated role.
Refer to caption: https://arxiv.org/html/2604.03253v1/2604.03253v1/x9.png

### A.2 Self-RLEF Example Inference

To demonstrate how the iterative self-fixing and self verification looks in practice in *Self-RLEF* we provide the (abbreviated) multi-turn inference for a successful LCB-IO solution using our model.

### A.3 Hyper-Parameters

##### Supervised Fine-Tuning.

All Qwen supervised fine-tuning use a sequence length of $65,536$ by applying scaled RoPE (Su et al., 2024) with a factor of two relative to the base models to support longer context. CWM uses a context length of $131,072$ like in the original paper. Models were trained for $15.5$k steps, with a batch size of $4$M tokens per-update step, for a total of $65$B tokens. They were trained using a peak learning rate of $8e-6$ after a warmup of $1$k steps.
The estimated compute per-training run is $7.9e21$ FLOPs for 7B, and $5.0e21$ for 3B. Both models were trained for ${\sim}20$ hours on 128 and 64 NVIDIA H100 GPUs respectively.

##### Reinforcement Learning.

We train the models on NVIDIA H100
GPUs, with a standard configuration of $192$ GPUs for a single training run of CWM, and $86$ for Qwen 7B and 3B. Typically 1/3 of the GPUs are used as trainers and the rest for rollouts. By default, we employ the maximum context of the model from SFT for generation, packing training sequences by maximum of 131,072
tokens, use a global batch size of 1M tokens, a group size of 8, discarding rollouts with a staleness of more than 8 off-policy steps. We train the CWM models for 10k update steps, and the Qwen models for 4k, as we noted loops and collapses with longer training. This corresponds to roughly 9B and 3.2B tokens respectively. We use the last checkpoint for CWM, as training was stable, and the best checkpoint based on pass@1 by DMCValidation for Qwen (at 200 step increments) as the training was more prone to degradation in the end of training. We use 400 steps of linear learning rate warmup to a peak $1.4e-7$, with gradient clipping at $0.1$.
For single turn solving jointly with output prediction we sample output prediction at $15\%$ of the time while the rest is for solving. For Self-RLEF we increase this ratio to $25\%$.

For sampling in evaluation we compare temperature $0.6$ and $1.0$, with top-p $0.95$ as these were common values for Qwen and CWM. We select the best per-model based on DMC pass@1 rates. For CWM results didn’t change notably for all training setups, and yet for Qwen with temperature of $0.6$ there were many loops leading to not finishing rollouts, this could be to the smaller model size. Thus for all Qwen models we use temperature $1.0$, as well as for all CWM models except of the results with two fixing turns which performed slightly better with $0.6$.

### A.4 Prompts

As mentioned in Section [2.1](#S2.SS1) the data is created by converting raw traces to natural language by prompting an LLM, followed by a verification procedure. Below we provide the prompt used for the conversion.

### A.5 Data Samples

We provide examples from our NLEX data below.

### A.3 Hyper-Parameters

##### Supervised Fine-Tuning.

All Qwen supervised fine-tuning use a sequence length of $65,536$ by applying scaled RoPE (Su et al., 2024) with a factor of two relative to the base models to support longer context. CWM uses a context length of $131,072$ like in the original paper. Models were trained for $15.5$k steps, with a batch size of $4$M tokens per-update step, for a total of $65$B tokens. They were trained using a peak learning rate of $8e-6$ after a warmup of $1$k steps.
The estimated compute per-training run is $7.9e21$ FLOPs for 7B, and $5.0e21$ for 3B. Both models were trained for ${\sim}20$ hours on 128 and 64 NVIDIA H100 GPUs respectively.

##### Reinforcement Learning.

We train the models on NVIDIA H100
GPUs, with a standard configuration of $192$ GPUs for a single training run of CWM, and $86$ for Qwen 7B and 3B. Typically 1/3 of the GPUs are used as trainers and the rest for rollouts. By default, we employ the maximum context of the model from SFT for generation, packing training sequences by maximum of 131,072
tokens, use a global batch size of 1M tokens, a group size of 8, discarding rollouts with a staleness of more than 8 off-policy steps. We train the CWM models for 10k update steps, and the Qwen models for 4k, as we noted loops and collapses with longer training. This corresponds to roughly 9B and 3.2B tokens respectively. We use the last checkpoint for CWM, as training was stable, and the best checkpoint based on pass@1 by DMCValidation for Qwen (at 200 step increments) as the training was more prone to degradation in the end of training. We use 400 steps of linear learning rate warmup to a peak $1.4e-7$, with gradient clipping at $0.1$.
For single turn solving jointly with output prediction we sample output prediction at $15\%$ of the time while the rest is for solving. For Self-RLEF we increase this ratio to $25\%$.

For sampling in evaluation we compare temperature $0.6$ and $1.0$, with top-p $0.95$ as these were common values for Qwen and CWM. We select the best per-model based on DMC pass@1 rates. For CWM results didn’t change notably for all training setups, and yet for Qwen with temperature of $0.6$ there were many loops leading to not finishing rollouts, this could be to the smaller model size. Thus for all Qwen models we use temperature $1.0$, as well as for all CWM models except of the results with two fixing turns which performed slightly better with $0.6$.

### A.4 Prompts

As mentioned in Section [2.1](#S2.SS1) the data is created by converting raw traces to natural language by prompting an LLM, followed by a verification procedure. Below we provide the prompt used for the conversion.

### A.5 Data Samples

We provide examples from our NLEX data below.

### A.5 Data Samples

We provide examples from our NLEX data below.
