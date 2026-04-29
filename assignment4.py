from collections import deque
from assignment1 import Graph

def topological_sort(graph):
    """
    Verifies if the graph is a DAG and performs topological sorting
    using predecessor counters (Kahn's algorithm).
    Complexity: O(v + e)
    """
    in_degree = {}
    vertices = graph.get_vertices()

    # 1. Calculate predecessor counters (in-degrees)
    for v in vertices:
        in_degree[v] = len(graph.inbound_neighbors(v))

    # 2. Add all vertices with 0 in-degree to the queue
    queue = deque([v for v in vertices if in_degree[v] == 0])
    topo_order = []

    # 3. Process the queue
    while queue:
        u = queue.popleft()
        topo_order.append(u)

        # Decrement the in-degree of all neighbors
        for neighbor in graph.neighbors(u):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # 4. If the sorted list has all vertices, it's a DAG
    is_dag = len(topo_order) == len(vertices)

    return is_dag, topo_order

def highest_cost_path(graph, start_vertex, target_vertex):
    """
    Finds the highest cost path between two vertices in a DAG.
    Complexity: O(v + e)
    """
    # Verify DAG and get the topological order
    is_dag, topo_order = topological_sort(graph)

    if not is_dag:
        raise ValueError("Error: The graph is not a Directed Acyclic Graph (DAG). It contains a cycle.")

    vertices = graph.get_vertices()
    if start_vertex not in vertices or target_vertex not in vertices:
        raise ValueError("Error: Start or target vertex does not exist in the graph.")

    # Initialize distances to -infinity and parents to None
    distances = {v: float('-inf') for v in vertices}
    parents = {v: None for v in vertices}

    distances[start_vertex] = 0

    # Process vertices strictly in topological order
    for u in topo_order:
        if distances[u] != float('-inf'):  # Only process reachable vertices
            for v in graph.neighbors(u):
                weight = graph.get_weight(u, v)

                # Relaxation for HIGHEST cost (we want to maximize distance)
                if distances[u] + weight > distances[v]:
                    distances[v] = distances[u] + weight
                    parents[v] = u

    # Reconstruct the path from target back to start
    path = []
    current = target_vertex

    # If the target is reachable, build the path
    if distances[target_vertex] != float('-inf'):
        while current is not None:
            path.append(current)
            if current == start_vertex:
                break
            current = parents[current]
        path.reverse()
    else:
        # If unreachable, return negative infinity and empty path
        return float('-inf'), []

    return distances[target_vertex], path

def main():
    graph_file = "dag_test.txt"

    try:
        g = Graph.create_from_file(graph_file)

        start_node = "A"
        target_node = "F"

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