#!/usr/bin/python3
import sys, os
import requests
import confutils

MAX_RETRIES = 10

gurl = ""
gcurrnum = 0

debug = False
threads = 0

def download(sess, url, id):
    req = sess.get(url % id, timeout=(5, 30))
    if req.ok:
        with open(str(id)+'.png','wb') as f:
            f.write(req.content)
        return True
    else:
        if debug:
            with open(str(id)+'.err.txt','wb') as f:
                f.write(req.content)
        return False

import tqdm

def process():
    global gcurrnum
    retries = 0
    with requests.Session() as rsess, tqdm.tqdm(initial=gcurrnum) as bar:
        while retries < MAX_RETRIES:
            try:
                while download(rsess, gurl, gcurrnum):
                    bar.update()
                    retries = 0
                    gcurrnum += 1
                    confutils.writeconf(gcurrnum, gurl)
            except requests.exceptions.ReadTimeout:
                retries += 1
                print('! Request Timed Out.')
                continue
            except requests.exceptions.ConnectionError as e:
                retries += 1
                print('! Connection Error')
                continue
            print(f'! {gcurrnum}.png not found!')
            bar.update()
            retries += 1
            gcurrnum += 1

def main(arg):
    global gcurrnum, gurl
    if not os.path.isdir(arg): os.mkdir(arg)
    os.chdir(arg)
    gcurrnum, gurl = confutils.readconf()
    process()

def parse_opts():
    running = True
    global debug, threads
    while running:
        if sys.argv[1] == 'd':
            debug = True
            sys.argv.pop(1)
        elif sys.argv[1] == '-t':
            sys.argv.pop(1)
            threads = int(sys.argv.pop(1))
        else:
            running = False

parse_opts()
main(sys.argv[1])
