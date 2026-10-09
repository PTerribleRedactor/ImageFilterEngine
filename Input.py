import json
import sys
import inspect 
from pathlib import Path 
from urllib.parse import urlparse 
from typing import Any    

from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator
from Filter import Filter   
from Blender import BLEND 

# Listes à définir plus tard  
from registre_filtres import REGISTRE
List_filter = REGISTRE.noms()  
List_BLEND = set(BLEND)

EXTENSIONS_OK = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}


class FilterSpec(BaseModel):
    model_config = ConfigDict(extra="ignore")

    filter_name: str
    filter_params: dict[str, Any] = Field(default_factory=dict)

    @field_validator("filter_name")
    @classmethod
    def verifier_nom(cls, v: str) -> str:
        if v not in List_filter:
            raise ValueError(f"filtre '{v}' inconnu, valeurs permises : {sorted(List_filter)}")
        return v

    """
    @model_validator(mode="after")
    def verifier_params(self):
        autorises = set(list(inspect.signature(List_filter[self.filter_name]).parameters)[1:])
        inconnus = set(self.filter_params) - autorises
        if inconnus:
            raise ValueError(f"paramètres inconnus : {sorted(inconnus)}, permis : {sorted(autorises)}")
        return self
    """


class Layer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    path_image: Path
    filtre: list[FilterSpec]
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
            raise ValueError(f"extension '{p.suffix}' non supportée")
        try:
            with Image.open(p) as im:
                im.verify()
        except (UnidentifiedImageError, OSError) as e:
            raise ValueError(f"le fichier n'est pas une image valide : {p} ({e})")
        return p

    @field_validator("blend")
    @classmethod
    def verifier_blend(cls, v: str) -> str:
        if v not in BLEND:
            raise ValueError(f"blend '{v}' inconnu, valeurs permises : {sorted(BLEND)}")
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
        return doc 
    except FileNotFoundError:
        sys.exit(f"Fichier introuvable : {sys.argv[1]}")
    except json.JSONDecodeError as e:
        sys.exit(f"JSON invalide : {e}")
    except ValidationError as e:
        sys.exit(f"JSON non conforme :\n{e}")

    #traiter(doc) 

