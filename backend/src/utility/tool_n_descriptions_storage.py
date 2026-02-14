from langchain.utilities import WikipediaAPIWrapper
from langchain.tools import DuckDuckGoSearchRun
from langchain.chains import LLMMathChain

descriptions = {
    "wikipedia": "Useful for when you need to look up a company, company description or person on wikipedia.",
    "duckduckgo": "Useful for when you need to do a search on the internet to find specific informations about a specific topic.",
    "llm-math": "Useful for when you need to calculate costs, subtotals, totals or in general have to do mathematical calculations.",
    "Basic LLM": "use this tool when you are asked questions that a assistant can answer Dont use this tool if u are asked questions abouth math, like calculating subtotals.",
}
tool_no_llm = {"wikipedia": WikipediaAPIWrapper, "duckduckgo": DuckDuckGoSearchRun}
tool_llm = {"llm-math": LLMMathChain}


# duckduckgo
# Useful for when you need to do a search on the internet to find specific informations about a company or a specific product the company produces, aswell as its prices. Be specific with your input.
