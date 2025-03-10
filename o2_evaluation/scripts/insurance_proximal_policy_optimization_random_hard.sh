#!/bin/bash

#SBATCH --job-name="Optimos V2 Run insurance Proximal Policy Optimization Random HARD"
#SBATCH --partition=main
#SBATCH --time=012:00:00
#SBATCH --mem=10G
#SBATCH --cpus-per-task=2

export LD_LIBRARY_PATH="$HOME/lib"
module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "less_actions_insurance_hard" \
    --active-scenarios "insurance" \
    --agents "Proximal Policy Optimization Random" \
    --number-of-cases 1000 \
    --duration-fn "1 * size" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 10001 \
    --dump-interval 1000 \
    --max-threads 23 \
    --max-number-of-actions-per-iteration 23 \
    --max-non-improving-actions 2500 \
    --iterations-per-solution 2 \
    --max-number-of-variations-per-action 2 \
    --log-level DEBUG \
    --log-file ./logs/less_actions_proximal_policy_optimization_random_insurance_hard.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
