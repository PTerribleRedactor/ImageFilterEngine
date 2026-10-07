from PIL import Image
import numpy as np

def ImageReshape(photo1: np.ndarray, photo2: np.ndarray, position_top_left: np.array):

    height1, width1, _ = photo1.shape
    height2, width2, _ = photo2.shape
    height = max(height1, height2)
    width = max(width1, width2)
    

    #RGB to RGBA
    alpha1 = np.ones((height1, width1, 1))
    alpha2 = np.ones((height2, width2, 1))

    photo1 = np.concatenate((photo1, alpha1), axis=2)
    photo2 = np.concatenate((photo2, alpha2), axis=2)

    #Transparent
    result1 = np.zeros((height, width, 4))
    result2 = np.zeros((height, width, 4))

    x1 = (width - width1) // 2
    y1 = (height - height1) // 2
    x2 = position_top_left[0]
    y2 = position_top_left[1]

    

    result1[y1:y1 + height1, x1:x1 + width1] = photo1
    result2[y2:y2 + height2, x2:x2 + width2] = photo2

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

def DifferenceBlend(photo1: np.ndarray, photo2: np.ndarray):
    return np.abs(photo1-photo2)

BLEND = {
    "ImageReshape" : ImageReshape,
    "NormalBlend" : NormalBlend,
    "MultiplyBlend" : MultiplyBlend,
    "LighterBlend" : LighterBlend,
    "OverlayBlend" : OverlayBlend, 
    "DifferenceBlend" : DifferenceBlend 
}