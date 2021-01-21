import reqbase
import requests
import json.decoder

api_url = "https://www.worldofskins.org/project/api.php"
accesstoken = "vmU^8UdW&k#dJY*Bg4CgN&H#kCxR44a="

def base_get(sess, act, rparams={}, headers={}, **kwargs):
    'Wrapper for the base get request function'
    if sess is None: sess = requests.Session()
    if not isinstance(sess, requests.Session):
        raise TypeError('sess param is not a Session object')
    return reqbase.get(api_url, sess, act=act, accesstoken=accesstoken, headers=headers, rparams=rparams, **kwargs)

def get_count(folder, sess=None, **kwargs):
    'Count all PNG images on a directory inside a server'
    return base_get(sess, 'count_max_skins', folder=folder, rparams=kwargs)['response']

def get_data(type, id, sess=None, **kwargs):
    'Request skin info from server'
    return base_get(sess, 'get', id=id, type=type, rparams=kwargs)

def set_viewed(id, sess=None, **kwargs):
    'increment view count on a specific id'
    return base_get(sess, 'views', id=id, rparams=kwargs)

def set_downloaded(id, sess=None, **kwargs):
    'increment download count on a specific id'
    return base_get(sess, 'views', id=id, rparams=kwargs)

def set_liked(id, sess=None, **kwargs):
    'increment like count on a specific id'
    return base_get(sess, 'likes', id=id, rparams=kwargs)

def set_disliked(id, sess=None, **kwargs):
    'increment dislike count on a specific id'
    return base_get(sess, 'dislike', id=id, rparams=kwargs)
