#!/usr/bin/python
import mapsdatas
import os, json

def main():
    files = list(filter(lambda x: x.endswith('.json'), os.listdir('caches')))
    files.sort(key=lambda x: os.path.getmtime('caches/'+x))
    with open('caches/'+files[-1]) as f: 
        ffjj = [mapsdatas.mapdata.parsefromjson(a) for a in json.load(f)]
    if not os.path.exists('data'): os.mkdir('data')
    os.chdir('data')
    def printchange(text, key):
        if d[key] == l[key]: return
        print(f'{text:>10}: {l[key]:<8} (+{l[key]-d[key]})')
    for l in ffjj:
        fil = f'{l.id}.dat'
        if not os.path.isfile(fil):
            print(f'{fil}: Not found! Creating...\n')
            with open(fil,'wb') as f:
                l.writetofile(f)
            continue

        with open(fil,'rb') as f:
            d = mapsdatas.mapdata.parsefromdatafile(f)

        if any(map(lambda x: l[x] != d[x], ('downloads','views','likes','dislike'))):
            print(fil+':')
            printchange('Downloads', 'downloads')
            printchange('View Count', 'views')
            printchange('Likes', 'likes')
            printchange('Dislikes', 'dislike')
            print()

        d.updatecounts(l)
        with open(fil,'wb') as f:
            d.writetofile(f)

main()
