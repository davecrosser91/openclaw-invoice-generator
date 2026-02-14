import json
import locale
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, Any
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTImage
from bs4 import BeautifulSoup
from src.PyPPeteer.Python_html_to_pdf import html_to_pdf
from src.document_generator_python_backend.src.TemplateGenerator import (
    TemplateGenerator,
)
from src.non_specific_scripts.dumb_dicts_in_json import dump_dicts_in_json
from pdfminer.image import ImageWriter
from math import ceil
from dotenv import load_dotenv

load_dotenv()
GLOBAL_LIST = []


def show_ltitem_hierarchy(o: Any, name: str, depth: int = 0) -> None:
    """
    Show location and text of LTItem and all its descendants
    :param name: Name unter der die Images der PDF gespeichert werden.
    :param o: Iterable das mit PDF Miner erstellt wird (pages = extract_pages(path), path = Speicherort der PDF)
    :param depth: Tiefe innerhalb des Elements. Bsp:
                Page d = 0
                  TextBox d = 1
                      TextLine d = 2
                         Character d = 3
                         Anno      d = 3
    :return: None. Füllt die GLOBAL_LIST mit allen LTItems.
    """

    if depth == 0:
        print("element                        x1    y1   x2     y2      font  text")
        print("------------------------------ ----- ---- -----  ------  ----- -----")
    bbox = get_optional_bbox(o)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    font = get_optional_fontinfo(o)
    if get_indented_name(o, depth) == "LTCurve":
        GLOBAL_LIST.append(
            {
                "type": f"{get_indented_name(o, depth)}",
                "bbox": {
                    "left": bbox[0],
                    "bottom": bbox[1],
                    "width": width,
                    "height": height,
                },
                "text": get_optional_text(o),
                "font": font[0],
                "size": font[1],
                "fill": o.fill,
                "stroking_color": o.stroking_color,
                "non_stroking_color": o.non_stroking_color,
                "line_width": o.linewidth,
                "points": o.original_path,
            }
        )
        # print(o)
    elif get_indented_name(o, depth) == "LTRect":
        GLOBAL_LIST.append(
            {
                "type": f"{get_indented_name(o, depth)}",
                "bbox": {
                    "left": bbox[0],
                    "bottom": bbox[1],
                    "width": width,
                    "height": height,
                },
                "text": get_optional_text(o),
                "font": font[0],
                "size": font[1],
                "fill": o.fill,
                "stroking_color": o.stroking_color,
                "non_stroking_color": o.non_stroking_color,
                "line_width": o.linewidth,
                "points": o.original_path,
            }
        )

    elif get_indented_name(o, depth) == "LTLine":
        GLOBAL_LIST.append(
            {
                "type": f"{get_indented_name(o, depth)}",
                "bbox": {
                    "left": bbox[0],
                    "bottom": bbox[1],
                    "width": width,
                    "height": height,
                },
                "text": get_optional_text(o),
                "font": font[0],
                "size": font[1],
                "fill": o.fill,
                "stroking_color": o.stroking_color,
                "non_stroking_color": o.non_stroking_color,
                "line_width": o.linewidth,
                "points": o.original_path,
            }
        )

    elif get_indented_name(o, depth) == "LTImage":
        GLOBAL_LIST.append(
            {
                "type": f"{get_indented_name(o, depth)}",
                "bbox": {
                    "left": bbox[0],
                    "bottom": bbox[1],
                    "width": width,
                    "height": height,
                },
            }
        )
        o.name = name
        """Speichern des Bilds"""
        # extract_picture_from_pdf(image=o)

    elif get_indented_name(o, depth) == "LTPage":
        if o.groups:
            GLOBAL_LIST.append(
                {
                    "type": f"{get_indented_name(o, depth)}",
                    "bbox": {
                        "left": bbox[0],
                        "bottom": bbox[1],
                        "width": width,
                        "height": height,
                    },
                    "bbox_LRTB": {
                        "left": round(o.groups[0].x0),
                        "bottom": round(o.groups[0].y0),
                        "width": round(o.groups[0].width),
                        "height": round(o.groups[0].height),
                    },
                }
            )

        else:
            GLOBAL_LIST.append(
                {
                    "type": f"{get_indented_name(o, depth)}",
                    "bbox": {
                        "left": bbox[0],
                        "bottom": bbox[1],
                        "width": width,
                        "height": height,
                    },
                }
            )

    # print(o)
    # if get_indented_name(o, depth) == "LTChar":
    #     GLOBAL_LIST.append({"type": f'{get_indented_name(o, depth)}',
    #                         "bbox": {"left": bbox[0], "bottom": bbox[1], "width": width, "height": height},
    #                         "text": get_optional_text(o), "font": font[0], "size": font[1],
    #                         "fill": o.fill, "non_stroking_color": o.non_stroking_color, "line_width": o.linewidth,
    #                         "points": o.original_path}
    #                        )
    elif get_indented_name(o, depth) == "LTTextBoxHorizontal":
        GLOBAL_LIST.append(
            {
                "type": f"{get_indented_name(o, depth)}",
                "bbox": {
                    "left": bbox[0],
                    "bottom": bbox[1],
                    "width": width,
                    "height": height,
                },
                "text": get_optional_text(o),
                "font": font[0],
                "size": font[1],
            }
        )
    elif get_indented_name(o, depth) == "LTChar":
        GLOBAL_LIST.append(
            {
                "type": f"{get_indented_name(o, depth)}",
                "bbox": {
                    "left": bbox[0],
                    "bottom": bbox[1],
                    "width": width,
                    "height": height,
                },
                "text": get_optional_text(o),
                "font": font[0],
                "size": font[1],
            }
        )
    elif get_indented_name(o, depth) == "LTAnno":
        GLOBAL_LIST.append(
            {
                "type": f"{get_indented_name(o, depth)}",
                "bbox": {
                    "left": bbox[0],
                    "bottom": bbox[1],
                    "width": width,
                    "height": height,
                },
                "text": get_optional_text(o),
                "font": font[0],
                "size": font[1],
            }
        )
    # else:
    #     GLOBAL_LIST.append({"type": f'{get_indented_name(o, depth)}',
    #                         "bbox": {"left": bbox[0], "bottom": bbox[1], "width": width, "height": height},
    #                         "text": get_optional_text(o), "font": font[0], "size": font[1]})
    print(
        f"{get_indented_name(o, depth):<30.30s} {get_optional_bbox(o)} {get_optional_fontinfo(o)}{get_optional_text(o)}"
    )

    if isinstance(o, Iterable):
        for i in o:
            show_ltitem_hierarchy(i, depth=depth + 1, name=name)


def get_indented_name(o: Any, depth: int) -> str:
    """Indented name of LTItem"""
    # return '  ' * depth + o.__class__.__name__
    return o.__class__.__name__


def get_optional_bbox(o: Any) -> list[int]:
    """Bounding box of LTItem if available, otherwise empty string"""
    # if hasattr(o, 'bbox'):
    #     return ''.join(f'{i:<4.0f}' for i in o.bbox)
    # return ''
    if hasattr(o, "bbox"):
        return [round(bbox) for bbox in o.bbox]
        # return [math.floor(bbox) for bbox in o.bbox]
    return [0, 0, 0, 0]


def get_optional_text(o: Any) -> str:
    """Text of LTItem if available, otherwise empty string"""
    if hasattr(o, "get_text"):
        return o.get_text().strip()
    return ""


def get_optional_fontinfo(o: Any) -> list[str]:
    """Font info of LTChar if available, otherwise empty string"""
    if hasattr(o, "fontname") and hasattr(o, "size"):
        # return f'{o.fontname} {round(o.size)}pt'
        # actual_font_size_pt = int(char.size) * 72 / 96
        return [f"{o.fontname}", f"{int(o.size * 72 / 96)}pt"]
    # return ''
    return ["", ""]


def return_global():
    return GLOBAL_LIST


def safe_html(html: str, safe_path: str) -> None:
    with open(safe_path, "w", encoding="utf-8") as f:
        f.write(html)


def map_characters_font_specs_to_bbox(list_lt_items: list[dict]) -> list[dict]:
    """
    Ergebnis ist, dass jeder Line in einer Textbox (\n als Separator) die Möglichkeit einer eigenen Font und Size
    gegeben wird. Textboxen werden extrahiert. Text wird auf \n untersucht. Wenn kein \n vorhanden ist, wird die Font
    und Size des ersten Buchstaben in der Line genommen und auf die Zeile angewandt.
    Wenn \n gefunden werden, werden die Texte aufgeteilt und jede Line bekommt die Font und Size des ersten Buchstaben
    der Line. Gespeichert wird die Information in den dict keys "font" und "size" der Textboxen.
    Wenn ein Text mehrere Lines enthält, sind TEXTBOX["font"] und TEXTBOX["size"] Listen und keine str bzw. ints.

    :param list_lt_items: Liste mit den LTItems. Parameter sind in dicts gespeichert.
    :return: Der modifizierte Input ohne Characters und Annotations.
    """

    all_textbox_indx: list[int] = [
        count
        for count, lt_dict in enumerate(list_lt_items)
        if lt_dict["type"] == "LTTextBoxHorizontal"
    ]
    all_textbox_indx.append(
        len(list_lt_items) - 1
    )  # Letzte Zeile von list_lt_items anhängen, um alle Inhalte zu splitten.
    splitted_into_bboxes: list[list[dict]] = [
        list_lt_items[all_textbox_indx[num] : all_textbox_indx[num + 1]]
        for num in range(len(all_textbox_indx) - 1)
    ]
    all_textbox_indx.pop(
        -1
    )  # Letze zeile wieder entfernen, da die Varaible später noch gebraucht wird und nur die Positionen der Boxen enthalten soll.
    for bbox_count, bbox_content in enumerate(splitted_into_bboxes):
        """Durchsuchen des bbox_content auf "Anomalien". Es kommt vor, dass Leerzeichen erkennt werden und als LTChar 
        mit text = "" abgespeichert werden. Zusätzlich wird im Normalfall aber auch eine Annotation eingefügt (LTAnno) 
        die von PDFMiner als Leerzeichen eingesetzt wird. Es kommt (sehr sehr selten) vor, dass nach einem LTChar mit
         text = "", kein LTAnno eingefügt wird. Der Fall muss gefunden werden, sodass der Algorithmus in 
         if len(splitted_sentence) > 1: funktioniert. Es werden also alle dicts mit type = LTChar und text = "" entfernt
         WENN ihnen ein dict mit type = LTAnno folgt. Wenn jedoch kein dict mit type = LTAnno wird das dict mit 
          type = LTChar und text = "" NICHT entfernt und es fungiert als Separator."""

        bbox_content: list[dict] = [
            dicts
            for count, dicts in enumerate(bbox_content)
            if not (
                dicts["type"] == "LTChar"
                and dicts["text"] == ""
                and bbox_content[count + 1]["type"] == "LTAnno"
            )
        ]  # if not (dicts["type"] == "LTChar" and dicts["text"] == "")
        list_with_word_params = []
        font = []
        font_size = []
        word = ""
        splitted_sentence = [
            list(filter(lambda x: x != "", subset.split(" ")))
            for subset in bbox_content[0]["text"].split("\n")
        ]
        if len(splitted_sentence) > 1:
            for dicts in bbox_content:
                if dicts["type"] == "LTChar" and dicts["text"] != "":
                    # Normaler Character wird appended an das aktuelle Wort
                    word = word + dicts["text"]
                    font.append(dicts["font"])
                    font_size.append(dicts["size"])
                if dicts["type"] == "LTAnno" or (dicts["type"] == "LTChar" and dicts["text"] == ""):
                    # Ende des Wortes. Ende entweder durch LTAnno oder ein LTChar mit text = "".
                    # Wort wird an Wort Liste appended mit seinen Fonts und Sizes
                    list_with_word_params.append(
                        {
                            "word": word,
                            "font_per_char": font,
                            "font_size_per_char": font_size,
                        }
                    )
                    word = ""
                    font = []
                    font_size = []
            font_list_textbox, font_size_list_textbox = [], []

            for entry in splitted_sentence:
                """Man geht der Reihenfolge nach durch, deswegen passt es auch wenn man es immer an die Listen appendet. Reihenfolge ist fix und kann dann auch so auf die einzelnen Linien angewendet werden."""
                """Derzeit ist die Länge egal. Wird 2 mal das gleiche gemacht. Vlt für später die Unterschiedung um einzelne Wörter verschiedene Font zu geben."""
                # if len(entry) > 1:
                #     for entry1 in list_with_word_params:
                #         entry1["word"] = entry1["word"].rstrip(" ")
                #         if entry1["word"] == entry[0]:
                #             font_list_textbox.append(entry1["font_per_char"][0])
                #             font_size_list_textbox.append(entry1["font_size_per_char"][0])
                # else:
                #     for entry2 in list_with_word_params:
                #         entry2["word"] = entry2["word"].rstrip(" ")
                #         if entry2["word"] == entry[0]:
                #             font_list_textbox.append(entry2["font_per_char"][0])
                #             font_size_list_textbox.append(entry2["font_size_per_char"][0])
                for entry1 in list_with_word_params:
                    entry1["word"] = entry1["word"]
                    if entry1["word"] == entry[0]:
                        font_list_textbox.append(entry1["font_per_char"][0])
                        font_size_list_textbox.append(entry1["font_size_per_char"][0])

            list_lt_items[all_textbox_indx[bbox_count]]["font"] = font_list_textbox
            list_lt_items[all_textbox_indx[bbox_count]]["size"] = font_size_list_textbox

        else:
            """Wenn Textbox nur 1 Zeile hat wird für die gesamte Box 1 Font und 1 Size angegeben. 
               Ist egal von welchem Character."""
            list_lt_items[all_textbox_indx[bbox_count]]["font"] = bbox_content[1]["font"]
            list_lt_items[all_textbox_indx[bbox_count]]["size"] = bbox_content[1]["size"]
            # man braucht Characters und Annos (Leerzeichen) nicht mehr.
    return [entry for entry in list_lt_items if entry["type"] not in ["LTChar", "LTAnno"]]


def gen_html_from_lt_items(data: list, page_dim: dict = None, *args) -> str:
    """
    Umwandeln der LTItems in HTML Code mithilfe von (hauptsächlich) div Elementen.

    :param page_dim: Maße des Outputs: DIN A4 am sinnvollsten mit 595px x 842px
    :param data: Alle LTItems dem eingelesenen PDF in einer Liste
    :return: soup.prettify() → HTML String.
    """
    # Create HTML document
    if page_dim is None:
        page_dim = {"width": 595, "height": 842}
    invoice_title = ";Rechnung R0020923366"
    author = "Benedikt Fetzer"
    creation_date = datetime.now()
    description = "Test Template erstellt mit PDFMiner und gerendert durch WeasyPrint."

    html_doc = (
        f"<!DOCTYPE html><html lang='de'><head><meta charset='utf-8' /><meta content='"
        f" initial-scale=1.0' name='viewport' /><meta name='author' content='{author}' />"
        f"<meta name='description' content='{description}' /><meta name='date' content='{creation_date}' />"
        f"<title>{invoice_title}</title><link"
        " href='https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css' rel='stylesheet' "
        "/></head><body class='bg-white'>"
    )
    # margin, padding, background, width, height = "margin", "padding", "background-color", "width", "height"
    # margin_v, padding_v, background_v, width_v, height_v = 0, 0, "white", 100, 100
    # html_doc = f"<!DOCTYPE html><html lang='de'><head><meta charset='utf-8' /><meta content='" \
    #            f" initial-scale=1.0' name='viewport' /><meta name='author' content='{author}' />" \
    #            f"<meta name='description' content='{description}' /><meta name='date' content='{creation_date}' />" \
    #            f"<title>{invoice_title}</title>" \
    #            f"<style>" \
    #            f"body {margin}: {margin_v}; " \
    #            f"    {padding}: {padding_v};" \
    #            f"    {background}: {background_v};" \
    #            f"    {width}: {width_v}%;" \
    #            f"    {height}: {height_v}vh;" \
    #            f"</style>" \
    #            f"<link href='https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css' rel='stylesheet' />" \
    #            f"</head><body class='bg-white'>"

    soup = BeautifulSoup(html_doc, "html.parser")

    # Create HTML elements from LTItems
    body = soup.body
    if data[0]["type"] != "LTPage":
        exit("Does not Start with a LTPage Object. Something went wrong,")
    # check for dimension difference
    width_scale, height_scale, needs_to_be_scaled = 1, 1, False
    if (data[0]["bbox"]["width"] != page_dim["width"]) or data[0]["bbox"]["height"] != page_dim[
        "height"
    ]:
        needs_to_be_scaled = True
        width_scale = page_dim["width"] / data[0]["bbox"]["width"]
        height_scale = page_dim["height"] / data[0]["bbox"]["height"]
    div = soup.new_tag("div")
    div["style"] = (
        f"left: {round(data[0]['bbox']['left'] * width_scale)}px; bottom: {round(data[0]['bbox']['bottom'] * height_scale)}px; width: {round(data[0]['bbox']['width'] * width_scale)}px; height: {round(data[0]['bbox']['height'] * height_scale)}px; margin: auto; overflow: hidden; background-color: white; padding: 4px;"
    )

    """der LRTB Ansatz muss noch weiter untersucht werden. Haben nicht alle PDFS. Ist auch etwas kleiner als die normale bbox. Nicht ganz DIN A 4 Konform."""
    # if "bbox_LRTB" in LTItem.keys():
    #     div[
    #         "style"] = f"left: {LTItem['bbox_LRTB']['left']}px; bottom: {LTItem['bbox_LRTB']['bottom']}px; width: {LTItem['bbox_LRTB']['width']}px; height: {LTItem['bbox_LRTB']['height']}px; margin: auto; overflow: hidden; background-color: white; padding: 4px;"
    # else:
    #     div[
    #         "style"] = f"left: {LTItem['bbox']['left']}px; bottom: {LTItem['bbox']['bottom']}px; width: {LTItem['bbox']['width']}px; height: {LTItem['bbox']['height']}px; margin: auto; overflow: hidden; background-color: white; padding: 4px;"

    # div[
    #     "class"] = f"width: {LTItem['bbox']['width']}px; height: {LTItem['bbox']['height']}px; margin: auto; overflow: hidden; background-color: white; padding: 8px;"
    # bod[
    #     "class"] = f"left: {LTItem['bbox_LRTB']['left']}px; bottom: {LTItem['bbox_LRTB']['bottom']}px; width: {LTItem['bbox_LRTB']['width']}px; height: {LTItem['bbox_LRTB']['height']}px; margin: auto; overflow: hidden; background-color: white; padding: 8px;"
    body.append(div)
    for LTItem in data:
        if needs_to_be_scaled:
            for key, value in LTItem["bbox"].items():
                if key == "left" or key == "width":
                    LTItem["bbox"][key] = ceil(value * width_scale)
                elif key == "bottom" or key == "height":
                    LTItem["bbox"][key] = round(value * height_scale)
            if "size" in LTItem.keys() and LTItem["size"]:
                if not isinstance(LTItem["size"], list):
                    LTItem["size"] = f"{round(int(LTItem['size'].rstrip('pt')) * height_scale)}pt"
                else:
                    for line_pos, font_size in enumerate(LTItem["size"]):
                        LTItem["size"][line_pos] = (
                            f"{round(int(font_size.rstrip('.pt')) * height_scale)}pt"
                        )

        if LTItem["type"] == "LTTextBoxHorizontal":
            div = soup.new_tag("div")
            div["class"] = "textbox"
            # LTItem['font'] = "serif"
            # div[
            #     "style"] = f"position: absolute; left: {LTItem['bbox']['left']}px; bottom: {LTItem['bbox']['bottom']}px; width: {LTItem['bbox']['width']}px; height: {LTItem['bbox']['height']}px; font-family: {LTItem['font']}, serif; font-size: {LTItem['size']};" \
            #     if (LTItem['font'] and LTItem[
            #     'size']) else f"position: absolute; left: {LTItem['bbox']['left']}px; bottom: {LTItem['bbox']['bottom']}px; width: {LTItem['bbox']['width']}px; height: {LTItem['bbox']['height']}px;"
            div["style"] = (
                f"position: absolute; left: {LTItem['bbox']['left']}px; bottom: {LTItem['bbox']['bottom']}px; width: {LTItem['bbox']['width']}px; height: {LTItem['bbox']['height']}px; z-index: 1; background-color: transparent;"
                if (LTItem["font"] and LTItem["size"])
                else f"position: absolute; left: {LTItem['bbox']['left']}px; bottom: {LTItem['bbox']['bottom']}px; width: {LTItem['bbox']['width']}px; height: {LTItem['bbox']['height']}px; z-index: 1; background-color: transparent;"
            )
            # lines = [f"<div>{line}</div>" if len(LTItem["text"].split("\n"))>1 else line for line in LTItem["text"].split("\n")]
            # line_str = ""
            # for sep_text in lines:
            #     line_str = line_str + sep_text
            # div.string = line_str
            # Teile den Text in Zeilen auf und füge sie als separate div-Tags hinzu
            lines = LTItem["text"].split("\n")
            for line_count, line in enumerate(lines):
                line_div = soup.new_tag("div")
                line_div["style"] = (
                    f"font-family: serif; font-size: {LTItem['size']};"
                    if isinstance(LTItem["font"], str) and isinstance(LTItem["size"], str)
                    else f"font-family: serif; font-size: {LTItem['size'][line_count]};"
                )

                """Regex um Fehler mit Umlauten zu finden. \xa8 ist der Unicode für ¨ die Umlautpunkte.
                   Bisher wars immer so: Leerzeichen, 'Umlautpunkte',  a,o,u,A,O,U. """
                line = re.sub(
                    r" ([\xa8])([aAouOU])",
                    lambda m: {
                        "\xa8a": "ä",
                        "\xa8A": "Ä",
                        "\xa8o": "ö",
                        "\xa8O": "Ö",
                        "\xa8u": "ü",
                        "\xa8U": "Ü",
                    }[m.group(1) + m.group(2)],
                    line,
                )
                line_div.string = line
                div.append(line_div)

            body.append(div)

        if LTItem["type"] == "LTLine":
            hr = soup.new_tag("hr")
            hr["style"] = (
                f"position: absolute; left: {LTItem['bbox']['left']}px; bottom: {LTItem['bbox']['bottom']}px; width: {LTItem['bbox']['width']}px; height: {LTItem['bbox']['height']}px;"
            )
            body.append(hr)

        if LTItem["type"] == "LTFigure":
            div = soup.new_tag("div")
            div["class"] = "Figure"
            div["style"] = (
                f"position: absolute; left: {LTItem['bbox']['left']}px; bottom: {LTItem['bbox']['bottom']}px; width: {LTItem['bbox']['width']}px; height: {LTItem['bbox']['height']}px;"
            )
            body.append(div)

        if LTItem["type"] == "LTImage":
            img = soup.new_tag("img")
            img["alt"] = "No Pic"
            img["src"] = (
                "src/tests/ai_2.jpg"  # LTItem["text"]  # Hier müsstest du den richtigen Quellpfad angeben
            )
            img["style"] = (
                f"position: absolute; left: {LTItem['bbox']['left']}px; bottom: {LTItem['bbox']['bottom']}px; width: {LTItem['bbox']['width']}px; height: {LTItem['bbox']['height']}px;"
            )
            body.append(img)

        if LTItem["type"] == "LTRect":
            div = soup.new_tag("div")
            div["class"] = "rectangle"
            div["style"] = (
                f"position: absolute; left: {LTItem['bbox']['left']}px; bottom: {LTItem['bbox']['bottom']}px; width: {LTItem['bbox']['width']}px; height: {LTItem['bbox']['height']}px; background-color: rgb({int(LTItem['non_stroking_color'][0] * 255)},{int(LTItem['non_stroking_color'][1] * 255)}, {int(LTItem['non_stroking_color'][2] * 255)});"
            )

            body.append(div)

        if LTItem["type"] == "LTCurve":
            div = soup.new_tag("div")
            div["class"] = "rectangle"  # Fügen Sie eine CSS-Klasse hinzu, um das Styling zu steuern
            div["style"] = (
                f"position: absolute; left: {LTItem['bbox']['left']}px; bottom: {LTItem['bbox']['bottom']}px; width: {LTItem['bbox']['width']}px; height: {LTItem['bbox']['height']}px; background-color: rgb({int(LTItem['non_stroking_color'][0] * 255)},{int(LTItem['non_stroking_color'][1] * 255)}, {int(LTItem['non_stroking_color'][2] * 255)});"
            )

            body.append(div)
            # svg = soup.new_tag("svg", xmlns="http://www.w3.org/2000/svg", width="100%", height="100%")
            # # Festlegen von Farbe und Strichbreite für die Kurve
            # # Definieren der Bezierkurve im SVG-Path-Element
            # curve_path = ""
            # first_time_line = True
            # for curve_coord in LTItem["points"]:
            #     if curve_coord[0] == "m":
            #         curve_path = curve_path + "M" + f"{curve_coord[1][0]}" + f" {curve_coord[1][1]} "
            #     if curve_coord[0] == "l":
            #         if first_time_line:
            #             curve_path = curve_path + "C" + f"{curve_coord[1][0]}" + f" {curve_coord[1][1]},"
            #             first_time_line = False
            #         else:
            #             curve_path = curve_path + f" {curve_coord[1][0]}" + f" {curve_coord[1][1]},"
            #     if curve_coord[0] == "h":
            #         if curve_path.endswith(","):
            #             curve_path = curve_path.rstrip(",")
            #         curve_path = curve_path + " Z"
            #
            # path = soup.new_tag("path", d=curve_path)
            # # path = soup.new_tag("path", d="M{} {} C{} {}, {} {}, {} {}".format(
            # #     LTItem["points"][0][0], LTItem["points"][0][1],  # Startpunkt
            # #     LTItem["points"][1][0], LTItem["points"][1][1],  # Erster Steuerpunkt
            # #     LTItem["points"][2][0], LTItem["points"][2][1],  # Zweiter Steuerpunkt
            # #     LTItem["points"][3][0], LTItem["points"][3][1]  # Endpunkt
            # # ))
            # path["fill"] = LTItem["fill"]  # Keine Füllung
            # path["stroke"] = LTItem["stroking_color"]  # Farbe des Strichs
            # path["stroke-width"] = LTItem["line_width"]  # Strichbreite
            # # Hinzufügen des Path-Elements zum SVG
            # svg.append(path)
            #
            # # Hinzufügen des SVG-Elements zum Body
            # # if len([values for values in LTItem["bbox"].values() if values >0]) == 4:
            # #     body.append(svg)

    return soup.prettify()


def fill_template(
    html_soup: str,
    legit_placeholder_with_data: dict,
    false_placeholder_in_template: list = None,
) -> str:
    """
    NUR KOPIERT
    Datum der letzten Änderung: 06.02.2024
    Ersetzen der Placeholder mit den eigentlichen Werten aus der Invoice.
    Zahlen werden hierbei gemäß den lokalisierten Formatierungseinstellungen des Betriebssystems dargestellt.
    In diesem Fall: 'de_DE.UTF-8'

    :param html_soup: HTML String
    :param false_placeholder_in_template:
    :param legit_placeholder_with_data: Zweites dict im return von match_data_from_invoice_to_placeholders(). Dict in dem
        die Rechnungsdaten mit den Placeholdern gematcht sind.
    :return: In dem Sinne None, weil self.html_template überschrieben wird. Im Grunde genommen ist es ein str, der
        zurückgeliefert wird.
    """

    if false_placeholder_in_template is not None:
        """Durch was sollen die anderen Platzhalter ersetzt werden. Derzeit werden sie durch "" ersetzt."""
        for entry in false_placeholder_in_template:
            html_soup = re.sub(rf"\b{re.escape(entry)}\b", "", html_soup)

    for key, value in legit_placeholder_with_data.items():
        if isinstance(key, int) or isinstance(key, float):
            """Für alle Zahlen"""
            html_soup = re.sub(
                rf"\b{re.escape(str(key))}\b",
                rf"{locale.format_string('%.2f', value, grouping=True)}",
                html_soup,
            )
        elif isinstance(key, str):
            try:
                dt: datetime = datetime.fromisoformat(value)
                # Formatieren des Datums im deutschen Format
                formatted_date: str = dt.strftime("%d.%m.%Y, %H:%M:%S")
                # Ersetze `key` durch das formatierte Datum
                html_soup = re.sub(rf"\b{re.escape(key)}\b", f"{formatted_date}", html_soup)
            except ValueError:
                # `value` entspricht nicht dem ISO-Datumsformat, standardmäßiges Ersetzen der Werte mit Strings.
                html_soup = re.sub(rf"\b{re.escape(key)}\b", f"{value}", html_soup)
    return html_soup


def extract_picture_from_pdf(image: LTImage, outputdir: str = "src/tests/pdfminer_img") -> None:
    """
    Extract Pictures from PDF via PDFMiner.
    Can be used to integrate in the PDF Reconstruction Process.
    :param image:
    :param outputdir: Speicherort
    :return:
    """

    im_writer = ImageWriter(outdir=outputdir)
    im_writer.export_image(image)


def main() -> None:
    import time
    import re

    with open("src/tests/david_invoice_amazon_pminer.html", "r") as f:
        template = f.read()
    pdf_path = "src/tests/selco_searchable_4.pdf"
    path = Path(pdf_path).expanduser()
    from pdfminer.layout import LAParams

    LAparams = LAParams(all_texts=True, detect_vertical=True)
    pages = extract_pages(path, laparams=LAparams)
    pattern = r"/([^/]+)\.pdf$"
    match = re.search(pattern, pdf_path)
    show_ltitem_hierarchy(pages, name=match.group(1))

    GLOBAL_LIST = return_global()
    # del GLOBAL_LIST[0] # war nötig als man beim Speichern in GLOBAl in show_hierarchy noch alles gespeichert hat

    correct_l = map_characters_font_specs_to_bbox(GLOBAL_LIST)

    html = gen_html_from_lt_items(correct_l)

    safe_html(html=html, safe_path="src/tests/TEST_2.html")
    start_time = time.time()
    """In html_to_pdf wurden stylesheet Optionen gerade auskommentiert und die aus der HTML übernommen."""
    # html_to_pdf(html, "src/tests/TEST_1.pdf", dpi=300,
    #             stylesheet=[CSS(string='body { font-family: serif !important; font-size: 8px; }')
    #                         ],
    #             html_as_string=True)
    html_to_pdf(html, "src/tests/TEST_2.pdf", html_as_string=True)
    end_time = time.time()
    print(
        f"Gesamtzeit: {end_time - start_time} Sekunden bzw. {(end_time - start_time) / 60} Minuten."
    )


def main_1() -> None:
    all_placeholder = [
        "{buyer_address}",
        "{buyer_name}",
        "{buyer_employee}",
        "{buyer_email}",
        "{buyer_website}",
        "{buyer_phone}",
        "{buyer_fax}",
        "{buyer_bankdetails}",
        "{buyer_ifforeigntaxidentifier}",
        "{buyer_customerID}",
        "{seller_address}",
        "{seller_name}",
        "{seller_employee}",
        "{seller_email}",
        "{seller_website}",
        "{seller_phone}",
        "{seller_fax}",
        "{seller_bankdetails}",
        "{seller_taxidentifier}",
        "{dateofinvoice}",
        "{dateofdeliveryorservice}",
        "{invoicenumber}",
        "{subtotal}",
        "{taxes}",
        "{total}",
    ]
    product_placeholder = [
        "{product_name_}",
        "{product_price_}",
        "{product_unity_}",
        "{product_quantity_}",
        "{product_sales_tax_percent_}",
        "{product_sales_tax_cost_}",
        "{product_cost_wo_tax_}",
    ]
    with open("src/tests/TEST_1.html", "r") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    # text_html = soup.prettify()
    text = soup.get_text()
    # os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    generator = TemplateGenerator()
    prompt_lehrer = (
        "## System: Du bist ein Deutschlehrer und kannst ausschließlichim JSON-Format antworten. Du kannst keine Erklärungen geben."
        f"Im Folgenden ist ein möglicherweise fehlerhafter Text gegeben. "
        f"Text: {text}"
        f"### Aufgabe: Untersuche den Text auf Rechtschreibfehler bzw. falsch geschriebene Wörter und korrigiere alle Fehler. "
        f"Ziehe auch die im Text enthaltenen Wörter heran um unvollständige Wörter zu vervollständigen. Korrigiere keine Vor- bzw. Nachnamen es sei denn der Name wurde im Zusammenhang des Textes bereits öfters anders geschrieben."
        f"Gebe final ein dictionary zurück, in dem die fehlerhaften Wörter bzw die Rechtschreibfehler die keys sind und die korrigierten Wörter die values. Liefere NIEMALS zusätzliche Erklärungen. "
    )

    prompt = (
        "## System: Du bist ein Anwaltsgehilfe und kannst ausschließlich im JSON- Format Antworten. Du kannst keine Erklärungen geben."
        f"Im Folgenden ist der exakte Textinhalt einer Rechnung gegeben. "
        f"Textinhalt: {text}"
        f"### Aufgabe: Finde und ersetze Entitäten und Personen im Text der Rechnung durch einen der folgenden Platzhalter: {all_placeholder}."
        f" Die Beschreibungen der Platzhalter sind innerhalb der geschweiften Klammern. Ersetze nur Wörter im Text bei denen du dir sicher bist und wenn dir einer der Platzhalter für sinnvoll erscheint."
        f"Beachte, dass einzelne alleinstehnde Ziffern oder Buchstaben in den meisten Fällen einen vorausgehend oder nachfolgenden Kontext haben und selten eine eigene Entität oder Person sind.  "
        f"Ersetze Produkte in Tabellen oder Listen durch folgende Platzhalter und nummeriere sie entsprechend ihrer Position in der Tabelle oder Liste durch in dem du dem Platzhalter die Position als Zahl anhängst: {product_placeholder}. "
        "Gebe ein dictionary mit den Wörtern zurück die ersetzt wurden und die dazugehörigen Platzhalter. Das Wort im Text soll dabei der key sein und der Platzhalter der value. Liefere NIEMALS zusätzliche Erklärungen. "
    )
    # html_w_placeholder = generator.make_html_w_placeholders_from_html(prompt=prompt)
    # data_dict = json.loads(html_w_placeholder)
    # dump_dicts_in_json(data_dict,
    #                    path=fr"src/tests/david_rechnung_final_placeholder_json.json")
    # with open("src/tests/src/tests/david_rechnung_final_placeholder_json.json", 'r') as file:
    #     data_dict = json.load(file)
    # soup_1 = fill_template(html_soup=soup.prettify(), legit_placeholder_with_data=data_dict)
    # print(soup_1)
    dict_w_corrected_words = json.loads(
        generator.correct_misinterpreted_words_from_tesseract(prompt=prompt_lehrer)
    )

    dump_dicts_in_json(dict_w_corrected_words, path=rf"src/tests/TEST_1_corrected_words.json")

    soup_2 = fill_template(
        html_soup=soup.prettify(), legit_placeholder_with_data=dict_w_corrected_words
    )
    html_to_pdf(html, "src/tests/david_rechnung_final_w_placeholder_1.pdf", html_as_string=True)


if __name__ == "__main__":
    main()
    # main_1()
