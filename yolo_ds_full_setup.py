import os
import sys

import json
import time

import threading
import queue

import oss2

from omegaconf import OmegaConf as oconf

from rich.progress import track
from rich.progress import Progress
from rich.progress import TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.progress import MofNCompleteColumn, Column

HOME = os.environ.get('HOME')
C = oconf.create()
C.ds_name = 'dib10k-full-v1'
C.source = f'{HOME}/work/cs/datasets/.dib-10k'
C.dataset_root = '../datasets'
C.workers = 40


def setup_one_class(task):
    progress = task['progress']
    task_top = task['task_top']
    meta = task['meta']
    c = task['config']
    mode = task['mode']
    fns = task['files']

    dest_dir = os.path.join(c.dataset_root, c.ds_name, mode, meta['realname'])
    os.makedirs(dest_dir, exist_ok=True)
    task_link = progress.add_task(meta['realname'], total=len(fns))
    for fn in fns:
        base_fn = os.path.basename(fn)
        try:
            os.link(f'{c.source}/{fn}', f'{dest_dir}/{base_fn}')
        except:
            pass
        progress.update(task_link, advance=1)
    progress.remove_task(task_link)
    progress.update(task_top, advance=1)


def run(progress, mode):
    with open(f'{C.ds_name}/{mode}.json') as f:
        fns = json.load(f)

    task_top = progress.add_task(f'{mode.capitalize()} dataset ...', total=len(fns), transient=True)


    for c in fns.keys():
        files = fns[c]
        meta = {'realname': c}
        task = {
            'mode': mode,
            'progress': progress,
            'task_top': task_top,
            'meta': meta,
            'files': files,
            'config': C,
        }
        setup_one_class(task)

    progress.remove_task(task_top)

def main():
    if len(sys.argv) > 1:
        C.ds_name = sys.argv[1]

    with Progress(
        TextColumn("[progress.description]{task.description}", justify='left', table_column=Column(ratio=1)),
        BarColumn(bar_width=None, table_column=Column(ratio=4)),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        expand=True, 
        transient=True,
        refresh_per_second=1) as progress:

        run(progress, 'train')
        run(progress, 'val')

if __name__ == '__main__':
    main()
