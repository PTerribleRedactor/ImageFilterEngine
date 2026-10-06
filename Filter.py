from PIL import Image
import numpy as np

R = 0
B = 1
G = 2

def GrayScale(photo:np.ndarray):
    gray = 0.299 * photo[:, :, R] +  0.587 * photo[:, :, G] +  0.114 * photo[:, :, B]
    photo[:,:,R] = gray
    photo[:,:,G] = gray
    photo[:,:,B] = gray
    return photo

def BlackWhiteFilter(photo:np.ndarray, degree:float):   
    gray = 0.299 * photo[:, :, R] +  0.587 * photo[:, :, G] +  0.114 * photo[:, :, B] #first research on internet

    photo[:, :, R] = np.where(gray < degree, 0, 1)
    photo[:, :, G] = np.where(gray < degree, 0, 1)
    photo[:, :, B] = np.where(gray < degree, 0, 1)
    return photo

def Warm(photo:np.ndarray, wish:float):
    photo[:,:,R] += wish
    return photo

def Cool(photo:np.ndarray, wish:float):
    photo[:,:,B] += wish
    return photo

def InvertedBlueGreen(photo:np.ndarray):
    dataphoto = photo[:,:,G]
    photo[:,:,G] = photo[:,:,B] 
    photo[:,:,B] = dataphoto
    return photo

def InvertedRedBlue(photo:np.ndarray):
    dataphoto = photo[:,:,R]
    photo[:,:,R] = photo[:,:,B] 
    photo[:,:,B] = dataphoto
    return photo

def InvertedGreenRed(photo:np.ndarray):
    dataphoto = photo[:,:,G]
    photo[:,:,G] = photo[:,:,R] 
    photo[:,:,R] = dataphoto
    return photo

def ColorFilter(photo:np.ndarray, color_wish:str):
    try :
        match color_wish:
            case "R":
                photo[:,:,B] = 0
                photo[:,:,G] = 0
            case "G":
                photo[:,:,G] = 0
                photo[:,:,R] = 0
            case "B":
                photo[:,:,B] = 0
                photo[:,:,R] = 0
            case "P":
                photo[:,:,B] = 0
            case "C":
                photo[:,:,R] = 0
            case "Y":
                photo[:,:,G] = 0
            case "M":
                photo[:,:,B] = 0
                photo[:,:,G] *= 0.5
            case "V":
                photo[:,:,B] = 0
                photo[:,:,R] *= 0.7
            case "O":
                photo[:,:,G] = 0
                photo[:,:,B] *= 0.5
            case "T":
                photo[:,:,R] = 0
                photo[:,:,B] *= 0.7
        return photo
    except : print("Error : Color not known")

def ColorBoost(photo:np.ndarray,color_wish:float):
    try :
        match color_wish:
            case "R":
                photo[:,:,R] *= 1.5
            case "B":
                photo[:,:,B] *= 1.5
            case "G":
                photo[:,:,G] *= 1.5
        return photo
    except : print("Error : invalid Color")

def Negative(photo:np.ndarray):
    photo[:, :, :] = 1 - photo[:, :, :]
    return photo

def Posterize(photo: np.ndarray, levels: int):
    step = 1 / (levels - 1)
    photo[:, :, :] = np.round(photo[:, :, :] / step) * step
    return photo

def Brightness(photo:np.ndarray,wish:float):   

    photo[:, :, R] += wish
    photo[:, :, G] += wish
    photo[:, :, B] += wish
    return photo

def Darkness(photo:np.ndarray,wish:float):   

    photo[:, :, R] -= wish
    photo[:, :, G] -= wish
    photo[:, :, B] -= wish
    return photo

def Contrast(photo:np.ndarray,facteur:float):
    photo[:, :, R] = np.clip(facteur * (photo[:, :, R]-0.5)+0.5,0,1)
    photo[:, :, G] = np.clip(facteur * (photo[:, :, G]-0.5)+0.5,0,1)
    photo[:, :, B] = np.clip(facteur * (photo[:, :, B]-0.5)+0.5,0,1)
    return photo

def BlackBorder(photo:np.ndarray,nbpixel:int,color:np.array):
    photo[:nbpixel, :, :] = color
    photo[-nbpixel:, :, :] = color
    photo[:, :nbpixel, :] = color
    photo[:, -nbpixel:, :] = color
    return photo

def Sepia(photo: np.ndarray):
    R = photo[:, :, 0]
    G = photo[:, :, 1]
    B = photo[:, :, 2]
    """
    internet formula 
    """
    new_R = 0.393 * R + 0.769 * G + 0.189 * B 
    new_G = 0.349 * R + 0.686 * G + 0.168 * B
    new_B = 0.272 * R + 0.534 * G + 0.131 * B
    photo[:, :, 0] = np.clip(new_R, 0, 1)
    photo[:, :, 1] = np.clip(new_G, 0, 1)
    photo[:, :, 2] = np.clip(new_B, 0, 1)
    return photo

def Blur(photo:np.ndarray, coef:int):
    height, width, chan = photo.shape
    result = photo.copy()
    for y in range(coef, height - coef):
        for x in range(coef, width - coef):
            for c in range(chan):
                result[y, x, c] = np.mean(photo[y-coef:y+coef, x-coef:x+coef, c])
    photo[:, :, :] = result
    return photo

def Noisefilter(photo:np.ndarray, coef:float):
    low = -coef
    high = coef
    noise = np.random.uniform(low, high, size=photo.shape)
    return photo+noise

def Sharpen(photo: np.ndarray, coef:int):
    height, width, chan = photo.shape
    result = photo.copy()
    for y in range(coef, height - coef):
        for x in range(coef, width - coef):
            for c in range(chan):
                result[y, x, c] = (5 * photo[y, x, c]- photo[y-coef, x, c]- photo[y+coef, x, c]- photo[y, x-coef, c]- photo[y, x+coef, c])
    photo[:, :, :] = np.clip(result, 0, 1)
    return photo

def Emboss(photo: np.ndarray):

    height, width, chan = photo.shape
    result = photo.copy()
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            for c in range(chan):
                result[y, x, c] = (-2 * photo[y-1, x-1, c]-photo[y-1, x, c]+photo[y, x+1, c]-photo[y+1, x, c]+2 * photo[y+1, x+1, c]+0.5)
    photo[:, :, :] = np.clip(result, 0, 1)
    return photo

def Vignette(photo: np.ndarray, strength: float):

    height, width, chan = photo.shape
    center_y = height / 2
    center_x = width / 2
    max_distance = np.sqrt(center_x**2 + center_y**2)
    for y in range(height):
        for x in range(width):
            distance = np.sqrt((x - center_x)**2 +(y - center_y)**2)
            factor = 1 - strength * (distance / max_distance)
            factor = np.clip(factor, 0, 1)
            photo[y, x, :] *= factor
    return photo

def Pixelate(photo: np.ndarray, size: int):
    height, width, chan = photo.shape
    for y in range(0, height, size):
        for x in range(0, width, size):
            block = photo[y:min(y + size, height),x:min(x + size, width),:]
            average = np.mean(block, axis=(0, 1))
            photo[y:min(y + size, height),x:min(x + size, width),:] = average
    return photo

def Solarize(photo: np.ndarray, color_limit: float):
    mask = photo > color_limit
    photo[mask] = 1 - photo[mask]
    return photo

def Gamma(photo: np.ndarray, gamma: float):
    photo[:, :, :] = np.clip(photo[:, :, :] ** gamma,0,1)
    return photo

"""
def Blend(photo1: np.ndarray, photo2: np.ndarray, alpha: float):
    return (1 - alpha) * photo1 + alpha * photo2
"""

"""
Parti test des filtres
"""

def array_to_img(arr:np.ndarray):
    adjusted = np.array(np.clip(arr,0,1)*255,dtype = np.uint8)
    pil_img = Image.fromarray(adjusted)
    return pil_img

def array_from_file(str):
    pil_im = Image.open(str).convert("RGB")
    return np.array(pil_im)/255

def show_from_array(arr:np.ndarray):
    bound_im=np.clip(arr,0,1)
    new_pil_im = array_to_img(bound_im)
    new_pil_im.show()
    input("Press Enter to continue")
    

def main():
    im = array_from_file("C:/Users/tholl/Documents/createch/compsci/workshop2/cute energy.jpg")
    im = Gamma(im,3.4)
    show_from_array(im)
main()
