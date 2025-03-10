#!/bin/bash

#SBATCH --job-name="Optimos V2 Run BPI_Challenge_2012 Tabu Search MID"
#SBATCH --partition=main
#SBATCH --time=05:00:00
#SBATCH --mem=48G
#SBATCH --cpus-per-task=24

export LD_LIBRARY_PATH="$HOME/lib"
module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "strict_ordered_bpi_challenge_2012_mid" \
    --active-scenarios "BPI_Challenge_2012" \
    --agents "Tabu Search" \
    --number-of-cases 1000 \
    --duration-fn "1 / (1 + (log(size) / log(100)))" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --sa-strict-ordered \
    --max-batch-size 50 \
    --max-iterations 1001 \
    --dump-interval 2400 \
    --max-threads 23 \
    --max-number-of-actions-per-iteration 23 \
    --max-non-improving-actions 5750 \
    --iterations-per-solution 3 \
    --max-number-of-variations-per-action 3 \
    --log-level DEBUG \
    --log-file ./logs/strict_ordered_tabu_search_bpi_challenge_2012_mid.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
