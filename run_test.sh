#!/bin/bash

#SBATCH --job-name="Optimos V2 Test run"
#SBATCH --partition=testing
#SBATCH --time=00:05:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=16

module load any/python/3.8.3-conda
conda activate opti2

cd optimos_v2
poetry install
./o2_evaluation/data_collector.py --active-scenarios Purchasing --models "Tabu Search" --max-iterations 50 --dump-interval 10