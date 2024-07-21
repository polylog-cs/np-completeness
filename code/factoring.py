from pysat.formula import CNF
from pysat.solvers import Glucose3

DEBUG = False  # Set this to True for verbose output


class Wire:
    counter = 1

    def __init__(self):
        self.id = Wire.counter
        Wire.counter += 1


def print_debug(message):
    if DEBUG:
        print(message)


def create_circuit(k):
    a = [Wire() for _ in range(k)]
    b = [Wire() for _ in range(k)]
    intermediate = [[Wire() for _ in range(k)] for _ in range(k)]
    sum_wires = [[Wire() for _ in range(2 * k)] for _ in range(k - 1)]
    carry_wires = [[Wire() for _ in range(2 * k)] for _ in range(k - 1)]
    output = [Wire() for _ in range(2 * k)]
    true_wire = Wire()
    false_wire = Wire()
    return {
        "inputs": (a, b),
        "intermediate": intermediate,
        "sum_wires": sum_wires,
        "carry_wires": carry_wires,
        "output": output,
        "true": true_wire,
        "false": false_wire,
    }


def add_clause(cnf, literals, description):
    cnf.append(literals)
    print_debug(f"{description}: {literals}")


def add_gate(cnf, output, inputs, operation):
    if operation == "AND":
        add_clause(
            cnf,
            [-x.id for x in inputs] + [output.id],
            "AND gate: if all inputs are true, output has to be true",
        )
        for x in inputs:
            add_clause(
                cnf,
                [x.id, -output.id],
                "AND gate: if any input is false, output must be false",
            )
    elif operation == "OR":
        add_clause(
            cnf,
            [x.id for x in inputs] + [-output.id],
            "OR gate: if all inputs are false, output has to be false",
        )
        for x in inputs:
            add_clause(
                cnf,
                [-x.id, output.id],
                "OR gate: if any input is true, output must be true",
            )
    elif operation == "XOR":
        if len(inputs) == 2:
            x, y = inputs[0].id, inputs[1].id
            z = output.id
            add_clause(
                cnf,
                [x, y, -z],
                "XOR gate (2 inputs): if both inputs are false, output is false",
            )
            add_clause(
                cnf,
                [x, -y, z],
                "XOR gate (2 inputs): if inputs are different (01), output is true",
            )
            add_clause(
                cnf,
                [-x, y, z],
                "XOR gate (2 inputs): if inputs are different (10), output is true",
            )
            add_clause(
                cnf,
                [-x, -y, -z],
                "XOR gate (2 inputs): if both inputs are true, output is false",
            )
        elif len(inputs) == 3:
            x, y, w = inputs[0].id, inputs[1].id, inputs[2].id
            z = output.id
            add_clause(
                cnf,
                [x, y, w, -z],
                "XOR gate (3 inputs): if all inputs are false, output is false",
            )
            add_clause(
                cnf,
                [x, y, -w, z],
                "XOR gate (3 inputs): if one input is true (001), output is true",
            )
            add_clause(
                cnf,
                [x, -y, w, z],
                "XOR gate (3 inputs): if one input is true (010), output is true",
            )
            add_clause(
                cnf,
                [-x, y, w, z],
                "XOR gate (3 inputs): if one input is true (100), output is true",
            )
            add_clause(
                cnf,
                [x, -y, -w, -z],
                "XOR gate (3 inputs): if two inputs are true (011), output is false",
            )
            add_clause(
                cnf,
                [-x, y, -w, -z],
                "XOR gate (3 inputs): if two inputs are true (101), output is false",
            )
            add_clause(
                cnf,
                [-x, -y, w, -z],
                "XOR gate (3 inputs): if two inputs are true (110), output is false",
            )
            add_clause(
                cnf,
                [-x, -y, -w, z],
                "XOR gate (3 inputs): if all inputs are true, output is true",
            )
        else:
            raise ValueError("XOR gate currently supports only 2 or 3 inputs")
    elif operation == "MAJ":
        if len(inputs) != 3:
            raise ValueError("MAJ gate requires exactly 3 inputs")
        x, y, w = inputs[0].id, inputs[1].id, inputs[2].id
        z = output.id
        add_clause(cnf, [-x, -y, z], "MAJ gate: if two inputs are true, output is true")
        add_clause(cnf, [-x, -w, z], "MAJ gate: if two inputs are true, output is true")
        add_clause(cnf, [-y, -w, z], "MAJ gate: if two inputs are true, output is true")
        add_clause(
            cnf, [x, y, -z], "MAJ gate: if two inputs are false, output is false"
        )
        add_clause(
            cnf, [x, w, -z], "MAJ gate: if two inputs are false, output is false"
        )
        add_clause(
            cnf, [y, w, -z], "MAJ gate: if two inputs are false, output is false"
        )


def circuit_to_cnf(circuit, n):
    cnf = CNF()
    k = len(circuit["inputs"][0])

    add_clause(cnf, [circuit["true"].id], "Setting true wire to true")
    add_clause(cnf, [-circuit["false"].id], "Setting false wire to false")

    # AND gates for intermediate results
    for i in range(k):
        for j in range(k):
            add_gate(
                cnf,
                circuit["intermediate"][i][j],
                [circuit["inputs"][0][i], circuit["inputs"][1][j]],
                "AND",
            )

    # Addition logic (XOR and carry)
    for i in range(k - 1):
        for j in range(2 * k):
            x = (
                circuit["intermediate"][0][j]
                if i == 0 and j < k
                else circuit["sum_wires"][i - 1][j]
                if i > 0
                else circuit["false"]
            )
            y = (
                circuit["intermediate"][i + 1][j - (i + 1)]
                if j >= (i + 1) and j < k + (i + 1)
                else circuit["false"]
            )
            c = circuit["false"] if j == 0 else circuit["carry_wires"][i][j - 1]

            add_gate(cnf, circuit["sum_wires"][i][j], [x, y, c], "XOR")
            add_gate(cnf, circuit["carry_wires"][i][j], [x, y, c], "MAJ")

    # Define the output wires
    print_debug("\nConnecting sum wires to output:")
    for i in range(2 * k):
        add_gate(cnf, circuit["output"][i], [circuit["sum_wires"][k - 2][i]], "AND")

    # Require that the input cannot be 1
    add_clause(
        cnf,
        [x.id for x in circuit["inputs"][0][1:]] + [-circuit["inputs"][0][0].id],
        "a != 1",
    )
    add_clause(
        cnf,
        [x.id for x in circuit["inputs"][1][1:]] + [-circuit["inputs"][1][0].id],
        "b != 1",
    )

    print_debug("\nSetting output to n:")
    for i in range(2 * k):
        clause = (
            [circuit["output"][i].id] if (n >> i) & 1 else [-circuit["output"][i].id]
        )
        add_clause(cnf, clause, f"Setting output bit {i}")

    return cnf


def factor(n):
    k = n.bit_length()
    print(f"Bit length of {n}: {k}")
    circuit = create_circuit(k)
    cnf = circuit_to_cnf(circuit, n)

    print(f"\nNumber of clauses: {len(cnf.clauses)}")
    print(f"Number of variables: {Wire.counter - 1}")

    solver = Glucose3()
    for clause in cnf.clauses:
        solver.add_clause([lit for lit in clause if lit != 0])

    print("\nSolving SAT problem...")
    if solver.solve():
        print("SAT problem solved successfully")
        model = solver.get_model()

        if DEBUG:
            for i, val in enumerate(model, 1):
                print(f"Variable {i}: {val}")

        a = sum(
            1 << i
            for i in range(k)
            if circuit["inputs"][0][i].id <= len(model)
            and model[circuit["inputs"][0][i].id - 1] > 0
        )
        b = sum(
            1 << i
            for i in range(k)
            if circuit["inputs"][1][i].id <= len(model)
            and model[circuit["inputs"][1][i].id - 1] > 0
        )
        print(f"Raw factors: a = {a}, b = {b}")
        return a, b
    else:
        print("SAT solver couldn't find a solution")
        return None


def main():
    instances = [
        283 * 293,
        1663 * 1667,
        5449 * 5471,
        7907 * 7919,
        33391 * 35317,
        106033 * 108301,
    ]

    for n in instances:  # range(2, 100):
        try:
            print(f"\nAttempting to factor {n}")
            factors = factor(n)
            if factors:
                a, b = factors
                print(f"Factors of {n}: {a} and {b}")
                print(f"Verification: {a} * {b} = {a * b}")
            else:
                print(f"No factors found for {n}")
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback

            traceback.print_exc()
        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()
