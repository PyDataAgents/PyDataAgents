from dataclasses import dataclass, field
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ...nodes.NodeException import NodeException
from ...services.webbrowser.BrowserAutomationService import BrowserAutomationService
from .BrowserAutomationAction import BrowserAutomationAction

@dataclass
class BrowserClickElementAction(BrowserAutomationAction):
    
    xpath : str = field(default=None, metadata={"description": "XPath definition to locate the element to get a value from"})
    wait : int = field(default=0, metadata={"description": "maximum wait time before the UI element is accessed"})
    scroll_into_view : bool = field(default=False, metadata={"description": "scrolls the element into view before attempting click"})
    force_click : bool = field(default=False, metadata={"description": "forces click via javascript"})
    wait_for_modal : str = field(default=None, metadata={"description": "waits for the modal element specified by class"})
               
    def _on_execute(self):
        if isinstance(self._service, BrowserAutomationService):
            try:                                
                if self.wait > 0:
                    w = WebDriverWait(self._service.get_driver(), self.wait)
                    element = w.until(EC.element_to_be_clickable((By.XPATH, self.xpath)))
                else:
                    element = self._service.get_driver().find_element(By.XPATH, self.xpath)
            except NoSuchElementException as nsee:
                raise NodeException(f"could not find element by xpath={self.xpath}") from nsee
            if self.scroll_into_view:
                self._service.get_driver().execute_script("arguments[0].scrollIntoView(true);", element)
            if self.wait_for_modal:
                w = WebDriverWait(self._service.get_driver(), self.wait)
                w.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.wait_for_modal)))
            if self.force_click:
                self._service.get_driver().execute_script("arguments[0].click();", element)    
            else:
                element.click()
        else:
            raise NodeException(f"{self._service.cname()} is not of type {BrowserAutomationService.cname()}")