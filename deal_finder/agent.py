"""
agent.py — Root Deal Finder Agent

Entry point for the ADK application. ADK discovers the root_agent variable.
We are using Gemini API (Google LLM's Api) for the root and research agents, 
and gemini-2.5-flash-lite for the analyzer.

Architecture:
We have a single Root Agent that serves as the main orchestrator. It uses one AgentTool to perform 
market research (the Market Research Agent) and has one sub_agent for deal analysis (the Deal Analyzer Agent).

    Deal Finder (Root)
        ├── Market Research Agent (as AgentTool — uses google_search)
        └── Deal Analyzer Agent (as sub_agent — uses custom calc tools)

The Market Research Agent is wrapped as an AgentTool instead of a sub_agent
due to a known ADK limitation (github.com/google/adk-python/issues/53)
where google_search conflicts with transfer_to_agent function calling.

This is the main orchestrator agent that interacts with the user, gathers preferences,
and coordinates the research and analysis agents to find and evaluate real estate deals.

Updates I can make to this project
MARKET_RESEARCH_AGENT_PROMPT — add explicit instructions like 
"verify the listing says duplex/triplex/fourplex before including it" or "discard any single-family or condo results." 
or prompts.py in general 

"""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .prompts import ROOT_AGENT_PROMPT
from .research_agent import research_agent
from .analyzer_agent import analyzer_agent

root_agent = Agent(
    name="deal_finder",
    model="gemini-2.5-flash-lite",
    instruction=ROOT_AGENT_PROMPT,
    description="Real estate deal finder specializing in house stacking.",
    tools=[AgentTool(agent=research_agent)],
    sub_agents=[analyzer_agent],
)
