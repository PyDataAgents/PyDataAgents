from selenium import webdriver

def test_000():
    
    driver = webdriver.Edge()
    driver.get("https://selenium.dev")
    driver.quit()    