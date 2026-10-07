from Input import Load_Image_JSON, FILTRE, BLEND 
from PIL import Image 
import numpy as np 


def charger_image(chemin) -> np.ndarray:
    with Image.open(chemin) as im:
        return np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0   # valeurs 0..1

def charger_image(chemin) -> np.ndarray:
    with Image.open(chemin) as im:
        return np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0   # valeurs 0..1

def appliquer(doc: Document) -> np.ndarray:
    resultat = None
    for layer in doc.layers:
        for filters in doc.layers.filter:
            calque += FILTRES[layer.filtre](charger_image(layer.path_image))
        
        melange = BLENDS[layer.blend](resultat, calque)
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