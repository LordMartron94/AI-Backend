from typing import List, Dict, Union, Any

import pydantic


class AgentTaskModel(pydantic.BaseModel):
	task_description: str
	expected_output: str

	prior_conversation_context: List[Dict[str, Union[str, Any]]]
