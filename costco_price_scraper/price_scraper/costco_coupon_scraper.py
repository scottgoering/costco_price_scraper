"""
Module: price_scraper

This module defines functions for scraping data from sales posts on a website,
storing the data in a CSV file, and updating the database with the scraped information.

Functions:
- scrape_website(url): Scrape data from a website given its URL.
- get_sales_post_urls(): Get relevant links for sales posts.
- scrape_items_from_posts(post_urls_list): Scrape items from lists of sales posts.
- store_data_csv(data, filename): Store data in a CSV file.
- run_price_scraper(): Orchestrates the price scraper workflow.

Constants:
- CSV_FILENAME (str): Default CSV file name for storing scraped data.

Note: The 'requests' library is used for making HTTP requests,
and 'BeautifulSoup' is used for HTML parsing.
"""
import csv
import re
from bs4 import BeautifulSoup
import requests

from costco_price_scraper.price_scraper import items_db
from costco_price_scraper.price_scraper.regex import parse_product_string

CSV_FILENAME = "scraped_coupon_data.csv"


def scrape_coupons(url):
    """
    Scrape data from a website.

    Args:
        url (str): The URL of the website.

    Returns:
        list: A list of lists containing scraped data.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        batch_data = []
        soup = BeautifulSoup(response.content, "html5lib")
        all_items = soup.find_all('div', class_='MuiBox-root mui-17tvcl1')
        #coupons = soup.find_all("div", class_="MuiBox-root mui-1d73mkv")
        coupons = []
        for item in all_items:
            location = item.find('div', {"class": re.compile('MuiTypography-root MuiTypography-bodyCopy.*')})
            if location:
                location_text = location.get_text()
                if 'Warehouse' in location_text:
                    coupons.append(item)

        disclaimer_header_elements = soup.find_all("div", class_="MuiTypography-root MuiTypography-bodyCopy mui-8recv0")
        disclaimer_header_text = disclaimer_header_elements[0].get_text()
        valid_date_pattern = r'(?:.*Valid \d{1,2}/\d{1,2}/\d{1,2} - )(\d{1,2}/\d{1,2}/\d{1,2})'
        valid_to_match = re.match(valid_date_pattern, disclaimer_header_text)
        expiry_date = valid_to_match.groups()[0]

        for item in coupons:
            item_text = item.find("div", class_="MuiBox-root mui-1d73mkv")
            item_name, item_numbers, price, savings = parse_product_string(item_text.get_text(' '))
            for item_id in item_numbers:
                batch_data.append(
                    [item_id, item_name, savings, expiry_date, price]
                )
        return batch_data
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None


def store_data_csv(data, filename):
    """
    Store data in a CSV file.

    Args:
        data (list): A list of lists containing data to be stored.
        filename (str): The name of the CSV file.
    """
    # Write the batch data to the CSV file
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        # Create a CSV writer
        csv_writer = csv.writer(csvfile)

        # Write header
        csv_writer.writerow(
            ["Item ID", "Item Name", "Savings", "Expiry Date", "Sale Price"]
        )

        # Write the batch data
        csv_writer.writerows(data)

    print(f"Batch data written to {filename}")


def run_price_scraper():
    """
    Run the price scraper workflow.

    This function orchestrates the process of scraping data from sales posts on a website,
    storing the data in a CSV file, and updating the database with the scraped information.

    Steps:
    1. Get the list of URLs for sales posts.
    2. Print the list of obtained URLs.
    3. Create the items table in the database.
    4. Delete expired items from the database.
    5. Scrape data from the sales posts using the obtained URLs.
    6. If data is successfully scraped:
        a. Upsert (update or insert) the scraped data into the database.
        b. Remove duplicate entries based on item ID.
        c. If unique data is obtained:
            i. Store the unique scraped data in a CSV file.
            ii. Print a success message.
    7. If the scraping process failed, print an error message.
    """
    url = 'https://www.costco.com/online-offers.html'

    # Step 2: Create the items table in the database
    items_db.create_items_table()

    # Step 3: Delete expired items from the database
    items_db.delete_expired_items()

    # Step 4: Scrape data from the sales posts using the obtained URLs
    scraped_data = scrape_coupons(url)

    # Step 5: If data is successfully scraped
    if scraped_data:
        # Step 6a: Upsert the scraped data into the database
        items_db.upsert_items(scraped_data)

        # Step 6b: Remove duplicate entries based on item ID
        unique_dict = {}
        for inner_list in scraped_data:
            key = inner_list[0]

            # Only add the inner list if the key is not in the dictionary
            if key not in unique_dict:
                unique_dict[key] = inner_list

        # Step 6c: Convert the dictionary values back to a list
        scraped_data = list(unique_dict.values())

        # Step 6d: If unique data is obtained
        if scraped_data:
            # Step 6d-i: Store the unique scraped data in a CSV file
            store_data_csv(scraped_data, CSV_FILENAME)

            # Step 6d-ii: Print a success message
            print(f"Scraped_data stored in {CSV_FILENAME}")

    else:
        # Step 7: If the scraping process failed, print an error message
        print("Scraping failed.")

if __name__ == '__main__':
    run_price_scraper()