import csv
import json
import os

from packaging.version import Version
from packaging.specifiers import SpecifierSet

DEPENDENCIES_CSV = "data/pypi_package_dependencies.csv"
INSECURE_PACKAGES_CSV = "data/insecure_pypi_packages_january.csv"
INSECURE_PACKAGES_JSON = "data/insecure_pypi_packages_january.json"
METADATA_FOLDER = "data/package_metadata"
OUTPUT_CSV = "data/pypi_package_dependencies_with_vulnerabilities.csv"

insecure_packages = set()
with open(INSECURE_PACKAGES_CSV, "r", encoding="utf-8") as f_insecure:
    reader = csv.DictReader(f_insecure)
    for row in reader:
        package_name = row["package_name"].strip()
        insecure_packages.add(package_name)

# 1) Read the insecure *version specs* from JSON (version-level vulnerability)
with open(INSECURE_PACKAGES_JSON, "r", encoding="utf-8") as f_json:
    insecure_data = json.load(f_json)
    # insecure_data example below
    #   {
    #       "package_name": ["<0.6", "==0.8pre", ">=1.0,<1.2"],
    #       "another_package": [...],
    #       ...
    #   }

def is_version_vulnerable(pkg_name, pkg_version):
    # If package not listed in the JSON, then no version-based vulnerabilities
    if pkg_name not in insecure_data:
        return False
    
    specs = insecure_data[pkg_name]  # e.g. ["<0.6", "==0.8pre", ">=1.0,<1.2"]
    current_ver = Version(pkg_version)
    
    for spec_str in specs:
        spec = SpecifierSet(spec_str)
        if current_ver in spec:
            return True
    return False

# 3) Read existing pypi_package_dependencies.csv and add 'ulnerable' and 'vulnerable_current_version' cols
with open(DEPENDENCIES_CSV, "r", encoding="utf-8") as f_dependencies, \
     open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f_out:

    reader = csv.DictReader(f_dependencies)

    fieldnames = reader.fieldnames + ["vulnerable", "vulnerable_current_version"]
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        project_name = row["project"]
        
        # package-level vulnerability
        is_vulnerable = project_name in insecure_packages
        
        # package+version-level vulnerability: 
        # 1) find project's current version from data/package_metadata/<project_name>.json
        # 2) check if it's in is_version_vulnerable
        json_path = os.path.join(METADATA_FOLDER, f"{project_name}.json")
        
        # if can't determine the version then default is false
        is_vulnerable_current_version = False
        
        if os.path.isfile(json_path):
            with open(json_path, "r", encoding="utf-8") as jf:
                metadata = json.load(jf)
            
            # get the version from metadata
            current_version = metadata.get("info", {}).get("version", "")
            if current_version:
                #check if that version is vulnerable
                is_vulnerable_current_version = is_version_vulnerable(project_name, current_version)
        
        row["vulnerable"] = "True" if is_vulnerable else "False"
        row["vulnerable_current_version"] = "True" if is_vulnerable_current_version else "False"
        
        writer.writerow(row)

print(f"Created {OUTPUT_CSV} with columns 'vulnerable' and 'vulnerable_current_version'.")
