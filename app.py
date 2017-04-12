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
from datetime import datetime, timedelta
# Redis modules.
import brukva
# Import application modules.
from base import BaseHandler
#from login import LoginHandler
from login import LogoutHandler
import magic
#import settings as config
# Define port from command line parameter.
tornado.options.define("port", default=8888, help="run on the given port", type=int)
class ChatEdit(tornado.web.RequestHandler):
    def post(self):
        print "Placeholder"
class UploadHandler(tornado.web.RequestHandler):#tornado.web.RequestHandler):
    def post(self):#, url):
        db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB)
        cursor = db.cursor()
        uri = self.request.uri
        url = uri.split('?')
        RoomName = url[1]
        UserName = url[2]
        sql = 'SELECT RoomID FROM abcd_un WHERE RoomName = %s', [RoomName]
        cursor.execute(*sql)
        RoomID = cursor.fetchone()
        print 'roomid', RoomID
        RoomID = str(RoomID[0])
        RoomID = RoomID.decode()
        origin = self.request.protocol + "://" + self.request.host + '/room/' + url[1]# + '/' + url[3]
        file1 = self.request.files['file1'][0]
        original_fname = file1['filename']
        try: # TODO : Better use mime type!
            encoded_fname = tornado.escape.url_escape(original_fname, plus=False) #Filename must be %20 and not +
            current_location2 = self.request.protocol + "://" + self.request.host + "/static/uploads/" + 'resized-' + encoded_fname
            fname_tuple = original_fname.rsplit('.', 1)

            # if fname_tuple[1] == 'png':
            #     file_url2 = "<img src ='" + current_location2 + "'/>"
            #
            #     message2 = {
            #     '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
            #     'date': time.strftime("%Y-%m-%d %H:%M:%S"),
            #     'type': 'file',
            #     'from': UserName,
            #     'body': file_url2,
            #     }
            # elif fname_tuple[1] == 'gif':
            #     file_url2 = '<img src ="' + current_location2 + '" >'
            #     message2 = {
            #         '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
            #         'date': time.strftime("%Y-%m-%d %H:%M:%S"),
            #         'type': 'file',
            #         'from': UserName,
            #         'body': file_url2,
            #         }
            # elif fname_tuple[1] == 'jpg':
            #     #file_url2 = '<img src ="' + current_location2 + '" />'
            #
            #     message2 = {
            #         '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
            #         'date': time.strftime("%Y-%m-%d %H:%M:%S"),
            #         'type': 'file',
            #         'from': UserName,
            #         #'body': file_url2,
            #         #'body': file1,
            #         'body': current_location2
            #         }
            output_file = open("static/uploads/" + original_fname, 'wb')
            output_file.write(file1['body'])
            size = 128, 128
            output_file.close()
            mime = magic.Magic(mime=True)
            fileloc = "static/uploads/" + original_fname
            test = mime.from_file(fileloc)
            print 'mimeresult', test
            if test.startswith('image'):
                file_url2 = '<img src ="' + current_location2 + '"/>'
                message2 = {
                    '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                    'date': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'type': 'file',
                    'from': UserName,
                    'body': file_url2,
                }
                thumbwidhtsize, thumbheightsize = 128, 128
                size = thumbwidhtsize, thumbheightsize
                img = Image.open(os.path.join("static/uploads/", original_fname))
                width, height = img.size
                if width > height:  # Ratio calculation, depending on wich side is the longuest one
                    ratio = width / thumbwidhtsize
                    finalsize = width / ratio, height / ratio
                    img = img.resize((finalsize), Image.BILINEAR)
                else:
                    ratio = height / thumbheightsize
                    finalsize = width / ratio, height / ratio
                    img = img.resize((finalsize), Image.BILINEAR)
                img.save(os.path.join("static/uploads/", 'resized-' + original_fname))
            elif test.startswith('video'):
                file_url2 = '<video width="320" height="240" controls="controls">' + '<source src="'+ current_location2 + '" type="video/mp4" />' + '</video>'
                message2 = {
                    '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                    'date': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'type': 'file',
                    'from': UserName,
                    'body': file_url2,
                }
            else:
                file_url2 = ''
                message2 = ''


            redistogo_url = os.getenv('REDISTOGO_URL', None)
            REDIS_HOST = 'localhost'
            REDIS_PORT = 6379
            REDIS_PWD = None
            REDIS_USER = None
            client = brukva.Client(host=REDIS_HOST, port=int(REDIS_PORT), password=REDIS_PWD)
            client.connect()
            client.listen(self)
            current_location = self.request.protocol + '://' + self.request.host + "/static/uploads/" + encoded_fname
            file_url = 'file ' + encoded_fname + ' has been uploaded to ' + tornado.escape.linkify(current_location)
            message = {
                '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                'date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'type': 'regular',
                'from': UserName,
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
class UnPinItem(BaseHandler):
    def get(self, truc):
        origin = self.request.uri
        #print machinuri
        db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB, charset='utf8')
        cursor = db.cursor()
        BroswerSessionID = self.get_secure_cookie('SessionID')
        testunpin = origin.split('?')
        testunpin = testunpin[1].split('&')
        #testunpin = origin[0]
        #testunpin = testunpin[1]
        sql = "SELECT UserID FROM Users WHERE SessionID = %s", [BroswerSessionID]
        cursor.execute(*sql)
        UserID = cursor.fetchone()
        sql = "SELECT UserName FROM Users_info WHERE UserID = %s", [UserID]
        cursor.execute(*sql)
        UserName = cursor.fetchone()
        sql = "SELECT UserGroupID, CompanyID FROM Users_info WHERE UserID = %s", [UserID]
        cursor.execute(*sql)
        GroupandOwnerID = cursor.fetchone()
        sql = "SELECT AppID, Tableprefix, AppName FROM GroupApps WHERE GroupID = %s AND OwnerID = %s", [
            GroupandOwnerID[0],
            GroupandOwnerID[1]]
        cursor.execute(*sql)
        AppID = cursor.fetchone()
        Tablename = AppID[1] + AppID[2]
        sql = 'DELETE FROM ' + Tablename + '_PinnedItems' + ' WHERE MessageID = %s', [testunpin[0]]
        cursor.execute(*sql)
        db.commit()
        db.close()
        redirect = '/room/' + testunpin[1]
        self.redirect(redirect)
class PinItem(BaseHandler):
    def search(self, result):
         machinuri = self.request.uri
         db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB, charset='utf8')
         cursor = db.cursor()
         BroswerSessionID = self.get_secure_cookie('SessionID')
         sql = "SELECT UserID FROM Users WHERE SessionID = %s", [BroswerSessionID]
         cursor.execute(*sql)
         UserID = cursor.fetchone()
         sql = "SELECT UserName FROM Users_info WHERE UserID = %s", [UserID]
         cursor.execute(*sql)
         UserName = cursor.fetchone()
         sql = "SELECT UserGroupID, CompanyID FROM Users_info WHERE UserID = %s", [UserID]
         cursor.execute(*sql)
         GroupandOwnerID = cursor.fetchone()
         sql = "SELECT AppID, Tableprefix, AppName FROM GroupApps WHERE GroupID = %s AND OwnerID = %s", [
             GroupandOwnerID[0],
             GroupandOwnerID[1]]
         cursor.execute(*sql)
         AppID = cursor.fetchone()
         Tablename = AppID[1] + AppID[2]
         origin = machinuri.split('&', 1)
         testpin = origin[0]
         testpin = testpin.split('?')
         testpin = testpin[1]
         origin = '/room/' + origin[1]
         print 'youpiurl', testpin
         i = 0
         for message in result:
            temp = (tornado.escape.json_decode(message))
            if temp['_id'] == testpin:
                sql = 'SELECT MessageID FROM ' + Tablename + '_PinnedItems' + ' WHERE MessageID = %s', [temp[u'_id']]
                cursor.execute(*sql)
                if cursor.fetchone():
                    break
                else:
                    sql = 'INSERT INTO '  + Tablename + '_PinnedItems' + '(MessageID, Date, UserName, Body) VALUES (%s, %s, %s, %s)', [temp['_id'], temp['date'], temp['from'], temp['body']]
                    cursor.execute(*sql)
                    db.commit()
                    db.close
                break
    def on_result(self, result):
        assert result != 'n', 'Result is fucked up'
        result = '-' + str(result) #We need a negative start position for redis
        self.application.client.lrange('82c42a73b26dc109f681618ef297ef89', result, -1, self.search)
    def get(self, result, room=None):
        url = self.request.uri
        url = url.split('&')
        REDIS_HOST = 'localhost'
        REDIS_PORT = 6379
        REDIS_PWD = None
        REDIS_USER = None
        client = brukva.Client(host=REDIS_HOST, port=int(REDIS_PORT), password=REDIS_PWD)
        client.connect()
        client.listen(self)
        self.application.client.llen('82c42a73b26dc109f681618ef297ef89', self.on_result)  # Todo : Boooh, hardcoded value
        redirection = 'room/' + url[1]
        self.redirect(redirection)
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
                url = url[2].split('&')
                RoomName = url[0]
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
        global messages
        messages = []
        messages = result
    def stockb(self, result):
        global notifications
        notifications = []
        notifications = result
        self.on_conversation_found()
    def on_conversation_found(self):
        i = 0
        global messages
        global notifications
        mix = messages# + notifications
        db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB)
        cursor = db.cursor()
        AppID = '1'
        RoomNumber = '1' #Todo : Change that to non hardcoded values
        sql = "SELECT RoomID FROM abcd_un WHERE RoomNumber = %s AND AppID = %s", [RoomNumber, AppID] #Todo : Change that to non hardcoded values
        cursor.execute(*sql)
        RoomIDS = cursor.fetchall()
        temp = []
        messages = []
        notifications = []
        checktypevariable = str(type(mix))
        if checktypevariable == "<type 'tuple'>":
            messages =  'Error, you are using a non functional version of brukva, please use the one from evilkost<br><H1>Program terminated</H1>'
            self.render("test.html", messages=messages)
            sys.exit(1)
        elif checktypevariable == "<type 'list'>":
            for message in mix:
                try:
                    temp.append(tornado.escape.json_decode(message))
                except:
                    print 'faulty message: ', message
                    i += 1 #if a message is bad, added to number of bad messages
                    print 'Hey, something went wrong in message sorting!', sys.exc_info()
                    pass
                if len(temp) == len(mix) - i: # number of bad messages soustracted to total messages received to get correct total before processing
                    currentday = ''
                    try:
                        for message in temp:
                            if not 'type' in message.keys():
                                message['type'] = 'file'
                            elif message['type'] == 'notification':
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
                                    lastusername = message['from']
                                    #checkdate = messa
                                    now = datetime.now()

                                    try:
                                        #newday = ''

                                        if datetime.strptime(message['date'], "%Y-%m-%d %H:%M:%S"):
                                            splitdate = message['date'].split(' ')
                                            print splitdate
                                            if splitdate[0] != currentday:
                                                currentday = splitdate[0]
                                                print 'message date', message['date']
                                                print 'new day', currentday
                                                message['newday'] = str(splitdate[0])
                                                message['date'] = str(splitdate[1])
                                            else:
                                                print 'nope', message['date']
                                                message['date'] = str(splitdate[1])

                                    except ValueError:
                                        print 'value error, date is', message['date']
                                        pass
                                messages.append(message)
                    except:
                        print 'error is', sys.exc_info()
                        print 'faulty message: ', message
                        pass
        else:
            logging.error('Something really wrong happened')
            sys.exit(1)
        self.pagerender(messages, notifications)
        db.close()
    def pagerender(self, messages, notifications):#Renderding pages
        GroupID = '1'
        db = connect(host=config.SQLSERVER, user=config.SQLUSER, passwd=config.SQLPASS, db=config.SQLDB, charset='utf8mb4')
        cursor = db.cursor()
        BroswerSessionID = self.get_secure_cookie('SessionID')
        sql = "SELECT UserID FROM Users WHERE SessionID = %s", [BroswerSessionID]
        cursor.execute(*sql)
        UserID = cursor.fetchone()
        sql = "SELECT UserName FROM Users_info WHERE UserID = %s", [UserID]
        cursor.execute(*sql)
        UserName = cursor.fetchone()
        sql = "SELECT UserGroupID, CompanyID FROM Users_info WHERE UserID = %s", [UserID]
        cursor.execute(*sql)
        GroupandOwnerID = cursor.fetchone()
        sql = "SELECT AppID, Tableprefix, AppName FROM GroupApps WHERE GroupID = %s AND OwnerID = %s", [GroupandOwnerID[0],
                                                                                                        GroupandOwnerID[1]]
        cursor.execute(*sql)
        AppID = cursor.fetchone()
        Tablename = AppID[1] + AppID[2]
        print 'Tablename', Tablename
        sql = "SELECT RoomName FROM " + Tablename + " WHERE AppID = %s", [AppID[0]]
        cursor.execute(*sql)
        AllRoomName = cursor.fetchall()
        sql = "SELECT Csspath FROM Templates WHERE AppID = %s  AND GroupID = %s AND IsActive = '1'", (
            AppID[0], GroupID)
        cursor.execute(*sql)
        draftcsspath = cursor.fetchall()
        draftcsspath = draftcsspath[0][0].split('css', 1)
        draftcsspath = '../static/css' + draftcsspath[1]
        AappID = 1
        RoomNumber = '1'  # Todo : Change that to non hardcoded values
        sql = "SELECT RoomID FROM abcd_un WHERE RoomNumber = %s AND AppID = %s", [RoomNumber,
                                                                                  AappID]  # Todo : Change that to non hardcoded values
        cursor.execute(*sql)
        RoomIDS = cursor.fetchall()
        sql = "SELECT GroupID FROM GroupApps WHERE AppID = %s", [AppID[0]]
        cursor.execute(*sql)
        GroupIDS = cursor.fetchall()
        sql = "SELECT UserId FROM User_Groups WHERE GroupID IN %s", [GroupIDS]
        cursor.execute(*sql)
        UserIDS = cursor.fetchall()
        sql = "SELECT UserName FROM Users_info WHERE UserID IN %s", [UserIDS]
        cursor.execute(*sql)
        UserNames = cursor.fetchall()
        sql = "SELECT RoomName FROM " + Tablename + " WHERE RoomID = %s", RoomIDS
        cursor.execute(*sql)
        RoomName = cursor.fetchone()
        sql = 'SELECT * FROM ' + Tablename + '_PinnedItems ORDER BY Date ASC'
        cursor.execute(sql)
        pins = cursor.fetchall() #Pinned items won't display
        newday = ''
        pinnedcontent = self.render_string("Pinneditems.html", RoomName=RoomName[0], pins=pins, messages=messages)
        content = self.render_string("messages.html", newday=newday, RoomName=RoomName[0], messages=messages)
        notifcontent = self.render_string("notifications.html", notifications=notifications)
        self.render_default("index.html", pinnedcontent=pinnedcontent, UserNames=UserNames, RoomName=RoomName, UserName=UserName, draftcsspath=draftcsspath, userlist=userlist, AllRoomName=AllRoomName, notifcontent=notifcontent, content=content, chat=1)
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
            if 'body' in dir(message):
                m = tornado.escape.json_decode(message.body)
                # Send messages to other clients and finish connection.
                self.write_message(dict(messages=[m]))
        except :
            print 'message is:', dir(message)
            self.on_close()
            print 'Hey, something went wrong in section on_messages_published!', sys.exc_info()

    def on_message(self, data):
        """
        Callback when new message received vie the socket.
        """
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
            'date': time.strftime("%Y-%m-d %H:%M:%S"),
            'type': messagetype,
            'from': self.get_secure_cookie('user', rightdatadecoded),
            'body': tornado.escape.linkify(datadecoded["body"]),
        }
        textandsmyley = ''
        if 'emojioneemoji' in message['body']:
            Smileys = True
            templistmessagebody = datadecoded['body'].split('<')
            templistmessagebody = filter(None, templistmessagebody)
            print templistmessagebody
            Convertall = False
            for i, row in enumerate(templistmessagebody):
                if 'img' in templistmessagebody[i]:
                    templistmessagebody[i] = '<' + templistmessagebody[i]
                    print 'message number', i, templistmessagebody[i]
                    if not templistmessagebody[i].startswith('<img') or not templistmessagebody[i].endswith('>'):
                        #if not 'emojioneemoji' in templistmessagebody[i]:
                        Convertall = True
                        pos = templistmessagebody[i].find('>')
                        print 'ca passe'
                        # for i, row in enumerate(templistmessagebody):
            if Convertall == True:
                for i, row in enumerate(templistmessagebody):
                    if templistmessagebody[i].startswith('<img'):
                        pos = templistmessagebody[i].find('>')
                        templistmessagebody[i] = templistmessagebody[i][:pos] + ' width="32" ' + templistmessagebody[i][pos:]
                        print 'hihi', i
            else:
                if not datadecoded['body'].startswith('<img'):
                    print 'ok'
                    for i, row in enumerate(templistmessagebody):
                        print 'content', templistmessagebody[i]
                        if 'img' in templistmessagebody[i]:
                            print 'img found'
                            pos = templistmessagebody[i].find('>')
                            templistmessagebody[i] = templistmessagebody[i][:pos] + ' width="32" ' + templistmessagebody[i][
                                                                                                     pos:]
            textandsmyley = textandsmyley.join(templistmessagebody)
            print '1', templistmessagebody
            print '2', textandsmyley
            message = {
                '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                'date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'type': messagetype,
                'from': self.get_secure_cookie('user', rightdatadecoded),
                'body': textandsmyley,
            }
        else:
            print 'je tape dans le else'
            message = {
                '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                'date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'type': messagetype,
                'from': self.get_secure_cookie('user', rightdatadecoded),
                'body': datadecoded["body"],
            }
        notificationcheck = message['body'].split(' ')[0]
        notificationcheck = notificationcheck.split('@')
        notificationcheck = filter(None, notificationcheck)
        if '&nbsp' in notificationcheck[0]:
            notificationcheck[0].split('&nbsp')
            notificationcheck = notificationcheck[0]
        if message['body'].startswith('@' + notificationcheck[0]):
            listmessagebody = message['body'].split(' ')[0]
            listmessagebody = listmessagebody.split('@')
            message2 = {
                '_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                'date': time.strftime("%Y-%m-%d %H:%M:%S"),
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

        # Save message and publish in Redis.
        try:
            # Convert to JSON-literal.
            message_encoded = tornado.escape.json_encode(message)
            print 'message encoded', message_encoded
            self.write_message(message_encoded)
            # Persistently store message in Redis.
            self.application.client.rpush(self.room, message_encoded)
            # Publish message in Redis channel, redefining message content, to not handle the display in the javascript.
            splitdate =  message['date'].split(' ')
            message = {
                '_id': message['_id'],
                'date': splitdate[1],
                'type': messagetype,
                'from': self.get_secure_cookie('user', rightdatadecoded),
            }
            if 'Smileys' in locals():
                if Smileys == True:
                    message['body'] = textandsmyley
                    Smileys == False
            else:
                message['body'] = datadecoded["body"]
                #Smileys == False
            message_encoded = tornado.escape.json_encode(message)
            print 'message encoded step 2', message_encoded
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
            (r"/room/([^/]+)", MainHandler),
            (r"/testpin?([^/]+)", PinItem),
            (r"/testunpin?([^/]+)", UnPinItem),
            #(r"/room/([a-zA-Z0-9]*)$", MainHandler),
            #(r"/room&([^/]+)", MainHandler),
            (r"/logout", LogoutHandler),
            (r"/socket", ChatSocketHandler),
            (r"/socket/([a-zA-Z0-9]*)$", ChatSocketHandler),
            #(r"/upload?([^/]+)", UploadHandler),
            (r"/upload", UploadHandler),
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
