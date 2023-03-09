from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import json
import re

def getPropertyTax(url):
    # Set up the driver
    driver = webdriver.Chrome()
    driver.maximize_window()

    # Navigate to the rental calculator page
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    property_tax_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/div[2]/section[10]/aotf-tax-history/div/aotf-multi-column-list/div[2]/table/tbody/tr[1]/td[2]')))
    property_tax = property_tax_element.get_attribute("textContent")

    match = re.search(r'\$(\d[\d,]*\.\d+)', property_tax)
    if match:
        property_tax = match.group(1).replace(',', '')
        print(property_tax)
    else:
        print("No match found")

    print(f"Property tax: {property_tax}")


    input("Press Enter to close the browser...")
    driver.quit()

url = ""
getPropertyTax(url)