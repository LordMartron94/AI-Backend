import time
from typing import List, Dict

from PyCommon.md_py_common.py_common.cli_framework import CommandLineInterface
from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI
from src.conversation.character_manager import CharacterManager, ConverseOutputModel
from src.conversation.default_prompts import DEFAULT_SYSTEM_PROMPT
from src.conversation.utils.response_to_json import ResponseToJson
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
		self._response_to_json: ResponseToJson = ResponseToJson(logger)
		self._character_manager: CharacterManager = CharacterManager(logger, api=api)

		self._exit_requested: bool = False

		self._user_character_name = "user"

		self.initialize()

	def initialize(self):
		self._logger.debug(f"Initializing conversation manager", separator=self._module_separator)
		self._current_conversation.append(self._api.construct_message(
			role="system",
			content=DEFAULT_SYSTEM_PROMPT
		))

		self._cli_tool.add_command(["converse", "c"], action=self.converse, description="Converse with the AI")
		self._cli_tool.add_command(["print", "p"], action=self.print_conversation, description="Prints the conversation.")
		self._cli_tool.add_command(["set_character", "sc"], action=self.set_user_character, description="Sets the user's character.")
		self._cli_tool.add_command(["print-costs", "pc"], action=self.print_costs, description="Prints the total costs of the current session.")

		self._logger.info(f"Initialized conversation manager", separator=self._module_separator)

	def print_conversation(self):
		for message in self._current_conversation:
			print(f"{message['role']}: {message['content'][0]['text']}")
			time.sleep(0.2)

	def set_user_character(self):
		character_name: str = input("Enter your character's name: ")
		self._user_character_name: str = character_name

	def _print_message_smartly(self, message: str):
		m_spl: List[str] = smart_split(message)
		for m_l in m_spl:
			print(m_l)

	def converse(self):
		prompt: str = input("What to say to the AI?: ")
		self._logger.debug(f"${{ignore=default}}Conversing with AI: {prompt}", separator=self._module_separator)

		adjusted_prompt: str = f"[{self._user_character_name}]: {prompt}"

		self._current_conversation.append(self._api.construct_message(
			content=adjusted_prompt,
			role="user"
		))

		response: ConverseOutputModel = self._character_manager.converse(self._current_conversation, self._user_character_name)
		json_response = self._response_to_json.convert(response.final_response)

		self._current_conversation.append(self._api.construct_message(
			content=json_response['response'],
			role="assistant"
		))

		self._print_turn(self._user_character_name, prompt, response)

		self._logger.debug(f"${{ignore=default}}Response: {response}", separator=self._module_separator)

	def start_conversation_loop(self):
			self._cli_tool.start_listen_loop()

	def print_costs(self):
		print(f"Total costs: {self._api.get_total_costs_for_session()}")

	def _print_turn(self, user_character_name: str, prompt: str, response: ConverseOutputModel):
		print(f"{user_character_name}:")
		self._print_message_smartly(prompt)
		print("AI:")

		final_response_json = self._response_to_json.convert(response.final_response)

		self._print_message_smartly(final_response_json['response'])

		for summary in response.characters_summary_output:
			print(f"{summary.character_name}:")
			print(f"Feeling: {summary.feeling}")
			print(f"Thinking: {summary.thinking}")
			print(f"Motivated to: {summary.motivated_to}")
			print("--------------------")
