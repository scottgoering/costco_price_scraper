# from costco_price_scraper.price_scraper import price_scraper as ps

# ps.run_price_scraper()

from costco_price_scraper.price_scraper import price_scraper as ps
from costco_price_scraper.receipt_scraper import receipt_scraper as rs
import requests


def call_api(all_items_list):
    """
    Make a POST request to a Flask API and print the response.

    Args:
        all_items_list (list): List of item IDs.

    Returns:
        None
    """
    # URL of your Flask API
    api_url = "http://localhost:5000/check_sale"  # Update with your actual URL

    # Example item IDs

    # JSON payload
    payload = {"item_ids": all_items_list}

    # Make a POST request
    response = requests.post(api_url, json=payload, timeout=10)

    # Check the response
    if response.status_code == 200:
        data = response.json()
        print("Total Savings:", data["total_savings"])
        print("Sale Info:")
        for sale_item in data["sale_info"]:
            print(f"Item ID: {sale_item['item_id']}")
            print(f"Item Name: {sale_item['item_name']}")
            print(f"Savings: {sale_item['savings']}")
            print(f"Expiry Date: {sale_item['expiry_date']}")
            print(f"Sale Price: {sale_item['sale_price']}")
            print("---")
    else:
        print("Request failed with status code:", response.status_code)
        print(response.text)


if __name__ == "__main__":
    ps.run_price_scraper()
    all_items_list = rs.run_receipt_scraper()
    call_api(all_items_list)
