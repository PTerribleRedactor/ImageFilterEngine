"""
Génère des fichiers .json (valides et invalides) puis vérifie que valider() :
  - retourne un objet Document pour les JSON valides ;
  - REJETTE les JSON invalides (retourne None ou lève une exception).

À placer à la racine du projet (à côté de validation.py et du dossier
"stockage_d'image"), puis :   python verifier_jsons.py

Les fichiers sont écrits dans  tests_json/valides  et  tests_json/invalides
(vous pouvez les ouvrir et les modifier à la main).
"""
import contextlib
import io
import json
import shutil
import sys
from pathlib import Path

from Input import LISTE_A, LISTE_B, Document, charger 

RACINE = Path(__file__).parent
DOSSIER_IMAGES = "stockage_image"
SORTIE = RACINE / "tests_json"
VALIDES = SORTIE / "valides"
INVALIDES = SORTIE / "invalides"
FIXTURES = SORTIE / "fixtures"

FILTRE_OK = sorted(LISTE_A)[0]
BLEND_OK = sorted(LISTE_B)[0]

IMAGES = [
    "Liam_sous_courbes.png",
    "Thomas_fait_de_la_guitare.jpg",
    "sashimi.jpg",
    "razer_rgb.jpg",
    "coming_out_de_thomas.jpg",
    "Lulu1.png",
    "Lulu2.png",
]


# --------------------------------------------------------------------------- #
# Briques de construction
# --------------------------------------------------------------------------- #
def img(nom: str) -> str:
    # Chemin relatif à la racine du projet (le script se place dans RACINE)
    return f"{DOSSIER_IMAGES}/{nom}"


def layer(**overrides) -> dict:
    base = {
        "path_image": img("sashimi.jpg"),
        "filtre": FILTRE_OK,
        "blend": BLEND_OK,
        "opacity": 0.5,
    }
    base.update(overrides)
    return base


def sans(champ: str) -> dict:
    d = layer()
    del d[champ]
    return d


def doc(*layers) -> dict:
    return {"layers": list(layers)}


def fixture(nom: str) -> str:
    return f"{SORTIE.name}/fixtures/{nom}"


# --------------------------------------------------------------------------- #
# Cas : (nom_fichier, contenu)   contenu = dict (-> JSON) ou str (texte brut)
# --------------------------------------------------------------------------- #
CAS_VALIDES = {
    "v01_une_image": doc(layer()),
    "v02_deux_images": doc(layer(), layer(path_image=img("Lulu1.png"))),
    "v03_sept_images": doc(*[layer(path_image=img(n)) for n in IMAGES]),
    "v04_opacity_0": doc(layer(opacity=0)),
    "v05_opacity_1": doc(layer(opacity=1)),
    "v06_opacity_float_0_0": doc(layer(opacity=0.0)),
    "v07_opacity_float_1_0": doc(layer(opacity=1.0)),
    "v08_opacity_0_001": doc(layer(opacity=0.001)),
    "v09_opacity_0_999": doc(layer(opacity=0.999)),
    "v10_champ_supplementaire_ignore": doc(layer(commentaire="ignoré")),
    "v11_opacity_chaine_convertie": doc(layer(opacity="0.5")),
    "v12_meme_image_deux_fois": doc(layer(), layer()),
    "v13_image_png": doc(layer(path_image=img("Lulu2.png"))),
    "v14_image_jpg": doc(layer(path_image=img("razer_rgb.jpg"))),
}
# Une entrée par valeur de liste A et B
for _i, _f in enumerate(sorted(LISTE_A)):
    CAS_VALIDES[f"v15_filtre_{_i}"] = doc(layer(filtre=_f))
for _i, _b in enumerate(sorted(LISTE_B)):
    CAS_VALIDES[f"v16_blend_{_i}"] = doc(layer(blend=_b))


CAS_INVALIDES = {
    # ---- syntaxe JSON cassée (texte brut) ----
    "i01_syntaxe_virgule_finale": '{"layers": [],}',
    "i02_syntaxe_accolade_non_fermee": '{"layers": [',
    "i03_syntaxe_fichier_vide": "",
    "i04_syntaxe_guillemets_simples": "{'layers': []}",
    "i05_syntaxe_backslash_windows": (
        '{"layers": [{"path_image": "C:\\Users\\moi\\a.png", '
        f'"filtre": "{FILTRE_OK}", "blend": "{BLEND_OK}", "opacity": 0.5}}]}}'
    ),
    "i06_syntaxe_commentaire": '{"layers": [] // commentaire\n}',
    "i07_syntaxe_texte_quelconque": "bonjour",
    # ---- structure globale ----
    "i10_racine_liste": [layer()],
    "i11_racine_chaine": "texte",
    "i12_racine_null": None,
    "i13_layers_absent": {},
    "i14_layers_null": {"layers": None},
    "i15_layers_objet": {"layers": layer()},
    "i16_layers_chaine": {"layers": "abc"},
    "i17_layers_vide": {"layers": []},
    "i18_element_chaine": {"layers": ["sashimi.jpg"]},
    "i19_element_null": {"layers": [None]},
    "i20_element_objet_vide": {"layers": [{}]},
    # ---- path_image ----
    "i30_path_inexistant": doc(layer(path_image=img("n_existe_pas.png"))),
    "i31_path_dossier": doc(layer(path_image=DOSSIER_IMAGES)),
    "i32_path_vide": doc(layer(path_image="")),
    "i33_path_entier": doc(layer(path_image=123)),
    "i34_path_liste": doc(layer(path_image=["a.png"])),
    "i35_path_extension_txt": doc(layer(path_image=fixture("notes.txt"))),
    "i36_path_sans_extension": doc(layer(path_image=fixture("image_sans_ext"))),
    "i37_path_texte_deguise_png": doc(layer(path_image=fixture("faux.png"))),
    "i38_path_fichier_vide_png": doc(layer(path_image=fixture("vide.png"))),
    "i39_path_png_corrompu": doc(layer(path_image=fixture("corrompu.png"))),
    # ---- filtre ----
    "i40_filtre_inconnu": doc(layer(filtre="inconnu")),
    "i41_filtre_vide": doc(layer(filtre="")),
    "i42_filtre_mauvaise_casse": doc(layer(filtre=FILTRE_OK.swapcase())),
    "i43_filtre_espaces": doc(layer(filtre=f" {FILTRE_OK} ")),
    "i44_filtre_valeur_de_liste_b": doc(layer(filtre=BLEND_OK)),
    "i45_filtre_entier": doc(layer(filtre=123)),
    "i46_filtre_liste": doc(layer(filtre=[FILTRE_OK])),
    "i47_filtre_null": doc(layer(filtre=None)),
    "i48_filtre_absent": doc(sans("filtre")),
    # ---- blend ----
    "i50_blend_inconnu": doc(layer(blend="inconnu")),
    "i51_blend_vide": doc(layer(blend="")),
    "i52_blend_mauvaise_casse": doc(layer(blend=BLEND_OK.swapcase())),
    "i53_blend_espaces": doc(layer(blend=f" {BLEND_OK} ")),
    "i54_blend_valeur_de_liste_a": doc(layer(blend=FILTRE_OK)),
    "i55_blend_entier": doc(layer(blend=123)),
    "i56_blend_liste": doc(layer(blend=[BLEND_OK])),
    "i57_blend_null": doc(layer(blend=None)),
    "i58_blend_absent": doc(sans("blend")),
    # ---- opacity ----
    "i60_opacity_negative": doc(layer(opacity=-0.1)),
    "i61_opacity_superieure_a_1": doc(layer(opacity=1.1)),
    "i62_opacity_tres_grande": doc(layer(opacity=100)),
    "i63_opacity_chaine_non_numerique": doc(layer(opacity="abc")),
    "i64_opacity_chaine_vide": doc(layer(opacity="")),
    "i65_opacity_pourcentage": doc(layer(opacity="50%")),
    "i66_opacity_virgule_decimale": doc(layer(opacity="0,5")),
    "i67_opacity_null": doc(layer(opacity=None)),
    "i68_opacity_liste": doc(layer(opacity=[0.5])),
    "i69_opacity_absente": doc(sans("opacity")),
    "i70_opacity_nan_chaine": doc(layer(opacity="nan")),
    "i71_opacity_inf_chaine": doc(layer(opacity="inf")),
    # ---- path_image absent / null ----
    "i80_path_absent": doc(sans("path_image")),
    "i81_path_null": doc(layer(path_image=None)),
    # ---- plusieurs layers ----
    "i90_deuxieme_layer_invalide": doc(layer(), layer(opacity=5)),
    "i91_dernier_layer_invalide": doc(
        *[layer(path_image=img(n)) for n in IMAGES], layer(blend="nope")
    ),
    "i92_erreurs_multiples_dans_un_layer": doc(
        layer(filtre="x", blend="y", opacity=9, path_image=img("absent.png"))
    ),
    "i93_erreurs_sur_plusieurs_layers": doc(
        layer(filtre="x"), layer(), layer(blend="y")
    ),
}


# --------------------------------------------------------------------------- #
# Génération des fichiers
# --------------------------------------------------------------------------- #
def ecrire(dossier: Path, nom: str, contenu) -> None:
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / f"{nom}.json"
    if isinstance(contenu, str) and nom.startswith("i0"):
        chemin.write_text(contenu, encoding="utf-8")        # texte brut
    else:
        chemin.write_text(json.dumps(contenu, indent=2, ensure_ascii=False),
                          encoding="utf-8")


def generer() -> None:
    if SORTIE.exists():
        shutil.rmtree(SORTIE)

    # Fichiers "pièges" référencés par certains JSON invalides
    FIXTURES.mkdir(parents=True)
    (FIXTURES / "notes.txt").write_text("du texte", encoding="utf-8")
    (FIXTURES / "image_sans_ext").write_bytes(b"\x00\x01")
    (FIXTURES / "faux.png").write_text("ceci n'est pas une image", encoding="utf-8")
    (FIXTURES / "vide.png").write_bytes(b"")
    (FIXTURES / "corrompu.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"garbage" * 10)

    for nom, contenu in CAS_VALIDES.items():
        ecrire(VALIDES, nom, contenu)
    for nom, contenu in CAS_INVALIDES.items():
        ecrire(INVALIDES, nom, contenu)


# --------------------------------------------------------------------------- #
# Exécution
# --------------------------------------------------------------------------- #
def tester(chemin: Path) -> tuple[str, str]:
    tampon = io.StringIO()
    try:
        with contextlib.redirect_stdout(tampon):
            resultat = charger(str(chemin))
    except Exception as e:
        return f"CRASH:{type(e).__name__}", f"{type(e).__name__}: {e}"
    return ("DOCUMENT" if isinstance(resultat, Document) else "NONE"), tampon.getvalue()


def main() -> int:
    generer()
    echecs = 0

    fichiers = [("valides", p) for p in sorted(VALIDES.glob("*.json"))] + \
               [("invalides", p) for p in sorted(INVALIDES.glob("*.json"))]

    # Largeur de colonne calculée sur le nom le plus long
    w = max(len(f"{d}/{p.name}") for d, p in fichiers) + 2

    print(f"{'FICHIER':<{w}}{'ATTENDU':<12}{'OBTENU':<28}OK?")
    print("-" * (w + 44))

    for dossier, chemin in fichiers:
        statut, sortie = tester(chemin)          # <- on déballe le tuple ici

        if dossier == "valides":
            attendu, ok = "DOCUMENT", statut == "DOCUMENT"
        else:
            attendu, ok = "CRASH", statut.startswith("CRASH")

        echecs += not ok
        print(f"{dossier + '/' + chemin.name:<{w}}{attendu:<12}{statut:<28}{'✅' if ok else '❌'}")

        if not ok:
            # Affiche la raison de l'échec (3 premières lignes)
            detail = " | ".join(sortie.strip().splitlines()[:3])
            if detail:
                print("      ↳", detail)

    total = len(fichiers)
    print("-" * (w + 44))
    print(f"{total - echecs}/{total} cas conformes")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
