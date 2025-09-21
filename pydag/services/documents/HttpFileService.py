from dataclasses import dataclass, field
from http.server import SimpleHTTPRequestHandler
import socketserver
import threading
from loguru import logger

from ...services.Service import Service


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


@dataclass
class HttpFileService(Service):
    """ A `Service` that provides a webserver hosting documents from `folder_path` under localhost:{`port`}

    Args:
        Service (_type_): _description_
    """
    
    folder_path : str = field(default=None, metadata={"description": ""})
    port : int = field(default=None, metadata={"description": ""})
    
    def __post_init__(self):
        super().__post_init__()
        self.httpd : socketserver.TCPServer = None
        
    def start(self):
        super().start()
        threading.Thread(target=self._start_server, daemon=True).start()       
    
    def _start_server(self):
        handler = lambda *args, **kwargs: CORSRequestHandler(
            *args, directory=self.folder_path, **kwargs
        )
        self.httpd = socketserver.TCPServer(("", self.port),  handler)
        self.httpd.RequestHandlerClass.directory = str(self.folder_path)
        logger.info(f"serving {self.folder_path} at http://localhost:{self.port}")
        self.httpd.serve_forever()
        
    def stop(self):
        self.httpd.shutdown()
        super().stop()