import re
from datetime import datetime
import numpy as np
from collections.abc import Mapping, Iterable
from typing import Any

from bs4 import BeautifulSoup, Tag
import asyncio
from src.PDF_Processing.LTItemsExtractor import LTItemExtractor
from src.PDF_Processing.Pyppeteer import extract_div_params
from src.types import JSON
import warnings
from collections import Counter


class LTItemsToHtmlConverter:
    page_width = 595
    page_height = 842

    @staticmethod
    def convert_lt_items_to_line_level(lt_items: list[JSON]) -> list[JSON]:
        """
        The result is that each line in a text box (\n as separator) has the option of its own font and size.
        Text boxes are extracted. The text inside the text boxes is checked for \n. If no \n is present, the font and
        size of the first letter of the text is taken and applied to the whole line.
        If \n are found, the texts are split and each line is given the font and size of the first letter of the
        specific line. The information is then stored in the dict keys "font" and "size" of the respective text boxes.
        If a text contains several lines (separated by \n), dict["font"] and dict["size"] are lists (of str and int)
        and not single str/ints.
        :param lt_items: All LTItems found in a PDF. Found with LTItemExtractor.return_lt_list().
        :return: The modified input WITHOUT characters and annotations.
        """

        all_textbox_indx: list[int] = [
            count
            for count, lt_dict in enumerate(lt_items)
            if lt_dict["type"] == "LTTextBoxHorizontal"
        ]
        all_textbox_indx.append(
            len(lt_items) - 1
        )  # Letzte Zeile von list_lt_items anhängen, um alle Inhalte zu splitten.
        splitted_into_bboxes: list[list[JSON]] = [
            lt_items[all_textbox_indx[num] : all_textbox_indx[num + 1]]
            for num in range(len(all_textbox_indx) - 1)
        ]
        all_textbox_indx.pop(
            -1
        )  # Letze zeile wieder entfernen, da die Varaible später noch gebraucht wird und nur die Positionen der Boxen enthalten soll.
        for bbox_count, bbox_content in enumerate(splitted_into_bboxes):
            """Searching the bbox_content for “anomalies”. It can happen that spaces are recognized and saved as LTChar
               with text = “”. However, an annotation is normally also inserted (LTAnno) which is used by PDFMiner as a 
               space. It happens (very rarely) that no LTAnno is inserted after an LTChar with text = “”. This case must
               be found so that the algorithm in if len(splitted_sentence) > 1: works. This means that all dicts with 
               type = LTChar and text = “” are removed IF they are followed by a dict with type = LTAnno. However, if no
               dict with type = LTAnno follows, the dict with type = LTChar and text = “” is NOT removed and it acts as
               a separator."""

            bbox_content: list[JSON] = [
                dicts
                for count, dicts in enumerate(bbox_content)
                if count == len(bbox_content) - 1
                or not (
                    dicts["type"] == "LTChar"
                    and dicts["text"] == ""
                    and bbox_content[count + 1]["type"] == "LTAnno"
                )
            ]

            list_with_word_params, font, font_size, word = [], [], [], ""
            """ATTENTION: The sentences are splitted with spaces (' ') and unbreakable spaces (\xa0).
               1.08.2024 only 1 Invocie was with unbreakable sapces. Maybe there should be a complete check for 
               unicode before the whole splitting etc. """
            splitted_sentence = [
                list(filter(lambda x: x != "", re.split(r"[ \xa0]+", subset)))
                for subset in bbox_content[0]["text"].split("\n")
            ]
            if len(splitted_sentence) > 1:
                for dicts in bbox_content:
                    if dicts["type"] == "LTChar" and dicts["text"] != "":
                        # Normal character is appended to the current word
                        word = word + dicts["text"]
                        font.append(dicts["font"])
                        font_size.append(dicts["size"])
                    if dicts["type"] == "LTAnno" or (
                        dicts["type"] == "LTChar" and dicts["text"] == ""
                    ):
                        # End of the word. End either by LTAnno or an LTChar with text = “”.
                        # Word is appended to word list with its fonts and sizes
                        list_with_word_params.append(
                            {
                                "word": word,
                                "font_per_char": font,
                                "font_size_per_char": font_size,
                            }
                        )
                        font, font_size, word = [], [], ""

                font_list_textbox, font_size_list_textbox = [], []

                for entry in splitted_sentence:
                    """You go through them in order, which is why it fits if you always apply it to the lists. The order
                       is fixed and can then also be applied to the individual lines. 
                       The length is currently irrelevant.The same thing is done twice. 
                       Maybe for later the differentiation to give individual words different fonts."""
                    for entry1 in list_with_word_params:
                        if entry1["word"] == entry[0]:
                            font_list_textbox.append(entry1["font_per_char"][0])
                            font_size_list_textbox.append(entry1["font_size_per_char"][0])
                            break

                """check_for_similar size and font. If yes -> <p>...</p>"""
                if all([font == font_list_textbox[0] for font in font_list_textbox]) & all(
                    [size == font_size_list_textbox[0] for size in font_size_list_textbox]
                ):
                    lt_items[all_textbox_indx[bbox_count]]["font"] = font_list_textbox[
                        0
                    ]  # bbox_content[1]["font"]
                    lt_items[all_textbox_indx[bbox_count]]["size"] = font_size_list_textbox[
                        0
                    ]  # bbox_content[1]["size"]
                    lt_items[all_textbox_indx[bbox_count]]["text"] = bbox_content[0][
                        "text"
                    ]  # Test 29-05-2024

                else:
                    lt_items[all_textbox_indx[bbox_count]]["font"] = font_list_textbox
                    lt_items[all_textbox_indx[bbox_count]]["size"] = font_size_list_textbox

            else:
                """If the text box has only 1 line, then 1 font and 1 size are specified for the entire box. It does not 
                   matter which character. Tests have shown that text boxes can sometimes have no font and size. 
                   A search is therefore carried out until a character is found whose font and size have content. 
                   If none is found, a warning is issued and the values Arial and 10px are specified by default for 
                   font and size"""
                font_size_set: bool = False
                for bbox in bbox_content:
                    if bbox["font"] and bbox["size"]:
                        lt_items[all_textbox_indx[bbox_count]]["font"] = bbox["font"]
                        lt_items[all_textbox_indx[bbox_count]]["size"] = bbox["size"]
                        font_size_set = True
                        break
                if not font_size_set:
                    lt_items[all_textbox_indx[bbox_count]]["font"] = "Arial"
                    lt_items[all_textbox_indx[bbox_count]]["size"] = "10px"
                    warnings.warn(
                        "Font and size were never set. Default values (Arial, 10px) are set. "
                    )

                # you no longer need characters and annotations (spaces).
        return [entry for entry in lt_items if entry["type"] not in ["LTChar", "LTAnno"]]

    async def gen_html_from_lt_items(self, lt_items: list[JSON], metadata: JSON) -> str:
        """
        Convert the LTItems into HTML code using (mainly) div elements.

        :param lt_items: All LTItems found in a PDF. Found with LTItemExtractor.return_lt_list().
        :param metadata: Various metadata, such as the dimensions of the document title, author description,
                         margin, overflow, background color, padding.
        :return: soup.prettify() → HTML String.
        """
        # Convert lt_items directly to "line" format, where the h-textboxes hold the font specs and not the characters.
        lt_items = self.convert_lt_items_to_line_level(lt_items=lt_items)
        # Check for metadata
        page_width: int = metadata["width"] if "width" in metadata.keys() else self.page_width
        page_height: int = metadata["height"] if "height" in metadata.keys() else self.page_height
        invoice_title: str = (
            metadata["invoice_title"] if "invoice_title" in metadata.keys() else "Rechnung 1"
        )
        author: str = metadata["author"] if "author" in metadata.keys() else "Regrapes"
        creation_date: str = (
            metadata["creation_date"]
            if "creation_date" in metadata.keys()
            else datetime.now().isoformat()
        )
        description: str = metadata["author"] if "author" in metadata.keys() else "Testbeschreibung"
        margin: str | int = metadata["margin"] if "margin" in metadata.keys() else 0
        overflow: str = metadata["overflow"] if "overflow" in metadata.keys() else "hidden"
        padding: int = metadata["padding"] if "padding" in metadata.keys() else 0
        back_grnd_c: str = metadata["back_grnd_c"] if "back_grnd_c" in metadata.keys() else "white"
        font_family: str = (
            metadata["font-family"] if "family" in metadata.keys() else "Arial, sans-serif"
        )

        # Create HTML doc
        html_doc = (
            f"<!DOCTYPE html><html lang='de'><head><meta charset='utf-8' /><meta content='"
            f" initial-scale=1.0' name='viewport' /><meta name='author' content='{author}' />"
            f"<meta name='description' content='{description}' /><meta name='date' content='{creation_date}' />"
            f"<script src='https://cdn.tailwindcss.com'></script>"
            f"<title>{invoice_title}</title></head><body>"
        )

        soup = BeautifulSoup(html_doc, "html.parser")
        head = soup.find("head")
        body = soup.body
        # We just created the HTML, so head and body definitely exist
        assert head is not None
        assert body is not None
        if lt_items[0]["type"] != "LTPage":
            exit("Does not Start with a LTPage Object. Something went wrong.")
        # check for dimension difference
        width_scale, height_scale = self.check_page_dimensions_match(
            lt_page=lt_items[0], page_height=page_height, page_width=page_width
        )
        # append LTPage style to head
        head.append(
            self.generate_page_html_content(
                soup=soup,
                width_px=round(lt_items[0]["bbox"]["width"] * width_scale),
                height_px=round(lt_items[0]["bbox"]["height"] * height_scale),
                margin=margin,
                overflow=overflow,
                padding=padding,
                back_grnd_c=back_grnd_c,
                font_family=font_family,
            )
        )
        # append global CSS styles to head

        # Create HTML elements from LTItems
        if width_scale != 1 and height_scale != 1:
            lt_items = [
                self.scale_lt_item_bboxes(
                    lt_item=entry, width_scale=width_scale, height_scale=height_scale
                )
                for entry in lt_items
            ]

        lt_items_wo_rec_curve_lines = [
            entry for entry in lt_items if entry["type"] not in ["LTRect", "LTCurve", "LTLine"]
        ]
        lt_items_only_rec_curve_lines = [
            entry for entry in lt_items if entry["type"] in ["LTRect", "LTCurve", "LTLine"]
        ]
        if lt_items_only_rec_curve_lines:
            # Actually only to check whether width or height values are 0.
            lt_items_only_rec_curve_lines = self.check_for_unwanted_values(
                dict_to_check=lt_items_only_rec_curve_lines,
                key_to_check=[["bbox", "width"], ["bbox", "height"]],
                check_val_and_replacement=[(0, 1), (0, 1)],
            )
            # Sometimes the whole Page gets registered as Rectangle. Which is a bug from PDFMiner
            # Keep an eye on whether this fits or whether you are eliminating lines /rects/curves unnecessarily.
            lt_items_only_rec_curve_lines = self.drop_erroneous_items(
                lt_items=lt_items_only_rec_curve_lines,
                page_width=page_width,
                page_height=page_height,
            )

            compact_rec_curves_lines = self.merge_split_recs_curves_lines(
                lt_lines_rects_curves=lt_items_only_rec_curve_lines
            )
            # appending the z-index to the items according to their hierarchies
            compact_rec_curves_lines = self.set_div_hierarchies(
                rects_curves_lines=compact_rec_curves_lines
            )
        else:
            compact_rec_curves_lines = []

        for item in lt_items_wo_rec_curve_lines:
            # if width_scale != 1 and height_scale != 1:
            #     item = self.scale_lt_item_bboxes(lt_item=item, width_scale=width_scale, height_scale=height_scale)
            if item["type"] == "LTTextBoxHorizontal":
                body.append(self.generate_h_textbox_html_content(soup=soup, lt_item=item))

            if item["type"] == "LTFigure":
                body.append(self.generate_figure_html_content(soup=soup, lt_item=item))

            if item["type"] == "LTImage":
                body.append(self.generate_image_html_content(soup=soup, lt_item=item))

        for item1 in compact_rec_curves_lines:  # compact_rec_curves_lines
            if item1["type"] == "LTRect":
                body.append(self.generate_rectangle_html_content(soup=soup, lt_item=item1))

            if item1["type"] == "LTCurve":
                body.append(self.generate_curve_html_content(soup=soup, lt_item=item1))

            if item1["type"] == "LTLine":
                body.append(self.generate_line_html_content(soup=soup, lt_item=item1))

        # return self.simplify_ptag_format(soup.prettify(formatter="minimal"))
        # last step. Sort the divs according to the bottom value
        divs = soup.find_all("div")
        pattern_bottom = r"bottom-\[(\d+)px\]"
        pattern_left = r"left-\[(\d+)px\]"

        sorted_divs = sorted(
            divs,  # list of the `div`-elements
            key=lambda lambda_div: (  # type: ignore[misc]
                self.extract_number_for_sorting(
                    str(lambda_div["class"]), pattern_bottom
                ),  # bottom value
                # negation of the left value to enable sorting from small to big
                -self.extract_number_for_sorting(str(lambda_div["class"]), pattern_left),  # left value
            ),
            reverse=True,  # Sort in descending order
        )
        # [re.search(pattern=r'bottom-\[(\d+)px\]', string=div["class"]).group(1) for div in divs]
        # sorted_divs = sorted(divs, [re.search(pattern=r'bottom-\[(\d+)px\]',string=div["class"]).group(1) for div in divs])
        body = soup.body
        assert body is not None
        for div in sorted_divs:
            body.append(div)
        # for old_div, new_div in zip(divs, sorted_divs):
        #     old_div.replace_with(new_div)
        soup = await self.convert_left_to_right_position(soup)
        return str(soup.prettify())

    @staticmethod
    def extract_number_for_sorting(div_class: str, pattern: str):
        match = re.search(pattern, div_class)
        if match:
            return int(match.group(1))
        return float("inf")  # Very high value if no pattern found

    @staticmethod
    def check_page_dimensions_match(lt_page: JSON, page_height: int, page_width: int):
        """
        Checks whether the current dimensions of the document correspond to the desired dimensions and scales them if
        it is not the case. Returns unit scaling factors if current dimension == desired dimension
        :param lt_page: LTPage dict.
        :param page_height: Desired document height.
        :param page_width: Desired document width.
        :return: Width and height scaling factors.
        """

        if (lt_page["bbox"]["width"] != page_width) or lt_page["bbox"]["height"] != page_height:
            width_scale = page_width / lt_page["bbox"]["width"]
            height_scale = page_height / lt_page["bbox"]["height"]
            return width_scale, height_scale
        else:
            return 1, 1

    @staticmethod
    def scale_lt_item_bboxes(lt_item: JSON, width_scale: int, height_scale: int) -> JSON:
        """
        Scales LTItems boundaries according to given width and height scaling factors.
        :param lt_item: Dict with the infos about a specific LTItem element.
        :param width_scale: Width scaling factor.
        :param height_scale: Height scaling factor.
        :return: Scaled LTItem.
        """
        for key, value in lt_item["bbox"].items():
            if key == "left" or key == "width":
                lt_item["bbox"][key] = int(np.ceil(value * width_scale))
            elif key == "bottom" or key == "height":
                lt_item["bbox"][key] = round(value * height_scale)
        if "size" in lt_item.keys() and lt_item["size"]:
            if not isinstance(lt_item["size"], list):
                lt_item["size"] = (
                    f"{round(int(lt_item['size'].rstrip('px')) * height_scale)}px"  # hier war mal statt px pt
                )
            else:
                for line_pos, font_size in enumerate(lt_item["size"]):
                    lt_item["size"][line_pos] = (
                        f"{round(int(font_size.rstrip('.px')) * height_scale)}px"
                    )

        return lt_item

    def merge_split_recs_curves_lines(self, lt_lines_rects_curves: list[JSON]) -> list[JSON]:
        """
        Function to combine and save the lines / rectangles / (curves), some of which are recognized by PDFMiner
        in several pieces and therefore saved in several divs, in one div. Means an element in the HTML code is also
        represented by only 1 div (as it should be). Serves to streamline the final HTML code
        and simplifies the editing of the HTML code by the user
        Example:
        Input:  3 divs for the same line (same bottom value but different widths)
        Output: 1 div with a corrected width /height (depending on the orientation of the line)
        Visual: func(I1:--- I2:-- I3:----) -->  O1:---------
        :param lt_lines_rects_curves: Lines, rectangles (and curves) recognized by PDF Miner.
        :return: Return value  is a list of dicts  with the divs of the lines, rectangles (and curves) combined in only
                 1 div each.
        """

        # merged_lt_items: list[dict] = []
        # First step. Find the items with the same bottom value.
        # dicts_sorted_by_bottom: dict = self.get_dicts_sorted_by_key(lt_items=lt_lines_rects_curves,
        #                                                             key=["bbox", "bottom"])
        # horizontal
        dicts_sorted_by_bottom_and_height = {
            key: self.get_dicts_sorted_by_key(lt_items=items, key=["bbox", "height"])
            for key, items in self.get_dicts_sorted_by_key(
                lt_items=lt_lines_rects_curves, key=["bbox", "bottom"]
            ).items()
        }
        sorted_dicts_h, separate_merged_lt_items_h = self.pre_process_sorted_dicts(
            sorted_dicts=dicts_sorted_by_bottom_and_height,
            horizontal_or_vertical="horizontal",
        )
        """THE VERTICAL DIVS APPROACH IS NOT YET WORKING PROPERLY
           THE VERTICAL APPROACH NEEDS THE SAME AS BELOW BUT NOT WITH SMALLEST LEFT BUT SMALLEST BOTTOM"""
        dicts_sorted_by_left_and_width = {
            key: self.get_dicts_sorted_by_key(lt_items=items, key=["bbox", "width"])
            for key, items in self.get_dicts_sorted_by_key(
                lt_items=lt_lines_rects_curves, key=["bbox", "left"]
            ).items()
        }
        sorted_dicts_v, separate_merged_lt_items_v = self.pre_process_sorted_dicts(
            sorted_dicts=dicts_sorted_by_left_and_width,
            horizontal_or_vertical="vertical",
        )
        merged_lt_items = separate_merged_lt_items_h + separate_merged_lt_items_v
        # Third find the smallest and the biggest value within the values with the same bottom value.
        # Calculate the merged width according to:
        # (biggest_left_div[bbox][left] + biggest_left_div[bbox][width]) - smallest_left_div[bbox][left]
        merged_items_h1 = self.merge_sorted_dicts(
            sorted_dicts=sorted_dicts_h, horizontal_or_vertical="horizontal"
        )
        # merged_items_v1 = self.merge_sorted_dicts(sorted_dicts=sorted_dicts_v, horizontal_or_vertical="vertical")
        merged_lt_items = merged_lt_items + merged_items_h1  # + merged_items_v1
        """delete duplicates via frozenset"""
        merged_lt_items = list({self.to_frozenset(d): d for d in merged_lt_items}.values())
        #         merged_lt_items.append(value[0])

        return merged_lt_items

    def check_for_unwanted_values(
        self,
        dict_to_check: list[JSON],
        key_to_check: str | list[str] | list[list[str]],
        check_val_and_replacement: tuple[int | str | float, int | str | float]
        | list[tuple[int | str | float, int | str | float]],
    ) -> list[JSON]:
        """
        Function that checks whether the value  of a key_to_check is like the check_value (check_val_and_replacement[0]
        and if so replaces it with check_val_and_replacement[1].
        Common use-case would be to check for 0 and replace it with a meaningful replacement.

        :param dict_to_check: List of dicts whose specific key-value pair is to be checked
        :param key_to_check: Specific key whose value is to be checked
        :param check_val_and_replacement: Tuple with the “trigger” value and the replacement
        :return: Returns the modified list of dicts
        """
        if isinstance(key_to_check, str) and isinstance(check_val_and_replacement, tuple):
            for dictionary in dict_to_check:
                if dictionary[key_to_check] == check_val_and_replacement[0]:
                    dictionary[key_to_check] = check_val_and_replacement[1]
        elif isinstance(key_to_check, list) and isinstance(check_val_and_replacement, list):
            if len(key_to_check) != len(check_val_and_replacement):
                raise ValueError(
                    "Mismatch of the input values. Make sure that the number of keys to be checked and the "
                    "tuples with “trigger” value and replacement are the same. You can search for a arbitrary nested"
                    " values inside your dictionary. "
                )
            # condition if there are subdicts which need to be handled f-.exp [bbox][width] (width key inside bbox key)
            if isinstance(key_to_check[0], list):
                # Type narrowing: key_to_check is list[list[str]] in this branch
                for pos, key_list in enumerate(key_to_check):
                    assert isinstance(key_list, list)  # Help pyright understand this is list[str]
                    for dictionary in dict_to_check:
                        value = self.get_nested_value(dictionary=dictionary, keys=key_list)
                        if value == check_val_and_replacement[pos][0]:
                            self.set_nested_value(
                                dictionary=dictionary,
                                keys=key_list,
                                value=check_val_and_replacement[pos][1],
                            )
            else:
                # Type narrowing: key_to_check is list[str] in this branch
                for pos, key in enumerate(key_to_check):
                    assert isinstance(key, str)  # Help pyright understand this is str
                    for dictionary in dict_to_check:
                        if dictionary[key] == check_val_and_replacement[pos][0]:
                            dictionary[key] = check_val_and_replacement[pos][1]

        return dict_to_check

    @staticmethod
    def drop_erroneous_items(lt_items: list[JSON], page_height: int, page_width: int) -> list[JSON]:
        """
        Function to drop the dicts with erroneous value. Current check is for values that exceed the page width
        and height. Checked are the solo width and height values as well as the combination of left value + width
        and bottom value + height. 06.06.2024
        :param lt_items: List with the dicts to check
        :param page_height: Page height for comparison
        :param page_width: Page width for comparison
        :return: list of dicts without the dicts with unsuitable values in their specific parameters
        """
        return [
            item
            for item in lt_items
            if not (
                item["bbox"]["width"] > page_width * 0.99
                and item["bbox"]["height"] > page_height * 0.99
                or item["bbox"]["width"] >= page_width
                or item["bbox"]["left"] + item["bbox"]["width"] >= page_width
                or item["bbox"]["height"] >= page_height
                or item["bbox"]["bottom"] + item["bbox"]["height"] >= page_height
            )
        ]

    @staticmethod
    def get_nested_value(dictionary: JSON, keys: list[str]) -> Any:
        """
        Gives back the value of an arbitrary nested dictionary according to a given key-list.
        :param dictionary: Nested dictionary
        :param keys: List of keys, sorted from left to right in descending hierarchy in the dictionary
        :return: Value of the arbitrary nested dict.
        """
        for key in keys:
            dictionary = dictionary[key]
        return dictionary

    @staticmethod
    def set_nested_value(dictionary: JSON, keys: list[str], value: Any) -> None:
        """
        Sets the value inside an arbitrary nested dictionary according to a given key-list.
        :param dictionary: Nested dictionary
        :param keys: List of keys, sorted from left to right in descending hierarchy in the dictionary
        :param value: Value that is to be set
        :return: None
        """
        for key in keys[:-1]:
            dictionary = dictionary.setdefault(key, {})
        dictionary[keys[-1]] = value

    @staticmethod
    def generate_page_html_content(
        soup: BeautifulSoup,
        width_px: int,
        height_px: int,
        margin: str | int,
        overflow: str,
        back_grnd_c: str,
        padding: int,
        font_family: str,
        dpi: int = 96,
    ) -> Tag:
        """

        :param dpi: Dots per inch. 1px = 1/96 inch. https://www.w3.org/TR/css3-values/#absolute-lengths
        :param font_family: Font to be sued in the body.
        :param soup: BeautifulSoup object.
        :param width_px: Width of the document.
        :param height_px: Height of the document.
        :param margin: "Empty space" around the document. Rec: auto
        :param overflow: Decides if Text exceeding the boundaries of the Document will be hidden or not. Rec: hidden
        :param back_grnd_c: Background color of the document. Rec: white
        :param padding: Padding of the Document. Rec: 4-8 (px)
        :return:HTML div element filled with the specific information about the document.
        """
        style_tag = soup.new_tag("style")
        body_string = f"""               
                height: {height_px}px;
                width: {width_px}px;
                margin-left: {margin};
                margin-right: {margin};
                background: {back_grnd_c};
                font-family:{font_family};
                overflow: {overflow};
                padding: {padding}px;
        """
        page_string = f"""               
                size: {round(width_px / dpi, 2)}in {round(height_px / dpi, 2)}in ;
                margin: {margin};
                padding: {padding};
         """
        tailwind_string = f"""
            @tailwind base;
            @tailwind components;
            @tailwind utilities;
        """

        pre_string = f"""
                   font-family: inherit !important;
                   white-space:pre-line;     
        """
        # 49 as safety for the text to always be above the other divs. Above 49 there are conflicts with the Frontend
        textbox_string = f"""               
            position: absolute;
            background-color: transparent;
            z-index: 49; 
            padding: 0px;
            margin: 0px;
        """
        absolute_pos = f"""               
               position: absolute;
           """

        mark_string = f"""               
            background-color: #00ff00;
            color: black;
           """

        style_tag.string = (
            f"\n"
            f"@page {{ {page_string} }}\n"
            f"      body {{ {body_string} }}\n"
            f"      pre {{ {pre_string} }}\n"
            f"      .textbox {{ {textbox_string} }}\n"
            f"      .rectangle {{ {absolute_pos} }}\n"
            f"      .line {{ {absolute_pos} }}\n"
            f"      mark {{ {mark_string} }}\n"
            f"      {tailwind_string}\n"
            f"  }}\n"
            f"        "
        )

        return style_tag

    def generate_h_textbox_html_content(self, soup: BeautifulSoup, lt_item: JSON):
        """
        !!!
        At the moment it doesn't matter which font the lines have, because serif is always used.
        This is due to the fact that some fonts are simply displayed strangely. Bad display due to
        copyright fonts ? (25.07.2024, to be checked if that is rly the case still)
        !!!
        Every line of text gehts a new div tag to make it possible for every Line to have its own Size and font.
        In the future it could be thought of a way to give every word its own font and size.
        :param soup: BeautifulSoup object.
        :param lt_item: Dict with the infos about the LTTextBoxHorizontal element.
        :return: HTML div element filled with the specific information.
        """
        if all(ord(char) < 32 or ord(char) == 127 for char in lt_item["text"]):
            """There was an invoice in which a line was recognized as a control character"""
            return self.generate_line_html_content(soup=soup, lt_item=lt_item)

        div = soup.new_tag("div")

        div["class"] = (
            f"textbox bottom-[{lt_item['bbox']['bottom']}px] left-[{lt_item['bbox']['left']}px] w-auto h-auto "
        )

        if isinstance(lt_item["size"], str):
            text_pretag = soup.new_tag("pre")
            text_pretag["class"] = f"text-[{lt_item['size']}]"
            # Add inline font-size for PDF generation (doesn't rely on Tailwind CDN)
            text_pretag["style"] = f"font-size: {lt_item['size']};"

            text_pretag.string = self.substitute_hex_vals(
                text=self.substitute_vowels(lt_item["text"])
            )
            div.append(text_pretag)
        else:
            lines = lt_item["text"].split("\n")
            pre_tag_list: list[Tag] = []
            indexes_to_pop: list[int] = []
            for line_count, line in enumerate(lines):
                text_pretag = soup.new_tag("pre")
                line = self.substitute_hex_vals(text=self.substitute_vowels(line))

                if line_count != 0:
                    # round brackets in the regex enable Capture Group. Example: text-[8px]
                    # match.group(0) = 'text-[8px]', match.group(1) = '8px'
                    pattern = r"text-\[(\d+px)\]"
                    match = re.search(pattern, pre_tag_list[line_count - 1]["class"])
                    if match and match.group(1) == lt_item["size"][line_count]:
                        text = f"{pre_tag_list[line_count - 1].string}\n{line}"
                        indexes_to_pop.append(line_count - 1)
                        line = text  # combine text with text from previous line
                text_pretag.string = line  # BeautifulSoup formatiert pre-Tag nicht
                text_pretag["class"] = f"text-[{lt_item['size'][line_count]}]"
                # Add inline font-size for PDF generation (doesn't rely on Tailwind CDN)
                text_pretag["style"] = f"font-size: {lt_item['size'][line_count]};"
                pre_tag_list.append(text_pretag)
                # pop entries in the list if there are any
            if indexes_to_pop:
                # moving backwards through the array avoids index collision
                for index in sorted(indexes_to_pop, reverse=True):
                    pre_tag_list.pop(index)
            for pre_tag in pre_tag_list:
                div.append(pre_tag)

        return div

    def generate_line_html_content(self, soup: BeautifulSoup, lt_item: JSON):
        """

        :param soup: BeautifulSoup object.
        :param lt_item: Dict with the infos about the LTLine element.
        :return: HTML hr element filled with the specific information. 07-06.2024 trying with div to enable color.
        """
        rgb_vals = self.check_background_color(lt_item=lt_item)
        hr = soup.new_tag("div")
        hr["class"] = (
            f"line bottom-[{lt_item['bbox']['bottom']}px] "
            f"left-[{lt_item['bbox']['left']}px] "
            f" {'z-' + str(lt_item['z-index']) if 'z-index' in lt_item.keys() else ''}"
        )
        hr["style"] = (
            f"width: {lt_item['bbox']['width']}px; "
            f"height: {lt_item['bbox']['height']}px; "
            f"background-color: rgb({rgb_vals[0]},"
            f"{rgb_vals[1]},"
            f"{rgb_vals[2]}); "
        )
        return hr

    @staticmethod
    def generate_figure_html_content(soup: BeautifulSoup, lt_item: JSON):
        """
        It is still necessary to check whether Figures are really relevant or whether it is just the general
        designation for placeholders which are then specified by e.g. Image.
        :param soup: BeautifulSoup object.
        :param lt_item: Dict with the infos about the LTFigure element.
        :return: HTML div element filled with the specific information.
        """
        div = soup.new_tag("div")
        div["class"] = (
            f"Figure bottom-[{lt_item['bbox']['bottom']}px] left-[{lt_item['bbox']['left']}px] "
        )
        div["style"] = (
            f"position: absolute; width: {lt_item['bbox']['width']}px; height: {lt_item['bbox']['height']}px; "
        )
        return div

    @staticmethod
    def generate_image_html_content(soup: BeautifulSoup, lt_item: JSON, alt_text: str = "No Pic"):
        """

        :param alt_text: Alternative text if image is not found.
        :param soup: BeautifulSoup object.
        :param lt_item: Dict with the infos about the LTImage element.
        :return: HTML img element filled with the specific information.
        """
        img = soup.new_tag("img")
        img["alt"] = alt_text
        img["src"] = (
            "src/tests/ai_2.jpg"  # item["text"]  # You would have to enter the correct source path here
        )
        img["class"] = f"bottom-[{lt_item['bbox']['bottom']}px] left-[{lt_item['bbox']['left']}px] "
        img["style"] = (
            f"position: absolute; width: {lt_item['bbox']['width']}px; height: {lt_item['bbox']['height']}px; "
        )
        return img

    def generate_rectangle_html_content(self, soup: BeautifulSoup, lt_item: JSON):
        """

        :param soup: BeautifulSoup object.
        :param lt_item: Dict with the infos about the LTRectangle element.
        :return: HTML div element filled with the specific information.ƒ
        """
        rgb_vals = self.check_background_color(lt_item=lt_item)

        div = soup.new_tag("div")
        # A border is added to rectangles with a white background so that they can be seen against the white background
        border_when_white: str = (
            "border-color: rgb(0, 0, 0); "
            if all(color == 255 for color in rgb_vals)
            else f"border-color: rgb({rgb_vals[0]}, {rgb_vals[1]}, {rgb_vals[2]}); "
        )

        div["class"] = (
            f"rectangle bottom-[{lt_item['bbox']['bottom']}px] "
            f"left-[{lt_item['bbox']['left']}px] "
            f"border {'z-' + str(lt_item['z-index']) if 'z-index' in lt_item.keys() else ''}"
        )
        div["style"] = (
            f"width: {lt_item['bbox']['width']}px; "
            f"height: {lt_item['bbox']['height']}px; "
            f"{border_when_white}"
            f"background-color: rgb({rgb_vals[0]},"
            f"{rgb_vals[1]},"
            f"{rgb_vals[2]}); "
        )
        return div

    def generate_curve_html_content(self, soup: BeautifulSoup, lt_item: JSON):
        """
        !!!
        I have yet to find an example in which curves were really Bezier curves. Rectangles are
        subclass of Bezier Curves and therefore (I think) it happens that Rectangles are interpreted as
        Curves by mistake. Curves are therefore (as of 10.04.2024) treated in the same way as rectangles.
        !!!

        :param soup: BeautifulSoup object.
        :param lt_item: Dict with the infos about the LTCurve element.
        :return: HTML div element filled with the specific information.
        """
        rgb_vals = self.check_background_color(lt_item=lt_item)

        div = soup.new_tag("div")
        # A border is added to rectangles with a white background so that they can be seen against the white background
        # border_when_white: str = "border border-rose-500 " if all(color == 255 for color in rgb_vals) else ""
        border_when_white: str = (
            "border-color: rgb(0, 0, 0); "
            if all(color == 255 for color in rgb_vals)
            else f"border-color: rgb({rgb_vals[0]}, {rgb_vals[1]}, {rgb_vals[2]}); "
        )

        div["class"] = (
            f"rectangle bottom-[{lt_item['bbox']['bottom']}px] "
            f"left-[{lt_item['bbox']['left']}px] "
            f"border {'z-' + str(lt_item['z-index']) if 'z-index' in lt_item.keys() else ''}"
        )
        div["style"] = (
            f"width: {lt_item['bbox']['width']}px; "
            f"height: {lt_item['bbox']['height']}px; "
            f"{border_when_white}"
            f"background-color: rgb({rgb_vals[0]},"
            f"{rgb_vals[1]},"
            f"{rgb_vals[2]}); "
        )
        return div

    @staticmethod
    def simplify_ptag_format(html_text: str):
        """
        25.07.2024: deprecated
        NO LONGER IN USE. Switched to pre-tag and other creation.
        Searches everything between <p>...</p> including spaces and tabs. BeautifulSoup separates everything in the
        p-tag automatically with tabs, which stretches the HTML and makes it harder to edit. Function searches in the
        finished HTML text (soup.prettify()) for the separated p-tags and corrects them.
        :param html_text: html. Always soup.prettify()
        :return: html with fewer tabs in the p-tags.
        """
        full_match = [
            f"<p>{match}</p>" for match in re.findall(r"<p>(.*?)</p>", html_text, re.DOTALL)
        ]
        full_match_no_tab = [
            f"<p>{match2}</p>"
            for match2 in [
                re.sub(r"\s+", "", match)
                for match in re.findall(r"<p>(.*?)</p>", html_text, re.DOTALL)
            ]
        ]
        for count in range(len(full_match)):
            html_text = re.sub(full_match[count], full_match_no_tab[count], html_text)
        return html_text

    @staticmethod
    def substitute_vowels(text: str):
        """
        Regex to find errors with umlauts. \xa8 is the Unicode for ¨ the umlaut dots.
        Until now, it was always like this: space, 'umlaut dots', a, o, u, A, O, U.
        :param text: Input text
        return: Corrected text
        """
        return re.sub(
            r" (\xa8)([aAouOU])",
            lambda m: {
                "\xa8a": "ä",
                "\xa8A": "Ä",
                "\xa8o": "ö",
                "\xa8O": "Ö",  # [\xa8]
                "\xa8u": "ü",
                "\xa8U": "Ü",
            }[m.group(1) + m.group(2)],
            text,
        )

    @staticmethod
    def substitute_hex_vals(text: str):
        """
        The background is that for some invoices, if PDFMiner does not recognize the letter, it then uses hex values.
        However, since it is not foreseeable that this is the only character, all unprintable characters are removed.
        The pattern is currently in beta (4.06.2024) and it must be further checked whether it requires further
        adaptation.

        :param text: Input text
        :return: Corrected text
        """
        return re.sub(r"[^ -~äöüÄÖÜß\n\t]", " ", text)

    @staticmethod
    def check_background_color(lt_item: JSON) -> list[int]:
        """
        23.07.2024: Stroking Color is the border color and non stroking color is the background color.
        So far, lines have a stroking color and curves and rectangles have a non_stroking_color
        :param lt_item: dict with the infos about a line, rectangle or curve
        :return: background color of the line, rectangle or curve
        """

        if lt_item["type"] != "LTLine":
            color = (
                lt_item["non_stroking_color"] if "non_stroking_color" in lt_item.keys() else None
            )
        else:
            color = lt_item["stroking_color"] if "stroking_color" in lt_item.keys() else [0, 0, 0]

        if isinstance(color, int):
            rgb_vals: list[int] = [color, color, color]
        elif isinstance(color, tuple) or isinstance(color, list):
            rgb_vals: list[int] = (
                [int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)]
                if color and len(color) == 3 and all(c <= 1 for c in color)
                else [255, 255, 255]
            )
        else:
            rgb_vals: list[int] = [255, 255, 255]  # See if this is a good default.

        # 23.07.2024 Approach to avoid large divs having a black background.
        # Thought: Divs represent large “borders” as well as small sublines.
        # Must be ensured that divs with a width and height > ?px no longer have a black background
        # Theoretically, this should ensure that the stroke remains black, but large divs that only display borders
        # can never be completely black. Default maximum size 5px. To be checked!
        if all(color == 0 for color in rgb_vals):
            if lt_item["bbox"]["width"] > 5 and lt_item["bbox"]["height"] > 5:
                rgb_vals: list[int] = [255, 255, 255]
        return rgb_vals

    def del_duplicates_safe_uniques(self, lt_items: list[JSON], horizontal_or_vertical: str):
        """
        HORIZONTAL: SAME: BOTTOM, HEIGHT; DIFFERENT: WIDTH OR LEFT
        Function to delete the duplicates (in the Rectangle, Curves and Lines). Could be extended to all Items (like
        horizontal textboxes) but there was no example (05.06.2024) where there was a duplicate in any other item,
        except the rectangles, curves and lines.
        06.06.2024: Function was extended to also safe dicts where there is a
        :param lt_items: list with the items/dicts to check
        :param horizontal_or_vertical: distinguish between horizontal or vertical lines to observe
        :return: cleaned list of items/dicts
        """
        # according to keys to check: check_vals_xx lists ->[bottom-value, height-value left-value, width-value]
        # Order is currently relevant. So be careful when changing.
        keys_to_check: list[list[str]] = [
            ["bbox", "bottom"],
            ["bbox", "height"],
            ["bbox", "left"],
            ["bbox", "width"],
        ]

        keys_to_pop: list[int] = []
        dicts_rescued_from_merging: list[JSON] = []

        dicts_separated_by_height_or_width = (
            self.get_dicts_sorted_by_key(lt_items=lt_items, key=keys_to_check[1])
            if (horizontal_or_vertical == "horizontal")
            else (self.get_dicts_sorted_by_key(lt_items=lt_items, key=keys_to_check[3]))
        )

        for height_key in dicts_separated_by_height_or_width.keys():
            for key_prim, primary_item in enumerate(dicts_separated_by_height_or_width[height_key]):
                if key_prim not in keys_to_pop:
                    check_vals_prim = [
                        self.get_nested_value(dictionary=primary_item, keys=key)
                        for key in keys_to_check
                    ]
                    for key_sec, secondary_item in enumerate(lt_items):
                        # make sure that not the same item is compared
                        if key_sec != key_prim:
                            check_vals_sec = [
                                self.get_nested_value(dictionary=secondary_item, keys=key2)
                                for key2 in keys_to_check
                            ]
                            if check_vals_prim == check_vals_sec:
                                # full duplicate
                                keys_to_pop.append(key_sec)
                                break

                            check_left_or_bottom = (
                                2 if horizontal_or_vertical == "horizontal" else 0
                            )
                            check_width_or_height = (
                                3 if horizontal_or_vertical == "horizontal" else 1
                            )

                            if (
                                check_vals_prim[check_left_or_bottom]
                                == check_vals_sec[check_left_or_bottom]
                            ):
                                """ 
                                check_vals_prim[2]: left value
                                check_vals_prim[0]: bottom value
                                check left value, so its a check if everything except the width is the same
                                If yes also check color. 
                                If color is also the same its redundant -> keep the one with the bigger width
                                If color is not the same both should still be popped from the dict and given back
                                separately, so they can be appended to merged_lt_items in merge_split_recs_and_curves().
                                Currently non_stroking_color is checked maybe also stroking color needs to be checked in
                                future implementations.
                                 """
                                same_color: bool = self.get_nested_value(
                                    dictionary=primary_item, keys=["non_stroking_color"]
                                ) == self.get_nested_value(
                                    dictionary=secondary_item,
                                    keys=["non_stroking_color"],
                                )

                                if same_color:
                                    if (
                                        check_vals_prim[check_width_or_height]
                                        >= check_vals_sec[check_width_or_height]
                                    ):
                                        # delete 2nd dict if the width or height is smaller / same value as the 1st dict
                                        keys_to_pop.append(key_sec)
                                    else:
                                        # if 1st is smaller delete first and break out of the 2nd loop
                                        keys_to_pop.append(key_prim)
                                        break
                                else:
                                    keys_to_pop.append(key_prim)
                                    keys_to_pop.append(key_sec)
                                    dicts_rescued_from_merging.append(primary_item)
                                    dicts_rescued_from_merging.append(secondary_item)

        if keys_to_pop:
            for index in sorted(keys_to_pop, reverse=True):
                lt_items.pop(index)
        return lt_items, dicts_rescued_from_merging

    def check_for_relation(self, lt_items: list[JSON], horizontal_or_vertical: str):
        """
        Function to check the items for "deeper" relation. The past showed that only taking the bottom value as
        reference for merging lines, rects and curves with the merge_split_recs_and_curves()-Function lead to some
        rectangles/lines/curves getting overwritten, because they had the same bottom value although these were not the
        lines/rectangles/curves recognized by PDF Miner as fragments that were to be combined into a single item
        by the function.

        :param lt_items: items to check for relation
                :param horizontal_or_vertical: distinguish between horizontal or vertical lines to observe
        :return: dicts_w_rel: List with the dicts that have a deeper relationship to atleast one  other dict in the list
                 no_rel_dicts: Dicts that have no deeper relationship to another dict in the corresponding list
        """

        # return lists
        (
            dicts_w_rel,
            no_rel_dicts,
        ) = [], []
        # At least 2 occurrences with either the same height or width have to occur otherwise no deeper relation then
        # same bottom value is given
        check_val = 2
        keys_to_check: list[list[str]] = [["bbox", "height"], ["bbox", "width"]]
        correct_key = (
            keys_to_check[0] if horizontal_or_vertical == "horizontal" else keys_to_check[1]
        )
        unique_height_or_width = self.get_unique_values_and_counts(
            lt_items=lt_items, keys_to_check=correct_key, key_str=correct_key[1]
        )

        if len(unique_height_or_width[0]) == 1:
            dicts_w_rel = lt_items
            return dicts_w_rel, no_rel_dicts
        else:
            # multiple occurrences of relations f.exp : ! unique_X[0]= actual width/height values, [1] = counts
            # unique_heights: [dict_keys([7, 9, 2]), dict_values([5, 2, 2])]
            # unique_widths: [dict_keys([7, 6, 5, 1, 2]), dict_values([1, 3, 2, 1, 2])]
            # Trying to find unique pairs, where there is !no! ambiguity

            # dict_with_h_and_w_relations = {"height": {},
            #                                "width": {}}
            dict_with_h_or_w_relations = {correct_key[1]: {}}
            for indx_l2, item in enumerate(lt_items):
                item_h_or_w = self.get_nested_value(dictionary=item, keys=correct_key)

                if item_h_or_w not in dict_with_h_or_w_relations[correct_key[1]].keys():
                    dict_with_h_or_w_relations[correct_key[1]][item_h_or_w] = [indx_l2]
                else:
                    dict_with_h_or_w_relations[correct_key[1]][item_h_or_w].append(indx_l2)

                for indx_l3, item2 in enumerate(lt_items):
                    if indx_l3 != indx_l2:
                        temp_item_h_or_w = self.get_nested_value(dictionary=item2, keys=correct_key)
                        if temp_item_h_or_w == item_h_or_w:
                            dict_with_h_or_w_relations[correct_key[1]][item_h_or_w].append(indx_l3)

            # remove duplicates in the lists of the dicts: SPECIFIC FOR DICT IN DICT WITH LIST AS VALUE

            for key in dict_with_h_or_w_relations:
                for sub_key in dict_with_h_or_w_relations[key]:
                    dict_with_h_or_w_relations[key][sub_key] = list(
                        set(dict_with_h_or_w_relations[key][sub_key])
                    )

            for key_h_or_w, index_same_h_or_w in dict_with_h_or_w_relations[correct_key[1]].items():
                # append every unique pair to his own list so it can the relations can be separated in the next
                # step for the merging process in
                temp_list = [lt_items[index] for index in index_same_h_or_w]
                dicts_w_rel.append(temp_list)

        return dicts_w_rel, no_rel_dicts

    def get_unique_values_and_counts(
        self, lt_items: list[JSON], keys_to_check: list[str], key_str: str
    ) -> list[Any]:
        """
        Function to get all unique values and the corresponding counts in a dictionary with the specific keys height
        and width. Can be generalized if needed later currently specific to check_for_relation()-Function.
        :param lt_items:
        :param keys_to_check: currently only 1 key to 1 value is allowed. so u can nest keys but u cant give 2 keys
                              that would return 2 values
        :param key_str: name on how the dicts key should be named
        :return:
        """
        values_and_occurrences: dict[str, list[int]] = {key_str: []}

        for indx, value in enumerate(lt_items):
            values_and_occurrences[key_str].append(
                self.get_nested_value(dictionary=value, keys=keys_to_check)
            )

        return [
            Counter(values_and_occurrences[key_str]).keys(),
            Counter(values_and_occurrences[key_str]).values(),
        ]

    @staticmethod
    def find_unique_pairs(relations: JSON):
        """
        Function to find the unique pairs in the relation dict.
        Function is specific to the check_for_relation()-Function.
        Example of a relation_dict. Returns
        relations = {
            'height': {2: [6, 7], 7: [0, 2, 3, 5, 8], 9: [1, 4]},
            'width': {1: [6], 2: [8, 7], 5: [3, 5], 6: [1, 2, 4], 7: [0]}
        }
        Return is [(3, 5), (1, 4)]
        :param relations: The dictionary with the relations between width and height. The keys of the height and width
         dicts in the relations dict are the actual unique pixel values. The values are the indexes of dicts inside the
         lt_items list (of dicts).
        """
        unique_pairs = []

        for height_key, height_values in relations["height"].items():
            for i in range(len(height_values)):
                for j in range(i + 1, len(height_values)):
                    h1 = height_values[i]
                    h2 = height_values[j]
                    h1_in_widths = []
                    h2_in_widths = []

                    # Check where h1 and h2 occur in the width dictionary
                    for width_key, width_values in relations["width"].items():
                        if h1 in width_values:
                            h1_in_widths.append(width_key)
                        if h2 in width_values:
                            h2_in_widths.append(width_key)

                    # Check if they both occur in the same width lists
                    if set(h1_in_widths) == set(h2_in_widths):
                        unique_pairs.append((h1, h2))

        return unique_pairs

    def get_dicts_sorted_by_key(self, lt_items: list[JSON], key: list[str]):
        """
        Function to sort a list of dicts by a given key.
        Common usage to separate by bottom or left value to check for horizontal or vertical lines to merge
        :param lt_items: list of unsorted dicts
        :param key: Key used for sorting
        :return: returns a dict with lists. Every key represents a specific value of the key, that is represented in the
                 list of dicts (lt_items). The lists contain the dicts with the same value.
                 exp. dicts_sorted_by_key = {703: [{...},{...},{...}], 653: [{...}], 321: [{...},{...}]}
        """
        dicts_sorted_by_key: dict[str, list[JSON]] = {}
        # First step. Find the items with the same bottom value.
        for item in lt_items:
            key_value = self.get_nested_value(dictionary=item, keys=key)  # item["bbox"]["bottom"]
            if key_value not in dicts_sorted_by_key.keys():
                dicts_sorted_by_key[key_value] = [item]
            else:
                dicts_sorted_by_key[key_value].append(item)
        return dicts_sorted_by_key

    def pre_process_sorted_dicts(
        self, sorted_dicts: JSON, horizontal_or_vertical: str
    ) -> tuple[JSON, list[JSON]]:
        """
        Function to preprocess the sorted values before the merging. First duplicates get removed and also
        redundant Pieces. Uniques (f.exp entries with different color) get saved and given back separately in the
        merged_lt_items list. Those dicts will directly be converted to HTML later and don't go through the merging
        process.
        The function currently does its purpose. Needs to be monitored, if everything is working to plan in the future.

        :param sorted_dicts: list of dicts sorted by the bottom value. dicts with same bottom value are in the
        same dict
        :param horizontal_or_vertical: distinguish between horizontal or vertical lines to observe
        :return: returns a tuple. First the dicts which are not unique. In this list the duplicates have been removed.
                 Second, the list of unique dicts in the merged_lt_items list.

        """
        merged_lt_items: list[JSON] = []
        value_pop_stor: list[Any] = []
        append_after_stor: list[Any] = []
        for bottom_or_left_val, height_or_width_lists in sorted_dicts.items():
            for height_or_width_val, lists_w_dicts in height_or_width_lists.items():
                if len(lists_w_dicts) > 1:
                    cleaned_dups_value, dicts_rescued_before_merge = (
                        self.del_duplicates_safe_uniques(
                            lt_items=lists_w_dicts,
                            horizontal_or_vertical=horizontal_or_vertical,
                        )
                    )

                    if dicts_rescued_before_merge:
                        for dicts in dicts_rescued_before_merge:
                            # append items directly to the list where the merged items are stored
                            merged_lt_items.append(dicts)
                    if cleaned_dups_value:
                        dicts_w_rel, no_rel_dicts = self.check_for_relation(
                            lt_items=cleaned_dups_value,
                            horizontal_or_vertical=horizontal_or_vertical,
                        )
                        if not no_rel_dicts and not all(
                            isinstance(item, dict) for item in dicts_w_rel  # type: ignore[arg-type]
                        ):
                            break
                        else:
                            value_pop_stor.append(bottom_or_left_val)
                            if no_rel_dicts:
                                for dicts in no_rel_dicts:
                                    merged_lt_items.append(dicts)
                            if dicts_w_rel:
                                if all(isinstance(item, dict) for item in dicts_w_rel):  # type: ignore[arg-type]
                                    append_after_stor.append(
                                        [
                                            f"{bottom_or_left_val}_{height_or_width_val}_new",
                                            dicts_w_rel,
                                        ]
                                    )
                                    # dicts_sorted_by_bottom[f"{key}new"] = dicts_w_rel
                                elif all(isinstance(item, list) for item in dicts_w_rel):
                                    for count, list_w_dict in enumerate(dicts_w_rel):
                                        append_after_stor.append(
                                            [
                                                f"{bottom_or_left_val}_{height_or_width_val}_new{count}",
                                                list_w_dict,
                                            ]
                                        )
                                        # dicts_sorted_by_bottom[f"{key}new{count}"] = list_w_dict
                    else:
                        value_pop_stor.append(bottom_or_left_val)
                else:
                    merged_lt_items.append(lists_w_dicts[0])
                    value_pop_stor.append(bottom_or_left_val)

        # append all the dicts which were split from the original dict due to relation issues
        for entry in append_after_stor:
            if all(isinstance(item, dict) for item in entry[1]):
                sorted_dicts[entry[0]] = entry[1]
        # pop all already in merged_lt_items saved keys
        for key_to_pop in value_pop_stor:
            if key_to_pop in sorted_dicts.keys():
                sorted_dicts.pop(key_to_pop)
        return sorted_dicts, merged_lt_items

    @staticmethod
    def merge_sorted_dicts(sorted_dicts: JSON, horizontal_or_vertical: str):
        merging_choices = [["left", "width"], ["bottom", "height"]]
        merging_indexes: Any = [0, [1, 1]] if horizontal_or_vertical == "horizontal" else [1, [0, 1]]
        first_idx: int = merging_indexes[0]
        second_idx: list[int] = merging_indexes[1]
        bottom_or_left = merging_choices[first_idx][0]
        bigger_value = merging_choices[first_idx][1]
        smaller_value = merging_choices[second_idx[0]][1]
        height_or_width = (
            "width" if horizontal_or_vertical == "horizontal" else "height"
        )  # horizontal == same height
        temp_merged_lt_items = []
        for _, value in sorted_dicts.items():
            if len(value) > 1:
                smallest_left_or_bottom_div, biggest_left_or_bottom_div = {}, {}
                for item in value:
                    if not smallest_left_or_bottom_div:
                        smallest_left_or_bottom_div = item
                    else:
                        smallest_left_or_bottom_div = (
                            item
                            if item["bbox"][bottom_or_left]
                            < smallest_left_or_bottom_div["bbox"][bottom_or_left]
                            else (smallest_left_or_bottom_div)
                        )
                        if not biggest_left_or_bottom_div:
                            biggest_left_or_bottom_div = item
                        else:
                            biggest_left_or_bottom_div = (
                                item
                                if item["bbox"][bottom_or_left]
                                > biggest_left_or_bottom_div["bbox"][bottom_or_left]
                                else biggest_left_or_bottom_div
                            )
                # Check if horizontal or vertikal line/rectangle :
                # Height >> Width --> Vertikal ; Width >> Height --> Horizontal. Current factor: min. x5
                # Does not matter which height/width is taken. Currently smallest_left_div["bbox"]["width"]/["height"]
                if (
                    smallest_left_or_bottom_div["bbox"][bigger_value]
                    >= 5 * smallest_left_or_bottom_div["bbox"][smaller_value]
                ):
                    merged_div: JSON = smallest_left_or_bottom_div
                    merged_width: int = (
                        biggest_left_or_bottom_div["bbox"][bottom_or_left]
                        + biggest_left_or_bottom_div["bbox"][height_or_width]
                    ) - smallest_left_or_bottom_div["bbox"][bottom_or_left]
                    merged_div["bbox"]["width"] = merged_width
                else:  # Vertical Orientation
                    #     #merged_lt_items = merged_lt_items + value
                    merged_div = value
                #     """TEMPORÄR bis die vertikalen rects/linien/curves entsprechend merged werden.
                #     Dann müssten die values auch gelöscht werden können"""
                #     # merged_div: dict = smallest_left_div
                #     # merged_height: int = ((biggest_left_div["bbox"]["bottom"] + biggest_left_div["bbox"]["height"])
                #     #                       - smallest_left_div["bbox"]["bottom"])
                #     # merged_div["bbox"]["height"]: int = merged_height
                # CURRENT IMPLEMENTATION TAKES THE COLOR OF THE SMALLEST DIV. MAYBE THERE WILL BE A NEED TO ITERATE
                # OVER ALL ITEMS IN VALUE AND GET THE COLOR WITH THE MOST OCCURRENCES (MAYBE Except (0,0,0) & (1,1,1))
                # IN THE FUTURE
                if isinstance(merged_div, list):
                    temp_merged_lt_items = temp_merged_lt_items + value
                else:
                    temp_merged_lt_items.append(merged_div)
            else:
                temp_merged_lt_items.append(value[0])
        return temp_merged_lt_items

    async def convert_left_to_right_position(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Function to adjust the referencing of elements specifically to their placement within the PDF.
        To avoid overflows at the margins, it makes sense to reference everything < 0.5*Page-Width to the left and
        everything > 0.5*Page-Width to the right. The = sign is currently listed with left.
        :param soup: HTML-Soup
        :return:Soup with optimized referencing
        """
        if soup.find_all("pre"):  # to not run into await error in extract_div_params-function
            task = asyncio.create_task(
                extract_div_params(html_content=str(soup.prettify()))
            )  # asyncio.get_event_loop().run_until_complete(...)
            div_param_dict = await task
            pattern = r"left-\[((\d+)px)\]"
            for index, pre in enumerate(soup.find_all("pre")):
                class_text_parent_div = pre.parent.attrs["class"]
                match = re.search(pattern, class_text_parent_div)
                if not match:
                    continue
                left_px_val = int(match.group(2))
                if left_px_val > 0.5 * self.page_width:
                    # actually redundant, as both occur in the same order
                    # ES GIBT IMMER WIEDER EINEN KEY ERROR. VIELLEICHT DOCH ENTFERNEN DIE IF ABFRAGE????
                    # MAL KEY ERROR 1 MAL 0 mal auch 2. BEIM 2TEN MAL ERSTELLEN FUNKTIONIERT ES DANN?
                    # if pre.text == div_param_dict[index]["text"]:
                    text_width = int(div_param_dict[index]["width"])
                    conver_to_right_pos = (
                        f"right-[{int(self.page_width - left_px_val - np.floor(text_width))}px]"
                    )
                    new_class = re.sub(pattern, conver_to_right_pos, pre.parent.attrs["class"])
                    pre.parent.attrs["class"] = new_class.split()
        return soup

    def set_div_hierarchies(self, rects_curves_lines: list[JSON]) -> list[JSON]:
        """
        Function to check whether divs are overlapping and there is a need to adjust their z-index to make sure the
        small divs inside bigger divs are all visible. Only the divs containing the lines, rectangles and curves have
        to be checked, because the z-index of the text is set to 99 (24.07.2024) to make sure that the text is always
        above the divs.
        :param rects_curves_lines: List with all the lines, recs and curves that are to be written to the HTML.
        :return: The rects, lines and curves with their respective z-index appended to them.
        """
        all_correlation_checked = False
        depth_to_check = 0
        correlated_divs = self.hierarchy_comparisons(rects_curves_lines=rects_curves_lines)
        """DAS IST IMMER NOCH NICHT DER WEG. REKURSIVER ANSATZ KLAPPT EINFACH NICHT"""
        correlated_divs = self.it(correlated_divs)
        # # very first check for correlation of the divs. is the baseline of correlations. afterwards there is /needs to
        # # be a recursive way to check for overlapping to get the whole hierarchy
        # while not all_correlation_checked:
        #     change_counter = 0  # track if there were changes
        #     if not correlated_divs:
        #         all_correlation_checked = True
        #     else:
        #
        #         for idx, parent_div in enumerate(correlated_divs):
        #
        #             subset = [entry for idx, entry in enumerate(rects_curves_lines) if
        #                       idx in list(parent_div.values())[0]]
        #             # check hierarchie with the subset. Goal is to check if there are any more overlapping divs inside
        #             correl_subsets = self.hierarchy_comparisons(rects_curves_lines=subset) if len(subset) > 1 else None
        #             if correl_subsets:
        #                 change_counter += 1
        #                 for change in correl_subsets:
        #                     parent_key_val = int(list(change.keys())[0]) # check if the value is in the list
        #                     if parent_key_val in parent_div[list(parent_div.keys())[0]]:
        #                         idx_in_parent = parent_div[list(parent_div.keys())[0]].index(parent_key_val)
        #                         correlated_divs[idx][list(parent_div.keys())[0]][idx_in_parent] = change
        #                     else:
        #                         for entry_idx, entry in enumerate(parent_div[list(parent_div.keys())[0]]):
        #                             if isinstance(entry, dict):
        #                                 if parent_key_val in entry[list(entry.keys())[0]]:
        #                                     idx_in_dict_parent = entry[list(entry.keys())[0]].index(parent_key_val)
        #                                     correlated_divs[idx][list(parent_div.keys())[0]][entry_idx][list(entry.keys())[0]][idx_in_dict_parent] = change
        #
        #                     for i in range(len(correlated_divs[idx][list(parent_div.keys())[0]]) - 1, -1, -1):
        #                         correlated_divs[idx][list(parent_div.keys())[0]].pop(i) if \
        #                             correlated_divs[idx][list(parent_div.keys())[0]][i] in list(change.values())[
        #                                 0] else None
        #
        #         depth_to_check += 1  # to skip the dicts . NEEDS TO BE CONTINUED FOR >2 DIV OVERLAPPING
        #         if change_counter == 0:
        #             all_correlation_checked = True

        hierarchies = self.extract_hierarchy_levels(correlated_divs)
        all_possible_levels = list(set([key for entry in hierarchies for key in entry.keys()]))

        compact_hierarchies = {}
        for level in all_possible_levels:
            if level not in compact_hierarchies.keys():
                compact_hierarchies[level] = []
            for entry in hierarchies:
                if level in entry.keys():
                    if isinstance(entry[level], int):
                        compact_hierarchies[level].append(entry[level])
                    elif isinstance(entry[level], list):
                        for single_entry in entry[level]:
                            compact_hierarchies[level].append(single_entry)
                    elif isinstance(entry[level], dict):
                        """For later, first have to find an example with more than 1 nesting"""
                        raise ValueError("NOCH NICHT GESCHAUT WAS MAN MACHEN MUSS")

        for key, value in compact_hierarchies.items():
            level_as_int = int(key.lstrip("Level "))
            for idx, entry in enumerate(rects_curves_lines):
                entry["z-index"] = (
                    level_as_int * 10 if idx in value else 10
                )  # 10 as default for all divs.

        return rects_curves_lines

    def hierarchy_comparisons(self, rects_curves_lines: list[JSON]) -> list[JSON]:
        """
        Compares the Entries of the rects_curves_lines list against each other via the check_for_parent_div-function.
        Returns the List of related divs.
        :param rects_curves_lines: List with the dictionaries containing the information needed for the check.
        :return: List of divs with correlations. The Keys of the dicts are the indexes of the parent div in
                 rects_curves_lines. The values of the dicts are the child divs.
        """
        correlated_divs: list[Any] = []
        for idx, entry in enumerate(rects_curves_lines):
            temp_dict = {idx: []}
            for idx2, entry2 in enumerate(rects_curves_lines):
                if entry != entry2:
                    temp_dict[idx].append(idx2) if self.check_for_parent_div(
                        possible_parent=entry, possible_child=entry2
                    ) else None
            correlated_divs.append(temp_dict) if temp_dict[idx] else None
        return correlated_divs

    @staticmethod
    def check_for_parent_div(possible_parent: JSON, possible_child: JSON) -> bool:
        """
        Compares 2 divs against each other to look if the first is a parent of the second. By parents it is meant if
        the second div is completely inside the first div. It is ok if the boundaries top, bottom, or left from the
        child are the same from the parent.
        The decision is made by comparing the x1, y1, x2 and y2 value of parent and child against each other.

                                                x1 value is the left value
        Both value fix the bottom-left point &
                                                y1 value is the bottom value

                                                x2 value is the left value + the width value
        Both value fix the top-right point &
                                                y2 value is the bottom value + the height value

        To meet the requirements of a parent, the x1 & y1 values of the parent must be less than or equal to that of
        the child. The x2 & y2 values, on the other hand, must be greater than or equal to that of the child.

        :param possible_parent: dict with the information of the possible parent. Relevant Info is inside the "bbox" key
        :param possible_child:dict with the information of the possible child. Relevant Info is inside the "bbox" key
        :return: Returns true or false according to the outcome of the Algorithm
        :rtype:
        """

        x1_p, y1_p, x2_p, y2_p = (
            possible_parent["bbox"]["left"],
            possible_parent["bbox"]["bottom"],
            (possible_parent["bbox"]["width"] + possible_parent["bbox"]["left"]),
            (possible_parent["bbox"]["height"] + possible_parent["bbox"]["bottom"]),
        )

        x1_c, y1_c, x2_c, y2_c = (
            possible_child["bbox"]["left"],
            possible_child["bbox"]["bottom"],
            (possible_child["bbox"]["width"] + possible_child["bbox"]["left"]),
            (possible_child["bbox"]["height"] + possible_child["bbox"]["bottom"]),
        )
        return x1_p <= x1_c and y1_p <= y1_c and x2_p >= x2_c and y2_p >= y2_c

    def extract_hierarchy_levels(self, data: Any, current_level: int = 1) -> Any:
        """
        Function that recursively runs through the list of hierarchies. The fact is that keys are always one level
        below their values because they are parent divs and therefore require a lower z-index so that the children are
        all displayed correctly in the rendered HTML.

        Exemplary structure of the level hierarchy
            List -> dict(key) = level 1
            List -> dict(key) -> dict(value) == int/list[int] or dict = level 2
            List -> dict(key) -> dict(value) == dict -> dict(key) = level 3
            List -> dict(key) -> dict(value) == dict -> dict(key) -> dict(value) == int/list[int] or dict = level 4
            etc.

        :param data: data in which the hierarchical structure is to be examined
        :param current_level: Hierarchy level. Defaults to 1
        :return: Depending on the recursion it is a dict with the Level or the data itself.
        """
        if isinstance(data, list):
            # If data is a list, process each item
            return [self.extract_hierarchy_levels(item, current_level) for item in data]

        elif isinstance(data, dict):
            # If data is a dictionary, annotate each key-value pair
            annotated_dict = {f"Level {current_level}": list(data.keys())[0]}
            current_level += 1
            for value in data.values():
                if isinstance(value, dict):
                    # Recursively process nested dictionaries
                    annotated_dict[f"Level {current_level}"] = self.extract_hierarchy_levels(
                        value, current_level
                    )
                elif isinstance(value, list):
                    # Recursively process lists within dictionaries
                    annotated_dict[f"Level {current_level}"] = self.extract_hierarchy_levels(
                        value, current_level
                    )
                else:
                    # Annotate the value with the current level
                    annotated_dict[f"Level {current_level}"] = self.extract_hierarchy_levels(
                        value, current_level
                    )
            return annotated_dict

        else:
            # If data is a single value (int), just return it
            return data

    def to_frozenset(self, value: Any) -> Any:
        """
        Helper function for converting nested data structures to frozenset.
        :param value: value to convert into frozenset
        :return: value as frozenset
        """

        if isinstance(value, Mapping):
            # Convert a dictionary recursively into a frozenset
            return frozenset((k, self.to_frozenset(v)) for k, v in value.items())
        elif isinstance(value, Iterable) and not isinstance(value, str):
            # Convert a list recursively into a frozenset
            return frozenset(self.to_frozenset(v) for v in value)
        else:
            # Otherwise, return it as it is
            return value

    def it(self, hierarchies: list[Any]) -> list[Any]:
        """
        Mal Ansatz um mit dem correlated div zu arbeiten, dass als basis erstellt wird.
        :param hierarchies:
        :type hierarchies:
        :return:
        :rtype:
        """

        all_parents_div_numbers = [list(parent_dict.keys())[0] for parent_dict in hierarchies]
        index_to_skip = []
        for hierarchie_idx, entry in enumerate(hierarchies):
            if not hierarchie_idx in index_to_skip:
                for parent_idx, parent in enumerate(all_parents_div_numbers):
                    # if the parent is in the list of another parent replace the integer with the corespnding parent_dict
                    # f.exp 7 will be replaced with {7:[1, 2 ,3]}
                    if parent in entry[list(entry.keys())[0]]:
                        child_idx = entry[list(entry.keys())[0]].index(parent)
                        hierarchies[hierarchie_idx][list(entry.keys())[0]][child_idx] = hierarchies[
                            parent_idx
                        ]
                        """Erklärung: Sollte so funktionieren. Es ist möglich, dass in mehreren dicts die gleiche Zahl
                           eines parents steht, die dann replaced wird. Nach jedem replacen wird der index_to_skip um 
                           den index des parents in hierarchy erweitert. Jetzt muss aber geschaut werden, das nicht 2mal
                           der gleiche Index  appendet wird, da das ansonsten zu zu viel Entfernen führen würde, da ja 
                           index 2 nachdem index 2 schonmal entfernt wurde nicht mehr Index 2 sondern (einfachster Fall
                           mit exakt 1 mal Entfernen ) index 3 wäre z.B. """
                        index_to_skip.append(
                            parent_idx
                        ) if parent_idx not in index_to_skip else None  # indexes of the parents which are children of other parents

        for index in sorted(index_to_skip[::-1], reverse=True):
            # pop the parents which are children from other parents
            hierarchies.pop(index)

        hierarchies = self.remove_duplicates_in_hierarchy(hierarchies)
        return hierarchies

    def remove_duplicates_in_hierarchy(self, hierarchies: list[Any]) -> list[Any]:
        """
        Entfernt die duplikate. Wenn key als list item vorhanden ist was ein integer wird es entfernt. Aber halt nur 1 mal
        rekursirver Ansatz , der dann alles durch geht klappt nicht. Keine Ahnung was das Abbruchkriterium sein soll.
        :param hierarchies:
        :type hierarchies:
        :return:
        :rtype:
        """
        for hierarchie_idx, entry in enumerate(hierarchies):
            if not all(isinstance(x, int) for x in entry[list(entry.keys())[0]]):
                possible_vals_to_drop = [
                    value for value in entry[list(entry.keys())[0]] if isinstance(value, int)
                ]

                for value in entry[list(entry.keys())[0]]:
                    if isinstance(value, dict):
                        # get common elements of both lists
                        non_dict_vals = [
                            val for val in value[list(value.keys())[0]] if isinstance(val, int)
                        ]
                        if len(non_dict_vals) != len(value[list(value.keys())[0]]):
                            """Then there is another dict in the dict which needs to be checked."""
                            ...
                        common_elements = self.get_common_elements(
                            non_dict_vals, possible_vals_to_drop
                        )
                        # get the indizes in the hierarchy of the common elements
                        indexes_of_common_elements_in_hierarchy = [
                            hierarchies[hierarchie_idx][list(entry.keys())[0]].index(element)
                            for element in common_elements
                        ]
                        # get the indizes in possible_vals_to_drop of the common elements
                        indexes_of_common_elements_in_possible_vals_to_drop = [
                            possible_vals_to_drop.index(element) for element in common_elements
                        ]
                        for i in reversed(range(len(indexes_of_common_elements_in_hierarchy))):
                            # drop the redundant integers in the list
                            hierarchies[hierarchie_idx][list(entry.keys())[0]].pop(
                                indexes_of_common_elements_in_hierarchy[i]
                            )
                            possible_vals_to_drop.pop(
                                indexes_of_common_elements_in_possible_vals_to_drop[i]
                            )
        return hierarchies

    def get_common_elements(self, list1: list[Any], list2: list[Any]) -> list[Any]:
        """
        Schauen ob es gleiche Werte in den Liste gibt und wenn ja werden diese ausgegeben,
        :param list1:
        :type list1:
        :param list2:
        :type list2:
        :return:
        :rtype:
        """
        set1 = set(list1)
        set2 = set(list2)
        return list(set1 & set2)


async def main() -> None:
    from pprint import pprint

    pdf_path = "src/PDF_Processing/test_pdfs/Jendrik/Balolo.pdf"
    detect_vertical_text = True
    text_in_images = False
    save_embd_imgs = False
    image_directory = ""
    metadata = {}  # gibt viele default Werte
    item_extractor = LTItemExtractor(
        pdf_path_or_bytes_io=pdf_path,
        detect_vertical_text=detect_vertical_text,
        text_in_images=text_in_images,
        save_embd_imgs=save_embd_imgs,
        image_directory=image_directory,
    )
    html_converter = LTItemsToHtmlConverter()
    html: str = await html_converter.gen_html_from_lt_items(
        lt_items=item_extractor.return_lt_list(), metadata=metadata
    )
    # html_ohne_tab = re.findall(rf"<p>\n(.*?)\n</p>\n")
    with open("testInProgress.html", "w") as file:
        file.write(html)
    pprint(html)


if __name__ == "__main__":
    asyncio.run(main())
