#!/bin/bash

#SBATCH --job-name="Optimos V2 Run BPI_Challenge_2017 Proximal Policy Optimization HARD"
#SBATCH --partition=main
#SBATCH --time=02:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=25

module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "bpi_challenge_2017_hard" \
    --active-scenarios "BPI_Challenge_2017" \
    --models "Proximal Policy Optimization" \
    --number-of-cases 1000 \
    --duration-fn "1 * size" \
    --max-batch-size 100 \
    --max-iterations 1500 \
    --dump-interval 250 \
    --max-non-improving-actions 1250 \
    --max-threads 24 \
    --log-level DEBUG \
    --log-file ./logs/proximal_policy_optimization_bpi_challenge_2017_hard_2025-02-14T02:01:54.409780.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
