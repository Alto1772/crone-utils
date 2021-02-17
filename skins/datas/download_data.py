#!/usr/bin/python3
import crone_api
import struct
import zlib
import confutils

gcurrnum = 0
args = {'type':'','debug':False,'threads':4, 'err': False}

import requests
def download(sess, type, id):
    try:
        rq=crone_api.get_data(type, id, sess, timeout=(5,30))
    except requests.exceptions.ConnectionError: return 0
    except requests.exceptions.Timeout: return 1
    if args['debug']: print(rq)
    if isinstance(rq, str) or rq.get('response') == '500':
        print('String returned:')
        print(rq)
        return (rq, False)
    else: return (rq, True)

encoding = 'utf-8'

def writedata(f, data):
    '''
    id        = int [I]
    likes     = int [I]
    downloads = int [I]
    views     = int [I]

    comment = compressed string (length as short [H])
    author  = compressed string (length as short [H])
    date    = string (YYYY-MM-DD)
    hash    = compressed string (length as short [H])

    AA AA AA AA BB BB BB BB CC CC CC CC DD DD DD DD
    EE EE FF FF GG GG GG GG GG GG GG GG GG GG HH HH ...
    '''
    f.write(struct.pack('>4I', int(data['id']), int(data['likes']), int(data['downloads']), int(data['views'])))

    comm_compressed = zlib.compress(bytes(data['comment'],encoding)) if data['comment'].strip() else b''
    auth_compressed = zlib.compress(bytes(data['author'],encoding)) if data['author'] or data['author'] != 'Unknown' else b''
    date = bytes(data['date'], 'ascii')
    hash_compressed = zlib.compress(bytes(data['hash'],encoding)) if data['hash'] else b''

    f.write(struct.pack('>HH10sH', len(comm_compressed), len(auth_compressed), date, len(hash_compressed)))

    f.write(comm_compressed)
    f.write(auth_compressed)
    f.write(hash_compressed)

import threading, queue
threads = []
max_size = 256
def tinit():
    for i in range(args['threads']):
        printdbg(f'# Init Thread {i}')
        qin = queue.Queue(args['threads'])
        qout = queue.Queue()
        t = threading.Thread(target=process, args=(i,qin,qout,requests.Session()))
        threads.append((t,qin,qout))
        threads[i][0].start()

def tquit():
    printdbg('# Quitting Threads')
    for ti in threads:
        while not ti[2].empty(): ti[2].get()
        try: ti[1].put(False, timeout=1)
        except queue.Full: pass
        ti[0].join()

def printdbg(*vargs, **kwargs):
    if args['debug']: print(*vargs, **kwargs)

def printcond(tid, msg):
    if args['debug']: print(f'#{tid}. {msg}')
    else: print(msg)

import os, sys
def process(id, queuein, queueout, rsess):
    printdbg(f'#{id}. > [INIT]')
    retries = 0
    tryagain = False
    while True:
        if not tryagain: q = queuein.get()
        if q is False:
            printdbg(f'#{id}. > [REQUEST STOP]')
            queueout.put(False)
            break
        if os.path.isfile(f'{q}.dat'):
            printdbg(f'#{id}. ! {q}.dat exists!')
            retries = 0
            queueout.put(True)
            continue
        data = download(rsess, args['type'], q)
        if type(data) is tuple and data[1] :
            printcond(id, f'> {q}.dat')
            retries = 0
            tryagain = False
            with open(f'{q}.dat','wb') as f:
                writedata(f, data[0])
            queueout.put(True)
        elif data == 1:
            printcond(id, '! Request timed out.')
            retries += 1
            tryagain = True
        elif data == 0:
            printcond(id,'! Connection Error.')
            retries += 1
            tryagain = True
        else:
            printcond(id, f'! {q}.dat not found!')
            if args['debug'] and args['err']:
                import json
                with open(f'{q}.err','w') as ef:
                    if type(data[0]) is str: ef.write(data[0])
                    else: json.dump(data[0],ef)
            retries += 1
            tryagain = False
            queueout.put(True)
        if retries == 10:
            printdbg(f'#{id}. > [STOPPED]')
            queueout.put(False)
            break

#import tqdm
def checkthreads():
    status = []
    for ti in threads:
        vv = None
        while not ti[2].empty():
            vv = ti[2].get_nowait()
        if vv is None: vv = ti[0].is_alive()
        #if vv is True: tdm.update()
        status.append(vv)
    printdbg(status)
    return any(status)

def main(argv):
    global gcurrnum, tdm
    os.chdir(argv)
    gcurrnum, args['type'] = confutils.readconf()
    tinit()
    for ai in range(15):
        for ti in threads:
            ti[1].put(gcurrnum)
            gcurrnum += 1
    #with tqdm.tqdm(initial=gcurrnum) as tdm:
    running = True
    while running:
      try:
        while checkthreads():
          for ti in threads:
            ti[1].put(gcurrnum, timeout=10)
            gcurrnum += 1
      except queue.Full:
          if not checkthreads(): running = False
    tquit()

def parseopts():
    running = True
    while running:
        if sys.argv[1] == '-d':
            args['debug'] = True
            sys.argv.pop(1)
        elif sys.argv[1] == '-e':
            args['err'] = True
            sys.argv.pop(1)
        elif sys.argv[1] == '-t':
            sys.argv.pop(1)
            args['threads'] = int(sys.argv.pop(1))
        else: running = False

parseopts()
main(sys.argv[1])
