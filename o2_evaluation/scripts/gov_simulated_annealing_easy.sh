#!/bin/bash

#SBATCH --job-name="Optimos V2 Run GOV Simulated Annealing EASY"
#SBATCH --partition=main
#SBATCH --time=05:00:00
#SBATCH --mem=48G
#SBATCH --cpus-per-task=24

export LD_LIBRARY_PATH="$HOME/lib"
module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "less_actions_gov_easy" \
    --active-scenarios "GOV" \
    --agents "Simulated Annealing" \
    --number-of-cases 1000 \
    --duration-fn "1/size" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 1001 \
    --dump-interval 2400 \
    --max-threads 23 \
    --max-number-of-actions-per-iteration 23 \
    --max-non-improving-actions 5750 \
    --iterations-per-solution 2 \
    --max-number-of-variations-per-action 2 \
    --log-level DEBUG \
    --log-file ./logs/less_actions_simulated_annealing_gov_easy.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
