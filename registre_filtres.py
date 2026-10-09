import importlib.util
import inspect
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from Filter import Filter as _Natif

DOSSIER_EXTERNE = Path(__file__).parent / "external_filters"
_ATTRS_DICT = ("FILTER_CLASSES", "FILTRE", "FILTERS")


# --- modules de compatibilité pour les fichiers externes --------------------
# Certains fichiers font `from filtre_class import Filter` et
# `from image_io import load_image` : on les fournit à la volée,
# sauf s'ils existent déjà dans le projet.

def _installer_modules_compat() -> None:
    import types
    from abc import ABC, abstractmethod

    if importlib.util.find_spec("filtre_class") is None:
        class Filter(ABC):
            @abstractmethod
            def apply(self, image):
                raise NotImplementedError

        mod = types.ModuleType("filtre_class")
        mod.Filter = Filter
        sys.modules["filtre_class"] = mod

    if importlib.util.find_spec("image_io") is None:
        def load_image(path) -> Image.Image:
            with Image.open(Path(path)) as im:
                im.load()
                return im.copy()

        mod = types.ModuleType("image_io")
        mod.load_image = load_image
        sys.modules["image_io"] = mod


# --- conversions numpy <-> PIL ---------------------------------------------

def _to_pil(img: np.ndarray) -> Image.Image:
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


def _from_pil(pil: Image.Image, dtype) -> np.ndarray:
    return (np.asarray(pil.convert("RGB"), dtype=np.float32) / 255.0).astype(dtype)


# --- adaptation d'une classe externe ----------------------------------------

def _veut_pil(cls) -> bool:
    params = list(inspect.signature(cls.apply).parameters.values())[1:]
    if not params:
        return False
    a = params[0].annotation
    return a is Image.Image or (isinstance(a, str) and "Image" in a)


def _construire(cls, params: dict):
    noms = list(inspect.signature(cls.__init__).parameters)[1:]
    if noms == ["params"]:          # style __init__(self, params: dict)
        return cls(params)
    return cls(**params)            # style arguments nommés


def _runner(cls):
    pil = _veut_pil(cls)

    def run(img: np.ndarray, **params) -> np.ndarray:
        try:
            f = _construire(cls, params)
        except KeyError as e:
            raise TypeError(f"paramètre manquant : {e}") from None
        if pil:
            return _from_pil(f.apply(_to_pil(img)), img.dtype)
        return f.apply(img)

    return run


# --- chargement d'un fichier externe -----------------------------------------

def _charger_module(chemin: Path):
    nom = "filtre_externe_" + "".join(c if c.isalnum() else "_" for c in chemin.stem)
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom] = module
    spec.loader.exec_module(module)
    return module


def _decouvrir(module) -> dict:
    for attr in _ATTRS_DICT:
        d = getattr(module, attr, None)
        if isinstance(d, dict):
            return {str(k).lower(): v for k, v in d.items()}
    trouves = {}
    for n, c in vars(module).items():
        if (inspect.isclass(c) and c.__module__ == module.__name__
                and callable(getattr(c, "apply", None))
                and not inspect.isabstract(c)):
            cle = n.lower()
            trouves[cle.removesuffix("filter") or cle] = c
    return trouves


# --- registre ----------------------------------------------------------------

class Registre:
    def __init__(self, dossier: Path = DOSSIER_EXTERNE):
        self._natif = _Natif()
        self._noms_natifs = set(_Natif.FILTRE.keys())
        self._externes = {}
        _installer_modules_compat()
        if dossier.is_dir():
            for fichier in sorted(dossier.glob("*.py")):
                self._ajouter(fichier)

    def _ajouter(self, fichier: Path) -> None:
        try:
            classes = _decouvrir(_charger_module(fichier))
        except Exception as e:
            print(f"[filtres] {fichier.name} ignoré : {e}")
            return
        for cle, cls in classes.items():
            if cle in self._noms_natifs or cle in self._externes:
                cle = f"{fichier.stem}.{cle}"      # évite d'écraser un filtre existant
            self._externes[cle] = _runner(cls)

    def noms(self) -> set:
        return self._noms_natifs | set(self._externes)

    def apply(self, nom: str, img: np.ndarray, **params) -> np.ndarray:
        """KeyError si le filtre n'existe pas ; TypeError/ValueError si params invalides."""
        if nom in self._noms_natifs:
            return self._natif.Apply(nom, img, **params)
        return self._externes[nom](img, **params)


REGISTRE = Registre()
