#!/bin/bash

#SBATCH --job-name="Optimos V2 Run POC Simulated Annealing Random HARD"
#SBATCH --partition=main
#SBATCH --time=05:00:00
#SBATCH --mem=48G
#SBATCH --cpus-per-task=23

module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "poc_hard" \
    --active-scenarios "POC" \
    --agents "Simulated Annealing Random" \
    --number-of-cases 1000 \
    --duration-fn "1 * size" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 1001 \
    --dump-interval 2300 \
    --max-threads 22 \
    --max-number-of-actions-per-iteration 22 \
    --max-non-improving-actions 1100 \
    --iterations-per-solution 3 \
    --max-number-of-variations-per-action 3 \
    --log-level DEBUG \
    --log-file ./logs/simulated_annealing_random_poc_hard.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
