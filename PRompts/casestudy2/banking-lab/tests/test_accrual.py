"""Tests for daily interest accrual."""

import pytest

from src.interest.accrual import accrue, accrue_many
from src.interest.rates import rate_for_product
from src.ledger.posting import batch_total, post_journal


def test_rate_lookup():
    assert rate_for_product("SAV-STD") == 3.50
    assert rate_for_product("SAV-PLUS") == 4.25


def test_unknown_product_raises():
    with pytest.raises(KeyError):
        rate_for_product("SAV-NOPE")


def test_accrue_returns_two_decimals():
    result = accrue(10000.00)
    assert result == round(result, 2)


def test_accrue_zero_balance():
    assert accrue(0.00) == 0.00


def test_accrue_negative_balance_returns_zero():
    assert accrue(-5000.00) == 0.00


def test_accrue_missing_balance_raises():
    with pytest.raises(ValueError):
        accrue(None)


def test_accrue_higher_rate_gives_more_interest():
    std = accrue(100000.00, "SAV-STD")
    plus = accrue(100000.00, "SAV-PLUS")
    assert plus > std


def test_accrue_many_returns_one_per_account():
    balances = [1000.00, 2000.00, 3000.00]
    assert len(accrue_many(balances)) == 3


def test_batch_total_is_positive():
    balances = [10432.17, 8891.44, 50120.09]
    assert batch_total(balances) > 0


def test_batch_total_skips_negative_balances():
    with_neg = batch_total([10000.00, -5000.00])
    without_neg = batch_total([10000.00])
    assert with_neg == without_neg


def test_batch_total_empty_list():
    assert batch_total([]) == 0.00


def test_journal_has_both_legs():
    entry = post_journal([10000.00, 20000.00])
    assert entry["credit_account"].startswith("GL-")
    assert entry["debit_account"].startswith("GL-")


def test_journal_counts_accounts():
    entry = post_journal([1000.00, 2000.00, 3000.00])
    assert entry["account_count"] == 3


def test_journal_amount_matches_batch_total():
    balances = [10432.17, 8891.44]
    entry = post_journal(balances)
    assert entry["amount"] == batch_total(balances)
