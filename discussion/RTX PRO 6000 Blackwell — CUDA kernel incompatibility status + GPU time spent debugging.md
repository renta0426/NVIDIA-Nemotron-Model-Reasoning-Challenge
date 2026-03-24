RTX PRO 6000 Blackwell — CUDA kernel incompatibility status + GPU time spent debugging
The pre-installed mamba_ssm and causal_conv1d packages in the competition environment are compiled for sm_90, but the RTX PRO 6000 Blackwell GPU requires sm_120.

This means:

The demo notebook loads and saves weights fine (no forward pass required) Any actual training or inference immediately crashes with AcceleratorError: CUDA error: no kernel image is available for execution on the device Internet is disabled on the Blackwell accelerator, so we cannot pip install fixed packages The workaround (forcing Mamba's Python slow path + patching Triton's ptxas permissions) works but is extremely slow and incompatible with gradient checkpointing

I've spent hours of GPU time across multiple sessions just debugging environment issues — not training, not experimenting, just trying to get a single forward pass to complete. Based on the other threads here, I'm far from alone.

Two questions for the organizers:

Is there a timeline for updating the base environment with sm_120-compatible builds of mamba_ssm, causal_conv1d, and Triton? This is currently a blocker for every participant attempting to train on the provided hardware. ( i dont have strong enough local hardware for it )

Will GPU hours consumed debugging this infrastructure issue be credited back? The weekly GPU quota is limited, and a significant portion has been spent on an environment problem rather than actual competition work.

For context: I'm not just raising this from the sidelines. I've put significant time into dataset analysis and training data preparation, and I have a working notebook ready to go via slow-path workarounds. I just need the environment to cooperate so I can train at a reasonable speed.

I'm genuinely excited about this competition! The problem design is clever (love ciphers… nah, not those substitution ones) and the reasoning challenges are legitimately hard. Would love to focus that energy on training and iteration rather than fighting CUDA kernels.

Thanks for the op guys!

Pinned comments
Tiffany Xiang
Kaggle Staff
Posted 14 hours ago

The new Docker image with CUDA 12.8 and updated PyTorch and Triton is rolled out now! Thanks everyone for your patience :)


Reply

2
King Kush
Posted 11 hours ago

· 504th in this Competition

tiffany thanks for your hard work!! I did analysis this is what i found post update if this is expected everything is good ty KK

What's FIXED (can drop from notebooks):

sklearn — imports clean, no blocker needed flash_attn 2.8.3 — available, so packing=True is now safe (no cross-contamination warning)

What STILL needs fixing (keep in notebooks):

mamba_ssm — still from utility script, sys.path.insert still required

ptxas-blackwell — executable=False, still need to copy to /tmp

Triton get_ptxas_version — still fails ('>=' not supported between str and int), patch still needed trl — NOT installed, still need offline pip install

is_fast_path_available — still needs patching (model loaded but crashed before we could check)

New info:

transformers 5.3.0 from utility script (was unversioned before) datasets 4.8.3 pre-installed (don't need offline install for this one) Compute capability 12.0, 188 SMs — Blackwell confirmed CUDA driver 13.0, nvcc 12.8 flash_sdp enabled — flash attention works natively Model loads in 682s (~11 min), same as before


Reply

1
Anton Kratz
Posted 6 hours ago

· 555th in this Competition

I want to install mamba_ssm. It does not seem to be there post update. I try:

# Fix 1: Add utility script to Python path (provides mamba_ssm, triton, etc.)
sys.path.insert(0, '/kaggle/usr/lib/notebooks/ryanholbrook/nvidia_utility_script')
Then I get: ModuleNotFoundError: No module named 'cutlass'


Reply

React
Anton Kratz
Posted 6 hours ago

· 555th in this Competition

P.S.: I get the ModuleNotFoundError: No module named 'cutlass' even with https://www.kaggle.com/code/kingkush123/reasoning-challenge-starter-notebook from @kingkush123


Reply

React
King Kush
Posted 6 hours ago

· 504th in this Competition

anton get the latest version i fixed the mamba 3 issue.. should run now


Reply

React
Anton Kratz
Posted 5 hours ago

· 555th in this Competition

Thank you @kingkush123 Version 3 of 3? Yes just started it seems to be working! (I am during training stage right so of course it will take a couple of hours to finish). I think your notebook is extremely valuable.


Reply

React
King Kush
Posted 4 hours ago

· 504th in this Competition

Aton btw,,these are the failure modes i hit i have yet to get a valid train with convergence and im out of credits for 99 hours so see what you can find out until then ill be around i just cant train yet


Reply

1
Anton Kratz
Posted 4 hours ago

· 555th in this Competition

Please clarify what do you mean by "convergence"? convergence == "Training loss going down"?!?


Reply

React
King Kush
Posted 3 hours ago

· 504th in this Competition

yes exactly


Reply

React
Anton Kratz
Posted an hour ago

· 555th in this Competition

I ran your entire most reecent notebook. I submitted, it scores 0.56! Can confirm that this is legit.


Reply

React
King Kush
Posted 9 minutes ago

· 504th in this Competition

ok perfect.. thanks for the report👍


Reply

React

Hide replies
All other comments
Eidan Rosado
Posted 3 days ago

· 390th in this Competition

I ended up burning through a bit of the week's credits debugging, but I made the patches public (without my fine-tuning logic for now): https://www.kaggle.com/code/edyvision/nvidia-nemotron-submission-demo-w-blackwell-patch

Hope this unblocks some folks in the meantime while the official env gets updated! It is indeed exceptionally slow.


Reply

React
King Kush
Posted 3 days ago

· 504th in this Competition

thanks i also used gpu on this debugging and im out now so ill test your method when resets..i got working but no mamba cores was really slow training wasted like 6 hours got not much roi


Reply

React
Addison Howard
Kaggle Staff
Posted 4 days ago

We're working on upgrading the docker image and getting it released shortly!


Reply

2

2
Donald Galliano III
Topic Author
Posted 4 days ago

· 655th in this Competition

Thank you!


Reply

React
Jaisree D.R.
Posted 2 days ago

Hello, are there any updates on the docker image yet? Thank you!


Reply

React
Anton Kratz
Posted a day ago

· 555th in this Competition

Dear @addisonhoward has there been any progress on this issue? I want to participate in this challenge, however I depend on the provided Blackwell GPU. I have spend over 10 GPU hours on this plus more for troubleshooting, documented my work in a public notebook here on Kaggle, could not get it to work. I believe this really needs to be fixed from the Kaggle side, not by the much slower workarounds that the community could develop. I would be excited to implement some of the ideas that I have for increasing the reasoning score, however I feel the "AcceleratorError: CUDA error: no kernel image is available for execution on the device" issue is a real blocker.


Reply

React
King Kush
Posted a day ago

· 504th in this Competition

i set this up for you hope it helps https://www.kaggle.com/code/kingkush123/reasoning-challenge-starter-notebook


Reply

React
Dustin
Kaggle Staff
Posted 4 days ago

https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/681820#3422400

We're working on getting the default env updated. In the meantime, its probably best to dump the needed deps into a dataset/notebook, and then do an "offline" install of the upgrades on the rtx pro 6000 machine.