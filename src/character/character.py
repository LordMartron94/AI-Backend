from typing import List, Dict, Union, Any

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.agent import Agent
from src.agents.agent_task_model import AgentTaskModel
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI
from src.character.model.character_configuration_model import CharacterConfigurationModel


class Character:
	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI, agents: Dict[Agent, AgentTaskModel], character_config: CharacterConfigurationModel):
		self._logger: HoornLogger = logger
		self._api: ILargeLanguageModelAPI = api
		self._agents: Dict[Agent, AgentTaskModel] = agents
		self._character_config: CharacterConfigurationModel = character_config
		self._module_separator = f"Characters.{self._character_config.name.replace(' ', '_')}"

	def get_character_name(self) -> str:
		"""
		Retrieves the character name from the configuration model.

		:return: Character name.
		"""

		return self._character_config.name

	def _get_character_prompt(self) -> str:
		return f"""
The character you are imitating is: {self._character_config.name}.

This is a short biography of the character:
{self._character_config.biography}

Here is some standard information about the character's personality:
{self._character_config.personality}
"""

	def converse(self, prior_conversation: List[Dict[str, Union[str, Any]]], current_user_name: str) -> str:
		context = prior_conversation.copy()  # Create a copy of the prior conversation to avoid modifying the original list
		context.append(self._api.construct_message(content=self._get_character_prompt(), role="system"))
		current_response: str = ""

		for agent, task in self._agents.items():
			task.prior_conversation_context = context
			current_response = agent.converse(task, current_character_name=self._character_config.name, current_user_name=current_user_name)

			current_agent_response = f"""
Make sure to use the provided data by {agent.get_name()} as input for your response:
{current_response}
"""

			context.append(self._api.construct_message(content=current_agent_response, role="system"))

		return current_response


