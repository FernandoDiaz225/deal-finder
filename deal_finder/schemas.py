"""
schemas.py — Structured output schemas for the Deal Finder agents.

These schemas define the JSON structure that agents produce at each stage.
They serve as documentation and can be referenced in agent prompts to
enforce consistent output formatting.
"""

# Schema for the Root Agent's extracted investor preferences
INVESTOR_PREFERENCES_SCHEMA = {
    "target_city": "string — city or metro area (e.g., 'Phoenix metro')",
    "max_budget": "number — maximum purchase price in dollars",
    "property_type": "string — 'duplex', 'triplex', or 'fourplex'",
    "down_payment": "number — cash available for down payment in dollars",
    "financing_type": "string — 'FHA' (3.5% down), 'Conventional' (5-20%), or 'VA' (0%)",
    "investment_goal": "string — 'house_hack', 'pure_rental', or 'house_hack_then_rental'",
    "additional_notes": "string — any extra preferences (e.g., 'near ASU', 'good schools')",
}

# Schema for each listing the Market Research Agent finds
LISTING_SCHEMA = {
    "address": "string — full street address",
    "city": "string",
    "state": "string",
    "zip_code": "string",
    "list_price": "number — asking price in dollars",
    "property_type": "string — duplex/triplex/fourplex",
    "units": "number — total unit count",
    "bedrooms_per_unit": "string — e.g., '2br/1ba each' or '3br/2ba + 2br/1ba'",
    "square_footage": "number or null",
    "year_built": "number or null",
    "days_on_market": "number or null",
    "listing_url": "string — link to Zillow/Redfin/Realtor.com listing",
    "estimated_rent_per_unit": "number — monthly rent estimate based on comps",
    "source": "string — where the data came from",
}

# Schema for the Market Research Agent's full output
MARKET_BRIEF_SCHEMA = {
    "target_area": "string",
    "search_date": "string — ISO date",
    "listings_found": ["<LISTING_SCHEMA>"],
    "average_rent_range": {
        "low": "number",
        "high": "number",
    },
    "market_notes": "string — general observations about the market",
    "data_quality_disclaimer": "string — note about data freshness and accuracy",
}

# Schema for a single property's deal scorecard
DEAL_SCORECARD_SCHEMA = {
    "address": "string",
    "list_price": "number",
    "property_type": "string",
    "financing": {
        "down_payment_pct": "number",
        "down_payment_amount": "number",
        "loan_amount": "number",
        "interest_rate": "number",
        "term_years": "number",
        "monthly_mortgage": "number",
    },
    "income": {
        "units_rented": "number — how many units produce rental income",
        "total_monthly_rent": "number",
        "owner_occupied_unit": "string or null — which unit you live in",
    },
    "expenses": {
        "mortgage": "number — monthly",
        "taxes": "number — monthly",
        "insurance": "number — monthly",
        "vacancy_reserve": "number — monthly",
        "maintenance_reserve": "number — monthly",
        "total_monthly": "number",
    },
    "analysis": {
        "monthly_cash_flow": "number — can be negative for house hack",
        "annual_cash_flow": "number",
        "cap_rate_pct": "number",
        "cash_on_cash_return_pct": "number",
        "rent_to_price_ratio": "number",
        "cost_to_live": "number — what you pay monthly as owner-occupant",
        "comparable_rent": "number — what a similar unit rents for",
        "monthly_savings_vs_renting": "number",
    },
    "verdict": "string — 'STRONG BUY', 'SOLID HOUSE HACK', 'MARGINAL', or 'PASS'",
    "verdict_reasoning": "string — plain-language explanation",
}

# Schema for the final deal report
DEAL_REPORT_SCHEMA = {
    "investor_preferences": "<INVESTOR_PREFERENCES_SCHEMA>",
    "market_brief": "<MARKET_BRIEF_SCHEMA>",
    "scorecards": ["<DEAL_SCORECARD_SCHEMA>"],
    "recommendation_summary": "string — overall recommendation across all properties",
}
