from sqlalchemy import Column, String, Integer
from src.SQLAlchemy.Base import Base


class Strassen(Base):
    __tablename__ = "Strassen"

    s_id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
