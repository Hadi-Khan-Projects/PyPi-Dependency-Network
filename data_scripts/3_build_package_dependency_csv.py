import csv
import os
import json
import re

TOP_PACKAGES_CSV = "data/top_pypi_packages_january.csv"
OUTPUT_CSV = "data/pypi_package_dependencies.csv"
METADATA_FOLDER = "data/package_metadata"

# Read the top 8000 packages into lkst
top_packages = []
with open(TOP_PACKAGES_CSV, "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        top_packages.append(row)

top_package_names = {row["project"] for row in top_packages}

# output CSV. original columns plus 3 new ones.
fieldnames = ["download_count", "project", "dependencies_raw", "dependencies_cleaned", "dependencies_filtered"]

# Regex captures everything before any of these tokens: space, ==, >=, <=, >, <, = 
split_pattern = re.compile(r"\s|==|>=|<=|>|<|=")

with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in top_packages:
        package_name = row["project"]
        download_count = row["download_count"]
        
        # load the metadata JSON for this package
        json_path = os.path.join(METADATA_FOLDER, f"{package_name}.json")
        if not os.path.isfile(json_path):
            writer.writerow({
                "download_count": download_count,
                "project": package_name,
                "dependencies_raw": "",
                "dependencies_cleaned": "",
                "dependencies_filtered": ""
            })
            continue
        
        with open(json_path, "r", encoding="utf-8") as json_file:
            metadata = json.load(json_file)
        
        # requires_dist from metadata["info"]
        requires_dist = metadata.get("info", {}).get("requires_dist", None)
        
        if requires_dist is None:
            deps_raw_list = []
        else:
            deps_raw_list = requires_dist
        
        # add raw dependencies to  CSV
        dependencies_raw = "; ".join(deps_raw_list)
        
        # alsos troed cleaned dependency by removing version / extra info
        # (for edge creation between packages, still use version to evaluate infection)
        cleaned_list = []
        for dep_raw in deps_raw_list:
            # Example: 
            # "typeguard<4.3.0,>=2.13.3; python_version < '3.11'"
            # "typeguard"

            parts = split_pattern.split(dep_raw, maxsplit=1)
            if parts:
                cleaned_list.append(parts[0].strip())
            else:
                # Fallback
                cleaned_list.append(dep_raw.strip())
        
        dependencies_cleaned = "; ".join(cleaned_list)
        
        # Filter the cleaned dependencies to only those in the top 8000
        filtered_list = [dep for dep in cleaned_list if dep in top_package_names]
        dependencies_filtered = "; ".join(filtered_list)
        
        writer.writerow({
            "download_count": download_count,
            "project": package_name,
            "dependencies_raw": dependencies_raw,
            "dependencies_cleaned": dependencies_cleaned,
            "dependencies_filtered": dependencies_filtered
        })

print(f"Successfully created {OUTPUT_CSV} with dependency information.")
