import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.auth
import tornado.options
import tornado.escape
import os
import json
from tornado import gen
##
tornado.options.define("port", default=8080, help="run on the given port", type=int)
class Jsontest1(tornado.web.RequestHandler):
    def set_default_headers(self):
        print("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Content-Type", "application/json")


    def get(self):
        print('hop')
        # self.content_type = 'application/json'

        # self.set_header("Access-Control-Allow-Origin: *")
        # print 'xsrf token', self.xsrf_token
        print('je get?')
        a = []
        # testmsg = {
        #     "username": "machin",
        #     "body": "bidule",
        #     "avatar": "none"}
        testmsg = {
            "username": "Ewen Lidgey",
            "email": "elidgey0@soundcloud.com",
            "userId": "21be5411-e474-4760-8973-d96d0649a3d3",
            # "avatar": "https://robohash.org/quodnullarepellendus.jpg?size=200x200\u0026set=set1",
            "body": "Vivamus vel nulla eget eros elementum pellentesque. Quisque porta volutpat erat. Quisque erat eros, viverra eget, congue eget, semper rutrum, nulla.",
            "timestamp": "3:57 AM"
        }
        # ,{
        #     "username": "bidule",
        #      "body": "truc",
        #      "avatar": "none"}
        # }
        multikeys = []
        for i in range(3):
            multikeys.append(testmsg)
            # multikeys.append(dict([(x, x ** 3) for x in xrange(1, 3)]))
        # print 'testmsg?', testmsg, '\n'
        encoded_content = tornado.escape.json_encode(multikeys)
        # print 'encoded', multikeys
        # print 'type?', type(multikeys)
        print('encoded', encoded_content)
        self.write(encoded_content)
        print("c'et fini!")
        # self.finish()
class Application(tornado.web.Application):
    """
    Main Class for this application holding everything together.
    """
    def __init__(self):
        # Handlers defining the url routing.
        handlers = [
            (r"/chat.json", Jsontest1)
        ]
        settings = dict(
            cookie_secret="43osdETzKXasdQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            # BAAAD, according to some devs, this cookie secret is as important as a ssl private key, so must be put outside of code
            login_url="/login",
            template_path=os.path.join(os.path.dirname(__file__), "themes"),
            static_path=os.path.join(os.path.dirname(__file__), "themes"),
            # static_url_prefix=os.path.join(os.path.dirname(__file__), "themes"),
            xsrf_cookies=True,
            autoescape="xhtml_escape",
            # Set this to your desired database name.
            db_name='chat',
            # apptitle used as page title in the template.
            apptitle='Chat example: Tornado, Redis, brukva, Websockets',
            autoreload=True,
            debug=True,
        )
        # Call super constructor.
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    application = Application()
    application.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
    main()
