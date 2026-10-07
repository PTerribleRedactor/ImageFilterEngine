"""
Génère des fichiers .json (valides et invalides) puis vérifie que charger() :
  - retourne un objet Document pour les JSON valides ;
  - CRASHE (lève une exception) pour les JSON invalides.

Format testé :
{
  "layers": [
    {
      "path_image": "stockage_image/sashimi.jpg",
      "filtre": [ {"filter_name": "Blur", "filter_params": {"param1": 1.0}} ],
      "blend": "multiply",
      "opacity": 0.5
    }
  ]
}

Utilisation (à la racine du projet, à côté de Input.py et de "stockage_image") :
    python verifier_jsons.py            # lance les vérifications
    python verifier_jsons.py --regen    # réécrit d'abord les .json (écrase vos modifs)

Les .json sont écrits dans tests_json/valides et tests_json/invalides ;
les fichiers "pièges" (faux png, etc.) dans tests_json/fixtures.

Fichier généré par IA, uniquement pour tester le code principal.
"""
import contextlib
import inspect
import io
import json
import os
import sys
from pathlib import Path

from Input import FILTRE, BLEND, Document, charger

# --------------------------------------------------------------------------- #
# Réglages
# --------------------------------------------------------------------------- #
RACINE = Path(__file__).parent
DOSSIER_IMAGES = "stockage_image"
SORTIE = RACINE / "tests_json"
VALIDES = SORTIE / "valides"
INVALIDES = SORTIE / "invalides"
FIXTURES = SORTIE / "fixtures"

# Une liste "filtre" vide ([]) est-elle acceptée par votre modèle ?
# Mettre False si vous avez ajouté Field(min_length=1) sur "filtre".
FILTRE_VIDE_AUTORISE = True

FILTRE_OK = sorted(FILTRE)[0]
FILTRE_2 = sorted(FILTRE)[-1]          # un 2e filtre, pour tester le chaînage
BLEND_OK = sorted(BLEND)[0]

IMAGES = [
    "Liam_sous_courbes.png",
    "Thomas_fait_de_la_guitare.jpg",
    "sashimi.jpg",
    "razer_rgb.jpg",
    "coming_out_de_thomas.jpg",
    "Lulu1.png",
    "Lulu2.png",
]


def trouver_param() -> tuple[str | None, str | None]:
    """Cherche un filtre qui accepte un paramètre (en plus du tableau d'image)."""
    if not isinstance(FILTRE, dict):
        return None, None
    ok = (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
    for nom in sorted(FILTRE):
        try:
            params = list(inspect.signature(FILTRE[nom]).parameters.values())[1:]
        except (TypeError, ValueError):
            continue
        noms = [p.name for p in params if p.kind in ok]
        if noms:
            return nom, noms[0]
    return None, None


NOM_AVEC_PARAM, PARAM = trouver_param()      # ex: ("Blur", "param1")


# --------------------------------------------------------------------------- #
# Briques de construction
# --------------------------------------------------------------------------- #
def img(nom: str) -> str:
    return f"{DOSSIER_IMAGES}/{nom}"


def fspec(nom: str | None = None, params=None, **extra) -> dict:
    """Un élément de la liste 'filtre'. Sans params => clé filter_params absente."""
    d = {"filter_name": FILTRE_OK if nom is None else nom}
    if params is not None:
        d["filter_params"] = params
    d.update(extra)
    return d


def layer(**overrides) -> dict:
    base = {
        "path_image": img("sashimi.jpg"),
        "filtre": [fspec()],
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
# Cas : nom_fichier -> contenu    (dict => JSON ; str commençant par "i0" => brut)
# --------------------------------------------------------------------------- #
CAS_VALIDES = {
    # ---- structure de base ----
    "v01_une_image": doc(layer()),
    "v02_deux_images": doc(layer(), layer(path_image=img("Lulu1.png"))),
    "v03_sept_images": doc(*[layer(path_image=img(n)) for n in IMAGES]),
    "v04_champ_supplementaire_ignore": doc(layer(commentaire="ignoré")),
    "v05_meme_image_deux_fois": doc(layer(), layer()),
    "v06_image_png": doc(layer(path_image=img("Lulu2.png"))),
    "v07_image_jpg": doc(layer(path_image=img("razer_rgb.jpg"))),
    # ---- opacity ----
    "v10_opacity_0": doc(layer(opacity=0)),
    "v11_opacity_1": doc(layer(opacity=1)),
    "v12_opacity_float_0_0": doc(layer(opacity=0.0)),
    "v13_opacity_float_1_0": doc(layer(opacity=1.0)),
    "v14_opacity_0_001": doc(layer(opacity=0.001)),
    "v15_opacity_0_999": doc(layer(opacity=0.999)),
    "v16_opacity_chaine_convertie": doc(layer(opacity="0.5")),
    # ---- filtre (liste de {filter_name, filter_params}) ----
    "v20_filtre_sans_params": doc(layer(filtre=[fspec()])),
    "v21_filtre_params_vide": doc(layer(filtre=[fspec(params={})])),
    "v22_deux_filtres_chaines": doc(layer(filtre=[fspec(FILTRE_OK), fspec(FILTRE_2)])),
    "v23_meme_filtre_deux_fois": doc(layer(filtre=[fspec(), fspec()])),
    "v24_cle_en_trop_dans_filtre_ignoree": doc(layer(filtre=[fspec(note="ignoré")])),
    "v25_trois_filtres_sur_deux_layers": doc(
        layer(filtre=[fspec(), fspec(FILTRE_2), fspec()]),
        layer(filtre=[fspec(FILTRE_2)], path_image=img("Lulu1.png")),
    ),
}
if FILTRE_VIDE_AUTORISE:
    CAS_VALIDES["v26_filtre_liste_vide"] = doc(layer(filtre=[]))

if PARAM:
    CAS_VALIDES["v30_param_connu_float"] = doc(
        layer(filtre=[fspec(NOM_AVEC_PARAM, {PARAM: 1.0})]))
    CAS_VALIDES["v31_param_connu_entier"] = doc(
        layer(filtre=[fspec(NOM_AVEC_PARAM, {PARAM: 1})]))
    CAS_VALIDES["v32_param_connu_chaine_numerique"] = doc(
        layer(filtre=[fspec(NOM_AVEC_PARAM, {PARAM: "1.0"})]))
    CAS_VALIDES["v33_param_negatif_ou_nul"] = doc(
        layer(filtre=[fspec(NOM_AVEC_PARAM, {PARAM: 0})]))

# Une entrée par nom de filtre et de blend connus
for _i, _f in enumerate(sorted(FILTRE)):
    CAS_VALIDES[f"v40_filtre_{_i}"] = doc(layer(filtre=[fspec(_f)]))
for _i, _b in enumerate(sorted(BLEND)):
    CAS_VALIDES[f"v41_blend_{_i}"] = doc(layer(blend=_b))


CAS_INVALIDES = {
    # ---- syntaxe JSON cassée (texte brut) ----
    "i01_syntaxe_virgule_finale": '{"layers": [],}',
    "i02_syntaxe_accolade_non_fermee": '{"layers": [',
    "i03_syntaxe_fichier_vide": "",
    "i04_syntaxe_guillemets_simples": "{'layers': []}",
    "i05_syntaxe_backslash_windows": (
        '{"layers": [{"path_image": "C:\\Users\\moi\\a.png", '
        f'"blend": "{BLEND_OK}", "opacity": 0.5}}]}}'
    ),
    "i06_syntaxe_commentaire": '{"layers": [] // commentaire\n}',
    "i07_syntaxe_texte_quelconque": "bonjour",
    # Votre erreur d'origine : paire clé:valeur dans un tableau []
    "i08_syntaxe_params_tableau_avec_cle_valeur": (
        '{"layers": [{"path_image": "' + img("sashimi.jpg") + '", '
        '"filtre": [{"filter_name": "' + FILTRE_OK + '", '
        '"filter_params": ["param1" : "1.0"]}], '
        f'"blend": "{BLEND_OK}", "opacity": 0.5}}]}}'
    ),
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
    "i90_path_absent": doc(sans("path_image")),
    "i91_path_null": doc(layer(path_image=None)),
    # ---- filtre : forme générale (doit être une liste d'objets) ----
    "i40_filtre_ancienne_forme_chaine": doc(layer(filtre=FILTRE_OK)),
    "i41_filtre_objet_au_lieu_de_liste": doc(layer(filtre=fspec())),
    "i42_filtre_null": doc(layer(filtre=None)),
    "i43_filtre_absent": doc(sans("filtre")),
    "i44_filtre_entier": doc(layer(filtre=123)),
    "i45_filtre_element_chaine": doc(layer(filtre=[FILTRE_OK])),
    "i46_filtre_element_null": doc(layer(filtre=[None])),
    "i47_filtre_element_objet_vide": doc(layer(filtre=[{}])),
    "i48_filtre_element_liste": doc(layer(filtre=[[fspec()]])),
    "i49_filtre_deuxieme_element_invalide": doc(
        layer(filtre=[fspec(), fspec("inconnu")])),
    # ---- filtre : filter_name ----
    "i50_filter_name_inconnu": doc(layer(filtre=[fspec("inconnu")])),
    "i51_filter_name_vide": doc(layer(filtre=[fspec("")])),
    "i52_filter_name_mauvaise_casse": doc(layer(filtre=[fspec(FILTRE_OK.swapcase())])),
    "i53_filter_name_espaces": doc(layer(filtre=[fspec(f" {FILTRE_OK} ")])),
    "i54_filter_name_valeur_de_blend": doc(layer(filtre=[fspec(BLEND_OK)])),
    "i55_filter_name_entier": doc(layer(filtre=[{"filter_name": 123}])),
    "i56_filter_name_null": doc(layer(filtre=[{"filter_name": None}])),
    "i57_filter_name_liste": doc(layer(filtre=[{"filter_name": [FILTRE_OK]}])),
    "i58_filter_name_absent_mais_params": doc(layer(filtre=[{"filter_params": {}}])),
    # ---- filtre : filter_params ----
    "i60_params_forme_liste_vide": doc(layer(filtre=[fspec(params=[])])),
    "i61_params_forme_liste_de_paires": doc(
        layer(filtre=[fspec(params=[{"param1": 1.0}])])),
    "i62_params_forme_liste_de_chaines": doc(
        layer(filtre=[fspec(params=["param1", "1.0"])])),
    "i63_params_chaine": doc(layer(filtre=[fspec(params="param1=1.0")])),
    "i64_params_null": doc(layer(filtre=[fspec(params=None, filter_params=None)])),
    "i65_params_entier": doc(layer(filtre=[fspec(params=5)])),
    "i66_params_nom_inconnu": doc(
        layer(filtre=[fspec(params={"parametre_inexistant": 1.0})])),
    "i67_params_un_connu_un_inconnu": doc(
        layer(filtre=[fspec(NOM_AVEC_PARAM or FILTRE_OK,
                            {**({PARAM: 1.0} if PARAM else {}), "inconnu": 1.0})])),
    # ---- blend ----
    "i70_blend_inconnu": doc(layer(blend="inconnu")),
    "i71_blend_vide": doc(layer(blend="")),
    "i72_blend_mauvaise_casse": doc(layer(blend=BLEND_OK.swapcase())),
    "i73_blend_espaces": doc(layer(blend=f" {BLEND_OK} ")),
    "i74_blend_valeur_de_filtre": doc(layer(blend=FILTRE_OK)),
    "i75_blend_entier": doc(layer(blend=123)),
    "i76_blend_liste": doc(layer(blend=[BLEND_OK])),
    "i77_blend_null": doc(layer(blend=None)),
    "i78_blend_absent": doc(sans("blend")),
    # ---- opacity ----
    "i80_opacity_negative": doc(layer(opacity=-0.1)),
    "i81_opacity_superieure_a_1": doc(layer(opacity=1.1)),
    "i82_opacity_tres_grande": doc(layer(opacity=100)),
    "i83_opacity_chaine_non_numerique": doc(layer(opacity="abc")),
    "i84_opacity_chaine_vide": doc(layer(opacity="")),
    "i85_opacity_pourcentage": doc(layer(opacity="50%")),
    "i86_opacity_virgule_decimale": doc(layer(opacity="0,5")),
    "i87_opacity_null": doc(layer(opacity=None)),
    "i88_opacity_liste": doc(layer(opacity=[0.5])),
    "i89_opacity_absente": doc(sans("opacity")),
    "i92_opacity_nan_chaine": doc(layer(opacity="nan")),
    "i93_opacity_inf_chaine": doc(layer(opacity="inf")),
    # ---- plusieurs layers / erreurs multiples ----
    "i95_deuxieme_layer_invalide": doc(layer(), layer(opacity=5)),
    "i96_dernier_layer_invalide": doc(
        *[layer(path_image=img(n)) for n in IMAGES], layer(blend="nope")),
    "i97_erreurs_multiples_dans_un_layer": doc(
        layer(filtre=[fspec("x")], blend="y", opacity=9,
              path_image=img("absent.png"))),
    "i98_erreurs_sur_plusieurs_layers": doc(
        layer(filtre=[fspec("x")]), layer(), layer(blend="y")),
    "i99_erreur_dans_filtre_du_second_layer": doc(
        layer(), layer(filtre=[fspec(), fspec(params={"inconnu": 1.0})])),
}

if not FILTRE_VIDE_AUTORISE:
    CAS_INVALIDES["i46b_filtre_liste_vide"] = doc(layer(filtre=[]))

if PARAM:
    CAS_INVALIDES["i68_param_valeur_non_numerique"] = doc(
        layer(filtre=[fspec(NOM_AVEC_PARAM, {PARAM: "abc"})]))
    CAS_INVALIDES["i69_param_valeur_null"] = doc(
        layer(filtre=[fspec(NOM_AVEC_PARAM, {PARAM: None})]))
    CAS_INVALIDES["i69b_param_valeur_liste"] = doc(
        layer(filtre=[fspec(NOM_AVEC_PARAM, {PARAM: [1.0]})]))
    CAS_INVALIDES["i69c_param_valeur_objet"] = doc(
        layer(filtre=[fspec(NOM_AVEC_PARAM, {PARAM: {"a": 1}})]))
    CAS_INVALIDES["i69d_param_valeur_vide"] = doc(
        layer(filtre=[fspec(NOM_AVEC_PARAM, {PARAM: ""})]))


# --------------------------------------------------------------------------- #
# Génération des fichiers (sans supprimer de dossier : évite les erreurs
# de permission avec OneDrive / Explorateur Windows)
# --------------------------------------------------------------------------- #
def ecrire(dossier: Path, nom: str, contenu) -> None:
    chemin = dossier / f"{nom}.json"
    if isinstance(contenu, str) and nom.startswith("i0"):
        chemin.write_text(contenu, encoding="utf-8")            # texte brut
    else:
        chemin.write_text(json.dumps(contenu, indent=2, ensure_ascii=False),
                          encoding="utf-8")


def generer() -> None:
    for dossier in (VALIDES, INVALIDES, FIXTURES):
        dossier.mkdir(parents=True, exist_ok=True)

    # Supprime les anciens .json (cas renommés ou supprimés depuis)
    for dossier in (VALIDES, INVALIDES):
        for f in dossier.glob("*.json"):
            f.unlink()

    # Fichiers "pièges" référencés par certains JSON invalides
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
    """Retourne (statut, détail). statut = DOCUMENT | NONE | CRASH:<Exception>."""
    tampon = io.StringIO()
    try:
        with contextlib.redirect_stdout(tampon):
            resultat = charger(str(chemin))
    except (Exception, SystemExit) as e:          # SystemExit : si charger() fait sys.exit
        return f"CRASH:{type(e).__name__}", f"{type(e).__name__}: {e}"
    statut = "DOCUMENT" if isinstance(resultat, Document) else "NONE"
    return statut, tampon.getvalue()


def main() -> int:
    os.chdir(RACINE)                               # les chemins relatifs des JSON en dépendent
    if "--regen" in sys.argv or not SORTIE.exists():
        generer()

    fichiers = [("valides", p) for p in sorted(VALIDES.glob("*.json"))] + \
               [("invalides", p) for p in sorted(INVALIDES.glob("*.json"))]
    if not fichiers:
        print("Aucun .json trouvé : lancez avec --regen")
        return 1

    echecs = 0
    w = max(len(f"{d}/{p.name}") for d, p in fichiers) + 2

    print(f"{'FICHIER':<{w}}{'ATTENDU':<12}{'OBTENU':<28}OK?")
    print("-" * (w + 44))

    for dossier, chemin in fichiers:
        statut, sortie = tester(chemin)

        if dossier == "valides":
            attendu, ok = "DOCUMENT", statut == "DOCUMENT"
        else:
            ERREURS_ATTENDUES = {"CRASH:JSONDecodeError", "CRASH:ValidationError"}
            attendu, ok = "CRASH", statut in ERREURS_ATTENDUES

        echecs += not ok
        print(f"{dossier + '/' + chemin.name:<{w}}{attendu:<12}{statut:<28}{'✅' if ok else '❌'}")

        if not ok:
            detail = " | ".join(sortie.strip().splitlines()[:3])
            if detail:
                print("      ↳", detail)

    total = len(fichiers)
    print("-" * (w + 44))
    print(f"{total - echecs}/{total} cas conformes")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())