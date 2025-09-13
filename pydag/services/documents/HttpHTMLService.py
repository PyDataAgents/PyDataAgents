from dataclasses import dataclass, field
import http
import socketserver
import threading
from loguru import logger

from ...services.Service import Service

def make_handler(html_bytes):
    class HTMLHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_bytes)
    return HTMLHandler

@dataclass
class HttpHTMLService(Service):
    
    port : int = field(default=8099, metadata={"description": ""})
    html : str = field(default="<h1>Hello World!</h1>", metadata={"description": "html to show on the website"})
    
    def __post_init__(self):
        super().__post_init__()
        self.httpd : socketserver.TCPServer = None
        
    def start(self):
        super().start()
        threading.Thread(target=self._start_server, daemon=True).start()
    
    def stop(self):        
        self.httpd.shutdown()
        self.httpd = None
        super().stop()
        
    def _start_server(self):
        handler_class = make_handler(self.html)
        with socketserver.TCPServer(("", self.port), handler_class) as self.httpd:
            logger.info(f"serving html at http://localhost:{self.port}")
            self.httpd.serve_forever()