#!/bin/bash

#SBATCH --job-name="Optimos V2 Run production Tabu Search EASY"
#SBATCH --partition=main
#SBATCH --time=03:00:00
#SBATCH --mem=60G
#SBATCH --cpus-per-task=25

module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "production_easy" \
    --active-scenarios "production" \
    --models "Tabu Search" \
    --number-of-cases 1000 \
    --duration-fn "1/size" \
    --sa-cooling-factor 0.95 \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 1001 \
    --dump-interval 2500 \
    --max-non-improving-actions 500 \
    --max-threads 24 \
    --log-level DEBUG \
    --log-file ./logs/tabu_search_production_easy.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
