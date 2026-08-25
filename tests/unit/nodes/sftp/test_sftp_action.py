import configparser
import os

from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.sftp.SFTPAction import SFTPAction


def test_sftp_uploads():    
    config = configparser.ConfigParser()
    config.read("config.ini")
    host = config["STRATO"]["HOST"]
    username = config["STRATO"]["USER"]
    password = config["STRATO"]["PW"]
    
    buf = DictBuffer()
    buf.install()
    
    buf.push({"local": f"{os.path.dirname(__file__) + os.sep + "file.txt"}", "remote": "/var/www/html/file.txt"})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    sa = SFTPAction(host=host, user=username, password=password, input_keys=["local", "remote"])
    sa.add_parent(lba)
    sa.install()
    
    sa.execute()
    
    print(sa.get_buffer().data())    
    assert len(sa.get_buffer().data()) == 3, "Buffer data did not contain the right amount of keys"
    