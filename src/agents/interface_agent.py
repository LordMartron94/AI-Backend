from abc import ABC, abstractmethod

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.context.agent_context_model import AgentContextModel
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI


class IAgent(ABC):
	"""
	Defines a contract for a specialized LLM agent.
	"""

	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI, is_child: bool = False):
		if not is_child:
			raise ValueError("You cannot instantiate an interface. Use a concrete implementation.")

		self._logger: HoornLogger = logger
		self._api: ILargeLanguageModelAPI = api

	@abstractmethod
	def get_agent_response(self, context: AgentContextModel) -> str:
		"""
        Returns the response for the given current message and previous messages.

        :param context: The context of the agent.

        :return: The response for the current message.
        """
		raise NotImplementedError("Subclasses must implement this method. Don't call an interface's method.")
