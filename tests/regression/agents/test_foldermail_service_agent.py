import configparser
from pathlib import Path
import pytest

from pydag.agents.Agent import Agent
from pydag.agents.AgentConfig import AgentConfig
from pydag.agents.YAMLConfig import YAMLConfig
from pydag.nodes.utils.MailAction import MailAction
from pydag.services.documents.FolderObserveMailService import FolderObserveMailService


def test_000():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("AST"):
        pytest.skip("Skipping folder mail regression test: missing [AST] in config.ini")
    for key in ("SMTP_HOST", "SMTP_PORT", "SMTP_ACCOUNT", "MY_MAIL"):
        if not config.has_option("AST", key):
            pytest.skip(f"Skipping folder mail regression test: missing {key} in [AST] of config.ini")
    
    agent = Agent()
        
    mail_action = MailAction()
    mail_action.id = "TestMailAction"
    mail_action.smtp_server = config["AST"]["SMTP_HOST"]
    mail_action.port = int(config["AST"]["SMTP_PORT"])
    mail_action.mail_account = config["AST"]["SMTP_ACCOUNT"]
    mail_action.recipients = [config["AST"]["MY_MAIL"]]
    mail_action.tls = False
    
    folder_service = FolderObserveMailService()
    folder_service.id = "TestFolderObserveMailService"
    folder_service.folder = str(Path.home() / "Downloads")
    folder_service.interval = 10 # Check every x seconds
    folder_service.skip_weekends = False
    folder_service.max_entries = 5
    folder_service.list_files = True
    folder_service.html_report = True
    folder_service.mail_action = mail_action
    
    agent.add_service(folder_service)
        
    gc = AgentConfig(agent)
    yc = YAMLConfig(str(Path.home() / "Downloads" / "t" / "folder_observe_config.yaml"))
    yc.save(gc)    
    
    agent.release()
    
    
def test_020():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("GMX"):
        pytest.skip("Skipping folder mail regression test: missing [GMX] in config.ini")
    for key in ("smtp_server", "smtp_port", "watchdog_mail", "watchdog_pw", "test_mail"):
        if not config.has_option("GMX", key):
            pytest.skip(f"Skipping folder mail regression test: missing {key} in [GMX] of config.ini")
    
    agent = Agent()
    
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
    
    agent.add_service(folder_service)
        
    gc = AgentConfig(agent)
    yc = YAMLConfig("tests\\services\\documents\\folder_observe_config.yaml")
    yc.save(gc)    
    
    agent.release()
    
    
def test_021():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("GMX"):
        pytest.skip("Skipping folder mail regression test: missing [GMX] in config.ini")
    for key in ("smtp_server", "smtp_port", "watchdog_mail", "watchdog_pw", "test_mail"):
        if not config.has_option("GMX", key):
            pytest.skip(f"Skipping folder mail regression test: missing {key} in [GMX] of config.ini")
    
    agent = Agent()
    
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
    folder_service.observing_time = 20 # Check every x seconds
    folder_service.skip_weekends = True
    folder_service.max_entries = 5
    folder_service.list_files = True
    folder_service.html_report = True
    folder_service.mail_action = mail_action    
    
    agent.add_service(folder_service)
    agent.release()
    
def test_030():
    yc : YAMLConfig = YAMLConfig("C:\\Users\\jhillenb\\Downloads\\t\\pdm_folder_mail_service.yaml") 
    #yc : YAMLConfig = YAMLConfig("tests\\services\\documents\\folder_observe_config.yaml") 
    ac : AgentConfig = yc.load()    
    ag : Agent = ac.create()
    ag.release() 
