from costco_price_scraper.price_scraper import price_scraper as ps
from costco_price_scraper.receipt_scraper import receipt_scraper as rs
from costco_price_scraper.receipt_scraper import receipts_db
from costco_price_scraper.utils import email_sender, email_builder, config
from costco_price_scraper.utils.api_utils import call_api

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
    to_email = config.read_username_config()
    paths = [receipt.get("receipt_path") for receipt in receipts]
    
    email_sender.send_email(subject, body, to_email, paths)

if __name__ == "__main__":
    main()
