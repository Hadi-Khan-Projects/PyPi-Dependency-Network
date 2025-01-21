import networkx as nx
import os

GRAPHML_FILE = "graph/pypi_dependencies.graphml"
RESULTS_FOLDER = "results"
CYCLES_FILE = os.path.join(RESULTS_FOLDER, "graph_cycles.txt")

os.makedirs(RESULTS_FOLDER, exist_ok=True)

G = nx.read_graphml(GRAPHML_FILE)

cycles = list(nx.simple_cycles(G))
print(f"Detected {len(cycles)} cycles in the graph.")

with open(CYCLES_FILE, "w") as f:
    f.write(f"Detected {len(cycles)} cycles:\n")
    for cycle in cycles:
        f.write(f"{' -> '.join(cycle)}\n")

print(f"Cycles saved to {CYCLES_FILE}")