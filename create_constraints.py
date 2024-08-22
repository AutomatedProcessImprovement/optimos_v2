from tests.fixtures.constraints_generator import ConstraintsGenerator


def main() -> None:
    """Generate a basic set of constraints from a BPMN model."""
    with open("examples/demo_legacy/model.bpmn") as f:
        bpmn_str = f.read()
        generator = ConstraintsGenerator(bpmn_str)
        constraints = generator.generate()

    with open("examples/demo_legacy/batching_constraints.json", "w") as f:
        f.write(constraints.to_json())

    print("Constraints generated successfully!")


if __name__ == "__main__":
    main()
