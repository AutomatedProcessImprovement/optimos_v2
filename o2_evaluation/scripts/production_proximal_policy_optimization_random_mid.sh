#!/bin/bash

#SBATCH --job-name="Optimos V2 Run production Proximal Policy Optimization Random MID"
#SBATCH --partition=main
#SBATCH --time=05:00:00
#SBATCH --mem=60G
#SBATCH --cpus-per-task=25

module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "production_mid" \
    --active-scenarios "production" \
    --agents "Proximal Policy Optimization Random" \
    --number-of-cases 1000 \
    --duration-fn "1 / (1 + (log(size) / log(100)))" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 1001 \
    --dump-interval 2500 \
    --max-non-improving-actions 500 \
    --max-threads 24 \
    --max-number-of-actions-to-select 24 \
    --log-level DEBUG \
    --log-file ./logs/proximal_policy_optimization_random_production_mid.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
