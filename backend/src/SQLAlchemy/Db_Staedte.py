from sqlalchemy import Column, String, Integer
from src.SQLAlchemy.Base import Base


class Staedte(Base):
    __tablename__ = "deutsche_Staedte"

    t_id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    plz = Column("plz", Integer, nullable=False)

    # def __init__(self, t_id, name, plz):
    #     self.t_id = t_id
    #     self.name = name
    #     self.plz = plz
    #
    # def __repr__(self):
    #     return f"(ID: {self.t_id}, Name: {self.name}, PLZ: {self.plz})"
    #
