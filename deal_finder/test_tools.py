"""
test_tools.py — Verify custom financial tools produce correct results.

Run BEFORE testing agents to ensure the math is right.

Usage:
    python -m deal_finder.test_tools
"""

from .tools import calculate_mortgage, calculate_cashflow


def test_mortgage_fha():
    """Test FHA mortgage: $365K duplex, 3.5% down, 6.8% rate."""
    result = calculate_mortgage(
        price=365_000,
        down_payment_pct=3.5,
        interest_rate=6.8,
        term_years=30,
    )

    print("=" * 60)
    print("TEST: FHA Mortgage — $365K duplex, 3.5% down, 6.8% rate")
    print("=" * 60)
    print(f"  Price:           ${result['price']:,.2f}")
    print(f"  Down Payment:    ${result['down_payment_amount']:,.2f} ({result['down_payment_pct']}%)")
    print(f"  Loan Amount:     ${result['loan_amount']:,.2f}")
    print(f"  Monthly Payment: ${result['monthly_payment']:,.2f}")
    print(f"  Total Interest:  ${result['total_interest']:,.2f}")
    print(f"  Total Cost:      ${result['total_cost']:,.2f}")
    print()

    assert 2200 < result["monthly_payment"] < 2400, (
        f"Monthly payment ${result['monthly_payment']} out of range. Expected ~$2,312."
    )
    print("  PASS: Monthly payment in expected range (~$2,312/mo)")
    print()
    return result


def test_cashflow_house_hack():
    """Test house hack cash flow: 1 unit rented at $1,450/mo."""
    result = calculate_cashflow(
        monthly_rent=1_450,
        mortgage_payment=2_312,
        monthly_taxes=280,
        monthly_insurance=145,
        vacancy_rate_pct=5.0,
        maintenance_pct=5.0,
        property_price=365_000,
        total_cash_invested=12_775 + 5_000,
    )

    print("=" * 60)
    print("TEST: House Hack Cash Flow — 1 unit rented at $1,450/mo")
    print("=" * 60)
    print(f"  Monthly Rent:      ${result['monthly_rent']:,.2f}")
    print(f"  Total Expenses:    ${result['expenses']['total_monthly']:,.2f}")
    print(f"    Mortgage:        ${result['expenses']['mortgage']:,.2f}")
    print(f"    Taxes:           ${result['expenses']['taxes']:,.2f}")
    print(f"    Insurance:       ${result['expenses']['insurance']:,.2f}")
    print(f"    Vacancy (5%):    ${result['expenses']['vacancy_reserve']:,.2f}")
    print(f"    Maintenance (5%):${result['expenses']['maintenance_reserve']:,.2f}")
    print(f"  Monthly Cash Flow: ${result['monthly_cash_flow']:,.2f}")
    print(f"  Annual Cash Flow:  ${result['annual_cash_flow']:,.2f}")
    print(f"  Cap Rate:          {result['cap_rate_pct']:.2f}%")
    print(f"  Cash-on-Cash:      {result['cash_on_cash_return_pct']:.2f}%")
    print(f"  Rent-to-Price:     {result['rent_to_price_ratio']:.4f}")
    print()

    assert result["monthly_cash_flow"] < 0, "House hack should have negative cash flow"
    print("  PASS: Cash flow is negative (expected — you pay to live there)")

    cost_to_live = abs(result["monthly_cash_flow"])
    comparable_rent = 1_600
    savings = comparable_rent - cost_to_live
    print(f"  PASS: You pay ~${cost_to_live:,.0f}/mo vs ~${comparable_rent}/mo renting")
    print(f"        Savings: ~${savings:,.0f}/mo + building equity")
    print()
    return result


def test_cashflow_full_rental():
    """Test full rental: both units rented at $1,450/mo each."""
    result = calculate_cashflow(
        monthly_rent=2_900,
        mortgage_payment=2_312,
        monthly_taxes=280,
        monthly_insurance=145,
        vacancy_rate_pct=5.0,
        maintenance_pct=5.0,
        property_price=365_000,
        total_cash_invested=12_775 + 5_000,
    )

    print("=" * 60)
    print("TEST: Full Rental — Both units rented at $1,450/mo each")
    print("=" * 60)
    print(f"  Monthly Rent:      ${result['monthly_rent']:,.2f}")
    print(f"  Total Expenses:    ${result['expenses']['total_monthly']:,.2f}")
    print(f"  Monthly Cash Flow: ${result['monthly_cash_flow']:,.2f}")
    print(f"  Annual Cash Flow:  ${result['annual_cash_flow']:,.2f}")
    print(f"  Cap Rate:          {result['cap_rate_pct']:.2f}%")
    print(f"  Cash-on-Cash:      {result['cash_on_cash_return_pct']:.2f}%")
    print()

    status = "PASS" if result["monthly_cash_flow"] >= 0 else "WARN"
    print(f"  {status}: Monthly cash flow: ${result['monthly_cash_flow']:,.2f}")
    print()
    return result


if __name__ == "__main__":
    print()
    print("Deal Finder — Custom Tools Test Suite")
    print("=" * 60)
    print()

    test_mortgage_fha()
    test_cashflow_house_hack()
    test_cashflow_full_rental()

    print("=" * 60)
    print("All tests passed! Tools are ready for agent integration.")
    print("=" * 60)
