import requests
import json
import os
from qb.tokens_storage import refresh_tokens



# qb/quickbook_api.py

VENDOR_MAP = {
    # TODO: replace with real QBO Vendor IDs
    "Verizon": "42",
}

ACCOUNT_MAP = {
    # TODO: replace with real QBO Account IDs
    "Expenses": "7",
}


# ------------------------------------------------------
# Load & manage tokens
# ------------------------------------------------------
def _load_tokens():
    with open("tokens.json", "r") as f:
        return json.load(f)

_tokens = _load_tokens()

ACCESS_TOKEN = _tokens["access_token"]
REFRESH_TOKEN = _tokens["refresh_token"]
REALM_ID = _tokens.get("realmId") or "9341454809864192"

BASE_URL = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{REALM_ID}"
MINOR_VERSION = "?minorversion=65"


# ------------------------------------------------------
# Headers + Token Refresh
# ------------------------------------------------------
def _authorized_headers():
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


def _handle_expired_token(response):
    """
    If QuickBooks returns 401, refresh tokens and retry.
    """
    global ACCESS_TOKEN, REFRESH_TOKEN

    if response.status_code != 401:
        return response  # OK

    print("⚠️ Access Token expired → refreshing...")

    new_tokens = refresh_tokens(REFRESH_TOKEN)
    ACCESS_TOKEN = new_tokens["access_token"]
    REFRESH_TOKEN = new_tokens["refresh_token"]

    with open("tokens.json", "w") as f:
        json.dump(new_tokens, f, indent=4)

    return None  # Signal the caller to retry


# ------------------------------------------------------
# HTTP Helpers
# ------------------------------------------------------
def get(endpoint):
    url = f"{BASE_URL}/{endpoint}{MINOR_VERSION}"
    headers = _authorized_headers()

    print(f"📡 GET → {url}")
    response = requests.get(url, headers=headers)
    retry = _handle_expired_token(response)

    if retry is None:
        response = requests.get(url, headers=_authorized_headers())

    return response.json()


def post(endpoint, body):
    url = f"{BASE_URL}/{endpoint}{MINOR_VERSION}"
    headers = _authorized_headers()

    print(f"📤 POST → {url}")
    print("Payload:", json.dumps(body, indent=2))

    response = requests.post(url, headers=headers, json=body)
    retry = _handle_expired_token(response)

    if retry is None:
        response = requests.post(url, headers=_authorized_headers(), json=body)

    return response.json()


# ------------------------------------------------------
# PUBLIC: BILL CREATION
# ------------------------------------------------------
def create_bill(vendor, amount, date=None, service=None, po_id=None):
    """
    Create a basic Bill entity in QBO Sandbox.
    QuickBooks requires VendorRef.value and AccountRef.value (the internal IDs),
    not just names.
    """
    # Resolve IDs from simple maps (for now)
    vendor_id = VENDOR_MAP.get(vendor)
    account_name = service or "Expenses"
    account_id = ACCOUNT_MAP.get(account_name)

    if not vendor_id:
        return {
            "error": f"Unknown vendor '{vendor}'. Please map it to a QBO VendorRef.value."
        }

    if not account_id:
        return {
            "error": f"Unknown account '{account_name}'. Please map it to a QBO AccountRef.value."
        }

    body = {
        "VendorRef": {
            "value": vendor_id,
            "name": vendor,
        },
        "TotalAmt": amount,
        "Line": [
            {
                "Amount": amount,
                "DetailType": "AccountBasedExpenseLineDetail",
                "AccountBasedExpenseLineDetail": {
                    "AccountRef": {
                        "value": account_id,
                        "name": account_name,
                    }
                },
            }
        ],
    }

    if date:
        body["TxnDate"] = date

    return post("bill", body)



# ------------------------------------------------------
# PUBLIC: PAY BILL / VENDOR PAYMENT
# ------------------------------------------------------
def pay_bill(vendor, amount, date=None, bill_id=None, payment_method=None):
    """
    QBO Sandbox vendor payment (BillPayment entity).
    """

    body = {
        "VendorRef": {"name": vendor},
        "TotalAmt": amount,
        "PayType": "Cash",
        "Line": [
            {
                "Amount": amount,
                "LinkedTxn": [
                    {"TxnId": bill_id, "TxnType": "Bill"} if bill_id else {}
                ]
            }
        ],
    }

    if date:
        body["TxnDate"] = date

    return post("billpayment", body)


# ------------------------------------------------------
# PUBLIC: CREATE INVOICE
# ------------------------------------------------------
def create_invoice(customer, amount, date=None, item="Service"):
    """
    Very simple invoice generator for testing.
    """
    body = {
        "CustomerRef": {"name": customer},
        "TotalAmt": amount,
        "Line": [
            {
                "Amount": amount,
                "DetailType": "SalesItemLineDetail",
                "SalesItemLineDetail": {"ItemRef": {"name": item}}
            }
        ]
    }

    if date:
        body["TxnDate"] = date

    return post("invoice", body)


# ------------------------------------------------------
# PUBLIC: BALANCE SHEET REPORT
# ------------------------------------------------------
def run_balance_sheet_report(start_date=None, end_date=None):
    params = []
    if start_date:
        params.append(f"start_date={start_date}")
    if end_date:
        params.append(f"end_date={end_date}")

    param_str = "&".join(params)
    if param_str:
        endpoint = f"reports/BalanceSheet&{param_str}"
    else:
        endpoint = "reports/BalanceSheet"

    return get(endpoint)


# ------------------------------------------------------
# TEST
# ------------------------------------------------------
if __name__ == "__main__":
    print("🔍 Testing QuickBooks Connection...")
    print(get(f"companyinfo/{REALM_ID}"))
