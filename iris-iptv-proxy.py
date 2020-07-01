from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import config
import iris


class HandleRequests(BaseHTTPRequestHandler):
    def _set_headers(self, response_code):
        self.send_response(response_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        # Check url path , quit if no matching /channel/{chnNumber}
        print('Request ' + self.path)
        url_split = self.path.split("/")

        # Basic Validation
        if str(url_split[1]) != "m3u" and str(url_split[1]) != "watch" and str(url_split[1]) != "epg" and (
                str(url_split[1]) != "channel" and len(url_split) != 3 or (not url_split[2].isnumeric())):
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Please try one of the following paths: \n" +
                             b"  - /channel/{channelNumber}\n" +
                             b"  - /m3u\n" +
                             b"  - /epg\n" +
                             b"  - /watch")
            return

        # Dispatching based on request
        if str(url_split[1]) == "m3u":
            self.send_response(200)
            self.send_header('Content-type', 'audio/x-mpegurl')
            self.send_header("Content-Disposition", "attachment; filename=playlist.m3u")
            self.end_headers()
            self.loadM3U()
        elif str(url_split[1]) == "channel":
            channel = url_split[2]
            self.watchChannel(channel)
        elif str(url_split[1]) == "watch":
            self.watchCurrent()
        elif str(url_split[1]) == "epg":
            self.loadEPG()

    def do_POST(self):
        self.do_GET()

    def do_PUT(self):
        self.do_GET()

    def send_resp_headers(self, resp):
        respheaders = resp.headers
        print ('Response Header')
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length', 'Content-Length']:
                print (key, respheaders[key])
                self.send_header(key, respheaders[key])
        self.end_headers()

    def watchChannel(self, channel):
        # request parsing is good, now let's switch to the right channel first
        iris.SwitchChannel(channel)
        # and now let's open the streaming
        iris.WatchCurrentStream(self)

    def watchCurrent(self):
        # and now let's open the streaming
        iris.WatchCurrentStream(self)

    def loadM3U(self):
        iris.GenerateM3U(self)

    def loadEPG(self):
        iris.GenerateEPG(self)


def run(server_class=ThreadingHTTPServer, handler_class=HandleRequests):
    server_address = ('', int(config.Config.IRIS_PROXY_PORT))
    httpd = server_class(server_address, handler_class)
    print("Starting iris-iptv-proxy on port " + config.Config.IRIS_PROXY_PORT)
    httpd.serve_forever()


if __name__ == '__main__':
    run()
