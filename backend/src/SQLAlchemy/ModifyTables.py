import os
from src.SQLAlchemy.PostgresConnection import PostgressConnection
from sqlalchemy import Column, Integer, String
from src.SQLAlchemy.Db_Strassen import Strassen
from src.SQLAlchemy.Db_Vor_u_Nachnamen import VornamenM, VornamenW, Nachnamen
from src.SQLAlchemy.Db_Staedte import Staedte
from src.SQLAlchemy.Db_Firmen import Firmen
from dotenv import load_dotenv

load_dotenv()
conn = PostgressConnection(url=os.getenv("POSTGRESDB_URL_LOCAL"))
#
# # Tabelle Staedte erstellen ---------------------------------------------------
# table_columns = [
#     Column('id', Integer, primary_key=True),
#     Column('name', String, nullable=False),
#     Column('plz', Integer, nullable=False)
# ]
# tabelle_name = "deutsche_Staedte"
"""Tabellen für Staedte erstellt"""
# conn.create_table(table_name=tabelle_name, table_columns=table_columns)
"""Tabellen für Strassen Vornamen und Nachnamen erstellt"""
# conn.create_table_w_orm_classes(Strassen, VornamenM, VornamenW, Nachnamen)
# conn.create_table_w_orm_classes(VornamenM)
"""Tabelle für Firmen"""
conn.create_table_w_orm_classes(
    Firmen
)  # erstellt alle Tabellen muss ich mal dahinte rkom men warum eigentlich


"""Tabelle löschen"""
# conn.delete_table(table_name="VornamenM")
