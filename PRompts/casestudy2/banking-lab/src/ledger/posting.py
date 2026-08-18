"""Nightly interest posting to the general ledger.

The batch computes a single control total for the day's interest
accrual and posts it as one journal line. The per-account amounts
are posted separately by the account service.
"""

from src.interest.rates import rate_for_product

DAYS_IN_YEAR = 365


def batch_total(balances, product_code="SAV-STD"):
    """Compute the day's total interest across all accounts.

    This is the control total posted to the general ledger. It must
    agree with the sum of the per-account accruals.

    Args:
        balances: closing balances for every account in the batch
        product_code: the savings product, used to look up the rate

    Returns:
        The total interest for the batch, rounded to 2 decimal places.
    """
    annual_rate = rate_for_product(product_code)

    total = 0.0
    for balance in balances:
        if balance is None or balance < 0:
            continue
        total += balance * (annual_rate / 100) / DAYS_IN_YEAR

    return round(total, 2)


def post_journal(balances, product_code="SAV-STD"):
    """Build the journal entry for the nightly interest run."""
    total = batch_total(balances, product_code)

    return {
        "account_count": len(balances),
        "credit_account": "GL-4100-INTEREST-PAYABLE",
        "debit_account": "GL-8200-INTEREST-EXPENSE",
        "amount": total,
    }
