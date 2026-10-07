import json
import sys
from pathlib import Path 
from urllib.parse import urlparse 

from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field, ValidationError, field_validator

# Listes à définir plus tard
FILTRE = {"sepia", "blur", "grayscale"}       
BLEND = {"multiply", "screen", "overlay"}  

EXTENSIONS_OK = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}

class Layer(BaseModel):
    path_image: Path 
    filtre: str
    blend: str
    opacity: float = Field(ge=0, le=1)    

    @field_validator("path_image")
    @classmethod
    def verifier_image(cls, p: Path) -> Path:
        if not p.exists():
            raise ValueError(f"fichier introuvable : {p}")
        if not p.is_file():
            raise ValueError(f"ce chemin n'est pas un fichier : {p}")
        if p.suffix.lower() not in EXTENSIONS_OK:
            raise ValueError(
                f"extension '{p.suffix}' non supportée, permises : {sorted(EXTENSIONS_OK)}"
            )
        try:
            with Image.open(p) as img:
                img.verify() 
        except (UnidentifiedImageError, OSError) as e:
            raise ValueError(f"le fichier n'est pas une image valide : {p} ({e})")
        return p

    @field_validator("filtre")
    @classmethod
    def verifier_filtre(cls, v):
        if v not in LISTE_A:
            raise ValueError(f"filtre '{v}' inconnu, valeurs permises : {sorted(LISTE_A)}")
        return v

    @field_validator("blend")
    @classmethod
    def verifier_blend(cls, v):
        if v not in LISTE_B:
            raise ValueError(f"blend '{v}' inconnu, valeurs permises : {sorted(LISTE_B)}")
        return v


class Document(BaseModel):
    layers: list[Layer] = Field(min_length=1)  




def lire_json(chemin: str) -> dict:
    """Lit le fichier. Lève FileNotFoundError ou json.JSONDecodeError."""
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


def valider(data: dict) -> Document:
    """Valide la structure. Lève pydantic.ValidationError si non conforme."""
    return Document.model_validate(data)


def charger(chemin: str) -> Document:
    """Lecture + validation, en une seule étape."""
    return valider(lire_json(chemin))


def traiter(doc: Document) -> None:
    for i, layer in enumerate(doc.layers):
        print(i, layer.path_image, layer.filtre, layer.blend, layer.opacity)


def Load_Image_JSON() -> Document | None:
    if len(sys.argv) < 2:
        sys.exit("Usage : python script.py fichier.json")

    try:
        doc = charger(sys.argv[1])
        return Document
    except FileNotFoundError:
        sys.exit(f"Fichier introuvable : {sys.argv[1]}")
    except json.JSONDecodeError as e:
        sys.exit(f"JSON invalide : {e}")
    except ValidationError as e:
        sys.exit(f"JSON non conforme :\n{e}")

    #traiter(doc) 

