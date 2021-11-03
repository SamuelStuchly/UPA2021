import csv
import pymongo
import wget
from os.path import exists

SOURCE_1_URL= "https://nrpzs.uzis.cz/res/file/export/export-sluzby-2021-10.csv"
SOURCE_2_URL= "https://www.czso.cz/documents/62353418/143522504/130142-21data043021.csv/760fab9c-d079-4d3a-afed-59cbb639e37d?version=1.1"

DIR = "data/"
CSVFILE1 = DIR + "data1.csv"
CSVFILE2 = DIR + "data2.csv"

DB_STRING = "mongodb://localhost:27017"

COLLECTION1 = "poskytovateleZP"
COLLECTION2 = "obyvatelstvo"

DB_NAME = "upa"

CZ_ENCODING = 'ISO-8859-2'
UTF = 'utf-8'

def parse_csv(csvFilePath, delimeter,enc):
    
    data = []

    with open(csvFilePath, encoding=enc) as csvfile:
        csvReader = csv.DictReader(csvfile,delimiter=delimeter)

        for rows in csvReader:
            data.append(rows)

    return data


def download_data(url,path):
    if not exists(path): 
        wget.download(url, out=path)

if __name__ == "__main__":
    download_data(SOURCE_1_URL,CSVFILE1)
    download_data(SOURCE_2_URL,CSVFILE2)

    myclient = pymongo.MongoClient(DB_STRING)
    mydb = myclient[DB_NAME]

    data1 = parse_csv(CSVFILE1,";",CZ_ENCODING)
    data2 = parse_csv(CSVFILE2,",",UTF)

    col1 = mydb[COLLECTION1]
    col2 = mydb[COLLECTION2]

    x = col1.insert_many(data1)
    print(x.inserted_ids)

    y = col2.insert_many(data2)
    print(y.inserted_ids)