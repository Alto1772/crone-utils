import struct

def readconf():
    with open('conf','rb') as f:
        return struct.unpack('>I',f.read(4))[0], f.read().decode('utf8')

def writeconf(currnum, url):
    with open('conf','wb') as f:
        f.write(struct.pack('>I',currnum))
        f.write(bytes(url,'utf8'))

