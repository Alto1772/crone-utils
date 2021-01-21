#!/usr/bin/python3
import os, sys

def get_current_num(directory, file):
    num = int.from_bytes(file.read(4),'big')
    file.seek(0)
    os.chdir(directory)
    retries = 0
    while True: 
        if os.path.isfile(f'{num}.dat'):
            num += 1
            retries = 0
        elif os.path.isfile(f'{num}.err'):
            print(f'Detected {num}.err')
            num += 1
            retries = 0
        else:
            if retries == 0: realnum = num
            retries += 1
            num += 1
            if retries == 10:
                num = realnum
                break
            else: print(f'{num-1} not found. {retries} retries left.')
    print(f'{num} is missing, writing current num into conf.')
    file.write(num.to_bytes(4,'big'))

folder = sys.argv[1]

if len(sys.argv) == 2:
    a = os.path.isdir(folder)
    if a:
        with open(f'{folder}/conf','r+b') as f: get_current_num(folder, f)
    exit(not a)
if len(sys.argv) > 2: fol = sys.argv[2]
else: fol = folder

if len(sys.argv) > 3: num = int(sys.argv[3])
else: num = 0

if not os.path.isdir(folder): os.mkdir(folder)
with open(folder + '/conf','wb') as f:
    f.write(num.to_bytes(4,'big'))
    f.write(bytes(fol,'utf8'))
