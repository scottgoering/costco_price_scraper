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


def create_items_table():
    """
    Create the 'items' table in the database if it doesn't exist.
    """
    conn = sqlite3.connect("scraped_prices.db")
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
    conn.commit()
    conn.close()


def delete_expired_items():
    """
    Delete expired items from the 'items' table.
    """
    conn = sqlite3.connect("scraped_prices.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM items
        WHERE expiry_date < CURRENT_DATE;
    """
    )
    conn.commit()
    conn.close()


def upsert_items(items):
    """
    Update and insert items into the database.

    Args:
        items (list): A list of lists containing item data.
    """
    conn = sqlite3.connect("scraped_prices.db")
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()
