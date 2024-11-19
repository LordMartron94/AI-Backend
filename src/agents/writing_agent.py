from typing import List, Dict

from PyCommon.md_py_common.py_common.logging import HoornLogger
from src.agents.context.agent import Agent
from src.agents.context.agent_context_model import AgentContextModel
from src.agents.interface_agent import IAgent
from src.api.interface_large_language_model_api import ILargeLanguageModelAPI


class WritingAgent(IAgent):
	def __init__(self, logger: HoornLogger, api: ILargeLanguageModelAPI):
		super().__init__(logger, api, is_child=True)
		self._module_separator: str = "WritingAgent"

	@staticmethod
	def _get_agent_prompt(context: AgentContextModel) -> str:
		return f"""
[WritingAgent]
***STORY AGENT INSTRUCTIONS***
    * Focus on recent dialogue. Ensure **NO** overlap or near-repetition of words, actions or tone between your response and previous responses.
    * Write a response containing at least 3 lengthy and verbose paragraphs, each containing at least four sentences with a mix of action and speech.
	    * Utilize analysis from other agents to reflect the option chosen by Decision_agent while authentically capturing the chosen character's personality and voice. 
	    * The final response must be a cohesive whole, representing the character's behavior and dialogue. Written as if part of a novel.
	    * Avoid repeating details already established earlier.
    * NEVER write for {context.user_name} or describe their thoughts or actions.  Use markdown to italicize actions and thoughts *like this*, and put all speech in quotation marks "like this".  AVOID italicizing words inside of quotes or quoting words inside of italics.  Be descriptive, providing vivid details about the present character's actions, emotions, sensations and the environment. 
    * Avoid summarizing statements at the end of a paragraph, it's an open-ended story and it's immensely annoying to see paragraphs like this at the end: "She's intrigued, yes, but she's also wary. This is a dance, a game of power and influence, and she's determined  to be the one leading."
    * After your response, create a summary of the following, contained within a code block, using the context of the conversation and the current response to fill in the variables, using the following formatting:

```
[Character Name]: 
Feeling: X, Y
Thinking: X, Y 
Motivated to: X, Y
```
    
Consider the following information for the scenario details:
{context.agent_responses[Agent.StoryAgent]} 

Consider the following analysis from the personality agent:
{context.agent_responses[Agent.PersonalityAgent]}

Consider the following analysis from the planning agent:
{context.agent_responses[Agent.PlanAgent]}

Consider the following decision analysis (this is from Decision_agent):
{context.agent_responses[Agent.DecisionAgent]}

***END STORY AGENT INSTRUCTIONS***
"""

	def get_agent_response(self, context: AgentContextModel) -> str:
		conversation_context: List[Dict[str, str]] = context.previous_conversation.copy()

		current_prompt: str = self._get_agent_prompt(context)

		self._logger.debug(f"${{ignore=default}}Sending prompt: {current_prompt}", separator=self._module_separator)
		response = self._api.send_message(current_prompt, conversation_context)
		context.agent_responses[Agent.WritingAgent] = response
		self._logger.debug(f"${{ignore=default}}Gotten response: {response}", separator=self._module_separator)

		return response
