from typing import List, Dict

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.context.agent import Agent
from src.agents.context.agent_context_model import AgentContextModel
from src.agents.interface_agent import IAgent
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI


class ProposeAgent(IAgent):
	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI):
		super().__init__(logger, api, is_child=True)
		self._module_separator: str = "ProposeAgent"

	@staticmethod
	def _get_agent_prompt(context: AgentContextModel) -> str:
		return f"""
[ProposeAgent]
***STORY AGENT INSTRUCTIONS***
    * Focus on the character's recent dialogue. Ensure **NO** overlap or near-repetition of actions or tone between your proposals. Craft options offering DISTINCTLY different approaches.
    * Identify TWO contrasting core motivations driving the character in this scenario (example: fear vs. curiosity). For each proposal below, ensure it clearly prioritizes ONE of these motivations. 
    * Develop three diverse, fresh, and unique response options that effectively synthesize insights from previous agents.  
    * Option 1: [Summarize option in neutral 3rd person, not mirroring {context.character_model.name}'s speech patterns] 
	    - Strength: [Reason, focused on how this aligns with a core motivation] 
	    - Weakness: [Potential inconsistency, be extra critical if option feels repetitive]
    * Option 2:  [Summarize option in neutral 3rd person, not mirroring {context.character_model.name}'s speech patterns] 
	    - Strength: [Reason, focused on how this aligns with the OTHER core motivation] 
	    - Weakness: [Potential inconsistency, be extra critical if option feels repetitive]
    * Option 3: [Summarize option in neutral 3rd person, not mirroring {context.character_model.name}'s speech patterns] 
	    - Strength: [Reason, focused on how this aligns with a THIRD core motivation] 
	    - Weakness: [Potential inconsistency, be extra critical if option feels repetitive]
    
Consider the following information for the scenario details:
{context.agent_responses[Agent.StoryAgent]} 

Consider the following analysis from the personality agent:
{context.agent_responses[Agent.PersonalityAgent]}

Consider the following analysis from the plan agent:
{context.agent_responses[Agent.PlanAgent]}

***END STORY AGENT INSTRUCTIONS***
"""

	def get_agent_response(self, context: AgentContextModel) -> str:
		conversation_context: List[Dict[str, str]] = context.previous_conversation.copy()

		current_prompt: str = self._get_agent_prompt(context)

		self._logger.debug(f"${{ignore=default}}Sending prompt: {current_prompt}", separator=self._module_separator)
		response = self._api.send_message(current_prompt, conversation_context)
		context.agent_responses[Agent.ProposeAgent] = response
		self._logger.debug(f"${{ignore=default}}Gotten response: {response}", separator=self._module_separator)

		return response
