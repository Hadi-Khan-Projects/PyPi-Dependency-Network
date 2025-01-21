import csv
import os
import requests # type: ignore

CSV_FILE_PATH = 'data/top_pypi_packages_january.csv'
OUTPUT_FOLDER = 'data/package_metadata'

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

with open(CSV_FILE_PATH, 'r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    
    for row in reader:
        package_name = row['project']
        url = f'https://pypi.org/pypi/{package_name}/json'
        
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'Error fetching data for {package_name}: {e}')
            continue
        
        output_file = os.path.join(OUTPUT_FOLDER, f'{package_name}.json')
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(response.text)
        
        print(f'Successfully saved metadata for {package_name} to {output_file}')
