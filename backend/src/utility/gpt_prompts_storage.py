from dataclasses import dataclass

"""All prompts (with parameters) stored in dataclasses for better clarity"""


@dataclass
class Entity_Finder_Prompt:
    non_product_placeholder: list[str]
    product_placeholder: list[str]
    html_text: str

    def get_prompt(self):
        return (
            "## System: Du bist ein Anwaltsgehilfe und kannst ausschließlich im JSON- Format Antworten. "
            "Du kannst keine Erklärungen geben."
            "Im Folgenden ist der exakte Textinhalt einer Rechnung dargestellt. "
            f"Textinhalt: {self.html_text}"
            "### Aufgabe: Finde und ersetze alle Entitäten und Personen im Text der Rechnung durch einen der "
            f"folgenden Platzhalter: {self.non_product_placeholder}. "
            "Die Bedeutung der Platzhalter ist jeweils innerhalb der geschweiften Klammern. Ersetze nur Wörter "
            "im Text bei denen du dir sicher bist das sie durch einen der Platzhalter sinnvollerweise ersetzt "
            "werden können. Beziehe auch die Hierarchie des Textes in die Entscheidung mit ein."
            "Ersetze zusätzlich Produkte und Produkteigenschaften in Tabellen oder Listen durch folgende "
            f"Platzhalter: {self.product_placeholder} und nummeriere sie entsprechend ihrer Position in der "
            "Tabelle oder Liste durch, in dem du dem jeweiligen Platzhalter die Position als Zahl anhängst. "
            "Bsp, wenn das Produkt an erster Stelle steht, soll der Platzhalter product_name_1 sein, für "
            " das zweite Produkt product_name_2 usw. . Verwende AUSSCHLIEßLICH die vorgegebenen Platzhalter und  "
            f"erfinde KEINE zusätzlichen Platzhalter. Gebe ein dictionary mit den Wörtern zurück die "
            "ersetzt wurden und die dazugehörigen Platzhalter. Das Wort im Text soll dabei der key sein und der "
            "Platzhalter der value. Achte darauf die EXAKTE SCHREIBWEISE der Wörter im Text zu verwenden."
            "Entferne KEINE Doppelleerzeichen, Punkte/Doppelpunkte, Kommas, Bindestriche, Anführungszeichen, "
            "oder andere Zeichen in den ersetzten Wörtern um eine nahtlose Weiterverarbeitung der "
            "dictionaries zu gewährleisten. Ersetze Zeilenumbrüche in den erkannten Entitäten unbedingt durch "
            "das Tabulatorzeichen 'backslash'n und hänge das Tabulatorzeichen an das nachfolgende Wort "
            "an. Bsp: Entität:  "
            "Hallo"
            "Welt"
            "Wird zu Entität: Hallo'backslash'nWelt. Dies ist wichtig um die Information des Zeilenumbruchs "
            "auch im dictionary key zu behalten. Nutze die richtige Version ohne '' zwischen backslash und n. "
            "Liefere NIEMALS zusätzliche Erklärungen."
        )


@dataclass
class Template_Modifier_Prompt:
    html: str

    def get_modify_product_count_prompt(self, product_count: int):
        return (
            "## System: Du bist ein Webdeveloper und bist spezialisiert darauf HTML Code zu analysieren und "
            f"bei Bedarf den HTML Code anhand von Kundenwünschen entsprechend zu ändern und "
            f"zu optimieren. Du kannst zudem nur im JSON-Format Antworten und lieferst "
            f"NIEMALS zusätzliche Erklärungen.  "
            f"Im Folgenden ist der exakte HTML Code einer Rechnung gegeben."
            f"HTML: {self.html}"
            f"### Kontext: Ein Kunde möchte, dass der vorliegenden HTML Code so angepasst wird, "
            f"dass die Rechnung Platz für {product_count} Produkte auf der Rechnung bietet."
            f"### Aufgabe: Passe den HTML Code so an, dass die vom Kunden gewünschte Anzahl von "
            f"{product_count}  Produkten auf der Rechnung dargestellt wird. Passe hierfür die "
            f"im HTML Code befindliche Struktur in der die Produktdetails dargestellt entsprechend "
            f"der Anzahl an gewünschten Produkten an. Passe zudem auch die Koordinaten aller "
            f"von der Abänderung der Struktur betroffenen Elemente im HTML Code an, um zu Vermeiden, "
            f"dass es beim Rendern des HTML Codes zu Überlappungen der Inhalte der Elemente "
            f"aufgrund der Abänderung der Produktanzahl im HTML Code kommt."
            f"Gebe final den korrigierten HTML Code als Text zurück. "
            f"Liefere keine zusätzlichen Erklärungen"
        )
