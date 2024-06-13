from tests.fixtures.constraints_generator import ConstraintsGenerator


def main():
    with open("examples/purchase.bpmn") as f:
        bpmn_str = f.read()
        generator = ConstraintsGenerator(bpmn_str)
        constraints = generator.generate()

    with open("examples/purchase_constraints.json", "w") as f:
        f.write(constraints.to_json())

    print("Constraints generated successfully!")


if __name__ == "__main__":
    main()
