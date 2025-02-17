#!/bin/bash

#SBATCH --job-name="Optimos V2 Run LoanOrigination-MC-LU Simulated Annealing HARD"
#SBATCH --partition=main
#SBATCH --time=03:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=25

module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "loanorigination-mc-lu_hard" \
    --active-scenarios "LoanOrigination-MC-LU" \
    --models "Simulated Annealing" \
    --number-of-cases 1000 \
    --duration-fn "1 * size" \
    --max-batch-size 100 \
    --max-iterations 1500 \
    --dump-interval 250 \
    --max-non-improving-actions 1250 \
    --max-threads 24 \
    --log-level DEBUG \
    --log-file ./logs/simulated_annealing_loanorigination-mc-lu_hard.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
