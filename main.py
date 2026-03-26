import importlib.util
import os
import sys
import tempfile
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

    def assert_raises(callable_obj, msg=""):
        try:
            callable_obj()
        except Exception:
            return
        raise AssertionError(msg or "Expected exception was not raised")

    def print_graph_from_file(graph_obj, file_name):
        # Print a full, human-readable snapshot of what was parsed from each file.
        print(f"\n===== {file_name} =====")
        print(graph_obj)
        print("Vertices:", graph_obj.get_vertices())
        print("Edges:", graph_obj.get_edges())
        print(f"Counts: V={graph_obj.get_v()}, E={graph_obj.get_e()}")

    def iterator_maps_to_labels(iterator_obj):
        # Convert internal iterator maps from index keys to label keys for readable debug output.
        idx_to_label = iterator_obj._graph._index_to_label

        parent_map = {}
        for child_idx, parent_idx in iterator_obj._parent_map.items():
            child_label = idx_to_label[child_idx]
            parent_label = None if parent_idx is None else idx_to_label[parent_idx]
            parent_map[child_label] = parent_label

        distance_map = {idx_to_label[idx]: dist for idx, dist in iterator_obj._distance_map.items()}
        path_map = {idx_to_label[idx]: path for idx, path in iterator_obj._path_map.items()}
        return parent_map, distance_map, path_map

    def print_full_dfs_debug(graph_obj, graph_name):
        # Run DFS on every component so disconnected graphs are fully covered.
        print(f"\nDFS iterator debug for {graph_name}:")
        visited = set()
        full_order = []
        merged_parent_map = {}
        merged_distance_map = {}
        merged_path_map = {}

        for start_vertex in graph_obj.get_vertices():
            if start_vertex in visited:
                continue

            dfs_it = graph_obj.DFS_iter(start_vertex)
            print(f"  Component start: {start_vertex}")
            while dfs_it.valid():
                current = dfs_it.get_current()
                distance, path = dfs_it.get_path_length()
                print(f"    current={current}, distance={distance}, path={path}")
                visited.add(current)
                full_order.append(current)
                dfs_it.next()

            parent_map, distance_map, path_map = iterator_maps_to_labels(dfs_it)
            merged_parent_map.update(parent_map)
            merged_distance_map.update(distance_map)
            merged_path_map.update(path_map)

        print("  Full DFS order:", full_order)
        print("  Parent map:", merged_parent_map)
        print("  Distance map:", merged_distance_map)
        print("  Path map:", merged_path_map)

    # --- Directed, unweighted basic operations ---
    g = Graph()
    for vertex in ("A", "B", "C"):
        g.add_vertex(vertex)
    assert_eq(g.get_v(), 3, "Vertex count after insertion")

    g.add_edge("A", "B")
    g.add_edge("B", "C")
    assert_eq(g.get_e(), 2, "Edge count after insertion")
    assert g.is_edge("A", "B"), "A->B should exist"
    assert not g.is_edge("C", "A"), "C->A should not exist"
    assert g.neighbors("A") == ["B"], "Neighbors(A) mismatch"
    assert g.inbound_neighbors("B") == ["A"], "Inbound(B) mismatch"

    g.remove_edge("A", "B")
    assert_eq(g.get_e(), 1, "Edge count after removal")
    assert not g.is_edge("A", "B"), "A->B should be removed"

    g.remove_vertex("B")
    assert_eq(g.get_v(), 2, "Vertex count after removing B")
    assert_eq(g.get_edges(), [], "No edges should remain")

    # --- Undirected behavior and symmetry ---
    ug = Graph(directed=False)
    for vertex in ("1", "2", "3"):
        ug.add_vertex(vertex)
    ug.add_edge("1", "2")
    assert ug.is_edge("1", "2") and ug.is_edge("2", "1"), "Undirected edge must be symmetric"
    assert_eq(sorted(ug.neighbors("1")), ["2"], "Neighbors(1) mismatch")
    assert_eq(sorted(ug.inbound_neighbors("1")), ["2"], "Inbound and outbound must match")

    # --- Weighted behavior ---
    wg = Graph(directed=True, weighted=True)
    for vertex in ("X", "Y"):
        wg.add_vertex(vertex)
    wg.add_edge("X", "Y", 3.5)
    assert_eq(wg.get_weight("X", "Y"), 3.5, "Initial edge weight mismatch")
    wg.set_weight("X", "Y", -2)
    assert_eq(wg.get_weight("X", "Y"), -2, "Updated edge weight mismatch")
    wg.remove_edge("X", "Y")
    assert_raises(lambda: wg.get_weight("X", "Y"), "Weight lookup should fail after edge removal")

    # --- Mode switches: directed <-> undirected ---
    mode_g = Graph(directed=True)
    for vertex in ("A", "B", "C"):
        mode_g.add_vertex(vertex)
    mode_g.add_edge("A", "B")
    mode_g.change_if_directed(False)
    assert mode_g.is_edge("A", "B") and mode_g.is_edge("B", "A"), "Directed->undirected should merge edges"
    mode_g.change_if_directed(True)
    assert mode_g.is_edge("A", "B") and mode_g.is_edge("B", "A"), "Undirected->directed should duplicate both directions"

    # --- Mode switches: weighted <-> unweighted ---
    mode_w = Graph(directed=False, weighted=False)
    mode_w.add_vertex("P")
    mode_w.add_vertex("Q")
    mode_w.add_edge("P", "Q")
    mode_w.change_if_weighted(True)
    assert_eq(mode_w.get_weight("P", "Q"), 0, "Default weight should become 0 when enabling weighted mode")
    mode_w.set_weight("P", "Q", 9)
    mode_w.change_if_weighted(False)
    assert_raises(lambda: mode_w.get_weight("P", "Q"), "Weight lookup should fail when graph becomes unweighted")

    # --- BFS and DFS iterators + bonus path ---
    it_g = Graph(directed=True)
    for vertex in ("A", "B", "C", "D"):
        it_g.add_vertex(vertex)
    it_g.add_edge("A", "B")
    it_g.add_edge("A", "C")
    it_g.add_edge("B", "D")

    bfs = it_g.BFS_iter("A")
    bfs_order = []
    bfs_paths = {}
    while bfs.valid():
        current = bfs.get_current()
        bfs_order.append(current)
        bfs_paths[current] = bfs.get_path_length()
        bfs.next()
    assert_eq(bfs_order, ["A", "B", "C", "D"], "BFS order mismatch")
    assert_eq(bfs_paths["D"], (2, ["A", "B", "D"]), "BFS path info for D mismatch")
    assert_raises(lambda: bfs.get_current(), "BFS get_current should fail when iterator is invalid")
    assert_raises(lambda: bfs.next(), "BFS next should fail when iterator is invalid")

    dfs = it_g.DFS_iter("A")
    dfs_order = []
    dfs_paths = {}
    while dfs.valid():
        current = dfs.get_current()
        dfs_order.append(current)
        dfs_paths[current] = dfs.get_path_length()
        dfs.next()
    dfs_parent_map, dfs_distance_map, dfs_path_map = iterator_maps_to_labels(dfs)
    print("\nDFS iterator debug for in-memory test graph:")
    print("  DFS order:", dfs_order)
    print("  Parent map:", dfs_parent_map)
    print("  Distance map:", dfs_distance_map)
    print("  Path map:", dfs_path_map)
    assert_eq(dfs_order, ["A", "B", "D", "C"], "DFS order mismatch")
    assert_eq(dfs_paths["D"], (2, ["A", "B", "D"]), "DFS path info for D mismatch")

    # --- File loading using provided graph files ---
    g1 = Graph.create_from_file(os.path.join(base, "Graph1.txt"))
    print_graph_from_file(g1, "Graph1.txt")
    print_full_dfs_debug(g1, "Graph1.txt")
    assert_eq(g1.get_e(), 8, "Graph1 edge count mismatch")
    assert str(g1).splitlines()[0] == "undirected weighted", "Graph1 header mismatch"
    assert_eq(g1.get_weight("1", "3"), 5.0, "Graph1 weight mismatch")

    g2 = Graph.create_from_file(os.path.join(base, "Graph2.txt"))
    print_graph_from_file(g2, "Graph2.txt")
    print_full_dfs_debug(g2, "Graph2.txt")
    assert_eq(g2.get_e(), 6, "Graph2 edge count mismatch")
    assert str(g2).splitlines()[0] == "undirected unweighted", "Graph2 header mismatch"

    g3 = Graph.create_from_file(os.path.join(base, "Graph3.txt"))
    print_graph_from_file(g3, "Graph3.txt")
    print_full_dfs_debug(g3, "Graph3.txt")
    assert_eq(g3.get_e(), 9, "Graph3 edge count mismatch")
    assert str(g3).splitlines()[0] == "directed unweighted", "Graph3 header mismatch"
    assert g3.is_edge("A", "B") and not g3.is_edge("B", "A"), "Graph3 directed edge semantics mismatch"

    g4 = Graph.create_from_file(os.path.join(base, "Graph4.txt"))
    print_graph_from_file(g4, "Graph4.txt")
    print_full_dfs_debug(g4, "Graph4.txt")
    assert_eq(g4.get_e(), 8, "Graph4 edge count mismatch")
    assert str(g4).splitlines()[0] == "directed weighted", "Graph4 header mismatch"
    assert_eq(g4.get_weight("A", "F"), -2.0, "Graph4 weight mismatch")

    # --- File loading: blank line handling ---
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8") as tmp:
        tmp.write("\n\ndirected weighted\n\nA\n\nA B 2\n\n")
        tmp_path = tmp.name
    try:
        gb = Graph.create_from_file(tmp_path)
        assert_eq(gb.get_v(), 2, "Blank-line file vertex count mismatch")
        assert_eq(gb.get_e(), 1, "Blank-line file edge count mismatch")
        assert_eq(gb.get_weight("A", "B"), 2.0, "Blank-line file weight mismatch")
    finally:
        os.remove(tmp_path)

    print("All tests passed")


if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print("TESTS FAILED:", e)
        traceback.print_exc()
        sys.exit(1)
