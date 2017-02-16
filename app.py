#
# coding=UTF-8
# General modules.
from MySQLdb import *
import settings as config
import os, os.path
import logging
import sys
from threading import Timer
import string
import random
from PIL import Image
# Tornado modules.
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.auth
import tornado.options
import tornado.escape
from tornado import gen
import time
# Redis modules.
import brukva
# Import application modules.
from base import BaseHandler
#from login import LoginHandler
from login import LogoutHandler
#import settings as config
# Define port from command line parameter.
tornado.options.define("port", default=8888, help="run on the given port", type=int)
class ChatEdit(tornado.web.RequestHandler):
    def post(self):
        print "Placeholder"
class UploadHandler(tornado.web.RequestHandler):#tornado.web.RequestHandler):
    def post(self, url):
        db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB)
        cursor = db.cursor()
        uri = self.request.uri
        url = uri.split('/')
        RoomName = url[3]
        sql = 'SELECT RoomID FROM abcd_un WHERE RoomName = %s', [RoomName]
        cursor.execute(*sql)
        RoomID = cursor.fetchone()
        RoomID = str(RoomID[0])
        RoomID = RoomID.decode()
        origin = self.request.protocol + "://" + self.request.host + '/' + url[2] + '/' + url[3]
        file1 = self.request.files['file1'][0]
        original_fname = file1['filename']
        try: # TODO : Better use mime type!
            current_location2 = self.request.protocol + "://" + self.request.host + "/static/uploads/" + 'resized-' + original_fname
            fname_tuple = original_fname.rsplit('.', 1)
            if fname_tuple[1] == 'jpg':
                file_url2 = "<img src ='" + current_location2 + "'/>"
                message2 = {
                '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                'date': time.strftime("%H:%M:%S"),
                'type': 'regular',
                'from': 'Guest',
                'body': file_url2,
                }
            elif fname_tuple[1] == 'gif':
                print "It's a JIF!"
                file_url2 = '<img src ="' + current_location2 + '" >'
                message2 = {"body": file_url2,
                "_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),	"from": "Guest"}
            elif fname_tuple[1] == 'png':
                file_url2 = '<img src ="' + current_location2 + '" width="50%" height="50%"/>'
                message2 = {"body": file_url2,
                "_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),	"from": "Guest"}
            elif fname_tuple[1] == 'bmp':
                file_url2 = '<img src ="' + current_location2 + '" width="50%" height="50%"/>'
                message2 = {"body": file_url2,
                "_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),	"from": "Guest"}
            elif fname_tuple[1] == 'mp4':
                file_url2 = '<video width="320" height="240" controls="controls">' + '<source src="'+ current_location2 + '" type="video/mp4" />' + '</video>'
                message2 = {"body": file_url2,
                "_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),	"from": "Guest"}
            else:
                file_url2 = ''
                message2 = ''
            output_file = open("static/uploads/" + original_fname, 'wb')
            output_file.write(file1['body'])
            size = 128, 128
            output_file.close()
            thumbwidhtsize, thumbheightsize = 128, 128
            size = thumbwidhtsize, thumbheightsize
            img = Image.open(os.path.join("static/uploads/", original_fname))
            width, height = img.size
            if width > height: #Ratio calculation, depending on wich side is the longuest one
                ratio = width / thumbwidhtsize
                finalsize = width / ratio, height / ratio
                print finalsize
                img = img.resize((finalsize), Image.BILINEAR)
            else:
                ratio = height / thumbheightsize
                finalsize = width / ratio, height / ratio
                img = img.resize((finalsize), Image.BILINEAR)

            img.save(os.path.join("static/uploads/", 'resized-' + original_fname))

            redistogo_url = os.getenv('REDISTOGO_URL', None)
            REDIS_HOST = 'localhost'
            REDIS_PORT = 6379
            REDIS_PWD = None
            REDIS_USER = None
            client = brukva.Client(host=REDIS_HOST, port=int(REDIS_PORT), password=REDIS_PWD)
            client.connect()
            client.listen(self)
            current_location = self.request.protocol + '://' + self.request.host + "/static/uploads/" + original_fname
            file_url = 'file ' + original_fname + ' has been uploaded to ' + tornado.escape.linkify(current_location)
            message = {
                '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                'date': time.strftime("%H:%M:%S"),
                'type': 'regular',
                'from': 'Guest',
                'body': file_url,
            }
            message_encoded = tornado.escape.json_encode(message)
            room = RoomID #FIXME : message will land in room 1 for all upload in all rooms
            logging.info('New user for upload connected to chat room ' + room)
            client.rpush(room, message_encoded)
            #Publish message in Redis channel
            client.publish(room, message_encoded)
            if message2 is not '':
                message_encoded = tornado.escape.json_encode(message2)
                client.rpush(room, message_encoded)
                #Publish message in Redis channel.
                client.publish(room, message_encoded)
            else:
                pass
            time.sleep(1)
            t = Timer(0.1, client.disconnect)
            t.start()
            db.close()
            self.redirect(origin)
            # self.finish('pouet')
        except:
            print 'Hey, something went wrong!', sys.exc_info()

class MainHandler(BaseHandler):
    """
    Main request handler for the root path and for chat rooms.
    """
    def post(self, RoomName):
        db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB)
        cursor = db.cursor()
        uri = self.request.uri
        url = uri.split('/')
        RoomName = url[2]
        sql = 'SELECT RoomID FROM abcd_un WHERE RoomName = %s', [RoomName]
        cursor.execute(*sql)
        RoomID = cursor.fetchone()
        RoomID = str(RoomID[0])
        RoomID = RoomID.decode()
        fullurl = 'ws://' + self.request.host + '/socket/' + RoomID

        #print uri
        db.close()
        wsurl = {
            'url': fullurl,
        }
        wsurl_encoded = tornado.escape.json_encode(wsurl)
        self.write(wsurl_encoded)
    @tornado.web.asynchronous
    def get(self, room=None):
        print 'xsrf token', self.xsrf_token #DO NOT REMOVE doing that is enough to set the xsrf cookie, required by javascript to post, strange, i know
        url = self.request.uri
        url = url.split('/')
        RoomName = url[2]
        db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB)
        cursor = db.cursor()

        sql = 'SELECT RoomID FROM abcd_un WHERE RoomName = %s', [RoomName]
        cursor.execute(*sql)
        RoomID = cursor.fetchone()
        if not room:
            #self.redirect("/room/1")
            print 'error, no rooms'
            return
        # Set chat room as instance var (should be validated).
        self.room = RoomID
        # Get the current user.
        self._get_current_user(callback=self.on_auth)


    def on_auth(self, user):
        # Load 50 latest messages from this chat room.
        db = connect (host = config.SQLSERVER, user = config.SQLUSER, passwd = config.SQLPASS, db = config.SQLDB)
        cursor = db.cursor ()
        """
        Callback for third party authentication (last step).
        """
        if not user:
            self.redirect("/login") # TODO: Make this hard coded value fecthable from db for flexible configuration
        else:
            sql = ("SELECT UserID FROM Users_info WHERE UserName = '%s'") % user
            cursor.execute(sql)
            useridresult = cursor.fetchone()
            sql = "SELECT SessionID FROM Users WHERE UserID = %s", [useridresult]
            cursor.execute(*sql)
            SQLSessionID = cursor.fetchone()
            BroswerSessionID = self.get_secure_cookie('SessionID')
            if SQLSessionID[0] == BroswerSessionID:
                uri = self.request.uri
                url = uri.split('/')
                RoomName = url[2]
                RoomName = RoomName.strip('?')
                sql = 'SELECT RoomID FROM abcd_un WHERE RoomName = %s', [RoomName]
                cursor.execute(*sql)
                RoomID = cursor.fetchone()
                RoomID = str(RoomID[0])
                RoomID = RoomID.decode()
                if not 'userlist' in globals():
                    global userlist
                    userlist = []
                global userlist
                if user not in userlist:
                    userlist.append(user)
                self.room = RoomID
                self.application.client.lrange(self.room, -50, -1, self.stocka)
                self.application.client.lrange(user, -5, -1, self.stockb)
            else:
                self.redirect("/login") # TODO: Make this hard coded value fecthable from db for flexible configuration
    def stocka(self, result):
        print 'result type: ', type(result)
        global messages
        messages = []
        messages = result
        print 'messagesresultare :', messages
    def stockb(self, result):
        global notifications
        notifications = []
        notifications = result
        print 'notifresult is:', result
        self.on_conversation_found()
    def on_conversation_found(self):
        i = 0
        global messages
        global notifications
        mix = messages# + notifications
        print len(mix)
        db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB)
        cursor = db.cursor()
        AppID = '1'
        RoomNumber = '1' #Todo : Change that to non hardcoded values
        sql = "SELECT RoomID FROM abcd_un WHERE RoomNumber = %s AND AppID = %s", [RoomNumber, AppID]
        cursor.execute(*sql)
        RoomIDS = cursor.fetchall()
        temp = []
        messages = []
        notifications = []
        print 'mix is: ', type(mix), mix
        checktypevariable = str(type(mix))
        #checktypevariable = str(checktypevariable)
        print 'checkcontent', checktypevariable
        if checktypevariable == "<type 'tuple'>":
            print 'bing...'
            # messages={}
            messages =  'Error, you are using a non functional version of brukva, please use the one from evilkost<br><H1>Program terminated</H1>'
            self.render("test.html", messages=messages)
            sys.exit(1)
        elif checktypevariable == "<type 'list'>":
            for message in mix:
                print "je m'en fout"
               #checkvartype = "<type 'tuple'>"
                print 'typemessage', type(messages)
                try:
                    #print 'message type is: ', type(message), 'len is: ', len(message), 'and content[0] is: ', message
                    temp.append(tornado.escape.json_decode(message))
                    print "yep, it's a message"
                except:
                    print 'faulty message: ', message
                    i += 1 #if a message is bad, added to number of bad messages
                    print 'Hey, something went wrong in message sorting!', sys.exc_info()
                    pass
                if len(temp) == len(mix) - i: # number of bad messages soustracted to total messages received to get correct total before processing
                    try:
                        for message in temp:
                            if message['type'] == 'notification':
                                notifications.append(message)
                            elif message['type'] is not 'notification':
                                if 'username' not in locals():
                                    username = ''
                                if 'lastusername' not in locals():
                                    lastusername = ''
                                if message['from'] == lastusername:
                                    message['from'] = ''
                                    #time.sleep(0.2)
                                else:
                                    print 'username', message['from']
                                    lastusername = message['from']
                                messages.append(message)
                    except:
                        print 'faulty message: ', message
                        pass
        else:
            logging.error('Something really wrong happened')
            sys.exit(1)
        self.pagerender(messages, notifications)
        db.close()
    def pagerender(self, messages, notifications):#Renderding pages
        GroupID = '1'
        db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB)
        cursor = db.cursor()
        BroswerSessionID = self.get_secure_cookie('SessionID')
        print 'BroswerSessionID', BroswerSessionID
        sql = "SELECT UserID FROM Users WHERE SessionID = %s", [BroswerSessionID]
        cursor.execute(*sql)
        UserID = cursor.fetchone()
        print 'Userid', UserID
        sql = "SELECT UserGroupID, CompanyID FROM Users_info WHERE UserID = %s", [UserID]
        cursor.execute(*sql)
        GroupandOwnerID = cursor.fetchone()
        print 'GroupandOwnerID', GroupandOwnerID
        sql = "SELECT AppID, Tableprefix, AppName FROM GroupApps WHERE GroupID = %s AND OwnerID = %s", [GroupandOwnerID[0],
                                                                                                        GroupandOwnerID[1]]
        cursor.execute(*sql)
        AppID = cursor.fetchone()
        print 'AppID', AppID
        Tablename = AppID[1] + AppID[2]
        print 'Tablename', Tablename
        sql = "SELECT RoomName FROM " + Tablename + " WHERE AppID = %s", [AppID[0]]
        cursor.execute(*sql)
        RoomName = cursor.fetchall()
        print 'appid is:', AppID
        sql = "SELECT Csspath FROM Templates WHERE AppID = %s  AND GroupID = %s AND IsActive = '1'", (
            AppID[0], GroupID)
        cursor.execute(*sql)
        draftcsspath = cursor.fetchall()
        draftcsspath = draftcsspath[0][0].split('css', 1)
        draftcsspath = '../static/css' + draftcsspath[1]
        print 'draftcsspath is:', draftcsspath
        content = self.render_string("messages.html",  messages=messages)
        notifcontent = self.render_string("notifications.html", notifications=notifications)
        self.render_default("index.html", draftcsspath=draftcsspath, userlist=userlist, RoomName=RoomName, notifcontent=notifcontent, content=content, chat=1)
        print "je pagerender"
        db.close()
class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    """
    Handler for dealing with websockets. It receives, stores and distributes new messages.

    TODO: Not proper authentication handling!
    """
    def fileinfo(self):
        logging.info("i'm in")
        message = 'File ' + original_fname + ' has been uploaded'
        message_encoded = tornado.escape.json_encode(message)
        self.write_message(message_encoded)
        # Persistently store message in Redis.
        self.application.client.rpush(self.room, message_encoded)
        # Publish message in Redis channel.
        self.application.client.publish(self.room, message_encoded)
        fileflag = ''
        logging.info("i'm out")
    @gen.engine
    def open(self, room='root'):
        """
        Called when socket is opened. It will subscribe for the given chat room based on Redis Pub/Sub.
        """
        # Check if room is set.
        if not room:
            self.write_message({'error': 1, 'textStatus': 'Error: No room specified'})
            self.close()
            return
        self.room = str(room)
        self.new_message_send = False
        # Create a Redis connection.
        self.client = redis_connect()
        # Subscribe to the given chat room.
        self.client.subscribe(self.room)
        self.subscribed = True
        self.client.listen(self.on_messages_published)
        BroswerSessionID = self.get_secure_cookie('SessionID')
        user = self.get_secure_cookie('user')
        db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB)
        cursor = db.cursor()
        sql = "SELECT UserID From Users WHERE SessionID = %s", [BroswerSessionID]
        cursor.execute(*sql)
        UserID = cursor.fetchone()
        sql = "SELECT UserName FROM Users_info WHERE UserID = %s", [UserID]
        cursor.execute(*sql)
        UserName = cursor.fetchone()
        self.client.subscribe(user)
        self.subscribed = True
        self.client.listen(self.on_messages_published)
        logging.info('New user connected to chat room ' + room)


    def on_messages_published(self, message):
        """
        Callback for listening to subscribed chat room based on Redis Pub/Sub. When a new message is stored
        in the given Redis chanel this method will be called.
        """
        try:
            # Decode message
            #print 'message lenght is: ', len(message), 'and content is: ', message
            #print 'message index: ', message.index
            if 'body' in dir(message):
                m = tornado.escape.json_decode(message.body)
                # Send messages to other clients and finish connection.
                self.write_message(dict(messages=[m]))
        except :
            print 'message is:', dir(message)
            print message.__doc__
            self.on_close()
            print 'Hey, something went wrong in section on_messages_published!', sys.exc_info()

    def on_message(self, data):
        """
        Callback when new message received vie the socket.
        """
        logging.info('Received new message %r', data)
        try:
            # Parse input to message dict.
            datadecoded = tornado.escape.json_decode(data)
            what = str(datadecoded['user'])

            rightdatadecoded = what.split('"', 1)
            rightdatadecoded = str(rightdatadecoded[1]) # Workaround because #tornado.escape.json_decode(data) keeps an unwanted leading " : [W 160909 14:32:41 web:2659] #Invalid cookie signature '"ZXhhbHRpYQ==|1473424358|015bc4923b6db19a0a7c084cdc60b81952868c12'
            #                          ^There
            #coded(JSON) example message is : #{"body":"222","_xsrf":"b8f28cd1a8184afeb9296d48bb943d0a","user":"\"ZXhhbHRpYQ==|1473424358|015b#c4923b6db19a0a7c084cdc60b81952868c12"} wich seems right
            messagetype = 'regular'
            myuser = self.get_secure_cookie('user', rightdatadecoded)
            message = {
                '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                'date': time.strftime("%H:%M:%S"),
                'type': messagetype,
                'from': self.get_secure_cookie('user', rightdatadecoded),
                'body': tornado.escape.linkify(datadecoded["body"]),
            }
            notificationcheck = message['body'].split(' ')[0]
            notificationcheck = notificationcheck.split('@')
            print notificationcheck
            if message['body'].startswith('@' + notificationcheck[0]):
                listmessagebody = message['body'].split(' ')[0]
                listmessagebody = listmessagebody.split('@')
                message2 = {
                    '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                    'date': time.strftime("%H:%M:%S"),
                    'type': 'notification',
                    'from': self.get_secure_cookie('user', rightdatadecoded),
                    'body': 'You were directly mentionned',
                }
                message2_encoded = tornado.escape.json_encode(message2)
                self.write_message(message2_encoded)
                # Persistently store message in Redis.
                self.application.client.rpush(str(listmessagebody[1]), message2_encoded)
                # Publish message in Redis channel.
                self.application.client.publish(str(listmessagebody[1]), message2_encoded)
            if not message['from']:
                logging.warning("Error: Authentication missing")
                message['from'] = 'Guest'
        except Exception, err:
            # Send an error back to client.
            self.write_message({'error': 1, 'textStatus': 'Bad input data ... ' + str(err) + data})
            print sys.exc_info()
            return

        # Save message and publish in Redis.
        try:
            # Convert to JSON-literal.
            message_encoded = tornado.escape.json_encode(message)
            self.write_message(message_encoded)
            # Persistently store message in Redis.
            self.application.client.rpush(self.room, message_encoded)
            # Publish message in Redis channel.
            self.application.client.publish(self.room, message_encoded)
        except Exception, err:
            err = str(sys.exc_info()[0])
            # Send an error back to client.
            self.write_message({'error': 1, 'textStatus': 'Error writing to database: ' + str(err)})
            return
        # Send message through the socket to indicate a successful operation.
        self.write_message(message)
        return
    def on_close(self):
        """
        Callback when the socket is closed. Frees up resource related to this socket.
        """
        logging.info("socket closed, cleaning up resources now")
        if hasattr(self, 'client'):
            myuser = self.get_secure_cookie('user')
            userlist.remove(myuser)
            # Unsubscribe if not done yet.
            if self.subscribed:
                self.client.unsubscribe(self.room) #Todo: unsuscribe from username room
                self.subscribed = False
            # Disconnect connection after delay due to this issue:
            # https://github.com/evilkost/brukva/issues/25
            t = Timer(0.1, self.client.disconnect) #Todo : remove user from userlist
            t.start()



class Application(tornado.web.Application):
    """
    Main Class for this application holding everything together.
    """
    def __init__(self):

        # Handlers defining the url routing.
        handlers = [
            (r"/", MainHandler),
            (r"/room/([a-zA-Z0-9]*)$", MainHandler),
            (r"/logout", LogoutHandler),
            (r"/socket", ChatSocketHandler),
            (r"/socket/([a-zA-Z0-9]*)$", ChatSocketHandler),
            (r"/upload?([^/]+)", UploadHandler),
            (r"/uploads", MainHandler),
            (r"/save", ChatEdit),
        ]

        # Settings:
        settings = dict(
            cookie_secret = "43osdETzKXasdQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=", #BAAAD, according to some devs, this cookie secret is as important as a ssl private key, so must be put outside of code
            login_url = "/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies= True,
            autoescape="xhtml_escape",
            # Set this to your desired database name.
            db_name = 'chat',
            # apptitle used as page title in the template.
            apptitle = 'Chat example: Tornado, Redis, brukva, Websockets',
            autoreload=True,
            debug=True,
        )

        # Call super constructor.
        tornado.web.Application.__init__(self, handlers, **settings)

        # Stores user names.
        self.usernames = {}

        # Connect to Redis.
        self.client = redis_connect()


def redis_connect():
    """
    Established an asynchronous resi connection.
    """
    # Get Redis connection settings for Heroku with fallback to defaults.
    redistogo_url = os.getenv('REDISTOGO_URL', None)
    if redistogo_url == None:
        REDIS_HOST = 'localhost'
        REDIS_PORT = 6379
        REDIS_PWD = None
        REDIS_USER = None
    else:
        redis_url = redistogo_url
        redis_url = redis_url.split('redis://')[1]
        redis_url = redis_url.split('/')[0]
        REDIS_USER, redis_url = redis_url.split(':', 1)
        REDIS_PWD, redis_url = redis_url.split('@', 1)
        REDIS_HOST, REDIS_PORT = redis_url.split(':', 1)
    client = brukva.Client(host=REDIS_HOST, port=int(REDIS_PORT))#, password=REDIS_PWD)
    client.connect()
    return client



def main():
    """
    Main function to run the chat application.
    """
     # This line will setup default options.
    tornado.options.parse_command_line()
    # Create an instance of the main application.
    application = Application()
    # Start application by listening to desired port and starting IOLoop.
    application.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
