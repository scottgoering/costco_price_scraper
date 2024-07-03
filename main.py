from costco_price_scraper.price_scraper import price_scraper as ps
from costco_price_scraper.receipt_scraper import receipt_scraper as rs
from costco_price_scraper.receipt_scraper import receipts_db
from costco_price_scraper.utils import email_sender, email_builder

import configparser
import requests

config_path = '/home/jacky/Code/costco_price_scraper/config.ini'

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
    config.read(config_path)
    return config["Credentials"]["USERNAME"]

def main():
    ps.run_price_scraper()
    all_items_list = rs.run_receipt_scraper_with_api()
    sale_item_hashmap = call_api(all_items_list)
    
    receipt_items_list = []
    receipt_id_set = set()
    
    for item in all_items_list:
        if item[1] in sale_item_hashmap:
            receipt_items_list.append(item)
            receipt_id_set.add(item[7])
    
    receipt_id_list = list(receipt_id_set)
    receipts = receipts_db.get_receipts_by_ids(receipt_id_list)
    
    subject, body = email_builder.construct_receipt_email_body_and_subject(receipt_items_list, sale_item_hashmap)
    to_email = read_receiver_email_config()
    paths = [receipt.get("receipt_path") for receipt in receipts]
    
    email_sender.send_email(subject, body, to_email, paths)

if __name__ == "__main__":
    main()
