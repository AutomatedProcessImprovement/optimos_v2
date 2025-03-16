#!/bin/bash

#SBATCH --job-name="Optimos V2 Run AC-CRD Proximal Policy Optimization Random HARD"
#SBATCH --partition=main
#SBATCH --time=024:00:00
#SBATCH --mem=30G
#SBATCH --cpus-per-task=6

export LD_LIBRARY_PATH="$HOME/lib"
module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "ac-crd_hard" \
    --active-scenarios "AC-CRD" \
    --agents "Proximal Policy Optimization Random" \
    --number-of-cases 500 \
    --duration-fn "1 * size" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 10000 \
    --max-solutions 10000 \
    --dump-interval 200 \
    --max-threads 23 \
    --max-number-of-actions-per-iteration 23 \
    --max-non-improving-actions 500 \
    --iterations-per-solution 3 \
    --max-number-of-variations-per-action 3 \
    --log-level DEBUG \
    --log-file ./logs/proximal_policy_optimization_random_ac-crd_hard.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
