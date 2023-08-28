#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --mem=20GB
#SBATCH --job-name=count_canonical_tokens

module purge

singularity exec --nv \
            --overlay /vast/bc3194/pytorch-example/my_pytorch.ext3:ro \
            /scratch/work/public/singularity/cuda11.7.99-cudnn8.5-devel-ubuntu22.04.2.sif\
            /bin/bash -c "source /ext3/env.sh; export TRANSFORMERS_CACHE='/vast/bc3194/huggingface_cache'; python -u count_canonical_tokens.py --test_lines "${SLURM_ARRAY_TASK_ID}
