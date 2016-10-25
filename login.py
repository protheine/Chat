# coding=UTF-8
from MySQLdb import *
import settings
# Tornado modules.
import tornado.web
import tornado.escape

# Import application modules.
from base2 import BaseHandler

# General modules.
import logging

class LoginHandler(BaseHandler):
	"""
	Handler for logins with Google Open ID / OAuth
	http://www.tornadoweb.org/documentation/auth.html#google
	"""
	@tornado.web.asynchronous
	def get(self):
		logging.warning("Hell yeah right in the place!")
		if self.get_argument("start_direct_auth", None):
			# Get form inputs.
			try:
				user = dict()
				user["email"] = self.get_argument("email", default="")
				user["password"] = self.get_argument("password", default="")
			except:
				# Send an error back to client.
				content = "<p>There was an input error. Fill in all fields!</p>"
				self.render_default("index.html", content=content)
			# If user has not filled in all fields.
			if not user["email"] or not user["password"]:
				content = ('<h2>2. Direct Login</h2>' 
				+ '<p>Fill in both fields!</p>'
				+ '<form class="form-inline" action="/login" method="get"> '
				+ '<input type="hidden" name="start_direct_auth" value="1">'
				+ '<input class="form-control" type="text" name="email" placeholder="Your email" value="' + str(user["email"]) + '"> '
				+ '<input class="form-control" type="text" name="password" placeholder="Password" value="' + str(user["password"]) + '"> '
				+ '<input type="submit" class="btn btn-default" value="Sign in">'
				+ '</form>')
				#self.render_default("index.html", content=content)
			# All data given. Log user in!
			else:
				self._on_auth(user)
		else:
			# Logins.
			content = '<div class="page-header"><h1>Login</h1></div>'
			content += ('<h2>1. Google Login</h2>' 
			+ '<form action="/login" method="get">' 
			+ '<input type="hidden" name="start_google_oauth" value="1">'
			+ '<input type="submit" class="btn" value="Sign in with Google">'
			+ '</form>')
			content += ('<h2>2. Direct Login</h2>' 
			+ '<form class="form-inline" action="/login" method="get"> '
			+ '<input type="hidden" name="start_direct_auth" value="1">'
			+ '<input class="form-control" type="text" name="email" placeholder="Your Email"> '
			+ '<input class="form-control" type="text" name="password" placeholder="Password"> '
			+ '<input type="submit" class="btn btn-default" value="Sign in">'
			+ '</form>')
			self.render_default("index.html", content=content)
	def _on_auth(self, user):
		"""
		Callback for third party authentication (last step).
		"""
		print user
		if not user:
			print "qu'est ce que je fout la dedans"
			content = ('<div class="page-header"><h1>Login</h1></div>'
			+ '<div class="alert alert-error">' 
			+ '<button class="close" data-dismiss="alert">×</button>'
			+ '<h3>Authentication failed</h3>'
			+ '<p>This might be due to a problem in Tornados GoogleMixin.</p>'
			+ '</div>')
			self.render_default("index.html", content=content)
			return None
			return None
		db = connect (host = settings.SQLSERVER, user = settings.SQLUSER, passwd = settings.SQLPASS, db = settings.SQLDB)
		cursor = db.cursor ()
		#SQL time
		print (user["email"])
		username = str(user["email"])
		print type(username)
		print username
		sql = ("SELECT UserID FROM Users_info WHERE UserName = '%s'") % username
		print type(sql)
		print sql
		cursor.execute(sql)
		print "1"
		useridresult = cursor.fetchone()
		print "2"
		print useridresult
		if useridresult is None:
			content = "Bad username or password, try again!"
			self.render_default("index.html", content=content)
		else:	
			print "je fait le if quand meme -_-"
			cursor.execute ("SELECT Password FROM Users WHERE UserID = %s", (useridresult))
			result = cursor.fetchone()
			result = str(result[0])
			
		#self.finish()		
		# @todo: Validate user data.
		# Save user when authentication was successful.
			#@todo: We should check if email is given even though we can assume.
		try:
			if result == "null" or not result:
				# If user does not exist, create a new entry.
				self.finish("Bad password or inexistent user")
				print "3"
			else:
				print "USSSEEEEEEEER" + username
				self.application.client.set("user:" + user["email"], tornado.escape.json_encode(username))
				# Update existing user.
				# @todo: Should use $set to update only needed attributes?
				# self.application.client.set("user:" + user["email"], tornado.escape.json_encode(user))
				# dbuser = tornado.escape.json_decode(result)
				# dbuser.update(user)
				# user = dbuser
				self.set_secure_cookie("user", username)
				self.application.usernames[user["email"]] = username or user.get(username)#user.get("name") or 
				print "4"
				print result
				print user["password"]
				if user["password"] == result:
					print "4.5"
					self.redirect("/room/1")
					#self.finish()
					print "5"
				# Save user id in cookie.
					# self.set_secure_cookie("user", user["email"])
					# self.application.usernames[user["email"]] = user.get("name") or user["email"]
				#Closed client connection
				# if self.request.connection.stream.closed():
					# logging.warning("Waiter disappeared")
					# return
				# self.redirect("/")
				# dbuser = self.application.client.get("user:" + user["email"], on_user_find)
				print "6"
		except:
			content = "Bad password or inexistent user" #Normalize this please, or if texte are different there is a way to know if the user exists
			self.render_default("index.html", content=content)
class LogoutHandler(BaseHandler):
	def get(self):
		self.clear_cookie('user')
		self.redirect("/")