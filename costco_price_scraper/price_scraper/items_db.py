"""
This module provides functions to interact with an SQLite database ('scraped_prices.db') for 
managing item data.

Functions:
- `create_items_table`: Create the 'items' table in the database if it doesn't exist.
- `delete_expired_items`: Delete expired items from the 'items' table.
- `upsert_items`: Update and insert items into the database.

Usage:
1. Use `create_items_table()` to initialize the 'items' table.
2. Employ `delete_expired_items()` to remove items with expiry dates in the past.
3. Apply `upsert_items(items)` to update or insert a list of items into the 'items' table.

Note: Each function establishes a connection to the database, performs the necessary 
operations, and commits changes. Ensure to close the database connection after usage.
"""
import sqlite3
from costco_price_scraper.utils.db_utils import date_parse

DB_FILE = "scraped_prices.db"


def create_items_table():
    """
    Create the 'items' table in the database if it doesn't exist.
    """
    with sqlite3.connect(DB_FILE) as conn:
        conn.create_function("date_parse", 1, date_parse)
        cursor = conn.cursor()
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


def delete_expired_items():
    """
    Delete expired items from the 'items' table.
    """
    #with sqlite3.connect(DB_FILE) as conn:
    #    conn.create_function("date_parse", 1, date_parse)
    #    cursor = conn.cursor()
    #    cursor.execute(
    #        """
    #        DELETE FROM items
    #        WHERE expiry_date < CURRENT_DATE;
    #    """
    #    )
    pass


def upsert_items(items):
    """
    Update and insert items into the database using executemany().

    Args:
        items (list): A list of lists containing item data.
    """
    with sqlite3.connect(DB_FILE) as conn:
        conn.create_function("date_parse", 1, date_parse)
        cursor = conn.cursor()

        for item in items:
            cursor.execute("""
            INSERT OR REPLACE INTO items (item_id, item_name, savings, expiry_date, sale_price)
            VALUES (?, ?, ?, date_parse(?), ?)
            """,
            item,)

        # Use executemany() for bulk inserts
        #cursor.executemany(
        #    """
        #    INSERT OR REPLACE INTO items (item_id, item_name, savings, expiry_date, sale_price)
        #    VALUES (?, ?, ?, date_parse(?), ?)
        #""",
        #    items,
        #)


def check_sale(items):
    """
    Check sale information based on IDs passed in

    Args:
        items (list): A list of ids
    """
    with sqlite3.connect(DB_FILE) as conn:
        conn.create_function("date_parse", 1, date_parse)
        cursor = conn.cursor()

        # Query the database for sale information
        cursor.execute(
            """
            SELECT item_id, item_name, savings, expiry_date, sale_price
            FROM items
            WHERE item_id IN ({})
             AND strftime('%Y-%m-%d', expiry_date) >= strftime('%Y-%m-%d', 'now', 'localtime')
            """.format(
                ",".join(map(str, items))
            )
        )

        # Fetch the results
        results = cursor.fetchall()

    total_savings = sum(row[2] for row in results)

    # Convert results to a list of dictionaries
    sale_info = [
        {
            "item_id": row[0],
            "item_name": row[1],
            "savings": row[2],
            "expiry_date": row[3],
            "sale_price": row[4],
        }
        for row in results
    ]
    refund_info = {"total_savings": total_savings, "sale_info": sale_info}

    return refund_info
