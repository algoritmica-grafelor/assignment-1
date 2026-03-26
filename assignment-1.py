from collections import deque


class BFSIterator:
    def __init__(self, graph, start_vertex):
        self._graph = graph
        self._start_vertex = start_vertex
        # Frontier for BFS order.
        self._queue = deque()
        self._visited = set()
        # Parent and cached path info for O(1) path query at current node.
        self._parent_map = {}
        self._distance_map = {}
        self._path_map = {}
        self._current_idx = None
        self.first()

    def first(self):
        if self._start_vertex not in self._graph._dict_labels:
            raise ValueError("Error: Start vertex does not exist.")

        start_idx = self._graph._dict_labels[self._start_vertex]
        self._queue = deque([start_idx])
        self._visited = {start_idx}
        self._parent_map = {start_idx: None}
        self._distance_map = {start_idx: 0}
        self._path_map = {start_idx: [self._start_vertex]}
        self._current_idx = None
        self._advance()

    def get_current(self):
        if not self.valid():
            raise ValueError("Error: Iterator is not valid.")
        return self._graph._index_to_label[self._current_idx]

    def next(self):
        if not self.valid():
            raise ValueError("Error: Iterator is not valid.")
        self._advance()

    def valid(self):
        return self._current_idx is not None

    def get_path_length(self):
        if not self.valid():
            raise ValueError("Error: Iterator is not valid.")
        return self._distance_map[self._current_idx], self._path_map[self._current_idx]

    def _advance(self):
        if not self._queue:
            self._current_idx = None
            return

        # Pop next node in BFS order, then discover its unseen neighbors.
        self._current_idx = self._queue.popleft()
        current_label = self._graph._index_to_label[self._current_idx]
        for neighbor in self._graph.neighbors(current_label):
            neighbor_idx = self._graph._dict_labels[neighbor]
            if neighbor_idx not in self._visited:
                self._visited.add(neighbor_idx)
                self._queue.append(neighbor_idx)
                self._parent_map[neighbor_idx] = self._current_idx
                self._distance_map[neighbor_idx] = self._distance_map[self._current_idx] + 1
                self._path_map[neighbor_idx] = self._path_map[self._current_idx] + [neighbor]


class DFSIterator:
    def __init__(self, graph, start_vertex):
        self._graph = graph
        self._start_vertex = start_vertex
        # Explicit stack for iterative DFS.
        self._stack = []
        self._visited = set()
        # Parent and cached path info for O(1) path query at current node.
        self._parent_map = {}
        self._distance_map = {}
        self._path_map = {}
        self._current_idx = None
        self.first()

    def first(self):
        if self._start_vertex not in self._graph._dict_labels:
            raise ValueError("Error: Start vertex does not exist.")

        start_idx = self._graph._dict_labels[self._start_vertex]
        self._stack = [start_idx]
        self._visited = {start_idx}
        self._parent_map = {start_idx: None}
        self._distance_map = {start_idx: 0}
        self._path_map = {start_idx: [self._start_vertex]}
        self._current_idx = None
        self._advance()

    def get_current(self):
        if not self.valid():
            raise ValueError("Error: Iterator is not valid.")
        return self._graph._index_to_label[self._current_idx]

    def next(self):
        if not self.valid():
            raise ValueError("Error: Iterator is not valid.")
        self._advance()

    def valid(self):
        return self._current_idx is not None

    def get_path_length(self):
        if not self.valid():
            raise ValueError("Error: Iterator is not valid.")
        return self._distance_map[self._current_idx], self._path_map[self._current_idx]

    def _advance(self):
        if not self._stack:
            self._current_idx = None
            return

        # Pop next node in DFS order, then push unseen neighbors.
        self._current_idx = self._stack.pop()
        current_label = self._graph._index_to_label[self._current_idx]
        neighbors = self._graph.neighbors(current_label)

        # Reverse push keeps neighbor exploration in natural adjacency order.
        for neighbor in reversed(neighbors):
            neighbor_idx = self._graph._dict_labels[neighbor]
            if neighbor_idx not in self._visited:
                self._visited.add(neighbor_idx)
                self._stack.append(neighbor_idx)
                self._parent_map[neighbor_idx] = self._current_idx
                self._distance_map[neighbor_idx] = self._distance_map[self._current_idx] + 1
                self._path_map[neighbor_idx] = self._path_map[self._current_idx] + [neighbor]


class Graph:
    def __init__(self, directed=True, weighted=False):
        """
        Creates an empty graph.
        Complexity: O(1)
        """
        self._directed = directed
        self._weighted = weighted
        self._matrix = []  # Adjacency matrix
        self._weights = {}  # Map: (start_index, end_index) -> edge weight
        self._dict_labels = {}  # Map: node_name -> matrix_index (example: {A:0, B:1})
        self._index_to_label = []  # Map: matrix_index -> node_name
        self._nr_edges = 0

    def add_vertex(self, vertex):
        """
        Adds a new vertex. Raises an error if it already exists.
        Complexity: O(n) due to row/column expansion, where n is the number of vertices.
        """
        if vertex in self._dict_labels:
            raise ValueError(f"Error: Vertex {vertex} already exists.")

        new_index = len(self._index_to_label)
        self._dict_labels[vertex] = new_index
        self._index_to_label.append(vertex)

        # Append a new column (0 to each row)
        for row in self._matrix:
            row.append(0)

        # Append a new zero-filled row for the new vertex
        self._matrix.append([0] * (new_index + 1))

    def _recompute_edge_count(self):
        """Recompute the number of edges according to the current graph mode."""
        n = len(self._matrix)

        if self._directed:
            self._nr_edges = sum(sum(row) for row in self._matrix)
            return

        edges = 0
        for i in range(n):
            if self._matrix[i][i] == 1:
                edges += 1
            for j in range(i + 1, n):
                if self._matrix[i][j] == 1 or self._matrix[j][i] == 1:
                    edges += 1
        self._nr_edges = edges

    def add_edge(self, start_v, end_v, weight=0.0):
        """
        Adds an edge. If it already exists, do nothing.
        Complexity: O(1)
        """
        if start_v not in self._dict_labels or end_v not in self._dict_labels:
            raise ValueError("Error: One or both vertices do not exist.")

        i, j = self._dict_labels[start_v], self._dict_labels[end_v]

        if self._directed:
            if self._matrix[i][j] == 0:
                self._matrix[i][j] = 1
                self._nr_edges += 1
                if self._weighted:
                    self._weights[(i, j)] = weight
            return

        # Undirected graph: maintain symmetric matrix.
        if i == j:
            if self._matrix[i][i] == 0:
                self._matrix[i][i] = 1
                self._nr_edges += 1
                if self._weighted:
                    self._weights[(i, i)] = weight
            return

        if self._matrix[i][j] == 0 and self._matrix[j][i] == 0:
            self._nr_edges += 1
        self._matrix[i][j] = 1
        self._matrix[j][i] = 1
        if self._weighted:
            self._weights[(i, j)] = weight
            self._weights[(j, i)] = weight

    def remove_edge(self, start_v, end_v):
        """
        Removes the edge between the given vertices.
        Complexity: O(1)
        """
        if start_v in self._dict_labels and end_v in self._dict_labels:
            i, j = self._dict_labels[start_v], self._dict_labels[end_v]

            if self._directed:
                if self._matrix[i][j] == 1:
                    self._matrix[i][j] = 0
                    self._weights.pop((i, j), None)
                    self._nr_edges -= 1
                return

            # Undirected graph: remove both directions at once.
            if i == j:
                if self._matrix[i][i] == 1:
                    self._matrix[i][i] = 0
                    self._weights.pop((i, i), None)
                    self._nr_edges -= 1
                return

            if self._matrix[i][j] == 1 or self._matrix[j][i] == 1:
                self._matrix[i][j] = 0
                self._matrix[j][i] = 0
                self._weights.pop((i, j), None)
                self._weights.pop((j, i), None)
                self._nr_edges -= 1

    def remove_vertex(self, vertex):
        """
        Removes the vertex and all incident edges.
        Complexity: O(n) because the matrix must drop a row/column and rebuild mappings, where n is the number of vertices.
        """
        if vertex not in self._dict_labels:
            raise ValueError("Error: Vertex does not exist.")

        idx_to_remove = self._dict_labels[vertex]
        old_weights = dict(self._weights)

        # Remove the row and column from the matrix
        self._matrix.pop(idx_to_remove)
        for row in self._matrix:
            row.pop(idx_to_remove)

        # Refresh the mapping structures
        self._index_to_label.pop(idx_to_remove)
        self._dict_labels = {label: i for i, label in enumerate(self._index_to_label)}

        # Rebuild weight keys because matrix indices shift after vertex removal.
        self._weights = {}
        for (i, j), w in old_weights.items():
            if i == idx_to_remove or j == idx_to_remove:
                continue
            new_i = i - 1 if i > idx_to_remove else i
            new_j = j - 1 if j > idx_to_remove else j
            self._weights[(new_i, new_j)] = w

        self._recompute_edge_count()

    def get_v(self):
        """ Returns the number of vertices. Complexity: O(1)  """
        return len(self._index_to_label)

    def get_e(self):
        """ Returns the number of edges. Complexity: O(1) """
        return self._nr_edges

    def is_edge(self, v1, v2):
        """ Checks whether the edge exists. Complexity: O(1)  """
        if v1 not in self._dict_labels or v2 not in self._dict_labels:
            return False
        return self._matrix[self._dict_labels[v1]][self._dict_labels[v2]] == 1

    def neighbors(self, vertex):
        """
        Returns the list of vertices reachable from `vertex`.
        Complexity: O(n), where n is the number of vertices (scan of the adjacency row).
        """
        if vertex not in self._dict_labels:
            raise ValueError("Vertex does not exist.")

        idx = self._dict_labels[vertex]
        return [self._index_to_label[j] for j, val in enumerate(self._matrix[idx]) if val == 1]

    def inbound_neighbors(self, vertex):
        """
        Returns the vertices that have edges toward `vertex`.
        Complexity: O(n), where n is the number of vertices.
        """
        if vertex not in self._dict_labels:
            raise ValueError("Vertex does not exist.")

        if not self._directed:
            return self.neighbors(vertex)

        idx = self._dict_labels[vertex]
        return [self._index_to_label[i] for i, row in enumerate(self._matrix) if row[idx] == 1]

    def get_vertices(self):
        """ Returns the list of all vertices. Complexity: O(n), where n is the number of vertices.  """
        return list(self._index_to_label)

    def get_edges(self):
        """ Returns the list of all edges. Complexity: O(n^2), where n is the number of vertices (full matrix scan).  """
        edges = []
        for i in range(len(self._matrix)):
            for j in range(len(self._matrix)):
                if self._matrix[i][j] == 1:
                    edges.append((self._index_to_label[i], self._index_to_label[j]))
        return edges

    def change_if_directed(self, directed: bool):
        """
        Changes graph mode between directed and undirected and normalizes adjacency accordingly.
        """
        directed = bool(directed)
        if directed == self._directed:
            return

        n = len(self._matrix)

        if not self._directed and directed:
            # Undirected -> directed: ensure every undirected edge exists in both directions.
            for i in range(n):
                for j in range(i + 1, n):
                    if self._matrix[i][j] == 1 or self._matrix[j][i] == 1:
                        self._matrix[i][j] = 1
                        self._matrix[j][i] = 1
                        if self._weighted:
                            w = self._weights.get((i, j), self._weights.get((j, i), 0))
                            self._weights[(i, j)] = w
                            self._weights[(j, i)] = w
        else:
            # Directed -> undirected: merge opposite directions into one undirected edge.
            for i in range(n):
                for j in range(i + 1, n):
                    val = 1 if (self._matrix[i][j] == 1 or self._matrix[j][i] == 1) else 0
                    self._matrix[i][j] = val
                    self._matrix[j][i] = val
                    if self._weighted:
                        if val == 1:
                            w = self._weights.get((i, j), self._weights.get((j, i), 0))
                            self._weights[(i, j)] = w
                            self._weights[(j, i)] = w
                        else:
                            self._weights.pop((i, j), None)
                            self._weights.pop((j, i), None)

        self._directed = directed
        # Recompute edge count because edge semantics changed.
        self._recompute_edge_count()

    def change_if_weighted(self, weighted: bool):
        """
        Enables/disables weighted mode and normalizes the internal weights dictionary.
        """
        weighted = bool(weighted)
        if weighted == self._weighted:
            return

        if not weighted:
            # In unweighted mode, edge costs should not be stored.
            self._weights.clear()
            self._weighted = False
            return

        self._weighted = True
        n = len(self._matrix)
        for i in range(n):
            for j in range(n):
                if self._matrix[i][j] == 1:
                    # Existing edges get default 0 cost if missing.
                    self._weights[(i, j)] = self._weights.get((i, j), 0)

        if not self._directed:
            for i in range(n):
                for j in range(i + 1, n):
                    if self._matrix[i][j] == 1 or self._matrix[j][i] == 1:
                        w = self._weights.get((i, j), self._weights.get((j, i), 0))
                        self._weights[(i, j)] = w
                        self._weights[(j, i)] = w

    def set_weight(self, start_v, end_v, weight):
        """
        Sets the edge weight for an existing edge.
        """
        if not self._weighted:
            raise ValueError("Error: Graph is unweighted.")
        if start_v not in self._dict_labels or end_v not in self._dict_labels:
            raise ValueError("Error: One or both vertices do not exist.")

        i, j = self._dict_labels[start_v], self._dict_labels[end_v]
        if self._matrix[i][j] != 1:
            raise ValueError("Error: Edge does not exist.")

        self._weights[(i, j)] = weight
        if not self._directed:
            self._weights[(j, i)] = weight

    def get_weight(self, start_v, end_v):
        """
        Returns the edge weight for an existing edge.
        """
        if not self._weighted:
            raise ValueError("Error: Graph is unweighted.")
        if start_v not in self._dict_labels or end_v not in self._dict_labels:
            raise ValueError("Error: One or both vertices do not exist.")

        i, j = self._dict_labels[start_v], self._dict_labels[end_v]
        if self._matrix[i][j] != 1:
            raise ValueError("Error: Edge does not exist.")

        return self._weights.get((i, j), 0)

    def BFS_iter(self, start_vertex):
        """
        Returns a BFS iterator starting from the given vertex.
        """
        return BFSIterator(self, start_vertex)

    def DFS_iter(self, start_vertex):
        """
        Returns a DFS iterator starting from the given vertex.
        """
        return DFSIterator(self, start_vertex)

    @staticmethod
    def create_from_file(filepath):
        """
        Builds and returns a Graph instance from a text file.

        File format:
        - First non-empty line: contains graph mode words (directed/undirected, weighted/unweighted)
        - Remaining non-empty lines:
            1 token  -> vertex
            2 tokens -> unweighted edge
            3 tokens -> weighted edge (third token parsed as float)
        """
        # We read all lines once so we can find the first non-empty header line.
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        header = None
        header_line_no = None
        for line_no, raw in enumerate(lines, start=1):
            stripped = raw.strip()
            if stripped:
                header = stripped.lower().split()
                header_line_no = line_no
                break

        if header is None:
            raise ValueError("Error: Empty file or missing graph header.")

        has_directed = "directed" in header
        has_undirected = "undirected" in header
        has_weighted = "weighted" in header
        has_unweighted = "unweighted" in header

        if has_directed == has_undirected:
            raise ValueError(
                f"Error: Invalid direction flag on line {header_line_no}. "
                "Use exactly one of: directed / undirected."
            )

        if has_weighted == has_unweighted:
            raise ValueError(
                f"Error: Invalid weight flag on line {header_line_no}. "
                "Use exactly one of: weighted / unweighted."
            )

        graph = Graph(directed=has_directed, weighted=has_weighted)

        # Parse data lines after header. Empty lines are ignored.
        for line_no, raw in enumerate(lines[header_line_no:], start=header_line_no + 1):
            stripped = raw.strip()
            if not stripped:
                continue

            parts = stripped.split()
            if len(parts) == 1:
                vertex = parts[0]
                if vertex not in graph._dict_labels:
                    graph.add_vertex(vertex)
                continue

            if len(parts) == 2:
                start_v, end_v = parts
                # Auto-create missing vertices when edges mention them.
                if start_v not in graph._dict_labels:
                    graph.add_vertex(start_v)
                if end_v not in graph._dict_labels:
                    graph.add_vertex(end_v)
                graph.add_edge(start_v, end_v)
                continue

            if len(parts) == 3:
                start_v, end_v, weight_raw = parts
                try:
                    weight = float(weight_raw)
                except ValueError as exc:
                    raise ValueError(f"Error: Invalid weight on line {line_no}: '{weight_raw}'.") from exc

                if start_v not in graph._dict_labels:
                    graph.add_vertex(start_v)
                if end_v not in graph._dict_labels:
                    graph.add_vertex(end_v)
                graph.add_edge(start_v, end_v, weight)
                continue

            raise ValueError(
                f"Error: Invalid line format at line {line_no}. "
                "Expected 1, 2, or 3 tokens."
            )

        return graph

    def __str__(self):
        """
        Formats the graph for export.
        Complexity: O(n^2), where n is the number of vertices (full matrix traversal).
        """
        graph_type = "directed" if self._directed else "undirected"
        weight_type = "weighted" if self._weighted else "unweighted"
        lines = [f"{graph_type} {weight_type}"]
        printed_nodes = set()

        n = len(self._matrix)

        # Append the edges
        if self._directed:
            for i in range(n):
                for j in range(n):
                    if self._matrix[i][j] == 1:
                        if self._weighted:
                            lines.append(
                                f"{self._index_to_label[i]} {self._index_to_label[j]} {self._weights.get((i, j), 0)}"
                            )
                        else:
                            lines.append(f"{self._index_to_label[i]} {self._index_to_label[j]}")
                        printed_nodes.add(self._index_to_label[i])
                        printed_nodes.add(self._index_to_label[j])
        else:
            # For undirected graphs we only print each edge once (upper triangle).
            for i in range(n):
                for j in range(i, n):
                    if self._matrix[i][j] == 1 or self._matrix[j][i] == 1:
                        if self._weighted:
                            w = self._weights.get((i, j), self._weights.get((j, i), 0))
                            lines.append(f"{self._index_to_label[i]} {self._index_to_label[j]} {w}")
                        else:
                            lines.append(f"{self._index_to_label[i]} {self._index_to_label[j]}")
                        printed_nodes.add(self._index_to_label[i])
                        printed_nodes.add(self._index_to_label[j])

        # Append isolated vertices
        for node in self._index_to_label:
            if node not in printed_nodes:
                lines.append(str(node))

        return "\n".join(lines)