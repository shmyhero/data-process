import urllib


class HttpHelper:

    def __init__(self):
        pass

    @staticmethod
    def http_get(url):
        f = urllib.urlopen(url)
        s = f.read()
        return s



