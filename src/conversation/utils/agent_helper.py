from typing import Dict

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.agent import Agent
from src.agents.agent_factory import AgentFactory
from src.agents.agent_task_model import AgentTaskModel
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI
from src.character.default_prompts import CHARACTER_AGENT_DEFINITIONS
from src.conversation.default_prompts import CHARACTER_SELECTOR_AGENT_DEFINITIONS, NARRATIVE_AGENT_DEFINITIONS


class AgentHelper:
	"""
	Utility class to help with agent-related tasks.
	"""

	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI):
		self._logger: HoornLogger = logger
		self._api: ILargeLanguageModelAPI = api
		self._agent_factory: AgentFactory = AgentFactory(logger)
		self._module_separator: str = "AgentHelper"

	def _create_agent_from_definition(self, agent_def: Dict) -> (Agent, AgentTaskModel):
		config = self._agent_factory.create_agent_config(
			agent_name=agent_def["name"],
			agent_role=agent_def["role"],
			agent_backstory=agent_def["backstory"],
		)
		task = self._agent_factory.create_agent_task(
			task_description=agent_def["task_description"],
			expected_output=agent_def["expected_output"],
			prior_conversation=[],
		)
		agent = Agent(self._logger, self._api, agent_config=config)
		return agent, task

	def get_character_agents(self) -> Dict[Agent, AgentTaskModel]:
		agents = {}
		for agent_def in CHARACTER_AGENT_DEFINITIONS:
			agent, task = self._create_agent_from_definition(agent_def)
			agents[agent] = task
		return agents

	def get_character_selector_agents(self) -> Dict[Agent, AgentTaskModel]:
		agents = {}
		for agent_def in CHARACTER_SELECTOR_AGENT_DEFINITIONS:
			agent, task = self._create_agent_from_definition(agent_def)
			agents[agent] = task
		return agents

	def get_narrative_agents(self):
		agents = {}
		for agent_def in NARRATIVE_AGENT_DEFINITIONS:
			agent, task = self._create_agent_from_definition(agent_def)
			agents[agent] = task
		return agents

