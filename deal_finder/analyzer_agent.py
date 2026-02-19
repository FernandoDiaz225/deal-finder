"""
analyzer_agent.py — Deal Analyzer Agent

Takes market research data and investor preferences, then runs financial
analysis using calculate_mortgage and calculate_cashflow tools.

I used gemini-2.5-flash-lite for higher rate limits (15 RPM, 1000 RPD on
free tier) since this agent only calls deterministic Python tools and
doesn't need the full power of gemini-2.5-flash.
"""

from google.adk.agents import Agent

from .prompts import DEAL_ANALYZER_AGENT_PROMPT
from .tools import calculate_mortgage, calculate_cashflow

analyzer_agent = Agent(
    name="deal_analyzer_agent",
    model="gemini-2.5-flash-lite",
    instruction=DEAL_ANALYZER_AGENT_PROMPT,
    description=(
        "Runs financial analysis on real estate properties using mortgage "
        "and cash flow calculation tools. Produces deal scorecards with "
        "buy/pass verdicts. Delegate after market research is complete."
    ),
    tools=[calculate_mortgage, calculate_cashflow],


    # this stores final response in root agent's 'deal_analysis' variable for later synthesis into final report
    output_key="deal_analysis",
)
