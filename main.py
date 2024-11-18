from typing import List

from PyCommon.md_py_common.py_common.cli_framework import CommandLineInterface
from PyCommon.md_py_common.py_common.logging import HoornLogger, LogType, DefaultHoornLogOutput, FileHoornLogOutput, \
	LogDirectoryBuilder
from src.constants import APP_NAME, MODULE_SEPARATOR_ROOT
from src.api.openrouter_api import OpenrouterAPI


def smart_split(text, max_line_length=120) -> List[str]:
	"""
	Splits a string into lines, trying to keep words intact and within the
	specified max_line_length.

	Args:
	  text: The string to split.
	  max_line_length: The maximum length of each line.

	Returns:
	  A list of strings, where each string is a line.
	"""

	words = text.split()
	lines = []
	current_line = []

	current_line_length: int = 0

	for word in words:
		if current_line_length + len(word) <= max_line_length:
			current_line.append(word)
			current_line_length += len(word) + 1
		else:
			lines.append(" ".join(current_line))
			current_line = [word + " "]
			current_line_length = len(word) + 1

	if current_line:
		lines.append(" ".join(current_line))

	return lines

def send_message(api: OpenrouterAPI) -> None:
	message = input("Enter a message to send to the AI: ")

	response = api.send_message(message, [])
	response_lines = smart_split(response)

	print("You: " + message)
	print("AI: ")
	for line in response_lines:
		print(f"{line}")

if __name__ == "__main__":
	logger: HoornLogger = HoornLogger(
		min_level=LogType.DEBUG,
		outputs=[
			DefaultHoornLogOutput(),
			FileHoornLogOutput(LogDirectoryBuilder.build_log_directory(APP_NAME, []), max_logs_to_keep=5)
		],
		separator_root=MODULE_SEPARATOR_ROOT
	)
	cli: CommandLineInterface = CommandLineInterface(logger)
	openrouter_api = OpenrouterAPI(logger)

	logger.info("AI Backend successfully started!")

	cli.add_command(["test"], action=send_message, description="Run test command", arguments=[openrouter_api])

	cli.start_listen_loop()
