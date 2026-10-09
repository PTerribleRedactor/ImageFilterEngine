from abc import ABC, abstractmethod
import numpy as np
from scipy.signal import convolve2d
         

class Filter(ABC):

    @abstractmethod
    def apply(self, img: np.ndarray) -> np.ndarray:
        ''' Applique le filtre et renvoie une image sous forme de tableau'''
        raise NotImplementedError
    
    

class BrightnessFilter(Filter):
    def __init__(self,params):
        self.level = params["level"]

    def apply(self,img :np.ndarray) -> np.ndarray:
        return np.clip(img + self.level, 0.0, 1.0)

    

class GrayscaleFilter(Filter):
    def apply(self,img: np.ndarray) -> np.ndarray:
        gray = (img[:,:, 0] + img[:, :, 1] + img[:, :, 2]) / 3
        new_img = np.stack((gray, gray, gray),axis = -1)
        return new_img



class GaussianBlurFilter(Filter):
    def __init__(self, params):
        self.window = params["window"]
        self.sigma = params["sigma"]

        if type(self.window) is not int or self.window <= 0 or self.window % 2 == 0:
            raise ValueError("window doit être un entier positif impair")

        if self.sigma <= 0:
            raise ValueError("sigma doit être strictement positif")

    def apply(self, img: np.ndarray) -> np.ndarray:
        radius = self.window // 2
        coordinates = np.arange(-radius, radius + 1)
        x, y = np.meshgrid(coordinates, coordinates)

        kernel = np.exp(-(x**2 + y**2) / (2 * self.sigma**2))
        kernel /= kernel.sum()

        channels = [
            convolve2d(
                img[:, :, channel],
                kernel,
                mode="same",
                boundary="symm",
            )
            for channel in range(img.shape[2])
        ]

        return np.stack(channels, axis=-1).astype(img.dtype, copy=False)


class InvertFilter(Filter):
    def apply(self,img: np.ndarray) -> np.ndarray:
        return 1.0 - img


class ContrastFilter(Filter):
    def __init__(self,params):
        self.factor = params["factor"]

        if self.factor <0:
            raise ValueError("factor doit être positif ou nul ")
        
    def apply(self,img: np.ndarray) -> np.ndarray :
        return np.clip((img - 0.5) * self.factor + 0.5, 0.0, 1.0)
    








