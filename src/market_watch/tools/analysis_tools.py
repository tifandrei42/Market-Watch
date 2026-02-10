import yfinance as yf
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class ChartGenerationToolInput(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol (e.g., 'NVDA', 'AAPL').")

class ChartGenerationTool(BaseTool):
    name: str = "Chart Generation Tool"
    description: str = (
        "Generates a 1-year logarithmic price chart for a given stock ticker using yfinance and matplotlib. "
        "Saves the chart as a PNG file in the 'output' directory and returns the file path."
    )
    args_schema: Type[BaseModel] = ChartGenerationToolInput

    def _run(self, ticker: str) -> str:
        try:
            # Fetch data
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            
            if hist.empty:
                return f"Error: No data found for ticker {ticker}"

            # Ensure output directory exists
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Create Plot
            plt.figure(figsize=(10, 6))
            plt.plot(hist.index, hist['Close'], label=f'{ticker} Close Price')
            plt.yscale('log')
            plt.title(f'{ticker} Price History (1 Year Logarithmic)')
            plt.xlabel('Date')
            plt.ylabel('Price (Log Scale)')
            plt.legend()
            plt.grid(True, which="both", ls="-", alpha=0.2)

            # Save Plot
            file_path = os.path.join(output_dir, f"{ticker}_chart.png")
            plt.savefig(file_path)
            plt.close()

            return f"Chart saved successfully at: {file_path}"
        except Exception as e:
            return f"Error generating chart for {ticker}: {str(e)}"

class TechnicalAnalysisToolInput(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol.")

class TechnicalAnalysisTool(BaseTool):
    name: str = "Technical Analysis Tool"
    description: str = (
        "Performs technical analysis on a stock including RSI, MACD, and SMA. "
        "Returns a summary of the indicators."
    )
    args_schema: Type[BaseModel] = TechnicalAnalysisToolInput

    def _run(self, ticker: str) -> str:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo")
            
            if df.empty:
                return f"No data for {ticker}"

            # Calculate Indicators
            # RSI
            df.ta.rsi(length=14, append=True)
            # MACD
            df.ta.macd(append=True)
            # SMA
            df.ta.sma(length=50, append=True)
            df.ta.sma(length=200, append=True)

            latest = df.iloc[-1]
            
            # Format Output
            rsi = latest['RSI_14']
            macd = latest['MACD_12_26_9']
            macdsignal = latest['MACDs_12_26_9']
            sma50 = latest['SMA_50']
            sma200 = latest['SMA_200']
            price = latest['Close']

            analysis = f"Technical Analysis for {ticker} (Price: ${price:.2f}):\n"
            analysis += f"- RSI (14): {rsi:.2f} ({'Overbought' if rsi>70 else 'Oversold' if rsi<30 else 'Neutral'})\n"
            analysis += f"- MACD: {macd:.4f} (Signal: {macdsignal:.4f}) -> {'Bullish' if macd > macdsignal else 'Bearish'} Crossover\n"
            analysis += f"- SMA 50: ${sma50:.2f} | SMA 200: ${sma200:.2f}\n"
            analysis += f"- Trend: {'Bullish' if price > sma200 else 'Bearish'} (vs 200 SMA)"

            return analysis

        except Exception as e:
            return f"Error performing TA on {ticker}: {str(e)}"

class FundamentalDataToolInput(BaseModel):
    ticker: str = Field(..., description="The stock ticker symbol.")

class FundamentalDataTool(BaseTool):
    name: str = "Fundamental Data Tool"
    description: str = (
        "Fetches key fundamental metrics for a stock: Market Cap, P/E Ratio, EPS, "
        "52 Week High/Low, and Sector."
    )
    args_schema: Type[BaseModel] = FundamentalDataToolInput

    def _run(self, ticker: str) -> str:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return (
                f"Fundamentals for {ticker}:\n"
                f"- Name: {info.get('longName', 'N/A')}\n"
                f"- Sector: {info.get('sector', 'N/A')}\n"
                f"- Market Cap: ${info.get('marketCap', 0):,}\n"
                f"- P/E Ratio: {info.get('forwardPE', 'N/A')}\n"
                f"- EPS (Trailing): {info.get('trailingEps', 'N/A')}\n"
                f"- 52 Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}\n"
                f"- 52 Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}\n"
            )
        except Exception as e:
            return f"Error fetching fundamentals for {ticker}: {str(e)}"
