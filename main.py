# from costco_price_scraper.price_scraper import price_scraper as ps

# ps.run_price_scraper()

from costco_price_scraper.price_scraper import price_scraper as ps
from costco_price_scraper.receipt_scraper import receipt_scraper as rs
from costco_price_scraper.receipt_scraper import receipts_db
import requests
import subprocess
import os


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

    sale_item_id_set = set()

    # Check the response
    if response.status_code == 200:
        data = response.json()
        print("Total Savings:", data["total_savings"])
        print("Sale Info:")
        for sale_item in data["sale_info"]:
            sale_item_id_set.add(sale_item["item_id"])
            print(f"Item ID: {sale_item['item_id']}")
            print(f"Item Name: {sale_item['item_name']}")
            print(f"Savings: {sale_item['savings']}")
            print(f"Expiry Date: {sale_item['expiry_date']}")
            print(f"Sale Price: {sale_item['sale_price']}")
            print("---")

        print("Items Bought:")
        for item in all_items_list:
            if item[1] in sale_item_id_set:
                on_sale = item[5] == 1
                print(f"Item ID: {item[1]}")
                print(f"Item Name: {item[2]}")
                print(f"Amount: {item[3]}")
                print(f"Unit: {item[4]}")
                print(f"On Sale: {on_sale}")
                print(f"Date: {item[6]}")
                print(f"Receipt ID: {item[7]}")
                print("---")
        return data
    else:
        print("Request failed with status code:", response.status_code)
        print(response.text)
        return None


if __name__ == "__main__":
    ps.run_price_scraper()
    all_items_list = rs.run_receipt_scraper_with_api()
    # all_items_list = rs.run_receipt_scraper()
    # all_items_list = receipts_db.get_all_items_not_on_sale()
    data = call_api(all_items_list)
    sale_item_id_set = set()
    receipt_items_list = []
    for sale_item in data["sale_info"]:
        sale_item_id_set.add(sale_item["item_id"])

    receipt_id_set = set()
    for item in all_items_list:
        if item[1] in sale_item_id_set:
            receipt_items_list.append(item)
            receipt_id_set.add(item[7])

    receipt_id_list = list(receipt_id_set)
    receipts = receipts_db.get_receipts_by_ids(receipt_id_list)
    for receipt in receipts:
        path = receipt.get("receipt_path")
        try:
            subprocess.Popen(["start", "", os.path.normpath(path)], shell=True)
        except FileNotFoundError:
            print(f"The file '{path}' does not exist.")
        except Exception as e:
            print(f"An error occurred while trying to open the image: {e}")
