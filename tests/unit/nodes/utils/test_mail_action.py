import configparser
from pydag.nodes.utils.MailAction import MailAction


def test_000():
    config = configparser.ConfigParser()
    config.read("config.ini")
    
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
       