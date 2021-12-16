import csv
import numpy as np
import pandas as pd


INPUT_FILE = "query-c.csv"
OUTPUT_FILE = "query-c-after.csv"
COLUMN_TO_NORMALIZE = "2021-07"
COLUMN_TO_DISCRETIZE = "2021-10"

NORMALIZE_MIN = 0
NORMALIZE_MAX = 1

data_normalize = []
data_discretize = []

NUMBER_OF_BINS = 4

data = []

try:
    with open(INPUT_FILE, encoding='utf-8') as csvfile:
        csvReader = csv.DictReader(csvfile, delimiter=",")
        fieldnames = csvReader.fieldnames

        for row in csvReader:
            data_normalize.append(int(row[COLUMN_TO_NORMALIZE]))
            data_discretize.append(int(row[COLUMN_TO_DISCRETIZE]))
            data.append(row)

        # normalize data
        max_value = max(data_normalize)
        min_value = min(data_normalize)

        normalized = []

        for value in data_normalize:
            min_max = ((value - min_value)/(max_value - min_value)) * (NORMALIZE_MAX-NORMALIZE_MIN) + NORMALIZE_MIN 
            normalized.append(min_max)


        # discretize data
        discretized = []

        df = pd.DataFrame(data_discretize, columns=[COLUMN_TO_DISCRETIZE])
        # quantile-based discretization with use of binning
        df['bins']=pd.qcut(df[COLUMN_TO_DISCRETIZE],NUMBER_OF_BINS)

        for idx, value in enumerate(data):
            data[idx][COLUMN_TO_DISCRETIZE] = df.iloc[idx]["bins"]
            data[idx][COLUMN_TO_NORMALIZE] = normalized[idx]
except IOError:
    print("I/O error: Could not read the file!")

# write to a csv file 
try:
    with open(OUTPUT_FILE, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in data:
            writer.writerow(i)
except IOError:
    print("I/O error: Could not write to a file!")
                
  
    
