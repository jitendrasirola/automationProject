import json
import math
import sys
import time
import requests
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from requests.exceptions import HTTPError

# Provide user input in json format
try:
    userInput = input("Please Provide the Json input:")
    # Extract the json data
    jsonToDict = json.loads(userInput)
    city = (jsonToDict["city"])
    apiKey = (jsonToDict["appid"])
    variancePer = (jsonToDict["variance"]) / 100
# Exception handling for Json input
except json.decoder.JSONDecodeError:
    print("Invalid Json Format")
    sys.exit()
except Exception as jsonToDict:
    print(f"Json error: Incorrect keyword:{jsonToDict}")
    sys.exit()
    
# important paths and urls to run the script
pathWebDriver = "C://chromedriver.exe"
webSiteUrl = "https://weather.com/"
urlApi = "http://api.openweathermap.org/data/2.5/weather?q={cityName}&appid={APIkey}".format(cityName=city,APIkey=apiKey)
driver = webdriver.Chrome(pathWebDriver)
driver.implicitly_wait(15)

# selenium script to get the temperature from the UI
try:
    driver.get(webSiteUrl)
    time.sleep(3)
    element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "LocationSearch_input")))
    element.send_keys(city)
    time.sleep(3)
    element.send_keys(Keys.ENTER)
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.ID, 'MainContent')))
    temp = driver.find_element_by_xpath('//*[@data-testid="TemperatureValue"]').text
    ui_temp = int(temp.strip('°'))
    # print(ui_temp)

except ElementNotInteractableException:
    print("Failed to load element: Element not intractable")
    sys.exit()
except NoSuchElementException as selector:
    print(f'Failed to load element: {selector}')
    sys.exit()
finally:
    driver.quit()
    
# API automation script to get the temperature form the API
try:
    response = requests.get(urlApi)
    # access JSOn content
    json_response = response.json()
    if json_response["cod"] == 200:
        temp = (json_response["main"]["temp"])
        temp_celsius = (temp - 273.15)
        api_temp = int(math.trunc(temp_celsius))
        print(api_temp)
    else:
        api_message = (json_response["message"])
        print(f'Error:{api_message}')
        sys.exit()

except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
    sys.exit()
except Exception as err:
    print(f'Other error occurred: {err}')
    sys.exit()
    
# Comparator to compare the temperature of two sources
if ui_temp == api_temp:
    print('The temperature of ' + city + ' is same in both API and UI')
else:
    print('The temperature of ' + city + ' is no same in API and UI')
    # logic to check the variance of data from the two sources
    listTem = [ui_temp, api_temp]
    l_temp = len(listTem) - 1
    avg_temp = sum(listTem) / len(listTem)
    print(avg_temp)
    v = sum((x - avg_temp) ** 2 for x in listTem)
    variance = v / l_temp
    if variance / 100 in range(variancePer):
        print("Success : The temperature is within specified variance percentage range.")
    else:
        raise Exception("The temperature not is within specified variance percentage range.")
sys.exit()
