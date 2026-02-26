# Test harness pentru `assignment-1.py`

import importlib.util
import os
import sys
import traceback


def load_graph_class(path):
    """Încarcă modulul dintr-un fișier (poate conține cratime în nume) și returnează clasa Graph."""
    spec = importlib.util.spec_from_file_location("assignment_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "Graph"):
        return module.Graph
    raise ImportError("Clasa Graph nu a fost gasita in modulul furnizat.")


def run_tests():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "assignment-1.py")
    Graph = load_graph_class(path)

    def assert_eq(a, b, msg=""):
        if a != b:
            raise AssertionError(f"{msg}: {a} != {b}")

    g = Graph()

    # Test: adaugare noduri
    g.add_vertex("A")
    g.add_vertex("B")
    g.add_vertex("C")
    assert_eq(g.get_v(), 3, "Numar noduri dupa adaugare")

    # Test: adaugare muchii
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    assert_eq(g.get_e(), 2, "Numar muchii dupa adaugare")
    assert g.is_edge("A", "B"), "A->B ar trebui sa existe"
    assert not g.is_edge("C", "A"), "C->A nu ar trebui sa existe"

    # Test: vecini si inbound
    assert g.neighbors("A") == ["B"], f"Neighbors(A) asteptat ['B'], obtinut {g.neighbors('A')}"
    assert g.neighbors("B") == ["C"], f"Neighbors(B) asteptat ['C'], obtinut {g.neighbors('B')}"
    assert g.inbound_neighbors("B") == ["A"], f"Inbound(B) asteptat ['A'], obtinut {g.inbound_neighbors('B')}"

    # Test: lista muchii
    edges = set(g.get_edges())
    assert edges == {("A", "B"), ("B", "C")}, f"Get_edges() invalide: {edges}"

    # Test: stergere muchie
    g.remove_edge("A", "B")
    assert_eq(g.get_e(), 1, "Numar muchii dupa stergere muchie")
    assert not g.is_edge("A", "B"), "A->B ar trebui sa fie stearsa"

    # Test: stergere nod
    g.remove_vertex("B")
    assert_eq(g.get_v(), 2, "Numar noduri dupa stergere nod")

    # Dupa stergerea lui B, nu ar trebui sa existe muchii
    assert g.get_edges() == [], f"Asteptat nici o muchie, obtinut {g.get_edges()}"

    # Afisare pentru inspectie
    print("String output pentru graf:\n", str(g))

    print("All tests passed")


if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print("TESTS FAILED:", e)
        traceback.print_exc()
        sys.exit(1)
