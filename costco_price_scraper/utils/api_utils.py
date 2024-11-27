import requests

def call_api(all_items_list):
    """
    Make a GET request to a Flask API and print the response.

    Args:
        all_items_list (list): List of item IDs.

    Returns:
        dict: A hashmap of sale items.
    """
    api_url = "http://127.0.0.1:5000/check_sale"  # Update with your actual URL
    all_item_ids = [item[1] for item in all_items_list]
    unique_item_ids = list(set(all_item_ids))
    params = {"items": unique_item_ids}
    
    response = requests.get(api_url, params=params, timeout=10)
    sale_item_hashmap = {}
    
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
                print(f"Date Bought: {item[4]}")
                print(f"Is on Sale: {on_sale}")
                print("---")
    else:
        print("Failed to get a valid response from the API. Status code:", response.status_code)
        print(response.text)
        return None

    return sale_item_hashmap