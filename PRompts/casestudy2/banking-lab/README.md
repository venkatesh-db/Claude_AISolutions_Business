# interest-accrual

Daily interest accrual and nightly general ledger posting for retail
savings products.

## What it does

Each night the batch computes one day of interest on the closing
balance of every savings account, and posts a single control total to
the general ledger. Per-account amounts are posted separately by the
account service.

Interest uses a simple 365-day convention. Rates come from the product
master; for this environment they are held in `src/interest/rates.py`.

## Layout

```
src/interest/accrual.py    per-account daily accrual
src/interest/rates.py      product rate table
src/ledger/posting.py      batch control total and journal entry
tests/test_accrual.py      unit tests
fixtures/make_batch.py     generates a batch and prints the delta
evidence/                  reconciliation exception reports
```

## Running

```bash
python3 -m pytest -q
python3 fixtures/make_batch.py
```

## Known issue

The nightly reconciliation has been raising an exception since
2026-07-02. The GL control total does not agree with the sum of the
per-account accruals. The difference is small — under a rupee on a
5,000 account batch — but the tolerance is zero, so the batch fails
every night and is cleared manually by operations.

Latest exception report: `evidence/recon-fail-2026-08-16.txt`

## Contacts

Owner: Retail Deposits Engineering
Escalation: #retail-deposits-oncall
