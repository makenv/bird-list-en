import os
import sys
import json
import csv
from ruamel import yaml


MAX_CLASSES = 12000
DS_NAME = 'dib10k-200-200-v1'


def load_dib_meta():
    R = {}
    with open("class.json") as f:
        R["class"] = json.load(f)
    return R


def main():
    # -- load dib meta
    dib_meta = load_dib_meta()
    dib_meta["name"] = { v["name"]:k for (k, v) in dib_meta["class"].items()}
    

    names = {}
    for i in range(MAX_CLASSES):
        name = dib_meta["class"].get(str(i), None)
        if name == None:
            names[i] = f'n{i}'
        else:
            names[i] = name['name']

    C = {
        'path': f'../datasets/{DS_NAME}',
        'train': 'train',
        'test': 'test',
        'names': names,
    }

    with open(f'{DS_NAME}.yaml', 'w') as f:
        yaml.dump(C, f)


if __name__ == '__main__':
    main()
