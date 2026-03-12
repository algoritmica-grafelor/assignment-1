import copy


class Graph:
    def __init__(self):
        """
        Creates an empty directed graph.
        Complexity: O(1)
        """
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

    def add_edge(self, start_v, end_v):
        """
        Adds a directed edge. If it already exists, do nothing.
        Complexity: O(1)
        """
        if start_v not in self._dict_labels or end_v not in self._dict_labels:
            raise ValueError("Error: One or both vertices do not exist.")

        i, j = self._dict_labels[start_v], self._dict_labels[end_v]

        if self._matrix[i][j] == 0:
            self._matrix[i][j] = 1
            self._nr_edges += 1

    def remove_edge(self, start_v, end_v):
        """
        Removes the edge between the given vertices.
        Complexity: O(1)
        """
        if start_v in self._dict_labels and end_v in self._dict_labels:
            i, j = self._dict_labels[start_v], self._dict_labels[end_v]
            if self._matrix[i][j] == 1:
                self._matrix[i][j] = 0
                self._nr_edges -= 1

    def remove_vertex(self, vertex):
        """
        Removes the vertex and all incident edges.
        Complexity: O(n) because the matrix must drop a row/column and rebuild mappings, where n is the number of vertices.
        """
        if vertex not in self._dict_labels:
            raise ValueError("Error: Vertex does not exist.")

        idx_to_remove = self._dict_labels[vertex]

        # Decrease the edge count for each deleted edge
        for j in range(len(self._matrix)):
            if self._matrix[idx_to_remove][j] == 1: self._nr_edges -= 1
            if self._matrix[j][idx_to_remove] == 1 and j != idx_to_remove: self._nr_edges -= 1

        # Remove the row and column from the matrix
        self._matrix.pop(idx_to_remove)
        for row in self._matrix:
            row.pop(idx_to_remove)

        # Refresh the mapping structures
        self._index_to_label.pop(idx_to_remove)
        self._dict_labels = {label: i for i, label in enumerate(self._index_to_label)}

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
        Complexity: O(n), where n is the number of vertices (scan of the adjacency column).
        """
        if vertex not in self._dict_labels:
            raise ValueError("Vertex does not exist.")

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

    def __str__(self):
        """
        Formats the graph for export.
        Complexity: O(n^2), where n is the number of vertices (full matrix traversal).
        """
        lines = ["directed unweighted"]
        printed_nodes = set()

        # Append the edges
        for i in range(len(self._matrix)):
            has_edge = False
            for j in range(len(self._matrix)):
                if self._matrix[i][j] == 1:
                    lines.append(f"{self._index_to_label[i]} {self._index_to_label[j]}")
                    has_edge = True
                    printed_nodes.add(self._index_to_label[i])
                    printed_nodes.add(self._index_to_label[j])

        # Append isolated vertices
        for node in self._index_to_label:
            if node not in printed_nodes:
                lines.append(str(node))

        return "\n".join(lines)