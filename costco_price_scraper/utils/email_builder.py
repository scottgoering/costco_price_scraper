

from datetime import datetime, timedelta


def construct_receipt_email_body_and_subject(receipt_items_list, sale_item_hashmap):
    if not receipt_items_list:
        subject = "No Costco Price Adjustments Found"
        body = (
            "<div style='font-family: Arial, sans-serif;'>"
            "<pre style='font-size: 16px;'>No price adjustments detected.</pre></div>"
        )
        return subject, body
    
    subject = "Costco Price Adjustment Opportunity Detected"
    body = "<div style='font-family: Arial, sans-serif;'><pre style='font-size: 16px;'>Its on sale now!\n"
    body += "Get your money back!\n"
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

    return subject, body