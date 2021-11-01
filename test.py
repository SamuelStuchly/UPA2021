import csv
import json
import pymongo

db_string = "mongodb://localhost:27017"

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["test2"]
print(myclient.list_database_names())
mycol = mydb["customers"]


# Decide the two file paths according to your
# computer system
csvFilePath = "data.csv"
jsonFilePath = "data.json"



# Function to convert a CSV to JSON
# Takes the file paths as arguments
def make_json(csvFilePath, jsonFilePath):
    # create a dictionary
    data = []
    # Open a csv reader called DictReader
    with open(csvFilePath, encoding='ISO-8859-1') as csvf:
        csvReader = csv.DictReader(csvf,delimiter=";")
        # Convert each row into a dictionary
        # and add it to data
        # count = 0
        for rows in csvReader:
            # print(rows)
            # Assuming a column named 'No' to
            # be the primary key
            # key = rows['ZdravotnickeZarizeniId']

            data.append(rows)
            # count+=1

    return data
    # # Open a json writer, and use the json.dumps()
    # # function to dump data
    # with open(jsonFilePath, 'w', encoding='ISO-8859-1') as jsonf:
    # 	jsonf.write(json.dumps(data, indent=4))


# # Call the make_json function
data = make_json(csvFilePath, jsonFilePath)

# print(data)
x = mycol.insert_many(data)
print(x.inserted_ids)