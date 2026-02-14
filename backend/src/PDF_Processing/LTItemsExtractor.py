import re
from pathlib import Path
from typing import Iterator, Any, Iterable
from io import BytesIO
from pdfminer.high_level import extract_pages
from pdfminer.image import ImageWriter
from pdfminer.layout import LTPage, LAParams, LTImage
from src.types import JSON


class LTItemExtractor:
    lt_items_storage: list[JSON] = []  # List with the LTItems. Parameters are stored in dicts.

    def __init__(
        self,
        pdf_path_or_bytes_io: str | BytesIO,
        detect_vertical_text: bool,
        text_in_images: bool,
        save_embd_imgs: bool,
        image_directory: str | None = None,
    ):
        """

        :param pdf_path_or_bytes_io: Path of the POF or PDF as bytes
        :param detect_vertical_text: Recognition of vertical text
        :param text_in_images: Recognition of text in images
        :param save_embd_imgs: Save found images
        """
        self.pdf_path_or_b = pdf_path_or_bytes_io
        if isinstance(pdf_path_or_bytes_io, str):
            match = re.search(r"/([^/]+)\.pdf", pdf_path_or_bytes_io)
            self.pdf_save_name = match.group(1) if match else "unknown.pdf"
        else:
            self.pdf_save_name = "bytes.pdf"
        self.vert_text = detect_vertical_text
        self.text_in_img = text_in_images
        self.save_embd_img = save_embd_imgs
        self.img_dir = image_directory
        # Is required to reset the  memory for each API request. Otherwise, all lt_items are saved
        # per session (until the API is reset) and there is an overlap of LTItems found in different PDFS,
        # which is not acceptable.
        self.lt_items_storage = []

    def get_pages(self) -> Iterator[LTPage]:
        """

        :return: Pages
        """
        if isinstance(self.pdf_path_or_b, str):
            return extract_pages(
                Path(self.pdf_path_or_b).expanduser(),
                laparams=LAParams(all_texts=self.text_in_img, detect_vertical=self.vert_text),
                maxpages=1,
            )
        else:
            return extract_pages(
                self.pdf_path_or_b,
                laparams=LAParams(all_texts=self.text_in_img, detect_vertical=self.vert_text),
                maxpages=1,
            )

    def scan_pdf_for_ltitems(self, o: Any, depth: int = 0) -> None:
        """
        Show location and text of LTItem and all its descendants
        :param o: Iterable created with PDF Miner (pages = extract_pages(path), path = location of the PDF)
        :param depth: Depth within the element. Ex:
                    Page d = 0
                      TextBox d = 1
                          TextLine d = 2
                             Character d = 3
                             Anno      d = 3
        :return: None. Fills the lt_items_storage with all LTItems.
        """

        # if depth == 0:
        #     print('element                        x1    y1   x2     y2      font  text')
        #     print('------------------------------ ----- ---- -----  ------  ----- -----')
        bbox = self.get_optional_bbox(o)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        font = self.get_optional_fontinfo(o)
        if self.get_indented_name(o, depth) == "LTCurve":
            self.lt_items_storage.append(
                {
                    "type": f"{self.get_indented_name(o, depth)}",
                    "bbox": {
                        "left": bbox[0],
                        "bottom": bbox[1],
                        "width": width,
                        "height": height,
                    },
                    "text": self.get_optional_text(o),
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
        elif self.get_indented_name(o, depth) == "LTRect":
            self.lt_items_storage.append(
                {
                    "type": f"{self.get_indented_name(o, depth)}",
                    "bbox": {
                        "left": bbox[0],
                        "bottom": bbox[1],
                        "width": width,
                        "height": height,
                    },
                    "text": self.get_optional_text(o),
                    "font": font[0],
                    "size": font[1],
                    "fill": o.fill,
                    "stroking_color": o.stroking_color,
                    "non_stroking_color": o.non_stroking_color,
                    "line_width": o.linewidth,
                    "points": o.original_path,
                }
            )

        elif self.get_indented_name(o, depth) == "LTLine":
            self.lt_items_storage.append(
                {
                    "type": f"{self.get_indented_name(o, depth)}",
                    "bbox": {
                        "left": bbox[0],
                        "bottom": bbox[1],
                        "width": width,
                        "height": height,
                    },
                    "text": self.get_optional_text(o),
                    "font": font[0],
                    "size": font[1],
                    "fill": o.fill,
                    "stroking_color": o.stroking_color,
                    "non_stroking_color": o.non_stroking_color,
                    "line_width": o.linewidth,
                    "points": o.original_path,
                }
            )

        elif self.get_indented_name(o, depth) == "LTImage":
            self.lt_items_storage.append(
                {
                    "type": f"{self.get_indented_name(o, depth)}",
                    "bbox": {
                        "left": bbox[0],
                        "bottom": bbox[1],
                        "width": width,
                        "height": height,
                    },
                }
            )
            o.name = self.pdf_save_name
            """Speichern des Bilds"""
            if self.save_embd_img:
                self.extract_picture_from_pdf(
                    image=o, outputdir=self.img_dir or "src/PDF_Processing/img_storage"
                )

        elif self.get_indented_name(o, depth) == "LTPage":
            if o.groups:
                self.lt_items_storage.append(
                    {
                        "type": f"{self.get_indented_name(o, depth)}",
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
                self.lt_items_storage.append(
                    {
                        "type": f"{self.get_indented_name(o, depth)}",
                        "bbox": {
                            "left": bbox[0],
                            "bottom": bbox[1],
                            "width": width,
                            "height": height,
                        },
                    }
                )

        elif self.get_indented_name(o, depth) == "LTTextBoxHorizontal":
            self.lt_items_storage.append(
                {
                    "type": f"{self.get_indented_name(o, depth)}",
                    "bbox": {
                        "left": bbox[0],
                        "bottom": bbox[1],
                        "width": width,
                        "height": height,
                    },
                    "text": self.get_optional_text(o),
                    "font": font[0],
                    "size": font[1],
                }
            )
        elif self.get_indented_name(o, depth) == "LTChar":
            self.lt_items_storage.append(
                {
                    "type": f"{self.get_indented_name(o, depth)}",
                    "bbox": {
                        "left": bbox[0],
                        "bottom": bbox[1],
                        "width": width,
                        "height": height,
                    },
                    "text": self.get_optional_text(o),
                    "font": font[0],
                    "size": font[1],
                }
            )
        elif self.get_indented_name(o, depth) == "LTAnno":
            self.lt_items_storage.append(
                {
                    "type": f"{self.get_indented_name(o, depth)}",
                    "bbox": {
                        "left": bbox[0],
                        "bottom": bbox[1],
                        "width": width,
                        "height": height,
                    },
                    "text": self.get_optional_text(o),
                    "font": font[0],
                    "size": font[1],
                }
            )
        # debugging
        # print(
        #     f'{self.get_indented_name(o, depth):<30.30s} '
        #     f'{self.get_optional_bbox(o)} '
        #     f'{self.get_optional_fontinfo(o)}'
        #     f'{self.get_optional_text(o)}'
        # )

        if isinstance(o, Iterable):
            for i in o:
                self.scan_pdf_for_ltitems(i, depth=depth + 1)

        # print(f"src/PDF_Processing/img_storage/{self.pdf_save_name}")  # ?

    @staticmethod
    def get_indented_name(o: Any, depth: int) -> str:
        """Indented name of LTItem"""
        # return '  ' * depth + o.__class__.__name__
        return o.__class__.__name__

    @staticmethod
    def get_optional_bbox(o: Any) -> list[int]:
        """Bounding box of LTItem if available, otherwise empty string"""
        # if hasattr(o, 'bbox'):
        #     return ''.join(f'{i:<4.0f}' for i in o.bbox)
        # return ''
        if hasattr(o, "bbox"):
            return [round(bbox) for bbox in o.bbox]
            # return [math.floor(bbox) for bbox in o.bbox]
        return [0, 0, 0, 0]

    @staticmethod
    def get_optional_text(o: Any) -> str:
        """Text of LTItem if available, otherwise empty string"""
        if hasattr(o, "get_text"):
            return o.get_text().strip()
        return ""

    @staticmethod
    def get_optional_fontinfo(o: Any) -> list[str]:
        """Font info of LTChar if available, otherwise empty string"""
        if hasattr(o, "fontname") and hasattr(o, "size"):
            # return f'{o.fontname} {round(o.size)}pt'
            # actual_font_size_pt = int(char.size) * 72 / 96
            # return [f'{o.fontname}', f'{int(o.size * 72 / 96)}pt']
            return [f"{o.fontname}", f"{int(o.size)}px"]
            # return [f'{o.fontname}', f'{int(o.size * 0,2116)}mm'] # test für meinen Bildschirm mit 120 dpi
        # return ''
        return ["", ""]

    @staticmethod
    def extract_picture_from_pdf(
        image: LTImage, outputdir: str = "src/PDF_Processing/img_storage"
    ) -> None:
        """
        Extract Pictures from PDF via PDFMiner.
        Can be used to integrate in the PDF Reconstruction Process.
        :param image: Image to be saved.
        :param outputdir: Output directory
        :return:
        """

        im_writer = ImageWriter(outdir=outputdir)
        im_writer.export_image(image)

    def get_lt_list(self) -> list[JSON]:
        return self.lt_items_storage

    def reset_lt_list(self) -> None:
        self.lt_items_storage = []

    def return_lt_list(self) -> list[JSON]:
        self.scan_pdf_for_ltitems(o=self.get_pages())
        return self.get_lt_list()


def main() -> None:
    from pprint import pprint

    pdf_path = "src/PDF_Processing/test_pdfs/Jendrik/TestObjekt1.pdf"
    # pdf_path = "src/PDF_Processing/test_pdfs/GOT-2024_00911.pdf"
    with open(pdf_path, "rb") as file:
        pdf_bytes = file.read()
    IOpdf = BytesIO(pdf_bytes)
    extractor = LTItemExtractor(
        pdf_path_or_bytes_io=IOpdf,
        detect_vertical_text=True,
        text_in_images=False,
        save_embd_imgs=True,
        image_directory="src/PDF_Processing/img_storage",
    )
    # test = extract_pages(pdf_bytes, laparams=LAParams(all_texts=False, detect_vertical=False))
    lt_list = extractor.return_lt_list()
    pprint(lt_list)


if __name__ == "__main__":
    main()
