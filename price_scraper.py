# pylint: disable=invalid-name,missing-function-docstring
import csv
from datetime import datetime, timedelta, timezone
import re
import sqlite3
import requests
from bs4 import BeautifulSoup


# TODO: use a proxy

# ### Scrape Item Prices from URL


def scrape_website(url):
    """
    Scrape data from a website.

    Args:
        url (str): The URL of the website.

    Returns:
        list: A list of lists containing scraped data.
    """
    # Send an HTTP request to the URL
    response = requests.get(url)

    if response.status_code == 200:
        # Parse HTML content of the page
        soup = BeautifulSoup(response.content, "html.parser")

        pattern = re.compile(
            r"(\d+) (.+?) \(\$([\d.]+) INSTANT SAVINGS EXPIRES ON (\d{4}-\d{2}-\d{2})\) \$(\d+\.\d+)"
        )

        batch_data = []

        for item in soup.find_all("figcaption", class_="wp-caption-text"):
            matches = pattern.findall(item.text)

            current_date = datetime.now().date()

            # Print extracted data
            for match in matches:
                item_id, item_name, savings, expiry_date, sale_price = match
                # check for valid dates
                try:
                    expiry_date_obj = datetime.strptime(expiry_date, "%Y-%m-%d").date()
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


# ### Scrape Relevant Links


def get_sales_post_urls():
    """
    Get relevant links for sales posts.

    Returns:
        list: A list of URLs for sales posts.
    """
    base_url = "https://cocowest.ca"

    urls_list = []
    for page_number in range(1, 4):
        # construct the url for each page
        page_url = f"{base_url}/page/{page_number}/"

        # Send an HTTP request to the URL
        response = requests.get(page_url)

        if response.status_code == 200:
            # Parse HTML content of the page
            soup = BeautifulSoup(response.content, "html.parser")

            list_items = soup.find_all("li", class_="g1-collection-item-carmania")

            # Setting threshold date for the past 30 days
            threshold_date = datetime.now(timezone.utc) - timedelta(days=30)

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
                            href = item.find("h3", class_="g1-gamma").a["href"]
                            print(f"Post within the last 30 days: {href}")
                            urls_list.append(href)
                else:
                    print("No time element found for:", item)
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
    return urls_list


post_urls_list = get_sales_post_urls()
print(post_urls_list)

# ### Connect to database


def create_items_table(cursor):
    """
    Create the 'items' table in the database if it doesn't exist.

    Args:
        cursor: The SQLite database cursor.
    """
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY,
            item_name TEXT,
            savings REAL,
            expiry_date DATE,
            sale_price REAL
        )
    """
    )


def delete_expired_items(cursor):
    """
    Delete expired items from the 'items' table.

    Args:
        cursor: The SQLite database cursor.
    """
    cursor.execute(
        """
        DELETE FROM items
        WHERE expiry_date < CURRENT_DATE;
    """
    )


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
    print(len(data))
    return data


def upsert_items(cursor, items):
    """
    Update and insert items into the database.

    Args:
        cursor: The SQLite database cursor.
        items (list): A list of lists containing item data.
    """
    for item in items:
        item_id, item_name, savings, expiry_date, sale_price = item

        # Use INSERT OR REPLACE to perform upsert
        cursor.execute(
            """
            INSERT OR REPLACE INTO items (item_id, item_name, savings, expiry_date, sale_price)
            VALUES (?, ?, ?, ?, ?)
        """,
            (item_id, item_name, savings, expiry_date, sale_price),
        )


# ### Update and insert items into the database. Delete expired items.

# scrape items from posts and update the database
conn = sqlite3.connect("scraped_prices.db")
cursor = conn.cursor()

create_items_table(cursor)
delete_expired_items(cursor)

scraped_data = scrape_items_from_posts(post_urls_list)

if scraped_data:
    upsert_items(cursor, scraped_data)
else:
    print("Scraping failed")

conn.commit()
conn.close()

# ### Create CSV file for Sale Items


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


if not scraped_data:
    scraped_data = scrape_items_from_posts(post_urls_list)
else:
    unique_dict = {}
    for inner_list in scraped_data:
        key = inner_list[0]

        # Only add the inner list if the key is not in the dictionary
        if key not in unique_dict:
            unique_dict[key] = inner_list

    # Convert the dictionary values back to a list
    scraped_data = list(unique_dict.values())

    if scraped_data:
        # CSV filename
        csv_filename = "scraped_data.csv"

        # Store the scraped data in a CSV file
        store_data_csv(scraped_data, csv_filename)

        print(f"Scraped_data stored in {csv_filename}")
    else:
        print("Scraping failed.")
