from Blender import *
from Filter import *



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
    im1 = array_from_file("stockage_image/coming_out_de_thomas.jpg")
    im2 = array_from_file("stockage_image/sashimi.jpg")
    im1 = Sepia(im1)
    show_from_array(im1)
main()

