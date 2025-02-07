#!/bin/bash

#SBATCH --job-name="Optimos V2 Test run"
#SBATCH --partition=main
#SBATCH --time=02:00:00
#SBATCH --mem=12G
#SBATCH --cpus-per-task=25

module load any/python/3.8.3-conda
conda activate opti2

~/.conda/envs/opti2/bin/python ./o2_evaluation/data_collector.py \
    --active-scenarios Purchasing \
    --models "Tabu Search" \
    --max-iterations 1500 \
    --dump-interval 250 \
    --max-non-improving-actions 1250 \
    --max-threads 24 \
    --log-to-tensor-board True
