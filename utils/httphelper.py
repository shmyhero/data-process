import urllib2


class HttpHelper:

    def __init__(self):
        pass

    @staticmethod
    def http_get(url, headers=None):
        if headers:
            f = urllib2.urlopen(urllib2.Request(url=url, headers=headers))
        else:
            f = urllib2.urlopen(url)
        s = f.read()
        return s



