import reqbase
import requests
import json.decoder

api_url = "https://www.worldofskins.org/project/mapsapi.php"
accesstoken = "D0E0EF2765CCA96B7DCF8ADB72C928816CABF2BD3C9190D9DF95E046B2458C10"

def base_get(sess, act, rparams={}, headers={}, **kwargs):
    'Wrapper for the base get request function'
    if sess is None: sess = requests.Session()
    if not isinstance(sess, requests.Session):
        raise TypeError('sess param is not a Session object')
    return reqbase.get(api_url, sess, act=act, accesstoken=accesstoken, headers=headers, rparams=rparams, **kwargs)

def get_maps(sess=None, **kwargs):
    'Get all map infos from server'
    return base_get(sess, 'getall', rparams=kwargs)

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
