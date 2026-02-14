import json


def dump_dicts_in_json(data: dict, path: str) -> None:
    """
    Does what the name implies. Saves the passed dicts in the path as json.

    :param data: Data to be saved as dict.
    :param path: Path where the dict is to be saved.
    :return: None. dict was saved as json on the path.
    """
    with open(path, "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, indent=4)
