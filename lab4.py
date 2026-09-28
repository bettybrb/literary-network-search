import heapq
import random
import math
import networkx as nx
import numpy as np
from collections import deque, Counter
import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO


# ----------------------------------------
# Shared validation and initialization
# ----------------------------------------
def _check_nodes(G, s, g):
    """Validate that start and goal nodes exist in the graph."""
    if s not in G or g not in G:
        print("Invalid start or goal node.")
        return False
    return True


def _init_state():
    """Initialize common search state variables."""
    return {
        'visited': set(),
        'expanded': [],
        'tree': [],
        'depth': 0,
        'step': 0
    }


def _edge_cost(G, u, v, dist=None, idx=None):
    """Get the cost of an edge between two nodes."""
    if dist is not None:
        return float(dist[idx[u], idx[v]])
    return float(G[u][v].get("weight", 1))


def _report_goal(path, depth, maxq, cost=None):
    """Print goal reached message with statistics."""
    print("\nGOAL REACHED!")
    print(f"Path: {' → '.join(path)}")
    if cost is not None:
        print(f"Cost=${cost:.3f}")
    print(f"Length={len(path)-1}  Depth={depth}  Max frontier={maxq}")


def _report_fail(start, end, depth, maxq):
    """Print goal not found message with statistics."""
    print(f"\n❌ '{end}' not reachable from '{start}' (depth={depth}, max frontier={maxq})")


# ----------------------------------------
# Shared-neighbor heuristic (Starter Code)
# ----------------------------------------
def build_neighbor_map(nodes, adj):
    """
    Build a data structure (e.g., a dictionary) representing shared neighbor relationships
    between nodes in a graph.

    This function will be used to support a heuristic calculation based on how many
    neighbors two nodes have in common. Each node should be associated with other nodes
    it connects to, along with a count or weight reflecting how frequently that connection
    appears in the adjacency data.

    Parameters
    ----------
    nodes : iterable
        The collection of unique nodes (e.g., words) in the graph.
    adj : dict
        The adjacency information, typically a dictionary where keys are (source, target)
        pairs and values represent the number of transitions or edge weights.

    Returns
    -------
    neighbor_map : dict
        A nested dictionary structure mapping each node to its neighboring nodes and
        their corresponding counts or weights. For example:
            {
                'word1': {'word2': 3, 'word5': 1},
                'word2': {'word1': 3, 'word3': 2},
                ...
            }

    Notes
    -----
    - This structure will be used later by the heuristic function `h_shared`
      to estimate the similarity or "closeness" between two nodes.
    - You may assume that `nodes` contains all unique vertices appearing in `adj`.
    """

    # --- STUDENT CODE STARTS HERE ---
    neighbor_map = {n: {} for n in nodes}
    # accumulate counts for both (u,v) and (v,u) into u<->v
    for (u, v), c in adj.items():
        if u not in neighbor_map or v not in neighbor_map:
            continue
        neighbor_map[u][v] = neighbor_map[u].get(v, 0) + c
        neighbor_map[v][u] = neighbor_map[v].get(u, 0) + c
    return neighbor_map
    # --- STUDENT CODE ENDS HERE ---


def h_shared(a, b, neighbor_map, scale=1.0):
    """
    Compute a heuristic estimate of distance between two nodes based on their
    shared neighbors.

    The intuition is that if two nodes share many neighbors, they are likely to be
    "closer" in the graph structure, and thus the heuristic value should be smaller.
    If they share few or no neighbors, the heuristic should be larger.

    Parameters
    ----------
    a, b : hashable
        Node identifiers (e.g., strings representing words) between which the heuristic
        will be calculated.
    neighbor_map : dict
        The shared neighbor structure produced by `build_neighbor_map`.
    scale : float, optional
        A scaling factor to adjust the magnitude of the heuristic (default = 1.0).

    Returns
    -------
    h : float
        A non-negative heuristic value representing the estimated distance between
        `a` and `b`. Smaller values indicate higher similarity or connectivity.

    Notes
    -----
    - This heuristic can be used in graph search algorithms such as A* or best-first
      search to guide exploration.
    - You should ensure the heuristic is symmetric and non-negative.
    """

    # --- STUDENT CODE STARTS HERE ---
    if a not in neighbor_map or b not in neighbor_map:
        return float(scale)  # fallback small finite value
    na = neighbor_map[a]
    nb = neighbor_map[b]
    if not na or not nb:
        return float(scale)
    shared = set(na.keys()).intersection(nb.keys())
    shared_strength = sum(min(na[x], nb[x]) for x in shared)
    # larger shared_strength ⇒ closer ⇒ smaller heuristic
    return float(scale) * (1.0 / (1.0 + float(shared_strength)))
    # --- STUDENT CODE ENDS HERE ---


# ----------------------------------------
# Greedy Best-First Search (Starter)
# ----------------------------------------
def greedy_search(G, start, end, adj=None, nodes=None, dist=None, verbose=True, scale=1.0):
    """
    Perform Greedy Best-First Search on a given graph.

    This search algorithm expands the node that appears **closest to the goal** based solely
    on the heuristic function `h(n)`. It ignores path cost (unlike A*), so it is not guaranteed
    to find an optimal path.

    The algorithm uses a priority queue (min-heap) where each node is prioritized by its
    heuristic value relative to the target, and expands nodes in increasing order of `h(n)`.

    Parameters
    ----------
    G : networkx.Graph
        The graph on which to run the search.
    start : node
        The starting node.
    end : node
        The target or goal node.
    adj : dict, optional
        Precomputed adjacency counts used to build the heuristic neighbor map.
    nodes : list, optional
        List of all graph nodes (used for matrix indexing if needed).
    dist : ndarray, optional
        Distance or weight matrix, used only for reference (not required).
    verbose : bool, default=True
        If True, prints detailed progress of the algorithm.
    scale : float, default=1.0
        Scaling parameter for the heuristic.

    Returns
    -------
    path : list
        A list of nodes forming the path from `start` to `end`, if found.
    expanded : list
        The order in which nodes were expanded.
    tree : list
        The list of edges forming the exploration tree.
    depth : int
        The maximum depth reached during the search.

    Notes
    -----
    - Greedy search is fast but may get stuck in local minima.
    - You should use `heapq` with tuples (heuristic_value, tie_breaker, node, path).
    - Make sure to track visited nodes and store expansion order for visualization.
    """

    # --- STUDENT CODE STARTS HERE ---
    # Initialize necessary structures and implement Greedy Best-First logic
    if not _check_nodes(G, start, end):
        return None, [], [], 0

    # Build heuristic structure once
    if nodes is None:
        nodes = list(G.nodes())
    if adj is None:
        # default: derive a simple adjacency count (1 for each edge)
        adj = { (u,v):1 for u,v in G.edges() }
        adj.update({ (v,u):1 for u,v in G.edges() })
    nmap = build_neighbor_map(nodes, adj)

    visited = set()
    expanded = []
    tree = []
    depth_max = 0
    tie = 0

    # priority on h(n,end)
    pq = []
    h0 = h_shared(start, end, nmap, scale=scale)
    heapq.heappush(pq, (h0, tie, start, [start], 0))
    tie += 1
    peak = 1

    while pq:
        hval, _, u, path, depth = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        expanded.append(u)
        depth_max = max(depth_max, depth)
        if verbose:
            print(f"[Greedy] expand={u} h={hval:.4f} depth={depth} path_len={len(path)}")

        if u == end:
            _report_goal(path, depth_max, peak, cost=None)
            return path, expanded, tree, depth_max

        for v in G.neighbors(u):
            if v in visited:
                continue
            tree.append((u, v))
            hv = h_shared(v, end, nmap, scale=scale)
            heapq.heappush(pq, (hv, tie, v, path + [v], depth + 1))
            tie += 1
            peak = max(peak, len(pq))

    _report_fail(start, end, depth_max, peak)
    return None, expanded, tree, depth_max
    # --- STUDENT CODE ENDS HERE ---


# ----------------------------------------
# A* Search (Starter)
# ----------------------------------------
def astar_search(G, start, end, adj=None, nodes=None, dist=None, verbose=True, scale=1.0):
    """
    Implement A* Search using the shared-neighbor heuristic.

    A* uses both actual costs (g-values) and heuristic estimates (h-values) to guide the search.
    It prioritizes nodes by their **total estimated cost** f(n) = g(n) + h(n).

    Parameters
    ----------
    G : networkx.Graph
        The graph on which to run A* search.
    start : node
        Starting node.
    end : node
        Goal node.
    adj : dict, optional
        Adjacency count map used to generate heuristics.
    nodes : list, optional
        List of graph nodes for matrix indexing.
    dist : ndarray, optional
        Optional distance matrix of edge weights.
    verbose : bool, default=True
        Whether to print detailed iteration progress.
    scale : float, default=1.0
        Scaling factor for heuristic magnitude.

    Returns
    -------
    path : list
        The sequence of nodes from start to end, if found.
    expanded : list
        The order of node expansions.
    tree : list
        The set of tree edges (for visualization).
    depth : int
        The maximum expansion depth.
    total_cost : float
        The total cost of the path found, or infinity if no path exists.

    Notes
    -----
    - Maintain a priority queue with tuples (f_value, tie_breaker, node, path, g_value).
    - Use a dictionary to track the best known g-value for each node.
    - Only expand nodes if you’ve found a better g(n).
    - Be sure to print or log progress if `verbose` is True for instructional output.
    """

    # --- STUDENT CODE STARTS HERE ---
    # Initialize all required data structures and implement A* logic
    if not _check_nodes(G, start, end):
        return None, [], [], 0, float("inf")

    # Node indexing if a distance matrix is provided
    if nodes is None:
        nodes = list(G.nodes())
    idx = {n: i for i, n in enumerate(nodes)} if dist is not None else None

    # Heuristic prep
    if adj is None:
        adj = { (u,v):1 for u,v in G.edges() }
        adj.update({ (v,u):1 for u,v in G.edges() })
    nmap = build_neighbor_map(nodes, adj)

    expanded = []
    tree = []
    depth_max = 0
    tie = 0
    peak = 0

    # g-best
    gbest = {start: 0.0}

    # PQ: (f, tie, node, path, g)
    h0 = h_shared(start, end, nmap, scale=scale)
    pq = []
    heapq.heappush(pq, (h0, tie, start, [start], 0.0))
    tie += 1
    peak = 1

    while pq:
        f, _, u, path, g = heapq.heappop(pq)

        # Skip stale entries
        if g > gbest.get(u, float("inf")):
            continue

        expanded.append(u)
        depth_max = max(depth_max, len(path) - 1)
        if verbose:
            print(f"[A*] expand={u} g={g:.3f} h={f-g:.3f} f={f:.3f} depth={len(path)-1}")

        if u == end:
            _report_goal(path, depth_max, peak, cost=g)
            # tree edges from final path (optional visualization)
            if not tree:
                for a, b in zip(path, path[1:]):
                    tree.append((a, b))
            return path, expanded, tree, depth_max, g

        for v in G.neighbors(u):
            if v in path:  # ensure simple path (no repeats)
                continue
            step = _edge_cost(G, u, v, dist=dist, idx=idx)
            ng = g + step
            if ng < gbest.get(v, float("inf")):
                gbest[v] = ng
                hv = h_shared(v, end, nmap, scale=scale)
                fv = ng + hv
                tree.append((u, v))
                heapq.heappush(pq, (fv, tie, v, path + [v], ng))
                tie += 1
                peak = max(peak, len(pq))

    _report_fail(start, end, depth_max, peak)
    return None, expanded, tree, depth_max, float("inf")
    # --- STUDENT CODE ENDS HERE ---


# ----------------------------------------
# Simulated Annealing (Starter)
# ----------------------------------------
def simulated_annealing(G, path, dist, nodes, max_iter=1000, T0=100.0, alpha=0.95, verbose=True):
    """
    Apply Simulated Annealing to **maximize** the total path cost in a graph.

    This metaheuristic explores variations of a given path, occasionally accepting worse
    solutions to escape local optima. The acceptance probability decreases over time
    as the temperature cools.

    Algorithm Overview
    ------------------
    1. **Initialization:** start from an initial valid path.
    2. **Neighbor Generation:** randomly modify the current path:
         - Insert a node between two existing nodes,
         - Remove a middle node, or
         - Replace a node with a neighbor.
    3. **Cost Evaluation:** compute the total path cost using the distance matrix.
    4. **Acceptance Criterion:** 
         - Always accept better paths.
         - Sometimes accept worse paths with probability exp(Δ / T).
    5. **Cooling Schedule:** multiply T by α each iteration.

    Parameters
    ----------
    G : networkx.Graph
        The underlying graph structure.
    path : list
        Initial valid path (list of nodes).
    dist : ndarray
        Distance matrix giving pairwise edge costs.
    nodes : list
        Ordered list of all nodes corresponding to matrix indices.
    max_iter : int, default=1000
        Number of iterations.
    T0 : float, default=100.0
        Initial temperature controlling acceptance of bad solutions.
    alpha : float, default=0.95
        Cooling rate (0 < alpha < 1).
    verbose : bool, default=True
        If True, prints progress information.

    Returns
    -------
    best_path : list
        The best (highest-cost) path found.
    best_cost : float
        The total cost of that path.
    history : list of tuples
        (iteration_number, cost_value) pairs for analysis.

    Notes
    -----
    - Ensure paths remain valid (edges exist between consecutive nodes).
    - Use `nx.common_neighbors` for insertion logic.
    - Be mindful of temperature cooling and random acceptance.
    """

    # --- STUDENT CODE STARTS HERE ---
    # Implement the simulated annealing loop here
    node_index = {n: i for i, n in enumerate(nodes)}

    def path_cost(p):
        total = 0.0
        for a, b in zip(p, p[1:]):
            if a not in node_index or b not in node_index:
                return -float("inf")  # invalid
            ia, ib = node_index[a], node_index[b]
            # ensure edge exists in graph too
            if not G.has_edge(a, b) and not G.has_edge(b, a):
                return -float("inf")
            total += float(dist[ia, ib])
        return total

    def valid_path(p):
        # simple path with existing edges
        if len(p) != len(set(p)):
            return False
        for a, b in zip(p, p[1:]):
            if not (G.has_edge(a, b) or G.has_edge(b, a)):
                return False
        return True

    def propose_neighbor(p):
        """Three move types: insert, remove, or swap middle nodes."""
        if len(p) < 2:
            return p[:]  # trivial
        move = random.choice(["insert", "remove", "swap"])
        q = p[:]

        if move == "swap" and len(q) >= 4:
            i = random.randint(1, len(q) - 2)
            j = random.randint(1, len(q) - 2)
            if i != j:
                q[i], q[j] = q[j], q[i]
            return q

        if move == "remove" and len(q) > 2:
            k = random.randint(1, len(q) - 2)  # remove a middle node
            del q[k]
            return q

        if move == "insert":
            # Try inserting a common neighbor between consecutive nodes
            i = random.randint(0, len(q) - 2)
            u, v = q[i], q[i+1]
            # gather candidate mid nodes that connect u->mid->v
            candidates = []
            for mid in G.neighbors(u):
                if mid in q:  # keep path simple
                    continue
                if G.has_edge(mid, v) or G.has_edge(v, mid):
                    candidates.append(mid)
            if candidates:
                mid = random.choice(candidates)
                q = q[:i+1] + [mid] + q[i+1:]
            return q

        return q

    # Ensure initial path is valid
    if not valid_path(path):
        if verbose:
            print("[SA] Initial path invalid; aborting.")
        return path, -float("inf"), []

    current = path[:]
    best = path[:]
    cur_cost = path_cost(current)
    best_cost = cur_cost
    T = float(T0)
    history = [(0, cur_cost)]

    if verbose:
        print(f"[SA] start cost={cur_cost:.3f}")

    for it in range(1, max_iter + 1):
        cand = propose_neighbor(current)
        if not valid_path(cand):
            # skip invalid move; try again next iteration
            T *= alpha
            history.append((it, cur_cost))
            continue

        cand_cost = path_cost(cand)
        delta = cand_cost - cur_cost  # we MAXIMIZE

        if delta > 0 or random.random() < math.exp(delta / max(T, 1e-9)):
            current = cand
            cur_cost = cand_cost

            if cur_cost > best_cost:
                best = current[:]
                best_cost = cur_cost

        if verbose and it % max(1, max_iter // 10) == 0:
            print(f"[SA] it={it:4d} T={T:.4f} cur={cur_cost:.3f} best={best_cost:.3f}")

        T *= alpha
        history.append((it, cur_cost))

    return best, best_cost, history
    # --- STUDENT CODE ENDS HERE ---




class TestSearchAlgorithms(unittest.TestCase):
    """
    Write your own unit tests for the search algorithms.

    - Use the unittest framework.    
    - You decide what to test and how to structure your assertions.
    - Keep tests small, clear, and focused.
    """

    # --- STUDENT TESTS START HERE ---
    def setUp(self):
        # Simple graph:
        # A - B - C - D
        #  \       /
        #    \ E /
        self.G = nx.Graph()
        self.G.add_edges_from([('A','B'),('B','C'),('C','D'),('A','E'),('E','D')])

        # Nodes/adj for heuristic
        self.nodes = list(self.G.nodes())
        # treat each undirected edge as two directed unit-count edges
        self.adj = {(u,v):1 for u,v in self.G.edges()}
        self.adj.update({(v,u):1 for u,v in self.G.edges()})

        # Distance matrix: unit weights by default
        self.idx = {n:i for i,n in enumerate(self.nodes)}
        n = len(self.nodes)
        self.dist = np.ones((n,n), dtype=float)
        np.fill_diagonal(self.dist, 0.0)

    def test_greedy_finds_a_path(self):
        path, expanded, tree, depth = greedy_search(
            self.G, 'A', 'D', adj=self.adj, nodes=self.nodes, dist=self.dist, verbose=False
        )
        self.assertIsNotNone(path)
        self.assertEqual(path[0], 'A')
        self.assertEqual(path[-1], 'D')
        for u, v in zip(path, path[1:]):
            self.assertTrue(self.G.has_edge(u, v))

    def test_astar_cost_and_path(self):
        path, expanded, tree, depth, cost = astar_search(
            self.G, 'A', 'D', adj=self.adj, nodes=self.nodes, dist=self.dist, verbose=False
        )
        self.assertIsNotNone(path)
        # In this graph, short paths are A-E-D or A-B-C-D (2 vs 3 edges).
        self.assertIn(len(path)-1, (2, 3))
        # with unit dist, cost should equal hops
        self.assertAlmostEqual(cost, float(len(path)-1), places=6)

    def test_sa_runs(self):
        # seed a valid path
        init = ['A','E','D']
        best, best_cost, history = simulated_annealing(
            self.G, init, self.dist, self.nodes, max_iter=100, T0=5.0, alpha=0.9, verbose=False
        )
        self.assertIsInstance(best, list)
        self.assertTrue(len(history) > 0)
    # --- STUDENT TESTS END HERE ---


def run_tests():
    """Run all unit tests."""
    print("=" * 70)
    print("RUNNING UNIT TESTS FOR SEARCH ALGORITHMS")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSearchAlgorithms)
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print(f"Total tests run: {result.testsRun}")
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
