import requests
import logging
import json.decoder

# this version of the scripts
version = '1.0.3'

# user agent
useragent = "YourServersSuck/{}".format(version)

# debug request unfinished
def printdebugrequest(req):
    print(req.url)
    print(req.request.headers)
    print(req.headers)
    print(req.text)

def debugrequest(req):
    logging.debug(req.url)
    logging.debug(req.request.headers)
    logging.debug(req.headers)
    logging.debug(req.text)

def get(url, sess, *, rparams={}, headers={}, accesstoken=None, raw=True, **params):
    'This is the base get request function'
    req = sess.get(url, params=params, headers={
        'Authorization': accesstoken,
        'User-agent': useragent,
        **headers
    }, **rparams)
    #printdebugrequest(req)
    try:
        j = req.json()
    except json.decoder.JSONDecodeError:
        raw = False
    if raw: return j
    else: return req.text

