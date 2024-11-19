from typing import List, Dict

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.context.agent import Agent
from src.agents.context.agent_context_model import AgentContextModel
from src.agents.interface_agent import IAgent
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI


class PersonalityAgent(IAgent):
	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI):
		super().__init__(logger, api, is_child=True)
		self._module_separator: str = "PersonalityAgent"

	@staticmethod
	def _get_agent_prompt(context: AgentContextModel) -> str:
		return f"""
[PersonalityAgent]
***STORY AGENT INSTRUCTIONS***
    * Analyze the character's current physical state. Are they healthy? Injured? Tired? Impaired? Incapacitated?
    * What is the character's current emotional state? 
    * Is the character's current physical or emotional state likely to make their typical speech MORE or LESS pronounced?
    * In this scenario, would the character's established personality lead them to prioritize long, explanatory responses or short, direct ones?"
    * What assumptions about the scenario is the character making?  
    * Assess the validity of each of the character's assumptions.  Are they likely to be true, false, or are you unsure?    
    * How does the character perceive their relationship with the other characters? What facts are the character's perceptions of the other characters based on? 
    
Consider the following information for the scenario details:
{context.agent_responses[Agent.StoryAgent]} 

Stop here. Do not proceed further or generate any creative text unless specifically instructed in the STORY AGENT INSTRUCTIONS.
***END STORY AGENT INSTRUCTIONS***
"""

	def get_agent_response(self, context: AgentContextModel) -> str:
		conversation_context: List[Dict[str, str]] = context.previous_conversation.copy()

		current_prompt: str = self._get_agent_prompt(context)

		self._logger.debug(f"${{ignore=default}}Sending prompt: {current_prompt}", separator=self._module_separator)
		response = self._api.send_message(current_prompt, conversation_context)
		context.agent_responses[Agent.PersonalityAgent] = response
		self._logger.debug(f"${{ignore=default}}Gotten response: {response}", separator=self._module_separator)

		return response
