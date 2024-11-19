from typing import Dict, List, Union, Any

import pydantic

from src.agents.context.agent import Agent
from src.character.model.character_configuration_model import CharacterConfigurationModel


class AgentContextModel(pydantic.BaseModel):
	user_name: str
	character_model: CharacterConfigurationModel

	agent_responses: Dict[Agent, str] = {}
	previous_conversation: List[Dict[str, Union[str, Any]]] = []
