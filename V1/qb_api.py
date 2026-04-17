# qb_api.py

"""
High-level QuickBooks helpers used by the Lantern pipeline.

This is a thin wrapper around quickbook_api so that
ActionExecutor and the rest of the pipeline can just import qb_api.
"""

from qb.quickbook_api import (
    create_bill as qb_create_bill,
    pay_bill as qb_pay_bill,
    create_invoice as qb_create_invoice,
    run_balance_sheet_report as qb_run_balance_sheet_report,
)


def create_bill(vendor, amount, date=None, service=None, po_id=None):
    return qb_create_bill(
        vendor=vendor,
        amount=amount,
        date=date,
        service=service,
        po_id=po_id,
    )


def pay_bill(vendor, amount, date=None, bill_id=None, payment_method=None):
    return qb_pay_bill(
        vendor=vendor,
        amount=amount,
        date=date,
        bill_id=bill_id,
        payment_method=payment_method,
    )


def create_invoice(customer, amount, date=None, item="Service"):
    return qb_create_invoice(
        customer=customer,
        amount=amount,
        date=date,
        item=item,
    )


def run_balance_sheet_report(start_date=None, end_date=None):
    return qb_run_balance_sheet_report(
        start_date=start_date,
        end_date=end_date,
    )
