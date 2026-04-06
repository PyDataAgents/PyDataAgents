import os
import time
import webbrowser

from pydag.services.webserver.WebService import WebService


def test_000():
    root = os.path.dirname(__file__) + os.sep + "srv"
    ws = WebService(root=root)
    ws.install()
    ws.start()
    time.sleep(3)
    webbrowser.open(f"localhost:{ws.port}")
    ws.stop()
    ws.uninstall()