import time
import webbrowser
from pydag.services.webserver.HttpHTMLService import HttpHTMLService


def test_000():
    
    port = 8099
    html = "<h1>Hello World!</h1>"
    
    hhs = HttpHTMLService(html = html, port = port)
    hhs.install()
    hhs.start()
        
    time.sleep(3)
    
    webbrowser.open("http://localhost:8099")
    
    time.sleep(3)