import csv
from genericpath import isdir
import pymongo
import wget
from os.path import exists
from os import makedirs


DB_STRING = "mongodb://localhost:27017"

COLLECTION1 = "poskytovateleZP"
COLLECTION2 = "obyvatelstvo"

DB_NAME = "upa"

CZ_ENCODING = 'ISO-8859-2'
UTF = 'utf-8'

if __name__ == "__main__":

    myclient = pymongo.MongoClient(DB_STRING)
    mydb = myclient[DB_NAME]

    col1 = mydb[COLLECTION1]
    col2 = mydb[COLLECTION2]

    result = col1.aggregate([
        {"$match":
            {"AdresaZarizeni.KrajKod": "CZ064"}
        },
        {"$group":
            {"_id": "$Pece.OborPece", "count": {"$sum": 1}}
        },
        {"$sort": {"count":-1}},
        {"$match": {"_id": {"$ne":''}}},
        {"$limit": 15}
        ])
    F_QUERY1 = "query-a1.csv"
    with open(F_QUERY1, 'w', encoding=UTF) as f:
        f.write("typ_poskytovatele,pocet\n")
        for i in result:
            #print(i['_id'].encode().decode())
            # TODO fix encoding?
            f.write(str(i['_id'])+","+str(i['count'])+"\n")
