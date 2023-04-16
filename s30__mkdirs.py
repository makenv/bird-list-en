import csv
import os

SOURCE_FN = 'v10_0.csv'
DRY = True
# kid, ksn, kcn, ken
# id, sn, cn, en
DIR_PATTERN = '{kcn}__{ken}/{cn}__{en}'
DIR_PATTERN = '{kcn}/{cn}'

def main():
    cur_family = {}
    with open(SOURCE_FN) as fi:
        ci = csv.reader(fi)
        data = [i for i in ci]
    
    res = []
    for row in data:
        if row[4] == '':
            cur_family = {
                'kid': row[0],
                'ksn': row[1],
                'kcn': row[2],
                'ken': row[3].partition(' (')[0]
            }
            continue
        
        species = dict(cur_family)
        species.update({
            'id': row[0],
            'sn': row[1].replace(' ', '_'),
            'cn': row[2].replace(' ', '_'),
            'en': row[3].replace(' ', '_'),
            'iucn': row[4],
            'level': row[5],
        })
        if DRY:
            print('mkdir -p ' + DIR_PATTERN.format(**species))


if __name__ == '__main__':
    main()
