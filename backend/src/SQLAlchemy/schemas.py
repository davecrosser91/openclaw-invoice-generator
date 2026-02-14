from pydantic import BaseModel
from src.Datenvalidierung.Enum_Classes import Gender


class StadtMitPlz(BaseModel):
    name: str
    plz: int


class Strasse(BaseModel):
    name: str


class Vorname(BaseModel):
    name: str
    gender: Gender


class Nachname(BaseModel):
    name: str


class GenderSchema(BaseModel):
    gender: Gender


class Firma(BaseModel):
    name: str
    description: str


def main():
    male = GenderSchema(gender="male")
    if male == GenderSchema.gender.male:
        print(True)
    else:
        print("female")


if __name__ == "__main__":
    main()

# sqlalchemy.url = postgresql://Benedikt:mysecret@localhost:8005/postgres_db


# def upgrade() -> None:
#     op.create_table(
#         "deutsche_Staedte",
#         sa.Column("id", sa.Integer, primary_key=True),
#         sa.Column("name", sa.String, nullable=False),
#         sa.Column("plz", sa.Integer, nullable=False),
#     )
#
#
# def downgrade() -> None:
#     op.drop_table("Staedte")
