from pprint import pprint
from typing import List

import requests

from PyCommon.md_py_common.py_common.logging import HoornLogger
from secret.secrets import OPENROUTER_KEY


class OpenrouterGenerationTracker:
	def __init__(self, logger: HoornLogger):
		self._logger: HoornLogger = logger
		self._module_separator: str = "GenerationTracker"
		self._generations: List[str] = []

	def track_generation(self, generation_id: str):
		self._generations.append(generation_id)

	def get_total_costs_for_generations(self) -> float:
		cost: float = 0.0

		for generation_id in self._generations:
			self._logger.debug(f"${{ignore=default}}Tracking for: {generation_id}", separator=self._module_separator)
			headers = {
				"Authorization": f"Bearer {OPENROUTER_KEY}"
			}

			response = requests.get(
				f"https://openrouter.ai/api/v1/generation?id={generation_id}", headers=headers
			)

			data = response.json()

			# noinspection PyBroadException
			try:
				data = data['data']
				cost += data["total_cost"]
			except Exception:
				self._logger.warning(f"Failed to fetch cost for generation {generation_id}", separator=self._module_separator)
				continue

		return cost
