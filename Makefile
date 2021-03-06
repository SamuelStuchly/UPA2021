
ifeq ($(shell command -v podman > /dev/null 2>&1 ; echo $$? ), 0)
	ENGINE=podman
else
	ENGINE=docker
endif

VENV := venv

all: clean-data mongo run db

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt	

venv: $(VENV)/bin/activate

run: 
	python3 upa.py

part2:
	python3 extract_data.py
	python3 modify.py

modify:
	python3 modify.py

query:
	python3 extract_data.py

drop: 
	python3 drop.py

mongo:
	$(ENGINE) run -v mongodata:/data/db -p 27017:27017 --name mongodb -d  mongo:5.0.3 

start-mongo:	
	$(ENGINE) container start mongodb

stop-mongo:
	$(ENGINE) container stop mongodb

db:
	$(ENGINE) exec -it mongodb mongosh

clean: clean-data clean-contrainer

clean-venv:
	rm -rf $(VENV)
	rm -rf __pycache__
	
clean-data:
	rm -rf data/

clean-container: stop-mongo 
	$(ENGINE) container rm mongodb

ZIP_NAME := "xtetur01_xstuch06_xlitwo00"
archive:
	zip -r $(ZIP_NAME).zip upa.py drop.py Makefile README.md dokumentace.pdf

.PHONY: venv clean-contrainer clean clean-data run drop db stop-mongo start-mongo mongo clean-venv

