#!/bin/bash

#SBATCH --job-name="Optimos V2 Run LoanOrigination-SC-HU Simulated Annealing MID"
#SBATCH --partition=main
#SBATCH --time=02:00:00
#SBATCH --mem=12G
#SBATCH --cpus-per-task=25

module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --active-scenarios "LoanOrigination-SC-HU" \
    --models "Simulated Annealing" \
    --number-of-cases 1000 \
    --duration-fn "1 / (1 + log_100(x))" \
    --max-batch-size 100 \
    --max-iterations 1500 \
    --dump-interval 250 \
    --max-non-improving-actions 1250 \
    --max-threads 24 \
    --log-level DEBUG \
    --log-file ./logs/loanorigination-sc-hu_simulated_annealing_mid.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
