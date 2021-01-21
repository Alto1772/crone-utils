import mapsdatas
import os, sys
import json

def main():
    mapper = os.listdir('caches')[-1]
    with open('caches/'+mapper) as f: 
        ffjj = json.load(f)
    fw = mapsdatas.mapdata.parsefromjson(ffjj[int(sys.argv[1])])
    print(fw.__dict__)
main()
