import io
import os
import traceback

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

# Import TensorBoard utilities (make sure TensorFlow is installed)
from tensorboard.backend.event_processing.event_accumulator import (
    STORE_EVERYTHING_SIZE_GUIDANCE,
    EventAccumulator,
)
from tensorflow.python.framework import tensor_util


# -----------------------------------------------------------------------------
# 1. Data Extraction and Augmentation
# -----------------------------------------------------------------------------
def tflog2pandas(path: str) -> pd.DataFrame:
    """Convert a single TensorBoard log file to a pandas DataFrame,
    adding a 'time per step' metric computed from global/iteration events.

    The function loads each tensor event (including its wall_time), and then
    computes the per-step time (using differences) for the 'global/iteration' metric.
    """
    runlog_data = pd.DataFrame({"metric": [], "value": [], "step": [], "time": []})
    try:
        event_acc = EventAccumulator(path, STORE_EVERYTHING_SIZE_GUIDANCE)
        event_acc.Reload()
        tensors = event_acc.Tags().get("tensors", [])
        for tensor in tensors:
            event_list = event_acc.Tensors(tensor)
            # Extract values, steps, and wall times from each event.
            values = [tensor_util.MakeNdarray(x.tensor_proto) for x in event_list]
            steps = [x.step for x in event_list]
            times = [x.wall_time for x in event_list]
            df_temp = pd.DataFrame(
                {"metric": [tensor] * len(steps), "value": values, "step": steps, "time": times}
            )
            runlog_data = pd.concat([runlog_data, df_temp], ignore_index=True)
    except Exception:
        print("Event file possibly corrupt:", path)
        traceback.print_exc()

    # Compute "time per step" from global/iteration events.
    ref_df = runlog_data[runlog_data["metric"] == "global/iteration"].copy()
    ref_df.sort_values("step", inplace=True)
    if len(ref_df) >= 2:
        ref_df["time_diff"] = ref_df["time"].diff()
        ref_df["step_diff"] = ref_df["step"].diff()
        ref_df["time_per_step"] = ref_df["time_diff"] / ref_df["step_diff"]
        # Remove the first row (NaN) and create new rows for the metric.
        tps_df = ref_df.iloc[1:][["step", "time_per_step"]].copy()
        tps_df.rename(columns={"time_per_step": "value"}, inplace=True)
        tps_df["metric"] = "time per step"
        tps_df = tps_df[["metric", "value", "step"]]
        runlog_data = pd.concat([runlog_data, tps_df], ignore_index=True)

    # Optionally, drop the "time" column if not needed:
    # runlog_data.drop(columns=["time"], inplace=True)

    return runlog_data


def parse_folder_name(folder_name: str):
    """
    Parse a folder name such as:
      proximal_policy_optimization_bpi_challenge_2012_hard_2025-03-12T16:41:59.084145
    into:
      Agent  = "Proximal Policy Optimization" or "Proximal Policy Optimization Random"
      Model  = the remaining part (e.g. "Bpi Challenge 2012")
      Mode   = "Easy", "Mid", or "Hard"
      Timestamp = the remaining timestamp string.

    The search prioritizes longer agent tokens.
    """
    agents_ordered = [
        ("proximal_policy_optimization_random", "Proximal Policy Optimization Random"),
        ("simulated_annealing_random", "Simulated Annealing Random"),
        ("tabu_search_random", "Tabu Search Random"),
        ("proximal_policy_optimization", "Proximal Policy Optimization"),
        ("simulated_annealing", "Simulated Annealing"),
        ("tabu_search", "Tabu Search"),
    ]
    lower_name = folder_name.lower()
    agent_found = None
    for token, agent_name in agents_ordered:
        if lower_name.startswith(token):
            agent_found = agent_name
            token_len = len(token)
            break
    if agent_found is None:
        raise ValueError("Agent not recognized in folder name: " + folder_name)
    remainder = lower_name[token_len:].strip("_")  # type: ignore

    # Look for mode tokens: _easy_, _mid_ or _hard_
    mode = None
    model = None
    timestamp = None
    for m in ["easy", "mid", "hard"]:
        m_token = f"_{m}_"
        if m_token in remainder:
            parts = remainder.split(m_token)
            model = parts[0]
            timestamp = parts[1] if len(parts) > 1 else ""
            mode = m.title()
            break
        elif remainder.endswith(f"_{m}"):
            model = remainder[: -(len(m) + 1)]
            mode = m.title()
            timestamp = ""
            break
    if mode is None:
        raise ValueError("Mode not recognized in folder name: " + folder_name)
    model = model.replace("_", " ").title()  # type: ignore
    return agent_found, model, mode, timestamp


def load_all_event_data(root_dir: str) -> pd.DataFrame:
    """Walk over all folders in root_dir.

    Load their event file(s), and add
    Agent, Model, Mode, and Timestamp columns to the resulting DataFrame.
    If there are multiple folders for the same Agent-Model-Mode combination,
    only the one with the latest timestamp (as per lexicographical order) is used.
    """
    # Dictionary to hold the latest folder info for each (Agent, Model, Mode) combination.
    folder_info = {}
    for folder in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder)
        if os.path.isdir(folder_path):
            try:
                agent, model, mode, timestamp = parse_folder_name(folder)
            except ValueError as e:
                print("Skipping folder:", folder, e)
                continue
            key = (agent, model, mode)
            # Compare timestamps (ISO format allows lexicographical comparison)
            if key not in folder_info or timestamp > folder_info[key]["timestamp"]:
                folder_info[key] = {"folder": folder, "timestamp": timestamp}

    # Now load event data only from the selected (latest) folders.
    all_data = []
    for key, info in folder_info.items():
        folder = info["folder"]
        folder_path = os.path.join(root_dir, folder)
        # Look for event files starting with "events.out.tfevents"
        event_files = [f for f in os.listdir(folder_path) if f.startswith("events.out.tfevents")]
        if not event_files:
            continue
        # If multiple event files exist, sort and pick the last one.
        event_files.sort()
        event_path = os.path.join(folder_path, event_files[-1])
        df = tflog2pandas(event_path)
        # Re-parse to get proper values (they will be identical for this folder)
        agent, model, mode, timestamp = parse_folder_name(folder)
        df["Agent"] = agent
        df["Model"] = model
        df["Mode"] = mode
        df["Timestamp"] = timestamp
        all_data.append(df)
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


import os
import traceback
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image

# -----------------------------------------------------------------------------
# 1. Human Readable Metric Names and Explanations
# -----------------------------------------------------------------------------
human_metric_names = {
    "front/size": "Pareto Front Size",
    "global/solutions_tried": "Explored Solutions",
    "base_solutions": "Potential New Base Solutions",  # Combined metric for Tabu and SA.
    "front/avg_cycle_time": "Average Cycle Time",
    "front/min_cycle_time": "Min Cycle Time",
    "current_base/average_batch_size": "Average Batch Size",
    "global/iteration": "Iteration Number",
    "time per step": "Time per Step",  # NEW metric
    "Total Optimization Time": "Total Optimization Time",  # NEW column in summary table
}

metric_explanations = {
    "Pareto Front Size": "Number of solutions in the current Pareto Front.",
    "Steps": "Number of steps. Each step is a single mutation and simulation of a solution.",
    "Explored Solutions": "Total number of solutions for which all neighbors have been explored.",
    "Potential New Base Solutions": (
        "Potential new base solution within a small error radius for Tabu Search "
        "or within the temperature radius for Simulated Annealing."
    ),
    "Average Cycle Time": (
        "Average cycle time (from first enablement to the end of last activity) "
        "of all solutions in the current Pareto Front."
    ),
    "Min Cycle Time": "Minimum cycle time among all solutions in the current Pareto Front.",
    "Iteration Number": (
        "In one iteration, multiple mutations are performed. Depending on the agent, the solutions "
        "will be treated differently. Note that the number of solutions per iteration is not the same for all agents."
    ),
    "Average Batch Size": "Average number of tasks per batch (with a non batched task having a batch size of 1).",
    "Time per Step": "Average wall time per simulation step computed from differences between consecutive steps.",
    "Total Optimization Time": "Total wall clock time from the first to the last iteration (in minutes) ",
}

# Update the lists of metrics for plotting and summary.
report_metrics = [
    "front/size",
    "global/solutions_tried",
    "base_solutions",  # Combined metric for Tabu and SA.
    "front/avg_cycle_time",
    "front/min_cycle_time",
    "current_base/average_batch_size",
    "global/iteration",
    "time per step",  # NEW metric to be plotted
]

# For summary tables, drop "front/size" (it comes from the analyzer stats) but include the new metric.
summary_metrics = [
    "global/solutions_tried",
    "base_solutions",
    "front/avg_cycle_time",
    "front/min_cycle_time",
    "current_base/average_batch_size",
    "global/iteration",
    "time per step",  # NEW metric to be included in the summary table
]


# -----------------------------------------------------------------------------
# 2. Custom Number Formatting
# -----------------------------------------------------------------------------
def custom_format_number(cell):
    """
    Try to convert a string to a float and format it with two decimals,
    using '.' as thousands separator and ',' as decimal separator.
    If conversion fails, return the original string.
    """
    try:
        if not cell:
            return cell
        if "." in cell and "," in cell:
            value = float(cell.replace(".", "").replace(",", "."))
        else:
            value = float(cell.replace(",", "."))
        s = format(value, ",.2f")  # e.g. "1,234.56"
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return s
    except:
        return cell


# Define which metrics should be plotted using a logarithmic scale.
log_scale_metrics = ["base_solutions", "current_base/average_batch_size"]


# -----------------------------------------------------------------------------
# 3. Plot Generation with Fixed Figure Size (with caching, smoothing, and log scale)
# -----------------------------------------------------------------------------
def generate_plots(df: pd.DataFrame, output_dir: str, agent_colors: dict):
    plot_files = {}
    models = df["Model"].unique()
    for model in models:
        for mode in df[df["Model"] == model]["Mode"].unique():
            print(f"Processing plots for Model: {model}, Mode: {mode}...")
            subset = df[(df["Model"] == model) & (df["Mode"] == mode)]
            for metric in report_metrics:
                safe_metric = metric.replace("/", "_")
                filename = f"{model}_{mode}_{safe_metric}.png".replace(" ", "_")
                file_path = os.path.join(output_dir, filename)
                if os.path.exists(file_path):
                    print(
                        f"  Plot exists for {model} - {mode} - {human_metric_names.get(metric, metric)}. Skipping."
                    )
                    plot_files[(model, mode, metric)] = file_path
                    continue
                print(f"  Generating plot for {model} - {mode} - {human_metric_names.get(metric, metric)}...")
                plt.figure(figsize=(6, 4))
                for agent, agent_group in subset.groupby("Agent"):
                    if metric == "base_solutions":
                        # Combine Tabu and SA metrics.
                        tabu_data = agent_group[agent_group["metric"] == "tabu/solutions_left_in_radius"]
                        sa_data = agent_group[agent_group["metric"] == "sa/solutions_left_for_temperature"]
                        if tabu_data.empty and sa_data.empty:
                            continue
                        agent_data = pd.concat([tabu_data, sa_data])
                    elif metric == "time per step":
                        agent_data = agent_group[agent_group["metric"] == "time per step"]
                        if not agent_data.empty:
                            agent_data = agent_data.sort_values("step")
                            # Apply heavy smoothing (rolling average with window=50).
                            agent_data["value"] = agent_data["value"].rolling(window=50, min_periods=1).mean()
                    else:
                        agent_data = agent_group[agent_group["metric"] == metric]
                    if agent_data.empty:
                        continue
                    agent_data = agent_data.sort_values("step")
                    plt.plot(
                        agent_data["step"],
                        agent_data["value"],
                        label=agent,
                        color=agent_colors.get(agent, None),
                    )
                plt.xlabel("Solution (Step)")
                human_name = human_metric_names.get(metric, metric)
                plt.ylabel(human_name)
                plt.title(f"{model} - {mode} - {human_name}")
                plt.legend()
                # Apply logarithmic scale if required.
                if metric in log_scale_metrics:
                    plt.yscale("log")
                plt.savefig(file_path)
                plt.close()
                plot_files[(model, mode, metric)] = file_path
    return plot_files


# -----------------------------------------------------------------------------
# 4. Save Pareto Front Images (with caching and progress prints)
# -----------------------------------------------------------------------------
def save_pareto_front_images(df: pd.DataFrame, output_dir: str) -> dict:
    """
    For each (Model, Mode) and each agent, find the last 'pareto_front' event,
    extract the PNG image bytes (skipping the first two entries),
    and save the image as a PNG file if it doesn't already exist.
    """
    images = {}
    for (model, mode), group in df.groupby(["Model", "Mode"]):
        print(f"Processing Pareto Front images for Model: {model}, Mode: {mode}...")
        for agent in group["Agent"].unique():
            agent_group = group[group["Agent"] == agent]
            pf_group = agent_group[agent_group["metric"] == "pareto_front"]
            if pf_group.empty:
                continue
            last_pf = pf_group.loc[pf_group["step"].idxmax()]
            image_data = last_pf["value"]
            if isinstance(image_data, np.ndarray) and image_data.dtype == object:
                png_bytes = image_data[2] if image_data.shape[0] > 2 else image_data[0]
            else:
                png_bytes = image_data
            safe_agent = agent.replace(" ", "_")
            filename = f"{model}_{mode}_{safe_agent}_pareto_front.png".replace(" ", "_")
            file_path = os.path.join(output_dir, filename)
            if os.path.exists(file_path):
                print(f"  Pareto image for {model} - {mode} - {agent} exists. Skipping.")
                images[(model, mode, agent)] = file_path
                continue
            print(f"  Saving Pareto image for {model} - {mode} - {agent}...")
            img = Image.open(io.BytesIO(png_bytes))  # type: ignore
            img.save(file_path)
            images[(model, mode, agent)] = file_path
    return images


# -----------------------------------------------------------------------------
# 5. Summary Table Generation (Excluding Pareto Front Size, with Steps & Total Time)
# -----------------------------------------------------------------------------
def generate_summary_tables(df: pd.DataFrame) -> dict:
    """
    For each (Model, Mode) group, compute a summary table (rows: agents, columns: metrics)
    with the last (highest step) value for each metric (excluding Pareto Front Size).
    For the combined metric "base_solutions", data from both underlying metrics is concatenated.
    Also adds a column "Steps" (number of steps from the first to last iteration) and
    "Total Optimization Time" (formatted in hours and minutes with total step count).
    Returns a dict mapping (model, mode) to its summary DataFrame, with rows sorted by agent.
    """
    summary = {}
    for (model, mode), group in df.groupby(["Model", "Mode"]):
        rows = []
        for agent in sorted(group["Agent"].unique()):
            agent_group = group[group["Agent"] == agent]
            row = {"Agent": agent}
            for metric in summary_metrics:
                if metric == "base_solutions":
                    tabu_data = agent_group[agent_group["metric"] == "tabu/solutions_left_in_radius"]
                    sa_data = agent_group[agent_group["metric"] == "sa/solutions_left_for_temperature"]
                    if tabu_data.empty and sa_data.empty:
                        metric_group = pd.DataFrame()
                    else:
                        metric_group = pd.concat([tabu_data, sa_data])
                elif metric == "time per step":
                    metric_group = agent_group[agent_group["metric"] == "time per step"]
                else:
                    metric_group = agent_group[agent_group["metric"] == metric]
                if metric_group.empty:
                    row[metric] = None
                else:
                    last_row = metric_group.loc[metric_group["step"].idxmax()]
                    row[metric] = last_row["value"]
            # Compute Steps and Total Optimization Time from global/iteration events.
            global_iter = agent_group[agent_group["metric"] == "global/iteration"]
            if not global_iter.empty:
                steps = int(global_iter["step"].max() - global_iter["step"].min() + 1)
                total_time_sec = global_iter["time"].max() - global_iter["time"].min()
                minutes = int((total_time_sec) // 60)
                total_time_str = f"{minutes:,.0f}min<br/>(for {steps} Steps)"
            else:
                steps = None
                total_time_str = None
            row["Steps"] = steps
            row["Total Optimization Time"] = total_time_str
            rows.append(row)
        summary_df = pd.DataFrame(rows)
        # Reorder columns: Agent, Steps, then other metrics, then Total Optimization Time.
        cols = (
            ["Agent", "Steps"]
            + [c for c in summary_df.columns if c not in ["Agent", "Steps", "Total Optimization Time"]]
            + ["Total Optimization Time"]
        )
        summary_df = summary_df[cols]
        summary[(model, mode)] = summary_df
    return summary


# -----------------------------------------------------------------------------
# 6. Parsing the Analyzer Report (.ssv)
# -----------------------------------------------------------------------------
def parse_analyzer_report(file_path: str) -> dict:
    """
    Parses an analyzer report file (semicolon-separated) that contains advanced stats.
    The file is divided into sections per model (denoted by lines starting with "Sheet:").
    Returns a dictionary mapping model names to a list of groups.
    Each group is a tuple: (group_title, header_row, data_rows)
    """
    model_stats = {}
    current_model = None
    current_group_title = None
    current_header = None
    current_rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                if current_group_title is not None:
                    model_stats.setdefault(current_model, []).append(
                        (current_group_title, current_header, current_rows)
                    )
                    current_group_title = None
                    current_header = None
                    current_rows = []
                continue
            if line.startswith("---"):
                continue
            if line.startswith("Sheet:"):
                if current_group_title is not None and current_rows:
                    model_stats.setdefault(current_model, []).append(
                        (current_group_title, current_header, current_rows)
                    )
                    current_group_title = None
                    current_header = None
                    current_rows = []
                current_model = line.split("Sheet:")[1].strip()
                continue
            if not line.startswith(";"):
                if ";;" in line:
                    parts = line.split(";;", 1)
                    current_group_title = parts[0].strip()
                    header_part = parts[1].strip()
                    if header_part:
                        current_header = [x.strip() for x in header_part.split(";")]
                    else:
                        current_header = None
                else:
                    if line.startswith("#"):
                        subgroup = line.lstrip("#").strip()
                        if current_group_title:
                            current_group_title += " - " + subgroup
                        else:
                            current_group_title = subgroup
                    else:
                        if current_group_title is not None and current_rows:
                            model_stats.setdefault(current_model, []).append(
                                (current_group_title, current_header, current_rows)
                            )
                            current_group_title = None
                            current_header = None
                            current_rows = []
                        current_group_title = line.strip()
                continue
            if line.startswith(";"):
                row = [x.strip() for x in line.split(";")]
                current_rows.append(row)
        if current_group_title is not None and current_rows:
            model_stats.setdefault(current_model, []).append(
                (current_group_title, current_header, current_rows)
            )
    return model_stats


# -----------------------------------------------------------------------------
# 7. Table Formatter with Header Override
# -----------------------------------------------------------------------------
def format_markdown_table(header, rows):
    """
    Given an optional header (list of strings) and rows (list of lists of strings),
    returns a string representing a Markdown table.
    It removes an empty first column (if present) from both header and rows,
    applies custom number formatting to each cell, and if the resulting table has 4 columns,
    overrides the header with: ["Agent / Reference", "Easy", "Mid", "Hard"].
    """
    new_header = header[:] if header is not None else None
    if new_header and new_header[0] == "":
        new_header = new_header[1:]
    new_rows = []
    for row in rows:
        if row and row[0] == "":
            new_rows.append(row[1:])
        else:
            new_rows.append(row)
    new_rows = [[custom_format_number(cell) for cell in row] for row in new_rows]
    if new_rows and len(new_rows[0]) == 4:
        new_header = ["Agent / Reference", "Easy", "Mid", "Hard"]
    elif new_rows and new_header is not None and len(new_rows[0]) > len(new_header):
        new_header = ["Agent"] + new_header
    if new_header is None and new_rows:
        new_header = new_rows[0]
        new_rows = new_rows[1:]
    md = []
    if new_header:
        md.append("| " + " | ".join(new_header) + " |")
        md.append("|" + "|".join([" --- " for _ in new_header]) + "|")
    for row in new_rows:
        md.append("| " + " | ".join(row) + " |")
    return "\n".join(md)


# -----------------------------------------------------------------------------
# New Function: Create Composite Plot for Metrics
# -----------------------------------------------------------------------------
def create_composite_plot(model, mode, plot_files, composite_dir):
    """
    Combine all individual metric plots (for metrics in report_metrics) for a given model and mode
    into one composite image (stacked vertically). Returns the composite image path and the list of metrics included.
    """
    images = []
    metrics_present = []
    for metric in report_metrics:
        key = (model, mode, metric)
        if key in plot_files:
            img_path = plot_files[key]
            try:
                img = Image.open(img_path)
                images.append(img)
                metrics_present.append(metric)
            except Exception as e:
                print(f"Error loading image for {model}, {mode}, {metric}: {e}")
    if not images:
        return None, []
    widths, heights = zip(*(im.size for im in images))
    max_width = max(widths)
    total_height = sum(heights)
    composite = Image.new("RGB", (max_width, total_height), (255, 255, 255))
    y_offset = 0
    for im in images:
        composite.paste(im, (0, y_offset))
        y_offset += im.size[1]
    os.makedirs(composite_dir, exist_ok=True)
    composite_path = os.path.join(composite_dir, f"{model}_{mode}_composite.png".replace(" ", "_"))
    composite.save(composite_path)
    return composite_path, metrics_present


def create_composite_plot_grid(model, mode, plot_files, composite_dir, cell_default_size=(600, 400)):
    """
    Combine individual metric plots for a given model and mode into one composite image arranged in a 3x3 grid.
    For any metric not available, a blank image (of default size) is used.
    Since report_metrics contains 8 items, the bottom-right cell (9th cell) remains blank.

    Returns:
      composite_path: The file path of the saved composite image.
      metrics_used: The list of metric keys in the order of the grid.
    """
    # Use the defined order in report_metrics.
    metrics = report_metrics[:]  # Copy of the list.
    images = []
    for metric in metrics:
        key = (model, mode, metric)
        if key in plot_files:
            try:
                img = Image.open(plot_files[key])
                images.append(img)
            except Exception as e:
                print(f"Error loading image for {model}, {mode}, {metric}: {e}")
                blank = Image.new("RGB", cell_default_size, (255, 255, 255))
                images.append(blank)
        else:
            # Use a blank image for missing metric.
            blank = Image.new("RGB", cell_default_size, (255, 255, 255))
            images.append(blank)
    # We need exactly 9 cells; if we have only 8 images, append one blank.
    while len(images) < 9:
        blank = Image.new("RGB", cell_default_size, (255, 255, 255))
        images.append(blank)
    # If more than 9 (shouldn't happen), take only the first 9.
    images = images[:9]

    # Determine each cell's dimensions from the maximum image sizes.
    cell_width = max(img.width for img in images)
    cell_height = max(img.height for img in images)
    composite_width = 3 * cell_width
    composite_height = 3 * cell_height
    composite = Image.new("RGB", (composite_width, composite_height), (255, 255, 255))

    for i, img in enumerate(images):
        row = i // 3
        col = i % 3
        x = col * cell_width
        y = row * cell_height
        # Center the image in its cell.
        offset_x = (cell_width - img.width) // 2
        offset_y = (cell_height - img.height) // 2
        composite.paste(img, (x + offset_x, y + offset_y))

    os.makedirs(composite_dir, exist_ok=True)
    composite_path = os.path.join(composite_dir, f"{model}_{mode}_composite.png".replace(" ", "_"))
    composite.save(composite_path)
    return composite_path, metrics


# -----------------------------------------------------------------------------
# 8. Updated Markdown Report Generation (Using ##, ###, etc.)
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# 8. Updated Markdown Report Generation (Using ##, ###, etc.)
# -----------------------------------------------------------------------------
def generate_markdown_report(
    plot_files: dict,
    summary_tables: dict,
    pareto_images: dict,
    analyzer_stats: dict,
    composite_dir: str,
    output_md: str,
):
    """Generate a compact Markdown report.

    With the following sections:
    - An Overview section (## Overview) listing agents, models, and modes.
    - A Metrics Explanation section (## Metrics Explanation).
    - For each Model (### Model):
        - An Analyzer Overview (#### Analyzer Overview) with groups (##### Group Title).
        - For each Mode (#### Mode):
            - A Metric Plots section (##### Metric Plots) with an HTML table.
            - A Summary Table (##### Summary Table (Final Values)).
            - A Pareto Front Images section (##### Pareto Front Images) with an HTML table.
    """

    import os

    md_lines = []

    models = sorted({key[0] for key in plot_files.keys()})
    all_modes = sorted({mode for (m, mode, _) in plot_files.keys()})
    all_agents = set()
    for table in summary_tables.values():
        if "Agent" in table.columns:
            all_agents.update(table["Agent"].tolist())
    all_agents = sorted(all_agents)

    md_lines.append("## Overview\n")
    md_lines.append(
        "This report includes data for the following **agents**, **models**, and **modes**. "
        "Click on a model to jump to its section.\n"
    )

    md_lines.append("### Agents")
    for agent in all_agents:
        md_lines.append(f"- {agent}")
    md_lines.append("")

    md_lines.append("### Models")
    for model in models:
        anchor = model.lower().replace(" ", "-")
        md_lines.append(f"- [{model}](#{anchor})")
    md_lines.append("")

    md_lines.append("### Modes")
    for mode in all_modes:
        md_lines.append(f"- {mode}")
    md_lines.append("\n---\n")

    md_lines.append("## Metrics Explanation\n")
    md_lines.append(
        "Below is an explanation of the metrics used in this report. "
        "Note that one simulation (or 'Solution') corresponds to one step on the x-axis.\n"
    )
    md_lines.append("<ul>")
    for orig_metric, human_name in human_metric_names.items():
        explanation = metric_explanations[human_name]
        md_lines.append(f"<li><strong>{human_name}:</strong> {explanation}</li>")
    md_lines.append("</ul>\n")

    desired_groups = {
        "# Iterations",
        "# Solutions",
        "# Invalid Solutions Ratio",
        "Pareto Size",
        "Hyperarea Ratio",
        "Hausdorff",
        "Delta",
        "Purity",
        "Avg Cycle Time",
        "Best Cycle Time",
    }

    for model in models:
        anchor = model.lower().replace(" ", "-")
        md_lines.append(f"### {model}\n")

        if model in analyzer_stats:
            md_lines.append("#### Analyzer Overview\n")
            for group_title, header, rows in analyzer_stats[model]:
                if group_title.strip() not in desired_groups:
                    continue
                md_lines.append(f"##### {group_title}\n")
                md_lines.append(format_markdown_table(header, rows))
                md_lines.append("<br>\n")

        modes = sorted({mode for (m, mode, _) in plot_files.keys() if m == model})
        for mode in modes:
            md_lines.append(f"#### {mode}\n")

            # Composite Metric Plots Section (3x3 grid)
            md_lines.append("##### Metric Plots\n")
            composite_path, metrics_used = create_composite_plot_grid(model, mode, plot_files, composite_dir)
            if composite_path:
                relative_composite_path = os.path.relpath(composite_path, os.path.dirname(output_md))
                md_lines.append(f"![]({relative_composite_path})")
                md_lines.append("")
                md_lines.append("Individual charts:")
                for metric in metrics_used:
                    key = (model, mode, metric)
                    if key in plot_files:
                        relative_individual = os.path.relpath(plot_files[key], os.path.dirname(output_md))
                        human_name = human_metric_names.get(metric, metric)
                        md_lines.append(f"- [{human_name}]({relative_individual})")
            else:
                md_lines.append("No metric plots available.")

            md_lines.append("")
            md_lines.append("##### Summary Table (Final Values)\n")
            table_df = summary_tables.get((model, mode))
            if table_df is not None:
                table_df = table_df.copy()
                table_df.rename(
                    columns={k: human_metric_names.get(k, k) for k in table_df.columns if k != "Agent"},
                    inplace=True,
                )
                md_lines.append(table_df.to_markdown(index=False))
            else:
                md_lines.append("No summary available.\n")

            md_lines.append("##### Pareto Front Images\n")
            agents_for_pf = [
                agent for (m, mode_key, agent) in pareto_images.keys() if m == model and mode_key == mode
            ]
            if agents_for_pf:
                md_lines.append("<table><tr>")
                for agent in agents_for_pf:
                    md_lines.append(f"<th>{agent}</th>")
                md_lines.append("</tr><tr>")
                for agent in agents_for_pf:
                    key = (model, mode, agent)
                    image_path = pareto_images.get(key, "No image")
                    if image_path != "No image":
                        relative_image_path = os.path.relpath(image_path, os.path.dirname(output_md))
                        md_lines.append(
                            f"<td><img src='{relative_image_path}' alt='Pareto Front for {agent}' style='width:300px;height:200px;'/></td>"
                        )
                    else:
                        md_lines.append("<td>No image</td>")
                md_lines.append("</tr></table>")
            else:
                md_lines.append("No Pareto Front images available.\n")
            md_lines.append("\n---\n")
        md_lines.append("\n---\n")

    with open(output_md, "w") as f:
        f.write("\n".join(md_lines))


# -----------------------------------------------------------------------------
# 9. Main Routine (with progress prints)
# -----------------------------------------------------------------------------
def main():
    print("Loading event data...")
    root_dir = "events/"
    output_dir = "report_outputs"
    image_dir = os.path.join(output_dir, "report_images")
    plots_dir = os.path.join(output_dir, "report_plots")
    composite_dir = os.path.join(output_dir, "composite_plots")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(composite_dir, exist_ok=True)

    df = load_all_event_data(root_dir)
    if df.empty:
        print("No event data found. Check your root_dir!")
        return

    print("Defining color mapping for agents...")
    agents = sorted(df["Agent"].unique())
    cmap = plt.get_cmap("tab10")
    agent_colors = {agent: cmap(i % 10) for i, agent in enumerate(agents)}

    print("Generating plots...")
    plot_files = generate_plots(df, plots_dir, agent_colors)

    print("Generating summary tables...")
    summary_tables = generate_summary_tables(df)

    print("Saving Pareto Front images...")
    pareto_images = save_pareto_front_images(df, image_dir)

    print("Parsing analyzer report...")
    analyzer_file = "analyzer_report.ssv"  # Adjust path if needed.
    analyzer_stats = parse_analyzer_report(analyzer_file)

    print("Generating Markdown report...")
    output_md = os.path.join(output_dir, "report.md")
    generate_markdown_report(
        plot_files, summary_tables, pareto_images, analyzer_stats, composite_dir, output_md
    )
    print("Report generated:", output_md)


if __name__ == "__main__":
    main()
