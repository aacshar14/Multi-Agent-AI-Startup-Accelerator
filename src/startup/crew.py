import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Union

from tools.custom_tool import (
    web_search_tool,
    scrape_website_tool,
    domain_check_tool,
    code_editor_tool,
    browser_test_tool,
    database_tool,
    api_test_tool,
    cloud_deploy_tool,
    docker_tool,
    domain_setup_tool,
    monitoring_tool,
)

@CrewBase
class StartupCrew:
    """Startup crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, agent_configs=None):
        super().__init__()
        self.agent_configs = agent_configs or {}

    def _get_agent_config(self, agent_id):
        """Get agent configuration with dynamic LLM settings"""
        config = self.agents_config[agent_id].copy()
        if self.agent_configs and agent_id in self.agent_configs:
            agent_config = self.agent_configs[agent_id]
            if agent_config.get('llm'):
                config['llm'] = agent_config['llm']
            if agent_config.get('api_key'):
                os.environ[f"{config['llm'].upper()}_API_KEY"] = agent_config['api_key']
        return config

    @agent
    def ideator(self) -> Agent:
        return Agent(
            config=self._get_agent_config('ideator'),
            verbose=True
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self._get_agent_config('researcher'),
            tools=[web_search_tool, scrape_website_tool],
            verbose=True
        )

    @agent
    def product_designer(self) -> Agent:
        return Agent(
            config=self._get_agent_config('product_designer'),
            verbose=True
        )

    @agent
    def brand_expert(self) -> Agent:
        return Agent(
            config=self._get_agent_config('brand_expert'),
            tools=[web_search_tool, domain_check_tool],
            verbose=True
        )

    @agent
    def pitch_writer(self) -> Agent:
        return Agent(
            config=self._get_agent_config('pitch_writer'),
            verbose=True
        )

    @agent
    def frontend_dev(self) -> Agent:
        return Agent(
            config=self._get_agent_config('frontend_dev'),
            tools=[code_editor_tool, browser_test_tool],
            verbose=True
        )

    @agent
    def backend_dev(self) -> Agent:
        return Agent(
            config=self._get_agent_config('backend_dev'),
            tools=[code_editor_tool, database_tool, api_test_tool],
            verbose=True
        )

    @agent
    def infra_tech(self) -> Agent:
        return Agent(
            config=self._get_agent_config('infra_tech'),
            tools=[cloud_deploy_tool, docker_tool, domain_setup_tool, monitoring_tool],
            verbose=True
        )

    @task
    def generate_startup_ideas(self) -> Task:
        return Task(
            config=self.tasks_config['generate_startup_ideas'],
            agent=self.ideator(),
            output_file='startup_idea.md'
        )

    @task
    def conduct_market_research(self) -> Task:
        return Task(
            config=self.tasks_config['conduct_market_research'],
            agent=self.researcher(),
            context=[self.generate_startup_ideas()],
            output_file='market_research.md'
        )

    @task
    def design_product_experience(self) -> Task:
        return Task(
            config=self.tasks_config['design_product_experience'],
            agent=self.product_designer(),
            context=[self.conduct_market_research()],
            output_file='product_Experience.md'
        )

    @task
    def create_brand_identity(self) -> Task:
        return Task(
            config=self.tasks_config['create_brand_identity'],
            agent=self.brand_expert(),
            context=[self.conduct_market_research()],
            output_file='brand_identity.md'
        )

    @task
    def write_investor_pitch(self) -> Task:
        return Task(
            config=self.tasks_config['write_investor_pitch'],
            agent=self.pitch_writer(),
            context=[
                self.conduct_market_research(),
                self.design_product_experience(),
                self.create_brand_identity(),
               
            ],
             output_file='investor_pitch.md'
        )

    @task
    def develop_frontend_mvp(self) -> Task:
        return Task(
            config=self.tasks_config['develop_frontend_mvp'],
            agent=self.frontend_dev(),
            context=[self.design_product_experience(), self.create_brand_identity()],
            output_file='frontend_code.md'
        )

    @task
    def build_backend_api(self) -> Task:
        return Task(
            config=self.tasks_config['build_backend_api'],
            agent=self.backend_dev(),
            context=[self.design_product_experience()],
            output_file='backend_code.md'
        )

    @task
    def deploy_mvp_infrastructure(self) -> Task:
        return Task(
            config=self.tasks_config['deploy_mvp_infrastructure'],
            agent=self.infra_tech(),
            context=[
                self.create_brand_identity(),
                self.develop_frontend_mvp(),
                self.build_backend_api()
            ],
            output_file='final_deliverable.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Startup crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )