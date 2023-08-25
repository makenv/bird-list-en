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

C = oconf.create()
C.ds_name = 'dib10k-200-800-v1'
C.oss_prefix = 'is/pub/datasets/dib-10k'
C.dataset_root = '../datasets'
C.workers = 40


def download(task):
    progress = task['progress']
    task_top = task['task_top']
    task_category = task['task_category']
    meta = task['meta']
    bucket = task['bucket']
    key = task['key']
    c = task['config']
    mode = task['mode']

    dest_dir = os.path.join(c.dataset_root, C.ds_name, mode, meta['realname'])
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    base_fn = os.path.basename(key)
    bucket.get_object_to_file(f'{C.oss_prefix}/{key}', f'{dest_dir}/{base_fn}')
    
    progress.advance(task_category)
    if progress._tasks[task_category].finished:
        task = progress._tasks[task_category]
        progress.remove_task(task_category)
        progress.advance(task_top)
        progress.console.print(f"[red]{time.strftime('%H:%M:%S')} [/red]{meta['realname']} ... {task.total} images")
    if progress._tasks[task_top].finished:
        progress.remove_task(task_top)


def download_worker(Q):
    while True:
        task = Q.get()
        download(task)
        Q.task_done()


def run(bucket, progress, Q, mode):
    with open(f'{C.ds_name}/meta.json') as f:
        metas = json.load(f)
    with open(f'{C.ds_name}/{mode}.json') as f:
        train = json.load(f)
    task_top = progress.add_task(f'{mode.capitalize()} dataset ...', total=len(train), transient=True)

    for c in train.keys():
        items = train[c]
        meta = metas[c]
        task_category = progress.add_task(meta['realname'], total=len(items), transient=True)
        task_base = {
            'mode': mode,
            'progress': progress,
            'task_top': task_top,
            'task_category': task_category,
            'bucket': bucket,
            'config': C,
            'meta': meta,
        }

        for item in items:
            task = dict(task_base)
            task.update(key=item)
            Q.put(task)


def main():
    if len(sys.argv) > 1:
        C.ds_name = sys.argv[1]

    print(oconf.to_yaml(C))
    print('--')


    with open('.private.oss.json') as f:
        C.oss = json.load(f)
    
    auth = oss2.Auth(C.oss['id'], C.oss['key'])
    bucket = oss2.Bucket(auth, C.oss['endpoint'], C.oss['bucket'])

    with Progress(
        TextColumn("[progress.description]{task.description}", justify='left', table_column=Column(ratio=1)),
        BarColumn(bar_width=None, table_column=Column(ratio=4)),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        expand=True, 
        transient=True,
        refresh_per_second=1) as progress:

        Q = queue.Queue(20)
    
        for i in range(C.workers):
            t = threading.Thread(target=download_worker, args=(Q,))
            t.daemon = True
            t.start()
    
        bs = time.time()
        run(bucket, progress, Q, 'train')
        run(bucket, progress, Q, 'val')
        Q.join()

    progress.stop()
    ts = time.time()
    print(f'{ts - bs:.2f}s')


if __name__ == '__main__':
    main()



