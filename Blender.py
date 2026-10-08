from PIL import Image
import numpy as np



def resize_to(img: np.ndarray, width: int, height: int) -> np.ndarray:
    """Redimensionne une image float [0,1] (gris, RGB ou RGBA) à (width, height)."""
    adjusted = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    pil = Image.fromarray(adjusted).resize((int(width), int(height)), Image.LANCZOS)
    return np.array(pil) / 255

def resize_cover(img: np.ndarray, width: int, height: int) -> np.ndarray:
    """Remplit exactement (width, height) sans déformer : agrandit/réduit puis rogne au centre."""
    h, w = img.shape[:2]
    scale = max(width / w, height / h)
    new_w = max(width, round(w * scale))
    new_h = max(height, round(h * scale))
    big = resize_to(img, new_w, new_h)
    x0, y0 = (new_w - width) // 2, (new_h - height) // 2
    return big[y0:y0 + height, x0:x0 + width]

def _to_rgba(img: np.ndarray) -> np.ndarray:
    """Convertit une image (gris, RGB ou RGBA) en RGBA, alpha opaque."""
    if img.ndim == 2:
        img = img[..., None]
    if img.shape[2] == 1:
        img = np.repeat(img, 3, axis=2)
    if img.shape[2] == 3:
        opaque = 255 if np.issubdtype(img.dtype, np.integer) else 1.0
        alpha = np.full(img.shape[:2] + (1,), opaque, dtype=img.dtype)
        img = np.concatenate((img, alpha), axis=2)
    return img

def _paste(canvas: np.ndarray, img: np.ndarray, x: int, y: int) -> None:
    """Colle img dans canvas (coin haut-gauche en (x, y)), en rognant ce qui dépasse."""
    H, W = canvas.shape[:2]
    h, w = img.shape[:2]
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, W), min(y + h, H)
    if x0 >= x1 or y0 >= y1:
        return
    canvas[y0:y1, x0:x1] = img[y0 - y:y1 - y, x0 - x:x1 - x]

def ImageReshape(photo1: np.ndarray, photo2: np.ndarray,
                 position_top_left, mode: str = "intersection"):
    """
    Met photo1 et photo2 au même format. photo2 est placée avec son coin
    haut-gauche en (x, y) dans le repère de photo1.

    mode :
      "intersection" : on RÉDUIT les deux images à la zone qu'elles ont en commun
                       (résultat entièrement opaque). Erreur si elles ne se chevauchent pas.
      "union"        : on AGRANDIT les deux images pour tout contenir
                       (transparent là où une image est absente).
      "photo1"       : cadre de photo1 conservé, photo2 rognée / complétée.
      "photo2"       : cadre de photo2 conservé, photo1 rognée / complétée.

    Retourne (result1, result2) : deux images RGBA de même shape.
    """
    x2, y2 = int(position_top_left[0]), int(position_top_left[1])

    photo1 = _to_rgba(photo1)
    photo2 = _to_rgba(photo2)
    h1, w1 = photo1.shape[:2]
    h2, w2 = photo2.shape[:2]

    if mode == "intersection":
        x_min, y_min = max(0, x2), max(0, y2)
        x_max, y_max = min(w1, x2 + w2), min(h1, y2 + h2)
        if x_min >= x_max or y_min >= y_max:
            raise ValueError("Les deux images ne se chevauchent pas : "
                             "mode 'intersection' impossible.")
    elif mode == "union":
        x_min, y_min = min(0, x2), min(0, y2)
        x_max, y_max = max(w1, x2 + w2), max(h1, y2 + h2)
    elif mode == "photo1":
        x_min, y_min, x_max, y_max = 0, 0, w1, h1
    elif mode == "photo2":
        x_min, y_min, x_max, y_max = x2, y2, x2 + w2, y2 + h2
    else:
        raise ValueError(f"mode inconnu : {mode!r}")

    W, H = x_max - x_min, y_max - y_min
    dtype = np.result_type(photo1.dtype, photo2.dtype)
    result1 = np.zeros((H, W, 4), dtype=dtype)
    result2 = np.zeros((H, W, 4), dtype=dtype)

    _paste(result1, photo1, -x_min, -y_min)
    _paste(result2, photo2, x2 - x_min, y2 - y_min)

    return result1, result2

def NormalBlend(photo1: np.ndarray, photo2: np.ndarray, opacity : float):
    return (1 - opacity) * photo1 + opacity * photo2

def MultiplyBlend(photo1: np.ndarray, photo2: np.ndarray):
    return photo1*photo2

def LighterBlend(photo1: np.ndarray, photo2: np.ndarray):
    return 1-(1-photo1)*(1-photo2)

def OverlayBlend(photo1: np.ndarray, photo2: np.ndarray):
    height, width, chan = photo1.shape
    result = photo1.copy()
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            for c in range(chan):
                if photo2[y,x,c] < 0.5:
                    result[y,x,c] = 2*photo2[y,x,c]*photo1[y,x,c]
                else :
                    result[y,x,c] = 1-2*(1-photo1[y,x,c])*(1-photo2[y,x,c])
    return result

def split(img):
    if img.shape[2] == 4:
        return img[..., :3], img[..., 3:4]
    return img, np.ones(img.shape[:2] + (1,), dtype=img.dtype)

def DifferenceBlend(photo1: np.ndarray, photo2: np.ndarray):
    c1, a1 = split(photo1)
    c2, a2 = split(photo2)

    diff = np.abs(c1 - c2)
    rgb = a1 * a2 * diff + a1 * (1 - a2) * c1 + a2 * (1 - a1) * c2
    alpha = a1 + a2 - a1 * a2
    rgb = np.divide(rgb, alpha, out=np.zeros_like(rgb), where=alpha > 0)

    if photo1.shape[2] == 3 and photo2.shape[2] == 3:
        return rgb
    return np.concatenate((rgb, alpha), axis=2)
  
BLEND = {
    "ImageReshape" : ImageReshape,
    "NormalBlend" : NormalBlend,
    "MultiplyBlend" : MultiplyBlend,
    "LighterBlend" : LighterBlend,
    "OverlayBlend" : OverlayBlend, 
    "DifferenceBlend" : DifferenceBlend 
}
    
    
  
  

