from Input import Load_Image_JSON, Document 
from Filter import Filter  
from Blender import BLEND, resize_cover 
from PIL import Image 
import numpy as np 


def charger_image(chemin, h1:int, w1:int) -> np.ndarray: 
    with Image.open(chemin) as im:
        arr = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
        if h1 == 0 & w1 == 0 :
            h1, w1 = arr.shape[:2]
            return arr, h1, w1 
        else:
            resized_im = resize_cover(arr ,w1, h1)
            return (resized_im, h1, w1)
        


def appliquer(doc: Document) -> np.ndarray:
    f = Filter()
    resultat = None
    h1 = 0
    w1 = 0
 
    for layer in doc.layers:
        calque, h1, w1 = charger_image(layer.path_image, h1, w1)

        for filtre in layer.filtre:
            nom = filtre.get("filter_name") if isinstance(filtre, dict) else filtre.filter_name
            params = filtre.get("filter_params", {}) if isinstance(filtre, dict) else getattr(filtre, "filter_params", {})
            
            try:
                calque = f.Apply(nom, calque, **params) 
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
final_im.shape[:]

#voir image
im_res = Image.fromarray((np.clip(final_im, 0, 1) * 255).astype(np.uint8))
im_res.show()

#sauvegarder l'image
sauvegarder(final_im, "stockage_image/resulatat.png")