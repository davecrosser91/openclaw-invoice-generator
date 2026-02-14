import json

dictionary = {}
with open(
    "src/Datenbank/json_storage/companies/Deutsche_Firmen.txt",
    "r",
    encoding="utf-8-sig",
) as f:
    contents = f.read()
    content = contents.strip().split("\n")  # splitten an den tabs
    gefilterte_liste = list(filter(lambda x: x != "", content))
    for i in range(1, len(gefilterte_liste), 2):
        dictionary[gefilterte_liste[i - 1]] = gefilterte_liste[i]

with open("json_storage/deutsche_firmen.json", "w") as json_file:
    json.dump(dictionary, json_file, indent=2)
