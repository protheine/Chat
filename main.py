import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.options
import tornado.escape
import os
import sys
import traceback
#import python_core_api.websocket #For future use

import hashlib
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider #one module to authentificate them all!
import dbmodel
# from time import sleep
#
# from tornado import gen
cluster = Cluster(['192.168.0.95'])
auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
cassandrasession = cluster.connect()
instancied_db_model = dbmodel
##
tornado.options.define("port", default=8080, help="run on the given port", type=int)
class cqlqueries(): #Use this in the futur to pass queries to the class
    pass

class test(tornado.web.RequestHandler):
    async def get(self):
        self.write('Hello world')
class LoginTest(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self):
        print('there')
        pass
    def post(self):
        print('pouet')
        httpbody = (self.request.body)
        httpbody = self.request.body.decode("utf-8")
        # httpbody = dict(httpbody)
        httpbody = tornado.escape.json_decode(httpbody)
        email = httpbody['email']
        httppassword = httpbody['password']
        print('password is', httppassword)
        result = instancied_db_model.users.objects.filter(email=email)
        sql = 'SELECT password FROM users.users WHERE email = %s'
        result = cassandrasession.execute(sql, [email])
        # print('cqlresult', result, 'type', type(result))
        for each in result:
            print('each result', each, 'type', type(each))
            if httppassword == each[0]:
                response_json = {
                    'token': '1234567890ABCDEFGHIJKLMOPQRSTUVWXYZZ', #Todo: generate token on the fly
                    'userId': 'null',
                    'userEmail': email,
                    'isAdmin': 'True'  # Not sure if the UI take that in account ATM
                }
                encoded_json = tornado.escape.json_encode(response_json)
                self.write(encoded_json)

            else:
                self.send_error(403) #if we don't send error, the application still gives access to the page



class Application(tornado.web.Application):
    """
    Main Class for this application holding everything together.
    """
    def __init__(self):

        # Handlers defining the url routing.
        handlers = [
            #(r"/chat.json", Jsontest1),
            (r"/auth/login", LoginTest),
            (r"/test", test),
            # (r"/", websockettest)
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
    if len(sys.argv) == 1:
        print('you must specify "firstinit" or "run" arg')
        sys.exit(1)
    else:
        if len(sys.argv) > 2:
            print('too much command line arguments, exiting')
            sys.exit(1)
        else:
            if str(sys.argv[1]) == 'firstinit':
                cluster = Cluster(['192.168.0.95'])
                auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
                cassandrasession = cluster.connect()
                print('create keyspace')
                cassandrasession.execute("""
                        CREATE KEYSPACE IF NOT EXISTS users
                        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
                        """)
                print('creating tables')
                try:
                    cassandrasession.execute("""
                           CREATE TABLE IF NOT EXISTS users.users (
                                    isActive boolean,
                                    isAdmin boolean,
                                    "_id" varchar,
                                    email varchar primary key,
                                    password varchar,
                                    name varchar,
                                    createdAt timestamp,
                                    lastLogin timestamp,
                                    updatedAt timestamp
                           )
                           """)
                    cassandrasession.execute("""
                            INSERT INTO users.users (email, "_id", createdat, isactive, isadmin, lastlogin, name, password, updatedat) VALUES ('exaltia@exaltia.org', null, null, True, True, null, null, 'password', null)
                            """,)
                    print('database initialisation ended, will exit now, relaunch your software\n with run parameter instead of firstinit')
                except:
                    print('something went wrong but there is not enough code ATM to say what gone wrong')
                    print(traceback.format_exc())
                    sys.exit(1)
                sys.exit(0)

            elif str(sys.argv[1]) == 'run':
                pass
            elif str(sys.argv[1]) == 'help':
                print('Only 1 option accepted wich is either firstinit or run\n '
                      'DO NOT run firstinit if you want to '
                      'keep data and have already initialised the software')
                sys.exit(0)
            else:
                print('invalid keyword, exiting')
                sys.exit(1)
    application = Application()
    application.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
    main()
