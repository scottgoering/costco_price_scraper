from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta, timezone
import re
import csv
import sqlite3
import os
import configparser

LOGON_URL = "https://www.costco.ca/LogonForm"


def get_username_and_password():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["Credentials"]["USERNAME"], config["Credentials"]["PASSWORD"]


# Create the webdriver with the specified options
# driver = webdriver.Chrome(service=service, options=options)
driver = uc.Chrome(use_subprocess=False)
# Open the website
driver.get(LOGON_URL)
WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, '//button[@id="next"]'))
)
time.sleep(4)
# Find the username and password input fields and submit button
username_field = driver.find_element("id", "signInName")
password_field = driver.find_element("id", "password")
sign_in_button = driver.find_element(By.XPATH, '//button[@id="next"]')


def run_receipt_scraper():
    username, password = get_username_and_password()
