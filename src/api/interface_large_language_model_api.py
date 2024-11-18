from abc import ABC, abstractmethod
from typing import List, Dict

from PyCommon.md_py_common.py_common.logging import HoornLogger


class ILargeLanguageModelAPI(ABC):
	def __init__(self, logger: HoornLogger, is_child=False):
		if not is_child:
			raise ValueError("You cannot instantiate an interface. Use a concrete implementation.")

		self._logger: HoornLogger = logger

	@abstractmethod
	def construct_message(self, content: str, role: str) -> Dict[str, str]:
		"""
		Constructs a message for the large language model.
        :param content: The content to construct the message from.
        :param role: The role of the content in the message.
        :return: A dictionary containing the message object.
        """
		raise NotImplementedError("Subclasses must implement this method. Don't call an interface's method.")

	@abstractmethod
	def send_message(self, message: str, prior_conversation_context: List[Dict[str, str]]) -> str:
		"""
        Sends a message to the large language model.
        :param message: The message to send.
        :param prior_conversation_context: The prior conversation context.
        :return: The response from the large language model.
        """
		raise NotImplementedError("Subclasses must implement this method. Don't call an interface's method.")
