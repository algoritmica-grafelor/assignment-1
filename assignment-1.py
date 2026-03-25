class Graph:
    def __init__(self, directed=True):
        """
        Creates an empty graph.
        Complexity: O(1)
        """
        self._directed = directed
        self._matrix = []  # Adjacency matrix
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

    def add_edge(self, start_v, end_v):
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
            return

        # Undirected graph: maintain symmetric matrix.
        if i == j:
            if self._matrix[i][i] == 0:
                self._matrix[i][i] = 1
                self._nr_edges += 1
            return

        if self._matrix[i][j] == 0 and self._matrix[j][i] == 0:
            self._nr_edges += 1
        self._matrix[i][j] = 1
        self._matrix[j][i] = 1

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
                    self._nr_edges -= 1
                return

            # Undirected graph: remove both directions at once.
            if i == j:
                if self._matrix[i][i] == 1:
                    self._matrix[i][i] = 0
                    self._nr_edges -= 1
                return

            if self._matrix[i][j] == 1 or self._matrix[j][i] == 1:
                self._matrix[i][j] = 0
                self._matrix[j][i] = 0
                self._nr_edges -= 1

    def remove_vertex(self, vertex):
        """
        Removes the vertex and all incident edges.
        Complexity: O(n) because the matrix must drop a row/column and rebuild mappings, where n is the number of vertices.
        """
        if vertex not in self._dict_labels:
            raise ValueError("Error: Vertex does not exist.")

        idx_to_remove = self._dict_labels[vertex]

        # Remove the row and column from the matrix
        self._matrix.pop(idx_to_remove)
        for row in self._matrix:
            row.pop(idx_to_remove)

        # Refresh the mapping structures
        self._index_to_label.pop(idx_to_remove)
        self._dict_labels = {label: i for i, label in enumerate(self._index_to_label)}

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
        else:
            # Directed -> undirected: merge opposite directions into one undirected edge.
            for i in range(n):
                for j in range(i + 1, n):
                    val = 1 if (self._matrix[i][j] == 1 or self._matrix[j][i] == 1) else 0
                    self._matrix[i][j] = val
                    self._matrix[j][i] = val

        self._directed = directed
        self._recompute_edge_count()

    def __str__(self):
        """
        Formats the graph for export.
        Complexity: O(n^2), where n is the number of vertices (full matrix traversal).
        """
        graph_type = "directed" if self._directed else "undirected"
        lines = [f"{graph_type} unweighted"]
        printed_nodes = set()

        n = len(self._matrix)

        # Append the edges
        if self._directed:
            for i in range(n):
                for j in range(n):
                    if self._matrix[i][j] == 1:
                        lines.append(f"{self._index_to_label[i]} {self._index_to_label[j]}")
                        printed_nodes.add(self._index_to_label[i])
                        printed_nodes.add(self._index_to_label[j])
        else:
            for i in range(n):
                for j in range(i, n):
                    if self._matrix[i][j] == 1 or self._matrix[j][i] == 1:
                        lines.append(f"{self._index_to_label[i]} {self._index_to_label[j]}")
                        printed_nodes.add(self._index_to_label[i])
                        printed_nodes.add(self._index_to_label[j])

        # Append isolated vertices
        for node in self._index_to_label:
            if node not in printed_nodes:
                lines.append(str(node))

        return "\n".join(lines)