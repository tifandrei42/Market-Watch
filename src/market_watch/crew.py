from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import yaml
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import BraveSearchTool
from .tools.analysis_tools import (
    ChartGenerationTool, 
    TechnicalAnalysisTool, 
    FundamentalDataTool
)
from .tools.reporting_tools import WordReportTool
from .tools.scanner_tools import SectorDiscoveryTool

@CrewBase
class MarketWatchCrew():
    """Market Watch multi-agent orchestration"""
    
    # Load configs
    agents_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../config/agents.yaml')
    tasks_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../config/tasks.yaml')

    @property
    def llm(self):
        return "gemini/gemini-flash-latest"

    # --- AGENTS ---
    @agent
    def market_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['market_scout'],
            tools=[SectorDiscoveryTool(), BraveSearchTool()],
            verbose=True,
            llm=self.llm
        )

    @agent
    def technical_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['technical_analyst'],
            tools=[ChartGenerationTool(), TechnicalAnalysisTool()],
            verbose=True,
            llm=self.llm
        )

    @agent
    def fundamental_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['fundamental_analyst'],
            tools=[FundamentalDataTool(), BraveSearchTool()],
            verbose=True,
            llm=self.llm
        )

    @agent
    def risk_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['risk_manager'],
            tools=[BraveSearchTool()],
            verbose=True,
            llm=self.llm
        )

    @agent
    def chief_investment_officer(self) -> Agent:
        return Agent(
            config=self.agents_config['chief_investment_officer'],
            verbose=True,
            llm=self.llm
        )

    @agent
    def reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['reporter'],
            tools=[WordReportTool()],
            verbose=True,
            llm=self.llm
        )

    # --- TASKS ---
    @task
    def scout_task(self) -> Task:
        return Task(
            config=self.tasks_config['scout_task'],
            agent=self.market_scout()
        )

    @task
    def technical_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['technical_analysis_task'],
            agent=self.technical_analyst()
        )

    @task
    def fundamental_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['fundamental_analysis_task'],
            agent=self.fundamental_analyst()
        )

    @task
    def risk_assessment_task(self) -> Task:
        return Task(
            config=self.tasks_config['risk_assessment_task'],
            agent=self.risk_manager()
        )

    @task
    def investment_decision_task(self) -> Task:
        return Task(
            config=self.tasks_config['investment_decision_task'],
            agent=self.chief_investment_officer()
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            agent=self.reporter()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=1 # Respect Gemini Free Tier - Very Conservative
        )