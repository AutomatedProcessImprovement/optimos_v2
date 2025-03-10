from math import ceil
import os
from textwrap import dedent

from o2.agents.agent import ACTION_CATALOG_BATCHING_ONLY

NAME_PREFIX = "strict_ordered_"

MAX_NUMBER_OF_ACTIONS_PER_ITERATION = len(ACTION_CATALOG_BATCHING_ONLY)
ITERATIONS_PER_SOLUTION = 3
# We go with a higher number than ITERATIONS_PER_SOLUTION,
MAX_NUMBER_OF_VARIATIONS_PER_ACTION = ITERATIONS_PER_SOLUTION


# Have one extra core for the main process
CORES = MAX_NUMBER_OF_ACTIONS_PER_ITERATION + 1
CORES_PPO = 2
MEMORY_GB = 48
MEMORY_GB_PPO = 10
MAX_TIME_HOURS = 5
MAX_TIME_HOURS_PPO = 12

MAX_SOLUTIONS = 10_000

# As an upper limit for the itearions, double the amount of "expected" iterations
# (E.g. solutions divided by actions per iteration (which is +/- 30% the number of solutions per iteration))
MAX_ITERATIONS = (MAX_SOLUTIONS // MAX_NUMBER_OF_ACTIONS_PER_ITERATION) * 2
# For PPO, because it's only doing one step per iteration,
# So iterations == solutions
MAX_ITERATIONS_PPO = MAX_SOLUTIONS

# We want 10 dumps per optimization run
DUMP_INTERVAL = MAX_SOLUTIONS // 10
DUMP_INTERVAL_PPO = MAX_SOLUTIONS // 10

# Early stopping after 10% of the max iterations without improvement
MAX_NON_IMPROVING_SOLUTIONS = ceil(0.1 * MAX_SOLUTIONS)
MAX_NON_IMPROVING_SOLUTIONS_PPO = ceil(0.1 * MAX_SOLUTIONS)

NUMBER_OF_CASES = 500
SA_COOLING_FACTOR = "auto"
SA_INITIAL_TEMPERATURE = "auto"


def generate_script(scenario: str, model: str, mode_name: str, max_batch_size: int, duration_fn: str) -> str:
    """Generate a script for the given params."""
    model_name = model.replace(" ", "_").lower()
    scenario_name = scenario.replace(" ", "_").lower()
    mode_name_sanitized = mode_name.replace(" ", "_").lower()
    memory_gb = MEMORY_GB if "Proximal Policy Optimization" not in model else MEMORY_GB_PPO
    cores = CORES if "Proximal Policy Optimization" not in model else CORES_PPO
    max_time_hours = MAX_TIME_HOURS if "Proximal Policy Optimization" not in model else MAX_TIME_HOURS_PPO
    max_iterations = MAX_ITERATIONS if "Proximal Policy Optimization" not in model else MAX_ITERATIONS_PPO
    dump_interval = DUMP_INTERVAL if "Proximal Policy Optimization" not in model else DUMP_INTERVAL_PPO

    return dedent(f"""\
    #!/bin/bash

    #SBATCH --job-name="Optimos V2 Run {scenario} {model} {mode_name}"
    #SBATCH --partition=main
    #SBATCH --time=0{max_time_hours}:00:00
    #SBATCH --mem={memory_gb}G
    #SBATCH --cpus-per-task={cores}

    export LD_LIBRARY_PATH="$HOME/lib"
    module load any/python/3.8.3-conda
    conda activate opti2

    conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \\
        --name "{NAME_PREFIX}{scenario_name}_{mode_name_sanitized}" \\
        --active-scenarios "{scenario}" \\
        --agents "{model}" \\
        --number-of-cases {NUMBER_OF_CASES} \\
        --duration-fn "{duration_fn}" \\
        --sa-cooling-factor {SA_COOLING_FACTOR} \\
        --sa-initial-temperature {SA_INITIAL_TEMPERATURE} \\
        --sa-strict-ordered \\
        --max-batch-size {max_batch_size} \\
        --max-iterations {max_iterations} \\
        --max-solutions {MAX_SOLUTIONS} \\
        --dump-interval {dump_interval} \\
        --max-threads {CORES - 1} \\
        --max-number-of-actions-per-iteration {MAX_NUMBER_OF_ACTIONS_PER_ITERATION} \\
        --max-non-improving-actions {MAX_NON_IMPROVING_SOLUTIONS} \\
        --iterations-per-solution {ITERATIONS_PER_SOLUTION} \\
        --max-number-of-variations-per-action {MAX_NUMBER_OF_VARIATIONS_PER_ACTION} \\
        --log-level DEBUG \\
        --log-file ./logs/{NAME_PREFIX}{model_name}_{scenario_name}_{mode_name_sanitized}.log \\
        --log-to-tensor-board \\
        --no-archive-tensorboard-logs
    """)


SCENARIOS = [
    "BPI_Challenge_2012",
    "BPI_Challenge_2017",
    "callcentre",
    "consulta_data_mining",
    "insurance",
    "production",
    "purchasing_example",
    "POC",
    "AC-CRD",
    "GOV",
    "WK-ORD",
    "BPIC2019_DAS",
    "Sepsis_DAS",
    "Trafic_DAS",
]

MODELS = [
    "Tabu Search",
    "Simulated Annealing",
    "Proximal Policy Optimization",
    "Tabu Search Random",
    "Simulated Annealing Random",
    "Proximal Policy Optimization Random",
]

MODES = [
    {"name": "EASY", "duration_fn": "1/size", "max_batch_size": 50},
    {
        "name": "MID",
        "duration_fn": "1 / (1 + (log(size) / log(100)))",
        "max_batch_size": 50,
    },
    {"name": "HARD", "duration_fn": "1 * size", "max_batch_size": 50},
]


if __name__ == "__main__":
    # Make scripts dir
    os.makedirs("o2_evaluation/scripts", exist_ok=True)
    # Delete all existing scripts
    for file in os.listdir("o2_evaluation/scripts"):
        os.remove(os.path.join("o2_evaluation/scripts", file))
    for scenario in SCENARIOS:
        for model in MODELS:
            for mode in MODES:
                script = generate_script(
                    scenario,
                    model,
                    mode["name"],
                    mode["max_batch_size"],
                    mode["duration_fn"],
                )
                model_name = model.replace(" ", "_").lower()
                scenario_name = scenario.replace(" ", "_").lower()
                mode_name = mode["name"].replace(" ", "_").lower()
                file_name = f"o2_evaluation/scripts/{scenario_name}_{model_name}_{mode_name}.sh"
                with open(file_name, "w") as f:
                    f.write(script)

                # Make the script executable
                os.chmod(file_name, 0o755)
