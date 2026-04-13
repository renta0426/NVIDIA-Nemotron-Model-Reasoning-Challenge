Kaggle CLI — Develop Locally and Run on RTX Pro 6000 GPU
Repository note: this discussion records workflow and environment guidance, but it does not replace the repository competition contract. In this repo, the authoritative evaluation and submission contract remains the top-level `README.md` (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`, final artifact `submission.zip`). Treat the CLI workflow notes below as operational guidance rather than as overrides of the README evaluation or submission rules.

I have also added a notebook version for easier navigation (table of contents): [https://www.kaggle.com/code/citerne/from-local-dev-rtx-6000-kaggle-cli-guide]

Practical guide for the NVIDIA Nemotron Model Reasoning Challenge. Hard-won lessons on setting up a CLI → Kaggle GPU workflow, pitfalls to avoid, and everything you need to get started.

Why This Workflow?
The Kaggle web interface is great for exploration, but once you want to:

Iterate quickly on training code
Use a proper IDE with autocomplete and dev tools (e.g. Claude Code, Copilot)
Version and push from a local Git repo
…the develop locally → push with CLI workflow becomes essential.

1. Install the Kaggle CLI (from GitHub)
The PyPI version (kaggle==1.7.x) does not support the --accelerator flag, which is required to target the RTX Pro 6000 GPU. You need to install from GitHub.

📦 Repo: https://github.com/Kaggle/kaggle-api

Requirement: Python 3.11+ (the GitHub version requires ≥ 3.11)

If you're on Python 3.10 (Ubuntu 22.04 default), use uv:

# Install Python 3.11 via uv
uv python install 3.11

# Install Kaggle CLI from GitHub with Python 3.11
uv tool install git+https://github.com/Kaggle/kaggle-api.git --python 3.11 --force

# Verify
kaggle --version  # → Kaggle CLI 2.0.0
2. Configure Credentials
mkdir -p ~/.config/kaggle
echo '{"username":"YOUR_USERNAME","key":"YOUR_API_KEY"}' > ~/.config/kaggle/kaggle.json
chmod 600 ~/.config/kaggle/kaggle.json
Find your API key at kaggle.com → Settings → API → Create New Token.

3. The kernel-metadata.json File
Every kernel (notebook or script) is defined by a kernel-metadata.json in its folder.

📄 Official metadata spec: https://github.com/Kaggle/kaggle-api/blob/main/docs/kernels_metadata.md

{
  "id": "username/kernel-slug",
  "title": "My Kernel",
  "code_file": "script.py",
  "language": "python",
  "kernel_type": "script",
  "is_private": true,
  "enable_gpu": true,
  "enable_tpu": false,
  "enable_internet": false,
  "keywords": [],
  "dataset_sources": [],
  "kernel_sources": [
    "ryanholbrook/nvidia-utility-script"
  ],
  "competition_sources": [
    "nvidia-nemotron-model-reasoning-challenge"
  ],
  "model_sources": [
    "metric/nemotron-3-nano-30b-a3b-bf16/Transformers/default/1"
  ]
}
Key Fields
Field	Values	Notes
kernel_type	"script" or "notebook"	Script = .py, Notebook = .ipynb
enable_internet	true / false	Must be false with the RTX Pro 6000
kernel_sources	["user/slug"]	Utility scripts that run before your kernel
competition_sources	["competition-slug"]	Grants access to competition data
model_sources	["owner/model/framework/variant/version"]	Kaggle models to attach
Pro tip: The easiest way to get a correct metadata file is to configure your kernel once via the web UI, then pull it locally:

kaggle kernels pull username/kernel-slug --metadata -p my_folder/
This guarantees all fields are correct, especially id_no and source paths.

4. Essential Commands
📄 Full CLI reference: https://github.com/Kaggle/kaggle-api/blob/main/docs/kernels.md

# Push and run a kernel — prints a direct URL to the run page
kaggle kernels push -p my_folder/

# Push with a specific GPU (requires Kaggle CLI 2.0+)
kaggle kernels push -p my_folder/ --accelerator NvidiaRtxPro6000

# Check run status
kaggle kernels status username/kernel-slug

# Download output files (trained models, generated files)
kaggle kernels output username/kernel-slug -p ./outputs/

# Pull a notebook with cell outputs
kaggle kernels pull username/kernel-slug -p my_folder/ --metadata

# Delete a kernel
kaggle kernels delete username/kernel-slug --yes
Viewing Live Logs
After kaggle kernels push, the CLI prints a direct link to your run:

Kernel version 1 successfully pushed. Please check progress at
https://www.kaggle.com/code/username/kernel-slug
Click it and go to the Logs tab — logs stream in real time as your kernel runs.

Available Accelerators (Feb 2026)
NvidiaTeslaP100 | NvidiaTeslaT4 | NvidiaTeslaT4Highmem
NvidiaTeslaA100 | NvidiaL4 | NvidiaH100
NvidiaRtxPro6000  ← Nemotron competition only
TpuV38 | TpuV5E8 | TpuV6E8
5. Competition-Specific Constraint: RTX Pro 6000 + No Internet
The RTX Pro 6000 (Blackwell GPU exclusive to this competition) does not support internet access in the main kernel. This means you cannot pip install from PyPI at runtime.

The solution: Utility Scripts.

6. Utility Scripts — How They Work
A Utility Script is a kernel that runs before your main notebook/script. It prepares the environment (installs packages, sets up paths, etc.).

Kaggle provides an official utility script for this competition: ryanholbrook/nvidia-utility-script — installs torch nightly cu128, causal-conv1d, and mamba-ssm (required for the Blackwell GPU).

📓 Notebook: https://www.kaggle.com/code/ryanholbrook/nvidia-utility-script

# ryanholbrook/nvidia-utility-script (simplified)
import subprocess, os

env = os.environ.copy()
env["PYTHONPATH"] = f"/kaggle/working:{env.get('PYTHONPATH', '')}"

commands = [
    "uv pip uninstall torch torchvision torchaudio",
    "uv pip install --target=/kaggle/working --system --pre torch torchvision torchaudio "
    "--index-url https://download.pytorch.org/whl/nightly/cu128",
    "uv pip install --target=/kaggle/working --system --no-build-isolation 'causal-conv1d>=1.4.0'",
    "uv pip install --target=/kaggle/working --system --no-build-isolation "
    "'git+https://github.com/state-spaces/mamba.git'",
]
for cmd in commands:
    subprocess.run(cmd, shell=True, check=True, env=env)
Creating Your Own Utility Script
If you need additional packages (e.g. trl, datasets), create your own utility script following the same pattern, then push it:

kaggle kernels push -p my_utility_folder/
Then chain it after Ryan's in your main kernel's metadata:

"kernel_sources": [
    "ryanholbrook/nvidia-utility-script",
    "your-username/your-utility-script"
]
Use --no-deps to avoid reinstalling packages already provided by the system or Ryan's script:

uv pip install --target=/kaggle/working --system --no-deps datasets trl
⚠️ Where Utility Script Packages Are Mounted
This is a subtle but important point. Packages installed by a utility script to /kaggle/working are not automatically in sys.path for script kernels (.py). They are for notebook kernels (.ipynb).

Packages installed by ryanholbrook/nvidia-utility-script are available at:

/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script/
This path is automatically added to sys.path — which is why import mamba_ssm just works in notebooks.

For your own utility script, packages end up at /kaggle/input/your-utility-script/. You need to add it manually at the top of your script (not needed if in a notebook) :

import sys, os
if os.path.exists("/kaggle/input"):
    # Use append (not insert) to keep system packages as priority
    sys.path.append("/kaggle/input/your-utility-script")
7. Full Workflow Example — Training Script
Project Structure
my-project/
  src/training/
    sft_train.py          ← training code
    kernel-metadata.json  ← Kaggle kernel config
kernel-metadata.json
{
  "id": "username/nemotron-sft-training",
  "title": "Nemotron SFT Training",
  "code_file": "sft_train.py",
  "language": "python",
  "kernel_type": "script",
  "is_private": true,
  "enable_gpu": true,
  "enable_internet": false,
  "kernel_sources": ["ryanholbrook/nvidia-utility-script"],
  "competition_sources": ["nvidia-nemotron-model-reasoning-challenge"],
  "model_sources": ["metric/nemotron-3-nano-30b-a3b-bf16/Transformers/default/1"]
}
Run Training
# Push + run on RTX Pro 6000 — CLI prints a direct link to live logs
kaggle kernels push -p src/training/ --accelerator NvidiaRtxPro6000

# Poll status from terminal
kaggle kernels status username/nemotron-sft-training

# Retrieve the trained adapter once complete
kaggle kernels output username/nemotron-sft-training -p ./outputs/
8. Notebooks vs Scripts
Notebook .ipynb	Script .py
Cell outputs	Saved on Kaggle, retrievable via pull	Logs only
sys.path	/kaggle/working added automatically	Must add manually
Recommended for	EDA, visualization, final submission	Training, batch evaluation
Pull with outputs	kaggle kernels pull --metadata	N/A
8b. Three Ways to Work with Kaggle Notebooks
These options apply any time you're working with a Kaggle notebook — for EDA, visualization, quick experiments, etc. — independently of the CLI push/pull workflow.

Option 1 — Kaggle Web UI
Open your notebook on kaggle.com and edit directly in the browser. This is the default and requires no setup.

Pros: Zero setup. GPU, data sources, and output all in one place. Cons: Limited editor — no extensions, no AI tools, no custom keybindings.

Options 2 & 3 — Connect your local editor to Kaggle's GPU
Both of the next options use the same starting point: Kaggle's Jupyter server URL.

How to get the URL:

Open a notebook on Kaggle (interactive session, not a script run)
Before starting, configure the session: go to the Settings and select your accelerator (GPU type, internet access, etc.)
In the top menu, go to Run → Kaggle Jupyter Server
A panel appears on the right — click Start Session
Copy the VS Code-compatible URL shown at the bottom (it includes an auth token)
Option 2 — VS Code connected to Kaggle
Open a .ipynb file in VS Code
Click the kernel picker (top right) → "Select Another Kernel…" → "Existing Jupyter Server"
Paste the Kaggle URL
VS Code runs the cells on Kaggle's GPU while you edit locally.

Pros: Full VS Code environment — extensions, Copilot, Claude Code, custom theme and keybindings. Cons: VS Code's kernel management is poor (restarting, switching, variable inspector are clunky). Works only while the Kaggle session is active.

Option 3 — Local Jupyter (JupyterLab or Notebook)
Instead of VS Code, connect a local Jupyter interface to the same URL:

In JupyterLab: File → Hub Control Panel → or use the "Connect to server" option and paste the URL
In Jupyter Notebook: use --NotebookApp.remote_jupyter_server_url
Pros: Much better kernel management than VS Code (clean restart, kernel list, variable inspector). Still executes on Kaggle's GPU. Cons: You lose the VS Code environment — no extensions, no integrated terminal.

Summary
Kaggle Web	VS Code	Jupyter
Setup	None	Copy URL → kernel picker	Copy URL → server dialog
IDE comfort	Low	High	Medium
Kernel management	Good	Poor	Good
Extensions / tooling	Kaggle only	Full VS Code	Jupyter only
Best for	Quick edits, EDA	Heavy coding with AI tools	Debugging, kernel-heavy work
9. Pre-Launch Checklist
kernel-metadata.json present in the pushed folder
competition_sources has the correct slug (nvidia-nemotron-model-reasoning-challenge)
model_sources has the full model path
kernel_sources includes ryanholbrook/nvidia-utility-script
enable_internet: false (required with RTX Pro 6000)
Pushing with --accelerator NvidiaRtxPro6000
Based on hands-on experience competing in the NVIDIA Nemotron Model Reasoning Challenge (March 2026).

---

Luis
Posted 3 days ago

· 686th in this Competition

Thanks for this post, it is really helpful


Reply

React
Keanan
Topic Author
Posted 4 days ago

· 642nd in this Competition

new section 8b added : "8b. Three Ways to Work with Kaggle Notebooks"


Reply

React
Keanan
Topic Author
Posted 4 days ago

· 642nd in this Competition

A quick note from me 👋

This guide reflects the specific issues I ran into on my setup (Ubuntu 22.04, Python 3.10). Your mileage may vary — some steps might not apply to you, or you might hit different walls entirely.

I'm sharing this because I spent a lot of time figuring these things out and hope it saves someone else a few hours. If something doesn't work on your end, or if you've found a better way to do any of this, drop a comment — I'd love to hear it.

Good luck to everyone competing, and happy training! 🚀


Reply

React
Deval Mukherjee1
Posted 3 days ago

· 177th in this Competition

hey, did you have any issues with saving the outputs and downloading them or even having access to them after session closed ? I have wasted so many hours of gpu time just to get that (on web notebooks). Do you have any solutions to that ?


Reply

React
Keanan
Topic Author
Posted 3 days ago

· 642nd in this Competition

Hey! A few things to check:

First, did your kernel actually finish without errors? Sometimes it looks like it ran but silently failed — worth checking the logs carefully.

Second, where are you saving your outputs in the code? Everything needs to go to /kaggle/working/ .

What kind of output are you trying to recover — model weights, a generated file?


Reply

React
Keanan
Topic Author
Posted 3 days ago

· 642nd in this Competition

Also, one of the easiest ways to figure this out — look at the public notebooks other people have shared for this competition. Most of them save their outputs somewhere, so you can just see exactly what path they use and how they handle it. Saves a lot of trial and error.


Reply

React
Deval Mukherjee1
Posted 3 days ago

· 177th in this Competition

well for some of the runs I the notebook had errors. But for the ones with the success too when I do save version it just says "queued" and never saves. And I always save to working


Reply

React
Keanan
Topic Author
Posted 3 days ago

· 642nd in this Competition

if you're talking about after submitting predictions to the competition, yeah that's totally normal. The evaluation on this competition takes 1h+ because it's running inference on the full test set. That wait is expected.


Reply

React
Deval Mukherjee1
Posted 3 days ago

· 177th in this Competition

Nope, just running the notebook and trying to get the output from it.


Reply

React
Keanan
Topic Author
Posted 3 days ago

· 642nd in this Competition

did you make sure the kernel has actually finished before saving?
