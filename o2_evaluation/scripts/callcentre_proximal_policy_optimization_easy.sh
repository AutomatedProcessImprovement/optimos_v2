#!/bin/bash

#SBATCH --job-name="Optimos V2 Run callcentre Proximal Policy Optimization EASY"
#SBATCH --partition=main
#SBATCH --time=012:00:00
#SBATCH --mem=12G
#SBATCH --cpus-per-task=2

module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "callcentre_easy" \
    --active-scenarios "callcentre" \
    --models "Proximal Policy Optimization" \
    --number-of-cases 1000 \
    --duration-fn "1/size" \
    --sa-cooling-factor 0.95 \
    --sa-initial-temperature auto \
    --max-batch-size 100 \
    --max-iterations 10001 \
    --dump-interval 2500 \
    --max-non-improving-actions 40 \
    --max-threads 24 \
    --log-level DEBUG \
    --log-file ./logs/proximal_policy_optimization_callcentre_easy.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
