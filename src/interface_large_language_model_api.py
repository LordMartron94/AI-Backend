from abc import ABC

from PyCommon.md_py_common.py_common.logging import HoornLogger


class ILargeLanguageModelAPI(ABC):
	def __init__(self, logger: HoornLogger, is_child=False):
		if not is_child:
			raise ValueError("You cannot instantiate an interface. Use a concrete implementation.")

		self._logger: HoornLogger = logger
