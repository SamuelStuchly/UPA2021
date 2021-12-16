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
CZ_ENCODING2 = 'windows-1250'


def query_a1(collection):
    file = "query-a1.csv"
    result = collection.aggregate([
        {"$match":
            {"AdresaZarizeni.Kraj": "Jihomoravský kraj"}
        },
        {"$group":
            {"_id": "$Pece.OborPece", "count": {"$sum": 1}}
        },
        {"$sort":
            {"count":-1}
        },
        {"$match":
            {"_id": {"$ne":''}}
        },
        {"$limit": 15}
        ])
    with open(file, 'w', encoding=UTF) as f:
        f.write("typ_poskytovatele,pocet\n")
        for i in result:
            # TODO fix encoding?
            f.write(str(i['_id'])+","+str(i['count'])+"\n")

def query_a2():
    file = "query-a2.csv"
    with open(file, 'w') as f:
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

            with open(file, 'a') as f:
                f.write("{}-{}".format(year,month))
                for i in result:
                    f.write("," + str(i['count']))
                f.write("\n")

def query_b1(col1, col2):
    file = "query-b1.csv"
    pipline = [
        {"$match":
            {"Pece.OborPece": "v\x9Aeobecné praktické lékařství"}
        },
        {"$group":
            {"_id": "$AdresaZarizeni.Kraj", "count": {"$sum": 1}}
        },
        {"$sort": {"count":-1}},
        {"$match":
            {"_id": {"$ne":''}}
        }]
    result = col1.aggregate(pipline)
    result_dict={}
    for i in result:
        result_dict.update({i['_id']: {"doctors": i['count'], "population": "null"}})

    pipeline = [
    {"$match":
        # vezme obyvatele starsi 20 let (vek_kod), pohlavi jsou obe (proto je tam prazdny retezec)
        {"vuzemi.vuzemi_cis": "100", "casref_do": "2020-12-31", "vek.vek_kod": {"$gte": "410020610025000"}, "pohlavi.pohlavi_kod" : "" }
    },
    {"$group":
        # group podle idhod, protoze se objevuji v databazi duplicitni hodnoty
        {"_id": "$idhod", "hodnota": {"$first": "$hodnota"},"vek": {"$first":"$vek.vek_txt"}, "kraj": {"$first": "$vuzemi.vuzemi_txt"}}
    },
    {"$group":
        # groupnu podle kjraju a spocitam sumy vsech vekovych skupin pro dany kraj
        {"_id": "$kraj", "celkemObyvatel": {"$sum": {"$toInt": "$hodnota"}}}
    }
    ]
    result = col2.aggregate(pipeline)
    for i in result:
        result_dict[i['_id']]["population"] = i['celkemObyvatel']
        result_dict[i['_id']]["prs_per_doc"] = i['celkemObyvatel'] / result_dict[i['_id']]["doctors"]
    with open(file, 'w') as f:
        f.write("kraj,vseob-doktoru,obyvatel,osob-na-lekare\n")
        for kraj in result_dict:
            f.write("{},{},{},{}\n".format(
                kraj,
                result_dict[kraj]["doctors"],
                result_dict[kraj]["population"],
                result_dict[kraj]["prs_per_doc"]
            ))


def query_custom1(col):
    """
    Cilem dotazu je zjisit jak se vyvijel pocet muzu a zen v Brne od roku 2010.
    """
    file = "query-custom1.csv"
    # Get info about men
    pipeline = [
        {"$match":
            {"vuzemi.vuzemi_cis": "101", "vek.vek_kod": "", "pohlavi.pohlavi_kod" : "1", "vuzemi.vuzemi_kod": "40711" }
        },
        {"$group":
            {"_id": "$idhod", "hodnota": {"$first": "$hodnota"}, "datum": {"$first": "$casref_do"}}
        },
        {"$sort" :
            { "datum" : -1 }
        }]
    result = col.aggregate(pipeline)
    result_dict={}
    for i in result:
        result_dict.update({i['datum']: {"muzi": i['hodnota'], "zeny": "null"}})

    # Get info about women
    pipeline = [
        {"$match":
            {"vuzemi.vuzemi_cis": "101", "vek.vek_kod": "", "pohlavi.pohlavi_kod" : "2", "vuzemi.vuzemi_kod": "40711" }
        },
        {"$group":
            {"_id": "$idhod", "hodnota": {"$first": "$hodnota"}, "datum": {"$first": "$casref_do"}}
        },
        {"$sort" :
            { "datum" : -1 }
        }]
    result = col.aggregate(pipeline)
    for i in result:
        result_dict[i['datum']]["zeny"] = i['hodnota']
    with open(file, 'w') as f:
        f.write("datum,muzi,zeny,pomer\n")
        for datum in result_dict:
            f.write("{},{},{},{}\n".format(
                datum,
                result_dict[datum]["muzi"],
                result_dict[datum]["zeny"],
                int(result_dict[datum]["muzi"])/int(result_dict[datum]["zeny"])
           ))


def query_custom2(col1, col2):
    """
    Cilem dotazu je zjisit jak se menil pocet deti na pocet
    detskych lekaru ve stredoceskem a jihomoravskem kraji
    behem let 2019-2021.
    """

    file = "query-custom2.csv"
    result_dict = {}
    # Pocet detskych lekarstvi v kraji
    pipeline = [
        {"$match": 
            { "$or" : [{"AdresaZarizeni.Kraj": "Středočeský kraj"},{"AdresaZarizeni.Kraj": "Jihomoravský kraj"}]}
        },
        {"$match": 
            {"Pece.OborPece": "dětské lékařství"}
        },
        {"$group": 
            {"_id": "$AdresaZarizeni.Kraj", "count": {"$sum": 1}}
        }]
    for year in range(2019,2022,1):
        col1 = mydb[COLLECTION1.format(year,'01')]
        result = col1.aggregate(pipeline)
    
        for i in result:
            date = str(year-1)+"-12-31"
            key = i['_id']+","+date
            result_dict.update({key: { "p_lekaru" : i['count'], "p_deti": "null"}})

    # Pocet deti do veku 15 let ve stredoceskem kraji
    pipeline = [
        {"$match":
            {"vuzemi.vuzemi_cis": "100", "vek.vek_kod": {"$lte": "410010610015000"}, "pohlavi.pohlavi_kod" : "", "vuzemi.vuzemi_kod": "3026", "vek.vek_txt": {"$ne":''}, "casref_do": {"$gte": "2018-12-31"} }
        },
        {"$group": 
            {"_id": "$idhod", "hodnota": {"$first": "$hodnota"},"kraj": {"$first": "$vuzemi.vuzemi_txt"},"datum": {"$first": "$casref_do"}}
        },
        {"$group": 
            {"_id": "$datum", "celkem": {"$sum": {"$toInt": "$hodnota"}}}
        },
        {"$sort" : {"_id": -1}
        }]

    result = col2.aggregate(pipeline)
    for i in result:
        key = "Středočeský kraj,"+i['_id']
        result_dict[key]["p_deti"] = i['celkem']
    
    # Pocet deti do veku 15 let v jihomoravskem kraji
    pipeline = [
        {"$match":
            {"vuzemi.vuzemi_cis": "100", "vek.vek_kod": {"$lte": "410010610015000"}, "pohlavi.pohlavi_kod" : "", "vuzemi.vuzemi_kod": "3034", "vek.vek_txt": {"$ne":''}, "casref_do": {"$gte": "2018-12-31"} }
        },
        {"$group": 
            {"_id": "$idhod", "hodnota": {"$first": "$hodnota"},"kraj": {"$first": "$vuzemi.vuzemi_txt"},"datum": {"$first": "$casref_do"}}
        },
        {"$group": 
            {"_id": "$datum", "celkem": {"$sum": {"$toInt": "$hodnota"}}}
        },
        {"$sort" : {"_id": -1}
        }]
    result = col2.aggregate(pipeline)
    for i in result:
        key = "Jihomoravský kraj,"+i['_id']
        result_dict[key]["p_deti"] = i['celkem']

    with open(file, 'w') as f:
        f.write("kraj,datum,pocet_deti,pocet_detskych_lekaru,pocet_deti_na_lekare\n")
        for i in result_dict:
            f.write("{},{},{},{}\n".format(
                i,
                result_dict[i]['p_deti'],
                result_dict[i]['p_lekaru'],
                result_dict[i]['p_deti'] / result_dict[i]['p_lekaru']
            ))

def query_c(colStart):
    file = "query-c.csv"

    seznam_zarizeni = ['v\x9Aeobecné praktické lékařství', 'zubní lékařství', 'Fyzioterapeut',
            'praktické lékařství pro děti a dorost', 'vnitřní lékařství', 'gynekologie a porodnictví',
            'Zubní technik', 'praktické lékárenství', 'V\x9Aeobecná sestra', 'ortopedie a traumatologie pohybového ústrojí',
            'chirurgie', 'rehabilitační a fyzikální medicína', 'psychiatrie', 'neurologie', 'oftalmologie', 'dermatovenerologie',
            'endokrinologie a diabetologie', 'Klinický psycholog', 'anesteziologie a intenzivní medicína',
            'otorinolaryngologie a chirurgie hlavy a krku'
        ]

    with open(file, 'w') as f:
        f.write("obor")
        for year in range(2019,2022,1):
            months = ['01', '04', '07', '10']
            for month in months:
                f.write(","+str(year)+"-"+str(month))
        f.write("\n")

    for pece in seznam_zarizeni:
        with open(file, 'a') as f:
            f.write(str(pece))
        for year in range(2019,2022,1):
            months = ['01', '04', '07', '10']
            for month in months:
                col1 = mydb[COLLECTION1.format(year,month)]
                result = col1.aggregate([
                    {"$match":
                        {"Pece.OborPece": pece}
                    },
                    {"$group":
                        {"_id": "Pece.OborPece", "count": {"$sum": 1}}}
                    ])
                # Handle empty result
                if(result.alive is False):
                    with open(file, 'a') as f:
                        f.write("," + str(float("NaN")))
                else:
                    with open(file, 'a') as f:
                        for i in result:
                            f.write(","+str(i['count']))

        with open(file, 'a') as f:
            f.write("\n")



if __name__ == "__main__":

    myclient = pymongo.MongoClient(DB_STRING)
    mydb = myclient[DB_NAME]

    col1 = mydb[COLLECTION1.format("2021","10")]
    col2 = mydb[COLLECTION2]

    #### Task A1:
    query_a1(col1)

    #### Task A2:
    query_a2()

    #### Task B1:
    col1 = mydb[COLLECTION1.format("2021","01")]
    query_b1(col1, col2)

    #### Vlastni dotaz 1
    # Alda:
    #jak se v Brně měnil poměr můžu a žen v historii
    # Udělat spojnicový graf (x: quartal, y: poměrně můžu/žen)
    col1 = mydb[COLLECTION1.format("2021","10")]
    query_custom1(col2)

    #### Vlastni dotaz 2
    # Zjistit jaky je pocet deti na jednoho detskeho lekare v JMK a SK
    # a jak se tento pocet menil za posledni tri roky
    #
    col1 = mydb[COLLECTION1.format("2021","01")]
    query_custom2(col1,col2)

    #### Dolovaci alg - C dotaz
    query_c(col1)
