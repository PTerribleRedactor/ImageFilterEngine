from Input import Load_Image_JSON, Document 
from Filter import FILTRE   
from Blender import BLEND  
from PIL import Image 
import numpy as np 


def charger_image(chemin) -> np.ndarray:
    with Image.open(chemin) as im:
        return np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0  

def charger_image(chemin) -> np.ndarray:
    with Image.open(chemin) as im:
        return np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0   

def appliquer(doc: Document) -> np.ndarray:
    resultat = None
 
    for layer in doc.layers:
        calque = charger_image(layer.path_image)

        for filtre in layer.filtre:
            nom = filtre.get("filter_name") if isinstance(filtre, dict) else filtre.filter_name
            params = filtre.get("filter_params", {}) if isinstance(filtre, dict) else getattr(filtre, "filter_params", {})

            try:
                calque = FILTRE[nom](calque, **params)
            except KeyError:
                print(f"Filtre inconnu : '{nom}', ignoré.")
            except TypeError as e:
                print(f"Paramètres invalides pour le filtre '{nom}' : {e}. Filtre ignoré.")

        # Premier calque : pas de fusion, on initialise juste le résultat
        if resultat is None:
            resultat = calque
            continue

        # Fusion (blend) avec gestion d'erreur
        try:
            melange = BLEND[layer.blend](resultat, calque)
        except KeyError:
            print(f"Mode de fusion inconnu : '{layer.blend}', calque appliqué sans fusion.")
            melange = calque
        except TypeError as e:
            print(f"Erreur d'application du blend '{layer.blend}' : {e}. Calque appliqué sans fusion.")
            melange = calque

        resultat = (1 - layer.opacity) * resultat + layer.opacity * melange

    return resultat

def sauvegarder(arr: np.ndarray, chemin: str) -> None:
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(chemin)



#take in json
Json_data = Load_Image_JSON()

#apply filters/blend/oppacity for each image
final_im = appliquer(Json_data)

#voir image
Image.fromarray(final_im).show() 

#sauvegarder l'image
sauvegarder(final_im)