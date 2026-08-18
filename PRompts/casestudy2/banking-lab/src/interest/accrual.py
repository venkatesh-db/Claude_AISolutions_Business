"""Daily interest accrual for savings accounts.

Interest is accrued daily on the closing balance using a simple
365-day convention. Accrued amounts are posted to the ledger by
the nightly batch (see src/ledger/posting.py).
"""

from src.interest.rates import rate_for_product

DAYS_IN_YEAR = 365


def daily_rate(product_code):
    """Return the annual rate for a product, as a percentage."""
    return rate_for_product(product_code)


def accrue(balance, product_code="SAV-STD"):
    """Accrue one day of interest on a single account balance.

    Args:
        balance: the account closing balance for the day
        product_code: the savings product, used to look up the rate

    Returns:
        The interest accrued for one day, rounded to 2 decimal places.
    """
    if balance is None:
        raise ValueError("balance is required")

    if balance < 0:
        # overdrawn accounts do not accrue credit interest
        return 0.00

    annual_rate = daily_rate(product_code)

    # convert the annual percentage to a daily fraction and apply it
    interest = balance * (annual_rate / 100) / DAYS_IN_YEAR

    return round(interest, 2)


def accrue_many(balances, product_code="SAV-STD"):
    """Accrue one day of interest for a list of account balances."""
    return [accrue(b, product_code) for b in balances]
