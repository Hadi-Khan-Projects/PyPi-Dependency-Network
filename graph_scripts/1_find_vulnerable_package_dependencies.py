import networkx as nx
import csv
import json
import os
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

GRAPHML_FILE = "graph/pypi_dependencies.graphml"
DEPENDENCIES_CSV = "data/pypi_package_dependencies_with_vulnerabilities.csv"
METADATA_FOLDER = "data/package_metadata"

# 2) Read the latest version of each package from its metadata .JSON
def load_latest_versions(metadata_folder):
    # Returns a dict: { package_name: "0.2.0" }
    # by reading each JSON file in data/package_metadata/<package_name>.json
    latest_versions = {}
    for fname in os.listdir(metadata_folder):
        if not fname.endswith(".json"):
            continue
        package_name = fname.replace(".json", "")
        json_path = os.path.join(metadata_folder, fname)
        try:
            with open(json_path, "r", encoding="utf-8") as jf:
                data = json.load(jf)
            version_str = data.get("info", {}).get("version", "")
            if version_str:
                latest_versions[package_name] = version_str
        except Exception:
            continue
    return latest_versions

# 3) Parse a single dependency string into dep_name and specifiers_str
def parse_dependency(raw_dep):
    # Given a raw dependency string (PEP 508 style), return (name, specifier_str).
    # Example of raw_dep: 'requests>=2.0,<3.0; python_version < "3.8"'
    # uses packaging.requirements.Requirement to parse.
    raw_dep = raw_dep.strip()
    if not raw_dep:
        return None, None
    
    try:
        req = Requirement(raw_dep)
        dep_name = req.name
        spec_str = str(req.specifier)  # e.g. '>=2.0,<3.0'
        return dep_name, spec_str
    except:  # noqa: E722
        return None, None

# 4) Build a dict of { package_name: [ (dep_name, specifiers), ... ] }
def load_package_dependencies(csv_path):
    # Reads pypi_package_dependencies_with_vulnerabilities.csv.
    # Returns a dict: 
    #     {
    #       'packageA': [(dep1, spec1), (dep2, spec2), ...],
    #       'packageB': [...],
    #       ...
    #     }
    # where each (dep, spec) is derived from the 'dependencies_raw' column.
    package_deps_map = {}
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            package_name = row["project"]
            deps_raw = row["dependencies_raw"]
            
            if deps_raw.strip():
                raw_list = [r.strip() for r in deps_raw.split(";")]
            else:
                raw_list = []
            
            dep_list = []
            for raw_entry in raw_list:
                if not raw_entry:
                    continue
                dep_name, spec_str = parse_dependency(raw_entry)
                if dep_name:
                    dep_list.append((dep_name, spec_str))
            
            package_deps_map[package_name] = dep_list
    
    return package_deps_map

# Given a reversed graph G (where an edge A->B means B depends on A),
# start_package is declared newly vulnerable in its *latest version*.

# I do a BFS/DFS in G - for each node that depends on an infected node,
# check if that node's dependency spec for the infected node includes
# the infected node's latest version. If so, it becomes infected too.

# Returns a set of infected packages (including the start_package).

# 5) Simulate vulnerability spread
def simulate_vulnerability_spread(G, package_deps_map, latest_versions, start_package):
    infected = set()
    stack = [start_package]
    
    # version of the start_package that is now vulnerable
    start_version_str = latest_versions.get(start_package, None)
    if not start_version_str:
        # no known version safe default
        start_version_str = "0"
    start_version = Version(start_version_str)

    while stack:
        current = stack.pop()
        if current in infected:
            continue
        infected.add(current)
        
        for next_pkg in G[current]:
            # next_pkg depends on current. check next_pkg's
            # dependency specs for 'current'.
            
            dep_list = package_deps_map.get(next_pkg, [])
            
            # if next_pkg depends on current
            # with a spec that includes start_version, then next_pkg becomes infected.
            for dep_name, spec_str in dep_list:
                if dep_name == current:
                    # spec parse
                    if spec_str:
                        try:
                            spec_set = SpecifierSet(spec_str)
                            if start_version in spec_set:
                                stack.append(next_pkg)
                                break
                        except:  # noqa: E722
                            pass
    
    return infected

def main():
    # Load the original directed graph from .graphml
    G_original = nx.read_graphml(GRAPHML_FILE)
    
    # Reverse the graph
    G_reversed = G_original.reverse(copy=True)
    
    # Gwt our package->dependencies map from the CSV
    package_deps_map = load_package_dependencies(DEPENDENCIES_CSV)
    
    # Get the latest versions from the metadata folder
    latest_versions = load_latest_versions(METADATA_FOLDER)
    
    # Example package to "infect"
    infected_package = "werkzeug"
    
    infected_set = simulate_vulnerability_spread(
        G=G_reversed,
        package_deps_map=package_deps_map,
        latest_versions=latest_versions,
        start_package=infected_package
    )
    
    print(f"Starting from {infected_package}, the following packages got infected:")
    for pkg in sorted(infected_set):
        print("  -", pkg)

if __name__ == "__main__":
    main()
