import os
import sys
import json
import csv
from ruamel import yaml

CATEGORY_FILE = "category-0.csv"
MAX_IMAGES = 200
VAL_RATE = 0.1
OUT_DIR = 'dib10k-200-200-v1'


NAME_MAP_0 = {
    "Common Magpie": "Eurasian Magpie",
    "Common Hoopoe": "Eurasian Hoopoe",
    "Japanese White-eye": "Warbling White-eye",
    "Chinese Spot-billed Duck": "Eastern Spot-billed Duck",
    "Great Bittern": "Eurasian Bittern",
    "Lammergeier": "Bearded Vulture",
    "Mongolian Gull": "Vega Gull",
    "Fork-tailed Swift": "Pacific Swift",
    "Common Raven": "Northern Raven",
    "Chinese Hill Babbler": "Beijing Babbler",
    "Orange-flanked Bluetail": "Red-flanked Bluetail",
    "Oriental Magpie Robin": "Oriental Magpie-Robin",
    "White-capped Water Redstart": "White-capped Redstart",
    "Pallas's Bunting": "Pallas's Reed Bunting",
    "Reed Bunting": "Common Reed Bunting",
}


def load_dib_meta():
    R = {}
    with open("class.json") as f:
        R["class"] = json.load(f)

    with open("dir.json") as f:
        R["dir"] = json.load(f)
    return R


def main():
    # -- load input categories
    with open(CATEGORY_FILE) as f:
        categories = f.readlines()
    categories = [ c.strip() for c in categories ]

    # -- load dib meta
    dib_meta = load_dib_meta()
    dib_meta["name"] = { v["name"]:k for (k, v) in dib_meta["class"].items()}
    
    name_dict = dib_meta['name']
    dir_dict = dib_meta['dir']

    
    invalided = 0
    for c in categories:
        c0 = c
        if c in NAME_MAP_0:
            c0 = NAME_MAP_0[c]
        if c0 not in name_dict:
            print(f'{c}:{c0}')
            invalided += 1
            continue
        # key = name_dict[c0]
        # print(f'{c} / {c0} / {len(dir_dict[key])}')
    
    if invalided != 0:
        sys.exit(0)

    os.makedirs(OUT_DIR, exist_ok=True)

    train_ds = {}
    val_ds = {}
    meta_info = {}
    
    for c in categories:
        c0 = NAME_MAP_0.get(c, c)
        bid = name_dict[c0]
        files = dir_dict[bid]
        images = len(files)
        if len(files) >= MAX_IMAGES:
            files = files[:MAX_IMAGES]
        files = [ f"{bid}.{c0}/{bid}.{c0.replace(' ', '_')}_{x}.jpg" for x in files]

        sp = int(len(files) * (1 - VAL_RATE))

        
        train_ds[c] = files[:sp]
        val_ds[c] = files[sp:]
        meta_info[c] = {
            'originname': c,
            'realname': c0,
            'id': bid,
            'images': images,
            'train': len(train_ds[c]),
            'valid': len(val_ds[c]),
        }

    save(f'{OUT_DIR}/train.json', train_ds)
    save(f'{OUT_DIR}/val.json', val_ds)
    save(f'{OUT_DIR}/meta.json', meta_info)

def save(fn, data):
    with open(fn, 'w') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    with open(fn.replace('.json', '.yaml'), 'w') as f:
        yaml.dump(data, f)

if __name__ == "__main__":
    main()
