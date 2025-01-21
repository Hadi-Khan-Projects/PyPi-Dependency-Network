import csv
import json
import networkx as nx
from packaging.specifiers import SpecifierSet


DEPENDENCIES_CSV = "data/pypi_package_dependencies_with_vulnerabilities.csv"
INSECURE_PACKAGES_JSON = "data/insecure_pypi_packages_january.json"
GRAPHML_FILE = "graph/pypi_dependencies.graphml"
DETECTED_VULNERABILITIES_CSV = "data/detected_vulnerabilities.csv"

# Load insecure .JSON
with open(INSECURE_PACKAGES_JSON, "r", encoding="utf-8") as f_json:
    insecure_data = json.load(f_json)

def is_version_range_vulnerable(pkg_name, version_range):
    # Checks if a version range overlaps with the vulnerabilities listed in the JSON.
    if pkg_name not in insecure_data:
        return False

    for vuln_spec in insecure_data[pkg_name]:
        vuln_spec_set = SpecifierSet(vuln_spec)
        dep_spec_set = SpecifierSet(version_range)
        
        # dependency version range overlaps with the vulnerability range
        if any(ver in vuln_spec_set for ver in dep_spec_set):
            return True
    return False

# Load the dependency GraphML
G = nx.read_graphml(GRAPHML_FILE)

# Identify all vulnerable packages
vulnerable_packages = [node for node, data in G.nodes(data=True) if data.get("vulnerable_current_version") == "True"]

# dependencies on these vulnerable packages
detected_vulnerabilities = []

for vulnerable_package in vulnerable_packages:
    # Iterate over all incoming edges (aka packages that depend on this vulnerable package)
    for dependent_package, _ in G.in_edges(vulnerable_package):
        # Get the raw dependencies
        dependent_data = G.nodes[dependent_package]
        raw_dependencies = dependent_data.get("dependencies_raw", "")

        if not raw_dependencies:
            continue
        
        # Extract dependency version specifications for the vulnerable package
        for dep in raw_dependencies.split(";"):
            dep_parts = dep.strip().split(" ")
            if dep_parts[0] == vulnerable_package:
                dep_version_range = " ".join(dep_parts[1:]).strip()  # Extract version range

                is_vulnerable_range = is_version_range_vulnerable(vulnerable_package, dep_version_range)
                
                # if it overlaps
                if is_vulnerable_range:
                    detected_vulnerabilities.append({
                        "package": dependent_package,
                        "vulnerable_dependency": vulnerable_package,
                        "dependency_version_range": dep_version_range,
                        "vulnerable_version_range": "; ".join(insecure_data[vulnerable_package])
                    })

with open(DETECTED_VULNERABILITIES_CSV, "w", encoding="utf-8", newline="") as f_out:
    writer = csv.DictWriter(f_out, fieldnames=["package", "vulnerable_dependency", "dependency_version_range", "vulnerable_version_range"])
    writer.writeheader()
    writer.writerows(detected_vulnerabilities)

print(f"Detected vulnerabilities written to {DETECTED_VULNERABILITIES_CSV}.")
