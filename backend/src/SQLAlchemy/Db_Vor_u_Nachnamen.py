from sqlalchemy import Column, String, Integer
from src.SQLAlchemy.Base import Base


class VornamenW(Base):
    __tablename__ = "VornamenW"

    n_id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)


class VornamenM(Base):
    __tablename__ = "VornamenM"

    n_id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)


class Nachnamen(Base):
    __tablename__ = "Nachnamen"

    n_id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
