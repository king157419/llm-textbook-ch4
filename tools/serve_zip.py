"""在 127.0.0.1:8765 上临时提供项目 zip（带 CORS 头），供浏览器内的 Overleaf 页面读取后上传。"""
import http.server, sys

ZIP = sys.argv[1]

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        data = open(ZIP, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Access-Control-Allow-Origin", "http://localhost:8088")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

http.server.HTTPServer(("127.0.0.1", 8765), H).serve_forever()
