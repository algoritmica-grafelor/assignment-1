from collections import deque
from assignment1 import Graph


def maximum_bipartite_matching_iterative(graph, partition_u, partition_v):
    """
    Finds the maximum matching in an undirected bipartite graph
    using an iterative algorithm (BFS for augmenting paths).

    Time Complexity: O(V * E)
    - In the worst case, we search for an augmenting path for each node in partition U.
    - A full BFS traversal takes O(V + E), where V is the number of vertices and E is the number of edges.
    - This yields a maximum theoretical complexity of O(V * (V + E)) which simplifies to O(V * E).

    Space Complexity: O(V)
    - The `match` and `parent` dictionaries, the `visited` set, and the `queue` require memory proportional to V.
    """

    # Dictionary holding the matches: match[node] = partner
    match = {}

    for u in partition_u:
        # Try to find an augmenting path only for nodes that are not yet matched
        if u not in match:

            # Initialize iterative BFS
            queue = deque([u])
            visited = {u}
            parent = {u: None}  # To reconstruct the augmenting path later

            found_augmenting_path = False
            end_node = None

            while queue:
                curr = queue.popleft()

                # If the current node is from partition U (Left side)
                if curr in partition_u:
                    # We can traverse any edge to partition V, as long as the node is unvisited
                    for neighbor in graph.neighbors(curr):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            parent[neighbor] = curr

                            if neighbor not in match:
                                # FOUND AN UNMATCHED NODE IN V!
                                # This is the end of the augmenting path.
                                found_augmenting_path = True
                                end_node = neighbor
                                break
                            else:
                                # Node is already matched, so we continue the BFS by adding it to the queue
                                queue.append(neighbor)

                    if found_augmenting_path:
                        break  # Stop the current BFS, we found an augmenting path

                # If the current node is from partition V (Right side)
                else:
                    # WE MUST go back to U on the existing matching edge
                    matched_u = match[curr]
                    if matched_u not in visited:
                        visited.add(matched_u)
                        parent[matched_u] = curr
                        queue.append(matched_u)

            # If we found an augmenting path, reconstruct it and alter the matching
            if found_augmenting_path:
                curr_node = end_node  # This is always a node from V

                while curr_node is not None:
                    p_u = parent[curr_node]  # Its parent (from U)
                    if p_u is None:
                        break

                    # Match the node from V with the node from U
                    match[curr_node] = p_u
                    match[p_u] = curr_node

                    # Jump to the next 'step' back on the path (which will be a node from V)
                    curr_node = parent.get(p_u)

    # Return the list of pairs (u, v), filtering only from U's perspective to avoid duplicates
    return [(u, match[u]) for u in partition_u if u in match]


def main():
    """
    Test function to validate the algorithm.
    We build a test bipartite graph directly in the code.
    """
    g = Graph.create_from_file("Bipartite.txt")

    # Define the partitions
    partition_u = ["A", "B", "C", "D"]
    partition_v = ["1", "2", "3", "4"]

    print("Bipartite Graph created. Searching for Maximum Matching...")

    matching = maximum_bipartite_matching_iterative(g, partition_u, partition_v)

    print(f"\nFound {len(matching)} maximum matching pairs:")
    for u, v in matching:
        print(f" - Node {u} is matched with {v}")


if __name__ == "__main__":
    main()