import time
from typing import List, Dict

from PyCommon.md_py_common.py_common.cli_framework import CommandLineInterface
from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI
from src.conversation.default_prompts import DEFAULT_SYSTEM_PROMPT


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
		self.initialize()

	def initialize(self):
		self._logger.debug(f"Initializing conversation manager", separator=self._module_separator)
		self._current_conversation.append(self._api.construct_message(
			role="system",
			content=DEFAULT_SYSTEM_PROMPT
		))

		self._cli_tool.add_command(["converse", "c"], action=self.converse, description="Converse with the AI")
		self._cli_tool.add_command(["print", "p"], action=self.print_conversation, description="Prints the conversation.")

		self._logger.info(f"Initialized conversation manager", separator=self._module_separator)

	def print_conversation(self):
		for message in self._current_conversation:
			print(f"{message['role']}: {message['content']}")
			time.sleep(0.2)

	def converse(self):
		prompt: str = input("What to say to the AI?: ")
		self._logger.debug(f"${{ignore=default}}Conversing with AI: {prompt}", separator=self._module_separator)

		response = self._api.send_message(prompt, self._current_conversation)

		self._current_conversation.append(self._api.construct_message(
			content=prompt,
			role="user"
		))

		self._current_conversation.append(self._api.construct_message(
			content=response,
			role="assistant"
		))

		print(f"User: {prompt}")
		print(f"AI: {response}")

		self._logger.debug(f"${{ignore=default}}Response: {response}", separator=self._module_separator)

	def start_conversation_loop(self):
			self._cli_tool.start_listen_loop()

