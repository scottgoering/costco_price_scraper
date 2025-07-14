from costco_price_scraper.price_scraper.items_db import check_sale

def call_api(all_items_list):
    """
    Make a GET request to a Flask API and print the response.

    Args:
        all_items_list (list): List of item IDs.

    Returns:
        dict: A hashmap of sale items.
    """
    all_item_ids = [item[1] for item in all_items_list]
    unique_item_ids = list(set(all_item_ids))
    data = check_sale(unique_item_ids)
    sale_item_hashmap = {}

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

    return sale_item_hashmap
