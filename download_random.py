# b4 i knew it the dream was all gOne
import urllib.request
import argparse
import uuid
import random
from tqdm import tqdm
import os


def download_random_image(width: int, height: int):
    urllib.request.urlretrieve(
        (f"https://picsum.photos/{width}/{height}?random"),
        (f"random_img/stock-image-{uuid.uuid4()}.jpg"),
    )


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "--num", type=int, default=100, help="how many pics to download yea"
    )
    args.add_argument("--min", type=int, default=500, help="minimum size")
    args.add_argument("--max", type=int, default=1000, help="maximum size")
    opt = args.parse_args()
    print(f"downloading {opt.num} images:\nmin width: {opt.min}\nmax width: {opt.max}")
    if not os.path.exists("random_img"):
        os.makedirs("random_img")
    for i in tqdm(range(opt.num)):
        download_random_image(
            random.randrange(opt.min, opt.max), random.randrange(opt.min, opt.max)
        )
