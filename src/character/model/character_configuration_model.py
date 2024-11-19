import pydantic


class CharacterConfigurationModel(pydantic.BaseModel):
	name: str
	biography: str
	personality: str

	id_weight: float
	ego_weight: float
	superego_weight: float


class CharacterConfigurationFactory:
	@staticmethod
	def create_character_configuration(name: str, biography: str, id_weight: float, ego_weight: float, superego_weight: float, personality: str) -> CharacterConfigurationModel:
		return CharacterConfigurationModel(name=name, biography=biography, id_weight=id_weight, ego_weight=ego_weight, superego_weight=superego_weight, personality=personality)
