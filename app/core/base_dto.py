from pydantic import BaseModel


class BaseDto(BaseModel):
    model_config = {
        "extra": "forbid",
    }
