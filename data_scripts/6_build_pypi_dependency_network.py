import csv
import networkx as nx


CSV_PATH = "data/pypi_package_dependencies_with_vulnerabilities.csv"
GRAPHML_FILE = "graph/pypi_dependencies.graphml"
GEXF_FILE = "graph/pypi_dependencies.gexf"

def build_dependency_graph(csv_path):
    G = nx.DiGraph()
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader):
            package = row["project"]
            download_count = row["download_count"]
            dependencies_filtered = row["dependencies_filtered"]
            vulnerable = row["vulnerable"]
            vulnerable_current_version = row["vulnerable_current_version"]
            
            G.add_node(
                package,
                downloads=int(download_count) if download_count.isdigit() else None,
                downloads_rank=idx + 1,  # rank is just the row index + 1
                vulnerable=(vulnerable == "True"),
                vulnerable_current_version=(vulnerable_current_version == "True"),
            )
            
            # add edges to each dependency
            if dependencies_filtered.strip():
                deps = [dep.strip() for dep in dependencies_filtered.split(";")]
                for dep in deps:
                    if dep: 
                        G.add_edge(package, dep)
    
    return G

def main():
    G = build_dependency_graph(CSV_PATH)
    
    # Write to GraphML and GEXF
    nx.write_graphml(G, GRAPHML_FILE)
    print(f"Graph written to {GRAPHML_FILE}")
    nx.write_gexf(G, GEXF_FILE)
    print(f"Graph written to {GEXF_FILE}")

if __name__ == "__main__":
    main()
