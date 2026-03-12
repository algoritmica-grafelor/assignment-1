import importlib.util
import os
import sys
import traceback


def load_graph_class(path):
    """Loads the module from a file (even if the filename contains dashes) and returns the Graph class."""
    spec = importlib.util.spec_from_file_location("assignment_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "Graph"):
        return module.Graph
    raise ImportError("The Graph class was not found in the provided module.")


def run_tests():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "assignment-1.py")
    Graph = load_graph_class(path)

    def assert_eq(a, b, msg=""):
        if a != b:
            raise AssertionError(f"{msg}: {a} != {b}")

    g = Graph()

    # Test: add vertices
    g.add_vertex("A")
    g.add_vertex("B")
    g.add_vertex("C")
    assert_eq(g.get_v(), 3, "Number of vertices after insertion")

    # Test: add edges
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    assert_eq(g.get_e(), 2, "Number of edges after insertion")
    assert g.is_edge("A", "B"), "A->B should exist"
    assert not g.is_edge("C", "A"), "C->A should not exist"

    # Test: neighbors and inbound
    assert g.neighbors("A") == ["B"], f"Neighbors(A) expected ['B'], got {g.neighbors('A')}"
    assert g.neighbors("B") == ["C"], f"Neighbors(B) expected ['C'], got {g.neighbors('B')}"
    assert g.inbound_neighbors("B") == ["A"], f"Inbound(B) expected ['A'], got {g.inbound_neighbors('B')}"

    # Test: edge list
    edges = set(g.get_edges())
    assert edges == {("A", "B"), ("B", "C")}, f"Invalid get_edges() result: {edges}"

    # Test: remove edge
    g.remove_edge("A", "B")
    assert_eq(g.get_e(), 1, "Edge count after deletion")
    assert not g.is_edge("A", "B"), "A->B should be removed"

    # Test: remove vertex
    g.remove_vertex("B")
    assert_eq(g.get_v(), 2, "Vertex count after removal")

    # After removing B there should be no edges left
    assert g.get_edges() == [], f"Expected no edges, got {g.get_edges()}"

    # Display string output for inspection
    print("String output for graph:\n", str(g))

    print("All tests passed")


if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print("TESTS FAILED:", e)
        traceback.print_exc()
        sys.exit(1)
