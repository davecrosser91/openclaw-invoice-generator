from pydantic import BaseModel, Field
from src.Datenvalidierung.Enum_Classes import (
    Type_LLM_Ckpt,
    CRUD_Types,
    Type_LLM_Base,
    Type_Invoice_language,
)


class LLMCkpt(BaseModel):
    chat_ckpt: Type_LLM_Ckpt


class LLMBase(BaseModel):
    base_llm: Type_LLM_Base


class TesseractConfig(BaseModel):
    ocr_engine: int = Field(ge=0, le=3)
    page_seg_mode: int = Field(ge=0, le=13)
    language: str
    # language: str = Field(min_length=3, max_length=3)  # Besser alle von tesseract unterstützen Sprachen nehmen.


class CRUD_Operators(BaseModel):
    operation: CRUD_Types


class Invoice_language(BaseModel):
    language: Type_Invoice_language
