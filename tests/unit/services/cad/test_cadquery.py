import os
import cadquery as cq
import http.server
import socketserver
import threading
import webbrowser
from pathlib import Path

# Settings
FOLDER = os.path.dirname(__file__)  # <-- change this
PORT = 8000

height = 60.0
width = 80.0
thickness = 10.0
diameter = 22.0
padding = 12.0

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def run_server(folder, port):
    # Change working directory for the handler
    httpd = socketserver.TCPServer(("", port),  CORSRequestHandler)
    # Serve files from the target folder (Python 3.7+)
    httpd.RequestHandlerClass.directory = str(folder)
    print(f"Serving {folder} at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    # make the base

    result = (
        cq.Workplane("XY")
        .box(height, width, thickness)
        .faces(">Z")
        .workplane()
        .hole(diameter)
        .faces(">Z")
        .workplane()
        .rect(height - padding, width - padding, forConstruction=True)
        .vertices()
        .cboreHole(2.4, 4.4, 2.1)
        .edges("|Z")
        .fillet(2.0)
    )

    model_name = "result.step"   # or .step
    cq.exporters.export(result, FOLDER + os.sep + model_name)
    
    # Run server in a background thread so script can keep going
    thread = threading.Thread(target=run_server, args=(FOLDER, PORT), daemon=True)
    thread.start()

    # For example: open a model file in 3dviewer.net
    url = f"https://3dviewer.net/#model=http://localhost:{PORT}/{model_name}"
    print(f"Opening 3D viewer for {model_name}")
    webbrowser.open(url)

    # Keep script alive so the server stays up
    input("Press Enter to stop the server and exit...")

    #show_object(result)
