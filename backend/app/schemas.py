from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    horizon: int = Field(
        default=24,
        ge=1,
        le=24,
        description="Number of hours to forecast."
    )


class ForecastPoint(BaseModel):
    datetime: str
    forecast: float


class ForecastResponse(BaseModel):
    horizon: int
    forecasts: list[ForecastPoint]