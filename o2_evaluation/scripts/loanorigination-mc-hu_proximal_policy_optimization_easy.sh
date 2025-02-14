#!/bin/bash

#SBATCH --job-name="Optimos V2 Run LoanOrigination-MC-HU Proximal Policy Optimization EASY"
#SBATCH --partition=main
#SBATCH --time=027:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1

module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "loanorigination-mc-hu_easy" \
    --active-scenarios "LoanOrigination-MC-HU" \
    --models "Proximal Policy Optimization" \
    --number-of-cases 1000 \
    --duration-fn "1/size" \
    --max-batch-size 100 \
    --max-iterations 15000 \
    --dump-interval 100 \
    --max-non-improving-actions 50 \
    --max-threads 24 \
    --log-level DEBUG \
    --log-file ./logs/proximal_policy_optimization_loanorigination-mc-hu_easy.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
