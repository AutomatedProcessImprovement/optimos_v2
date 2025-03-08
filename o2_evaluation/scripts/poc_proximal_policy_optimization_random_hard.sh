#!/bin/bash

#SBATCH --job-name="Optimos V2 Run POC Proximal Policy Optimization Random HARD"
#SBATCH --partition=main
#SBATCH --time=012:00:00
#SBATCH --mem=10G
#SBATCH --cpus-per-task=2

module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "poc_hard" \
    --active-scenarios "POC" \
    --agents "Proximal Policy Optimization Random" \
    --number-of-cases 1000 \
    --duration-fn "1 * size" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 10001 \
    --dump-interval 1000 \
    --max-threads 22 \
    --max-number-of-actions-per-iteration 22 \
    --max-non-improving-actions 100 \
    --iterations-per-solution 3 \
    --max-number-of-variations-per-action 3 \
    --log-level DEBUG \
    --log-file ./logs/proximal_policy_optimization_random_poc_hard.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
