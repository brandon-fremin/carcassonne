from PIL import Image
import requests, os

"""
           2
    ---------------
    |             |
    |             |
  3 |      5      | 1
    |             |
    |             |
    ---------------
           4
"""

CARDS = {
    "basic": {
        "v2": {
            "FFFR_M_XF12345678_N2H": "https://wikicarpedia.com/images/e/e6/Base_Game_C2_Tile_A.jpg",
            "FFFF_M_XF12345678_N4FD": "https://wikicarpedia.com/images/4/47/Base_Game_C2_Tile_B.jpg",
            "CCCC_S_XC1234_N1W": "https://wikicarpedia.com/images/9/9a/Base_Game_C2_Tile_C.jpg",
            "RCRF_XR13_XF14_XF5678_N4FP_start": "https://wikicarpedia.com/images/9/9b/Base_Game_C2_Tile_D.jpg",
            "FCFF_XF145678_N5GFW": "https://wikicarpedia.com/images/8/8d/Base_Game_C2_Tile_E.jpg",
            "CFCF_S_XC13_XF23_XF67_N2W": "https://wikicarpedia.com/images/d/d3/Base_Game_C2_Tile_F.jpg",
            "CFCF_XC13_XF23_XF67_N1": "https://wikicarpedia.com/images/1/1c/Base_Game_C2_Tile_G.jpg",
            "CFCF_XF2367_N3GW": "https://wikicarpedia.com/images/f/fa/Base_Game_C2_Tile_H.jpg",
            "CCFF_XF4567_N2G": "https://wikicarpedia.com/images/7/7d/Base_Game_C2_Tile_I.jpg",
            "RCFR_XR14_XF1456_XF78_N3HFC": "https://wikicarpedia.com/images/8/88/Base_Game_C2_Tile_J.jpg",
            "FCRR_XR34_XF1478_XF56_N3HFD": "https://wikicarpedia.com/images/f/f9/Base_Game_C2_Tile_K.jpg",
            "RCRR_XF14_XF56_XF78_N3": "https://wikicarpedia.com/images/9/90/Base_Game_C2_Tile_L.jpg",
            "CCFF_S_XC12_XF3456_N2G": "https://wikicarpedia.com/images/0/06/Base_Game_C2_Tile_M.jpg",
            "CCFF_XC12_XF3456_N3GW": "https://wikicarpedia.com/images/1/12/Base_Game_C2_Tile_N.jpg",
            "RCCR_S_XC23_XR14_XF16_XF78_N2FC": "https://wikicarpedia.com/images/c/cf/Base_Game_C2_Tile_O.jpg",
            "RCCR_XC23_XR14_XF16_XF78_N3HW": "https://wikicarpedia.com/images/3/31/Base_Game_C2_Tile_P.jpg",
            "CCCF_S_XC123_XF67_N1": "https://wikicarpedia.com/images/8/8b/Base_Game_C2_Tile_Q.jpg",
            "CCCF_XC123_XF67_N3GW": "https://wikicarpedia.com/images/1/14/Base_Game_C2_Tile_R.jpg",
            "CCCR_S_XC123_N2W": "https://wikicarpedia.com/images/d/dd/Base_Game_C2_Tile_S.jpg",
            "CCCR_XC123_N1": "https://wikicarpedia.com/images/0/0a/Base_Game_C2_Tile_T.jpg",
            "FRFR_XR24_XF1278_XF3456_N8GHHFP": "https://wikicarpedia.com/images/c/ca/Base_Game_C2_Tile_U.jpg",
            "FFRR_XR34_XF123478_XF56_N9GHHFPC": "https://wikicarpedia.com/images/f/f2/Base_Game_C2_Tile_V.jpg",
            "RFRR_XF1234_XF56_XF78_N4": "https://wikicarpedia.com/images/5/52/Base_Game_C2_Tile_W.jpg",
            "RRRR_XF12_XF34_XF56_XF78_N1": "https://wikicarpedia.com/images/1/13/Base_Game_C2_Tile_X.jpg"
        }   
    }
}

FEATURES = {
    "garden": "https://wikicarpedia.com/images/5/55/Feature_Garden_C2.png",
    "farmhouse": "https://wikicarpedia.com/images/0/0c/Feature_Farmhouse_C2.png",
    "cowshed": "https://wikicarpedia.com/images/2/22/Feature_Cows_C2.png",
    "watertower": "https://wikicarpedia.com/images/2/23/Feature_WaterTower_C2.png",
    "highwaymen": "https://wikicarpedia.com/images/e/e4/Feature_Highwayman_C2.png",
    "pigsty": "https://wikicarpedia.com/images/2/2c/Feature_Pigsty_C2.png",
    "donkeystable": "https://wikicarpedia.com/images/1/16/Feature_Donkeys_C2.png"
}

TILES_DIR = "tiles"
if not os.path.exists(TILES_DIR):
    os.mkdir(TILES_DIR)

CROP = 0.03  # crop 3% off left, right, top, and bottom

def fetch_image(name, url, c):
    # fetch image
    img_data = requests.get(url).content
    filename = f"{TILES_DIR}/{name}.jpg"
    with open(filename, 'wb') as handler:
        handler.write(img_data)
    img = Image.open(filename)

    # crop image
    width, height = img.size
    left = width * c
    right = width * (1 - c)
    top = height * c
    bottom = height * (1 - c)
    img = img.crop((left, top, right, bottom))

    # save image
    img.save(filename)

names = []
c = "A"
for game_key, game_val in CARDS.items():
    for version_key, version_val in game_val.items():
        for key, img_url in version_val.items():
            name = f"{game_key}_{version_key}_{c}"
            c = chr(ord(c) + 1)
            fetch_image(name, img_url, CROP)
            names.append(name)

# tileimages.js #################################################################
image_file = open(f"{TILES_DIR}/tileimages.js", "w")
for name in names:
    image_file.write(f"import {name}_tile from './{name}.jpg'\n")
image_file.write("\n")

image_file.write("const IMAGE_MAP = {\n")
for name in names:
    image_file.write(f"\t{name}: {name}_tile,\n")
image_file.write("}\n")
image_file.write("\n")

image_file.write("export default IMAGE_MAP\n")
image_file.close()
###############################################################################