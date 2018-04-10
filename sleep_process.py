import tornado.ioloop
from tornado.web import RequestHandler
# import tornado.options
from setproctitle import setproctitle
from subprocess import call, Popen
import sys
from time import sleep


class MainHandler(tornado.web.RequestHandler):
    def stoptornado(self):
        print 'stopping'

        tornado.ioloop.IOLoop.current().stop()
        print 'stopped'
    def get(self, param):
        self.render('templates/wakingup.html')
        print 'stopping tornado'
        self.stoptornado()
        print 'stoptornado done'
        result = Popen(['python', '/home/exaltia/Chat/app.py', 'waitforit'])
        print result
        sys.exit(result)
class Application(tornado.web.Application):
    """
    Main Class for this application holding everything together.
    """
    def __init__(self):
        # Handlers defining the url routing.
        handlers = [
            # (r"/swapspace", MainHandler),
            # (r"/room/([^/]+)", MainHandler),
            # (r"/privateroom/([^/]+)", PrivateRoom),
            # (r"/testpin?([^/]+)", PinItem),
            # (r"/testunpin?([^/]+)", UnPinItem),
            # (r"/detach?([^/]+)", DetachFile),
            # (r"/fileroom?([^/]+)", FileRoom),
            # #(r"/room/([a-zA-Z0-9]*)$", MainHandler),
            # #(r"/room&([^/]+)", MainHandler),
            # (r"/logout", LogoutHandler),
            # (r"/socket", ChatSocketHandler),
            # (r"/socket/([a-zA-Z0-9]*)$", ChatSocketHandler),
            # (r"/privatesocket", PrivateChatSocketHandler),
            # (r"/privatesocket/([a-zA-Z0-9]*)$", PrivateChatSocketHandler),
            # #(r"/upload?([^/]+)", UploadHandler),
            # (r"/upload", UploadHandler),
            # (r"/uploads", MainHandler),
            # (r"/save", ChatEdit),
            (r"/(.*)", MainHandler), #This line must stay at the end, or it intercept to urls who are handler by other code sections
        ]


        # Settings:
        settings = dict(
            # cookie_secret = "43osdETzKXasdQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=", #BAAAD, according to some devs, this cookie secret is as important as a ssl private key, so must be put outside of code
            # login_url = "/login",
            # template_path=os.path.join(os.path.dirname(__file__), "templates"),
            # static_path=os.path.join(os.path.dirname(__file__), "static"),
            # xsrf_cookies= True,
            # autoescape="xhtml_escape",
            # # Set this to your desired database name.
            # db_name = 'chat',
            # # apptitle used as page title in the template.
            # apptitle = 'Chat example: Tornado, Redis, brukva, Websockets',
            autoreload=True,
            debug=True,
        )

        # Call super constructor.
        tornado.web.Application.__init__(self, handlers, **settings)

        # Stores user names.
        self.usernames = {}

        # Connect to Redis.
        # self.client = redis_connect()

dictconf = {}
with open('./settings.cfg', 'r') as configfile: #Todo: Change this for ini style configparser
    for line in configfile:
        if '#' not in line:
            line = line.strip()
            line = line.replace(' ', '')
            line = line.split('=')
            dictconf[line[0]] = line[1]
# tornado.options.define("port", default=dictconf['port'], help="run on the given port", type=int)

# def redis_connect():
#     """
#     Established an asynchronous resi connection.
#     """
#     # Get Redis connection settings for Heroku with fallback to defaults.
#     redistogo_url = os.getenv('REDISTOGO_URL', None)
#     if redistogo_url == None:
#         REDIS_HOST = '10.42.42.1'
#         REDIS_PORT = 6379
#         REDIS_PWD = None
#         REDIS_USER = None
#     else:
#         redis_url = redistogo_url
#         redis_url = redis_url.split('redis://')[1]
#         redis_url = redis_url.split('/')[0]
#         REDIS_USER, redis_url = redis_url.split(':', 1)
#         REDIS_PWD, redis_url = redis_url.split('@', 1)
#         REDIS_HOST, REDIS_PORT = redis_url.split(':', 1)
#     client = brukva.Client(host=REDIS_HOST, port=int(REDIS_PORT))#, password=REDIS_PWD)
#     client.connect()
#     return client



def main():
    """
    Main function to run the chat application.
    """
     # This line will setup default options.
    # print('heh?')
    # print 'pid is', os.getpid()
    # tornado.options.parse_command_line()
    # Create an instance of the main application.
    application = Application()
    # Start application by listening to desired port and starting IOLoop.
    # proctitle = 'AppChat ' + dictconf['uniqueID']
    # print 'proctitle', proctitle
    setproctitle('AppChat sleeping ' + dictconf['uniqueID'])
    application.listen(dictconf['port'])
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()