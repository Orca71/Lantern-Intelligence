# pipeline/actions.py

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Action(ABC):
    """
    Base class for all executable actions.

    Bridge between:
        (domain, fine_intent, extracted JSON) → QuickBooks (or other systems)

    It does NOT call QuickBooks directly.
    It just normalizes the payload and knows whether
    it *could* be executed via QuickBooks.
    """

    name: str = "BASE_ACTION"
    domain: str = "GENERIC"
    fine_intent: str = "GENERIC"

    # QuickBooks-related metadata
    supported_by_qb: bool = False
    qb_endpoint: Optional[str] = None  # e.g. "bill", "payment", "reports/BalanceSheet"
    qb_method: Optional[str] = None    # "GET" / "POST" / etc.

    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload

    @abstractmethod
    def build_qb_request(self) -> Dict[str, Any]:
        """
        Return a normalized structure that the QuickBooks adapter
        can use to call the API:

            {
                "endpoint": "bill" | "payment" | "reports/BalanceSheet" | ...,
                "method": "GET" | "POST",
                "body": {...} or "params": {...}
            }
        """
        ...

    def to_dict(self) -> Dict[str, Any]:
        """
        For logging / debugging / returning through the pipeline.
        """
        return {
            "name": self.name,
            "domain": self.domain,
            "fine_intent": self.fine_intent,
            "supported_by_qb": self.supported_by_qb,
            "qb_endpoint": self.qb_endpoint,
            "qb_method": self.qb_method,
            "payload": self.payload,
        }


# =====================================================================
# AP domain
# =====================================================================

class PayVendorAction(Action):
    """
    AP / PAY_VENDOR

    Roughly:
    - paying an open bill for a vendor
    - or recording a vendor payment
    """

    name = "PAY_VENDOR"
    domain = "AP"
    fine_intent = "PAY_VENDOR"

    supported_by_qb = True
    qb_endpoint = "payments"   # your qb_api / quickbook_api will interpret this
    qb_method = "POST"

    def __init__(
        self,
        vendor: Optional[str],
        amount: Optional[float],
        date: Optional[str] = None,
        payment_method: Optional[str] = None,
        bill_id: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
    ):
        payload = {
            "vendor": vendor,
            "amount": amount,
            "date": date,
            "payment_method": payment_method,
            "bill_id": bill_id,
            "raw": raw or {},
        }
        super().__init__(payload)

    def build_qb_request(self) -> Dict[str, Any]:
        body = {
            "VendorRef": {"name": self.payload["vendor"]},
            "TotalAmt": self.payload["amount"],
        }
        if self.payload.get("date"):
            body["TxnDate"] = self.payload["date"]

        return {
            "endpoint": self.qb_endpoint,
            "method": self.qb_method,
            "body": body,
        }


class CreateBillAction(Action):
    """
    AP / CREATE_BILL
    """

    name = "CREATE_BILL"
    domain = "AP"
    fine_intent = "CREATE_BILL"

    supported_by_qb = True
    qb_endpoint = "bills"   # qb_api will interpret this
    qb_method = "POST"

    def __init__(
        self,
        vendor: Optional[str],
        amount: Optional[float],
        date: Optional[str] = None,
        service: Optional[str] = None,
        po_id: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
    ):
        payload = {
            "vendor": vendor,
            "amount": amount,
            "date": date,
            "service": service,
            "po_id": po_id,
            "raw": raw or {},
        }
        super().__init__(payload)

    def build_qb_request(self) -> Dict[str, Any]:
        body = {
            "VendorRef": {"name": self.payload["vendor"]},
            "TotalAmt": self.payload["amount"],
        }
        if self.payload.get("date"):
            body["TxnDate"] = self.payload["date"]

        return {
            "endpoint": self.qb_endpoint,
            "method": self.qb_method,
            "body": body,
        }


class RecordExpenseAction(Action):
    """
    AP / RECORD_EXPENSE
    """

    name = "RECORD_EXPENSE"
    domain = "AP"
    fine_intent = "RECORD_EXPENSE"

    supported_by_qb = True
    qb_endpoint = "expenses"  # interpreted by qb_api / quickbook_api
    qb_method = "POST"

    def __init__(
        self,
        vendor: Optional[str],
        amount: Optional[float],
        account: Optional[str] = None,
        date: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
    ):
        payload = {
            "vendor": vendor,
            "amount": amount,
            "account": account,
            "date": date,
            "raw": raw or {},
        }
        super().__init__(payload)

    def build_qb_request(self) -> Dict[str, Any]:
        body = {
            "Payee": self.payload["vendor"],
            "TotalAmt": self.payload["amount"],
        }
        if self.payload.get("date"):
            body["TxnDate"] = self.payload["date"]

        return {
            "endpoint": self.qb_endpoint,
            "method": self.qb_method,
            "body": body,
        }


# =====================================================================
# OPS domain
# =====================================================================

class GetBalanceSheetAction(Action):
    """
    OPS / GET_BALANCE_SHEET
    """

    name = "GET_BALANCE_SHEET"
    domain = "OPS"
    fine_intent = "GET_BALANCE_SHEET"

    supported_by_qb = True
    qb_endpoint = "reports/BalanceSheet"
    qb_method = "GET"

    def __init__(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
    ):
        payload = {
            "start_date": start_date,
            "end_date": end_date,
            "raw": raw or {},
        }
        super().__init__(payload)

    def build_qb_request(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if self.payload.get("start_date"):
            params["start_date"] = self.payload["start_date"]
        if self.payload.get("end_date"):
            params["end_date"] = self.payload["end_date"]

        return {
            "endpoint": self.qb_endpoint,
            "method": self.qb_method,
            "params": params,
        }


# =====================================================================
# PAYROLL domain
# =====================================================================

class RunPayrollAction(Action):
    """
    PAYROLL / RUN_PAYROLL (semantic only for now).
    """

    name = "RUN_PAYROLL"
    domain = "PAYROLL"
    fine_intent = "RUN_PAYROLL"

    supported_by_qb = False
    qb_endpoint = None
    qb_method = None

    def __init__(
        self,
        department: Optional[str] = None,
        period: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
    ):
        payload = {
            "department": department,
            "period": period,
            "raw": raw or {},
        }
        super().__init__(payload)

    def build_qb_request(self) -> Dict[str, Any]:
        return {
            "endpoint": self.qb_endpoint,
            "method": self.qb_method,
            "body": {
                "note": "RUN_PAYROLL is not yet wired to QuickBooks.",
                "payload": self.payload,
            },
        }


# =====================================================================
# Fallback
# =====================================================================

class UnsupportedAction(Action):
    """
    Fallback action when we have a fine_intent that doesn't
    have a direct QuickBooks mapping (or we haven't implemented it yet).
    """

    name = "UNSUPPORTED"
    domain = "GENERIC"
    fine_intent = "UNSUPPORTED"

    supported_by_qb = False
    qb_endpoint = None
    qb_method = None

    def __init__(self, domain: str, fine_intent: str, raw: Dict[str, Any]):
        self.domain = domain
        self.fine_intent = fine_intent
        payload = {"raw": raw}
        super().__init__(payload)

    def build_qb_request(self) -> Dict[str, Any]:
        return {
            "endpoint": None,
            "method": None,
            "body": {
                "note": f"No QuickBooks mapping implemented for {self.domain}/{self.fine_intent}",
                "raw": self.payload["raw"],
            },
        }
