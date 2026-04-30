import heapq
import time
import math
from assignment1 import Graph

def read_coordinates(filepath):
    """
    Reads vertex coordinates from an auxiliary file for the A* heuristic.

    Time Complexity: O(V)
    - Where V is the number of lines (vertices) in the coordinates file.
    - We iterate through the file exactly once.
    """
    coords = {}
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                vertex = parts[0]
                x = float(parts[1])
                y = float(parts[2])
                coords[vertex] = (x, y)
    return coords

def read_coordinates2(filepath):
    coords = {}
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split(',')

            if len(parts) >= 3:
                try:
                    vertex = parts[0].strip()
                    x = float(parts[1])
                    y = float(parts[2])
                    coords[vertex] = (x, y)
                except ValueError:
                    continue

    return coords

def euclidean_distance(v1, v2, coords):
    """
    Calculates the Euclidean distance between two vertices.

    Time Complexity: O(1)
    - Dictionary lookups and basic arithmetic operations execute in constant time.
    """
    if v1 not in coords or v2 not in coords:
        return 0  # Fallback to 0 (acts like Dijkstra) if coords are missing
    x1, y1 = coords[v1]
    x2, y2 = coords[v2]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def reconstruct_path(parents, start, target):
    """
    Backtracks through the parents dictionary to build the path.

    Time Complexity: O(V)
    - In the absolute worst case, the path spans every vertex in the graph,
      requiring V iterations to backtrack and an O(V) list reversal.
    """
    path = []
    current = target
    while current is not None:
        path.append(current)
        if current == start:
            break
        current = parents.get(current)
    path.reverse()
    return path

def dijkstra(graph, start, target):
    """
    Dijkstra's algorithm tracking time and operation counts.

    Time Complexity: O(V^2 + E log V)
    - Popping vertices from the priority queue takes O(log V) time and happens at most V times = O(V log V).
    - Finding neighbors for each vertex using an adjacency matrix takes O(V) time per vertex = O(V^2).
    - Pushing neighbor updates to the priority queue takes O(log V) time, happening at most E times = O(E log V).
    - Dominant terms are O(V^2) for neighbor lookups and O(E log V) for queue pushes.
    """
    stats = {'cost_checks': 0, 'pq_pushes': 0, 'pq_pops': 0}
    pq = []

    # Priority Queue stores tuples of (distance, vertex)
    heapq.heappush(pq, (0, start))
    stats['pq_pushes'] += 1

    distances = {start: 0}
    parents = {start: None}

    start_time = time.perf_counter()

    while pq:
        current_dist, current_v = heapq.heappop(pq)
        stats['pq_pops'] += 1

        # Stop early once we find the terminal vertex
        if current_v == target:
            break

        # Ignore outdated queue entries
        if current_dist > distances.get(current_v, float('inf')):
            continue

        for neighbor in graph.neighbors(current_v):
            weight = graph.get_weight(current_v, neighbor)
            stats['cost_checks'] += 1  # Counting edge cost checks

            new_dist = current_dist + weight

            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                parents[neighbor] = current_v
                heapq.heappush(pq, (new_dist, neighbor))
                stats['pq_pushes'] += 1

    end_time = time.perf_counter()

    return {
        'time_ms': (end_time - start_time) * 1000,
        'cost': distances.get(target, float('inf')),
        'path': reconstruct_path(parents, start, target) if target in distances else [],
        'stats': stats
    }

def a_star(graph, start, target, coords):
    """
    A* Search algorithm using Euclidean distance heuristic.

    Time Complexity: O(V^2 + E log V) worst-case
    - Worst case: Identical to Dijkstra's bounds. If the heuristic is useless (e.g., always 0),
      A* evaluates the exact same nodes as Dijkstra in the exact same matrix format.
    - Average/Practical case: Performs significantly better than worst-case bounds, closer
      to O(E_path log V) because the heuristic allows it to prune large sections of the graph.
    """
    stats = {'cost_checks': 0, 'pq_pushes': 0, 'pq_pops': 0}
    pq = []

    # Queue stores: (f_score, g_score, vertex)
    # f_score = g_score (actual cost) + h_score (heuristic)
    h_start = euclidean_distance(start, target, coords)
    heapq.heappush(pq, (h_start, 0, start))
    stats['pq_pushes'] += 1

    g_scores = {start: 0}
    parents = {start: None}

    start_time = time.perf_counter()

    while pq:
        f_score, current_g, current_v = heapq.heappop(pq)
        stats['pq_pops'] += 1

        # Stop early
        if current_v == target:
            break

        if current_g > g_scores.get(current_v, float('inf')):
            continue

        for neighbor in graph.neighbors(current_v):
            weight = graph.get_weight(current_v, neighbor)
            stats['cost_checks'] += 1

            tentative_g = current_g + weight

            if tentative_g < g_scores.get(neighbor, float('inf')):
                g_scores[neighbor] = tentative_g
                parents[neighbor] = current_v

                # Calculate heuristic and f_score
                h = euclidean_distance(neighbor, target, coords)
                f = tentative_g + h

                heapq.heappush(pq, (f, tentative_g, neighbor))
                stats['pq_pushes'] += 1

    end_time = time.perf_counter()

    return {
        'time_ms': (end_time - start_time) * 1000,
        'cost': g_scores.get(target, float('inf')),
        'path': reconstruct_path(parents, start, target) if target in g_scores else [],
        'stats': stats
    }

def print_comparison(start_v, target_v, res_dijkstra, res_astar):
    """
    Formats the output exactly as requested in the assignment.

    Time Complexity: O(V)
    - Joining the path list into a string takes time proportional to the length of the path (up to V).
    """
    print(f"\nMinimum cost walk {start_v} to {target_v}:")

    print(f"Dijkstra: time: {res_dijkstra['time_ms']:.2f}ms, cost: {res_dijkstra['cost']},")
    print(f"path: {', '.join(res_dijkstra['path'])}")

    print(f"A*: time: {res_astar['time_ms']:.2f}ms, cost: {res_astar['cost']},")
    print(f"path: {', '.join(res_astar['path'])}\n")

    print("Comparison:")
    print(f"{'Algorithm':<15} {'g.cost calls':<15} {'pq.push':<10} {'pq.pop':<10}")
    print("-" * 50)
    print(f"{'Dijkstra':<15} {res_dijkstra['stats']['cost_checks']:<15} {res_dijkstra['stats']['pq_pushes']:<10} {res_dijkstra['stats']['pq_pops']:<10}")
    print(f"{'A*':<15} {res_astar['stats']['cost_checks']:<15} {res_astar['stats']['pq_pushes']:<10} {res_astar['stats']['pq_pops']:<10}")

if __name__ == "__main__":
    graph_file = "positives_3_v50_e200.txt"
    coords_file = "positives_3_vertex_positions.txt"

    try:
        g = Graph.create_from_file(graph_file)
        coords = read_coordinates2(coords_file)

        start_node = "1"
        target_node = "50"

        dijkstra_results = dijkstra(g, start_node, target_node)
        astar_results = a_star(g, start_node, target_node, coords)

        print_comparison(start_node, target_node, dijkstra_results, astar_results)

    except FileNotFoundError as e:
        print(f"Please ensure {graph_file} and {coords_file} exist in the directory.")