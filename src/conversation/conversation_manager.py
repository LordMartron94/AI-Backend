import json
import time
from pathlib import Path
from pprint import pprint
from typing import List, Dict, Union

from PyCommon.md_py_common.py_common.cli_framework import CommandLineInterface
from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.agent import Agent
from src.agents.agent_factory import AgentFactory
from src.agents.agent_task_model import AgentTaskModel
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI
from src.character.character import Character
from src.character.default_prompts import AGENT_DEFINITIONS
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
		self._agent_factory: AgentFactory = AgentFactory(logger)

		self._exit_requested: bool = False

		self._user_character_name = "user"
		self._ai_characters: List[Character] = self._load_ai_characters(self._get_agents())

		self._selected_ai_character: Union[Character, None] = None

		self.initialize()

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

	def _get_agents(self) -> Dict[Agent, AgentTaskModel]:
		agents = {}
		for agent_def in AGENT_DEFINITIONS:
			agent, task = self._create_agent_from_definition(agent_def)
			agents[agent] = task
		return agents

	def _load_ai_characters(self, agents: Dict[Agent, AgentTaskModel]) -> List[Character]:
		characters: List[Character] = []

		with open(Path(PROJECT_ROOT, "data/characters.json"), "r") as file:
			characters_data: List[Dict] = json.load(file)
			for character_data in characters_data:
				character_config = CharacterConfigurationModel(**character_data)
				character = Character(logger=self._logger, api=self._api, character_config=character_config, agents=agents)
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
		self._cli_tool.add_command(["print-costs", "pc"], action=self.print_costs, description="Prints the total costs of the current session.")

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
			print(f"{num}. {character.get_character_name()}")

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

		self._current_conversation.append(self._api.construct_message(
			content=adjusted_prompt,
			role="user"
		))

		response: str = self._selected_ai_character.converse(self._current_conversation, self._user_character_name)

		if "```json" in response:
			response = response.replace("```", "")
			response = response.replace("json", "")

		json_response: dict = json.loads(response.strip())

		self._current_conversation.append(self._api.construct_message(
			content=json_response['response'],
			role="assistant"
		))

		print(f"{self._user_character_name}: ")
		self._print_message_smartly(prompt)
		print(f"{self._selected_ai_character.get_character_name()}: ")
		self._print_message_smartly(json_response['response'])
		print(f"""
Feeling: {json_response['feeling']}
Thinking: {json_response['thinking']}
Motivated to: {json_response['motivated_to']}
""")

		self._logger.debug(f"${{ignore=default}}Response: {response}", separator=self._module_separator)

	def start_conversation_loop(self):
			self._cli_tool.start_listen_loop()

	def print_costs(self):
		print(f"Total costs: {self._api.get_total_costs_for_session()}")
