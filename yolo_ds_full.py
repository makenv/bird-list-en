import os
import sys
import json
import csv
from ruamel import yaml

VAL_RATE = 0.1
OUT_DIR = 'dib10k-full-v1'
P1 = 400
V1 = 0.1
P2 = 2000
V2 = 0.05


def load_dib_meta():
    R = {}
    with open("class.json") as f:
        R["class"] = json.load(f)

    with open("dir.json") as f:
        R["dir"] = json.load(f)
    return R


def main():
    # -- load dib meta
    dib_meta = load_dib_meta()
    dib_meta["name"] = { v["name"]:k for (k, v) in dib_meta["class"].items()}
    
    name_dict = dib_meta['name']
    dir_dict = dib_meta['dir']
    class_dict = dib_meta['class']

    
    os.makedirs(OUT_DIR, exist_ok=True)

    # -- 
    train_ds = {}
    val_ds = {}
    meta_info = {}
    
    for bid in class_dict:
        c0 = class_dict[bid]['name']
        files = dir_dict[bid]
        file_num = len(files)
        if file_num < 50:
            print(f'{c0} ... {file_num} images, skipped')
            continue
        files = [ f"{bid}.{c0}/{bid}.{c0.replace(' ', '_')}_{x}.jpg" for x in files]

        if file_num >= P2:
            val_num = int(P2 * V2)
            test_num = P2 - val_num
        elif file_num <= P1:
            val_num = int(file_num * V1)
            test_num = file_num - val_num
        else:
            v = ((file_num - P1) * V1 + (P2 - file_num) * V2) / (P2 - P1)
            val_num = int(file_num * v)
            test_num = file_num - val_num

        train_files = files[:test_num]
        val_files = files[test_num:test_num + val_num]
        train_ds[c0] = train_files
        val_ds[c0] = val_files

        meta_info[c0] = {
            'originname': c0,
            'realname': c0,
            'id': bid,
            'file_num': file_num,
            'train': test_num,
            'valid': val_num,
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
