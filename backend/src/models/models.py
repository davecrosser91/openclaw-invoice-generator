from pydantic import BaseModel, Field


class GeneratedProduct(BaseModel):
    name: str = Field(
        description="Der Name des vom Unternehmen verkauften Produkts. Beispiel: BeispielFirma "
        "stellt Kupfer-Testplatten her. -> Name: Testplatte ODER Regrapes verkauft "
        "Softwarelizenzen für den Rechnungsgenerator 'Invoiceman': Name: Invoiceman "
        "Software-Lizenz",
    )

    price: float = Field(
        description="Der Preis des Produkts. Beispiel: Der Preis der Testplatten beträgt"
        " 5,50€ pro Platte -> Preis: 5,50 ODER Der Preis für eine "
        "Invoiceman-Softwarelizenz beträgt 300€ pro Monat. -> Preis: 300",
    )
    unity1_price: str = Field(
        description="Die Einheit, für die der Preis gilt. Die Preise sind immer pro"
        " 'etwas'. Beispiel: 75€/50ml -> Einheit: pro 50ml ODER 50€ pro"
        " Kilogramm -> Einheit: pro Kilogramm",
    )
    quantity: float = Field(
        description="Die gekaufte Menge des Produkts. Beispiel: "
        "Beispiel: 50 ml -> Menge: 50 ODER 23,5 kg -> Menge: 23,5",
    )
    unity: str = Field(
        description="Die Einheit der Menge, in der das Produkt gekauft wird. Beispiel: 50ml "
        "-> Einheit: ml ODER 23,5kg -> Einheit: kg",
    )
    taxrate: str = Field(
        description="Extrahieren Sie die Mehrwertsteuer (MwSt.) für das spezifische "
        "Produkt aus dem Kontext. Wenn aus dem Kontext hervorgeht, dass das Produkt "
        "weder einen ermäßigten Mehrwertsteuersatz von 0% noch von 7% hat, dann hat"
        " es einen Mehrwertsteuersatz von 19%. Geben Sie die Mehrwertsteuer IMMER "
        "in PROZENT an. Die Ausgabe MUSS entweder 0%, 7% oder 19% betragen.",
    )


class ProductContext(BaseModel):
    prompts: list
    responses: list
