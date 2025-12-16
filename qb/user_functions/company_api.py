from quickbook_api import get, REALM_ID
import json


def get_company_info():
    """Fetch company information from QuickBooks."""
    
    endpoint = f"companyinfo/{REALM_ID}?minorversion=65"

    data = get(endpoint)

    if "CompanyInfo" in data:
        print("🏢 Connected to QuickBooks Sandbox")
        print(json.dumps(data, indent=4))
        return data
    else:
        print("❌ Error retrieving company info:")
        print(json.dumps(data, indent=4))
        return None
