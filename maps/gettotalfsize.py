import mapsdatas
import sys, glob
import math

def formatsize(inte):
    units = ('B', 'kB', 'MB', 'GB')
    divider = int(math.log(inte, 1024))
    ret = inte / 1024 ** divider
    return '{:.2f} {}'.format(ret, units[divider])

fs=[]
for la in glob.glob('data/*.dat'):
    with open(la, 'rb') as f:
        d = mapsdatas.mapdata.parsefromdatafile(f)
    fs.append((d.name,d.fsize))
fs.sort(key=lambda x: x[1])
print(dict((a[0],formatsize(a[1])) for a in fs))
print(formatsize(sum(a[1] for a in fs)))
