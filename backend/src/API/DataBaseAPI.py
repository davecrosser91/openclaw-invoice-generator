import random
import os
from fastapi import FastAPI, Depends
from src.SQLAlchemy.schemas import (
    StadtMitPlz,
    Strasse,
    Vorname,
    Nachname,
    GenderSchema,
    Firma,
)
from sqlalchemy.orm import Session
from src.SQLAlchemy.PostgresConnection import PostgressConnection
from src.SQLAlchemy.Db_Staedte import Staedte
from src.SQLAlchemy.Db_Strassen import Strassen
from src.SQLAlchemy.Db_Vor_u_Nachnamen import VornamenW, VornamenM, Nachnamen
from src.SQLAlchemy.Db_Firmen import Firmen
from fastapi.responses import HTMLResponse
from src.Datenvalidierung.Enum_Classes import Gender
import pandas as pd
from dotenv import load_dotenv


"""!!!NOT NEEDED ANYMORE SINCE STRAPI IS USED!!!"""


load_dotenv()

app = FastAPI()
conn = PostgressConnection(url=os.getenv("POSTGRESDB_URL_LOCAL"))

# db = conn.retrieve_db_session
""" 
Funktion nur da weil sonst Depends nicht funktioniert. Versteh nicht so ganz warum es nicht funktioniert wenn man 
eine Funktion importiert. 
Bsp: conn = PostgressConnection(url="postgresql://Benedikt:***@localhost:8005/postgres_db")
db = conn.retrieve_db_session und dann  
database: Session = Depends(db) funktioniert nicht obwohl es eigentlich das Gleiche ist. 
"""


def get_db():
    db = conn.create_session(False, False)()
    try:
        yield db
    finally:
        if db:
            db.close()


@app.get("/", response_class=HTMLResponse)
def read_root():
    multi_string = """PostgresDb: Endpunkte: 
                C:--CREATE---------------------------------------------------------------------------------
                -------------------------------------------------------------------------------------------
                Staedte-Table:
                -----------------------------------------------------------------------------------------
                -   /create_single_town: Beispiel curl :  % curl --request POST --data '{'name': 'Schorndorf', 'plz': 73614}' -H 'Content-Type: application/json' localhost:8000/create_single_town | Output: {"success":True,"created_id":*ID*} %
                -   /create_town_list: Beispiel curl :  % curl --request POST 'localhost:8000/create_town_list' | Output: {"success":True}  %
                -----------------------------------------------------------------------------------------
                Strasse-Table:
                -----------------------------------------------------------------------------------------
                -   /create_single_street: Beispiel curl : % curl --request POST --data '{'name': 'Hauptstraße'}' -H 'Content-Type: application/json' localhost:8000/create_single_street | Output: {"success":True,"created_id":*ID*} %
                -   /create_street_list: Beispiel curl : % curl --request POST 'localhost:8000/create_street_list' | Output: {"success":True} %
                -----------------------------------------------------------------------------------------
                VornamenM/VornamenW-Table:
                -----------------------------------------------------------------------------------------
                -   /create_single_firstname: Beispiel curl : % curl --request POST --data '{'name': 'Ragnar', 'gender': 'male'}' -H 'Content-Type: application/json' localhost:8000/create_single_firstname | Output: {"success":True,"created_id":*ID*} %
                -   /create_firstname_list: Beispiel curl : % curl --request POST --data '{"gender": "female"}' -H 'Content-Type: application/json' localhost:8000/create_firstname_list | Output: {"success":True} %
                -----------------------------------------------------------------------------------------
                Nachnamen-Table:
                -----------------------------------------------------------------------------------------
                -   /create_single_lastname: Beispiel curl : % curl --request POST --data '{'name': 'Lothbrok'}' -H 'Content-Type: application/json' localhost:8000/create_single_lastname | Output: {"success":True,"created_id":*ID*} %
                -   /create_lastname_list: Beispiel curl : % curl --request POST 'localhost:8000/create_lastname_list' | Output: {"success":True} %
                -----------------------------------------------------------------------------------------
                Firmen-Table:
                -----------------------------------------------------------------------------------------
                -   /create_single_company: Beispiel curl : % curl --request POST --data '{'name': 'xyz','description':'The company xyz ...'}' -H 'Content-Type: application/json' localhost:8000/create_single_company | Output: {"success":True,"created_id":*ID*} %
                -   /create_company_list: Beispiel curl : % curl --request POST 'localhost:8000/create_company_list' | Output: {"success":True} %
                -----------------------------------------------------------------------------------------
                -----------------------------------------------------------------------------------------
                R:--READ---------------------------------------------------------------------------------
                -----------------------------------------------------------------------------------------
                Staedte-Table:
                -----------------------------------------------------------------------------------------
                -   /get_town_by_id:  Beispiel curl: % curl --request GET 'localhost:8000/get_town_by_id?t_id=1' | Output: {"name":"Aach","plz":78267,"t_id":1} %
                -   /get_town_by_name:  Beispiel curl: % curl --request GET 'localhost:8000/get_town_by_name?name=Schorndorf&plz=73614' plz ist optional sollte jedoch zur genauen Rückgabe definiert werden. | Output: {"name":"Schorndorf","plz":73614,"t_id":10376} %
                -   /get_town_by_plz:  Beispiel curl: % curl --request GET 'localhost:8000/get_town_by_plz?plz=73614' | Output: {"name":"Schorndorf","plz":73614,"t_id":10376} %
                -   /get_all_towns:  Beispiel curl: % curl --request GET 'localhost:8000/get_all_towns' | Output: [{"name":"Aach","plz":78267,"t_id":1},...,{"name":"Zwönitz","plz":8297,"t_id":12854}] %
                -   /get_random_town:  Beispiel curl: % curl --request GET 'localhost:8000/get_random_town' | Output: {"name":"*random_town_name*","plz":*random_town_plz*,"t_id":*random_town_id*} %
                -----------------------------------------------------------------------------------------
                Strasse-Table:
                -----------------------------------------------------------------------------------------
                -   /get_street_by_id:  Beispiel curl: % curl --request GET 'localhost:8000/get_street_by_id?s_id=1' | Output: {"s_id":1,"name":"Dorfstraße"} %
                -   /get_street_by_name:  Beispiel curl: % curl --request GET 'localhost:8000/get_street_by_name?name=Dorfstraße' | Output: *ß* muss noch in URL kodiert werden, daher derzeit nicht möglich 01.12.2023 %
                -   /get_all_streets:  Beispiel curl: % curl --request GET 'localhost:8000/get_all_streets' | Output: [{"s_id":1,"name":"Dorfstraße"},...,{"s_id":1259,"name":"Eichhörnchenweg"}] %
                -   /get_random_street:  Beispiel curl: % curl --request GET 'localhost:8000/get_random_street' | Output: {"s_id":"*random_strassen_id*","name":*random_strassen_name*} %
                -----------------------------------------------------------------------------------------
                VornamenM/VornamenW-Table:
                -----------------------------------------------------------------------------------------
                -   /get_firstname_by_id:  Beispiel curl: % curl --request GET 'localhost:8000/get_firstname_by_id?n_id=1&gender=male' | Output: {"n_id":1,"name":"Ben"} %
                -   /get_firstname_by_name:  Beispiel curl: % curl --request GET 'localhost:8000/get_firstname_by_name?name=Peter&gender=male' | Output: {"n_id":212,"name":"Peter"} %
                -   /get_all_firstnames:  Beispiel curl: % curl --request GET 'localhost:8000/get_all_firstnames?gender=male' | Output: [{"n_id":1,"name":"Ben"},...,{"n_id":500,"name":"Simeon"}] %
                -   /get_random_firstname:  Beispiel curl: % curl --request GET 'localhost:8000/get_random_firstname?gender=male' | Output: {"n_id":*random_vornamen_id*,"name":*random_vorname*} %
                -----------------------------------------------------------------------------------------
                Nachnamen-Table:
                -----------------------------------------------------------------------------------------
                -   /get_lastname_by_id:  Beispiel curl: % curl --request GET 'localhost:8000/get_lastname_by_id?n_id=1'  | Output: {"name":"Müller","n_id":1} %
                -   /get_lastname_by_name:  Beispiel curl: % curl --request GET 'localhost:8000/get_lastname_by_name?name=Müller'  | Output: *Ä,Ö,Ü,ä,ö,ü,ß* etc muss noch in URL kodiert werden, daher derzeit nicht möglich 01.12.2023%
                -   /get_all_lastnames:  Beispiel curl: % curl --request GET 'localhost:8000/get_all_lastnames'  | Output: [{"name":"Müller","n_id":1},...,{"name":"Löser","n_id":2000}] %
                -   /get_random_lastname:  Beispiel curl: % curl --request GET 'localhost:8000/get_random_lastname'  | Output: {"n_id":*random_nachnamen_id*,"name":*random_nachname*} %
                -----------------------------------------------------------------------------------------
                Firmen-Table:
                -----------------------------------------------------------------------------------------
                -   /get_company_by_id:  Beispiel curl: % curl --request GET 'localhost:8000/get_company_by_id?n_id=1'  | Output: {"name":"Volkswagen AG ","description":"Volkswagen AG, known...","f_id":1} %
                -   /get_company_by_name:  Beispiel curl: % curl --request GET 'localhost:8000/get_company_by_name?name=Volkswagen%20AG%20' | Output: *Ä,Ö,Ü,ä,ö,ü,ß* etc muss noch in URL kodiert werden, daher derzeit nicht möglich 01.12.2023 % 
                -   /get_all_companies:  Beispiel curl: % curl --request GET 'localhost:8000/get_all_companies'  | Output: [{"name":"Volkswagen AG ","description":"Volkswagen AG, known...","f_id":1},...,{"name":"Cobana GmbH & Co. KG","description":"Cobana GmbH & Co. KG operates...","f_id":591}] %
                -   /get_random_company:  Beispiel curl: % curl --request GET 'localhost:8000/get_random_company'  | Output: {"f_id":*random_company_id*,"name":*random_company_name*, "description":*random_company_description*} %
                -----------------------------------------------------------------------------------------
                -----------------------------------------------------------------------------------------
                U:--PUT/PATCH----------------------------------------------------------------------------
                -----------------------------------------------------------------------------------------
                D:--DELETE-------------------------------------------------------------------------------
                -----------------------------------------------------------------------------------------
                Staedte-Table: 
                -----------------------------------------------------------------------------------------
                -   /delete_town_by_id: Beispiel curl: % curl --request DELETE 'localhost:8000/delete_town_by_id?t_id=1' | Output: {"success": True}  %
                -   /delete_town_by_name: Beispiel curl: % curl --request DELETE 'localhost:8000/delete_town_by_name?name=Schorndorf&plz=73614' plz ist optional sollte jedoch zur genauen Entfernung definiert werden. | Output: {"success": True} %
                -   /delete_town_by_plz: Beispiel curl: % curl --request DELETE 'localhost:8000/delete_town_by_plz?plz=73614' | Output: {"success": True} %
                -----------------------------------------------------------------------------------------
                Strasse-Table:
                -----------------------------------------------------------------------------------------
                -   /delete_street_by_id: Beispiel curl: % curl --request DELETE 'localhost:8000/delete_street_by_id?s_id=1' | Output: {"success": True}  %
                -   /delete_street_by_name: Beispiel curl: % curl --request DELETE 'localhost:8000/delete_street_by_name?name=Dorfstraße' | Output: *Ä,Ö,Ü,ä,ö,ü,ß* etc muss noch in URL kodiert werden, daher derzeit nicht möglich 01.12.2023 %
                -----------------------------------------------------------------------------------------
                VornamenM/VornamenW-Table:
                -----------------------------------------------------------------------------------------
                -   /delete_firstname_by_id: Beispiel curl: % curl --request DELETE 'localhost:8000/delete_firstname_by_id?n_id=1' | Output: {"success": True}  %
                -   /delete_firstname_by_name: Beispiel curl: % curl --request DELETE 'localhost:8000/delete_firstname_by_name?name=Schorndorf' | Output: *Ä,Ö,Ü,ä,ö,ü,ß* etc muss noch in URL kodiert werden, daher derzeit nicht möglich 01.12.2023 %
                -----------------------------------------------------------------------------------------
                Nachnamen-Table:
                -----------------------------------------------------------------------------------------
                -   /delete_lastname_by_id: Beispiel curl: % curl --request DELETE 'localhost:8000/delete_lastname_by_id?n_id=1' | Output: {"success": True}  %
                -   /delete_lastname_by_name: Beispiel curl: % curl --request DELETE 'localhost:8000/delete_lastname_by_name?name=Müller' | Output: *Ä,Ö,Ü,ä,ö,ü,ß* etc muss noch in URL kodiert werden, daher derzeit nicht möglich 01.12.2023 %
                -----------------------------------------------------------------------------------------
                Firmen-Table:
                -----------------------------------------------------------------------------------------
                -   /delete_company_by_id: Beispiel curl: % curl --request DELETE 'localhost:8000/delete_company_by_id?f_id=1' | Output: {"success": True}  %
                -   /delete_company_by_name: Beispiel curl: % curl --request DELETE 'localhost:8000/delete_company_by_name?name==Volkswagen%20AG%20' | Output: *Ä,Ö,Ü,ä,ö,ü,ß* etc muss noch in URL kodiert werden, daher derzeit nicht möglich 01.12.2023 %
                -----------------------------------------------------------------------------------------
                """
    return f"<html><body><pre>{multi_string}</pre></body></html>"


"""C----------------------------------------------------------------------"""


@app.post("/create_single_town")
def create_single_town(data: StadtMitPlz, database: Session = Depends(get_db)):
    to_create = Staedte(name=data.name, plz=data.plz)
    database.add(to_create)
    database.commit()
    return {"success": True, "created_id": to_create.t_id}


@app.post("/create_single_street")
def create_single_street(data: Strasse, database: Session = Depends(get_db)):
    to_create = Strassen(name=data.name)
    database.add(to_create)
    database.commit()
    return {"success": True, "created_id": to_create.s_id}


@app.post("/create_single_firstname")
def create_single_firstname(data: Vorname, database: Session = Depends(get_db)):
    if data.gender.male:
        to_create = VornamenM(name=data.name)
    else:
        to_create = VornamenW(name=data.name)
    database.add(to_create)
    database.commit()
    return {"success": True, "created_id": to_create.n_id}


@app.post("/create_single_lastname")
def create_single_lastname(data: Nachname, database: Session = Depends(get_db)):
    to_create = Nachnamen(name=data.name)
    database.add(to_create)
    database.commit()
    return {"success": True, "created_id": to_create.n_id}


@app.post("/create_single_company")
def create_single_company(data: Firma, database: Session = Depends(get_db)):
    to_create = Firmen(name=data.name, description=data.description)
    database.add(to_create)
    database.commit()
    return {"success": True, "created_id": to_create.f_id}


"""Sollten vermutlich keine Endpunkte sein die der Enduser verwenden kann."""


@app.post("/create_town_list")
def create_town_list(database: Session = Depends(get_db)):
    data = pd.read_csv("src/GeoDaten/zuordnung_plz_ort.csv")[["ort", "plz"]]
    for towns in data.values:
        to_create = Staedte(name=towns[0], plz=towns[1])
        database.add(to_create)
        database.commit()
    return {"success": True}


@app.post("/create_street_list")
def create_street_list(database: Session = Depends(get_db)):
    data = pd.read_csv("src/GeoDaten/Straßennamen.csv")["strasse_name"]
    for strassen in data.values:
        to_create = Strassen(name=strassen)
        database.add(to_create)
        database.commit()
    return {"success": True}


@app.post("/create_firstname_list")
def create_firstname_list(gender: GenderSchema, database: Session = Depends(get_db)):
    if gender.gender.value == "male":
        data = pd.read_json("src/PersonenDaten/vornamen_m.json").transpose()
        for vornamen in data.values[0]:
            to_create = VornamenM(name=vornamen)
            database.add(to_create)
            database.commit()
    else:
        data = pd.read_json("src/PersonenDaten/vornamen_w.json").transpose()
        for vornamen in data.values[0]:
            to_create = VornamenW(name=vornamen)
            database.add(to_create)
            database.commit()
    return {"success": True}


@app.post("/create_lastname_list")
def create_lastname_list(database: Session = Depends(get_db)):
    data = pd.read_json("src/PersonenDaten/nachnamen.json").transpose()
    for nachname in data.values[0]:
        to_create = Nachnamen(name=nachname)
        database.add(to_create)
        database.commit()
    return {"success": True}


@app.post("/create_company_list")
def create_company_list(database: Session = Depends(get_db)):
    data = pd.read_json("src/Datenbank/json_storage/companies/all_companies.json").transpose()
    for company, description in data.values:
        to_create = Firmen(name=company, description=description)
        database.add(to_create)
        database.commit()
    return {"success": True}


"""----------------------------------------------------------------------"""
"""R----------------------------------------------------------------------"""


@app.get("/get_town_by_id")
def get_town_by_id(t_id: int, database: Session = Depends(get_db)):
    return database.query(Staedte).filter(Staedte.t_id == t_id).first()


@app.get("/get_street_by_id")
def get_street_by_id(s_id: int, database: Session = Depends(get_db)):
    return database.query(Strassen).filter(Strassen.s_id == s_id).first()


@app.get("/get_firstname_by_id")
def get_firstname_by_id(n_id: int, gender: Gender, database: Session = Depends(get_db)):
    if gender.value == "male":
        return database.query(VornamenM).filter(VornamenM.n_id == n_id).first()
    else:
        return database.query(VornamenW).filter(VornamenW.n_id == n_id).first()


@app.get("/get_lastname_by_id")
def get_lastname_by_id(n_id: int, database: Session = Depends(get_db)):
    return database.query(Nachnamen).filter(Nachnamen.n_id == n_id).first()


@app.get("/get_company_by_id")
def get_company_by_id(f_id: int, database: Session = Depends(get_db)):
    return database.query(Firmen).filter(Firmen.f_id == f_id).first()


@app.get("/get_town_by_name")
def get_town_by_name(name: str, plz: int = None, database: Session = Depends(get_db)):
    if not plz:
        return database.query(Staedte).filter(Staedte.name == name).first()
    else:
        return database.query(Staedte).filter(Staedte.name == name, Staedte.plz == plz).first()


@app.get("/get_street_by_name")
def get_street_by_name(name: str, database: Session = Depends(get_db)):
    return database.query(Strassen).filter(Strassen.name == name).first()


@app.get("/get_firstname_by_name")
def get_firstname_by_name(name: str, gender: Gender, database: Session = Depends(get_db)):
    if gender.value == "male":
        return database.query(VornamenM).filter(VornamenM.name == name).first()
    else:
        return database.query(VornamenW).filter(VornamenW.name == name).first()


@app.get("/get_lastname_by_name")
def get_lastname_by_name(name: str, database: Session = Depends(get_db)):
    return database.query(Nachnamen).filter(Nachnamen.name == name).first()


@app.get("/get_company_by_name")
def get_company_by_name(name: str, database: Session = Depends(get_db)):
    return database.query(Firmen).filter(Firmen.name == name).first()


@app.get("/get_town_by_plz")
def get_town_by_plz(plz: int, database: Session = Depends(get_db)):
    return database.query(Staedte).filter(Staedte.plz == plz).first()


@app.get("/get_all_towns")
def get_all_towns(database: Session = Depends(get_db)):
    return database.query(Staedte).all()


@app.get("/get_all_streets")
def get_all_streets(database: Session = Depends(get_db)):
    return database.query(Strassen).all()


@app.get("/get_all_firstnames")
def get_all_firstnames(gender: Gender, database: Session = Depends(get_db)):
    if gender.value == "male":
        return database.query(VornamenM).all()
    else:
        return database.query(VornamenW).all()


@app.get("/get_all_lastnames")
def get_all_lastnames(database: Session = Depends(get_db)):
    return database.query(Nachnamen).all()


@app.get("/get_all_companies")
def get_all_companies(database: Session = Depends(get_db)):
    return database.query(Firmen).all()


@app.get("/get_random_town")
def get_random_towns(database: Session = Depends(get_db)):
    count = database.query(Staedte).count()
    random_num = random.randint(1, count)
    random_item = database.query(Staedte).filter(Staedte.t_id == random_num).first()
    return random_item


@app.get("/get_random_street")
def get_random_street(database: Session = Depends(get_db)):
    count = database.query(Strassen).count()
    random_num = random.randint(1, count)
    random_item = database.query(Strassen).filter(Strassen.s_id == random_num).first()
    return random_item


@app.get("/get_random_firstname")
def get_random_firstname(gender: Gender, database: Session = Depends(get_db)):
    if gender.value == "male":
        count = database.query(VornamenM).count()
        random_num = random.randint(1, count)
        random_item = database.query(VornamenM).filter(VornamenM.n_id == random_num).first()
    else:
        count = database.query(VornamenW).count()
        random_num = random.randint(1, count)
        random_item = database.query(VornamenW).filter(VornamenW.n_id == random_num).first()
    return random_item


@app.get("/get_random_lastname")
def get_random_lastname(database: Session = Depends(get_db)):
    count = database.query(Nachnamen).count()
    random_num = random.randint(1, count)
    random_item = database.query(Nachnamen).filter(Nachnamen.n_id == random_num).first()
    return random_item


@app.get("/get_random_company")
def get_random_company(database: Session = Depends(get_db)):
    count = database.query(Firmen).count()
    random_num = random.randint(1, count)
    random_item = database.query(Firmen).filter(Firmen.f_id == random_num).first()
    return random_item


"""----------------------------------------------------------------------"""
"""U----------------------------------------------------------------------"""

"""----------------------------------------------------------------------"""
"""D----------------------------------------------------------------------"""


@app.delete("/delete_town_by_id")
def delete_town_by_id(t_id: int, database: Session = Depends(get_db)):
    database.query(Staedte).filter(Staedte.t_id == t_id).delete()
    database.commit()
    return {"success": True}


@app.delete("/delete_street_by_id")
def delete_street_by_id(s_id: int, database: Session = Depends(get_db)):
    database.query(Strassen).filter(Strassen.s_id == s_id).delete()
    database.commit()
    return {"success": True}


@app.delete("/delete_firstname_by_id")
def delete_firstname_by_id(n_id: int, gender: Gender, database: Session = Depends(get_db)):
    if gender.value == "male":
        database.query(VornamenM).filter(VornamenM.n_id == n_id).delete()
    else:
        database.query(VornamenW).filter(VornamenW.n_id == n_id).delete()
    database.commit()
    return {"success": True}


@app.delete("/delete_lastname_by_id")
def delete_lastname_by_id(n_id: int, database: Session = Depends(get_db)):
    database.query(Nachnamen).filter(Nachnamen.n_id == n_id).delete()
    database.commit()
    return {"success": True}


@app.delete("/delete_company_by_id")
def delete_company_by_id(f_id: int, database: Session = Depends(get_db)):
    database.query(Firmen).filter(Firmen.f_id == f_id).delete()
    database.commit()
    return {"success": True}


@app.delete("/delete_town_by_name")
def delete_town_by_name(name: str, plz: int = None, database: Session = Depends(get_db)):
    if not plz:
        """Erster Eintrag wird gelöscht?"""
        database.query(Staedte).filter(Staedte.name == name).delete()
        database.commit()
    else:
        database.query(Staedte).filter(Staedte.name == name, Staedte.plz == plz).delete()
        database.commit()
    return {"success": True}


@app.delete("/delete_street_by_name")
def delete_street_by_name(name: str, database: Session = Depends(get_db)):
    database.query(Strassen).filter(Strassen.name == name).delete()
    database.commit()
    return {"success": True}


@app.delete("/delete_firstname_by_name")
def delete_firstname_by_name(name: str, gender=Gender, database: Session = Depends(get_db)):
    if gender.value == "male":
        database.query(VornamenM).filter(VornamenM.name == name).delete()
    else:
        database.query(VornamenW).filter(VornamenW.name == name).delete()
    database.commit()
    return {"success": True}


@app.delete("/delete_lastname_by_name")
def delete_lastname_by_name(name: str, database: Session = Depends(get_db)):
    database.query(Nachnamen).filter(Nachnamen.name == name).delete()
    database.commit()
    return {"success": True}


@app.delete("/delete_company_by_name")
def delete_company_by_name(name: str, database: Session = Depends(get_db)):
    database.query(Firmen).filter(Firmen.name == name).delete()
    database.commit()
    return {"success": True}


@app.delete("/delete_town_by_plz")
def delete_town_by_plz(plz: int, database: Session = Depends(get_db)):
    database.query(Staedte).filter(Staedte.plz == plz).delete()
    database.commit()
    return {"success": True}


"""----------------------------------------------------------------------"""
