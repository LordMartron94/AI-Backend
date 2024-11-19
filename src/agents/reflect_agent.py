from typing import List, Dict

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.context.agent import Agent
from src.agents.context.agent_context_model import AgentContextModel
from src.agents.interface_agent import IAgent
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI


class ReflectAgent(IAgent):
	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI):
		super().__init__(logger, api, is_child=True)
		self._module_separator: str = "ReflectAgent"

	@staticmethod
	def _get_agent_prompt(context: AgentContextModel) -> str:
		return f"""
[ReflectAgent]
***STORY AGENT INSTRUCTIONS***
    * Rank order the proposed responses based on how accurately they embody the character and overall scenario.
    * Focus on identifying the option that clearly contradicts the character's personality or creates illogical action in the given scenario. This option should be definitively eliminated before proceeding.
    * Do not write the response itself out (do not put creative writing into the response), only rank the options and eliminate one of them. It's a different agent's job to transform it into creative writing.
    
Consider the following information for the scenario details:
{context.agent_responses[Agent.StoryAgent]} 

Consider the following analysis from the personality agent:
{context.agent_responses[Agent.PersonalityAgent]}

Consider the following analysis from the plan agent:
{context.agent_responses[Agent.PlanAgent]}

Consider the following analysis from the propose agent (these are the proposed responses):
{context.agent_responses[Agent.ProposeAgent]}

Stop here. Do not proceed further or generate any creative text unless specifically instructed in the STORY AGENT INSTRUCTIONS.
***END STORY AGENT INSTRUCTIONS***
"""

	def get_agent_response(self, context: AgentContextModel) -> str:
		conversation_context: List[Dict[str, str]] = context.previous_conversation.copy()

		current_prompt: str = self._get_agent_prompt(context)

		self._logger.debug(f"${{ignore=default}}Sending prompt: {current_prompt}", separator=self._module_separator)
		response = self._api.send_message(current_prompt, conversation_context)
		context.agent_responses[Agent.ReflectAgent] = response
		self._logger.debug(f"${{ignore=default}}Gotten response: {response}", separator=self._module_separator)

		return response
