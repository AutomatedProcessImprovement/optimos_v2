#!/bin/bash

#SBATCH --job-name="Optimos V2 Run consulta_data_mining Proximal Policy Optimization EASY"
#SBATCH --partition=main
#SBATCH --time=024:00:00
#SBATCH --mem=30G
#SBATCH --cpus-per-task=6

export LD_LIBRARY_PATH="$HOME/lib"
module load any/python/3.8.3-conda
conda activate opti2

conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \
    --name "consulta_data_mining_easy" \
    --active-scenarios "consulta_data_mining" \
    --agents "Proximal Policy Optimization" \
    --number-of-cases 500 \
    --duration-fn "1/size" \
    --sa-cooling-factor auto \
    --sa-initial-temperature auto \
    --max-batch-size 50 \
    --max-iterations 10000 \
    --max-solutions 10000 \
    --dump-interval 10 \
    --max-threads 1 \
    --max-number-of-actions-per-iteration 23 \
    --max-non-improving-actions 500 \
    --iterations-per-solution 3 \
    --max-number-of-variations-per-action 3 \
    --log-level DEBUG \
    --log-file ./logs/proximal_policy_optimization_consulta_data_mining_easy.log \
    --log-to-tensor-board \
    --no-archive-tensorboard-logs
