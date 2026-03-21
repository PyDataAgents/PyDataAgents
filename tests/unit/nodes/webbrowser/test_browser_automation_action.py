import time
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.browser.BrowserClickElementAction import BrowserClickElementAction
from pydag.nodes.browser.BrowserGetElementAction import BrowserGetElementAction
from pydag.nodes.browser.BrowserSetElementAction import BrowserSetElementAction
from pydag.nodes.browser.BrowserUrlNavigateAction import BrowserUrlNavigateAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.services.browser.BrowserAutomationService import BrowserAutomationService


def test_url_navigate():
    
    bas = BrowserAutomationService()
    bas.install()
    bas.start()
    
    buna = BrowserUrlNavigateAction(url="https://www.selenium.dev/")
    buna.set_service(bas)
    buna.install()
    buna.execute()
    buna.uninstall()
    
    time.sleep(3)
    
    bas.stop()
    bas.uninstall()
    
def test_link_click():
    
    bas = BrowserAutomationService()
    bas.install()
    bas.start()
    
    buna = BrowserUrlNavigateAction(url="https://www.selenium.dev/")
    buna.set_service(bas)
    buna.install()
    buna.execute()
    
    time.sleep(3)
    
    bcea = BrowserClickElementAction(xpath="(//div[@class='selenium-button-container'])[1]")
    bcea.set_service(bas)
    bcea.install()
    bcea.execute()
        
    time.sleep(3)
        
    buna.uninstall()
    bcea.uninstall()
    
    bas.stop()
    bas.uninstall()
    
    
def test_get_element_texts():
    
    bas = BrowserAutomationService()
    bas.install()
    bas.start()
    
    buna = BrowserUrlNavigateAction(url="https://www.selenium.dev/")
    buna.set_service(bas)
    buna.install()
    buna.execute()
    
    time.sleep(3)
    
    bgea = BrowserGetElementAction(xpath="//*[contains(@class, 'h3')]")
    bgea.set_service(bas)
    bgea.install()
    bgea.execute()
    
    print(bgea.get_buffer().data())
        
    time.sleep(3)
        
    buna.uninstall()
    bgea.uninstall()
    
    bas.stop()
    bas.uninstall()
    
def test_get_element_attributes():
    
    bas = BrowserAutomationService()
    bas.install()
    bas.start()
    
    buna = BrowserUrlNavigateAction(url="https://www.selenium.dev/")
    buna.set_service(bas)
    buna.install()
    buna.execute()
    
    time.sleep(3)
    
    bgea = BrowserGetElementAction(xpath="//a", attribute="href")
    bgea.set_service(bas)
    bgea.install()
    bgea.execute()
    
    print(bgea.get_buffer().data())
        
    time.sleep(3)
        
    buna.uninstall()
    bgea.uninstall()
    
    bas.stop()
    bas.uninstall()
    
def test_set_element_action():
    
    bas = BrowserAutomationService()
    bas.install()
    bas.start()
    
    buna = BrowserUrlNavigateAction(url="https://artoftesting.com/samplesiteforselenium/")
    buna.set_service(bas)
    buna.install()
    buna.execute()
    
    buf = ListBuffer(capacity=1)
    buf.install()
    buf.push("2+2")
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
        
    bsea = BrowserSetElementAction(xpath="//*[@id='fname']")
    bsea.set_service(bas)
    bsea.add_parent(lba)
    bsea.install()
    bsea.execute()
    
    bgea = BrowserGetElementAction(xpath="//*[@id='fname']", attribute="value")
    bgea.set_service(bas)
    bgea.install()
    bgea.execute()
    
    print(bgea.get_buffer().data())
    
    