"""Generate the nightly batch fixture and show the reconciliation delta.

Usage:
    python3 fixtures/make_batch.py
    python3 fixtures/make_batch.py 5000
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interest.accrual import accrue_many
from src.ledger.posting import batch_total

SEED = 42


def make_balances(count):
    random.seed(SEED)
    return [round(random.uniform(1000, 250000), 2) for _ in range(count)]


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    balances = make_balances(count)

    per_account_sum = round(sum(accrue_many(balances)), 2)
    control_total = batch_total(balances)
    delta = round(per_account_sum - control_total, 2)

    print(f"accounts             : {count}")
    print(f"sum of per-account   : {per_account_sum:>12.2f}")
    print(f"GL control total     : {control_total:>12.2f}")
    print(f"delta                : {delta:>12.2f}")
    print()
    print("PASS" if delta == 0 else "FAIL - reconciliation does not balance")


if __name__ == "__main__":
    main()
