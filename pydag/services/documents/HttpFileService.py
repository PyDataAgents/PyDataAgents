from dataclasses import dataclass, field
from http.server import SimpleHTTPRequestHandler
import mimetypes
import os
import socketserver
import threading
from loguru import logger

from ...services.Service import Service


class CORSRequestHandler(SimpleHTTPRequestHandler):
    
    # Add or override ICS MIME type
    mimetypes.add_type("text/calendar", ".ics")

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()
    
    # Ensure that the MIME type is correct
    def guess_type(self, path):
        # Use Python's mimetypes module for all file types
        mime = mimetypes.guess_type(path)[0]
        if mime:
            return mime
        return 'application/octet-stream'
    
    # Override send_head to disable 304 logic
    def send_head(self):
        path = self.translate_path(self.path)

        if os.path.isdir(path):
            # You can expand this if you want directory listing
            return self.list_directory(path)

        if not os.path.exists(path):
            self.send_error(404, "File not found")
            return None

        ctype = self.guess_type(path)
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "Cannot open file")
            return None

        # Always send 200 OK (disable 304)
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs.st_size))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        return f


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
        self._httpd : socketserver.TCPServer = None
        
    def _on_start(self):
        threading.Thread(target=self._start_server, daemon=True).start()       
    
    def _start_server(self):
        handler = lambda *args, **kwargs: CORSRequestHandler(
            *args, directory=self.folder_path, **kwargs
        )
        self._httpd = socketserver.TCPServer(("", self.port),  handler)
        self._httpd.RequestHandlerClass.directory = str(self.folder_path)
        logger.info(f"serving {self.folder_path} at http://localhost:{self.port}")
        self._httpd.serve_forever()
        
    def _on_stop(self):
        self._httpd.shutdown()