import json
import csv

with open("data/insecure_pypi_packages_january.json", "r") as file:
    data = json.load(file)

count = 1

for package in data:
    print(str(count) + ". " + package)
    count += 1
    with open("data/insecure_pypi_packages_january.csv", "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["package_name"])  # Write header
        for package in data:
            csvwriter.writerow([package])