import pymongo

DB_STRING = "mongodb://localhost:27017"
DB_NAME= "upa"
COLLECTION1 = "poskytovateleZP"
COLLECTION2 = "obyvatelstvo"


if __name__ == "__main__":
    myclient = pymongo.MongoClient(DB_STRING)
    mydb = myclient[DB_NAME]

    col1 = mydb[COLLECTION1]
    col2 = mydb[COLLECTION2]

    # col1.drop()
    # col2.drop()
    myclient.drop_database(DB_NAME)
    