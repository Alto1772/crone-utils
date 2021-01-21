#!/usr/bin/python
import mapsdatas
import os, json
import glob

def main():
    files = glob.glob('caches/*.json')
    files.sort(key=lambda x: os.path.getmtime(x))
    with open(files[-1]) as f: 
        ffjj = [mapsdatas.mapdata.parsefromjson(a) for a in json.load(f)]
    os.chdir('data')

    for l in ffjj:
        fil = f'{l.id}.dat'
        if not os.path.isfile(fil):
            print(f'{fil}: Not found! Ignored...\n')
            continue

        with open(fil,'rb') as f:
            d = mapsdatas.mapdata.parsefromdatafile(f)
        loist = dict((fd, l[fd] != d[fd]) for fd in l if fd != 'fsize')
        if any(loist.values()): 
            print(f'[{fil}] {l.name!r} differs.')
            for iw in loist.keys():
                if l[iw] != d[iw]:
                    print('[{}] {!r} - {!r}'.format(iw,l[iw],d[iw]))
            print()

main()
