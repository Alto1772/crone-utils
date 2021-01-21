#!/usr/bin/python3
import struct
import zlib
import sys

debug = False

def printvalue(name, value):
    print(f'{name} = {value!r}')

def decompress(file):
    '''                                                                              id        = int [I]
    likes     = int [I]
    downloads = int [I]                                                              views     = int [I]
                                                                                     comment = compressed string (length as short [H])                                author  = compressed string (length as short [H])                                date    = string (YYYY-MM-DD)
    hash    = compressed string (length as short [H])                                                                                                                 AA AA AA AA BB BB BB BB CC CC CC CC DD DD DD DD
    EE EE FF FF GG GG GG GG GG GG GG GG GG GG HH HH ...                              '''
    headers = struct.unpack('>4IHH10sH', f.read(0x20))

    comment = f.read(headers[4])
    author = f.read(headers[5])
    hash = f.read(headers[7])

    if debug:
        printvalue('id', headers[0])
        printvalue('likes', headers[1])
        printvalue('downloads', headers[2])
        printvalue('views', headers[3])
        printvalue('comment (len)', headers[4])
        printvalue('comment (cz)', comment)
        printvalue('author (len)', headers[5])
        printvalue('author (cz)', author)
        printvalue('date', headers[6])
        printvalue('hash (len)', headers[7])
        printvalue('hash (cz)', hash)

    if headers[4]: comm_dz = zlib.decompress(comment).decode('utf8')
    else: comm_dz = None
    if headers[5]: auth_dz = zlib.decompress(author).decode('utf8')
    else: auth_dz = None
    if headers[7]: hash_dz = zlib.decompress(hash).decode('ascii')
    else: hash_dz = None

    return {
        'id': headers[0],
        'likes': headers[1],
        'downloads': headers[2],
        'views': headers[3],
        'comment': comm_dz,
        'author': auth_dz,
        'date': headers[6].decode('ascii'),
        'hash': hash_dz
    }


if sys.argv[1] == '-d':
    debug = True
    sys.argv.pop(1)
with open(sys.argv[1],'rb') as f:
    print(decompress(f))
