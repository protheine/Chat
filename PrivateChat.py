from MySQLdb import *
#import settings as config
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
#from login import LogoutHandler
import magic
from itertools import chain
from app import BaseHandler
dictconf = {}
with open('./settings.cfg', 'r') as configfile:
    for line in configfile:
        if '#' not in line:
            line = line.strip()
            line = line.replace(' ', '')
            line = line.split('=')
            dictconf[line[0]] = line[1]
class PrivateRoom(BaseHandler):
    def post(self, RoomName):
        db = connect(host=dictconf['SQLSERVER'], user=dictconf['SQLUSER'], passwd=dictconf['SQLPASS'], db=dictconf['SQLDB'], charset='utf8mb4')
        cursor = db.cursor()
        uri = self.request.uri
        url = uri.split('/')
        print 'url, 1', url
        url[2] = url[2].split('&')
        print len(url)
        RoomName = url[2][0]
        print 'RoomName in post1', RoomName
        RoomName = tornado.escape.url_unescape(RoomName)
        sql = 'SELECT RoomID FROM abcd_un_PrivateChatRooms WHERE RoomName = %s', [RoomName]
        cursor.execute(*sql)
        RoomID = cursor.fetchone()
        print 'RoomID', RoomID
        RoomID = str(RoomID[0])
        RoomID = RoomID.decode()
        fullurl = 'ws://' + self.request.host + '/socket/' + RoomID
        db.close()
        wsurl = {
            'url': fullurl,
        }
        wsurl_encoded = tornado.escape.json_encode(wsurl)
        print 'wsurl', wsurl
        self.write(wsurl_encoded)
    @tornado.web.asynchronous
    def get(self, room=None):
        print 'xsrf token', self.xsrf_token #DO NOT REMOVE doing that is enough to set the xsrf cookie, required by javascript to post, strange, i know
        url = self.request.uri
        url = url.split('/')
        RoomName = url[2]
        db = connect(host=dictconf['SQLSERVER'], user=dictconf['SQLUSER'], passwd=dictconf['SQLPASS'], db=dictconf['SQLDB'], charset='utf8mb4')
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
        db = connect(host=dictconf['SQLSERVER'], user=dictconf['SQLUSER'], passwd=dictconf['SQLPASS'], db=dictconf['SQLDB'], charset='utf8mb4')
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
                RoomName = tornado.escape.url_unescape(RoomName)
                print 'RoomName', RoomName
                sql = 'SELECT RoomID FROM abcd_un_PrivateChatRooms WHERE RoomName = %s', ['@'+ user]
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
        print 'private rooms def'
        url = self.request.uri
        url = url.split('/')
        # #errormessage = 'Noneonconvfound'
        # if 'errormessage' not in globals():
        #     global errormessage
        #     errormessage = 'None'
        i = 0
        global messages
        global notifications
        mix = messages# + notifications
        db = connect(host=dictconf['SQLSERVER'], user=dictconf['SQLUSER'], passwd=dictconf['SQLPASS'], db=dictconf['SQLDB'], charset='utf8mb4')
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

                                    if splitdate[0] != currentday:
                                        currentday = splitdate[0]
                                        message['newday'] = str(splitdate[0])
                                        message['date'] = str(splitdate[1])
                                    else:
                                        message['date'] = str(splitdate[1])
                                else:
                                    print 'date', message['date']
                            except ValueError:
                                print 'value error, date is', message['date']
                                pass
                            if message['from'] == url[2] or message['from'] == 'Exaltia':
                                print 'url[2]', url[2]
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
        uri = self.request.uri
        print 'mon uri est', uri
        try:
            url = uri.split('errorcode=')
            errorcode = url[len(url) -1]
        except:
            errorcode = '0'
        if errorcode == '100':
            errormessage = 'File not uploaded, File name already exist.'
        else:
            errormessage = 'None'
        GroupID = '1'
        db = connect(host=dictconf['SQLSERVER'], user=dictconf['SQLUSER'], passwd=dictconf['SQLPASS'], db=dictconf['SQLDB'], charset='utf8mb4')
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
        sql = "SELECT RoomName FROM " + Tablename + " WHERE AppID = %s AND ISFileRoom = 0", [AppID[0]]
        cursor.execute(*sql)
        AllRoomName = cursor.fetchall()
        sql = "SELECT Csspath FROM Templates WHERE AppID = %s  AND GroupID = %s AND IsActive = '1'", (
            AppID[0], GroupID)
        cursor.execute(*sql)
        draftcsspath = cursor.fetchall()
        draftcsspath = draftcsspath[0][0].split('css', 1)
        draftcsspath = '../static/css' + draftcsspath[1]
        #AappID = 1
        #RoomNumber = '1'  # Todo : Change that to non hardcoded values

        #sql = "SELECT RoomID FROM abcd_un WHERE RoomNumber = %s AND AppID = %s", [RoomNumber, AappID]  # Todo : Change that to non hardcoded values
        uri = uri.split('/')
        uri[2] = tornado.escape.url_unescape(uri[2])
        sql = "SELECT RoomID FROM " + Tablename + ' WHERE RoomName = %s', [uri[2]]
        cursor.execute(*sql)
        RoomIDS = cursor.fetchall()
        print 'RoomIDs', RoomIDS
        print 'RoomName?', uri[2]
        sql = "SELECT GroupID FROM GroupApps WHERE AppID = %s", [AppID[0]]
        cursor.execute(*sql)
        GroupIDS = cursor.fetchall()
        sql = "SELECT UserId FROM User_Groups WHERE GroupID IN %s", [GroupIDS]
        cursor.execute(*sql)
        UserIDS = cursor.fetchall()
        sql = "SELECT UserName FROM Users_info WHERE UserID IN %s", [UserIDS]
        cursor.execute(*sql)
        UserNames = cursor.fetchall()
        #sql = "SELECT RoomName FROM " + Tablename + " WHERE RoomID = %s", RoomIDS
        #cursor.execute(*sql)
        #RoomName = cursor.fetchone()
        sql = 'SELECT * FROM ' + Tablename + '_PinnedItems ORDER BY Date ASC'
        cursor.execute(sql)
        pins = cursor.fetchall() #Pinned items won't display
        newday = ''
        sql = 'SELECT * FROM ' + Tablename + '_Files WHERE ISAttached = 1 AND RoomName = %s', [uri[2]]
        cursor.execute(*sql)
        Filespath = cursor.fetchall()
        pinnedcontent = self.render_string("Pinneditems.html", RoomName=uri[2], pins=pins, messages=messages)
        content = self.render_string("messages.html", newday=newday, RoomName=uri[2], messages=messages)
        notifcontent = self.render_string("notifications.html", notifications=notifications)
        self.render_default("index.html", errormessage=errormessage, Filespath=Filespath, pinnedcontent=pinnedcontent, UserNames=UserNames, RoomName=uri[2], UserName=UserName, draftcsspath=draftcsspath, userlist=userlist, AllRoomName=AllRoomName, notifcontent=notifcontent, content=content, chat=1)
        db.close()
        print 'end?'