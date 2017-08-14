import web
from portal.index import Index, Credit

urls = ("/", "Index",
        "/credit", "Credit")

app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()