#!/bin/bash

#SBATCH --job-name="Optimos V2 Run WK-ORD Simulated Annealing EASY"
#SBATCH --partition=main
#SBATCH --time=05:00:00
#SBATCH --mem=48G
#SBATCH --cpus-per-task=24

export LD_LIBRARY_PATH="$HOME/lib"
module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "strict_ordered_wk-ord_easy" \
    --active-scenarios "WK-ORD" \
    --agents "Simulated Annealing" \
    --number-of-cases 1000 \
    --duration-fn "1/size" \
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
    --log-file ./logs/strict_ordered_simulated_annealing_wk-ord_easy.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
