"""
CW1: Networks and Pathfinding on Literary Text Networks

This module implements graph search algorithms on a text network derived from 
George Orwell's Nineteen Eighty-Four. Each unique word is represented as a node 
and each transition between consecutive words forms a directed edge.

Author: Alzbeta Rehakova
Date: October 2025
"""

# =============================================================================
# IMPORTS
# =============================================================================
from lab2 import *
from lab3 import *
from lab4 import * 
import heapq, math
import math, heapq
import re, heapq, math

# TASK 1: LONGEST PATH [5 marks]
def print_long_path(text_network, start_word="water", end_word="end"):
    """Find a long path between given nodes (no external libs)."""
    if not isinstance(text_network, dict) or "graph" not in text_network:
        return []
    G = text_network["graph"]
    if not G or len(G) == 0 or not start_word or not end_word:
        return []

    if start_word not in G or end_word not in G:
        print(" Invalid start or end node.")
        return []

    print(f" Finding path from {start_word} → {end_word}")

    from io import StringIO
    import sys

    # Silent wrapper for lab search functions
    def silent_search(fn, *args):
        from io import StringIO
        import sys
        old = sys.stdout
        sys.stdout = StringIO()
        try:
            return fn(*args)
        finally:
            sys.stdout = old

    path, *_ = silent_search(depth_first_search, G, start_word, end_word)
    if not path:
        path, *_ = silent_search(breadth_first_search, G, start_word, end_word)

    if not path:
        print(f" No path found between {start_word} and {end_word}")
        return []

    print(f" Found path length: {len(path) - 1} edges")
    return path
    
# =============================================================================
# TASK 2: LONGEST QUOTE [5 marks]
# =============================================================================

def print_long_quote(text_network, start_word="was", end_word="see"):
    tokens = text_network.get("original_tokens", [])
    rare_tokens = text_network.get("rare_tokens", set())   

    if not tokens or start_word not in tokens or end_word not in tokens:
        print(" Invalid tokens or words not found.")
        return []

    best_quote = []
    n = len(tokens)
    for i in range(n):
        if tokens[i] == start_word:
            seen = set()
            for j in range(i, n):
                word = tokens[j]
                if word in seen or word in rare_tokens:   
                    break
                seen.add(word)
                if word == end_word:
                    quote = tokens[i:j + 1]
                    if len(quote) > len(best_quote):
                        best_quote = quote
                    break

    if best_quote:
        print(f" Longest quote found ({len(best_quote)} words): {best_quote[:5]} ... {best_quote[-5:]}")
    else:
        print(f" No quotes found between '{start_word}' and '{end_word}'.")
    return best_quote



# =============================================================================
# TASK 3: MOST EXPENSIVE PATH [5 marks]
# =============================================================================

def print_expensive_path(text_network, start_word="century", end_word="end"):
    """Find the most expensive path (highest cumulative cost) using max-priority expansion."""
    G = text_network["graph"]
    dist, nodes = text_network["distance_matrix"], text_network["nodes"]
    idx = {w: i for i, w in enumerate(nodes)}

    if start_word not in G or end_word not in G:
        print(" Invalid start or end node.")
        return [], 0.0

    print(f"\n Searching most expensive path: {start_word} → {end_word}\n")

    pq = [(-0.0, [start_word])]
    best_cost, best_path = {start_word: 0.0}, []
    top_score = 0.0

    while pq:
        cost, path = heapq.heappop(pq)
        node, cost = path[-1], -cost

        if node == end_word:
            best_path, top_score = path, cost
            print(" Reached end node.")
            break

        for nbr in G.neighbors(node):
            if nbr in path:  # no revisits
                continue
            i, j = idx[node], idx[nbr]
            edge = dist[i, j] * (1 + 1 / (len(G[nbr]) + 1e-9))
            new_cost = cost + edge
            if new_cost > best_cost.get(nbr, -float("inf")):
                best_cost[nbr] = new_cost
                heapq.heappush(pq, (-new_cost, path + [nbr]))
                if new_cost > top_score:
                    best_path, top_score = path + [nbr], new_cost

    print(f" Most expensive path found ({len(best_path)} words)")
    print(f" Total cost: {top_score:.2f}")
    print("Preview:", " → ".join(best_path[:25]), "...")
    return best_path, top_score
# =============================================================================
# TASK 4: MOST EXPENSIVE QUOTE [5 marks]
# =============================================================================
def print_expensive_quote(
    text_network, start_word="was", end_word="whether"):
    """
    Return the most expensive literal quote in the text network.
    Searches only among connected nodes (not full text scan).
    """
    G = text_network["graph"]
    dist = text_network["distance_matrix"]
    nodes = text_network["nodes"]
    idx = {w: i for i, w in enumerate(nodes)}

    def edge_cost(a, b):
        if not G.has_edge(a, b): return 0.0
        i, j = idx[a], idx[b]
        return dist[i, j] if dist[i, j] > 0 else 0.0

    placeholders = (
        "was",
        "whether"
    )
    global_search = (start_word in placeholders or end_word in placeholders)

    best_path, best_cost = [], 0.0

    def explore_path(start):
        """Find best contiguous chain from a given start node."""
        best_local_path, best_local_cost = [start], 0.0
        visited = {start}
        frontier = [(0.0, [start])]

        while frontier:
            cost, path = heapq.heappop(frontier)
            cur = path[-1]
            for nbr in G.neighbors(cur):
                if nbr in visited:  # no repeats
                    continue
                c = edge_cost(cur, nbr)
                if c <= 0:
                    continue
                new_cost = -cost + c
                new_path = path + [nbr]
                heapq.heappush(frontier, (-new_cost, new_path))
                visited.add(nbr)
                if new_cost > best_local_cost:
                    best_local_path, best_local_cost = new_path, new_cost
        return best_local_path, best_local_cost

    if global_search:
        # try all nodes as potential quote starts
        for s in nodes:
            path, cost = explore_path(s)
            if cost > best_cost:
                best_path, best_cost = path, cost
    else:
        # targeted mode: fixed start and end words
        if start_word not in G or end_word not in G:
            print(" Start or end word not in graph.")
            return [], 0.0
        path, cost = explore_path(start_word)
        # trim if we reached end_word
        if end_word in path:
            path = path[: path.index(end_word) + 1]
        best_path, best_cost = path, cost

    
    return best_path, best_cost

# =============================================================================
# TASK 5: HEURISTIC SEARCH [30 marks total]
# ==============================================
# =============================================================================
# TASK 5a: HEURISTIC SENTENCE COMPLETION (final lightweight version)
# =============================================================================

def complete_sentence(G, prompt="please believe my eyes <CONTENT>."):
    """Heuristic sentence completion using A* search with linguistic, morphological and graph heuristics."""
    if isinstance(G, dict) and "graph" in G:
        G = G["graph"]

    # --- Parse prompt ---
    words = prompt.replace("<CONTENT>", "<CONTENT> ").split()
    if "<CONTENT>" not in words:
        raise ValueError("Prompt must contain <CONTENT>")
    i = words.index("<CONTENT>")
    pre, suf = words[:i], words[i + 1:]
    start, goal = pre[-1] if pre else "<START>", suf[0] if suf else "<END>"

    COMMON_ADVERBS = {"suddenly", "again", "then", "very", "so", "now", "just"}

    # --- POS & Morphology ---
    def classify(w):
        w = w.lower().strip(".,;!?")
        if w.endswith(("ing","ed","en","ify","ise","ize")) or w.startswith(("re","be")): return "verb"
        if w.endswith("ly"): return "adv"
        if w.endswith(("ous","ful","less","ive","al","ic")): return "adj"
        if w.endswith(("tion","ment","ness","ity","age","ship","ism")): return "noun"
        return "other"

    def soft_end(w):
        return (classify(w) in {"adv","adj","verb"} and w.lower() not in COMMON_ADVERBS)

    # --- Anchors for unseen nodes ---
    anchors = {
        "verb":{"see","look","find","say","know","think","believe","travel","go","come","make"},
        "noun":{"truth","way","thing","friend","man","woman","city","world","day","light","face","life"},
        "adj":{"good","bad","big","small","dark","bright","new","old","real"},
        "adv":{"quickly","slowly","quietly","again","soon","already"},
    }

    def attach_by_type(node,t):
        if node not in G: G.add_node(node)
        related=set(anchors.get(t,set()))|{"the","a","to","and","of","is","in"}
        for a in related:
            if a in G.nodes():
                G.add_edge(node,a,weight=0.05)
                G.add_edge(a,node,weight=0.05)

    def find_similar(word):
        n=word.lower().strip(".,;!?")
        for node in G.nodes():
            if n==node or n in node or node in n: return node
        return None

    # --- Frequency-weighted morphological replacement ---
    def find_replacement_node(word):
        cls=classify(word); suf=word[-3:].lower()
        best,best_freq=None,-1
        for node in G.nodes():
            if classify(node)!=cls: continue
            if node.endswith(suf) or (word.endswith("ing") and node.endswith("ing")):
                freq=sum(G[node][n].get("weight",0) for n in G.neighbors(node))
                if freq>best_freq: best,best_freq=node,freq
        if not best:
            for node in G.nodes():
                if classify(node)==cls:
                    freq=sum(G[node][n].get("weight",0) for n in G.neighbors(node))
                    if freq>best_freq: best,best_freq=node,freq
        return best

    def fallback_to_previous(node,path):
        for prev in reversed(path[:-1]):
            if prev in G: return prev
        return None

    # --- Repair missing nodes ---
    for node in [start,goal]:
        if node not in G:
            sim=find_similar(node)
            if sim:
                if node==start: start=sim
                if node==goal: goal=sim
            else:
                repl=find_replacement_node(node)
                if repl:
                    if node==start: start=repl
                    if node==goal: goal=repl
                else:
                    attach_by_type(node,classify(node))

    # --- Heuristics ---
    def cost(a,b):
        """Edge cost factoring in transition strength and node specificity."""
        w = G[a][b].get("weight", 1e-6)
        deg = len(list(G.neighbors(b))) if b in G else 1
        c = -1.5 * math.log(w + 1e-9)
        # Penalize generic high-degree nodes
        c += math.log(deg + 1) * 0.8
        if b == "." or b.lower() in COMMON_ADVERBS:
            c += 3
        return c

    def ngram(a,b,c):
        w1 = G[a][b].get("weight",1e-6) if G.has_edge(a,b) else 1e-6
        w2 = G[b][c].get("weight",1e-6) if G.has_edge(b,c) else 1e-6
        return -math.log(w1*w2 + 1e-9)

    def lexical_relatedness(a,b):
        sa,sb=set(a.lower()),set(b.lower())
        sim=len(sa & sb)/max(1,len(sa | sb))
        return -1.5*sim

    def relation_score(a,b):
        """Reward natural phrase shapes."""
        ta,tb=classify(a),classify(b)
        if (ta,tb) in {("verb","adv"),("verb","noun"),("adj","noun"),("noun","verb")}: return -1.0
        if a in {"is","was","were","be"} and tb=="adj": return -2.0  # prefer adj after copula
        if a in {"is","was","were","be"} and tb=="noun": return 1.5   # penalize noun after copula
        if ta=="noun" and tb=="noun": return 1.0
        if ta==tb: return 0.3
        return 0.0

    def grammar_compatibility(a,b):
        ta,tb=classify(a),classify(b)
        if a in {"is","was","were","be"} and tb=="verb": return 2.5
        if ta=="verb" and tb=="verb": return 1.5
        if ta=="verb" and tb in {"adj","noun"}: return -0.7
        if ta=="adj" and tb=="noun": return -0.5
        if ta=="adj" and tb=="adj": return 0.3
        return 0.0

    def context_affinity(prev,nxt):
        score=0
        if nxt.lower() in {"truth","light","face","eyes","way"} and classify(prev)=="verb": score-=1
        if nxt.lower() in {"soon","again","already"} and classify(prev)=="verb": score-=1
        if classify(prev)==classify(nxt): score+=0.5
        return score

    # --- A* Search ---
    frontier=[(0,[start])]
    best,best_cost=None,float("inf")

    while frontier:
        s,path=heapq.heappop(frontier)
        cur=path[-1]

        # softer adaptive stopping rule
        if len(path)>2 and (cur==goal or soft_end(cur) or len(path)>=8 or s>best_cost+4):
            if s<best_cost:
                best,best_cost=path,s
            if soft_end(cur): break
            continue

        neigh=list(G.neighbors(cur)) if cur in G else []
        if not neigh:
            repl=find_replacement_node(cur)
            if repl and repl in G:
                neigh=list(G.neighbors(repl))
            else:
                prev=fallback_to_previous(cur,path)
                neigh=list(G.neighbors(prev)) if prev else []

        for nxt in neigh:
            if nxt in path or nxt in {",",";","<RARE>"}: continue
            if nxt=="." and len(path)<=3: continue
            g = (s + cost(cur,nxt)
                   + relation_score(cur,nxt)
                   + lexical_relatedness(cur,nxt)
                   + grammar_compatibility(cur,nxt)
                   + context_affinity(cur,nxt))
            h = ngram(path[-2],cur,nxt) if len(path)>1 else 0
            heapq.heappush(frontier,(g+h,path+[nxt]))

    # --- Reconstruct final sentence ---
    content = best[1:-1] if best and goal in best else (best[1:] if best else [])
    if not any(classify(c) in {"verb","noun","adj"} for c in content):
        return pre + suf
    sentence = [w for w in pre + content + suf if w not in {".",",",";","!","?"}]
    return sentence
# =============================================================================
# TASK 5b: HEURISTIC SENTENCE STARTING 
# =============================================================================

def start_sentence(G, prompt="two <CONTENT> can ask for a solution."):
    """A* search for a contextually plausible word to fill <CONTENT>, using only graph and morphology."""
    if isinstance(G, dict) and "graph" in G:
        G = G["graph"]

    # --- Parse input ---
    words = prompt.replace("<CONTENT>", "<CONTENT> ").split()
    if "<CONTENT>" not in words:
        raise ValueError("Prompt must contain <CONTENT>")
    i = words.index("<CONTENT>")
    pre, suf = words[:i], words[i + 1:]
    goal = suf[0] if suf else "<END>"
    start = pre[-1] if pre else "<START>"

    # --- Morphology / classification ---
    def classify(w):
        w = w.lower().strip(".,;!?")
        if w.endswith(("ing","ed","en")) or w.startswith(("re","be")): return "verb"
        if w.endswith("ly"): return "adv"
        if w.endswith(("ous","ful","less","ive","al","ic")): return "adj"
        if len(w) > 2: return "noun"
        return "other"

    # --- Heuristic cost functions ---
    def edge_cost(a, b):
        """Reward strong, low-degree edges."""
        if not G.has_edge(a, b): return 4.0
        w = G[a][b].get("weight", 1e-6)
        deg = len(G[b]) if b in G else 1
        return -math.log(w + 1e-9) + 0.6 * math.log(deg + 1)

    def relation(a, b):
        """Encourage coherent morphological transitions."""
        ta, tb = classify(a), classify(b)
        score = 0
        if ta == tb: score -= 0.2
        if (ta, tb) in {("noun","verb"),("adj","noun")}: score -= 0.4
        if (ta, tb) == ("det","noun"): score -= 0.5
        return score

    def lexical_penalty(w):
        """Discourage malformed tokens (apostrophes, RAREs, symbols)."""
        if re.search(r"[^a-zA-Z]", w): return 1.5
        if "<" in w or len(w) <= 2: return 1.0
        return 0.0

    def next_candidates(node, k=6):
        """Rank next nodes purely by graph connectivity (weight/degree ratio)."""
        if node not in G: return []
        neigh = list(G.neighbors(node))
        return sorted(
            neigh,
            key=lambda n: G[node][n].get("weight", 1e-6) / (len(G[n]) + 1e-3),
            reverse=True
        )[:k]

    # --- A* Search ---
    frontier = [(0.0, [start])]
    best_path, best_score = None, float("inf")

    while frontier:
        s, path = heapq.heappop(frontier)
        cur = path[-1]

        # stop early when reaching goal or small expansion depth
        if len(path) >= 3 or cur == goal:
            if s < best_score:
                best_path, best_score = path, s
            break

        for nxt in next_candidates(cur):
            if nxt in path: 
                continue
            g = s + edge_cost(cur, nxt) + relation(cur, nxt) + lexical_penalty(nxt)
            heapq.heappush(frontier, (g, path + [nxt]))

    # --- Build output ---
    content = [best_path[1]] if best_path and len(best_path) > 1 else []
    sentence = [w for w in pre + content + suf if w not in {".", ",", ";", "!", "?"}]

    return sentence


# =============================================================================
# AI USE DECLARATION
# =============================================================================
# Some parts of this file (e.g., code refactoring, heuristic explanations, and
# debugging suggestions) were developed with assistance from ChatGPT (GPT-5, 
# November 2025). The model was used to brainstorm ideas, rephrase pseudocode,
# and optimise structure — all outputs were critically reviewed and edited by me.
# =============================================================================