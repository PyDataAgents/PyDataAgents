import configparser
import time
from pathlib import Path
from pydag.agents.Agent import Agent
from pydag.agents.AgentConfig import AgentConfig
from pydag.agents.YAMLConfig import YAMLConfig
from pydag.services.documents.FolderObserveMailService import FolderObserveMailService
from pydag.statemachine.actions.MailAction import MailAction


def test_000():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    mail_action = MailAction()
    mail_action.id = "TestMailAction"
    mail_action.smtp_server = config["GMX"]["smtp_server"]
    mail_action.port = int(config["GMX"]["smtp_port"])
    mail_action.mail_account = config["GMX"]["watchdog_mail"]
    mail_action.pw = config["GMX"]["watchdog_pw"]
    mail_action.recipient = config["GMX"]["test_mail"]
    
    folder_service = FolderObserveMailService()
    folder_service.id = "TestFolderObserveMailService"
    folder_service.folder = str(Path.home() / "Downloads")
    folder_service.interval = 10 # Check every x seconds
    folder_service.skip_weekends = False
    folder_service.max_entries = 5
    folder_service.list_files = True
    folder_service.html_report = True
    folder_service.mail_action = mail_action
    
    folder_service.install()
    folder_service.start()
    
    # Wait for a while to let the service run
    time.sleep(240)  # Sleep for 5 minutes to allow the service to check the folder
    
    
def test_010():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
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
    
    agent.start_blocking()
    
    
def test_020():
    config = configparser.ConfigParser()
    config.read("config.ini")
    
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
    folder_service.interval = 10 # Check every x seconds
    folder_service.skip_weekends = False
    folder_service.max_entries = 5
    folder_service.list_files = True
    folder_service.html_report = True
    folder_service.mail_action = mail_action    
    
    agent.add_service(folder_service)
        
    gc = AgentConfig(agent)
    yc = YAMLConfig("tests\\services\\documents\\folder_observe_config.yaml")
    yc.save(gc)    
    
    agent.start_blocking()
    
    
def test_021():
    config = configparser.ConfigParser()
    config.read("config.ini")
    
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
    folder_service.interval = 20 # Check every x seconds
    folder_service.skip_weekends = True
    folder_service.max_entries = 5
    folder_service.list_files = True
    folder_service.html_report = True
    folder_service.mail_action = mail_action    
    
    agent.add_service(folder_service)
    agent.start_blocking()
    
def test_030():
    yc : YAMLConfig = YAMLConfig("C:\\Users\\jhillenb\\Downloads\\t\\pdm_folder_mail_service.yaml") 
    #yc : YAMLConfig = YAMLConfig("tests\\services\\documents\\folder_observe_config.yaml") 
    ac : AgentConfig = yc.load()    
    ag : Agent = ac.create() 
    
    ag.start_blocking() 
    
     