import csv
from genericpath import isdir
import pymongo
import wget
from os.path import exists
from os import makedirs


DB_STRING = "mongodb://localhost:27017"

COLLECTION1 = "poskytovateleZP-{}-{}"
COLLECTION2 = "obyvatelstvo"

DB_NAME = "upa"

CZ_ENCODING = 'ISO-8859-2'
UTF = 'utf-8'


if __name__ == "__main__":

    myclient = pymongo.MongoClient(DB_STRING)
    mydb = myclient[DB_NAME]

    col1 = mydb[COLLECTION1.format("2021","10")]

    result = col1.aggregate([
        {"$match":
            {"AdresaZarizeni.Kraj": "Jihomoravský kraj"}
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

    #### Task A2:
    F_QUERY2 = "query-a2.csv"
    #f.write("typ_poskytovatele,pocet\n")
    with open(F_QUERY2, 'w') as f:
        f.write("date,zubní lékařství,chirurgie,patologie,Fyzioterapeut,psychiatrie\n")
    for year in range(2019,2022,1):
        months = ['01', '04', '07', '10']
        for month in months:
            col1 = mydb[COLLECTION1.format(year,month)]
            result = col1.aggregate([
                {"$group":
                    {"_id": "$Pece.OborPece", "count": {"$sum": 1}}
                },
                {"$match":
                   {"$or": [ {"_id": "zubní lékařství"},{"_id": "chirurgie"}, {"_id": "patologie"}, {"_id": "Fyzioterapeut"}, {"_id": "psychiatrie"}]}
                },
                {"$sort": {"count":-1}},
                ])

            with open(F_QUERY2, 'a') as f:
                f.write("{}-{},".format(year,month))
                for i in result:
                    f.write(str(i['count'])+",")
                f.write("\n")

    #### Task B1:
    pipline = [
        {"$match":
            {"Pece.OborPece": "v\x9Aeobecné praktické lékařství"}
        },
        {"$group":
            {"_id": "$AdresaZarizeni.Kraj", "count": {"$sum": 1}}
        },
        {"$sort": {"count":-1}},
        {"$match": {"_id": {"$ne":''}}}
        ]
    col1 = mydb[COLLECTION1.format("2021","10")]
    result = col1.aggregate(pipline)
    result_dict={}
    for i in result:
        result_dict.update({i['_id']: {"doctors": i['count'], "population": "null"}})

    col2 = mydb[COLLECTION2]
    pipeline = [
    {"$match":
        # vezme obyvatele starsi 20 let (vek_kod), pohlavi jsou obe (proto je tam prazdny retezec)
        {"vuzemi.vuzemi_cis": "100", "casref_do": "2020-12-31", "vek.vek_kod": {"$gte": "410020610025000"}, "pohlavi.pohlavi_kod" : "" }
    },
    {"$group":
        # group podle idhod, protoze se objevuji v databazi duplicitni hodnoty
        # TODO zde asi neni treba si uchovavat 'vek.vek_txt'
        {"_id": "$idhod", "hodnota": {"$first": "$hodnota"},"vek": {"$first":"$vek.vek_txt"}, "kraj": {"$first": "$vuzemi.vuzemi_txt"}}
    },
    {"$group":
        # groupnu podle kjraju a spocitam sumy vsech vekovych skupin pro dany kraj
        {"_id": "$kraj", "celkemObyvatel": {"$sum": {"$toInt": "$hodnota"}}}
    }
    ]
    result2 = col2.aggregate(pipeline)
    for i in result2:
        result_dict[i['_id']]["population"] = i['celkemObyvatel']
        # TODO zaokrouhlit na cela cisla?
        result_dict[i['_id']]["prs_per_doc"] = i['celkemObyvatel'] / result_dict[i['_id']]["doctors"]
    F_QUERY3 = "query-b1.csv"
    with open(F_QUERY3, 'w') as f:
        f.write("kraj,vseob-doktoru,obyvatel,osob-na-lekare\n")
        for kraj in result_dict:
            f.write("{},{},{},{}\n".format(
                kraj,
                result_dict[kraj]["doctors"],
                result_dict[kraj]["population"],
                result_dict[kraj]["prs_per_doc"]
            ))
