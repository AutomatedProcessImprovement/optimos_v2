#!/bin/bash

#SBATCH --job-name="Optimos V2 Run BPI_Challenge_2012 Proximal Policy Optimization EASY"
#SBATCH --partition=main
#SBATCH --time=012:00:00
#SBATCH --mem=12G
#SBATCH --cpus-per-task=2

module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "bpi_challenge_2012_easy" \
    --active-scenarios "BPI_Challenge_2012" \
    --agents "Proximal Policy Optimization" \
    --number-of-cases 1000 \
    --duration-fn "1/size" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 10001 \
    --dump-interval 1000 \
    --max-non-improving-actions 40 \
    --max-threads 24 \
    --max-number-of-actions-to-select 24 \
    --log-level DEBUG \
    --log-file ./logs/proximal_policy_optimization_bpi_challenge_2012_easy.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
