import urllib2


class HttpHelper:

    def __init__(self):
        pass

    @staticmethod
    def http_get(url):
        f = urllib2.urlopen(url)
        s = f.read()
        return s



