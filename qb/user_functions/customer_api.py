from quickbook_api import get
import json


def get_customers():
    """Fetch all customers from QuickBooks."""
    data = get("customer")

    if "Customer" in data.get("QueryResponse", {}):
        customers = data["QueryResponse"]["Customer"]
        print(f"🧾 Retrieved {len(customers)} customers:")
        print(json.dumps(customers, indent=4))
        return customers

    print("❌ No customers found or error occurred.")
    print(json.dumps(data, indent=4))
    return None
