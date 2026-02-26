import copy


class Graph:
    def __init__(self):
        """
        Creează un graf nou gol.
        Complexitate: O(1)
        """
        self._matrix = []  # Matricea de adiacenta
        self._dict_labels = {}  # Mapare: nume_nod -> index_matrice
        self._index_to_label = []  # Mapare: index_matrice -> nume_nod
        self._nr_edges = 0

    def add_vertex(self, vertex):
        """
        Adaugă un nod nou. Ridică eroare dacă acesta există deja.
        Complexitate: O(n), unde n este numărul de noduri (din cauza extinderii rândurilor).
        """
        if vertex in self._dict_labels:
            raise ValueError(f"Eroare: Nodul {vertex} exista deja.")

        new_index = len(self._index_to_label)
        self._dict_labels[vertex] = new_index
        self._index_to_label.append(vertex)

        # Adaugam o coloana noua la fiecare rand existent
        for row in self._matrix:
            row.append(0)

        # Adaugam un rand nou plin de 0 pentru noul nod
        self._matrix.append([0] * (new_index + 1))

    def add_edge(self, start_v, end_v):
        """
        Adaugă o muchie orientată. Dacă muchia există, nu face nimic.
        Complexitate: O(1)
        """
        if start_v not in self._dict_labels or end_v not in self._dict_labels:
            raise ValueError("Eroare: Unul sau ambele noduri nu exista.")

        i, j = self._dict_labels[start_v], self._dict_labels[end_v]

        if self._matrix[i][j] == 0:
            self._matrix[i][j] = 1
            self._nr_edges += 1

    def remove_edge(self, start_v, end_v):
        """
        Elimină muchia dintre cele două noduri.
        Complexitate: O(1)
        """
        if start_v in self._dict_labels and end_v in self._dict_labels:
            i, j = self._dict_labels[start_v], self._dict_labels[end_v]
            if self._matrix[i][j] == 1:
                self._matrix[i][j] = 0
                self._nr_edges -= 1

    def remove_vertex(self, vertex):
        """
        Elimină nodul și toate muchiile conectate la acesta.
        Complexitate: O(n^2) - necesită reconstrucția matricei.
        """
        if vertex not in self._dict_labels:
            raise ValueError("Eroare: Nodul nu exista.")

        idx_to_remove = self._dict_labels[vertex]

        # Scadem numarul de muchii care vor fi sterse
        for j in range(len(self._matrix)):
            if self._matrix[idx_to_remove][j] == 1: self._nr_edges -= 1
            if self._matrix[j][idx_to_remove] == 1 and j != idx_to_remove: self._nr_edges -= 1

        # Stergem randul si coloana din matrice
        self._matrix.pop(idx_to_remove)
        for row in self._matrix:
            row.pop(idx_to_remove)

        # Actualizam structurile de mapare
        self._index_to_label.pop(idx_to_remove)
        self._dict_labels = {label: i for i, label in enumerate(self._index_to_label)}

    def get_v(self):
        """ Returnează numărul de noduri. Complexitate: O(1)  """
        return len(self._index_to_label)

    def get_e(self):
        """ Returnează numărul de muchii. Complexitate: O(1) """
        return self._nr_edges

    def is_edge(self, v1, v2):
        """ Verifică existența unei muchii. Complexitate: O(1)  """
        if v1 not in self._dict_labels or v2 not in self._dict_labels:
            return False
        return self._matrix[self._dict_labels[v1]][self._dict_labels[v2]] == 1

    def neighbors(self, vertex):
        """
        Returnează lista nodurilor accesibile din 'vertex'.
        Complexitate: O(n)
        """
        if vertex not in self._dict_labels:
            raise ValueError("Nodul nu exista.")

        idx = self._dict_labels[vertex]
        return [self._index_to_label[j] for j, val in enumerate(self._matrix[idx]) if val == 1]

    def inbound_neighbors(self, vertex):
        """
        Bonus: Returnează nodurile care au muchie către 'vertex'.
        Complexitate: O(n)
        """
        if vertex not in self._dict_labels:
            raise ValueError("Nodul nu exista.")

        idx = self._dict_labels[vertex]
        return [self._index_to_label[i] for i, row in enumerate(self._matrix) if row[idx] == 1]

    def get_vertices(self):
        """ Returnează lista tuturor nodurilor. Complexitate: O(n)  """
        return list(self._index_to_label)

    def get_edges(self):
        """ Returnează lista tuturor muchiilor. Complexitate: O(n^2)  """
        edges = []
        for i in range(len(self._matrix)):
            for j in range(len(self._matrix)):
                if self._matrix[i][j] == 1:
                    edges.append((self._index_to_label[i], self._index_to_label[j]))
        return edges

    def __str__(self):
        """
        Formatează graful pentru export.
        Complexitate: O(n^2)
        """
        lines = ["directed unweighted"]
        printed_nodes = set()

        # Adaugam muchiile
        for i in range(len(self._matrix)):
            has_edge = False
            for j in range(len(self._matrix)):
                if self._matrix[i][j] == 1:
                    lines.append(f"{self._index_to_label[i]} {self._index_to_label[j]}")
                    has_edge = True
                    printed_nodes.add(self._index_to_label[i])
                    printed_nodes.add(self._index_to_label[j])

        # Adaugam nodurile izolate
        for node in self._index_to_label:
            if node not in printed_nodes:
                lines.append(str(node))

        return "\n".join(lines)