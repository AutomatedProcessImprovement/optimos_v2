#!/bin/bash

#SBATCH --job-name="Optimos V2 Run AC-CRD Proximal Policy Optimization MID"
#SBATCH --partition=main
#SBATCH --time=012:00:00
#SBATCH --mem=10G
#SBATCH --cpus-per-task=6

export LD_LIBRARY_PATH="$HOME/lib"
module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "ac-crd_mid" \
    --active-scenarios "AC-CRD" \
    --agents "Proximal Policy Optimization" \
    --number-of-cases 500 \
    --duration-fn "1 / (1 + (log(size) / log(100)))" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 10000 \
    --max-solutions 10000 \
    --dump-interval 1000 \
    --max-threads 23 \
    --max-number-of-actions-per-iteration 23 \
    --max-non-improving-actions 1000 \
    --iterations-per-solution 3 \
    --max-number-of-variations-per-action 3 \
    --log-level DEBUG \
    --log-file ./logs/proximal_policy_optimization_ac-crd_mid.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
