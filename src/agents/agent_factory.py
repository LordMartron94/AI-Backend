from typing import Union, List, Dict, Any

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.agent_config_model import AgentConfigModel
from src.agents.agent_task_model import AgentTaskModel


class AgentFactory:
	def __init__(self, logger: HoornLogger):
		self._logger: HoornLogger = logger
		self._module_separator: str = "AgentFactory"

	def create_agent_config(self, agent_name: str, agent_role: str, agent_backstory: str) -> AgentConfigModel:
		self._logger.debug(f"{self._module_separator}: Creating agent config for {agent_name}")
		return AgentConfigModel(agent_name=agent_name, agent_role=agent_role, agent_backstory=agent_backstory)

	def create_agent_task(self, task_description: str, expected_output: str, prior_conversation: Union[List[Dict[str, Union[str, Any]]], None] = None) -> AgentTaskModel:
		self._logger.debug(f"${{ignore=default}}{self._module_separator}: Creating agent task for {task_description}")

		if prior_conversation is None:
			prior_conversation = []

		return AgentTaskModel(task_description=task_description, expected_output=expected_output, prior_conversation_context=prior_conversation)
