"""
Costco API Module

This module provides functions to interact with the Costco API for retrieving recent receipts
and details of specific receipts.

Usage:
- Use get_recent_receipts function to get recent receipts.
- Use receipt_details_request function to get details of a specific receipt.
- The module also includes utility functions for calculating recent dates and parsing transaction data.


"""

import datetime
import requests
import json

CLIENT_IDENTIFIER = "481b1aec-aa3b-454b-b81b-48187e28f205"


def get_recent_receipts(id_token, client_id):
    """
    Retrieve recent receipts using the Costco API.

    Parameters:
    - id_token (str): The user's ID token.
    - client_id (str): The client ID.

    Returns:
    - response: The API response.
    """
    start_date_str, end_date_str = calculate_recent_dates()
    url = "https://ecom-api.costco.com/ebusiness/order/v1/orders/graphql"

    headers = generate_headers(id_token, client_id)

    payload = {
        "query": "query receipts($startDate: String!, $endDate: String!) { receipts(startDate: $startDate, endDate: $endDate) { warehouseName documentType transactionDateTime transactionBarcode warehouseName transactionType total totalItemCount itemArray { itemNumber } tenderArray { tenderTypeCode tenderDescription amountTender } couponArray { upcnumberCoupon } } }",
        "variables": {
            "startDate": start_date_str,
            "endDate": end_date_str,
            "text": "Last 6 Months",
        },
    }

    response = make_api_request(url, headers, payload)
    return response


def receipt_details_request(id_token, client_id, receipt_id):
    """
    Retrieve details for a specific receipt using the Costco API.

    Parameters:
    - id_token (str): The user's ID token.
    - client_id (str): The client ID.
    - receipt_id (str): The receipt barcode.

    Returns:
    - response: The API response.
    """
    url = "https://ecom-api.costco.com/ebusiness/order/v1/orders/graphql"

    headers = generate_headers(id_token, client_id)

    payload = {
        "query": "query receipts($barcode: String!) { receipts(barcode: $barcode) { warehouseName documentType transactionDateTime transactionDate companyNumber warehouseNumber operatorNumber warehouseName warehouseShortName registerNumber transactionNumber transactionType transactionBarcode total warehouseAddress1 warehouseAddress2 warehouseCity warehouseState warehouseCountry warehousePostalCode totalItemCount subTotal taxes total itemArray { itemNumber itemDescription01 frenchItemDescription1 itemDescription02 frenchItemDescription2 itemIdentifier unit amount taxFlag merchantID entryMethod transDepartmentNumber } tenderArray { tenderTypeCode tenderDescription amountTender displayAccountNumber sequenceNumber approvalNumber responseCode transactionID merchantID entryMethod } couponArray { upcnumberCoupon voidflagCoupon refundflagCoupon taxflagCoupon amountCoupon } subTaxes { tax1 tax2 tax3 tax4 aTaxPercent aTaxLegend aTaxAmount bTaxPercent bTaxLegend bTaxAmount cTaxPercent cTaxLegend cTaxAmount dTaxAmount } instantSavings membershipNumber } }",
        "variables": {"barcode": receipt_id},
    }

    response = make_api_request(url, headers, payload)
    return response


def calculate_recent_dates():
    """
    Calculate the start and end dates for a 6-month period.

    Returns:
    - Tuple: (start_date_str, end_date_str)
    """
    end_date = datetime.date.today().replace(day=1)
    days_in_month = (
        end_date.replace(month=end_date.month % 12 + 1, day=1)
        - datetime.timedelta(days=1)
    ).day
    end_date = end_date.replace(day=days_in_month)

    if end_date.month > 6:
        start_month = end_date.month - 6
        start_year = end_date.year
    else:
        start_month = end_date.month + 12 - 6
        start_year = end_date.year - 1

    start_date = end_date.replace(month=start_month, year=start_year, day=1)

    start_date_str = start_date.strftime("%m/%d/%Y")
    end_date_str = end_date.strftime("%m/%d/%Y")
    return start_date_str, end_date_str


def generate_headers(id_token, client_id):
    """
    Generate headers for API requests.

    Parameters:
    - id_token (str): The user's ID token.
    - client_id (str): The client ID.

    Returns:
    - dict: Request headers.
    """
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json-patch+json",
        "Origin": "https://www.costco.ca",
        "Referer": "https://www.costco.ca/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "client-identifier": CLIENT_IDENTIFIER,
        "costco-x-authorization": f"Bearer {id_token}",
        "costco-x-wcs-clientId": client_id,
        "costco.env": "ecom",
        "costco.service": "restOrders",
        "sec-ch-ua": '"Not A Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    return headers


def make_api_request(url, headers, payload):
    """
    Make an API request.

    Parameters:
    - url (str): The API endpoint URL.
    - headers (dict): Request headers.
    - payload (dict): Request payload.

    Returns:
    - response: The API response.
    """
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print(response.status_code)
    print(response.json())
    return response


def parse_transaction_data(json_data):
    """
    Parse transaction data from the API response.

    Parameters:
    - json_data (dict): The JSON data from the API response.

    Returns:
    - list: Parsed transaction data.
    """
    try:
        receipts = json_data.get("data", {}).get("receipts", [])
        parsed_transactions = []

        for receipt in receipts:
            transaction_barcode = receipt.get("transactionBarcode", "")
            transaction_date = receipt.get("transactionDateTime", "")
            transaction_type = receipt.get("transactionType", "")

            parsed_transactions.append(
                {
                    "transactionBarcode": transaction_barcode,
                    "transactionDate": transaction_date,
                    "transactionType": transaction_type,
                }
            )

        return parsed_transactions

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None