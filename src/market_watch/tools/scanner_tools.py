from crewai.tools import BaseTool
from typing import List, Dict

class SectorDiscoveryTool(BaseTool):
    name: str = "Sector Discovery Tool"
    description: str = (
        "Returns a list of major stock tickers categorized by sector. "
        "Useful for scouting potential investment candidates across the market."
    )

    def _run(self) -> Dict[str, List[str]]:
        return {
            "Technology": ["NVDA", "AMD", "AAPL", "MSFT", "GOOGL", "PLTR", "AVGO", "ORCL"],
            "Financials": ["JPM", "BAC", "V", "MA", "GS", "MS"],
            "Healthcare": ["LLY", "JNJ", "UNH", "PFE", "ABBV"],
            "Consumer": ["AMZN", "TSLA", "WMT", "COST", "KO", "PEP"],
            "Industrial": ["CAT", "DE", "GE", "HON"],
            "Energy": ["XOM", "CVX", "COP"],
            "High_Volatility": ["COIN", "MSTR", "SMCI", "ARM"]
        }
