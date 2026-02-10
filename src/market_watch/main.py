from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from src.market_watch.crew import MarketWatchCrew

def run():
    # You can loop through your specific stocks here
    inputs = {
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    MarketWatchCrew().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()