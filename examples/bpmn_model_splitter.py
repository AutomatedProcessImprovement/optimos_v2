import os

from prosimos.simulation_properties_parser import parse_qbp_simulation_process


def main() -> None:
    """Split a BPMN model into BPMN and simod simulation model."""
    # Get the directory path for bpm_to_split
    bpmn_dir = "bpmn_to_split"

    # Ensure directory exists
    if not os.path.exists(bpmn_dir):
        print(f"Directory {bpmn_dir} does not exist")
        return

    # Process each .bpmn file
    for filename in os.listdir(bpmn_dir):
        if filename.endswith(".bpmn"):
            bpmn_path = os.path.join(bpmn_dir, filename)

            # Create output filename by replacing .bpmn with .json
            out_filename = filename.replace(".bpmn", ".json")
            out_path = os.path.join(bpmn_dir, out_filename)

            # Process the BPMN file
            parse_qbp_simulation_process(bpmn_path, out_path)
            print(f"Processed {filename} -> {out_filename}")


if __name__ == "__main__":
    main()
