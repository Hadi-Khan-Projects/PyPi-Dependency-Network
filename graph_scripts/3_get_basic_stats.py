import networkx as nx
import matplotlib.pyplot as plt
import os

GRAPHML_FILE = "graph/pypi_dependencies.graphml"
RESULTS_FOLDER = "results"
DEGREE_DISTRIBUTION_PLOT = os.path.join(RESULTS_FOLDER, "degree_distribution.png")
os.makedirs(RESULTS_FOLDER, exist_ok=True)

G = nx.read_graphml(GRAPHML_FILE)

# 1) Degree Distribution
in_degrees = [deg for _, deg in G.in_degree()]
out_degrees = [deg for _, deg in G.out_degree()]

def plot_degree_distribution(degrees, title, filename):
    plt.figure()
    plt.hist(degrees, bins=30, edgecolor='black', log=True)
    plt.title(title)
    plt.xlabel("Degree")
    plt.ylabel("Frequency (log scale)")
    plt.savefig(filename)
    plt.close()

# Plot in-degree distribution
plot_degree_distribution(in_degrees, "In-Degree Distribution", DEGREE_DISTRIBUTION_PLOT)
print(f"Degree distribution plot saved to {DEGREE_DISTRIBUTION_PLOT}")

# 2) average node Degree
average_in_degree = sum(in_degrees) / len(in_degrees)
average_out_degree = sum(out_degrees) / len(out_degrees)

print(f"Average In-Degree: {average_in_degree}")
print(f"Average Out-Degree: {average_out_degree}")

# 3) Top node degrees
combined_degrees = [(node, deg) for node, deg in G.degree()]
# Sort by degree desc order
sorted_degrees = sorted(combined_degrees, key=lambda x: x[1], reverse=True)
top_20_degrees = sorted_degrees[:20]
print("Top 20 Nodes by Degree:")
for node, degree in top_20_degrees:
    print(f"{node}: {degree}")

# 4) Average Path Length
if nx.is_strongly_connected(G):
    avg_path_length = nx.average_shortest_path_length(G)
else:
    largest_scc = max(nx.strongly_connected_components(G), key=len)
    subgraph = G.subgraph(largest_scc)
    avg_path_length = nx.average_shortest_path_length(subgraph)

print(f"Average Path Length: {avg_path_length}")

# 5) Average Clustering Coefficient
avg_clustering_coefficient = nx.average_clustering(G)
print(f"Average Clustering Coefficient: {avg_clustering_coefficient}")

# 6) Network Diameter
# computed on the largest strongly connected component
if nx.is_strongly_connected(G):
    diameter = nx.diameter(G)
else:
    largest_scc = max(nx.strongly_connected_components(G), key=len)
    subgraph = G.subgraph(largest_scc)
    diameter = nx.diameter(subgraph)

print(f"Network Diameter: {diameter}")

# 7) Network Density
network_density = nx.density(G)
print(f"Network Density: {network_density}")

# 8) Num of Components
num_components = nx.number_weakly_connected_components(G)
print(f"Number of Components: {num_components}")

# 9) Sizes of Components
component_sizes = [len(c) for c in nx.weakly_connected_components(G)]
print("Sizes of Components:")
for size in component_sizes:
    print(size)

results_file = os.path.join(RESULTS_FOLDER, "network_metrics.txt")
with open(results_file, "w") as f:
    f.write(f"Average In-Degree: {average_in_degree}\n")
    f.write(f"Average Out-Degree: {average_out_degree}\n")
    f.write("Top 20 Nodes by Degree:\n")
    for node, degree in top_20_degrees:
        f.write(f"{node}: {degree}\n")
    f.write(f"Average Path Length: {avg_path_length}\n")
    f.write(f"Average Clustering Coefficient: {avg_clustering_coefficient}\n")
    f.write(f"Network Diameter: {diameter}\n")
    f.write(f"Network Density: {network_density}\n")
    f.write(f"Number of Components: {num_components}\n")
    f.write("Sizes of Components:\n")
    for size in component_sizes:
        f.write(f"{size}\n")

print(f"Results saved to {results_file}")

def plot_component_size_bar(component_sizes, filename):
    from collections import Counter
    size_counts = Counter(component_sizes)
    
    # exclude largest component
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


COMPONENT_SIZE_DISTRIBUTION_PLOT = os.path.join(RESULTS_FOLDER, "component_size_distribution.png")
plot_component_size_bar(component_sizes, COMPONENT_SIZE_DISTRIBUTION_PLOT)
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
    
    plt.bar(smaller_sizes.keys(), smaller_sizes.values())
    
    plt.title("Component Size Distribution (Excluding Largest Component)")
    plt.xlabel("Component Size")
    plt.ylabel("Frequency (log scale)")
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

COMPONENT_SIZE_DISTRIBUTION_NO_LARGEST_PLOT = os.path.join(RESULTS_FOLDER, "component_size_distribution_no_largest.png")
plot_component_size_bar_without_largest(component_sizes, COMPONENT_SIZE_DISTRIBUTION_NO_LARGEST_PLOT)
print(f"Component size distribution (excluding largest) plot saved to {COMPONENT_SIZE_DISTRIBUTION_NO_LARGEST_PLOT}")