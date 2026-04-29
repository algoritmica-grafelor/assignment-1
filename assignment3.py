import heapq
import time
import math
from assignment1 import Graph

def read_coordinates(filepath):
    """Reads vertex coordinates from an auxiliary file for the A* heuristic."""
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

def euclidean_distance(v1, v2, coords):
    """Calculates the Euclidean distance between two vertices."""
    if v1 not in coords or v2 not in coords:
        return 0
    x1, y1 = coords[v1]
    x2, y2 = coords[v2]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def reconstruct_path(parents, start, target):
    """Backtracks through the parents dictionary to build the path."""
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
    """Dijkstra's algorithm tracking time and operation counts."""
    stats = {'cost_checks': 0, 'pq_pushes': 0, 'pq_pops': 0}
    pq = []

    heapq.heappush(pq, (0, start))
    stats['pq_pushes'] += 1

    distances = {start: 0}
    parents = {start: None}

    start_time = time.perf_counter()

    while pq:
        current_dist, current_v = heapq.heappop(pq)
        stats['pq_pops'] += 1

        if current_v == target:
            break

        if current_dist > distances.get(current_v, float('inf')):
            continue

        for neighbor in graph.neighbors(current_v):
            weight = graph.get_weight(current_v, neighbor)
            stats['cost_checks'] += 1

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
    """A* Search algorithm using Euclidean distance heuristic."""
    stats = {'cost_checks': 0, 'pq_pushes': 0, 'pq_pops': 0}
    pq = []

    h_start = euclidean_distance(start, target, coords)
    heapq.heappush(pq, (h_start, 0, start))
    stats['pq_pushes'] += 1

    g_scores = {start: 0}
    parents = {start: None}

    start_time = time.perf_counter()

    while pq:
        f_score, current_g, current_v = heapq.heappop(pq)
        stats['pq_pops'] += 1

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
    """Formats the output exactly as requested in the assignment."""
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
    graph_file = "positive_graph.txt"
    coords_file = "coordinates.txt"

    try:
        g = Graph.create_from_file(graph_file)
        coords = read_coordinates(coords_file)

        start_node = "1"
        target_node = "5"

        dijkstra_results = dijkstra(g, start_node, target_node)
        astar_results = a_star(g, start_node, target_node, coords)

        print_comparison(start_node, target_node, dijkstra_results, astar_results)

    except FileNotFoundError as e:
        print(f"Please ensure {graph_file} and {coords_file} exist in the directory.")