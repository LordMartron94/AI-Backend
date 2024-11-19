from typing import List, Dict

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.context.agent import Agent
from src.agents.context.agent_context_model import AgentContextModel
from src.agents.interface_agent import IAgent
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI


class DecisionAgent(IAgent):
	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI):
		super().__init__(logger, api, is_child=True)
		self._module_separator: str = "DecisionAgent"

	@staticmethod
	def _get_agent_prompt(context: AgentContextModel) -> str:
		return f"""
[DecisionAgent]
***STORY AGENT INSTRUCTIONS***
    * Utilize Critique_Agent analysis to make an informed final response selection. 
    * Return the chosen response based on the analysis from Critique_Agent.
    
Consider the following information for the scenario details:
{context.agent_responses[Agent.StoryAgent]} 

Consider the following analysis from the personality agent:
{context.agent_responses[Agent.PersonalityAgent]}

Consider the following critique analysis (this is from Critique_Agent):
{context.agent_responses[Agent.CritiqueAgent]}

Stop here. Do not proceed further or generate any creative text unless specifically instructed in the STORY AGENT INSTRUCTIONS.
***END STORY AGENT INSTRUCTIONS***
"""

	def get_agent_response(self, context: AgentContextModel) -> str:
		conversation_context: List[Dict[str, str]] = context.previous_conversation.copy()

		current_prompt: str = self._get_agent_prompt(context)

		self._logger.debug(f"${{ignore=default}}Sending prompt: {current_prompt}", separator=self._module_separator)
		response = self._api.send_message(current_prompt, conversation_context)
		context.agent_responses[Agent.DecisionAgent] = response
		self._logger.debug(f"${{ignore=default}}Gotten response: {response}", separator=self._module_separator)

		return response