import pydantic


class AgentConfigModel(pydantic.BaseModel):
	agent_name: str
	agent_role: str
	agent_backstory: str
