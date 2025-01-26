from langchain_community.tools.tavily_search import TavilySearchResults

# tools = [TavilySearchResults(max_results=1)]

from pydantic import BaseModel, Field

class Router(BaseModel):
    """Call this if you are able to route the user to the appropriate representative."""
    choice: str = Field(description="should be one of: music, customer")

tools = [Router]