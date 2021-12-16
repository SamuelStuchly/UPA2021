# UPA2021


This project assumes mongoDb running in container being exposed at `localhost:27017`. To use with mongodb running elsewhere change connection string in upa.py.

##### Requiremnts:
* Python3 
* Docker / Podman 


---
### Usage

Before running the script delete sample data in `data` directory.
```
make clean
```
Setup python virtual environment.
```
make venv
source venv/bin/activate
```
Either simply run `make`, or use individual commands as described below.


First need to spin up mongoDb container. (Make sure to have either podman or docker installed.) Then run the script to downlaod the data and insert them into the database.
```
make mongo
make run
```
After data have been inserted, connect to the database and access data.
```
make db
```



Inside mongosh choose database `upa` and view two collections `poskytovateleZP`,`obyvatelstvo`.
```
# inside mongoDB using mongosh
use upa
db.obyvatelstvo.find()
db.poskytovateleZP.find()
```
To drop the database with inserted data. 
```
make drop
```
---
###Part 2
To perform query and modification, and generate csv files:
```
make part2
```
#####Or
to make queries and create csv files:
```
make query
```
to then perform normalization and discretization:
```
make modify
```
