from typing import List, Dict

from openai import OpenAI

from PyCommon.md_py_common.py_common.logging import HoornLogger
from secret.secrets import OPENROUTER_KEY
from src.constants import APP_NAME, MAIN_CHAT_MODEL
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI


class OpenrouterAPI(ILargeLanguageModelAPI):
	"""
	API for interacting with OpenRouter.
	"""

	def __init__(self, logger: HoornLogger):
		super().__init__(logger, is_child=True)
		self._separator = "OpenRouterAPI"
		self._logger.info("Initializing OpenRouter API", separator=self._separator)
		self._client: OpenAI = OpenAI(
			api_key=OPENROUTER_KEY,
			base_url="https://openrouter.ai/api/v1"
		)

	def construct_message(self, content: str, role: str) -> Dict[str, str]:
		return {
			"role": role,
			"content": [
				{
					"type": "text",
					"text": content
				}
			]
		}

	def send_message(self, message: str, prior_conversation_context: List[Dict[str, str]]) -> str:
		"""
		Send a message to OpenRouter.

        :param message: The message to send.
        :param prior_conversation_context: The previous conversation context.
        :return: The response from OpenRouter.
        """

		messages = prior_conversation_context.copy()  # Copy the prior conversation context to avoid modifying it.
		messages.append(self.construct_message(role="user", content=message))

		completion = self._client.chat.completions.create(
			extra_headers={
				"X-Title": APP_NAME,
			},
			model=MAIN_CHAT_MODEL,
			messages=messages
		)

		if completion.choices is None:
			self._logger.error("No response received from OpenRouter", separator=self._separator)
			return ""

		response = completion.choices[0].message.content
		self._logger.debug(f"${{ignore=default}}Gotten: {response}", separator=self._separator)
		return response
