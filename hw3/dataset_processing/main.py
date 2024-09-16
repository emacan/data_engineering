import json
import os
import time

current_directory = None

# ------------ UTILS -------------
def init_working_dir():
    global current_directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

def get_absolute_path(relative_path):
    if not current_directory:
        init_working_dir()
    file_path = os.path.join(current_directory, relative_path)
    return file_path

def split_json_file(filename, output_prefix='split_'):
    with open(filename, 'r') as f:
        total_lines = sum(1 for _ in f)
        print(total_lines)
        midpoint = total_lines // 2

    with open(filename, 'r') as f, \
         open(output_prefix + '1.json', 'w') as f1, \
         open(output_prefix + '2.json', 'w') as f2:

        for i, line in enumerate(f):
            if i < midpoint:
                f1.write(line)
            else:
                f2.write(line)                
# ----------------------------------------

def extract_table_data(json_data,table_data):

    null_values = 0
   
    # Extract headers
    headers = []
    for cell in json_data["cells"]:
        if cell["isHeader"]:
            column_value = cell["cleanedText"]
            if len(column_value) > 0:
                headers.append(column_value)

    if headers:
    # Extract data for each column
        for cell in json_data["cells"]:
            if not cell["isHeader"]:
                column_index = cell["Coordinates"]["column"]

                if column_index < len(headers):
                    column_name = headers[column_index]

                    if column_name not in table_data:
                        table_data[column_name] = []
                    value = cell["cleanedText"]
                    if len(value) > 0:
                        if value not in table_data[column_name]:
                            table_data[column_name].append(value)
                    else:
                        null_values += 1
                else:
                    print("Invalid index.")
    else:
        print("Headers not found, skipping line.")

    return json_data["maxDimensions"]["row"], json_data["maxDimensions"]["column"], null_values

def process_distribution(distribution_data, rows, columns):
    distribution_data["rows"][rows] = distribution_data["rows"].get(rows, 0) + 1
    distribution_data["columns"][columns] = distribution_data["columns"].get(columns, 0) + 1

def run():
    print("Starting processing..")

    start_time = time.time()
    table_data = {}
    main_dir = get_absolute_path("")
    line_count = 0
    total_rows = 0
    total_columns = 0
    distribution = {
         "rows" : {},
         "columns" : {}
    }

    with open(f'{main_dir}/tables_reduced.json', 'r', encoding='utf-8') as file:
        for line in file:
            line_count += 1
            json_data = json.loads(line)
            print(line_count)
            rows, columns, null_values = extract_table_data(json_data,table_data)
            total_rows += rows 
            total_columns += columns
            process_distribution(distribution, rows, columns)

    output_file_path = f'{main_dir}/tables_reduced_processed.json' 

    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(table_data, json_file, ensure_ascii=False, indent=2)

    end_time = time.time()
    elapsed_time = end_time - start_time
    median_rows = total_rows / line_count
    median_columns = total_columns / line_count
    median_null_values = null_values / line_count
    print(f"Elapsed time: {elapsed_time} seconds")
    print(f"Number of tables: {line_count}")
    print(f"Median number of rows: {median_rows}")
    print(f"Median number of columns: {median_columns}")
    print(f"Median number of null values: {median_null_values}")
    print(distribution)

#split_json_file(filename)
run()