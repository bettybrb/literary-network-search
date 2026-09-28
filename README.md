# Literary Network Search

### Graph search and heuristic language exploration over a literary text network

A classical artificial-intelligence project that represents literary text as a graph and applies search algorithms to explore relationships between words.

The project transforms George Orwell's *Nineteen Eighty-Four* into a word-adjacency network and uses classical and heuristic search methods to navigate that graph.

## Project overview

Words are represented as nodes and relationships between neighbouring words become graph edges.

This converts the literary text into a searchable network on which standard artificial-intelligence search algorithms can be applied.

The project explores:

- graph construction from natural language
- word-frequency analysis
- uninformed graph search
- weighted graph search
- heuristic search
- graph-based sentence completion

## What I implemented

- text loading and preprocessing
- tokenisation and word-frequency analysis
- rare-token processing
- word-adjacency graph construction
- graph visualisation
- Breadth-First Search
- Depth-First Search
- Uniform Cost Search
- Greedy Best-First Search
- A* Search
- priority-queue-based traversal
- graph-distance calculations
- heuristic functions based on graph structure
- weighted path exploration
- heuristic sentence completion
- algorithm testing and comparison

## Graph representation

The source text is converted into a network in which individual words are nodes.

Edges represent adjacency relationships observed in the text, allowing language structure to be analysed using graph algorithms.

## Classical search

The project implements several uninformed search methods:

- **Breadth-First Search (BFS)** explores nodes level by level
- **Depth-First Search (DFS)** follows individual paths deeply before backtracking
- **Uniform Cost Search (UCS)** expands paths according to accumulated cost

These algorithms provide different strategies for navigating the same word network.

## Heuristic search

The project extends classical graph traversal with informed search methods:

- **Greedy Best-First Search**
- **A* Search**

Graph-based heuristic information is used to guide exploration toward more promising paths rather than searching every possibility equally.

## Language generation experiment

The project also explores sentence completion as a graph-search problem.

Candidate words are selected through relationships in the literary network, demonstrating a transparent search-based alternative to neural language generation.

## Repository structure

    literary-network-search/
    ├── cw1.py
    ├── lab2.py
    ├── lab3.py
    ├── lab4.py
    ├── requirements.txt
    ├── .gitignore
    └── README.md

The original Python filenames are retained so the relationships between the project modules remain unchanged.

## Tech

**Python · NetworkX · NumPy · Matplotlib · Requests · Pillow · unittest · graph algorithms · natural-language processing · Breadth-First Search · Depth-First Search · Uniform Cost Search · Greedy Best-First Search · A* Search · heuristic search**
