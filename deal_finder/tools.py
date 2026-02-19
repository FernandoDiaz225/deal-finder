"""
tools.py — Custom financial calculation tools for the Deal Finder agents.

These are registered as ADK tools so the Deal Analyzer Agent can call them
for exact, deterministic financial math. LLMs are bad at arithmetic — these
tools ensure every number in the deal scorecard is correct.

Pattern: The agent REASONS about WHEN to calculate. The TOOLS do the actual math.

Retry Logic:
    All tools are wrapped with exponential backoff retry to handle Gemini API
    rate limits (RESOURCE_EXHAUSTED errors). The retry decorator catches these
    errors at the tool level so the agent doesn't need to handle them.

    Backoff schedule: 2s → 4s → 8s → 16s → 32s (5 retries max)

    Why retry instead of caching:
    - Rate limits are transient (reset every minute on free tier)
    - Caching only helps for duplicate queries (rare in practice)
    - Retry directly solves the #1 failure mode we observed in testing
"""

import time
import functools
import logging

logger = logging.getLogger(__name__)


def retry_on_rate_limit(max_retries: int = 5, base_delay: float = 2.0):
    """Decorator that retries a function with exponential backoff on rate limit errors.

    When the Gemini free tier hits its RPM (requests per minute) limit, the API
    returns a RESOURCE_EXHAUSTED error. This decorator catches that and retries
    with increasing delays: 2s, 4s, 8s, 16s, 32s.

    Args:
        max_retries: Maximum number of retry attempts (default 5).
        base_delay: Initial delay in seconds, doubles each retry (default 2.0).

    Returns:
        Decorated function that automatically retries on rate limit errors.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_str = str(e).lower()
                    if "resource_exhausted" in error_str or "rate limit" in error_str:
                        last_exception = e
                        if attempt < max_retries:
                            delay = base_delay * (2 ** attempt)
                            logger.warning(
                                f"Rate limit hit on {func.__name__}, "
                                f"retry {attempt + 1}/{max_retries} in {delay}s"
                            )
                            time.sleep(delay)
                        else:
                            logger.error(
                                f"Rate limit: {func.__name__} failed after "
                                f"{max_retries} retries"
                            )
                    else:
                        raise  # Non-rate-limit error, don't retry
            raise last_exception
        return wrapper
    return decorator


@retry_on_rate_limit(max_retries=5, base_delay=2.0)
def calculate_mortgage(
    price: float,
    down_payment_pct: float,
    interest_rate: float,
    term_years: int = 30,
) -> dict:
    """Calculate monthly mortgage payment using standard amortization formula.

    Args:
        price: Property purchase price in dollars (e.g., 365000).
        down_payment_pct: Down payment as a percentage (e.g., 3.5 for FHA).
        interest_rate: Annual interest rate as a percentage (e.g., 6.8).
        term_years: Loan term in years (default 30).

    Returns:
        Dictionary with loan_amount, monthly_payment, total_interest, total_cost.
    """
    if price <= 0:
        return {"error": "Price must be positive."}
    if not (0 <= down_payment_pct <= 100):
        return {"error": "Down payment percentage must be between 0 and 100."}
    if interest_rate <= 0:
        return {"error": "Interest rate must be positive."}
    if term_years <= 0:
        return {"error": "Loan term must be positive."}

    down_payment = price * (down_payment_pct / 100)
    loan_amount = price - down_payment
    monthly_rate = (interest_rate / 100) / 12
    num_payments = term_years * 12

    if loan_amount == 0:
        return {
            "price": round(price, 2),
            "down_payment_pct": down_payment_pct,
            "down_payment_amount": round(down_payment, 2),
            "loan_amount": 0.0,
            "monthly_payment": 0.0,
            "total_interest": 0.0,
            "total_cost": round(price, 2),
        }

    # Standard amortization formula: M = P[r(1+r)^n] / [(1+r)^n - 1]
    monthly_payment = loan_amount * (
        (monthly_rate * (1 + monthly_rate) ** num_payments)
        / ((1 + monthly_rate) ** num_payments - 1)
    )

    total_paid = monthly_payment * num_payments
    total_interest = total_paid - loan_amount

    return {
        "price": round(price, 2),
        "down_payment_pct": down_payment_pct,
        "down_payment_amount": round(down_payment, 2),
        "loan_amount": round(loan_amount, 2),
        "interest_rate": interest_rate,
        "term_years": term_years,
        "monthly_payment": round(monthly_payment, 2),
        "total_interest": round(total_interest, 2),
        "total_cost": round(down_payment + total_paid, 2),
    }


@retry_on_rate_limit(max_retries=5, base_delay=2.0)
def calculate_cashflow(
    monthly_rent: float,
    mortgage_payment: float,
    monthly_taxes: float,
    monthly_insurance: float,
    vacancy_rate_pct: float = 5.0,
    maintenance_pct: float = 5.0,
    property_price: float = 0.0,
    total_cash_invested: float = 0.0,
) -> dict:
    """Calculate cash flow and investment metrics for a rental property.

    Args:
        monthly_rent: Total monthly rental income from ALL rented units.
        mortgage_payment: Monthly mortgage payment (P&I).
        monthly_taxes: Monthly property tax estimate.
        monthly_insurance: Monthly insurance estimate.
        vacancy_rate_pct: Expected vacancy rate as percentage (default 5%).
        maintenance_pct: Maintenance reserve as percentage (default 5%).
        property_price: Purchase price (for cap rate calculation).
        total_cash_invested: Down payment + closing costs (for cash-on-cash).

    Returns:
        Dictionary with cash flow, cap rate, cash-on-cash return, expenses.
    """
    if monthly_rent < 0 or mortgage_payment < 0:
        return {"error": "Rent and mortgage must be non-negative."}

    vacancy_reserve = monthly_rent * (vacancy_rate_pct / 100)
    maintenance_reserve = monthly_rent * (maintenance_pct / 100)

    total_monthly_expenses = (
        mortgage_payment
        + monthly_taxes
        + monthly_insurance
        + vacancy_reserve
        + maintenance_reserve
    )

    monthly_cash_flow = monthly_rent - total_monthly_expenses
    annual_cash_flow = monthly_cash_flow * 12

    # NOI = Rent - operating expenses (excludes mortgage)
    annual_noi = (
        monthly_rent - vacancy_reserve - maintenance_reserve
        - monthly_taxes - monthly_insurance
    ) * 12

    # Cap Rate = Annual NOI / Property Price
    cap_rate = (annual_noi / property_price * 100) if property_price > 0 else 0.0

    # Cash-on-Cash Return = Annual Cash Flow / Total Cash Invested
    cash_on_cash = (
        (annual_cash_flow / total_cash_invested * 100)
        if total_cash_invested > 0 else 0.0
    )

    # Rent-to-Price Ratio
    rent_to_price = (monthly_rent / property_price) if property_price > 0 else 0.0

    return {
        "monthly_rent": round(monthly_rent, 2),
        "expenses": {
            "mortgage": round(mortgage_payment, 2),
            "taxes": round(monthly_taxes, 2),
            "insurance": round(monthly_insurance, 2),
            "vacancy_reserve": round(vacancy_reserve, 2),
            "maintenance_reserve": round(maintenance_reserve, 2),
            "total_monthly": round(total_monthly_expenses, 2),
        },
        "monthly_cash_flow": round(monthly_cash_flow, 2),
        "annual_cash_flow": round(annual_cash_flow, 2),
        "annual_noi": round(annual_noi, 2),
        "cap_rate_pct": round(cap_rate, 2),
        "cash_on_cash_return_pct": round(cash_on_cash, 2),
        "rent_to_price_ratio": round(rent_to_price, 4),
    }
