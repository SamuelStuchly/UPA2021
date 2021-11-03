import csv
from genericpath import isdir
import pymongo
import wget
from os.path import exists
from os import makedirs

SOURCE_1_URL = "https://nrpzs.uzis.cz/res/file/export/export-sluzby-2021-10.csv"
SOURCE_2_URL = "https://www.czso.cz/documents/62353418/143522504/130142-21data043021.csv/760fab9c-d079-4d3a-afed-59cbb639e37d?version=1.1"

DIR = "data/"
CSVFILE1 = DIR + "data1.csv"
CSVFILE2 = DIR + "data2.csv"

DB_STRING = "mongodb://localhost:27017"

COLLECTION1 = "poskytovateleZP"
COLLECTION2 = "obyvatelstvo"

DB_NAME = "upa"

CZ_ENCODING = 'ISO-8859-2'
UTF = 'utf-8'

def restructure_pos(data):
    keys = ['ZdravotnickeZarizeniId', 'PCZ', 'PCDP', 'NazevCely', 'ZdravotnickeZarizeniKod', 'OdbornyZastupce', 'GPS', 'LastModified']
    druh = ['DruhZarizeniKod', 'DruhZarizeni', 'DruhZarizeniSekundarni']
    adresa = ['Obec', 'Psc', 'Ulice', 'CisloDomovniOrientacni','Kraj', 'KrajKod', 'Okres', 'OkresKod', 'SpravniObvod']
    poskytovatel = ['PoskytovatelTelefon', 'PoskytovatelFax', 'DatumZahajeniCinnosti', 'IdentifikatorDatoveSchranky', 'PoskytovatelEmail', 'PoskytovatelWeb', 'DruhPoskytovatele', 'PoskytovatelNazev', 'Ico', 'TypOsoby', 'PravniFormaKod']
    sidlo = ['KrajKodSidlo', 'KrajSidlo', 'OkresKodSidlo', 'OkresSidlo', 'PscSidlo', 'ObecSidlo', 'UliceSidlo', 'CisloDomovniOrientacniSidlo']
    pece = ['OborPece', 'FormaPece', 'DruhPece']
    structs = [(druh,"DruhZarizeni"),(adresa,"AdresaZarizeni"),(poskytovatel,"Poskytovatel"),(sidlo, "Sidlo"),(pece,"Pece")]
    
    new_data = {key:data[key] for key in keys if key in data}
    for s in structs:
        new_data[s[1]] = {key:data[key] for key in s[0] if key in data}

    return new_data

def restructure_oby(data):
    keys = ['idhod', 'hodnota', 'stapro_kod','casref_do']
    pohlavi = ['pohlavi_cis', 'pohlavi_kod','pohlavi_txt']
    vek = ['vek_cis', 'vek_kod','vek_txt']
    vuzemi = [ 'vuzemi_cis', 'vuzemi_kod', 'vuzemi_txt']
    structs = [(pohlavi,"pohlavi"),(vek,"vek"),(vuzemi,"vuzemi")]
    
    new_data = {key:data[key] for key in keys if key in data}
    for s in structs:
        new_data[s[1]] = {key:data[key] for key in s[0] if key in data}

    return new_data

def parse_csv(csvFilePath, delimeter, enc,restructure_func):

    data = []

    with open(csvFilePath, encoding=enc) as csvfile:
        csvReader = csv.DictReader(csvfile, delimiter=delimeter)

        for row in csvReader:
            row = restructure_func(row)
            data.append(row)

    return data


def download_data(url, path):
        if not exists(path):
            wget.download(url, out=path)
        else:
            print("Skipping donwload. Using stored data.")


if __name__ == "__main__":

    if not exists(DIR) or not isdir(DIR):
        makedirs(DIR)

    download_data(SOURCE_1_URL,CSVFILE1)
    download_data(SOURCE_2_URL,CSVFILE2)

    
    myclient = pymongo.MongoClient(DB_STRING)
    mydb = myclient[DB_NAME]

    data1 = parse_csv(CSVFILE1, ";", CZ_ENCODING,restructure_pos)
    data2 = parse_csv(CSVFILE2,",",UTF,restructure_oby)

    col1 = mydb[COLLECTION1]
    col2 = mydb[COLLECTION2]

    x = col1.insert_many(data1)
    print("\n" + COLLECTION1 + " inserted!")

    y = col2.insert_many(data2)
    print(COLLECTION2 + " inserted!")
