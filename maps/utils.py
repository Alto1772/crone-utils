from datetime import datetime
import urllib.parse
import struct
import zlib

debug = not True
def dprintf(fmt, *args):
    if debug: print(f'>) {fmt}' % args)
def debugprint(v1, v2):
    dprintf('[%s] %s', v1, v2)
def byteread(byt):
    d=[]
    for i in byt:
        d.append('%02x'%i)
    return ' '.join(d)

class BaseUtils():
    def __init__(self):
        self.__dict__['content'] = {}
        self.__dict__['attrs'] = {}
    def __call__(self):
        return self.__dict__['content']

    def __getitem__(self, key):
        return self.__dict__['content'][key]
    def __setitem__(self, key, val):
        self.__dict__['content'][key] = val
    def __len__(self):
        return len(self.__dict__['content'])

    def __getattr__(self, key):
        return self.__dict__['attrs'][key]
    def __setattr__(self, key, val):
        self.__dict__['attrs'][key] = val

class FileBaseUtils(BaseUtils):
    def __init__(self, file, encoding='utf8', bigendian=True):
        super().__init__()
        self.file = file
        self.encoding = encoding
        self.bigendian = bigendian

def exportedfunc(s, f):
    pass

class ParseJsonUtils(BaseUtils):
    def nothing(s,k,v): pass
    def baseput(s,k,v):
        s[k] = v; debugprint('baseput', f'{k!r} = {v!r}')
    def tointput(s,k,v):
        s.baseput(k, int(v))
    def authorput(s,k,v):
        s.baseput('author', None if v == "Unknown" else v)
    def descput(s,k,v):
        s.baseput('description', v.replace('\r\n','\n'))
    def urlput(s,k,v):
        s.baseput('dl_url', urllib.parse.urlparse(v).path)
    def dateput(s,k,v):
        s.baseput('date', datetime.strptime(v, '%Y-%m-%d %H:%M:%S'))
    def filesizeput(s,k,v):
        s.baseput('fsize',v)
    def isallowedput(s,k,v):
        s.baseput('is_allowed',bool(int(v)))
    def verput(s,k,v):
        s.baseput('for_versions', v if v else None)
    def imgurlput(s,k,v):
        debugprint('imgurlput', repr(v))
        if not v: return
        s['previews'].append(urllib.parse.urlparse(v).path)

    def __init__(self):
        super().__init__()
        self.exportedfuncs = (
            self.nothing,
            self.baseput,
            self.tointput,
            self.authorput,
            self.descput,
            self.urlput,
            self.dateput,
            self.filesizeput,
            self.isallowedput,
            self.verput,
            self.imgurlput,
        )

class ParseDataFileUtils(FileBaseUtils):
    def readpack(self, struc):
        bstruc = ('>' if self.bigendian else '<') + struc
        size = struct.calcsize(struc)
        by = self.file.read(size)
        l = struct.unpack(bstruc, by)
        debugprint('readpack', f'({struc}) - {size} = {byteread(by)} {l}')
        return l
    def readsingle(self, lem):
        bint = 'big' if self.bigendian else 'little'
        by = self.file.read(lem)
        l = int.from_bytes(by, bint)
        debugprint('readsingle', f'{lem} = {byteread(by)} ({l})')
        return l
    def readstring(self, byteleng=4):
        length = self.readsingle(byteleng)
        if not length: return None
        by = self.file.read(length)
        l = by.decode(self.encoding)
        debugprint('readstring', f'({byteleng}) - {length} = {byteread(by)} ({l!r})')
        return l

    def baseput(self, key, val):
        self[key] = val
    def putreadpack(self, struc, *keys):
        lekeys = self.readpack(struc)
        if len(lekeys) != len(keys):
            raise ValueError('calculated pack size too much/not enough for key args')
        self().update(zip(keys, lekeys))
    def putreadsingle(self, key, lem):
        self.baseput(key, self.readsingle(lem))
    def putreadstring(self, key, byteleng=4):
        self.baseput(key, self.readstring(byteleng))
    def putstrdecompress(self, key, byteleng=4, **kwargs):
        length = self.readsingle(byteleng)
        by = self.file.read(length)
        zby = zlib.decompress(by, **kwargs)
        debugprint('putstrdecompress', f'({byteleng}) - {length} = zby({byteread(by)!r}) = {byteread(zby)!r}')
        self.baseput(key, zby.decode(self.encoding))

class WriteToFileUtils(FileBaseUtils):
    def writesingle(self, num, length):
        bint = 'big' if self.bigendian else 'little'
        by = num.to_bytes(length, bint)
        debugprint('writesingle', f'{num}, {length} = {byteread(by)}')
        self.file.write(by)
    def writepack(self, struc, *vals):
        bstruc = ('>' if self.bigendian else '<') + struc
        pack = struct.pack(bstruc, *vals)
        debugprint('writepack', f'{struc!r}, {vals} = {byteread(pack)}')
        self.file.write(pack)
    def writestring(self, strin, length=4):
        if strin is None: self.writesingle(0, length)
        else:
            by = bytes(strin, self.encoding)
            lem = len(by)
            self.writesingle(lem, length)
            debugprint('writestring', f'{strin!r} ({lem}) = {byteread(by)}')
            self.file.write(by)
    def writestringcompress(self, strin, lem=4, **kwargs):
        by = bytes(strin, self.encoding)
        cby = zlib.compress(by, **kwargs)
        length = len(cby)
        self.writesingle(length, lem)
        self.file.write(cby)
