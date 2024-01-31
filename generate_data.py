import os
import numpy as np
from PIL import Image, ImageDraw
import random
import argparse
import uuid
from tqdm import tqdm
import json
from annotations import LabelMe

"""
generates synthetic training data by pasting card images over 
random ass backgrounds
"""


def create_lableme_label(xyxy: list, label: str, fname: str, dims: tuple):
    """
    creates a labelme file ayylmao
    """
    w, h = dims
    _labelme = LabelMe(w, h, fname)
    _labelme.add_label(label, xyxy, "rectangle")

    return _labelme


def random_resize_and_overlay_with_positions(
    background_path: str, overlay_path: str, output_path: str
) -> list:
    # Open the background image
    background = Image.open(background_path).convert("RGBA")

    # Open the overlay image
    overlay = Image.open(overlay_path).convert("RGBA")

    # Randomly resize the overlay image
    new_size = random.randint(int(overlay.width / 2), int(overlay.width / 2))
    overlay = overlay.resize((int(overlay.width / 3), int(overlay.height / 3)))

    # Randomly position the overlay on the background
    top_left_position = (
        random.randint(0, background.width - overlay.width),
        random.randint(0, background.height - overlay.height),
    )
    bottom_right_position = (
        top_left_position[0] + overlay.width,
        top_left_position[1] + overlay.height,
    )

    # Overlay the resized image onto the background
    background.paste(overlay, top_left_position, overlay)
    background.save(output_path)

    # Return the top-left and bottom-right positions
    return [top_left_position, bottom_right_position]


def generate_name(filename: str, keep_ext: bool = True) -> str:
    """
    creates a unique name given a filename (with no directores)
    example:
        penis.png -> penis-*uuid*.png
    """
    _filename = os.path.splitext(filename)
    if keep_ext:
        return f"{_filename[0]}{uuid.uuid4()}{_filename[1]}"
    else:
        return f"{_filename[0]}{uuid.uuid4()}"


def get_all_images(img_folder: str):
    return [x for x in os.listdir(img_folder) if x.endswith((".jpg", ".png", ".jpeg"))]


if __name__ == "__main__":
    GENERATED_DATA_FOLDER = "generated_data"
    args = argparse.ArgumentParser()
    args.add_argument("--source", type=str, help="source image path")
    args.add_argument(
        "--numgen", type=int, default=10, help="number of images to generate per image"
    )
    args.add_argument(
        "--randfolder", type=str, default="random_img", help="random images path"
    )
    args.add_argument(
        "--target",
        type=str,
        default="labelme",
        help="target format ; can be `labelme` or `yolo`",
    )
    opt = args.parse_args()

    # create export foler
    if not os.path.exists(GENERATED_DATA_FOLDER):
        os.makedirs(GENERATED_DATA_FOLDER)

    ALL_IMAGES = get_all_images(opt.source)
    BG_IMAGES = get_all_images(opt.randfolder)
    for image in tqdm(ALL_IMAGES):
        full_image_path = os.path.join(opt.source, image)
        class_name = os.path.splitext(image)[0]
        print(class_name)
        for _time in range(opt.numgen):
            _new_fname = generate_name(image)
            bg_image = os.path.join(
                opt.randfolder, BG_IMAGES[random.randrange(0, len(BG_IMAGES))]
            )
            output_path = os.path.join(GENERATED_DATA_FOLDER, _new_fname)
            _img_xyxy = random_resize_and_overlay_with_positions(
                bg_image, full_image_path, output_path
            )
            im0 = Image.open(bg_image)
            _lblm = create_lableme_label(
                list(_img_xyxy), class_name, _new_fname, (im0.width, im0.height)
            )
            json_file = os.path.splitext(_new_fname)[0] + ".json"
            _json = json.dumps(_lblm.to_dict(), indent=2)
            with open(os.path.join(GENERATED_DATA_FOLDER, json_file), "w") as writejson:
                writejson.write(_json)
