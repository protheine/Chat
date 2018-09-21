# coding=UTF-8
# General modules.
import os, os.path
import logging
import sys
from threading import Timer
import string
import random
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
from base2 import BaseHandler
from login import LoginHandler
from login import LogoutHandler
# from app import Truc
# Define port from command line parameter.
tornado.options.define("port", default=8880, help="run on the given port", type=int)
#ioloop.IOLoop.instance().start()
class MainHandler(BaseHandler):
	"""
	Main request handler for the root path and for chat rooms.
	"""

	@tornado.web.asynchronous
	def get(self):# room=None):
		print "ho"
		# if not room:
			# self.redirect("/room/1")
			# return
		# Set chat room as instance var (should be validated).
		# self.room = str(room)
		# Get the current user.
		self._get_current_user(callback=self.on_auth)
		#content = "index.html"
		self.render("index.html")


	def on_auth(self, user):
		print "he"
		# if not user:
			#Redirect to login if not authenticated.
			# self.redirect("/login")
		#	return
		# Load 50 latest messages from this chat room.
		self.finish("succes!")
		#self.application.client.lrange(self.room, -50, -1, self.on_conversation_found)
		
class Application(tornado.web.Application):
	"""
	Main Class for this application holding everything together.
	"""
	def __init__(self):

		# Handlers defining the url routing.
		handlers = [
			(r"/login", LoginHandler),
			(r"/logout", LogoutHandler),
			(r"/", MainHandler),
		]
		print "1"

		# Settings:
		settings = dict(
			debug=True,
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

		)
		print "2"
		# Call super constructor.
		tornado.web.Application.__init__(self, handlers, **settings)
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
	print "3"

if __name__ == "__main__":
	# global fileflag
	# trouveunvrainomdevariable = UploadHandler
	main()