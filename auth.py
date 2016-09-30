# coding=UTF-8

# Tornado modules.
import tornado.web
import tornado.escape
from MySQLdb import *
# Import application modules.
from base import BaseHandler

# General modules.
import logging
import settings #Todo : Reading regular file instead


class LoginHandler(BaseHandler, tornado.auth.GoogleMixin):
    """
    Handler for logins with Google Open ID / OAuth
    http://www.tornadoweb.org/documentation/auth.html#google
    """
    @tornado.web.asynchronous
    def get(self):
            if not user["email"] or not user["name"]
				self.redirect("/login") # TODO: Make this hard coded value fecthable from db for flexible configuration
            # All data given. Log user in!
            else:
                self._on_auth(user)
    def _on_auth(self, user):
		db = connect (host = settings.SQLSERVER, user = settings.SQLUSER, passwd = settings.SQLPASS, db = settings.SQLDB)
		cursor = db.cursor ()
        """
        Callback for third party authentication (last step).
        """
        if not user:
			self.redirect("/login") # TODO: Make this hard coded value fecthable from db for flexible configuration
		else:
			try:
				print "est ce que je passe par la?"
				username = str(user["email"])
				sql = ("SELECT UserID FROM Users_info WHERE UserName = '%s'") % username
				cursor.execute(sql)
				useridresult = cursor.fetchone()
				cursor.execute ("SELECT SessionID FROM Users WHERE UserID = %s", (useridresult))
				SQLSessionID = cursor.fetchone()
				BroswerSessionID = self.get_secure_cookie('SessionID')
				print BroswerSessionID
				if SQLSessionID == BroswerSessionID:
					print "je redirige"
					self.redirect("/room/1") # TODO: Make this hard coded value fecthable from db for flexible configuration
				else:
					"pourquoi passer dans le else?"
					self.redirect("/login") # TODO: Make this hard coded value fecthable from db for flexible configuration
			except:
				print "what? un except??"
				self.redirect("/login") # TODO: Make this hard coded value fecthable from db for flexible configuration
            return None
        
        # @todo: Validate user data.
        # Save user when authentication was successful.
        def on_user_find(result, user=user):
            #@todo: We should check if email is given even though we can assume.
			print "on_user_find"
            if result == "null" or not result:
                # If user does not exist, create a new entry.
                self.application.client.set("user:" + user["email"], tornado.escape.json_encode(user))
            else:
                # Update existing user.
                # @todo: Should use $set to update only needed attributes?
                dbuser = tornado.escape.json_decode(result)
                dbuser.update(user)
                user = dbuser
                self.application.client.set("user:" + user["email"], tornado.escape.json_encode(user))
            
            # Save user id in cookie.
            self.set_secure_cookie("user", user["email"])
            self.application.usernames[user["email"]] = user.get("name") or user["email"]
            # Closed client connection
            if self.request.connection.stream.closed():
                logging.warning("Waiter disappeared")
                return
            self.redirect("/")
        
        dbuser = self.application.client.get("user:" + user["email"], on_user_find)
        
        


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user')
		url = "192.168.0.92"
        self.redirect(url, permanent=true) # TODO: Make this hard coded value fecthable from db for flexible configuration
		self.finish()
        
    
