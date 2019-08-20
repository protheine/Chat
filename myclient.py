from ws4py.client import WebSocketBaseClient
from ws4py.manager import WebSocketManager
from ws4py import format_addresses, configure_logger
import tornado.escape
import random
import string
logger = configure_logger()

m = WebSocketManager()

class EchoClient(WebSocketBaseClient):
	def handshake_ok(self):
		logger.info("Opening %s" % format_addresses(self))
		m.add(self)

	def received_message(self, msg):
		logger.info(str(msg))

if __name__ == '__main__':
	import time

	try:
		#m.start()
		# for i in range(500):
		myclient = EchoClient('ws://192.168.0.92:8888/socket/1')
		myclient.connect()
		#message = 'body:"aaa","_xsrf":"be232ac58b72481ebb67fba3d908891b","user":"\\"ZXhhbHRpYUBnbWFpbC5jb20=|1472937969|36a2b09780307c5bfc265cea3a26603cab9ff4b7"'
		message2 = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
		message = {
		'_xsrf':'b8f28cd1a8184afeb9296d48bb943d0a',
		#'_id': ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
		'user':'''"\\"bm9Abm8ubm8=|1472806937|457287f0b5247021ec27abee60048d6e1c192169"''',#self.get_secure_cookie('user', str(datadecoded['user'])),
		'body': tornado.escape.linkify("aaaa"),#datadecoded["body"]),
		}
		# if not message['from']:
			# logging.warning("Error: Authentication missing")
			# message['from'] = 'Guest'
		message_encoded = tornado.escape.json_encode(message)
		myclient.send(message_encoded)
		logger.info("client connected")#%d clients are connected" % i)
		while True:
			for ws in m.websockets.itervalues():
				if not ws.terminated:
					time.sleep(3)
					ws.close()		
			else:
				break
			time.sleep(3)
		# m.close_all()
		# m.stop()
		# m.join()
	except KeyboardInterrupt:
		m.close_all()
		m.stop()
		m.join()
