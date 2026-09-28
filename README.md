# Literary Network Search

A graph-search and heuristic AI project that models literary text as a network and explores how classical search algorithms can be applied to language.

The project constructs a word network from George Orwell's *Nineteen Eighty-Four*, representing words as nodes and relationships between consecutive words as edges. Search algorithms are then used to investigate paths through the text and generate context-aware word sequences.

## Features

### Text-to-Graph Processing

The source text is tokenised and transformed into a graph representation based on word adjacency. The preprocessing pipeline includes text loading and tokenisation, word-frequency analysis, rare-token handling, adjacency counting, graph construction, distance matrices, and network visualisation.

### Classical Graph Search

Several fundamental search algorithms are implemented from scratch:

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Uniform Cost Search (UCS)

The implementations track paths, expanded nodes, search depth and frontier behaviour, allowing the algorithms to be compared.

### Heuristic Search

The project extends classical search with informed search techniques including Greedy Best-First Search, A* Search, shared-neighbour graph heuristics, and weighted path exploration.

The heuristic estimates relationships between words using their local connectivity within the text network.

### Literary Pathfinding

Search is applied directly to the literary network to investigate different types of routes through the text, including long paths and cost-based paths between words.

### Heuristic Sentence Generation

The project also explores language generation as a graph-search problem. Sentence completion uses heuristic search over the word network, combining graph structure with linguistic and morphological information to select plausible sequences between supplied sentence fragments.

## Technologies

- Python
- NetworkX
- NumPy
- Matplotlib
- Requests
- Pillow
- unittest

## Project Structure

- `cw1.py` - main literary-network and heuristic-search application
- `lab2.py` - text processing and network construction
- `lab3.py` - classical graph-search algorithms
- `lab4.py` - heuristic and informed-search algorithms
- `requirements.txt` - project dependencies

## Installation

```bash
pip install -r requirements.txt
```

## Concepts Demonstrated

- Graph modelling
- Natural-language preprocessing
- Breadth-first and depth-first search
- Uniform-cost search
- Greedy Best-First Search
- A* search
- Heuristic design
- Priority queues
- Graph-based language modelling
- Algorithm testing and visualisation

## Motivation

Rather than applying pathfinding only to conventional maps or synthetic graphs, this project explores how the same search principles can operate on natural language. A literary text becomes the search space, allowing graph algorithms and linguistic heuristics to interact within a single system.
