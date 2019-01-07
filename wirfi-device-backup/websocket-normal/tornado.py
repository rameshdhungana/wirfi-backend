from pusher import tornado


class StreamHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.set_header('Cache-Control',
        'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
        self.set_header('Connection', 'close')
        self.set_header('Content-Type', 'multipart/x-mixed-replace;boundary=-boundarydonotcross')
        while True:
            if self.get_argument('fd') == "true":
                img = cam.get_frame (True)
            else:
                img = cam.get_frame(False)
            self.write("--boundarydonotcross\n")
            self.write("Content-type: image/jpeg\r\n")
            self.write("Content-length: %s\r\n\r\n" % len(img))
            self.write(str(img))
            yield tornado.gen.Task(self.flush)