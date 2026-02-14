import openai
from openai import OpenAI
import base64
import requests
from PIL import Image
import fitz  # PyMuPDF
import io
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()


class TemplateGenerator:
    def __init__(self, openai_key: str = ""):
        # self.api_key = os.environ.get("OPENAI_API_KEY")
        # self.api_key = openai_key
        self.api_key = openai_key
        # self.client = OpenAI(api_key=openai_key)
        openai.api_key = openai_key

    def load_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def describe_image(self, base64_image):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        prompt = (
            f"## System: "
            f"Du bist ein Webdeveloper, kannst Informationen und Texte aus Bildern ziehen und diese analysieren"
            f" Du bist spezialisiert auf die Rekonstruktion von Rechnungen mit HTML."
            f"Das folgende Bild ist ein gescanntes Dokument "
            f"##Instruction:"
            f"Analysieren Sie das hochgeladene Dokument sorgfältig. Identifizieren Sie alle wichtigen "
            f"Elemente wie Textblöcke, Überschriften, Listen, Tabellen, Bilder und Grafiken."
            f"Beschreiben Sie genaue Details wie das Styling der Schriften in den einzelnen Blöcken und das "
            f" Styling der Tabellen, als wäre es mit Tailwindcss erstellt. "
            f"Achten Sie auf die Anordnung dieser Elemente zueinander und die Gesamtstruktur des Dokuments."
            f"Verwenden Sie Texterkennungstechnologien, um den Text aus dem Bild zu extrahieren. Strukturieren "
            f"Sie den Text gemäß dem Originaldokument, indem Sie Überschriften, Absätze, Listen und andere "
            f"Textelemente klar unterscheiden und organisieren. Ziel ist es im Anschluss das "
            f"Dokument mit der gelieferten Beschreibung 1:1 nachbauen zu können!"
        )

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 4096,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        print(response.json())
        return response.json()["choices"][0]["message"]["content"]

    def make_html_from_image(self, description, base64_image, prompt):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            "max_tokens": 4096,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        print(response.json())
        return response.json()["choices"][0]["message"]["content"]

    def make_html_w_placeholders_from_html(self, prompt):
        headers = {
            # "Content-Type": "application/json",
            "Accept": "text/plain",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": "gpt-4-1106-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 4096,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        print(response.json())
        return response.json()["choices"][0]["message"]["content"]

    def correct_misinterpreted_words_from_tesseract(self, prompt):
        headers = {"Accept": "text/plain", "Authorization": f"Bearer {self.api_key}"}

        payload = {
            "model": "gpt-3.5-turbo-0125",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 4096,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        print(response.json())
        return response.json()["choices"][0]["message"]["content"]

    def b64_to_pil(self, b64_string):
        """
        Convert a base64 encoded string to a PIL image.

        :param b64_string: The base64 encoded string of the image.
        :return: A PIL image object.
        """
        image_data = base64.b64decode(b64_string)
        image = Image.open(io.BytesIO(image_data))
        return image

    def pdf_to_b64_image(self, content):
        # Load the PDF
        pdf = fitz.open(content)
        # pdf = fitz.open("pdf", content)
        page = pdf.load_page(0)  # We'll just use the first page here

        # Render the page to an image
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")

        # Convert bytes to base64 string
        base64_encoded_image = base64.b64encode(img_bytes).decode()

        return base64_encoded_image


if __name__ == "__main__":
    html_path = "src/PDF_Processing/test_htmls/selco_invoice.html"
    entiy_path = "src/PDF_Processing/test_html_entities/selco_invoice_entities.json"
    # with open(pdf_path_5, "rb") as file:
    #     pdf_bytes = file.read()
    # raw_html: dict = create_raw_html(file=pdf_bytes, name="test", description="test", doctype="invoice")
    # pprint(raw_html["data"]["attributes"]["html"])
    with open(html_path, "r") as file:
        raw_html = file.read()
    temp = TemplateGenerator()
    temp.make_html_w_placeholders_from_html()
