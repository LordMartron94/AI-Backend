import json
import time
from pathlib import Path
from typing import List, Dict, Union

from PyCommon.md_py_common.py_common.cli_framework import CommandLineInterface
from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.critique_agent import CritiqueAgent
from src.agents.decision_agent import DecisionAgent
from src.agents.interface_agent import IAgent
from src.agents.personality_agent import PersonalityAgent
from src.agents.plan_agent import PlanAgent
from src.agents.propose_agent import ProposeAgent
from src.agents.reflect_agent import ReflectAgent
from src.agents.story_agent import StoryAgent
from src.agents.writing_agent import WritingAgent
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI
from src.character.character import Character
from src.character.model.character_configuration_model import CharacterConfigurationModel
from src.constants import PROJECT_ROOT
from src.conversation.default_prompts import DEFAULT_SYSTEM_PROMPT
from src.utils.utils import smart_split


class ConversationManager:
	"""
	Tool to manage the conversation itself.
	"""

	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI):
		self._logger: HoornLogger = logger
		self._api: ILargeLanguageModelAPI = api
		self._current_conversation: List[Dict[str, str]] = []
		self._module_separator: str = "ConversationManager"
		self._cli_tool: CommandLineInterface = CommandLineInterface(self._logger, log_module_sep=f"{self._module_separator}.CLI")
		self._cli_tool.set_exit_command(self._cli_tool.exit_conversation_loop)
		self._exit_requested: bool = False

		self._user_character_name = "user"
		self._ai_characters: List[Character] = self._load_ai_characters(self._get_agents())

		self._selected_ai_character: Union[Character, None] = None

		self.initialize()

	def _get_agents(self) -> List[IAgent]:
		return [
			StoryAgent(logger=self._logger, api=self._api),
			PersonalityAgent(logger=self._logger, api=self._api),
			PlanAgent(logger=self._logger, api=self._api),
			ProposeAgent(logger=self._logger, api=self._api),
			ReflectAgent(logger=self._logger, api=self._api),
			CritiqueAgent(logger=self._logger, api=self._api),
			DecisionAgent(logger=self._logger, api=self._api),
			WritingAgent(logger=self._logger, api=self._api)
		]

	def _load_ai_characters(self, agents: List[IAgent]) -> List[Character]:
		characters: List[Character] = []

		with open(Path(PROJECT_ROOT, "data/characters.json"), "r") as file:
			characters_data: List[Dict] = json.load(file)
			for character_data in characters_data:
				character_config = CharacterConfigurationModel(**character_data)
				character = Character(logger=self._logger, api=self._api, config=character_config, agents=agents)
				characters.append(character)

		return characters


	def initialize(self):
		self._logger.debug(f"Initializing conversation manager", separator=self._module_separator)
		self._current_conversation.append(self._api.construct_message(
			role="system",
			content=DEFAULT_SYSTEM_PROMPT
		))

		self._cli_tool.add_command(["converse", "c"], action=self.converse, description="Converse with the AI")
		self._cli_tool.add_command(["print", "p"], action=self.print_conversation, description="Prints the conversation.")
		self._cli_tool.add_command(["set_character", "sc"], action=self.set_user_character, description="Sets the user's character.")
		self._cli_tool.add_command(["select_ai_character", "sai"], action=self.select_ai_character, description="Selects an AI character.")

		self._logger.info(f"Initialized conversation manager", separator=self._module_separator)

	def print_conversation(self):
		for message in self._current_conversation:
			print(f"{message['role']}: {message['content'][0]['text']}")
			time.sleep(0.2)

	def set_user_character(self):
		character_name: str = input("Enter your character's name: ")
		self._user_character_name: str = character_name

	def select_ai_character(self):
		num: int = 0
		for character in self._ai_characters:
			num += 1
			print(f"{num}. {character.get_name()}")

		choice = int(input("Enter the number of the AI character you want to select: "))

		# Validate the choice
		if choice < 1 or choice > len(self._ai_characters):
			self._logger.warning("Invalid choice. Try again.", separator=self._module_separator)
			time.sleep(0.5)
			return self.select_ai_character()

		selected_character: Character = self._ai_characters[choice - 1]
		self._selected_ai_character = selected_character

	def _print_message_smartly(self, message: str):
		m_spl: List[str] = smart_split(message)
		for m_l in m_spl:
			print(m_l)

	def converse(self):
		prompt: str = input("What to say to the AI?: ")
		self._logger.debug(f"${{ignore=default}}Conversing with AI: {prompt}", separator=self._module_separator)

		if self._selected_ai_character is None:
			self._logger.warning("No AI character selected. Please select an AI character first.", separator=self._module_separator)
			return

		adjusted_prompt: str = f"[{self._user_character_name}]: {prompt}"

		response: str = self._selected_ai_character.converse(adjusted_prompt, self._current_conversation, self._user_character_name)

		self._current_conversation.append(self._api.construct_message(
			content=adjusted_prompt,
			role="user"
		))

		self._current_conversation.append(self._api.construct_message(
			content=response,
			role="assistant"
		))

		print(f"{self._user_character_name}: ")
		self._print_message_smartly(prompt)
		print(f"{self._selected_ai_character.get_name()}: ")
		self._print_message_smartly(response)

		self._logger.debug(f"${{ignore=default}}Response: {response}", separator=self._module_separator)

	def start_conversation_loop(self):
			self._cli_tool.start_listen_loop()
