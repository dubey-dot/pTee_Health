from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base for all API schemas.

    Serializes/accepts camelCase over the wire (matching the frontend's
    existing TS interfaces) while keeping snake_case Python attribute names.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
