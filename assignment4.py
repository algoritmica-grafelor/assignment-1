from collections import deque
from assignment1 import Graph

def topological_sort(graph):
    """
    Verifies if the graph is a DAG and performs topological sorting
    using predecessor counters (Kahn's algorithm).

    Overall Time Complexity: O(v + e), where v is the number of vertices
    and e is the number of edges.
    """
    in_degree = {}

    # Getting all vertices takes O(v) time.
    vertices = graph.get_vertices()

    # 1. Calculate predecessor counters (in-degrees)
    # This loop runs 'v' times. Inside, inbound_neighbors retrieves edges.
    # Across the entire loop, every edge in the graph is counted exactly once.
    # Therefore, this entire step takes O(v + e) time.
    for v in vertices:
        in_degree[v] = len(graph.inbound_neighbors(v))

    # 2. Add all vertices with 0 in-degree to the queue
    # This list comprehension checks the in_degree of every vertex once: O(v) time.
    queue = deque([v for v in vertices if in_degree[v] == 0])
    topo_order = []

    # 3. Process the queue
    # Each vertex is added to and popped from the queue exactly once: O(v) time.
    while queue:
        u = queue.popleft()
        topo_order.append(u)

        # Decrement the in-degree of all neighbors
        # This inner loop iterates over the outgoing edges of 'u'.
        # Over the course of the while loop, every edge is visited exactly once.
        # This contributes O(e) time.
        # Combined with the queue operations, this block is O(v + e).
        for neighbor in graph.neighbors(u):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # 4. If the sorted list has all vertices, it's a DAG
    # len() checks take O(1) time.
    is_dag = len(topo_order) == len(vertices)

    return is_dag, topo_order

def highest_cost_path(graph, start_vertex, target_vertex):
    """
    Finds the highest cost path between two vertices in a DAG.

    Overall Time Complexity: O(v + e), where v is the number of vertices
    and e is the number of edges.
    """
    # 1. topological_sort runs in O(v + e) time as proven above.
    is_dag, topo_order = topological_sort(graph)

    if not is_dag:
        raise ValueError("Error: The graph is not a Directed Acyclic Graph (DAG). It contains a cycle.")

    vertices = graph.get_vertices()
    if start_vertex not in vertices or target_vertex not in vertices:
        raise ValueError("Error: Start or target vertex does not exist in the graph.")

    # 2. Initialize distances to -infinity and parents to None
    # Dictionary comprehensions over 'v' vertices take O(v) time.
    distances = {v: float('-inf') for v in vertices}
    parents = {v: None for v in vertices}

    distances[start_vertex] = 0

    # 3. Process vertices strictly in topological order
    # The outer loop runs exactly 'v' times (once for each vertex in topo_order).
    for u in topo_order:
        if distances[u] != float('-inf'):  # Only process reachable vertices

            # The inner loop iterates through the outgoing neighbors of 'u'.
            # Over the course of the outer loop, every edge 'e' is evaluated exactly once.
            # Thus, this nested loop structure runs in exactly O(v + e) time.
            for v in graph.neighbors(u):
                weight = graph.get_weight(u, v)

                # Relaxation for HIGHEST cost (we want to maximize distance)
                # Dictionary lookups and assignments are O(1).
                if distances[u] + weight > distances[v]:
                    distances[v] = distances[u] + weight
                    parents[v] = u

    # 4. Reconstruct the path from target back to start
    path = []
    current = target_vertex

    # Backtracking follows the parent pointers.
    # In the worst-case scenario, the path includes every vertex, taking O(v) time.
    if distances[target_vertex] != float('-inf'):
        while current is not None:
            path.append(current)
            if current == start_vertex:
                break
            current = parents[current]
        # Reversing a list of size at most 'v' takes O(v) time.
        path.reverse()
    else:
        # If unreachable, return negative infinity and empty path
        return float('-inf'), []

    # Total complexity: O(v + e) [topological sort] + O(v) [initialization] + O(v + e) [edge relaxation] + O(v) [path reconstruction]
    # This simplifies to strictly O(v + e).
    return distances[target_vertex], path

def main():
    graph_file = "DAG.txt"

    try:
        g = Graph.create_from_file(graph_file)

        start_node = "1"
        target_node = "6"

        print("Checking graph and calculating highest cost path...")
        max_cost, path = highest_cost_path(g, start_node, target_node)

        if max_cost == float('-inf'):
            print(f"No path exists between {start_node} and {target_node}.")
        else:
            print(f"Highest cost path from {start_node} to {target_node}:")
            print(f"Cost: {max_cost}")
            print(f"Path: {' -> '.join(path)}")

    except ValueError as e:
        print(e)
    except FileNotFoundError:
        print(f"Error: Could not find file {graph_file}.")

if __name__ == "__main__":
    main()