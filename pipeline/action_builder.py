# pipeline/action_builder.py

from typing import Any, Dict, Optional

from .actions import (
    Action,
    PayVendorAction,
    CreateBillAction,
    RecordExpenseAction,
    GetBalanceSheetAction,
    RunPayrollAction,
    UnsupportedAction,
)


class ActionBuilder:
    """
    Maps (domain, fine_intent, extracted json) → Action instance.

    This is where we enforce:
      - which intents are actually actionable
      - which ones map to QuickBooks APIs
      - which ones are "semantic only" or not yet supported
    """

    def build_from_extractor(self, result: Dict[str, Any]) -> Optional[Action]:
        """
        result is the full dict from ExtractorManager.run()

        Expected shape:
        {
            "status": "complete" | "missing_fields" | "error",
            "domain": "AP" | "AR" | "OPS" | "PAYROLL",
            "fine_intent": "...",
            "json": {...},
            "raw_output": "..."
        }
        """
        status = result.get("status")
        if status != "complete":
            # Only build actions when required fields are satisfied
            return None

        domain = (result.get("domain") or "").upper()
        fine_intent = result.get("fine_intent")
        data: Dict[str, Any] = result.get("json") or {}

        # ----------------------------------------------------
        # AP domain
        # ----------------------------------------------------
        if domain == "AP":
            if fine_intent == "PAY_VENDOR":
                return PayVendorAction(
                    vendor=data.get("vendor"),
                    amount=data.get("amount"),
                    date=data.get("date"),
                    payment_method=data.get("payment_method"),
                    bill_id=data.get("bill_id"),
                    raw=data,
                )

            if fine_intent == "CREATE_BILL":
                return CreateBillAction(
                    vendor=data.get("vendor"),
                    amount=data.get("amount"),
                    date=data.get("date"),
                    service=data.get("service"),
                    po_id=data.get("po_id"),
                    raw=data,
                )

            if fine_intent == "RECORD_EXPENSE":
                return RecordExpenseAction(
                    vendor=data.get("vendor"),
                    amount=data.get("amount"),
                    account=data.get("account"),
                    date=data.get("date"),
                    raw=data,
                )

            # other AP fine_intents can be added here over time

        # ----------------------------------------------------
        # OPS domain
        # ----------------------------------------------------
        if domain == "OPS":
            if fine_intent == "GET_BALANCE_SHEET":
                return GetBalanceSheetAction(
                    start_date=data.get("start_date"),
                    end_date=data.get("end_date"),
                    raw=data,
                )
            # other OPS actions like GET_PROFIT_AND_LOSS_REPORT, etc.

        # ----------------------------------------------------
        # PAYROLL domain
        # ----------------------------------------------------
        if domain == "PAYROLL":
            if fine_intent in ("RUN_PAYROLL", "PROCESS_PAYROLL"):
                return RunPayrollAction(
                    department=data.get("department"),
                    period=data.get("period"),
                    raw=data,
                )

        # ----------------------------------------------------
        # If we reach here, we don't have a specific Action yet.
        # ----------------------------------------------------
        return UnsupportedAction(domain=domain, fine_intent=fine_intent, raw=data)
