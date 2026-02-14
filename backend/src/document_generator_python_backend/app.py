from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from models.types import ModificationPayload
from src.document_generator_python_backend.src import TemplateModifier
from src.document_generator_python_backend.src import TemplateGenerator
from bs4 import BeautifulSoup
import requests
import os

from dotenv import load_dotenv

load_dotenv()

template_modifier = TemplateModifier
template_generator = TemplateGenerator
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/modify_template")
def modify_template(payload: ModificationPayload):
    print(payload)
    template = payload.template
    instruction = payload.instruction
    template = template_modifier.modify(template, instruction)
    return {"status": "success", "template": template}


@app.post("/create_template")
async def create_html(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(...),
    doctype: str = Form(...),
):
    # Process the file or perform your logic here
    # Read the content of the file
    print("name", name)
    print("description", description)
    print("doctype", doctype)

    content = await file.read()
    b64_image = template_generator.pdf_to_b64_image(content)
    desc = await template_generator.describe_image(b64_image)
    html_string = await template_generator.make_html_from_image(desc, b64_image)
    html = BeautifulSoup(html_string, "html.parser")
    strapi_url = f"{os.environ.get('STRAPI_URL')}/api/templates"
    payload = {
        "data": {
            "name": name,
            "description": description,
            "doctype": doctype,
            "html": html.encode("utf-8"),  # }
        }
    }

    headers = {
        "Authorization": f"Bearer {os.environ.get('STRAPI_WRITE_TOKEN')}",
        "Content-Type": "application/json",
    }

    response = requests.post(strapi_url, json=payload, headers=headers)
    print(response)
    return response.json()
