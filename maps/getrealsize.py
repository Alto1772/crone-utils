#!/usr/bin/python3
import mapsdatas
import requests
import os, glob

def main():
    os.chdir('data')
    dirs = glob.glob('*.dat')
    sess = requests.Session()

    for y in dirs:
        with open(y,'rb') as f:
            i = mapsdatas.mapdata.parsefromdatafile(f)
        if type(i.fsize) is not str: continue

        print(i.dl_url)
        try: results = sess.head(mapsdatas.datafile_site + i.dl_url)
        except requests.exceptions.ConnectionError as px:
            print(px);print()
            continue

        if not results.ok:
            print(f'Error at {y}:')
            print(f'Status: {results.status_code}')
            print('Text:')
            print(results.text)
            continue # break

        newlen = int(results.headers['content-length'])
        print(f'{y}: {newlen} bytes')
        i.fsize = newlen
        #print(dict(i))

        with open(y,'wb') as f:
            i.writetofile(f)
main()
