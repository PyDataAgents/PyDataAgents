import configparser
import time
from pathlib import Path
import pytest
from pydag.services.documents.FolderObserveMailService import FolderObserveMailService
from pydag.nodes.utils.MailAction import MailAction


def test_000():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("GMX"):
        pytest.skip("Skipping folder observe mail service test: missing [GMX] in config.ini")
    for key in ("smtp_server", "smtp_port", "watchdog_mail", "watchdog_pw", "test_mail"):
        if not config.has_option("GMX", key):
            pytest.skip(f"Skipping folder observe mail service test: missing {key} in [GMX] of config.ini")
    
    mail_action = MailAction()
    mail_action.id = "TestMailAction"
    mail_action.smtp_server = config["GMX"]["smtp_server"]
    mail_action.port = int(config["GMX"]["smtp_port"])
    mail_action.mail_account = config["GMX"]["watchdog_mail"]
    mail_action.pw = config["GMX"]["watchdog_pw"]
    mail_action.recipients = [config["GMX"]["test_mail"]]
    
    folder_service = FolderObserveMailService()
    folder_service.id = "TestFolderObserveMailService"
    folder_service.folder = str(Path.home() / "Downloads")
    folder_service.observing_time = 10 # Check every x seconds
    folder_service.skip_weekends = False
    folder_service.max_entries = 5
    folder_service.list_files = True
    folder_service.html_report = True
    folder_service.mail_action = mail_action
    
    folder_service.install()
    folder_service.start()
    
    # Wait for a while to let the service run
    time.sleep(10)  # Sleep for x seconds to allow the service to check the folder
    
    folder_service.stop()
    
    
    
def test_040():
    
    path = __file__    
    print(Path(path).suffix.lower())
     
