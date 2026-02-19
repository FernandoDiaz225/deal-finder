"""
research_agent.py — Market Research Agent

This searches for real multi-family property listings and rental market data
using ADK's built-in Google Search tool.

This agent is used as an AgentTool (not a sub_agent) by the root agent
to avoid the google_search + transfer_to_agent known Google ADK Bug.

Google search import is a built-in ADK tool. 


"""

from google.adk.agents import Agent
from google.adk.tools import google_search

from .prompts import MARKET_RESEARCH_AGENT_PROMPT

research_agent = Agent(
    name="market_research_agent",
    model="gemini-2.5-flash",
    instruction=MARKET_RESEARCH_AGENT_PROMPT,
    description=(
        "Searches for real multi-family property listings and rental "
        "market data. Returns real listings only — never fabricates data."
    ),
    tools=[google_search],
    output_key="market_research",
)
