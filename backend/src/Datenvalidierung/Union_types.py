from typing import Union, List, Type
from sqlalchemy import Column
from src.SQLAlchemy.Base import Base

"""src/SQLAlchemy/PostgresConnection.py --> Typ für die Erstellung von Tabellen"""
TableColumnsType = Union[Column, List[Column]]
TableORMTypes = Union[Type[Base]]
