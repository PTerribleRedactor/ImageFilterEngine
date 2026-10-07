from PIL import Image
import numpy as np

R = 0
B = 1
G = 2

def CheckPhoto(photo):
    try:
        if not isinstance(photo, np.ndarray):
            raise TypeError("photo must be a numpy.ndarray")

        if photo.ndim != 3:
            raise ValueError("photo must have 3 dimensions")

        if photo.shape[2] != 3:
            raise ValueError("photo must have exactly 3 color channels")

        if photo.shape[0] <= 0 or photo.shape[1] <= 0:
            raise ValueError("photo must have a valid width and height")

        if not np.issubdtype(photo.dtype, np.number):
            raise TypeError("photo must contain numerical values")

        if not np.all(np.isfinite(photo)):
            raise ValueError("photo contains NaN or infinite values")

        if np.any(photo < 0) or np.any(photo > 1):
            raise ValueError("photo values must be between 0 and 1")

        return True
    except Exception as error:
        print(f"Photo error: {error}")
        return False


def GrayScale(photo:np.ndarray):
    try:
        if not CheckPhoto(photo):
            return None
        gray = 0.299 * photo[:, :, R] +  0.587 * photo[:, :, G] +  0.114 * photo[:, :, B]
        photo[:,:,R] = gray
        photo[:,:,G] = gray
        photo[:,:,B] = gray
        return photo
    except Exception as error:
        print(f"grayScale error: {error}")
        return None

def BlackWhiteFilter(photo:np.ndarray, degree:float):   
    try :
        if not CheckPhoto(photo):
            return None

        if not isinstance(degree, (int, float, np.number)):
            raise TypeError("degree must be a number")

        if not np.isfinite(degree):
            raise ValueError("degree must be finite")

        if not 0 <= degree <= 1:
            raise ValueError("degree must be between 0 and 1")
        
        gray = 0.299 * photo[:, :, R] +  0.587 * photo[:, :, G] +  0.114 * photo[:, :, B] #first research on internet
        
        photo[:, :, R] = np.where(gray < degree, 0, 1)
        photo[:, :, G] = np.where(gray < degree, 0, 1)
        photo[:, :, B] = np.where(gray < degree, 0, 1)
        return photo
    except Exception as error:
        print(f"BlackWhiteFilter error: {error}")
        return None

def Warm(photo:np.ndarray, wish:float):
    try:
        if not CheckPhoto(photo):
            return None

        if not isinstance(wish, (int, float, np.number)):
            raise TypeError("wish must be a number")

        if not np.isfinite(wish):
            raise ValueError("wish must be finite")
        photo[:,:,R] += wish
        return photo
    except Exception as error:
        print(f"Warm error: {error}")
        return None

def Cool(photo:np.ndarray, wish:float):
    try:
        if not CheckPhoto(photo):
            return None

        if not isinstance(wish, (int, float, np.number)):
            raise TypeError("wish must be a number")

        if not np.isfinite(wish):
            raise ValueError("wish must be finite")

        photo[:,:,B] += wish
        return photo
    except Exception as error:
        print(f"Cool error: {error}")
        return None

def InvertedBlueGreen(photo:np.ndarray):
    try:
        if not CheckPhoto(photo):
            return None
        dataphoto = photo[:,:,G]
        photo[:,:,G] = photo[:,:,B] 
        photo[:,:,B] = dataphoto
        return photo
    except Exception as error:
        print(f"InvertedBlueGreen error: {error}")
        return None

def InvertedRedBlue(photo:np.ndarray):
    try:
        if not CheckPhoto(photo):
            return None
        dataphoto = photo[:,:,R]
        photo[:,:,R] = photo[:,:,B] 
        photo[:,:,B] = dataphoto
        return photo
    except Exception as error:
        print(f"InvertedRedBlue error: {error}")
        return None

def InvertedGreenRed(photo:np.ndarray):
    try:
        if not CheckPhoto(photo):
            return None

        dataphoto = photo[:,:,G]
        photo[:,:,G] = photo[:,:,R] 
        photo[:,:,R] = dataphoto
        return photo
    except Exception as error:
        print(f"InvertedGreenRed error: {error}")
        return None

def ColorFilter(photo:np.ndarray, color_wish:str):
    try :
        if not CheckPhoto(photo):
            return None

        if not isinstance(color_wish, str):
            raise TypeError("color_wish must be a string")

        color_wish = color_wish.upper()
        if color_wish not in ["R", "G", "B", "P", "C", "Y", "M", "V", "O", "T"]:
            raise ValueError("color must be R, G, B, P, C, Y, M, V, O or T")
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
    except Exception as error:
        print(f"ColorFilter error: {error}")
        return None

def ColorBoost(photo:np.ndarray,color_wish:float):
    try :
        if not CheckPhoto(photo):
            return None
        if not isinstance(color_wish, str):
            raise TypeError("color_wish must be a string")
        color_wish = color_wish.upper()
        if color_wish not in ["R", "G", "B"]:
            raise ValueError("color must be R, G or B")
        match color_wish:
            case "R":
                photo[:,:,R] *= 1.5
            case "B":
                photo[:,:,B] *= 1.5
            case "G":
                photo[:,:,G] *= 1.5
        return photo
    except Exception as error:
        print(f"ColorBoost error: {error}")
        return None
    
def Negative(photo:np.ndarray):
    try:
        if not CheckPhoto(photo):
            return None
        photo[:, :, :] = 1 - photo[:, :, :]
        return photo
    except Exception as error:
        print(f"Negative error: {error}")
        return None

def Posterize(photo: np.ndarray, levels: int):
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(levels, (int, np.integer)):
            raise TypeError("levels must be an integer")
        if levels < 2:
            raise ValueError("levels must be greater than or equal to 2")
        step = 1 / (levels - 1)
        photo[:, :, :] = np.round(photo[:, :, :] / step) * step
        photo[:, :, :] = np.clip(photo[:, :, :], 0, 1)
        return photo
    except Exception as error:
        print(f"Posterize error: {error}")
        return None

def Brightness(photo:np.ndarray,wish:float):   
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(wish, (int, float, np.number)):
            raise TypeError("wish must be a number")
        if not np.isfinite(wish):
            raise ValueError("wish must be finite")
        photo[:, :, R] += wish
        photo[:, :, G] += wish
        photo[:, :, B] += wish
    except Exception as error:
            print(f"Brightness error: {error}")
            return None

def Darkness(photo:np.ndarray,wish:float):   
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(wish, (int, float, np.number)):
            raise TypeError("wish must be a number")
        if not np.isfinite(wish):
            raise ValueError("wish must be finite")
        photo[:, :, R] -= wish
        photo[:, :, G] -= wish
        photo[:, :, B] -= wish
        return photo
    except Exception as error:
        print(f"Darkness error: {error}")
        return None

def Contrast(photo:np.ndarray,facteur:float):
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(facteur, (int, float, np.number)):
            raise TypeError("facteur must be a number")
        if not np.isfinite(facteur):
            raise ValueError("facteur must be finite")
        if facteur < 0:
            raise ValueError("facteur must be greater than or equal to 0")
        photo[:, :, R] = np.clip(facteur * (photo[:, :, R]-0.5)+0.5,0,1)
        photo[:, :, G] = np.clip(facteur * (photo[:, :, G]-0.5)+0.5,0,1)
        photo[:, :, B] = np.clip(facteur * (photo[:, :, B]-0.5)+0.5,0,1)
        return photo
    except Exception as error:
        print(f"Contrast error: {error}")
        return None

def BlackBorder(photo:np.ndarray,nbpixel:int,color:np.array):
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(nbpixel, (int, np.integer)):
            raise TypeError("nbpixel must be an integer")
        if nbpixel <= 0:
            raise ValueError("nbpixel must be greater than 0")
        if nbpixel > min(photo.shape[0], photo.shape[1]) // 2:
            raise ValueError("nbpixel is too large for the image")
        if not isinstance(color, np.ndarray):
            raise TypeError("color must be a numpy.ndarray")
        if color.shape != (3,):
            raise ValueError("color must contain exactly 3 values")
        if not np.issubdtype(color.dtype, np.number):
            raise TypeError("color must contain numerical values")
        if np.any(color < 0) or np.any(color > 1):
            raise ValueError("color values must be between 0 and 1")
        photo[:nbpixel, :, :] = color
        photo[-nbpixel:, :, :] = color
        photo[:, :nbpixel, :] = color
        photo[:, -nbpixel:, :] = color
        return photo
    except Exception as error:
        print(f"BlackBorder error: {error}")
        return None

def Sepia(photo: np.ndarray):
    try:
        if not CheckPhoto(photo):
            return None
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
    except Exception as error:
        print(f"Sepia error: {error}")
        return None

def Blur(photo:np.ndarray, coef:int):
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(coef, (int, np.integer)):
            raise TypeError("coef must be an integer")
        if coef <= 0:
            raise ValueError("coef must be greater than 0")
        height, width, chan = photo.shape
        if coef >= min(height, width) / 2:
            raise ValueError("coef is too large for the image")
        result = photo.copy()
        for y in range(coef, height - coef):
            for x in range(coef, width - coef):
                for c in range(chan):
                    result[y, x, c] = np.mean(photo[y-coef:y+coef, x-coef:x+coef, c])
        photo[:, :, :] = result
        return photo
    except Exception as error:
        print(f"Blur error: {error}")
        return None

def Noisefilter(photo:np.ndarray, coef:float):
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(coef, (int, float, np.number)):
            raise TypeError("coef must be a number")
        if not np.isfinite(coef):
            raise ValueError("coef must be finite")
        if coef < 0:
            raise ValueError("coef must be greater than or equal to 0")
        low = -coef
        high = coef
        noise = np.random.uniform(low, high, size=photo.shape)
        return photo+noise
    except Exception as error:
        print(f"Noisefilter error: {error}")
        return None

def Sharpen(photo: np.ndarray, coef:int):
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(coef, (int, np.integer)):
            raise TypeError("coef must be an integer")
        if coef <= 0:
            raise ValueError("coef must be greater than 0")
        height, width, chan = photo.shape
        result = photo.copy()
        for y in range(coef, height - coef):
            for x in range(coef, width - coef):
                for c in range(chan):
                    result[y, x, c] = (5 * photo[y, x, c]- photo[y-coef, x, c]- photo[y+coef, x, c]- photo[y, x-coef, c]- photo[y, x+coef, c])
        photo[:, :, :] = np.clip(result, 0, 1)
        return photo
    except Exception as error:
        print(f"Sharpen error: {error}")
        return None

def Emboss(photo: np.ndarray):
    try:
        if not CheckPhoto(photo):
            return None
        height, width, chan = photo.shape
        result = photo.copy()
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                for c in range(chan):
                    result[y, x, c] = (-2 * photo[y-1, x-1, c]-photo[y-1, x, c]+photo[y, x+1, c]-photo[y+1, x, c]+2 * photo[y+1, x+1, c]+0.5)
        photo[:, :, :] = np.clip(result, 0, 1)
        return photo
    except Exception as error:
        print(f"Emboss error: {error}")
        return None

def Vignette(photo: np.ndarray, strength: float):
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(strength, (int, float, np.number)):
            raise TypeError("strength must be a number")
        if not np.isfinite(strength):
            raise ValueError("strength must be finite")
        if not 0 <= strength <= 1:
            raise ValueError("strength must be between 0 and 1")
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
    except Exception as error:
        print(f"Vignette error: {error}")
        return None

def Pixelate(photo: np.ndarray, size: int):
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(size, (int, np.integer)):
            raise TypeError("size must be an integer")
        if size <= 0:
            raise ValueError("size must be greater than 0")
        height, width, chan = photo.shape
        for y in range(0, height, size):
            for x in range(0, width, size):
                block = photo[y:min(y + size, height),x:min(x + size, width),:]
                average = np.mean(block, axis=(0, 1))
                photo[y:min(y + size, height),x:min(x + size, width),:] = average
        return photo
    except Exception as error:
        print(f"Pixelate error: {error}")
        return None

def Solarize(photo: np.ndarray, color_limit: float):
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(color_limit, (int, float, np.number)):
            raise TypeError("color_limit must be a number")
        if not np.isfinite(color_limit):
            raise ValueError("color_limit must be finite")
        if not 0 <= color_limit <= 1:
            raise ValueError("color_limit must be between 0 and 1")
        mask = photo > color_limit
        photo[mask] = 1 - photo[mask]
        return photo
    except Exception as error:
        print(f"Solarize error: {error}")
        return None

def Gamma(photo: np.ndarray, gamma: float):
    try:
        if not CheckPhoto(photo):
            return None
        if not isinstance(gamma, (int, float, np.number)):
            raise TypeError("gamma must be a number")
        if not np.isfinite(gamma):
            raise ValueError("gamma must be finite")
        if gamma <= 0:
            raise ValueError("gamma must be greater than 0")
        photo[:, :, :] = np.clip(photo[:, :, :] ** gamma,0,1)
        return photo
    except Exception as error:
        print(f"Gamma error: {error}")
        return None



FILTRE = {
    "GrayScale" : GrayScale, 
    "BlackWhiteFilter" : BlackWhiteFilter, 
    "Warm" : Warm,
    "Cool" : Cool,
    "InvertedBlueGreen" : InvertedBlueGreen,
    "InvertedRedBlue" : InvertedRedBlue,
    "InvertedGreenRed" : InvertedGreenRed,
    "ColorFilter" : ColorFilter,
    "ColorBoost" : ColorBoost,
    "Negative" : Negative,
    "Posterize" : Posterize,
    "Brightness" : Brightness,
    "Darkness" : Darkness,
    "Contrast" : Contrast,
    "BlackBorder" : BlackBorder,
    "Sepia" : Sepia,
    "Blur" : Blur,
    "Noisefilter" : Noisefilter,
    "Sharpen" : Sharpen,
    "Emboss" : Emboss,
    "Vignette" : Vignette,
    "Pixelate" : Pixelate,
    "Solarize" : Solarize,
    "Gamma" : Gamma
}  



