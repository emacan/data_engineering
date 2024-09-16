import json
import csv
import os
import commons.utils as utils

main_directory = utils.get_absolute_path("")
sources_directory = main_directory + "../sources/"

for filename in (os.listdir(sources_directory)):
    if ".json" in filename:
        filename = str.replace(filename, ".json", "")
        print("Processing: " + filename)
        with open(sources_directory + filename + '.json', 'r') as json_file:
            data = json.load(json_file)

        fieldnames = data[0].keys()

        with open(sources_directory + filename + '.csv', 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for row in data:
                writer.writerow(row)