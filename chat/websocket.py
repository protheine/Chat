import tornado.websocket
class websockettest(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True #Not secure!
    def open(self):
        print('chaussette')
    def on_message(self, message):
        print('message reçu')
        try:
            message = tornado.escape.json_decode(message)
        except:
            print('is this really json?')
        print(message['message']['body'])