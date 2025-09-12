from dataclasses import dataclass, field
import http
import socketserver
from loguru import logger

from ...services.Service import Service


class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


@dataclass
class HttpFileService(Service):
    
    folder_path : str = field(default=None, metadata={"description": ""})
    port : int = field(default=None, metadata={"description": ""})
    
    def __post_init__(self):
        super().__post_init__()
        self.httpd : socketserver.TCPServer = None
        
    def start(self):
        # Change working directory for the handler
        self.httpd = socketserver.TCPServer(("", self.port),  CORSRequestHandler)
        # Serve files from the target folder (Python 3.7+)
        self.httpd.RequestHandlerClass.directory = str(self.folder_path)
        logger.info(f"serving {self.folder_path} at http://localhost:{self.port}")
        self.httpd.serve_forever()