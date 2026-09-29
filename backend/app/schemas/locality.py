from pydantic import BaseModel


class LocalityResponse(BaseModel):
    id: int
    siruta: int
    name: str
    county: str
    siruta_sup: int | None
    locality_type: str | None
    population: int | None

    model_config = {
        "from_attributes": True,
    }