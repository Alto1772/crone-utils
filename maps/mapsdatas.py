from datetime import datetime
import urllib.parse
import struct
import zlib

import utils

datafile_version = (0, 1)
datafile_header = b'CRONEMAP'
datafile_site = 'https://www.worldofskins.org'

class MapParseError(Exception):
    pass

class DataVersionError(MapParseError):
    def __init__(self, tup):
        self.datversion = tup
        self.curversion = datafile_version
        self.args = (f"Version mismatch: {verpars(tup)}, (Current Version: {verpars(datafile_version)})",)

    @staticmethod
    def verpars(ver):
        return "v%d.%d" % ver

class NotMapFileError(MapParseError):
    def __init__(self, file):
        self.args = (f"{file.name!r} is not a map file!",)

class mapdata():
    'mapdata Class'

    def __init__(self, data):
        self.__dict__['content'] = data
    def __getitem__(self, key):
        return self.__dict__['content'][key]
    def __setitem__(self, key, val):
        self.__dict__['content'][key] = val
    def __getattr__(self, key):
        try: return self.__dict__['content'][key]
        except KeyError: return getattr(self.__dict__['content'],key)
    def __setattr__(self, key, val):
        self.__dict__['content'][key] = val
    def __iter__(self):
        return iter(self.__dict__['content'])

    @staticmethod
    def parsefromjson(jjj):
        '''
        Parse map info from the server

        Structure from json:
        id            - order id
        user_id       - ??? [always be 0] (ignored)
        author        - author of map [Unknown if unspecified]
        name          - name of the map
        category      - map category
        descr         - description (uses CR+LF as line terminator)
        urldownload   - download url
        dates         - date of published (%Y-%m-%d %H:%M:%S)
        filesize      - File Size in SI Unit prefix
        views         - view count after user clicks an item
        downloads     - download count after user clicks download
        likes         - like count
        dislike       - dislike count
        hash          - ??? ["no_hash" or null] (ignored)
        allowed       - ??? [must be 1 or 0]
        versions      - mcpe version depend (cannot be split)
        preview{0..9} - image preview url
        '''
 
        jsonstructure = ("id", "user_id", "author", "name", "category", "descr", "urldownload", "dates", "filesize", "views", "downloads", "likes", "dislike", "hash", "allowed", "versions", "preview0", "preview1", "preview2", "preview3"
, "preview4", "preview5", "preview6", "preview7", "preview8", "preview9")
        objstructure = (2, 0, 3, 1, 1, 4, 5, 6, 7, 2, 2, 2, 2, 0, 8, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10)

        fclass = utils.ParseJsonUtils() 
        fclass.baseput('previews',[])
        for jstruct, ostruct in zip(jsonstructure, objstructure):
            fclass.exportedfuncs[ostruct](jstruct, jjj[jstruct])
        return mapdata(fclass())

    def __repr__(self):
        return f"[mapdata <{self.id}> ({self.name!r})]"

    @staticmethod
    def parsefromdatafile(file):
        '''
        Parse data from file

        See "writetofile" for structure.
        '''

        putil = utils.ParseDataFileUtils(file)

        if putil.file.read(8) != datafile_header:
            raise NotMapFileError(file)
        vers = putil.readpack('BB')
        if vers != datafile_version:
            raise MapVersionError(vers)

        putil.putreadpack('H?','id','is_allowed')
        previewcount = putil.readsingle(1)
        putil.baseput('date', datetime.fromtimestamp(putil.readsingle(4)))
        putil.putreadpack('IIII','downloads','views','likes','dislike')

        putil.putreadstring('name', 2)
        putil.putreadstring('category', 1)
        putil.putreadstring('author', 1)
        putil.putstrdecompress('description', 2)

        putil.putreadstring('dl_url')
        if not putil.readsingle(1):
            putil.putreadstring('fsize', 1)
        else:
            putil.putreadsingle('fsize', 4)

        putil.baseput('previews', [])
        putil.putreadstring('for_versions', 1)
        for i in range(previewcount):
            putil['previews'].append(putil.readstring(2))

        return mapdata(putil())

    def writetofile(self, file):
        '''
        Write to file as bytes

        Structure to datafile:
          - Header name "CRONEMAP" (8 bytes)
          - Version Number (eg. 01 00 for v1.0) (2 bytes)
          - "Order" ID (2 bytes)
          - is_allowed (1 byte)
          - Count of images (1 byte)
          - Date uploaded (4 bytes)
          - Download count (4 bytes)
          - View count (4 bytes)
          - Like count (4 bytes)
          - Dislike count (4 bytes)
          - Map name (string)
          - Category name (string)
          - Author name (string)
          - Map description (compressed string)
          - Map Download URL (string)
          - If is real file size? (1 byte):
              - Map file size (4 bytes)
              - else Map file size (string)
          - Allowed Game Versions (string)
          - Per image url:
            - Image url (string)
        '''
        wutil = utils.WriteToFileUtils(file)

        # Header, Version, ID, "is_allowed", number of image previews,
        # Date, Download Count, View Count, Like Count, Dislike Count
        file.write(datafile_header)
        wutil.writepack('BB',*datafile_version)
        wutil.writepack('H?BI',self.id,self.is_allowed,len(self.previews),int(self.date.timestamp()))
        wutil.writepack('IIII',self.downloads,self.views,self.likes,self.dislike)

        # Name, Category, Author, Description
        wutil.writestring(self.name, 2)
        wutil.writestring(self.category, 1)
        wutil.writestring(self.author, 1)
        wutil.writestringcompress(self.description, 2)

        # Download URL, Download File size
        wutil.writestring(self.dl_url)
        if type(self.fsize) is str:
            wutil.writesingle(0, 1)
            wutil.writestring(self.fsize, 1)
        else:
            wutil.writesingle(1, 1)
            wutil.writesingle(self.fsize, 4)

        # "for_versions", Image Preview URLs
        wutil.writestring(self.for_versions, 1)
        for i in range(len(self.previews)):
            wutil.writestring(self.previews[i], 2)

    
    def updatecounts(self, mapdat):
        for l in ('downloads','views','likes','dislike'):
            self[l] = mapdat[l]
