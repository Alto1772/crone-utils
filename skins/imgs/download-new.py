#!/usr/bin/python3
import sys, os
import requests
import struct

gurl = ""
gcurrnum = 0
args = {"debug": False, "threads": 4, 'err': False, 'progress': False}

def download(sess, id):
    try: req = sess.get(gurl % id, timeout=(5, 30))
    except requests.exceptions.ConnectionError: return 0
    except requests.exceptions.Timeout: return 1
    if req.ok:
        with open(str(id)+'.png','wb') as f:
            f.write(req.content)
        return True
    else: return False

def readconf():
    global gcurrnum, gurl
    with open('conf','rb') as f:
        gcurrnum = struct.unpack('>I',f.read(4))[0]
        gurl = f.read().decode('utf8')

def writeconf():
    with open('conf','wb') as f:
        f.write(struct.pack('>I',gcurrnum))
        f.write(bytes(gurl,'utf8'))

# add threading begin

import threading, queue
threads = []
tdmthread = None
max_size = 256

def tinit():
    global tdmthread
    for i in range(args['threads']):
        printdbg(f'# Init Thread {i}')
        qin = queue.Queue(args['threads'])
        qout = queue.Queue()
        t = threading.Thread(target=process, args=(i,qin,qout,requests.Session()))
        threads.append((t,qin,qout))
        threads[i][0].start()
    if args['progress']:
        qin = queue.Queue(args['threads'])
        tdmthread = threading.Thread(target=tdmproc, args=(qin,)), qin

import tqdm
def tdmproc(hin):
    with tqdm.tqdm(initial=hin.get()) as tdm:
        while not hin.get_nowait():
            status = []
            for xai in threads:
                xai[2].get(); tdm.update()
                status.append(xai[0].is_alive())
            if any(status): break

def tquit():
    printdbg('# Quitting Threads')
    for ti in threads:
        while not ti[2].empty(): ti[2].get()
        try: ti[1].put(False, timeout=1)
        except queue.Full: pass
        ti[0].join()
    writeconf()
    notfu = True
    while notfu:
        try: 
            tdmthread[1].put(False, timeout=1)
            notfu=False
        except queue.Full: pass

def printdbg(*vargs, **kwargs):
    if args['debug']: print(*vargs, **kwargs)

def printcond(tid, msg, **kwargs):
    if args['debug']: print(f'#{tid}. {msg}', **kwargs)
    elif not args['progress']: print(msg, **kwargs)

def process(id, queuein, queueout, rsess):
    printdbg(f'#{id}. > [INIT]')
    retries = 0
    tryagain = False
    while True:
        if not tryagain: q = queuein.get()
        if q is False:
            printdbg(f'#{id}. > [REQUEST STOP]')
            break
        if os.path.isfile(f'{q}.png'):
            printdbg(f'#{id}. ! {q}.png exists!')
            retries = 0
            continue
        data = download(rsess, q)
        if data is True :
            printcond(id, f'> {q}.png')
            retries = 0
            tryagain = False
            queueout.put(id)
        elif data == 1:
            printcond(id, '! Request timed out.')
            retries += 1
            tryagain = True
        elif data == 0:
            printcond(id,'! Connection Error.')
            retries += 1
            tryagain = True
        else:
            printcond(id, f'! {q}.png not found!')
            retries += 1
            tryagain = False
        if retries == 10:
            printdbg(f'#{id}. > [STOPPED]')
            break

def checkthreads():
    status = []
    for ti in threads:
        if not args['progress']:
            while not ti[2].empty(): ti[2].get_nowait()
        status.append(ti[0].is_alive())
    printdbg(status)
    return any(status)

def main(argv):
    global gcurrnum
    os.chdir(argv)
    readconf()
    tinit()
    for ai in range(15):
        for ti in threads:
            ti[1].put(gcurrnum)
            gcurrnum += 1
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

# add threading end

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
        elif sys.argv[1] == '-p':
            args['progress'] = False
            sys.argv.pop(1)
        else: running = False

parseopts()
main(sys.argv[1])
