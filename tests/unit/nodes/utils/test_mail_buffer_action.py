import configparser
import pytest
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.utils.MailBufferAction import MailBufferAction


def test_000():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("GMX"):
        pytest.skip("Skipping mail buffer action test: missing [GMX] in config.ini")
    for key in ("test_mail", "smtp_server", "watchdog_mail", "smtp_port", "watchdog_pw"):
        if not config.has_option("GMX", key):
            pytest.skip(f"Skipping mail buffer action test: missing {key} in [GMX] of config.ini")
    
    buf = DictBuffer()
    buf.install()
    
    buf.push(
        {
            "recipients": config["GMX"]["test_mail"],
            "subject": "Test Mail from MailBufferAction",
            "body": "<h1>Header</h1><p>That's a paragraph from MailBufferAction</p>"
        }
    )
    buf.push(
        {
            "recipients": config["GMX"]["test_mail"],
            "subject": "2nd Test Mail from MailBufferAction",
            "body": "<h1>Header</h1><p>That's another paragraph from MailBufferAction</p>"
        }
    )
       
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    ma = MailBufferAction(
        smtp_server = config["GMX"]["smtp_server"],
        mail_account = config["GMX"]["watchdog_mail"],
        port = int(config["GMX"]["smtp_port"]),
        pw = config["GMX"]["watchdog_pw"],
        persistent=False,
        n=0
    )
    ma.add_parent(lba)
    ma.install()
    
    ma.execute()
