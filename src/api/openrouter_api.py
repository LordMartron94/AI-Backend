from typing import List, Dict

from openai import OpenAI

from PyCommon.md_py_common.py_common.logging import HoornLogger
from secret.secrets import OPENROUTER_KEY
from src.api.tracking.openrouter_generation_tracker import OpenrouterGenerationTracker
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
		self._tracker = OpenrouterGenerationTracker(logger)

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
			messages=messages,
			response_format={
				"type": "json_object"
			}
		)

		print_prompt = self._get_print_prompt(messages)

		self._logger.debug(f"${{ignore=default}}Sending: {print_prompt}", separator=self._separator)

		if completion.choices is None:
			self._logger.error("No response received from OpenRouter", separator=self._separator)
			return ""

		response = completion.choices[0].message.content
		self._tracker.track_generation(completion.id)

		self._logger.debug(f"${{ignore=default}}Gotten: {response}", separator=self._separator)
		return response

	def get_total_costs_for_session(self) -> float:
		return self._tracker.get_total_costs_for_generations()

	def _get_print_prompt(self, messages: List[Dict[str, str]]) -> str:
		message_list: List[str] = []

		for conv_msg in messages:
			message_list.append(conv_msg["content"][0]["text"])

		return "\n".join(message_list)

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
