from typing import Optional, List, Tuple
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import heapq
import unittest
import numpy as np
from io import StringIO
import sys


def _validate_inputs(G, start, end):
    """Common input validation for all search algorithms."""
    if start not in G or end not in G:
        print("Start or goal not in graph. Choose valid nodes.")
        return False
    return True

def _initialize_search_state():
    """Initialize common search state variables."""
    return {
        'visited': set(),
        'expanded': [],
        'tree_edges': [],
        'max_depth': 0,
        'step': 0
    }

def _print_frontier_state(step, frontier_data, algorithm):
    """Print current frontier state for any algorithm."""
    print(f"\n--- Step {step} ---")
    if algorithm == 'BFS' or algorithm == 'DFS':
        nodes, depths = frontier_data
        print(f"Frontier queue: {nodes} (depths: {depths}) | size={len(nodes)}")        
    elif algorithm == 'UCS':
        frontier_info = frontier_data
        print(f"Priority queue (cost-ordered): {frontier_info} | size={len(frontier_info)}")

def _print_goal_reached(path, max_depth, max_size, cost=None):
    """Print goal reached message with statistics."""
    print(f"\nGOAL REACHED!")
    print(f"Path: {' → '.join(path)}")
    if cost is not None:
        print(f"Total cost: ${cost:.1f}")
    print(f"Path length: {len(path)-1} edges")
    print(f"Max depth explored: {max_depth}")
    print(f"Peak memory usage: {max_size} nodes in {'queue' if cost is not None else 'queue/stack'}")

def _print_goal_not_found(end, start, max_depth, max_size):
    """Print goal not found message with statistics."""
    print(f"\n❌ Goal '{end}' not reachable from '{start}'")
    print(f"Max depth explored: {max_depth}")
    print(f"Peak memory usage: {max_size} nodes in queue")


def breadth_first_search(
    G: nx.Graph, 
    start: str, 
    end: str
) -> Tuple[Optional[List[str]], List[str], List[Tuple[str, str]], int]:
    """
    Perform Breadth-First Search (BFS) to find a path from start to end node.
    
    BFS explores nodes level by level using a queue (FIFO structure).
    
    Args:
        G: A NetworkX graph
        start: The starting node label
        end: The goal node label
    
    Returns:
        tuple: (path, expanded_nodes, tree_edges, max_depth)
            - path: List of nodes from start to end, or None if no path exists
            - expanded_nodes: List of nodes explored during search
            - tree_edges: List of (parent, child) tuples forming the search tree
            - max_depth: Maximum depth reached during search
    """
    if not _validate_inputs(G, start, end):
        return None, [], [], 0
    
    # ===== YOUR CODE HERE =====
    # TODO: Implement BFS algorithm
    # Hint: You'll need a queue and a way to track visited nodes
    # Hint: Think about what information you need to store for each node
    state = _initialize_search_state()
    from collections import deque

    # Queue holds (node, depth); also keep parent map for path reconstruction
    q = deque()
    q.append((start, 0))
    state['visited'].add(start)
    parent = {start: None}
    peak_size = len(q)

    while q:
        # Show frontier state (nodes + depths) per the helper
        nodes_snapshot = [n for (n, _) in q]
        depths_snapshot = [d for (_, d) in q]
        _print_frontier_state(state['step'], (nodes_snapshot, depths_snapshot), 'BFS')
        state['step'] += 1

        u, depth = q.popleft()
        state['expanded'].append(u)
        state['max_depth'] = max(state['max_depth'], depth)

        if u == end:
            # Reconstruct path from parent pointers
            path = []
            cur = u
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            _print_goal_reached(path, state['max_depth'], peak_size)
            return path, state['expanded'], state['tree_edges'], state['max_depth']

        # Explore neighbors in FIFO order
        for v in G.neighbors(u):
            if v not in state['visited']:
                state['visited'].add(v)
                parent[v] = u
                state['tree_edges'].append((u, v))
                q.append((v, depth + 1))
                peak_size = max(peak_size, len(q))
                        
    
    # ===== END YOUR CODE =====
    
    _print_goal_not_found(end, start, 0, 0)
    return None, [], [], 0


def depth_first_search(
    G: nx.Graph, 
    start: str, 
    end: str
) -> Tuple[Optional[List[str]], List[str], List[Tuple[str, str]], int]:
    """
    Perform Depth-First Search (DFS) to find a path from start to end node.
    
    DFS explores as deep as possible along each branch before backtracking,
    using a stack (LIFO structure).
    
    Args:
        G: A NetworkX graph
        start: The starting node label
        end: The goal node label
    
    Returns:
        tuple: (path, expanded_nodes, tree_edges, max_depth)
            - path: List of nodes from start to end, or None if no path exists
            - expanded_nodes: List of nodes explored during search
            - tree_edges: List of (parent, child) tuples forming the search tree
            - max_depth: Maximum depth reached during search
    """
    if not _validate_inputs(G, start, end):
        return None, [], [], 0
    
    # ===== YOUR CODE HERE =====
    # TODO: Implement DFS algorithm (iterative, not recursive)
    # Hint: Use a stack (LIFO) instead of a queue
    # Hint: Think about how this differs from BFS
    state = _initialize_search_state()

    # Stack holds (node, depth, path for simple-path constraint)
    stack = [(start, 0, [start])]
    visited_for_expanded = set()  # just to avoid duplicating in expanded list
    peak_size = len(stack)

    while stack:
        nodes_snapshot = [n for (n, _, _) in stack]
        depths_snapshot = [d for (_, d, _) in stack]
        _print_frontier_state(state['step'], (nodes_snapshot, depths_snapshot), 'DFS')
        state['step'] += 1

        u, depth, path = stack.pop()
        if u not in visited_for_expanded:
            visited_for_expanded.add(u)
            state['expanded'].append(u)
        state['max_depth'] = max(state['max_depth'], depth)

        if u == end:
            _print_goal_reached(path, state['max_depth'], peak_size)
            # Build tree edges from the found path (nice for visualization)
            # (Optional; the tree_edges also got some entries during pushing below)
            return path, state['expanded'], state['tree_edges'], state['max_depth']

        # Push neighbors (LIFO). Maintain simple paths (no repeated nodes).
        for v in G.neighbors(u):
            if v not in path:
                state['tree_edges'].append((u, v))
                stack.append((v, depth + 1, path + [v]))
                peak_size = max(peak_size, len(stack))
    
    
    
    # ===== END YOUR CODE =====
    
    _print_goal_not_found(end, start, 0, 0)
    return None, [], [], 0


def uniform_cost_search(
    G: nx.Graph, 
    start: str, 
    end: str,
    distance_matrix=None
) -> Tuple[Optional[List[str]], List[str], List[Tuple[str, str]], int, Optional[float]]:
    """
    Perform Uniform Cost Search (UCS) to find the lowest-cost path from start to end.
    
    UCS expands nodes in order of path cost, guaranteeing an optimal solution.
    Uses a priority queue where priority is the cumulative path cost.
    
    Args:
        G: A NetworkX graph with 'weight' attributes on edges
        start: The starting node label
        end: The goal node label
        distance_matrix: Optional numpy array of edge costs (if provided, used instead of edge weights)
    
    Returns:
        tuple: (path, expanded_nodes, tree_edges, max_depth, total_cost)
            - path: List of nodes from start to end, or None if no path exists
            - expanded_nodes: List of nodes explored during search
            - tree_edges: List of (parent, child) tuples forming the search tree
            - max_depth: Maximum depth reached during search
            - total_cost: Cost of the path found, or None if no path exists
    """
    if not _validate_inputs(G, start, end):
        return None, [], [], 0, 0
    
    # ===== YOUR CODE HERE =====
    # TODO: Implement UCS algorithm
    # Hint: Use heapq for the priority queue (heappush, heappop)
    # Hint: Priority should be cumulative path cost
    # Hint: Edge costs come from either distance_matrix or G[node][neighbor]["weight"]
    state = _initialize_search_state()
    import heapq

    # Optional distance matrix support (assume node order = sorted(G.nodes()))
    node_list = sorted(G.nodes())
    node_index = {n: i for i, n in enumerate(node_list)}
    use_matrix = (distance_matrix is not None and
                  distance_matrix.shape == (len(node_list), len(node_list)))

    def edge_cost(a, b):
        if use_matrix and a in node_index and b in node_index:
            return float(distance_matrix[node_index[a], node_index[b]])
        data = G.get_edge_data(a, b, default={})
        return float(data.get('weight', 1.0))

    # Priority queue of (g, node, path)
    pq = []
    heapq.heappush(pq, (0.0, start, [start]))
    best_g = {start: 0.0}
    peak_size = len(pq)

    while pq:
        frontier_info = [(round(g, 4), n) for (g, n, _) in pq]
        _print_frontier_state(state['step'], frontier_info, 'UCS')
        state['step'] += 1

        g, u, path = heapq.heappop(pq)
        state['expanded'].append(u)
        state['max_depth'] = max(state['max_depth'], len(path) - 1)
        peak_size = max(peak_size, len(pq))

        if u == end:
            _print_goal_reached(path, state['max_depth'], peak_size, cost=g)
            # Provide a simple tree made from the solution path
            for a, b in zip(path, path[1:]):
                state['tree_edges'].append((a, b))
            return path, state['expanded'], state['tree_edges'], state['max_depth'], g

        for v in G.neighbors(u):
            if v in path:  # enforce simple paths (no loops)
                continue
            ng = g + edge_cost(u, v)
            if v not in best_g or ng < best_g[v]:
                best_g[v] = ng
                heapq.heappush(pq, (ng, v, path + [v]))
                peak_size = max(peak_size, len(pq))

    
    
    # ===== END YOUR CODE =====
    
    _print_goal_not_found(end, start, 0, 0)
    return None, [], [], 0, None




def hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """Recursive hierarchy pos for tree drawing."""
    pos = {root:(xcenter,vert_loc)}
    children = list(G.neighbors(root))
    if children:
        dx = width/len(children)
        nextx = xcenter - width/2 - dx/2
        for child in children:
            nextx += dx
            pos.update(hierarchy_pos(G,child, width=dx, vert_gap=vert_gap,
                                     vert_loc=vert_loc-vert_gap, xcenter=nextx))
    return pos

def visualize_search_tree(tree_edges, start, end, path, expanded, 
                          title="Search Exploration Tree", 
                          show_distances=False, distance_matrix=None, nodes=None):
    """Visualize a search exploration tree (DFS, BFS, or UCS). Optionally show edge distances/costs."""
    T = nx.DiGraph()
    T.add_edges_from(tree_edges)

    if not T.nodes():
        print("No tree to visualize.")
        return

    pos = hierarchy_pos(T, start)
    colors = {"start": "green", "goal": "red", "path": "orange", "expanded": "yellow"}
    
    # Determine node colors
    node_colors = [colors["start"] if n == start else colors["goal"] if n == end 
                   else colors["path"] if path and n in path else colors["expanded"] 
                   if n in expanded else "lightblue" for n in T.nodes()]

    plt.figure(figsize=(10, 8))
    nx.draw_networkx_edges(T, pos, arrows=True, arrowstyle="-|>", arrowsize=18,
                          min_target_margin=12, connectionstyle="arc3,rad=0.06", 
                          width=1.5, edge_color="dimgray")
    nx.draw_networkx_nodes(T, pos, node_color=node_colors, node_size=700, 
                          edgecolors="black", linewidths=1.2)
    nx.draw_networkx_labels(T, pos, font_weight="bold")

    # Show distances if requested
    if show_distances:
        if distance_matrix is not None and nodes is not None:
            node_index = {node: i for i, node in enumerate(nodes)}
            labels = {(u, v): round(distance_matrix[node_index[u], node_index[v]], 2) 
                     for u, v in T.edges() if u in node_index and v in node_index}
        else:
            labels = nx.get_edge_attributes(T, "weight")
        nx.draw_networkx_edge_labels(T, pos, edge_labels=labels, font_color="blue")

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', label=label,
                             markerfacecolor=color, markeredgecolor='black', markersize=12)
                      for label, color in [('Start', colors["start"]), ('Goal', colors["goal"]),
                                          ('On solution path', colors["path"]), ('Expanded', colors["expanded"])]]
    plt.legend(handles=legend_elements, loc="upper right", frameon=True, title="Legend")

    plt.title(title, fontsize=14, fontweight="bold")
    plt.axis('off')
    plt.tight_layout()
    plt.show()


# =============================================================================
# UNIT TESTS FOR SEARCH ALGORITHMS
# =============================================================================

class TestSearchAlgorithms(unittest.TestCase):
    """Starter tests: one placeholder per algorithm. Students must implement."""

    def setUp(self):
        """Set up any graphs needed for tests.
        Hints:
        - Create a small unweighted graph for BFS/DFS.
        - Create a small weighted graph for UCS (use 'weight' attributes).
        - Consider adding a disconnected graph for later tests you write.
        """
        # TODO: Initialize graphs like: (just as examples)
        # self.graph = nx.Graph()
        # self.graph.add_edges_from([...])
        # self.weighted_graph = nx.Graph()
        # self.weighted_graph.add_edge('A', 'B', weight=1)
        pass

    def tearDown(self):
        """Optional cleanup."""
        pass

    def suppress_output(self):
        """Use this to silence prints while testing."""
        return SuppressOutput()

    # ==================== BFS Starter ====================

    def test_bfs_reaches_goal(self):
        """BFS: ensure a path from start to goal is found on an unweighted graph.
        Hints:
        - Call breadth_first_search on a small graph where a path exists.
        - Assert that a path is returned and it starts/ends at the expected nodes.
        - Optionally, later add an assertion that the path length equals the shortest distance.
        """
        # TODO: Implement the test body
        pass

    # ==================== DFS Starter ====================

    def test_dfs_finds_a_path(self):
        """DFS: ensure some valid path is found (not necessarily shortest).
        Hints:
        - Call depth_first_search on the same unweighted graph.
        - Assert that a path exists and each consecutive pair forms an edge in the graph.
        - Later, add tests demonstrating deeper-first exploration and unreachable cases.
        """
        # TODO: Implement the test body
        pass

    # ==================== UCS Starter ====================

    def test_ucs_optimal_cost(self):
        """UCS: ensure the returned path cost is optimal on a weighted graph.
        Hints:
        - Build a small weighted graph where the cheapest route is not the shortest by hops.
        - Call uniform_cost_search and assert the total cost equals the known optimum.
        - Later, add tests that use a distance_matrix, invalid inputs, and tie-breaking.
        """
        # TODO: Implement the test body
        pass


class SuppressOutput:
    """Context manager to suppress stdout."""
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = StringIO()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout


def run_search_tests():
    """Run all search algorithm unit tests."""
    print("=" * 60)
    print("RUNNING SEARCH ALGORITHM UNIT TESTS")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSearchAlgorithms)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ ALL SEARCH ALGORITHM TESTS PASSED!")
        print(f"Ran {result.testsRun} tests successfully")
    else:
        print("❌ SOME SEARCH ALGORITHM TESTS FAILED!")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        # Print failure details
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    print("=" * 60)
    return result.wasSuccessful()


if __name__ == "__main__":
    # Only run tests when script is executed directly
    success = run_search_tests()
    sys.exit(0 if success else 1)
