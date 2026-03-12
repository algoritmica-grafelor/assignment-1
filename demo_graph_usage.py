import importlib.util
import pathlib
from contextlib import suppress


def load_graph_class():
    module_path = pathlib.Path(__file__).with_name("assignment-1.py")
    spec = importlib.util.spec_from_file_location("assignment_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Graph


def print_graph_state(title, graph):
    print(f"\n=== {title} ===")
    print(f"Vertices ({graph.get_v()}): {graph.get_vertices()}")
    print(f"Edges ({graph.get_e()}): {graph.get_edges()}")
    print(str(graph))


def demo_graph_operations():
    Graph = load_graph_class()
    g = Graph()

    print_graph_state("Fresh graph", g)

    # Add vertices
    for label in ("A", "B", "C"):
        g.add_vertex(label)
        print_graph_state(f"After add_vertex('{label}')", g)

    # Trigger duplicate vertex error
    try:
        g.add_vertex("A")
    except ValueError as exc:
        print(f"\nDuplicate vertex error: {exc}")

    # Add edges
    g.add_edge("A", "B")
    print_graph_state("After add_edge('A', 'B')", g)

    g.add_edge("B", "C")
    print_graph_state("After add_edge('B', 'C')", g)

    # Query edges
    print(f"\nIs there an edge A->B? {g.is_edge('A', 'B')}")
    print(f"Is there an edge C->A? {g.is_edge('C', 'A')}")

    # Neighbor queries
    print(f"Neighbors of B: {g.neighbors('B')}")
    print(f"Inbound neighbors of B: {g.inbound_neighbors('B')}")

    # Remove edge
    g.remove_edge("A", "B")
    print_graph_state("After remove_edge('A', 'B')", g)

    # Attempt to remove non-existent edge
    with suppress(ValueError):
        g.remove_edge("A", "B")  # Should silently do nothing as per implementation
    print_graph_state("After redundant remove_edge('A', 'B')", g)

    # Remove vertex
    g.remove_vertex("B")
    print_graph_state("After remove_vertex('B')", g)

    # Attempt to remove missing vertex
    try:
        g.remove_vertex("Z")
    except ValueError as exc:
        print(f"\nMissing vertex error: {exc}")

    # Final state
    print_graph_state("Final graph", g)


if __name__ == "__main__":
    demo_graph_operations()

