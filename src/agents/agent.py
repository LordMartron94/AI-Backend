from typing import List, Dict, Union, Any

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.agent_config_model import AgentConfigModel
from src.agents.agent_task_model import AgentTaskModel
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI


class Agent:
	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI, agent_config: AgentConfigModel):
		self._logger: HoornLogger = logger
		self._api: ILargeLanguageModelAPI = api
		self._config: AgentConfigModel = agent_config

		self._module_seperator = f"Agents.{self._config.agent_name}"

	def _get_agent_system_prompt(self):
		return f"""
You are {self._config.agent_name}.

It is your role to be a: {self._config.agent_role}.

This is your backstory:
{self._config.agent_backstory}
"""

	def _get_task_prompt(self, task: AgentTaskModel, current_user_name: str, current_character_name: str) -> str:
		return f"""
Your current task is to {task.task_description.replace("{{char}}", current_character_name).replace("{{user}}", current_user_name)}.

The expected output format is:
{task.expected_output}

Be sure to adhere to this format and the task. Do not go beyond what is required.
Make sure to ONLY respond with the provided expected output format, and not write anything else.

If the format is JSON, then follow the json template completely. Do not return it in a markdown codeblock, but return the raw JSON...
Do not enclose the JSON output in code blocks or any other markdown elements.

I do not want to see any of the following in your response:
```json
```
"""

	def converse(self, task: AgentTaskModel, current_user_name: str, current_character_name: str) -> str:
		messages_to_be_sent: List[Dict[str, Union[str, Any]]] = [
			self._api.construct_message(self._get_agent_system_prompt(), role="system")
		]

		for message_in_context in task.prior_conversation_context:
			messages_to_be_sent.append(message_in_context)

		message = self._get_task_prompt(task, current_user_name, current_character_name)

		self._logger.debug(f"${{ignore=default}}Sending message: {message}", separator=self._module_seperator)
		response = self._api.send_message(message, messages_to_be_sent)
		self._logger.debug(f"${{ignore=default}}Gotten response: {response}", separator=self._module_seperator)

		return response

	def get_name(self):
		return self._config.agent_name
