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

def alpha_count(r: np.ndarray) -> int:
    """Nombre de pixels visibles (alpha > 0)."""
    return int((r[..., 3] > 0).sum())


def make_coord_img(h: int, w: int) -> np.ndarray:
    """Image dont chaque pixel (x, y) contient [x, y, 0] -> permet de vérifier l'alignement."""
    img = np.zeros((h, w, 3))
    img[..., 0] = np.arange(w)[None, :]
    img[..., 1] = np.arange(h)[:, None]
    return img


def run_tests():
    p1 = np.full((100, 200, 3), 0.2)      # h=100, w=200
    p2 = np.full((20, 30, 3), 0.8)        # h=20,  w=30
    big = np.full((300, 400, 3), 0.8)     # h=300, w=400

    def check(r1, r2, shape, a1=None, a2=None):
        assert r1.shape == r2.shape == shape, f"shape {r1.shape} / {r2.shape} != {shape}"
        if a1 is not None:
            assert alpha_count(r1) == a1, f"alpha r1 = {alpha_count(r1)} != {a1}"
        if a2 is not None:
            assert alpha_count(r2) == a2, f"alpha r2 = {alpha_count(r2)} != {a2}"

    r1, r2 = ImageReshape(p1, p2, [10, 10], "intersection")        
    check(r1, r2, (20, 30, 4), 600, 600)

    r1, r2 = ImageReshape(p1, p2, [190, 90], "intersection")       
    check(r1, r2, (10, 10, 4), 100, 100)

    r1, r2 = ImageReshape(p1, p2, [-10, -5], "intersection")       
    check(r1, r2, (15, 20, 4), 300, 300)

    r1, r2 = ImageReshape(p1, big, [0, 0], "intersection")    
    check(r1, r2, (100, 200, 4), 20000, 20000)

    r1, r2 = ImageReshape(p1, big, [-50, -20], "intersection")   
    check(r1, r2, (100, 200, 4), 20000, 20000)

    for pos in ([500, 500], [200, 0], [0, 100], [-30, 0], [0, -20]):   
        try:
            ImageReshape(p1, p2, pos, "intersection")
            assert False, f"ValueError attendue pour {pos}"
        except ValueError:
            pass

    r1, r2 = ImageReshape(p1, p2, [10, 10], "union")
    check(r1, r2, (100, 200, 4), 20000, 600)

    r1, r2 = ImageReshape(p1, p2, [190, 90], "union")
    check(r1, r2, (110, 220, 4), 20000, 600)

    r1, r2 = ImageReshape(p1, p2, [-10, -5], "union")
    check(r1, r2, (105, 210, 4), 20000, 600)

    r1, r2 = ImageReshape(p1, big, [-50, -20], "union")
    check(r1, r2, (300, 400, 4), 20000, 120000)

    r1, r2 = ImageReshape(p1, p2, [500, 500], "union")            
    check(r1, r2, (520, 530, 4), 20000, 600)

    r1, r2 = ImageReshape(p1, p2, [10, 10], "photo1")
    check(r1, r2, (100, 200, 4), 20000, 600)

    r1, r2 = ImageReshape(p1, p2, [190, 90], "photo1")         
    check(r1, r2, (100, 200, 4), 20000, 100)

    r1, r2 = ImageReshape(p1, p2, [-10, -5], "photo1")
    check(r1, r2, (100, 200, 4), 20000, 300)

    r1, r2 = ImageReshape(p1, big, [0, 0], "photo1")
    check(r1, r2, (100, 200, 4), 20000, 20000)

    r1, r2 = ImageReshape(p1, p2, [500, 500], "photo1")            
    check(r1, r2, (100, 200, 4), 20000, 0)

    r1, r2 = ImageReshape(p1, p2, [10, 10], "photo2")
    check(r1, r2, (20, 30, 4), 600, 600)

    r1, r2 = ImageReshape(p1, p2, [190, 90], "photo2")            
    check(r1, r2, (20, 30, 4), 100, 600)

    r1, r2 = ImageReshape(p1, big, [-50, -20], "photo2")        
    check(r1, r2, (300, 400, 4), 20000, 120000)

    c1 = make_coord_img(100, 200)
    c2 = make_coord_img(20, 30)

    r1, r2 = ImageReshape(c1, c2, [10, 10], "intersection")
    assert np.allclose(r1[0, 0, :2], [10, 10]) and np.allclose(r2[0, 0, :2], [0, 0])
    assert np.allclose(r1[-1, -1, :2], [39, 29]) and np.allclose(r2[-1, -1, :2], [29, 19])

    r1, r2 = ImageReshape(c1, c2, [-10, -5], "intersection")       
    assert np.allclose(r1[0, 0, :2], [0, 0]) and np.allclose(r2[0, 0, :2], [10, 5])

    r1, r2 = ImageReshape(c1, c2, [-10, -5], "union")          
    assert np.allclose(r1[5, 10, :2], [0, 0]) and np.allclose(r2[0, 0, :2], [0, 0])
    assert r1[0, 0, 3] == 0 and r2[104, 209, 3] == 0               

    r1, r2 = ImageReshape(c1, c2, [190, 90], "photo2")         
    assert np.allclose(r1[0, 0, :2], [190, 90]) and np.allclose(r2[0, 0, :2], [0, 0])
    assert r1[0, 10, 3] == 0                                   

    g = np.full((10, 10), 0.5)                                  
    r1, r2 = ImageReshape(p1, g, [0, 0], "intersection")
    check(r1, r2, (10, 10, 4), 100, 100)

    rgba = np.concatenate((p2, np.full((20, 30, 1), 0.5)), axis=2)
    r1, r2 = ImageReshape(p1, rgba, [0, 0], "photo1")
    assert r2[0, 0, 3] == 0.5

    r1, r2 = ImageReshape(p1, p2, [0, 0], "union")               
    assert r1[..., 3].max() == 1.0 and r2[..., 3].max() == 1.0

    u1, u2 = np.full((10, 10, 3), 50, np.uint8), np.full((5, 5, 3), 200, np.uint8)
    r1, r2 = ImageReshape(u1, u2, [0, 0], "union")                
    assert r1.dtype == np.uint8 and r1[..., 3].max() == 255

    r1, r2 = ImageReshape(p1, p2, np.array([10, 10]), "union")     
    check(r1, r2, (100, 200, 4))

    try:                                                      
        ImageReshape(p1, p2, [0, 0], "nimporte")
        assert False, "ValueError attendue"
    except ValueError:
        pass

    print("Tous les tests passent")


def main():
    run_tests()

    im1 = array_from_file("stockage_image/coming_out_de_thomas.jpg")
    im2 = array_from_file("stockage_image/sashimi.jpg")
    h1, w1 = im1.shape[:2]
    im2 = resize_cover(im2, w1, h1)
    im1 = Sepia(im1)
    im2 = Pixelate(im2, 40)
    position = [0, 0]
    print(f"im1 : {w1}x{h1} px | im2 : {im2.shape[1]}x{im2.shape[0]} px | position : {position}")

    try:
        r_fond, r_insert = ImageReshape(im1, im2, position, mode="intersection")
    except ValueError as e:
        print("Erreur :", e)
        return

    print("Format commun :", r_fond.shape)
    im = NormalBlend(r_fond, r_insert, 0.7)
    show_from_array(im)


main()

