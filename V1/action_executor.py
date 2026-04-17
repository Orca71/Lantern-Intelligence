# pipeline/action_executor.py

from typing import Dict, Any
from qb.qb_api import (
    create_bill,
    pay_bill,
    create_invoice,
    run_balance_sheet_report
)



class ActionExecutor:
    """
    The real bridge between an Action object and the QuickBooks API.

    Action.build_qb_request() creates a normalized schema.
    ActionExecutor takes that schema and calls the correct QuickBooks helper.
    """

    def execute(self, action) -> Dict[str, Any]:
        qb_request = action.build_qb_request()

        endpoint = qb_request.get("endpoint")
        method = qb_request.get("method")

        # ------------------------------
        # AP: PAY_VENDOR
        # ------------------------------
        if action.name == "PAY_VENDOR":
            return pay_bill(
                vendor=action.payload.get("vendor"),
                amount=action.payload.get("amount"),
                date=action.payload.get("date"),
                bill_id=action.payload.get("bill_id"),
                payment_method=action.payload.get("payment_method"),
            )

        # ------------------------------
        # AP: CREATE_BILL
        # ------------------------------
        if action.name == "CREATE_BILL":
            return create_bill(
                vendor=action.payload.get("vendor"),
                amount=action.payload.get("amount"),
                date=action.payload.get("date"),
                service=action.payload.get("service"),
                po_id=action.payload.get("po_id"),
            )

        # ------------------------------
        # AP: RECORD_EXPENSE
        # ------------------------------
        if action.name == "RECORD_EXPENSE":
            return create_bill(
                vendor=action.payload.get("vendor"),
                amount=action.payload.get("amount"),
                date=action.payload.get("date"),
                service=action.payload.get("account"),
            )

        # ------------------------------
        # OPS: GET_BALANCE_SHEET
        # ------------------------------
        if action.name == "GET_BALANCE_SHEET":
            return run_balance_sheet_report(
                start_date=action.payload.get("start_date"),
                end_date=action.payload.get("end_date"),
            )

        # ------------------------------
        # Unsupported or unimplemented
        # ------------------------------
        return {
            "error": f"No executor mapping for {action.name}",
            "qb_request": qb_request,
        }
