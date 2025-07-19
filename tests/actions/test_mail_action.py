import configparser
from pydg.statemachine.actions.MailAction import MailAction


def test_000():
    config = configparser.ConfigParser()
    config.read("config.ini")
    ma = MailAction()
    ma.smtp_server = config["GMX"]["smtp_server"]
    ma.mail_account = config["GMX"]["watchdog_mail"]
    ma.port = int(config["GMX"]["smtp_port"])
    ma.pw = config["GMX"]["watchdog_pw"]
    ma.sender = ma.mail_account
    ma.recipient = config["GMX"]["test_mail"]
    ma.subject = "Test Mail"
    ma.body = "<h1>Header</h1><p>That's a paragraph</p>"
    
    ma.execute()
       