import datetime
import requests
import json

CLIENT_IDENTIFIER = "481b1aec-aa3b-454b-b81b-48187e28f205"


def get_recent_receipts(id_token, client_id):
    start_date_str, end_date_str = calculate_recent_dates()
    url = "https://ecom-api.costco.com/ebusiness/order/v1/orders/graphql"

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
        "client-identifier": "481b1aec-aa3b-454b-b81b-48187e28f205",
        "costco-x-authorization": f"Bearer {id_token}",
        "costco-x-wcs-clientId": client_id,
        "costco.env": "ecom",
        "costco.service": "restOrders",
        "sec-ch-ua": '"Not A Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    payload = {
        "query": "query receipts($startDate: String!, $endDate: String!) { receipts(startDate: $startDate, endDate: $endDate) { warehouseName documentType transactionDateTime transactionBarcode warehouseName transactionType total totalItemCount itemArray { itemNumber } tenderArray { tenderTypeCode tenderDescription amountTender } couponArray { upcnumberCoupon } } }",
        "variables": {
            "startDate": start_date_str,
            "endDate": end_date_str,
            "text": "Last 6 Months",
        },
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    print(response.status_code)
    print(response.json())
    return response


def receipt_details_request(id_token, client_id, receipt_id):
    url = "https://ecom-api.costco.com/ebusiness/order/v1/orders/graphql"

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "client-identifier": CLIENT_IDENTIFIER,
        "costco-x-authorization": f"Bearer {id_token}",
        "costco-x-wcs-clientId": client_id,
        "costco.env": "ecom",
        "costco.service": "restOrders",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    # Define the payload
    payload = {
        "query": "query receipts($barcode: String!) { receipts(barcode: $barcode) { warehouseName documentType transactionDateTime transactionDate companyNumber warehouseNumber operatorNumber warehouseName warehouseShortName registerNumber transactionNumber transactionType transactionBarcode total warehouseAddress1 warehouseAddress2 warehouseCity warehouseState warehouseCountry warehousePostalCode totalItemCount subTotal taxes total itemArray { itemNumber itemDescription01 frenchItemDescription1 itemDescription02 frenchItemDescription2 itemIdentifier unit amount taxFlag merchantID entryMethod transDepartmentNumber } tenderArray { tenderTypeCode tenderDescription amountTender displayAccountNumber sequenceNumber approvalNumber responseCode transactionID merchantID entryMethod } couponArray { upcnumberCoupon voidflagCoupon refundflagCoupon taxflagCoupon amountCoupon } subTaxes { tax1 tax2 tax3 tax4 aTaxPercent aTaxLegend aTaxAmount bTaxPercent bTaxLegend bTaxAmount cTaxPercent cTaxLegend cTaxAmount dTaxAmount } instantSavings membershipNumber } }",
        "variables": {"barcode": receipt_id},
    }

    # Make the request
    response = requests.post(url, headers=headers, json=payload)
    return response


def calculate_recent_dates():
    end_date = datetime.date.today().replace(day=1)

    days_in_month = (
        end_date.replace(month=end_date.month % 12 + 1, day=1)
        - datetime.timedelta(days=1)
    ).day

    end_date = end_date.replace(day=days_in_month)

    if end_date.month >= 6:
        start_month = end_date.month - 6
        start_year = end_date.year
    else:
        start_month = end_date.month + 12 - 6
        start_year = end_date.year - 1

    # Set start_date to 6 months before the end date with the start day being the first day of the month
    start_date = end_date.replace(month=start_month, year=start_year, day=1)

    # Format dates as strings in the required format (MM/DD/YYYY)
    start_date_str = start_date.strftime("%m/%d/%Y")
    end_date_str = end_date.strftime("%m/%d/%Y")
    return start_date_str, end_date_str


def parse_transaction_data(json_data):
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
