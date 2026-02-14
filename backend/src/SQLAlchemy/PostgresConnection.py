import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from dataclasses import dataclass
from src.Datenvalidierung.Union_types import TableColumnsType, TableORMTypes
from src.SQLAlchemy.Base import Base


@dataclass
class PostgressConnection:
    url: str

    def create_session(
        self,
        autocommit: bool,
        autoflush: bool,
        bind: sqlalchemy.engine.base.Engine = None,
    ):
        bind = self.create_engine() if not bind else bind
        return sessionmaker(autocommit=autocommit, autoflush=autoflush, bind=bind)

    def create_engine(self):  # pw=None
        # pw = self.pw if not pw else pw
        return create_engine(self.url)

    def retrieve_db_session(self, session: sqlalchemy.orm.session.sessionmaker = None):
        session = self.create_session(False, False) if not session else session
        db = session()
        try:
            yield db
        finally:
            if db:
                db.close()

    def create_table(
        self,
        table_columns: TableColumnsType,
        table_name: str,
        engine: sqlalchemy.engine.base.Engine = None,
        metadata: sqlalchemy.sql.schema.MetaData = None,
        w_return: bool = False,
    ):
        if not engine:
            engine = self.create_engine()
        if not metadata:
            metadata = MetaData()

        table = Table(
            table_name,
            metadata,
            *table_columns if isinstance(table_columns, list) else table_columns,
        )
        metadata.create_all(engine)
        if w_return:
            return table
        else:
            print(f"Tabelle: {table_name} wurde erfolgreich erstellt.")

    def create_table_w_orm_classes(
        self,
        *args: TableORMTypes,
        engine: sqlalchemy.engine.base.Engine = None,
    ):
        if not engine:
            engine = self.create_engine()

        Base.metadata.create_all(bind=engine)
        Session = self.create_session(False, False)
        session = Session()

        for table_class in args:
            session.query(table_class).first()
            print("Successfully created:")
            print(table_class)

    def delete_table(
        self,
        table_name: str,
        engine: sqlalchemy.engine.base.Engine = None,
        metadata: sqlalchemy.sql.schema.MetaData = None,
    ) -> None:
        if not engine:
            engine = self.create_engine()
        if not metadata:
            metadata = MetaData()

        metadata.reflect(bind=engine)
        table = metadata.tables[table_name]
        if table is not None:
            Base.metadata.drop_all(engine, [table], checkfirst=True)
            print(f"Tabelle: {table_name} wurde erfolgreich gelöscht.")
        else:
            print("Tabelle war None")


def main():
    conn = PostgressConnection(url="postgresql://Benedikt:mysecret@localhost:8005/postgres_db")
    #
    # Tablle erstellen ---------------------------------------------------
    table_columns = [
        Column("id", Integer, primary_key=True),
        Column("name", String, nullable=False),
        Column("plz", Integer, nullable=False),
    ]
    tabelle_name = "deutsche_Staedte"
    conn.create_table(table_name=tabelle_name, table_columns=table_columns)
    # ----------------------------------------------------------------------
    # # Tabelle löschen
    # tabelle_name = "deutsche_Staedte"
    # conn.delete_table(table_name=tabelle_name)
    # #----------------------------------------------------------------------


if __name__ == "__main__":
    main()
