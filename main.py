# from costco_price_scraper.price_scraper import price_scraper as ps

# ps.run_price_scraper()

from costco_price_scraper.price_scraper import price_scraper as ps
from costco_price_scraper.receipt_scraper import receipt_scraper as rs
from costco_price_scraper.receipt_scraper import receipts_db
from costco_price_scraper.utils import email_sender
from datetime import datetime, timedelta

import configparser
import requests

# import subprocess
# import os


def call_api(all_items_list):
    """
    Make a GET request to a Flask API and print the response.

    Args:
        all_items_list (list): List of item IDs.

    Returns:
        None
    """
    # URL of your Flask API
    api_url = "http://localhost:5000/check_sale"  # Update with your actual URL

    # Example item IDs
    all_item_ids = [item[1] for item in all_items_list]
    unique_item_ids = list(set(all_item_ids))

    # Construct the query parameters for the GET request
    params = {"items": unique_item_ids}

    # Make a GET request
    response = requests.get(api_url, params=params, timeout=10)

    sale_item_hashmap = {}

    # Check the response
    if response.status_code == 200:
        data = response.json()
        print("Total Savings:", data["total_savings"])
        print("Sale Info:")
        for sale_item in data["sale_info"]:
            sale_item_hashmap[sale_item["item_id"]] = sale_item
            print(f"Item ID: {sale_item['item_id']}")
            print(f"Item Name: {sale_item['item_name']}")
            print(f"Savings: {sale_item['savings']}")
            print(f"Expiry Date: {sale_item['expiry_date']}")
            print(f"Sale Price: {sale_item['sale_price']}")
            print("---")

        print("Items Bought:")
        for item in all_items_list:
            if item[1] in sale_item_hashmap:
                on_sale = item[5] == 1
                print(f"Item ID: {item[1]}")
                print(f"Item Name: {item[2]}")
                print(f"Amount: {item[3]}")
                print(f"Unit: {item[4]}")
                print(f"On Sale: {on_sale}")
                print(f"Date: {item[6]}")
                print(f"Receipt ID: {item[7]}")
                print("---")
        return sale_item_hashmap
    else:
        print("Request failed with status code:", response.status_code)
        print(response.text)
        return None


def read_receiver_email_config():
    """Reads email config from the configuration file."""
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["Credentials"]["USERNAME"]


def construct_receipt_body(receipt_items_list, sale_item_hashmap):
    body = "<div style='font-family: Arial, sans-serif;'><pre style='font-size: 16px;'>You bought it at regular price and now it's on sale?!?!?!?!?\n"
    # body += "(╯°□°）╯︵ ┻━┻    (╯°□°）╯︵ ┻━┻    (╯°□°）╯︵ ┻━┻ \n"
    body += "Don't worry, I gotchu \n"
    body += "<strong style='font-size: 18px; color: #3366cc;'>List of Price Adjustment Items</strong>\n"
    body += "<hr style='border: 1px solid #ddd;'>\n"  # Horizontal line for separation
    total = 0
    label_width = 20
    value_width = 30

    for index, item in enumerate(receipt_items_list, start=1):
        purchase_date = datetime.strptime(item[6], "%Y-%m-%d")
        sale_expiry_date = datetime.strptime(
            sale_item_hashmap[item[1]]["expiry_date"], "%Y-%m-%d"
        )

        thirty_days_later = purchase_date + timedelta(days=30)
        earliest_date = min(thirty_days_later, sale_expiry_date)
        days_left = (earliest_date - datetime.now()).days

        total += sale_item_hashmap[item[1]]["savings"] * item[4]
        days_left_str = (
            f"{days_left} days" if days_left >= 0 else f"{-days_left} days ago"
        )

        text = (
            f"<p style='font-size: 14px;'><strong>Item Number {index}</strong></p>\n"
            f"<p style='font-size: 14px;'>{'Item ID:': <{label_width}} <span style='color: #555; font-size: 14px;'>{str(item[1]): >{value_width}}</span></p>\n"
            f"<p style='font-size: 14px;'>{'Item Name:': <{label_width}} <span style='color: #555; font-size: 14px;'>{str(item[2]): >{value_width}}</span></p>\n"
            f"<p style='font-size: 14px;'>{'Amount:': <{label_width}} <span style='color: #555; font-size: 14px;'>{str(item[3]): >{value_width}}</span></p>\n"
            f"<p style='font-size: 14px;'>{'Unit:': <{label_width}} <span style='color: #555; font-size: 14px;'>{str(item[4]): >{value_width}}</span></p>\n"
            f"<p style='font-size: 14px;'>{'Purchase Date:': <{label_width}} <span style='color: #555; font-size: 14px;'>{str(item[6]): >{value_width}}</span></p>\n"
            f"<p style='font-size: 14px;'>{'Sale Expiry Date:': <{label_width}} <span style='color: #555; font-size: 14px;'>{str(sale_item_hashmap[item[1]]['expiry_date']): >{value_width}}</span></p>\n"
            f"<p style='font-size: 14px;'>{'Receipt ID:': <{label_width}} <span style='color: #555; font-size: 14px;'>{str(item[7]): >{value_width}}</span></p>\n"
            f"<p style='font-size: 14px;'>{'Sale Price:': <{label_width}} <span style='color: #555; font-size: 14px;'>{'$'+str(sale_item_hashmap[item[1]]['sale_price']): >{value_width}}</span></p>\n"
            f"<p style='font-size: 14px;'>{'Per Unit Savings:': <{label_width}} <span style='color: #555; font-size: 14px;'>{'$'+str(sale_item_hashmap[item[1]]['savings']): >{value_width}}</span></p>\n"
            f"<p style='font-size: 14px;'>{'Total Item Savings:': <{label_width}} <span style='color: #555; font-size: 14px;'>{'$'+str(sale_item_hashmap[item[1]]['savings']*item[4]): >{value_width}}</span></p>\n"
            f"<p style='font-size: 14px;'>{'Days Left for Refund:': <{label_width}} <span style='color: #555; font-size: 14px;'>{days_left_str: >{value_width}}</span></p>\n"
            f"<p style='font-size: 14px;'>{'Last Day for Refund:': <{label_width}} <span style='color: #555; font-size: 14px;'>{str(earliest_date.strftime('%Y-%m-%d')): >{value_width}}</span></p>\n"
            "<hr style='border: 1px solid #ddd;'>\n"
        )
        body += text

    hotdog_amount = round(total / 1.5, 2)
    body += f"<p style='font-size: 16px;'><strong>Total Savings = ${total:.2f}</strong></p>\n"
    body += f"<p style='font-size: 16px;'>...which is equivalent to {hotdog_amount} hotdogs!!! {'🌭' * int(hotdog_amount)}</p></pre></div>"

    return body


if __name__ == "__main__":
    ps.run_price_scraper()
    # screenshots may not be ready yet
    all_items_list = rs.run_receipt_scraper_with_api()
    # all_items_list = rs.run_receipt_scraper()
    # all_items_list = receipts_db.get_all_items_not_on_sale()
    sale_item_hashmap = call_api(all_items_list)

    receipt_item_total_savings = {}
    receipt_items_list = []
    # for sale_item in data["sale_info"]:
    #     sale_item_id_hashmap[sale_item["item_id"]] = sale_item["savings"]

    receipt_id_set = set()
    for item in all_items_list:
        if item[1] in sale_item_hashmap:
            # items available for adjustments
            receipt_items_list.append(item)
            # receipts needed to attach for email
            receipt_id_set.add(item[7])

    receipt_id_list = list(receipt_id_set)
    receipts = receipts_db.get_receipts_by_ids(receipt_id_list)

    body = construct_receipt_body(receipt_items_list, sale_item_hashmap)
    subject = "Costco Price Adjustment Opportunity Detected"
    to_email = read_receiver_email_config()
    paths = []
    for receipt in receipts:
        paths.append(receipt.get("receipt_path"))

        # body = "This is a test email with an attachment."

        # attachment_path = 'path/to/your/photo.jpg'  # Replace with the path to your photo

    # email_sender.send_email(subject, body, to_email, paths)

    # try:
    #     subprocess.Popen(["start", "", os.path.normpath(path)], shell=True)
    # except FileNotFoundError:
    #     print(f"The file '{path}' does not exist.")
    # except Exception as e:
    #     print(f"An error occurred while trying to open the image: {e}")
