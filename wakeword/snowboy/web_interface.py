import json
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from os import curdir, sep


def MakeHandler(everloop, snowboy):
    class CustomHandler(BaseHTTPRequestHandler):
        def do_GET(self):

            path = urlparse(self.path).path
            params = parse_qs(urlparse(self.path).query)
            print("Path", path)
            print("Params", params)
    
            if path == "/modify_preset":
                self.do_modify_preset(params)
            elif path == "/remote_activation":
                self.do_remote_activate()
            else:
                sendReply = False
                if self.path.endswith(".html"):
                    mimetype='text/html'
                    sendReply = True
                elif self.path.endswith(".jpg"):
                    mimetype='image/jpg'
                    sendReply = True
                elif self.path.endswith(".gif"):
                    mimetype='image/gif'
                    sendReply = True
                elif self.path.endswith(".js"):
                    mimetype='application/javascript'
                    sendReply = True
                elif self.path.endswith(".css"):
                    mimetype='text/css'
                    sendReply = True

                if sendReply == True:
                    #Open the static file requested and send it
                    print(curdir + self.path)
                    f = open(curdir + self.path) 
                    self.send_response(200)
                    self.send_header("Content-type", mimetype)
                    self.end_headers()
                    self.wfile.write(f.read().encode())
                    f.close()

                # # Send response status code
                # self.send_response(200)

                # # Send headers
                # self.send_header("Content-type","text/html")
                # self.end_headers()
        
                # # Send message back to client
                # message = "Hello world!"

                # # Write content as utf-8 data
                # self.wfile.write(bytes(message, "utf8"))
            return


        def do_remote_activate(self):
            snowboy.remote_activation = True

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            
            self.wfile.write(bytes("Activated microphone", "utf8"))

            return


        def do_modify_preset(self, params):
            errors = []

            # Preset
            preset = params["preset"][0] if "preset" in params else ""
            if not preset:
                errors.apend("error - preset")

            # RGBW
            r = int(params["r"][0]) if "r" in params else -1
            if r < 0 or r > 255:
                errors.append("error - r")
            g = int(params["g"][0]) if "g" in params else -1
            if g < 0 or g > 255:
                errors.append("error - g")
            b = int(params["b"][0]) if "b" in params else -1
            if b < 0 or b > 255:
                errors.append("error - b")
            w = int(params["w"][0]) if "w" in params else -1
            if w < 0 or w > 255:
                errors.append("error - w")

            success = False
            if len(errors) == 0:
                success = everloop.modify_color_preset_rgbw(preset, r, g, b, w)
                if not success:
                    errors.append("error - undefined preset")
            
            response = {}
            if success:
                response["success"] = 1
                response["preset"] = preset
                response["color"] = {
                    "r": r,
                    "g": g,
                    "b": b,
                    "w": w
                }
            else:
                response["success"] = 0
                response["errors"] = errors
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(bytes(json.dumps(response, ensure_ascii=False), "utf8"))

            return

    return CustomHandler


def start(everloop, snowboy):
    print("starting server...")

    server_address = ("0.0.0.0", 8081)

    HandlerClass = MakeHandler(everloop, snowboy)
    httpd = HTTPServer(server_address, HandlerClass)
    print("running server...")


    thread = threading.Thread(target = httpd.serve_forever)
    thread.start()

    return httpd