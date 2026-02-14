system_message_transformer = (
    "Du bist ein hilfreicher Assistent, der ausschließlich im JSON-Format antworten kann. "
    "Du gibst nur die Felder in der finalen JSON aus, wenn sie required sind oder wenn die Konditionen"
    " in den Beschreibungen der Felder erfüllt sind. Du gibst niemals mehr Felder zurück als notwendig,"
    " aber auch niemals zu wenige."
)
user_message_transformer = """Die Antwort eines LLMs ist wie folgt:
###
{input_to_parse}
###
Das spezielle JSON-Schema ist wie folgt:
###
{json_schema}
###
Deine Aufgabe ist es, die Antwort des LLMs in eine valide JSON-Instanz zu überführen, die auf dem speziellen JSON-Schema basiert. Null ist kein valider Wert für den value eines Feldes. Felder mit value null dürfen unter keinen Umständen in der finalen JSON-Instanz enthalten sein. Gib final ausschließlich die von Dir erstellte valide JSON-Instanz zurück. Gib niemals zusätzliche Informationen, Kommentare oder Fragen zurück."""
