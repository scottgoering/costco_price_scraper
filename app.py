from flask import Flask, jsonify, request
import sqlite3
from dateutil import parser

app = Flask(__name__)

def date_parse(s):
    ''' sql udf to convert string to date'''
    try:
        t = parser.parse(s, parser.parserinfo(dayfirst=True))
        return t.strftime('%Y-%m-%d')
    except:
        return None


@app.route("/check_sale", methods=["GET"])
def check_sale():
    # Get the list of item IDs from the query parameters
    item_ids = request.args.getlist("items")

    # Connect to the database
    conn = sqlite3.connect("scraped_prices.db")
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
            ",".join(map(str, item_ids))
        )
    )

    # Fetch the results
    results = cursor.fetchall()

    # Close the database connection
    conn.close()

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

    return jsonify(refund_info)


if __name__ == "__main__":
    app.run(debug=True)
