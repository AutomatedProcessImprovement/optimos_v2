import os
from textwrap import dedent

CORES = 25
MEMORY_GB = 32
MAX_TIME_HOURS = 2
MAX_ITERATIONS = 1500
DUMP_INTERVAL = 250
MAX_NON_IMPROVING_ACTIONS = 1250
NUMBER_OF_CASES = 1000


def generate_script(
    scenario: str, model: str, mode_name: str, max_batch_size: int, duration_fn: str
) -> str:
    """Generate a script for the given params."""
    model_name = model.replace(" ", "_").lower()
    scenario_name = scenario.replace(" ", "_").lower()
    mode_name_sanitized = mode_name.replace(" ", "_").lower()
    return dedent(f"""\
    #!/bin/bash

    #SBATCH --job-name="Optimos V2 Run {scenario} {model} {mode_name}"
    #SBATCH --partition=main
    #SBATCH --time=0{MAX_TIME_HOURS}:00:00
    #SBATCH --mem={MEMORY_GB}G
    #SBATCH --cpus-per-task={CORES}

    module load any/python/3.8.3-conda
    conda activate opti2

    conda run -n opti2 --no-capture-output python ./o2_evaluation/data_collector.py \\
        --active-scenarios "{scenario}" \\
        --models "{model}" \\
        --number-of-cases {NUMBER_OF_CASES} \\
        --duration-fn "{duration_fn}" \\
        --max-batch-size {max_batch_size} \\
        --max-iterations {MAX_ITERATIONS} \\
        --dump-interval {DUMP_INTERVAL} \\
        --max-non-improving-actions {MAX_NON_IMPROVING_ACTIONS} \\
        --max-threads {CORES - 1} \\
        --log-level DEBUG \\
        --log-file ./logs/{scenario_name}_{model_name}_{mode_name_sanitized}.log \\
        --log-to-tensor-board \\
        --no-archive-tensorboard-logs
    """)


SCENARIOS = [
    "BPI_Challenge_2012",
    "BPI_Challenge_2017",
    "consulta_data_mining",
    "LoanOrigination-MC-HU",
    "LoanOrigination-MC-LU",
    "LoanOrigination-SC-HU",
    "LoanOrigination-SC-LU",
    # TODO: Get correct production model
    # "production",
]

MODELS = ["Tabu Search", "Simulated Annealing", "Proximal Policy Optimization"]

MODES = [
    {"name": "EASY", "duration_fn": "1/size", "max_batch_size": 100},
    {"name": "MID", "duration_fn": "1 / (1 + log_100(x))", "max_batch_size": 100},
    {"name": "HARD", "duration_fn": "1 * size", "max_batch_size": 100},
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
                file_name = (
                    f"o2_evaluation/scripts/{scenario_name}_{model_name}_{mode_name}.sh"
                )
                with open(file_name, "w") as f:
                    f.write(script)

                # Make the script executable
                os.chmod(file_name, 0o755)
