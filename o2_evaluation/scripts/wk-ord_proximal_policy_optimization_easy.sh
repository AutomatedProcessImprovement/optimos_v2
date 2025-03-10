#!/bin/bash

#SBATCH --job-name="Optimos V2 Run WK-ORD Proximal Policy Optimization EASY"
#SBATCH --partition=main
#SBATCH --time=012:00:00
#SBATCH --mem=10G
#SBATCH --cpus-per-task=2

export LD_LIBRARY_PATH="$HOME/lib"
module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "strict_ordered_wk-ord_easy" \
    --active-scenarios "WK-ORD" \
    --agents "Proximal Policy Optimization" \
    --number-of-cases 1000 \
    --duration-fn "1/size" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --sa-strict-ordered \
    --max-batch-size 50 \
    --max-iterations 10001 \
    --dump-interval 1000 \
    --max-threads 23 \
    --max-number-of-actions-per-iteration 23 \
    --max-non-improving-actions 2500 \
    --iterations-per-solution 3 \
    --max-number-of-variations-per-action 3 \
    --log-level DEBUG \
    --log-file ./logs/strict_ordered_proximal_policy_optimization_wk-ord_easy.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
