import configparser
import pytest
from pydag.nodes.utils.MailAction import MailAction


def test_000():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("GMX"):
        pytest.skip("Skipping mail action test: missing [GMX] in config.ini")
    for key in ("smtp_server", "watchdog_mail", "smtp_port", "watchdog_pw", "test_mail"):
        if not config.has_option("GMX", key):
            pytest.skip(f"Skipping mail action test: missing {key} in [GMX] of config.ini")
    
    ma = MailAction()
    ma.smtp_server = config["GMX"]["smtp_server"]
    ma.mail_account = config["GMX"]["watchdog_mail"]
    ma.port = int(config["GMX"]["smtp_port"])
    ma.pw = config["GMX"]["watchdog_pw"]
    ma.mail_account = ma.mail_account
    ma.recipients = [config["GMX"]["test_mail"]]
    ma.subject = "Test Mail"
    ma.body = "<h1>Header</h1><p>That's a paragraph</p>"
    
    ma.execute()
       
