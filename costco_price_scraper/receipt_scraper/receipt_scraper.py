"""Costco Price Scraper Module"""
from datetime import datetime
import os
import re
import time
import configparser

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc

from costco_price_scraper.receipt_scraper import receipts_db

LOGON_URL = "https://www.costco.ca/LogonForm"


def read_config():
    """Reads credentials from the configuration file."""
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["Credentials"]["USERNAME"], config["Credentials"]["PASSWORD"]


def initialize_webdriver():
    """Initializes the Chrome webdriver with specified options."""
    options = uc.ChromeOptions()
    # Add any additional options here
    return uc.Chrome(use_subprocess=False, options=options)


def login(driver, username, password):
    """
    Logs into the Costco website.

    Parameters:
    - driver: WebDriver instance
    - username: Costco account username
    - password: Costco account password
    """
    driver.get(LOGON_URL)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@id="next"]'))
    )
    time.sleep(4)
    # Find the username and password input fields and submit button
    username_field = driver.find_element("id", "signInName")
    password_field = driver.find_element("id", "password")
    sign_in_button = driver.find_element(By.XPATH, '//button[@id="next"]')
    # Enter your credentials and submit the form
    username_field.send_keys(username)
    username_field.clear()
    time.sleep(1)
    username_field.send_keys(username)
    time.sleep(1.1)
    password_field.send_keys(password)
    password_field.clear()
    time.sleep(2.4)
    password_field.send_keys(password)
    ActionChains(driver).move_to_element(sign_in_button).perform()
    time.sleep(5.3)
    ActionChains(driver).double_click(sign_in_button).perform()
    try:
        time.sleep(1)
        sign_in_button.click()
        time.sleep(5)
    except Exception:
        print("Timeout: The next page did not load within the expected time.")
    time.sleep(3)
    try:
        # Wait for the presence of an element on the next page (change the selector accordingly)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-field"))
        )

        # At this point, you can perform additional checks or actions on the next page
        # For example, check for a welcome message or other elements to confirm successful sign-in

        print("Sign-in successful!")

    except Exception:
        print("Timeout: The next page did not load within the expected time.")


def navigate_to_warehouse_orders(driver):
    """
    Navigates to the warehouse orders page.

    Parameters:
    - driver: WebDriver instance
    """
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "header_order_and_returns"))
    )
    account_button = driver.find_element("id", "header_order_and_returns")
    account_button.click()
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[@automation-id="myWarehouseOrdersTab"]')
        )
    )
    warehouse_button = driver.find_element(
        By.XPATH, '//button[@automation-id="myWarehouseOrdersTab"]'
    )
    warehouse_button.click()


def capture_screenshot(driver, folder, filename):
    """
    Captures a screenshot using the WebDriver.

    Parameters:
    - driver: WebDriver instance
    - folder: Folder to save the screenshot
    - filename: Name of the screenshot file

    Returns:
    - screenshot_path: Path to the saved screenshot
    """
    screenshot_path = os.path.join(folder, filename)
    driver.save_screenshot(screenshot_path)
    return screenshot_path


def process_receipt_metadata(driver, all_receipt_ids_set):
    """
    Processes receipt metadata.

    Parameters:
    - driver: WebDriver instance
    - all_receipt_ids_set: Set of all processed receipt IDs

    Returns:
    - receipt_id: ID of the processed receipt
    - date_time_str: Date and time of the receipt
    - receipt_path: Path to the saved receipt screenshot
    """
    # Locate the table element using its HTML structure
    receipt_element = driver.find_element(By.ID, "dataToPrint")
    # Get the HTML content of the table
    receipt_html = receipt_element.get_attribute("outerHTML")
    soup = BeautifulSoup(receipt_html, "html.parser")

    receipt_id = soup.find_all("div", class_="MuiBox-root css-11s8ayx")
    if receipt_id:
        receipt_id = receipt_id[-1].get_text(strip=True)
        print(receipt_id)
        # Check if receipt_id is in the set of all_receipt_ids_set
        if receipt_id in all_receipt_ids_set:
            print(f"Receipt {receipt_id} is already processed. Skipping...")
            return None, None, None  # Skip processing further
    date_str = soup.find("span", class_="date MuiBox-root css-ke5oan")
    time_str = soup.find("span", class_="time MuiBox-root css-5c53yh")
    if date_str is not None and time_str is not None:
        date_str = date_str.get_text(strip=True)
        time_str = time_str.get_text(strip=True)
        print(date_str)
    date_time_str = f"{date_str} {time_str}"
    date_time_format = "%m/%d/%Y %H:%M"
    date_time_obj = datetime.strptime(date_time_str, date_time_format)
    print(date_time_obj)

    receipts_folder = "receipts"
    if not os.path.exists(receipts_folder):
        os.makedirs(receipts_folder)

    # Generate a safe file name by replacing invalid characters
    filename_safe_str = re.sub(r"[^a-zA-Z0-9]", "_", date_time_str)
    file_name = f"receipt_{filename_safe_str}_{receipt_id}.png"
    receipt_path = capture_screenshot(driver, receipts_folder, file_name)
    print("Screenshot saved as:", receipt_path)

    return receipt_id, date_time_str, receipt_path


def check_for_discount_prefix(name):
    """
    Checks if an item name has a discount prefix.

    Parameters:
    - name: Item name

    Returns:
    - discount_id: ID extracted from the discount prefix
    """
    match = re.match(r"TPD/(\d+)", name)
    if match:
        return match.group(1)
    else:
        return None


def process_receipt_items(driver, receipt_id, date_time_str, receipt_path):
    """
    Processes receipt items.

    Parameters:
    - driver: WebDriver instance
    - receipt_id: ID of the receipt
    - date_time_str: Date and time of the receipt
    - receipt_path: Path to the saved receipt screenshot

    Returns:
    - item_list: List of processed items
    """
    # Locate the table element using its HTML structure
    table_element = driver.find_element(
        By.CSS_SELECTOR, 'table.MuiTable-root[aria-label="spanning table"]'
    )
    # Get the HTML content of the table
    table_html = table_element.get_attribute("outerHTML")
    soup = BeautifulSoup(table_html, "html.parser")
    item_list = []
    discount_set = set()
    table_body = soup.find("tbody", class_="MuiTableBody-root")
    for row in table_body.find_all("tr", class_="MuiTableRow-root css-ufft4h"):
        # Extract data from each column in the row
        item_id = row.find("td", class_="css-tedx13")
        item_name = row.find("td", class_="css-u9y9s5")
        item_price = row.find("td", class_="css-1879r0q")
        # Extract ID, name, and price
        if item_id is not None and item_name is not None and item_price is not None:
            item_id = item_id.get_text(strip=True)
            item_name = item_name.get_text(strip=True)
            # check for discounts
            discount_id = check_for_discount_prefix(item_name)
            if discount_id is not None:
                discount_set.add(discount_id)
                continue
            item_price = item_price.get_text(strip=True)
            item_info = {
                "item_id": item_id,
                "item_name": item_name,
                "item_price": item_price,
                "receipt_id": receipt_id,
                "date": date_time_str,
                "on_sale": False,
                "receipt_path": receipt_path,
            }
            item_list.append(item_info)
            # Perform desired actions, e.g., print or store in a list
            print(f"ID: {item_id}, Name: {item_name}, Price: {item_price}")
        else:
            break
    for item in item_list:
        item_id = item["item_id"]
        if item_id in discount_set:
            item["on_sale"] = True

    return item_list


def run_receipt_scraper():
    """
    The main function to execute the Costco Price Scraper.

    Returns:
        None
    """
    username, password = read_config()
    driver = initialize_webdriver()
    login(driver, username, password)
    navigate_to_warehouse_orders(driver)
    receipts_db.create_receipts_table()
    view_receipt_buttons = driver.find_elements(
        By.CSS_SELECTOR, 'button[automation-id="ViewInWareHouseReciept"]'
    )
    all_receipt_items_list = []
    for index, button in enumerate(view_receipt_buttons, start=1):
        print(f"Clicking 'View Receipt' button {index}")
        button.click()
        time.sleep(2)
        all_receipt_ids_set = set(receipts_db.get_all_receipt_ids())
        receipt_id, date_time_str, receipt_path = process_receipt_metadata(
            driver, all_receipt_ids_set
        )
        if receipt_id is not None:
            all_receipt_items_list += process_receipt_items(
                driver, receipt_id, date_time_str, receipt_path
            )
        else:
            # already processed the rest of the receipts
            close_popup = driver.find_element(
                By.CSS_SELECTOR, 'button.MuiButtonBase-root[aria-label="Close"]'
            )
            close_popup.click()
            break
        close_popup = driver.find_element(
            By.CSS_SELECTOR, 'button.MuiButtonBase-root[aria-label="Close"]'
        )
        close_popup.click()
        scroll_script = "window.scrollBy(0, 200);"
        driver.execute_script(scroll_script)
    receipts_db.upsert_receipt_data(all_receipt_items_list)
    all_items_list = receipts_db.get_all_item_ids_not_on_sale()
    return all_items_list
