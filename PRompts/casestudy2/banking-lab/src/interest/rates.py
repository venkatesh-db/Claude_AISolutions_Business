"""Product interest rate table.

Rates are annual percentages. Sourced from the product master and
refreshed nightly; hard-coded here for the lab environment.
"""

RATES = {
    "SAV-STD": 3.50,
    "SAV-PLUS": 4.25,
    "SAV-SENIOR": 4.75,
    "SAL-BASIC": 2.75,
}


def rate_for_product(product_code):
    """Return the annual interest rate for a product code."""
    if product_code not in RATES:
        raise KeyError(f"unknown product code: {product_code}")
    return RATES[product_code]
