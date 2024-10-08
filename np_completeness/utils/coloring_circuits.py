from typing import Hashable, TypeAlias, cast

from manim import *
from manim.typing import InternalPoint3D

from np_completeness.utils.circuit import Circuit
from np_completeness.utils.gate import NAND_TABLE, OR3_TABLE, Gate, LazyTruthTable
from np_completeness.utils.util_general import BASE00, CYAN, MAGENTA

Coloring: TypeAlias = dict[int, int]


def make_coloring_circuit(
    graph: Graph, coloring: Coloring, output_position: InternalPoint3D | None = None
) -> Circuit:
    if output_position is None:
        output_position = np.array([0, 0, 0])

    circuit = Circuit()
    n_colors = 3

    def get_degree(vertex: Hashable):
        edges = graph.edges.keys()
        return sum(1 for edge in edges if vertex in edge)

    for vertex_name in graph.vertices:
        position = graph.vertices[vertex_name].get_center()
        circuit.add_gate(
            f"vertex_{vertex_name}_or3", Gate(OR3_TABLE, position, visual_type="or")
        )
        try:
            color = coloring[cast(int, vertex_name)]
        except KeyError as e:
            raise KeyError(f"No color found in the coloring for {vertex_name}") from e

        assert color in range(n_colors)

        for i in range(n_colors):
            offset = rotate_vector(RIGHT * 0.7, angle=2 * PI / n_colors * i + 0.3)
            n_outputs = 3 + get_degree(vertex_name)
            gate = Gate(
                truth_table={(): tuple([color == i for _ in range(n_outputs)])},
                position=position + offset,
                visual_type="constant",
            )
            circuit.add_gate(f"vertex_{vertex_name}_value_{i}", gate)
            circuit.add_wire(
                f"vertex_{vertex_name}_value_{i}", f"vertex_{vertex_name}_or3"
            )

        assert n_colors == 3, "This part will need rewriting if we change n_colors"
        for i in range(n_colors):
            name_1 = f"vertex_{vertex_name}_value_{i}"
            name_2 = f"vertex_{vertex_name}_value_{(i+1)%n_colors}"

            and_gate = circuit.add_gate(
                f"vertex_{vertex_name}_nand_{i}",
                Gate(
                    truth_table=NAND_TABLE,
                    position=(circuit.position_of(name_1) + circuit.position_of(name_2))
                    / 2,
                    visual_type="nand",
                ),
            )
            circuit.add_wire(name_1, and_gate)
            circuit.add_wire(name_2, and_gate)

    for vertex_name_1, vertex_name_2 in graph.edges:
        for i in range(n_colors):
            name_1 = f"vertex_{vertex_name_1}_value_{i}"
            name_2 = f"vertex_{vertex_name_2}_value_{i}"

            nand_gate = circuit.add_gate(
                f"edge_{vertex_name_1}_{vertex_name_2}_nand_{i}",
                Gate(
                    truth_table=NAND_TABLE,
                    position=(circuit.position_of(name_1) + circuit.position_of(name_2))
                    / 2,
                    visual_type="nand",
                ),
            )
            circuit.add_wire(name_1, nand_gate)
            circuit.add_wire(name_2, nand_gate)

    gates_to_connect = []
    for gate in circuit.gates:
        n_outputs = len([wire for wire in circuit.wires if wire[0] == gate])
        if n_outputs == 0:
            gates_to_connect.append(gate)

    big_and_gate = circuit.add_gate(
        "big_and",
        Gate(
            LazyTruthTable(
                n_inputs=len(gates_to_connect),
                n_outputs=1,
                fn=lambda inputs: (all(inputs),),
            ),
            output_position,
            visual_type="and",
        ),
    )
    for gate in gates_to_connect:
        circuit.add_wire(gate, big_and_gate)

    output_gate = circuit.add_gate(
        "output",
        Gate.make_knot(
            circuit.gates[big_and_gate].position + DOWN * 0.5, n_inputs=1, n_outputs=0
        ),
    )
    circuit.add_wire(big_and_gate, output_gate)

    return circuit


GRAPH_COLORS = [MAGENTA, CYAN, ORANGE]


def get_example_graph(*, good_coloring: bool, colored=True) -> tuple[Graph, Coloring]:
    """Create an example graph.

    It's a function and not a constant so that we don't modify it accidentally.
    """
    graph = Graph(
        vertices=[1, 2, 3, 4, 5, 6],
        edges=[(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1), (2, 5), (2, 6)],
        layout="kamada_kawai",
        layout_scale=4,
        vertex_config={"fill_color": BASE00, "radius": 0.2},
        edge_config={"color": BASE00, "stroke_width": 10},
    )

    coloring = {1: 0, 2: 1, 3: 2, 4: 0, 5: 0, 6: 2}

    if good_coloring:
        coloring[4] = 1

    assert set(coloring.keys()) == set(graph.vertices.keys())

    if colored:
        for vertex in graph.vertices:
            graph.vertices[vertex].fill_color = GRAPH_COLORS[coloring[vertex]]  # type: ignore

    return graph, coloring
