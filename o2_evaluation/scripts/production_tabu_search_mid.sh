#!/bin/bash

#SBATCH --job-name="Optimos V2 Run production Tabu Search MID"
#SBATCH --partition=main
#SBATCH --time=010:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=24

export LD_LIBRARY_PATH="$HOME/lib"
module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "production_mid" \
    --active-scenarios "production" \
    --agents "Tabu Search" \
    --number-of-cases 500 \
    --duration-fn "1 / (1 + (log(size) / log(100)))" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 868 \
    --max-solutions 10000 \
    --dump-interval 10 \
    --max-threads 23 \
    --max-number-of-actions-per-iteration 23 \
    --max-non-improving-actions 500 \
    --iterations-per-solution 3 \
    --max-number-of-variations-per-action 3 \
    --log-level DEBUG \
    --log-file ./logs/tabu_search_production_mid.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
