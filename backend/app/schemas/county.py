from pydantic import BaseModel


class CountyResponse(BaseModel):
    id: int
    name: str
    nuts3: str
    nuts2: str
    latitude: float | None = None
    longitude: float | None = None

    model_config = {
        "from_attributes": True,
    }
