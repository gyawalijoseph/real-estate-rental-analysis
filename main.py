from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import json



def getRentalData(address_input):
    # Set up the driver
    driver = webdriver.Chrome()
    driver.maximize_window()

    # Navigate to the rental calculator page
    driver.get("https://www.hemlane.com/resources/rental-calculator/")

    # Fill's in address data after identifying the element
    wait = WebDriverWait(driver, 10)
    address = wait.until(EC.visibility_of_element_located((By.ID, "address")))
    address.send_keys(address_input)

    # Building Type Input
    wait = WebDriverWait(driver, 10)
    building_type = wait.until(EC.visibility_of_element_located((By.ID, "buildingType")))
    # Create a Select object and select an option by value
    select = Select(building_type)
    select.select_by_value("house")

    # Bedroom # Input
    wait = WebDriverWait(driver, 10)
    bedrooms = wait.until(EC.visibility_of_element_located((By.ID, "bedrooms")))
    # Create a Select object and select an option by value
    select = Select(bedrooms)
    select.select_by_value("3")

    # Bathroom # Input
    wait = WebDriverWait(driver, 10)
    bathrooms = wait.until(EC.visibility_of_element_located((By.ID, "bathrooms")))
    # Create a Select object and select an option by value
    select = Select(bathrooms)
    select.select_by_value("1.5+")

    # Dummy Rental Charge Input
    wait = WebDriverWait(driver, 10)
    rentalInput = wait.until(EC.visibility_of_element_located((By.ID, "rent")))
    rentalInput.send_keys("1000")

    # Button select
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div/div/div/div[4]/section/div[1]/div/form/div[6]/button')))
    button.click()


    # second portion fetching the rental data
    wait = WebDriverWait(driver, 10)
    price_elemnt = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div/div/div/div[4]/section/div[1]/div/div/div[1]/div[2]/div[2]/div/div[1]/p[2]')))
    average_price = price_elemnt.text
    print(f"Average Price: {average_price}")

    data = {
        "Address": f"{address_input}",
        "Average Rent": f"{average_price}"
    }

    # Open a file for writing
    with open("report.json", "w") as outfile: 
        # Write the data to the file in JSON format
        json.dump(data, outfile, indent=4)
    
    input("Press Enter to close the browser...")
    driver.quit()

address = ""

getRentalData(address)





