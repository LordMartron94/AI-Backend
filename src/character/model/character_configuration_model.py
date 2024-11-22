import pydantic


class CharacterConfigurationModel(pydantic.BaseModel):
	name: str
	biography: str
	personality: str


class CharacterConfigurationFactory:
	@staticmethod
	def create_character_configuration(name: str, biography: str, personality: str) -> CharacterConfigurationModel:
		return CharacterConfigurationModel(name=name, biography=biography, personality=personality)
