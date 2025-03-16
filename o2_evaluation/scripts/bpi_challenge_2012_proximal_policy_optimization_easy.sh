#!/bin/bash

#SBATCH --job-name="Optimos V2 Run BPI_Challenge_2012 Proximal Policy Optimization EASY"
#SBATCH --partition=main
#SBATCH --time=024:00:00
#SBATCH --mem=30G
#SBATCH --cpus-per-task=6

export LD_LIBRARY_PATH="$HOME/lib"
module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "bpi_challenge_2012_easy" \
    --active-scenarios "BPI_Challenge_2012" \
    --agents "Proximal Policy Optimization" \
    --number-of-cases 500 \
    --duration-fn "1/size" \
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
    --log-file ./logs/proximal_policy_optimization_bpi_challenge_2012_easy.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
