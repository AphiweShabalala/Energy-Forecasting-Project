from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database.crud import (
    get_latest_history,
    initialize_database,
    save_forecasts,
    get_saved_forecasts
)
from backend.app.schemas import (
    ForecastRequest,
    ForecastResponse,
)
from backend.app.services.forecasting import forecast_demand


app = FastAPI(
    title="Energy Demand Forecasting API",
    description="API for forecasting electricity demand.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
   allow_origins=[
    os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    initialize_database()




@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/forecast", response_model=ForecastResponse)
def create_forecast(request: ForecastRequest):

    # Get the latest 168 hours of historical demand
    history = get_latest_history(168)

    # Generate the forecast
    forecasts = forecast_demand(
        history,
        horizon=request.horizon
    )

    # Save forecasts to the database
    save_forecasts(forecasts)

    # Convert DataFrame to API response format
    forecast_points = [
        {
            "datetime": row.datetime.isoformat(),
            "forecast": float(row.forecast),
        }
        for row in forecasts.itertuples(index=False)
    ]

    return {
        "horizon": request.horizon,
        "forecasts": forecast_points,
    }

@app.get("/forecasts")
def get_forecasts(limit: int = 100):

    if limit < 1 or limit > 500:
        return {
            "error": "limit must be between 1 and 500"
        }

    rows = get_saved_forecasts(limit)

    return {
        "count": len(rows),
        "forecasts": [
            {
                "datetime": row["datetime"],
                "forecast": float(row["forecast"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ],
    }