from typing import List

from PyCommon.md_py_common.py_common.cli_framework import CommandLineInterface
from PyCommon.md_py_common.py_common.logging import HoornLogger, LogType, DefaultHoornLogOutput, FileHoornLogOutput, \
	LogDirectoryBuilder
from src.constants import APP_NAME, MODULE_SEPARATOR_ROOT
from src.api.openrouter_api import OpenrouterAPI
from src.conversation.conversation_manager import ConversationManager
from src.utils.utils import smart_split


def send_message(api: OpenrouterAPI) -> None:
	message = input("Enter a message to send to the AI: ")

	response = api.send_message(message, [])
	response_lines = smart_split(response)

	print("You: " + message)
	print("AI: ")
	for line in response_lines:
		print(f"{line}")

if __name__ == "__main__":
	max_separator_length = 50

	logger: HoornLogger = HoornLogger(
		min_level=LogType.DEBUG,
		outputs=[
			DefaultHoornLogOutput(max_separator_length=max_separator_length),
			FileHoornLogOutput(LogDirectoryBuilder.build_log_directory(APP_NAME, []), max_logs_to_keep=5, max_separator_length=max_separator_length)
		],
		separator_root=MODULE_SEPARATOR_ROOT,
		max_separator_length=max_separator_length
	)
	cli: CommandLineInterface = CommandLineInterface(logger)
	openrouter_api = OpenrouterAPI(logger)
	conversation_manager: ConversationManager = ConversationManager(logger, openrouter_api)

	logger.info("AI Backend successfully started!")

	cli.add_command(["test"], action=send_message, description="Run test command", arguments=[openrouter_api])
	cli.add_command(["converse"], action=lambda: conversation_manager.start_conversation_loop(), description="Start conversation loop")

	cli.start_listen_loop()
