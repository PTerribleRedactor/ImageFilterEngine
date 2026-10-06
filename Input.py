import json
import sys
from pathlib import Path 
from urllib.parse import urlparse 

from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field, ValidationError, field_validator

# Listes à définir plus tard
LISTE_A = {"sepia", "blur", "grayscale"}       # filtres autorisés
LISTE_B = {"multiply", "screen", "overlay"}    # blend modes autorisés

EXTENSIONS_OK = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff"}

class Layer(BaseModel):
    path_image: Path 
    filtre: str
    blend: str
    opacity: float = Field(ge=0, le=1)         # entre 0 et 1 inclus

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
                img.verify()   # lève une exception si le fichier est corrompu
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
    layers: list[Layer] = Field(min_length=1)  # au moins 1 image, sans maximum




def lire_json(chemin: str) -> Document | None:
    """Lit un fichier JSON et retourne son contenu."""
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            data : dict = json.load(f)
        return valider(data) 


    except FileNotFoundError:
        sys.exit(f"Fichier introuvable : {chemin}")
    except json.JSONDecodeError as e:
        sys.exit(f"JSON invalide : {e}")

def valider(data: dict) -> Document | None: 
    """Valider que le json respect les convention du program"""
    try:
        return Document.model_validate(data)
    except ValidationError as e:
        print(e)
        return None


def url_bien_formee(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def traiter(data: dict) -> None:
    """Votre logique métier ici."""
    for cle, valeur in data.items():
        print(cle, "->", valeur)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage : python script.py fichier.json")

    data = lire_json(sys.argv[1])
    traiter(data)

