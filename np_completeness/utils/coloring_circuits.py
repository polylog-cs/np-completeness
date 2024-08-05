from typing import Hashable, TypeAlias, cast

from manim import *

from np_completeness.utils.circuit import NAND_TABLE, OR3_TABLE, Circuit
from np_completeness.utils.gate import Gate
from np_completeness.utils.util_general import BASE00, CYAN, MAGENTA

Coloring: TypeAlias = dict[int, int]


def make_coloring_circuit(graph: Graph, coloring: Coloring) -> Circuit:
    circuit = Circuit()
    n_colors = 3

    def get_degree(vertex: Hashable):
        edges = graph.edges.keys()
        return sum(1 for edge in edges if vertex in edge)

    for vertex_name in graph.vertices:
        position = graph.vertices[vertex_name].get_center()
        circuit.add_gate(
            f"{vertex_name}_or3", Gate(OR3_TABLE, position, visual_type="or")
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
            circuit.add_gate(f"{vertex_name}_value_{i}", gate)
            circuit.add_wire(f"{vertex_name}_value_{i}", f"{vertex_name}_or3")

        assert n_colors == 3, "This part will need rewriting if we change n_colors"
        for i in range(n_colors):
            name_1 = f"{vertex_name}_value_{i}"
            name_2 = f"{vertex_name}_value_{(i+1)%n_colors}"

            and_gate = circuit.add_gate(
                f"{vertex_name}_nand_{i}",
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
            name_1 = f"{vertex_name_1}_value_{i}"
            name_2 = f"{vertex_name_2}_value_{i}"

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

    return circuit


def get_example_graph(*, good_coloring: bool) -> tuple[Graph, Coloring]:
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
    if good_coloring:
        raise NotImplementedError

    coloring = {1: 0, 2: 1, 3: 2, 4: 0, 5: 0, 6: 2}

    colors = [MAGENTA, CYAN, ORANGE]

    assert set(coloring.keys()) == set(graph.vertices.keys())

    for vertex in graph.vertices:
        graph.vertices[vertex].fill_color = colors[coloring[vertex]]  # type: ignore

    return graph, coloring
