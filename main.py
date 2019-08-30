import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.auth
import tornado.options
import tornado.escape
import os
from time import sleep

from tornado import gen
##
tornado.options.define("port", default=8080, help="run on the given port", type=int)
class LoginTest(tornado.web.RequestHandler):
    def set_default_headers(self):
        print("setting headers for options")
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, Access-Control-Allow-Origin, Authorization, Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')
        self.set_header('Access-Control-Allow-Credentials', 'true')
    #     self.set_header('X-XSRFToken', self.xsrf_token)

    def options(self):
        print('there')
        pass
    def post(self):
        print('pouet')
        # print(type(self.request.body))
        # httpbody = self.request.body.decode("utf-8")
        # httpbody = dict(httpbody)
        # print(type(httpbody))
        # sleep(5)
        # email = self.get_arguments('email')
        # password = self.get_arguments('password')
        # print('email is ', email)# == 'a@a.a')
        response_json = {
            'token': 'ABCDEFGHIJKLMOPQRSTUVWXYZ1234567890',
            'email': 'fakemail@fakedomain.com',
            'username': 'fakestaticusername'
        }
        encoded_json = tornado.escape.json_encode(response_json)
        self.write(encoded_json)
        # print(self.request.headers)

        # print(self.request.body)
class Jsontest1(tornado.web.RequestHandler):
    def set_default_headers(self):
        print("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Content-Type", "application/json")


    def get(self):
        print('hop')
        print('je get?')
        print(self.request.headers)
        a = []
        testmsg = {
            "username": "Ewen Lidgey",
            "email": "elidgey0@soundcloud.com",
            "userId": "21be5411-e474-4760-8973-d96d0649a3d3",
            # "avatar": "https://robohash.org/quodnullarepellendus.jpg?size=200x200\u0026set=set1",
            "body": "Vivamus vel nulla eget eros elementum pellentesque. Quisque porta volutpat erat. Quisque erat eros, viverra eget, congue eget, semper rutrum, nulla.",
            "timestamp": "3:57 AM"
        }
        multikeys = []
        for i in range(3):
            multikeys.append(testmsg)
        encoded_content = tornado.escape.json_encode(multikeys)
        print('encoded', encoded_content)
        self.write(encoded_content)
        print("c'et fini!")
class Application(tornado.web.Application):
    """
    Main Class for this application holding everything together.
    """
    def __init__(self):
        # Handlers defining the url routing.
        handlers = [
            (r"/chat.json", Jsontest1),
            (r"/login", LoginTest)
        ]
        debug = True
        settings = dict(
            cookie_secret="43osdETzKXasdQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            # BAAAD, according to some devs, this cookie secret is as important as a ssl private key, so must be put outside of code
            login_url="/login",
            template_path=os.path.join(os.path.dirname(__file__), "themes"),
            static_path=os.path.join(os.path.dirname(__file__), "themes"),
            # static_url_prefix=os.path.join(os.path.dirname(__file__), "themes"),
            xsrf_cookies=False,
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
