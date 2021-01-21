#!/usr/bin/python3
import os, sys
import struct

folder = sys.argv[1]
url = sys.argv[2]
if len(sys.argv) > 3: num = int(sys.argv[3])
else: num = 0

if not os.path.isdir(folder): os.mkdir(folder)
with open(folder + '/conf','wb') as f:
    f.write(struct.pack('>I',num))
    f.write(bytes(url,'utf8'))
