#!/usr/bin/python3
import sys, os

def write_existing(num):
    retries = 0
    with open('missing','r+') as f:
        off = 0
        while ai := f.readline():
            if int(ai[:-5]) >= num:
                break
            off += len(ai)
        f.seek(off)
        f.truncate()
        while retries != 10:
            if os.path.isfile(f'{num}.dat'):
                retries = 0
            else:
                print(f'{num}.dat is missing!')
                f.write(f'{num}.dat\n')
                retries += 1
            num += 1

def write_new(num):
    retries = 0
    with open('missing','w') as f:
        while retries != 10:
            if os.path.isfile(f'{num}.dat'):
                retries = 0
            else:
                print(f'{num}.dat is missing!')
                f.write(f'{num}.dat\n')
                retries += 1
            num += 1

dir = sys.argv[1]
os.chdir(dir)
with open('conf','rb') as f:
    num = int.from_bytes(f.read(4),'big')
if os.path.isfile('missing'): write_existing(num)
else: write_new(num)
