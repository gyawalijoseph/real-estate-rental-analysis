from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import json
import re
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from bs4 import BeautifulSoup






def getInformation(url):
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
        # print(property_tax)
    else:
        print("No match found")

    property_tax = round(float(property_tax) / 12, 2)


    wait = WebDriverWait(driver, 10)
    address_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/div[2]/aotf-property-header/section/address/p[1]')))
    address = address_element.get_attribute("textContent")

    address2_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/div[2]/aotf-property-header/section/address/p[2]')))
    address2 = address2_element.get_attribute("textContent")

    finalAddress = address + " " + address2


    wait = WebDriverWait(driver, 10)
    price_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/div[2]/section[1]/div/div/div[2]/aotf-property-detail-card/div/div/div/div[1]/p')))
    price = price_element.get_attribute("textContent")
    price = int(price.replace('$', '').replace(',',''))


    wait = WebDriverWait(driver, 10)
    price_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/div[2]/section[1]/div/div/div[2]/aotf-property-detail-card/div/div/div/div[1]/p')))
    price = price_element.get_attribute("textContent")
    price = int(price.replace('$', '').replace(',',''))
    

    # print(f"Address: {finalAddress}")
    # print(f"Property tax: {property_tax}")

    data = {
        "Address": finalAddress,
        "Price": price,
        "PropertyTax": property_tax
    }


    # wait = WebDriverWait(driver, 10)
    # hoa_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content"]/div[2]/section[1]/div/div/aotf-feature-list/ul/li[8]/dl')))
    # hoa = hoa_element.get_attribute("textContent").split(":")
    # data = {}
    # if hoa[0] == 'HOA Fee':
    #     hoa_data = hoa[1].split(" ")
    #     hoa_data[0] = hoa_data[0][1:]
    #     if hoa_data[1] == "Quarterly":
    #         hoa_data[0] = int(hoa_data[0])/3
    #     elif hoa_data[1] == "Annually":
    #         hoa_data[0] = int(hoa_data[0])/12
    # data["HOA"] = round(hoa_data[0],2)

    getRentalData(finalAddress, data)


    # input("Press Enter to close the browser...")
    driver.quit()


def getRentalData(address_input, data):
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
    price_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div/div/div/div[4]/section/div[1]/div/div/div[1]/div[2]/div[2]/div/div[1]/p[2]')))
    average_price = price_element.text
    average_price = int(average_price.replace("$", "").replace(",", ""))
    data["AverageRent"] = average_price
    print(data)
    # Open a file for writing
    with open("report.json", "w") as outfile: 
        # Write the data to the file in JSON format
        json.dump(data, outfile, indent=4)
    
    # input("Press Enter to close the browser...")
    driver.quit()


def createNewExcelSheet():
    # Set up Google Drive API credentials
    creds = service_account.Credentials.from_service_account_file('google_drive_credentials.json')

    # Set up Google Sheets API client
    service = build('drive', 'v3', credentials=creds)

    # Define the ID of the spreadsheet you want to copy
    spreadsheet_id = '1_sFTLladwl0VLvP28nyz4YB2PhK0RbezY8EHKiPWmxs'

    # Open the JSON file and load its contents into a variable
    with open('report.json', 'r') as file:
        data = json.load(file)

    

    # Define the name and parent folder ID for the copied spreadsheet
    copy_title = data['Address'] + ' Breakdown'
    parent_folder_id = '13wmMEtXOJjrXOI9n_79HZWHk8OUPqKs5'

    # Create the request body for the copy operation
    request_body = {
        'name': copy_title,
        'parents': [parent_folder_id]
    }

    # Make the copy request and print the new spreadsheet ID
    response = service.files().copy(fileId=spreadsheet_id, body=request_body).execute()
    new_spreadsheet_id = response['id']
    # print(f'New spreadsheet ID: {new_spreadsheet_id}')
    insert(new_spreadsheet_id)


def insert(spreadsheet_id):

    # Open the JSON file and load its contents into a variable
    with open('report.json', 'r') as file:
        data = json.load(file)

    service_account_file = 'google_drive_credentials.json'
    credentials = service_account.Credentials.from_service_account_file(
        filename = service_account_file
    )

    service_sheets = build('sheets', 'v4', credentials=credentials)
    # print(service_sheets)

    GOOGLE_SHEET_ID = spreadsheet_id

    values = (
        (data['Price'],),
    )

    value_range_body = {
        'majorDimension': 'Rows',
        'values': values
    }
    # Insert Price into B11
    response = service_sheets.spreadsheets().values().update(
        spreadsheetId = GOOGLE_SHEET_ID,
        valueInputOption = 'USER_ENTERED',
        range = "B11",
        body = value_range_body
    ).execute()

    values = (
        (data['AverageRent'],),
    )

    value_range_body = {
        'majorDimension': 'Rows',
        'values': values
    }
    # Insert Rent into B17
    response = service_sheets.spreadsheets().values().update(
        spreadsheetId = GOOGLE_SHEET_ID,
        valueInputOption = 'USER_ENTERED',
        range = "B17",
        body = value_range_body
    ).execute()

    values = (
        (data['PropertyTax'],),
    )

    value_range_body = {
        'majorDimension': 'Rows',
        'values': values
    }
    # Insert Property Tax into B21
    response = service_sheets.spreadsheets().values().update(
        spreadsheetId = GOOGLE_SHEET_ID,
        valueInputOption = 'USER_ENTERED',
        range = "B21",
        body = value_range_body
    ).execute()


def getEmailInformation():
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Call the Gmail API
    service = build('gmail', 'v1', credentials=creds)
    gmailLabel = "RealEstate"
    query = f'label:{gmailLabel} is:unread'

    response = service.users().messages().list(userId='me',q=query, labelIds=['INBOX', 'UNREAD']).execute()

    # print(response)

    messages = response.get('messages', [])
    latest_message = messages[0]



    message = service.users().messages().get(userId='me', id=latest_message['id']).execute()

    html_content = None
    payload = message.get('payload', {})
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/html':
                data = part['body'].get('data', '')
                html_content = base64.urlsafe_b64decode(data).decode('utf-8')
                break

    if html_content:
        # Do something with the HTML content
        # print(html_content)
        # Open a file in write mode
        with open('output.txt', 'w') as file:
            # Write data to the file
            file.write(html_content)

    else:
        print('No HTML content found in the message')

def extractUrl():
    with open('output.txt', 'r') as file:
        response = file.read()
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response, 'html.parser')
    links = soup.find_all('a')
    return links[2].get('href')

if __name__ == '__main__':
    # url = input("Enter the url of the onehome listing...\n")
    getEmailInformation()
    url = extractUrl()
    print(url)
    getInformation(url)
    createNewExcelSheet()






