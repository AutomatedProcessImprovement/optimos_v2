#!/bin/bash

#SBATCH --job-name="Optimos V2 Run BPI_Challenge_2017 Tabu Search MID"
#SBATCH --partition=main
#SBATCH --time=03:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=25

module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "bpi_challenge_2017_mid" \
    --active-scenarios "BPI_Challenge_2017" \
    --models "Tabu Search" \
    --number-of-cases 1000 \
    --duration-fn "1 / (1 + (log(size) / log(100)))" \
    --max-batch-size 100 \
    --max-iterations 1500 \
    --dump-interval 250 \
    --max-non-improving-actions 1250 \
    --max-threads 24 \
    --log-level DEBUG \
    --log-file ./logs/tabu_search_bpi_challenge_2017_mid.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
