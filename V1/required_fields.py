REQUIRED_FIELDS_AP = {
    "LIST_BILLS": [],
    "LIST_PURCHASE_ORDERS": [],
    "LIST_UNPAID_BILLS": [],
    "LIST_VENDORS": [],

    "GET_VENDOR_DETAILS": ["vendor"],
    "GET_VENDOR_BALANCE": ["vendor"],
    "UPDATE_VENDOR": ["vendor"],
    "DELETE_VENDOR": ["vendor"],

    "PAY_VENDOR": ["vendor", "amount"],
    "PAY_BILL": ["vendor", "amount"],
    "RECORD_EXPENSE": ["vendor", "amount"],
    "CREATE_BILL": ["vendor", "amount"],

    "CLOSE_PURCHASE_ORDER": ["vendor"],
    "GET_PURCHASE_ORDER_STATUS": ["vendor"],
    "CREATE_PURCHASE_ORDER": ["vendor"],
    "DELETE_PURCHASE_ORDER": ["vendor"],
}

REQUIRED_FIELDS_AR = {

    "LIST_CUSTOMERS": [],
    "LIST_INVOICES": [],
    "LIST_UNPAID_INVOICES": [],
    "GET_SALES_REPORT": [],

    "CREATE_CUSTOMER": ["customer"],
    "DELETE_CUSTOMER": ["customer"],
    "UPDATE_CUSTOMER": ["customer"],
    "GET_CUSTOMER_DETAILS": ["customer"],
    "GET_CUSTOMER_BALANCE": ["customer"],

    "DELETE_INVOICE": ["invoice"],
    "GET_INVOICE_STATUS": ["invoice"],
    "SEND_INVOICE": ["invoice"],
    "RECORD_INVOICE_PAYMENT": ["invoice"],

    "CREATE_INVOICE": ["customer", "amount"],
    "CREATE_ESTIMATE": ["customer", "amount"],
    "CONVERT_ESTIMATE_TO_INVOICE": ["invoice"],
    "CREATE_SALES_RECEIPT": ["customer", "amount"],

    "SEND_ESTIMATE": ["invoice"],
}

REQUIRED_FIELDS_PAYROLL = {

    "LIST_EMPLOYEES": [],
    "LIST_PAYROLL_RUNS": [],
    "GET_PAYROLL_SUMMARY": [],

    "ADD_EMPLOYEE": ["employee"],
    "DELETE_EMPLOYEE": ["employee"],
    "UPDATE_EMPLOYEE": ["employee"],
    "GET_EMPLOYEE_DETAILS": ["employee"],

    "PROCESS_PAYROLL": ["employee"],
    "RUN_PAYROLL": ["employee"],
}

REQUIRED_FIELDS_OPS = {

    "GET_BALANCE_SHEET": [],
    "GET_CASH_FLOW_REPORT": [],
    "GET_COMPANY_INFO": [],
    "GET_PROFIT_AND_LOSS_REPORT": [],
    "LIST_BANK_ACCOUNTS": [],
    "LIST_TRANSACTIONS": [],
    "LIST_INVENTORY_ITEMS": [],

    "ADD_USER": ["user"],
    "UPDATE_SERVICE_ITEM": ["item"],
    "UPDATE_COMPANY_INFO": ["company"],
    "GET_INVENTORY_DETAILS": ["item"],
    "UPDATE_INVENTORY_ITEM": ["item"],

    "ADD_CHART_OF_ACCOUNT": ["account"],
    "ADD_ITEM_CATEGORY": ["category"],
    "ADD_SERVICE_ITEM": ["item"],
    "ADD_TIME_ACTIVITY": ["activity"],

    "SET_DEFAULT_INVOICE_TERMS": ["terms"],
    "SET_FISCAL_YEAR_START": ["date"],
    "SET_SALES_TAX_RATE": ["rate"],

    "ADD_BANK_ACCOUNT": ["account"],
    "CREATE_TRANSFER": ["bank", "amount"],
    "TRANSFER_FUNDS": ["bank", "amount"],
    "DEPOSIT_FUNDS": ["bank", "amount"],
    "RECORD_DEPOSIT": ["bank", "amount"],

    "GET_ACCOUNT_BALANCES": ["account"],
    "GET_BANK_ACCOUNT_BALANCES": ["bank"],
    "GET_BANK_TRANSACTIONS": ["bank"],

    "START_RECONCILIATION": ["account"],

    "UPLOAD_ATTACHMENT": ["attachment"],

    "ADD_INVENTORY_ITEM": ["item"],
    "ADJUST_INVENTORY_QUANTITY": ["item"],
    "RECORD_INVENTORY_SHRINKAGE": ["item"],
}

REQUIRED_FIELDS = {
    "AP": REQUIRED_FIELDS_AP,
    "AR": REQUIRED_FIELDS_AR,
    "PAYROLL": REQUIRED_FIELDS_PAYROLL,
    "OPS": REQUIRED_FIELDS_OPS,
}

def get_missing_fields(domain: str, intent: str, data: dict):
    domain_map = REQUIRED_FIELDS.get(domain, {})
    required = domain_map.get(intent, [])
    return [field for field in required if not data.get(field)]


