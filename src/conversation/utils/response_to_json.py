import json

from PyCommon.md_py_common.py_common.logging import HoornLogger


class ResponseToJson:
	"""
	Utility class to convert a response string to JSON format.
	"""

	def __init__(self, logger: HoornLogger):
		self._logger: HoornLogger = logger
		self._module_separator = "ResponseToJson"

	def convert(self, response_str: str) -> dict:
		self._logger.debug(f"${{ignore=default}}Converting response to JSON: {response_str}", separator=self._module_separator)

		response = response_str

		if "```json" in response:
			response = response.replace("```", "")
			response = response.replace("json", "")

		return json.loads(response.strip())
