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
from datetime import datetime, timedelta, timezone
import re
from bs4 import BeautifulSoup
import requests

from costco_price_scraper.price_scraper import items_db

CSV_FILENAME = "scraped_data.csv"


def scrape_website(url):
    """
    Scrape data from a website.

    Args:
        url (str): The URL of the website.

    Returns:
        list: A list of lists containing scraped data.
    """
    response = requests.get(url, timeout=5)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html5lib")

        # pattern = re.compile(
        #    r"(\d+) (.+?) \(\$([\d.]+) INSTANT SAVINGS EXPIRES ON (\d{4}-\d{2}-\d{2})\) \$(\d+\.\d+)"
        # )
        # https://regex101.com/r/vXUiI8/1
        pattern = re.compile(
            r"(.+?) \$(\d+\.\d+) \(exp (\d{1,2}\/\d{1,2}\/\d{1,2})\.? \$(\d+) saved\. Item \#(\d+)\)"
        )

        batch_data = []
        blocks = soup.find_all("ul", class_="wp-block-list")
        for idx, block in enumerate(blocks):
            list_items = block.find_all("li", recursive=False)
            for iidx, item in enumerate(list_items):
                matches = pattern.findall(item.text)

                current_date = datetime.now().date()

                # Print extracted data
                for match in matches:
                    # item_id, item_name, savings, expiry_date, sale_price = match
                    item_name, sale_price, expiry_date, savings, item_id = match
                    # check for valid dates
                    try:
                        #expiry_date_obj = datetime.strptime(expiry_date, "%Y-%m-%d").date()
                        expiry_date_obj = datetime.strptime(expiry_date, "%m/%d/%y").date()
                    except ValueError:
                        print(f"Invalid date format: {expiry_date}")
                        continue
                    # Check if the item is not past its expiry date
                    if expiry_date_obj >= current_date:
                        batch_data.append(
                            [item_id, item_name, savings, expiry_date, sale_price]
                        )
                        print(f"Item ID: {item_id}")
                        print(f"Item Name: {item_name}")
                        print(f"Savings: ${savings}")
                        print(f"Expiry Date: {expiry_date}")
                        print(f"Sale Price: ${sale_price}")
                        print("\n")
                    else:
                        print(f"Item ID: {item_id} has expired and will not be included.")

        return batch_data
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None


def get_sales_post_urls():
    """
    Get relevant links for sales posts.

    Returns:
        list: A list of URLs for sales posts.
    """
    base_url = "https://www.frugalhotspot.com/tag/unadvertised/"

    urls_list = []
    for page_number in range(1, 2):
        # construct the url for each page
        page_url = f"{base_url}/page/{page_number}/"

        # Send an HTTP request to the URL
        response = requests.get(page_url, timeout=5)

        if response.status_code == 200:
            # Parse HTML content of the page
            soup = BeautifulSoup(response.content, "html5lib")

            #list_items = soup.find_all("li", class_="g1-collection-item-carmania")
            list_items = soup.find_all("li", class_="list-post pclist-layout")

            # Setting threshold date for the past 30 days
            threshold_date = datetime.now(timezone.utc) - timedelta(days=60)

            for item in list_items:
                # Extract the datetime attribute from the time element
                time_element = item.find("time", class_="entry-date")

                if time_element:
                    date_string = time_element.get("datetime", "")

                    if date_string:
                        # Convert date string to datetime object
                        post_date = datetime.strptime(
                            date_string, "%Y-%m-%dT%H:%M:%S%z"
                        )

                        # Make threshold_date timezone-aware
                        threshold_date_aware = threshold_date.astimezone(
                            post_date.tzinfo
                        )

                        if post_date >= threshold_date_aware:
                            #href = item.find("h3", class_="g1-gamma").a["href"]
                            href = item.find("h2", class_="penci-entry-title entry-title grid-title").a["href"]
                            print(f"Post within the last 30 days: {href}")
                            urls_list.append(href)
                else:
                    print("No time element found for:", item)
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
    return urls_list


def scrape_items_from_posts(post_urls_list):
    """
    Scrape items from lists of posts.

    Args:
        post_urls_list (list): List of URLs for sales posts.

    Returns:
        list: A list of lists containing scraped data.
    """
    data = []
    for url in post_urls_list:
        data.extend(scrape_website(url))

    return data


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
    # Step 1: Get the list of URLs for sales posts
    post_urls_list = get_sales_post_urls()
    print(post_urls_list)

    # Step 2: Create the items table in the database
    items_db.create_items_table()

    # Step 3: Delete expired items from the database
    items_db.delete_expired_items()

    # Step 4: Scrape data from the sales posts using the obtained URLs
    scraped_data = scrape_items_from_posts(post_urls_list)

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
        print("No Unadvertised deals available")
