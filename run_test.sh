#!/bin/bash

#SBATCH --job-name="Optimos V2 Test run"
#SBATCH --partition=testing
#SBATCH --time=00:15:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=17

module load any/python/3.8.3-conda
conda activate opti2

~/.conda/envs/opti2/bin/python ./o2_evaluation/data_collector.py \
    --active-scenarios Purchasing \
    --models "Tabu Search" \
    --max-iterations 50 \
    --dump-interval 10 \
    --max-non-improving-actions 800 \
    --max-threads 16 \
    --log-to-tensor-board True
