import csv

import xlrd

SOURCE_FN = '中国观鸟年报-中国鸟类名录_v10.0.xls'
DEST_FN = 'v10_0.csv'
SKIP_ROW = 8
NCOLS = 7


def main():
    workbook = xlrd.open_workbook(SOURCE_FN, formatting_info=True)
    sheet = workbook.sheet_by_index(0)
    data = []
    for row in range(SKIP_ROW + 1, sheet.nrows):
        row_data = [sheet.cell_value(row, col) for col in range(NCOLS) ]
        if row_data[0] == '' or row_data[0] == None:
            break
        row_data[0] = f'{int(row_data[0])}'
        print(row_data[0])
        data.append(row_data)

    
    with open(DEST_FN, 'w') as fo:
        cout = csv.writer(fo)
        cout.writerows(data)

if __name__ == '__main__':
    main()