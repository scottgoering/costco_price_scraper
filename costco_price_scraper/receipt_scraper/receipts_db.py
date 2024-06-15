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


def create_receipt_items_table():
    """
    Create the 'receipt_items' table in the SQLite database.

    The 'receipt_items' table has the following columns:
    - id: Auto-incremented primary key
    - item_id: Integer representing the item ID
    - item_name: Text representing the item name
    - amount: Real number representing the item amount
    - unit: Integer representing the item unit
    - on_sale: Boolean indicating whether the item is on sale
    - receipt_date: Date of the receipt
    - receipt_id: Text representing the receipt ID
    - receipt_type: Text representing the receipt type
    - username: Text representing the username
    """
    # Use the Connection as a Context Manager
    with sqlite3.connect(DB_FILE) as conn:
        # Create a cursor
        cursor = conn.cursor()

        # Don't use string formatting to build SQL queries
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS receipt_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INT,
                item_name TEXT,
                amount REAL,
                unit INT,
                on_sale BOOLEAN,
                receipt_date DATE,
                receipt_id TEXT,
                receipt_type TEXT,
                username TEXT
            )
        """
        )


def create_receipts_table():
    """
    Create the 'receipts' table in the SQLite database.

    The 'receipts' table has the following columns:
    - id: Auto-incremented primary key
    - receipt_id: Text representing the receipt ID
    - receipt_date: Date of the receipt
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
                receipt_id TEXT,
                receipt_date DATE,
                receipt_path TEXT
            )
        """
        )


def upsert_receipt_items_data(all_receipt_items_list):
    """
    Upsert receipt items data into the 'receipt_items' table using executemany().

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
                receipt_item.get("amount"),
                receipt_item.get("unit"),
                receipt_item.get("on_sale"),
                receipt_item.get("receipt_date"),
                receipt_item.get("receipt_id"),
                receipt_item.get("receipt_type"),
                receipt_item.get("username")
            )
            for receipt_item in all_receipt_items_list
        ]

        cursor.executemany(
            """
            INSERT OR REPLACE INTO receipt_items (item_id, item_name, amount, unit, on_sale, receipt_date, receipt_id, receipt_type, username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            data_to_insert,
        )

def upsert_receipt_data(all_receipts_list):
    """
    Upsert receipt data into the 'receipts' table using executemany().

    Args:
        all_receipts_list (list): A list of dictionaries representing receipts.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Extract data into a list of tuples
        # data_to_insert = [
        #     (
        #         receipt.get("receipt_id"),
        #         receipt.get("receipt_date"),
        #         receipt.get("receipt_path"),
        #     )
        #     for receipt in all_receipts_list
        # ]

        # Use executemany() for bulk inserts
        cursor.executemany(
            """
            INSERT OR REPLACE INTO receipts (receipt_id, receipt_date, receipt_path)
            VALUES (?, ?, ?)
        """,
            all_receipts_list,
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


def get_receipts_by_ids(receipt_ids):
    """
    Retrieve receipts from the 'receipts' table based on the provided receipt IDs.

    Args:
    - receipt_ids (list): List of receipt IDs to retrieve.

    Returns:
    - list: List of dictionaries representing the matching receipts.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM receipts
            WHERE receipt_id IN ({}) 
            """.format(
                ", ".join("?" for _ in receipt_ids)
            ),
            receipt_ids,
        )

        rows = cursor.fetchall()

        receipts = []
        for row in rows:
            receipt = {
                "id": row[0],
                "receipt_id": row[1],
                "receipt_date": row[2],
                "receipt_path": row[3],
            }
            receipts.append(receipt)

    return receipts


def get_all_item_ids_not_on_sale():
    """
    Get all distinct item IDs that are not on sale from the 'receipts' table.

    Returns:
        list: A list of distinct item IDs not on sale.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT item_id FROM receipt_items WHERE on_sale = 0")
        result = cursor.fetchall()

    # Close connection outside the 'with' block
    item_ids = [row[0] for row in result]
    return item_ids


def get_all_items_not_on_sale():
    """
    Get all rows from the 'receipt_items' table where items are not on sale.

    Returns:
        list: A list of rows where items are not on sale.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM receipt_items WHERE on_sale = 0")
        result = cursor.fetchall()

    # Close connection outside the 'with' block
    return result


def get_all_user_items_not_on_sale(username):
    """
    Get all rows from the 'receipt_items' table where items are not on sale and filter by username.

    Args:
        username (str): The username to filter the items by.

    Returns:
        list: A list of rows where items are not on sale for the specified username.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM receipt_items WHERE on_sale = 0 AND username = ?", (username,))
        result = cursor.fetchall()

    # Close connection outside the 'with' block
    return result