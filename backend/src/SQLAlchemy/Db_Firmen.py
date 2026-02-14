from sqlalchemy import Column, String, Integer
from src.SQLAlchemy.Base import Base


class Firmen(Base):
    __tablename__ = "deutscheFirmen"

    f_id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    description = Column("description", String, nullable=False)
