import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

GRAPHML_FILE = "graph/pypi_dependencies.graphml"
VISUALIZATION_FILE = "results/graph_visualization.png"

G = nx.read_graphml(GRAPHML_FILE)

# filter top N nodes by degree
TOP_N = 200 
top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:TOP_N]
subgraph_nodes = [node for node, _ in top_nodes]
subgraph = G.subgraph(subgraph_nodes)

# subgraph
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(subgraph) 
nx.draw_networkx_nodes(subgraph, pos, node_size=50, node_color="blue", alpha=0.7)
nx.draw_networkx_edges(subgraph, pos, alpha=0.1)
nx.draw_networkx_labels(subgraph, pos, font_size=8, font_color="red", alpha=1.0)

plt.title(f"Visualization of Top {TOP_N} Nodes by Degree")
plt.savefig(VISUALIZATION_FILE, dpi=300)
plt.close()

print(f"Graph visualization saved to {VISUALIZATION_FILE}")

# communities
communities = greedy_modularity_communities(G)
subgraph = G.subgraph(max(communities, key=len))

pos = nx.spring_layout(subgraph)
plt.figure(figsize=(12, 12))
nx.draw_networkx(subgraph, pos, node_size=50, node_color="lightblue", alpha=0.8)
plt.title("Visualization of Largest Community")
plt.savefig("results/largest_community_visualization.png", dpi=300)
plt.close()
