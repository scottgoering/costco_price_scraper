"""
Module to interact with an SQLite database for managing receipt data.

This module provides functions to create and query a 'receipts' table in an SQLite database.
The 'receipts' table stores information about items from receipts, including item details,
receipt ID, and sale status.

Functions:
- `create_receipts_table`: Create the 'receipts' table in the SQLite database.
- `get_all_receipt_ids`: Retrieve all distinct receipt IDs from the 'receipts' table.
- `get_all_item_ids_not_on_sale`: Retrieve all distinct item IDs that are not on sale.
- `upsert_receipt_data`: Upsert receipt data into the 'receipts' table using executemany().

Usage:
1. Use `create_receipts_table()` to initialize the 'receipts' table.
2. Retrieve receipt and item data using `get_all_receipt_ids()`, `get_all_item_ids_not_on_sale()`.
3. Upsert new receipt data using `upsert_receipt_data(all_receipt_items_list)`.

Note: Each function establishes a connection to the database, performs the necessary
operations, and commits changes. Context manager closes the database connection after usage.
"""

import sqlite3

DB_FILE = "scraped_prices.db"


def create_receipts_table():
    """
    Create the 'receipts' table in the SQLite database.

    The 'receipts' table has the following columns:
    - id: Auto-incremented primary key
    - item_id: Integer representing the item ID
    - item_name: Text representing the item name
    - item_price: Real number representing the item price
    - date: Date of the receipt
    - receipt_id: Text representing the receipt ID
    - on_sale: Boolean indicating whether the item is on sale
    - receipt_path: Text representing the path to the receipt
    """
    # Use the Connection as a Context Manager
    with sqlite3.connect(DB_FILE) as conn:
        # Create a cursor
        cursor = conn.cursor()

        # Don't use string formatting to build SQL queries
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INT,
                item_name TEXT,
                item_price REAL,
                date DATE,
                receipt_id TEXT,
                on_sale BOOLEAN,
                receipt_path TEXT
            )
        """
        )


def get_all_receipt_ids():
    """
    Get all distinct receipt IDs from the 'receipts' table.

    Returns:
        list: A list of distinct receipt IDs.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT receipt_id FROM receipts")
        result = cursor.fetchall()

    # Close connection outside the 'with' block
    receipt_ids = [row[0] for row in result]
    return receipt_ids


def get_all_item_ids_not_on_sale():
    """
    Get all distinct item IDs that are not on sale from the 'receipts' table.

    Returns:
        list: A list of distinct item IDs not on sale.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT item_id FROM receipts WHERE on_sale = 0")
        result = cursor.fetchall()

    # Close connection outside the 'with' block
    item_ids = [row[0] for row in result]
    return item_ids


def upsert_receipt_data(all_receipt_items_list):
    """
    Upsert receipt data into the 'receipts' table using executemany().

    Args:
        all_receipt_items_list (list): A list of dictionaries representing receipt items.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Extract data into a list of tuples
        data_to_insert = [
            (
                receipt_item.get("item_id"),
                receipt_item.get("item_name"),
                receipt_item.get("item_price"),
                receipt_item.get("date"),
                receipt_item.get("receipt_id"),
                receipt_item.get("on_sale"),
                receipt_item.get("receipt_path"),
            )
            for receipt_item in all_receipt_items_list
        ]

        # Use executemany() for bulk inserts
        cursor.executemany(
            """
            INSERT OR REPLACE INTO receipts (item_id, item_name, item_price, date, receipt_id, on_sale, receipt_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            data_to_insert,
        )
