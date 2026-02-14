import os
import io
from PIL import Image  # Dependency: Pillow
import pytesseract  # Dependency: pytesseract & Tesseract OCR engine itself
from dotenv import load_dotenv
from requence.service import ContextHelper, Service, RequenceFile

load_dotenv()


def hocr_message_handler(context: ContextHelper):
    """
    Handles incoming requests to perform OCR and return HOCR output for an image file.
    """
    context.debug.info("HOCR service: Request received.")

    # Assuming the input file is provided under the key "document" as a RequenceFile object
    input_file: RequenceFile = context.get_input().get("document")

    if not input_file:
        context.debug.error("HOCR service: No input file provided with key 'document'.")
        return {"error": "Input file with key 'document' not provided."}

    if not isinstance(input_file, RequenceFile):
        context.debug.error(
            f"HOCR service: Input 'document' is not a RequenceFile. Type: {type(input_file)}."
        )
        return {"error": "Input 'document' must be a file object of type RequenceFile."}

    try:
        # Assume RequenceFile has a .blob() method that returns the file's byte content
        image_bytes = input_file.blob()
        if not isinstance(image_bytes, bytes):
            context.debug.error(
                f"HOCR service: RequenceFile.read() did not return bytes. Got: {type(image_bytes)}"
            )
            return {"error": "Could not read bytes from the input file."}

        # Convert image bytes to a PIL Image object
        pil_image = Image.open(io.BytesIO(image_bytes))

        # Perform OCR to get HOCR output (using German language pack by default)
        hocr_data_bytes = pytesseract.image_to_pdf_or_hocr(pil_image, extension="hocr", lang="deu")
        hocr_output_str = hocr_data_bytes.decode("utf-8")

        context.debug.info("HOCR service: HOCR generation successful.")
        return {"hocr_output": hocr_output_str}

    except pytesseract.TesseractNotFoundError:
        context.debug.error(
            "HOCR service: Tesseract OCR engine is not installed or not found in PATH."
        )
        return {
            "error": "Tesseract OCR engine not found. Please ensure it's installed and in your system PATH."
        }
    except FileNotFoundError:  # More specific than general Exception for Image.open issues
        context.debug.error(
            "HOCR service: The provided file content is not a valid image or is corrupted."
        )
        return {"error": "Invalid or corrupted image file. Could not open image."}
    except Exception as e:
        # Check for PIL's UnidentifiedImageError specifically
        if "UnidentifiedImageError" in str(type(e)):
            context.debug.error(f"HOCR service: Cannot identify image file: {str(e)}")
            return {
                "error": "Cannot identify image file. Ensure it's a supported image format (e.g., PNG, JPEG)."
            }

        context.debug.error(f"HOCR service: Error during HOCR generation: {str(e)}")
        return {"error": f"An unexpected error occurred during HOCR processing: {str(e)}"}


# Configuration for the Tesseract HOCR service
# These should be set in your .env file or environment
TESSERACT_HOCR_SERVICE_TOKEN = os.environ.get("TESSERACT_HOCR_SERVICE_ACCESS_TOKEN")
TESSERACT_HOCR_SERVICE_VERSION = os.environ.get("TESSERACT_HOCR_SERVICE_VERSION")

if not TESSERACT_HOCR_SERVICE_TOKEN:
    print("Warning: TESSERACT_HOCR_SERVICE_ACCESS_TOKEN environment variable is not set.")  # noqa: T201
if not TESSERACT_HOCR_SERVICE_VERSION:
    print("Warning: TESSERACT_HOCR_SERVICE_VERSION environment variable is not set.")  # noqa: T201

# Initialize and register the service
# The 'name' parameter is optional but good for identifying the service if multiple are run.
tesseract_hocr_service = Service(
    {
        "access_token": TESSERACT_HOCR_SERVICE_TOKEN,
        "version": TESSERACT_HOCR_SERVICE_VERSION,
    },
    hocr_message_handler,
)

# The service will typically start listening for requests after instantiation,
# following the pattern of the requence.service framework.
print("Tesseract HOCR Service initialized.")  # noqa: T201
