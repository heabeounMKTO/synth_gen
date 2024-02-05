import os
import numpy as np
from PIL import Image, ImageDraw
import random
import argparse
import uuid
from tqdm import tqdm
import json
from annotations import LabelMe
from generate_data import random_resize_and_overlay_with_positions, generate_name,create_lableme_label, get_all_images
import cv2


def generate_data_from_labelme(times: int, all_classes: list):
    cut_folder = os.path.join(opt.source, "cut_export")
    for class_folder in tqdm(all_classes):
        cpath = os.path.join(cut_folder, class_folder)
        all_images = get_all_images(cpath)
        for image in all_images:
            for _time in range(times):
                _new_fname = generate_name(image)
                _new_fname = os.path.splitext(_new_fname)[0] + ".png"
                output_path = os.path.join(GENERATED_DATA_FOLDER, _new_fname)

                bg_image = os.path.join(opt.randfolder, BG_IMAGES[random.randrange(0, len(BG_IMAGES))])
                img_path = os.path.join(cpath, image)
                _img_xyxy = random_resize_and_overlay_with_positions(bg_image, img_path, output_path)
                im0 = Image.open(bg_image)
                _lblm = create_lableme_label(list(_img_xyxy), class_folder, _new_fname, (im0.width,im0.height))
                json_file = os.path.splitext(_new_fname)[0] + ".json"
                _json = json.dumps(_lblm.to_dict(), indent=2)
                with open(os.path.join(GENERATED_DATA_FOLDER,json_file), "w") as writejson:
                    writejson.write(_json)
                

def cut_images(json_file_path: str):
    jsonfile = json.load(open(json_file_path))
    _img = cv2.imread(os.path.join(opt.source, jsonfile["imagePath"]))
    for label in jsonfile["shapes"]:
        # get image
        _img0 = _img.copy()
        pos = label["points"]
        crop_img = _img0[int(pos[0][1]):int(pos[1][1]),int(pos[0][0]):int(pos[1][0])]
        # crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
        export_folder = os.path.join(opt.source, "cut_export")
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
        output_path = os.path.join(export_folder, label["label"]) + f"/{uuid.uuid4()}.jpg"
        cv2.imwrite(output_path, crop_img)


def get_all_classes():
    label_list = []
    for file in os.listdir(opt.source):
        if file.endswith(".json"):
            openjson = json.load(open(os.path.join(opt.source, file)))
            for label in openjson["shapes"]:
                label_list.append(label["label"])
    return sorted(set(label_list))

def make_label_class_folder(label_list):
    for label_class in label_list:
        label_cut = os.path.join(opt.source, "cut_export")
        label_fol = os.path.join(label_cut, label_class)
        if not os.path.exists(label_fol):
            os.makedirs(label_fol)


if __name__ == "__main__":
    
    args = argparse.ArgumentParser()
    args.add_argument("--source", type=str, help="source labels folder")
    args.add_argument("--randfolder", default="random_img",type=str, help="random images folder")
    args.add_argument("--numgen", type=int, default=10, help="number of images to generate per image")
    args.add_argument("--cut",  action='store_true', help="crop images")
    args.add_argument("--gen",  action='store_true', help="generate")
    opt = args.parse_args()
    
    GENERATED_DATA_FOLDER = "generated_data"
    ALL_CLASSES = get_all_classes()
    ALL_JSON = [os.path.join(opt.source, x) for x in os.listdir(opt.source) if x.endswith(".json")]
    
    # create export foler
    if not os.path.exists(GENERATED_DATA_FOLDER):
        os.makedirs(GENERATED_DATA_FOLDER)
    
    BG_IMAGES = get_all_images(opt.randfolder)
    make_label_class_folder(ALL_CLASSES)
    if opt.cut:
        [cut_images(x) for x in tqdm(ALL_JSON)]
    if opt.gen:
        generate_data_from_labelme(opt.numgen, ALL_CLASSES)
