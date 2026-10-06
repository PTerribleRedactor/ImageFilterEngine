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

def BlackWhiteFilter(photo:np.ndarray):   
    gray = 0.299 * photo[:, :, R] +  0.587 * photo[:, :, G] +  0.114 * photo[:, :, B] #first research on internet

    photo[:, :, R] = np.where(gray < 0.5, 0, 1)
    photo[:, :, G] = np.where(gray < 0.5, 0, 1)
    photo[:, :, B] = np.where(gray < 0.5, 0, 1)

def red_divide_2(im:np.ndarray):
    im[:,:,R] = im[:,:,R]/2

def InvertedBlueGreen(photo:np.ndarray):
    dataphoto = photo[:,:,G]
    photo[:,:,G] = photo[:,:,B] 
    photo[:,:,B] = dataphoto

def Brightness(photo:np.ndarray,wish):   

    photo[:, :, R] += wish
    photo[:, :, G] += wish
    photo[:, :, B] += wish

def Contrast(photo:np.ndarray,facteur):
    photo[:, :, R] = np.clip(facteur * (photo[:, :, R]-0.5)+0.5,0,1)
    photo[:, :, G] = np.clip(facteur * (photo[:, :, G]-0.5)+0.5,0,1)
    photo[:, :, B] = np.clip(facteur * (photo[:, :, B]-0.5)+0.5,0,1)

def BlackBorder(photo:np.ndarray,nbpixel:int,color:np.array):
    photo[:nbpixel, :, :] = color
    photo[-nbpixel:, :, :] = color
    photo[:, :nbpixel, :] = color
    photo[:, -nbpixel:, :] = color

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

def Blur(photo:np.ndarray, coef:int):
    height, width, chan = photo.shape
    result = photo.copy()

    for c in range(chan):
        integral = np.cumsum(np.cumsum(photo[:, :, c], axis=0), axis=1)
        for y in range(coef, height - coef):
            for x in range(coef, width - coef):
                total = (integral[y + coef, x + coef]- integral[y - coef, x + coef]- integral[y + coef, x - coef]+ integral[y - coef, x - coef])
                result[y, x, c] = total / ((2 * coef) ** 2)

    photo[:, :, :] = result

def Noisefilter(photo:np.ndarray, coef:float):
    low = -coef
    high = coef
    noise = np.random.uniform(low, high, size=photo.shape)
    return photo+noise

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
    im = array_from_file("cute energy.jpg")
    im = Noisefilter(im, 0.5)
    show_from_array(im)
main()
