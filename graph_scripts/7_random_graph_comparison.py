import networkx as nx
import matplotlib.pyplot as plt

import os

NUM_NODES = 8000
NUM_EDGES = 30128

RESULTS_FOLDER = "results"
RANDOM_GRAPHML_FILE = os.path.join(RESULTS_FOLDER, "random.graphml")
RANDOM_GRAPH_METRICS_FILE = os.path.join(RESULTS_FOLDER, "random_network_metrics.txt")
DEGREE_DISTRIBUTION_PLOT = os.path.join(RESULTS_FOLDER, "degree_distribution_random.png")


os.makedirs(RESULTS_FOLDER, exist_ok=True)

# random graph with the same number of nodes and edges
random_graph = nx.gnm_random_graph(NUM_NODES, NUM_EDGES, directed=True)

# GraphML file
nx.write_graphml(random_graph, RANDOM_GRAPHML_FILE)

# 1) Degree Distribution
in_degrees_random = [deg for _, deg in random_graph.in_degree()]
out_degrees_random = [deg for _, deg in random_graph.out_degree()]

# 2) Average Node Degree
average_in_degree_random = sum(in_degrees_random) / len(in_degrees_random)
average_out_degree_random = sum(out_degrees_random) / len(out_degrees_random)

def plot_degree_distribution(degrees, title, filename):
    plt.figure()
    plt.hist(degrees, bins=12, edgecolor='black', log=True)
    plt.title(title)
    plt.xlabel("Degree")
    plt.ylabel("Frequency (log scale)")
    plt.savefig(filename)
    plt.close()

plot_degree_distribution(in_degrees_random, "In-Degree Distribution", DEGREE_DISTRIBUTION_PLOT)
print(f"Degree distribution plot saved to {DEGREE_DISTRIBUTION_PLOT}")

# 3) Top 20 Node Degrees
combined_degrees_random = [(node, deg) for node, deg in random_graph.degree()]
sorted_degrees_random = sorted(combined_degrees_random, key=lambda x: x[1], reverse=True)
top_20_degrees_random = sorted_degrees_random[:20]

# 4) Average Path Length
# if nx.is_strongly_connected(random_graph):
#     avg_path_length_random = nx.average_shortest_path_length(random_graph)
# else:
#     largest_scc_random = max(nx.strongly_connected_components(random_graph), key=len)
#     subgraph_random = random_graph.subgraph(largest_scc_random)
#     avg_path_length_random = nx.average_shortest_path_length(subgraph_random)

# 5) Average Clustering Coefficient
avg_clustering_coefficient_random = nx.average_clustering(random_graph)

# 6) Network Diameter
if nx.is_strongly_connected(random_graph):
    diameter_random = nx.diameter(random_graph)
else:
    largest_scc_random = max(nx.strongly_connected_components(random_graph), key=len)
    subgraph_random = random_graph.subgraph(largest_scc_random)
    diameter_random = nx.diameter(subgraph_random)

# 7) Network Density
network_density_random = nx.density(random_graph)

# 8) Number of Components
num_components_random = nx.number_weakly_connected_components(random_graph)

# 9) Sizes of Components
component_sizes_random = [len(c) for c in nx.weakly_connected_components(random_graph)]

with open(RANDOM_GRAPH_METRICS_FILE, "w") as f:
    f.write(f"Average In-Degree: {average_in_degree_random}\n")
    f.write(f"Average Out-Degree: {average_out_degree_random}\n")
    f.write("Top 20 Nodes by Degree:\n")
    for node, degree in top_20_degrees_random:
        f.write(f"{node}: {degree}\n")
    # f.write(f"Average Path Length: {avg_path_length_random}\n")
    f.write(f"Average Clustering Coefficient: {avg_clustering_coefficient_random}\n")
    f.write(f"Network Diameter: {diameter_random}\n")
    f.write(f"Network Density: {network_density_random}\n")
    f.write(f"Number of Components: {num_components_random}\n")
    f.write("Sizes of Components:\n")
    for size in component_sizes_random:
        f.write(f"{size}\n")


def plot_component_size_bar(component_sizes, filename):
    from collections import Counter
    size_counts = Counter(component_sizes)
    
    largest_size = max(component_sizes)
    smaller_sizes = {k: v for k, v in size_counts.items() if k < largest_size}
    
    plt.figure(figsize=(12, 6))
    
    plt.bar(smaller_sizes.keys(), smaller_sizes.values(), label="Smaller Components")
    plt.bar([largest_size], [size_counts[largest_size]], color='red', label=f"Largest Component ({largest_size} nodes)")
    
    plt.title("Component Size Distribution")
    plt.xlabel("Component Size")
    plt.ylabel("Frequency (log scale)")
    plt.yscale("log")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

COMPONENT_SIZE_DISTRIBUTION_PLOT = os.path.join(RESULTS_FOLDER, "component_size_distribution_random.png")
plot_component_size_bar(component_sizes_random, COMPONENT_SIZE_DISTRIBUTION_PLOT)
print(f"Component size distribution plot saved to {COMPONENT_SIZE_DISTRIBUTION_PLOT}")

def plot_component_size_bar_without_largest(component_sizes, filename):
    from collections import Counter
    size_counts = Counter(component_sizes)
    
    # Exclude the largest component
    largest_size = max(component_sizes)
    smaller_sizes = {k: v for k, v in size_counts.items() if k < largest_size}
    
    plt.figure(figsize=(12, 6))

    for size, count in smaller_sizes.items():
        plt.text(size, count, str(count), ha='center', va='bottom')
    plt.text(largest_size, size_counts[largest_size], str(size_counts[largest_size]), ha='center', va='bottom', color='red')
    
    # Plot smaller components
    plt.bar(smaller_sizes.keys(), smaller_sizes.values())
    
    plt.title("Component Size Distribution (Excluding Largest Component)")
    plt.xlabel("Component Size")
    plt.ylabel("Frequency (log scale)")
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()



COMPONENT_SIZE_DISTRIBUTION_NO_LARGEST_PLOT = os.path.join(RESULTS_FOLDER, "component_size_distribution_no_largest_random.png")
plot_component_size_bar_without_largest(component_sizes_random, COMPONENT_SIZE_DISTRIBUTION_NO_LARGEST_PLOT)
print("Component size distribution (excluding largest) plot saved to")
