import json
from pathlib import Path
from typing import Dict, List, Union, Any, Tuple

import pydantic

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.agent import Agent
from src.agents.agent_task_model import AgentTaskModel
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI
from src.character.character import Character
from src.character.model.character_configuration_model import CharacterConfigurationModel
from src.constants import PROJECT_ROOT
from src.conversation.utils.agent_helper import AgentHelper
from src.conversation.utils.response_to_json import ResponseToJson

class CharacterSummaryOutputModel(pydantic.BaseModel):
	character_name: str
	feeling: str
	thinking: str
	motivated_to: str


class ConverseOutputModel(pydantic.BaseModel):
	final_response: str
	characters_summary_output: List[CharacterSummaryOutputModel]


class CharacterManager:
	"""
	Delegate of Conversation Manager to handle smooth roleplay between multiple characters at once.
	"""

	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI):
		self._logger: HoornLogger = logger
		self._module_separator = "ConversationManager.CharacterManager"
		self._api: ILargeLanguageModelAPI = api
		self._agent_helper: AgentHelper = AgentHelper(logger=logger, api=api)
		self._response_to_json: ResponseToJson = ResponseToJson(logger)

		self._all_characters: Dict[str, Character] = {}

		self._load_ai_characters(self._agent_helper.get_character_agents())
		self._character_selector_agents: Dict[Agent, AgentTaskModel] = self._agent_helper.get_character_selector_agents()
		self._narrative_agents: Dict[Agent, AgentTaskModel] = self._agent_helper.get_narrative_agents()

	def _load_ai_characters(self, agents: Dict[Agent, AgentTaskModel]) -> None:
		with open(Path(PROJECT_ROOT, "data/characters.json"), "r") as file:
			characters_data: List[Dict] = json.load(file)
			for character_data in characters_data:
				character_config = CharacterConfigurationModel(**character_data)
				character = Character(logger=self._logger, api=self._api, character_config=character_config, agents=agents)
				self._all_characters[character.get_character_name()] = character

	def get_characters_to_respond(self, user_character_name: str, conversation_context: List[Dict[str, Union[str, Any]]]) -> List[Character]:
		characters: List[Character] = []

		current_response: str = ""

		for agent, task in self._character_selector_agents.items():
			task.prior_conversation_context = conversation_context
			current_response = agent.converse(task, replacements={
				"character_options": ", ".join([f"{character.get_character_name()}" for character in self._all_characters.values()]),
				"user": user_character_name
			})

		json_response = self._response_to_json.convert(current_response)
		selected_characters = json_response["characters_needing_to_respond_in_dialogue"]

		for character_data in selected_characters:
			self._logger.debug(f"${{ignore=default}}Selecting character {character_data['character_name']} because of {character_data['reason_for_need']}", separator=self._module_separator)
			if character_data["character_name"] in self._all_characters.keys():
				characters.append(self._all_characters[character_data["character_name"]])
			else: self._logger.warning(f"Character {character_data['character_name']} not found in character data. Most likely, the AI is being dumb.", separator=self._module_separator)

		return characters

	def converse(self, current_conversation: List[Dict[str, Union[str, Any]]], user_character_name: str) -> ConverseOutputModel:
		characters_to_respond = self.get_characters_to_respond(user_character_name, current_conversation)

		character_responses: List[str] = []
		character_names: List[str] = []
		characters_feeling: List[str] = []
		characters_thinking: List[str] = []
		characters_motivated_to: List[str] = []

		for character in characters_to_respond:
			char_response = character.converse(current_conversation, user_character_name)

			try:
				char_response_json = self._response_to_json.convert(char_response)
			except Exception as e:
				self._logger.error(f"Failed to parse response as JSON: {e}", separator=self._module_separator)
				self._logger.debug(f"Original response: {char_response}", separator=self._module_separator)
				continue  # Skip this character if the response cannot be parsed as JSON

			character_names.append(character.get_character_name())
			characters_feeling.append(char_response_json["feeling"])
			characters_thinking.append(char_response_json["thinking"])
			characters_motivated_to.append(char_response_json["motivated_to"])
			character_responses.append(char_response_json["response"])

		altered_context = current_conversation.copy()  # Create a copy of the current conversation to avoid modifying the original
		altered_context.append(self._api.construct_message(role="system", content=f"""
The following are the responses by each character to be merged into a cohesive whole:

{', '.join([f"{character.get_character_name()}: {response}" for character, response in zip(characters_to_respond, character_responses)])}
"""))

		final_response: str = ""

		for agent, task in self._narrative_agents.items():
			task.prior_conversation_context = altered_context
			final_response = agent.converse(task)

		characters_summary_output: List[CharacterSummaryOutputModel] = [
			CharacterSummaryOutputModel(character_name=character_name, feeling=feeling, thinking=thinking, motivated_to=motivated_to)
            for character_name, feeling, thinking, motivated_to in zip(character_names, characters_feeling, characters_thinking, characters_motivated_to)
		]

		return ConverseOutputModel(final_response=final_response, characters_summary_output=characters_summary_output)
