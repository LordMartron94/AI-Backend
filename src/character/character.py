from typing import List, Dict

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.context.agent import Agent
from src.agents.context.agent_context_model import AgentContextModel
from src.agents.interface_agent import IAgent
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI
from src.character.model.character_configuration_model import CharacterConfigurationModel


class Character:
	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI, config: CharacterConfigurationModel, agents: List[IAgent]):
		self._logger: HoornLogger = logger
		self._api: ILargeLanguageModelAPI = api
		self._config: CharacterConfigurationModel = config
		self._appended: bool = False
		self._agents: List[IAgent] = agents

	def _get_persona_prompt(self) -> str:
		char = self._config.name

		return f"""
The name of the character you will be performing for is {char}.
		
The following is information about who you are (biography):
{self._config.biography}

This is your personality description (personality):
{self._config.personality}

If the character comes from established lore (such as Rumplestiltskin from Once Upon a Time, or Rowena MacLeod from Supernatural, TV Show), then you must be accurate to their established lore.
"""

	def _get_system_prompt(self) -> str:
		return """ 
You are a story agent. Your purpose is to work together with other agents to create realistic responses for a character you'll be performing for.
Later, you will get a few instructions (as bullet points) to go through, this will be defined as ***STORY AGENT INSTRUCTIONS*** until ***END STORY AGENT INSTRUCTIONS***. Everything between that, you must do... Anything else is strictly forbidden. This is to ensure cohesion.
		
It is of vital essence that you do not go beyond your instructions. If your instructions do not include to formulate a response for the character, then you do not formulate a response for the character.	

You MUST ALWAYS work through EACH bullet point, step-by-step, without skipping over any steps or any instructions within steps.
You MUST NEVER do more than is requested. No additional steps.	

Under no circumstances should you generate any dialogue or responses for the character unless a specific instruction explicitly requests it.

Do not include the story agent instructions heading in your response... That will fuck up all the subsequent steps.
Do not include the instructions you got in the response. Execute the instructions and only respond with the answers to the instructions.
"""

	def converse(self, prompt: str, previous_conversation: List[Dict[str, str]], user_name: str) -> str:
		"""
		Converse with the character using the provided prompt.

        :param previous_conversation: The previous conversation history.
        :param prompt: The prompt to be used for conversation.
        :return: The response from the character.
        """
		conv_context = previous_conversation.copy()
		conv_context.append(self._api.construct_message(content=self._get_system_prompt(), role="system"))
		conv_context.append(self._api.construct_message(content=self._get_persona_prompt(), role="system"))
		conv_context.append(self._api.construct_message(content=prompt, role="user"))

		context = AgentContextModel(user_name=user_name, previous_conversation=conv_context, character_model=self._config)

		for agent in self._agents:
			agent.get_agent_response(context=context)

		return context.agent_responses[Agent.WritingAgent]

	def get_name(self) -> str:
		return self._config.name
