import csv

DEPENDENCIES_CSV = "data/pypi_package_dependencies.csv"
INSECURE_PACKAGES_CSV = "data/insecure_pypi_packages_january.csv"
OUTPUT_CSV = "data/pypi_package_dependencies_with_vulnerabilities.csv"

# set of insecure packages for speedy lookup
insecure_packages = set()
with open(INSECURE_PACKAGES_CSV, "r", encoding="utf-8") as f_insecure:
    reader = csv.DictReader(f_insecure)
    for row in reader:
        package_name = row["package_name"].strip()
        insecure_packages.add(package_name)

with open(DEPENDENCIES_CSV, "r", encoding="utf-8") as f_dependencies, \
     open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f_out:

    reader = csv.DictReader(f_dependencies)
    
    # add 'vulnerable' field
    fieldnames = reader.fieldnames + ["vulnerable"]
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        project_name = row["project"]
        
        # Check if project is in insecure list
        is_vulnerable = project_name in insecure_packages
        row["vulnerable"] = "True" if is_vulnerable else "False"
        writer.writerow(row)

print(f"Created {OUTPUT_CSV} with new 'vulnerable' column.")
