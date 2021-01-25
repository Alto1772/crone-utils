#!/usr/bin/python3
import requests
import utils
import io
import gzip
import tqdm

datafile_url = 'https://www.worldofskins.org'

class ImagePreviews():
    def __init__(self, mapdata):
        self.__dict__.update({
            'previews': mapdata.previews,
            'previewdatas': [None] * len(mapdata.previews),
        })
    
    def dlimg(self, index, sess=None):
        if sess is None: sess = requests.Session()
        with io.BytesIO() as f:
            with requests.get(datafile_url+self.previews[index], stream=True) as req:
                print(f">> {req.headers['content-length']} bytes")
                with tqdm.tqdm(total=int(req.headers['content-length']),unit_scale=True,unit_divisor=1024,unit='B') as bar:
                    for it in req.iter_content(1024):
                        f.write(it)
                        bar.update(len(it))
            self.previewdatas[index] = f.getvalue()

    def writetofile(self, file):
        wu = utils.WriteToFileUtils(file)
        with gzip.open(file, 'wb') as zf:
            for la in self.previewdatas:
                if la is None:
                    wu.writesingle(0, 4)
                else:
                    wu.writesingle(len(la), 4)
                    zf.write(la)

    def __len__(self):
        return len(self.previews)

    def __getitem__(self, key):
        return self.previews[key]

    def __iter__(self):
        return iter(self.previews)

def main():
    import mapsdatas
    import os

    ls = os.listdir('data')
    os.chdir('data')
    rsess = requests.Session()

    for dld in ls:
        if not dld.endswith('.dat'): continue
        print(f'> Reading {dld}')
        with open(dld,'rb') as f:
            waf = mapsdatas.mapdata.parsefromdatafile(f)
            duf = ImagePreviews(waf)
        if os.path.isfile(str(waf.id) + '.imgs'): continue

        for idd in range(len(duf)):
            print(f'> Downloading #{idd} ({duf.previews[idd]!r})')
            try: duf.dlimg(idd, rsess)
            except requests.exceptions.ConnectionError as e:
                print(e)
        with open(str(waf.id) + '.imgs', 'wb') as f:
            print(f'> Writing {waf.id}.imgs')
            duf.writetofile(f)

if __name__ == '__main__':
    main()
