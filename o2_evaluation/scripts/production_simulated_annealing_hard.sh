#!/bin/bash

#SBATCH --job-name="Optimos V2 Run production Simulated Annealing HARD"
#SBATCH --partition=main
#SBATCH --time=05:00:00
#SBATCH --mem=48G
#SBATCH --cpus-per-task=24

export LD_LIBRARY_PATH="$HOME/lib"
module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "production_hard" \
    --active-scenarios "production" \
    --agents "Simulated Annealing" \
    --number-of-cases 500 \
    --duration-fn "1 * size" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 868 \
    --max-solutions 10000 \
    --dump-interval 1000 \
    --max-threads 23 \
    --max-number-of-actions-per-iteration 23 \
    --max-non-improving-actions 326 \
    --iterations-per-solution 3 \
    --max-number-of-variations-per-action 3 \
    --log-level DEBUG \
    --log-file ./logs/simulated_annealing_production_hard.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
