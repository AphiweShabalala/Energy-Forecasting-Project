# Energy Demand Forecasting

An end-to-end machine learning application for forecasting electricity demand. The project combines time-series feature engineering, XGBoost regression, a FastAPI backend, a React frontend, and SQLite-based forecast storage.

## Project Overview

The application forecasts total electricity demand one hour ahead using historical demand and calendar/time-series features.

The trained model is an `XGBRegressor`. The backend uses the model recursively to generate forecasts for a requested horizon of **1–24 hours**.

### Main components

- **Machine Learning:** XGBoost regression
- **Time-series features:** lag features, rolling statistics, calendar features, and cyclical time encoding
- **Backend:** FastAPI
- **Frontend:** React + Vite
- **Database:** SQLite
- **Model serialization:** Joblib
- **Validation:** Pydantic
- **Cross-validation:** TimeSeriesSplit
- **Train/test split:** Chronological 80/20 split

## Forecasting Pipeline

The forecasting workflow follows:

Historical electricity demand
          ↓
Data cleaning & aggregation
          ↓
Time-series feature engineering
          ↓
Chronological train/test split
          ↓
XGBoost model training
          ↓
TimeSeriesSplit validation
          ↓
Model evaluation
          ↓
Saved XGBoost model
          ↓
FastAPI prediction service
          ↓
React frontend


## Dataset

The project uses the UCI Electricity Load Diagrams dataset.

The original data contains electricity consumption measurements recorded at 15-minute intervals for multiple meter series.

For this project, the individual meter measurements were aggregated into a **total electricity demand** series and converted to an hourly forecasting problem.

The modelling target is the next hourly electricity demand value.

## Feature Engineering

The forecasting model uses 14 features:

```text
total_demand
lag_1
lag_2
lag_3
lag_24
lag_48
lag_168
hour
day_of_week
is_weekend
hour_sin
hour_cos
rolling_mean_24
rolling_std_24
```

### Lag features

Historical demand is used to provide the model with information about recent and seasonal demand patterns.

- `lag_1` — previous hour
- `lag_2` — two hours previously
- `lag_3` — three hours previously
- `lag_24` — same hour on the previous day
- `lag_48` — same hour two days previously
- `lag_168` — same hour one week previously

### Calendar features

The model also receives:

- Hour of day
- Day of week
- Weekend indicator

### Cyclical time features

Hour of day is represented using sine and cosine transformations:

```text
hour_sin
hour_cos
```

This allows the model to represent the cyclical relationship between the end and beginning of the day.

### Rolling statistics

The model uses 24-hour rolling statistics:

- `rolling_mean_24`
- `rolling_std_24`

These provide information about the recent daily demand level and variability.

## Model

The final forecasting model is an `XGBRegressor`.

Model artifact:

```text
models/xgboost_energy_forecaster.joblib
```

Model metadata:

```text
models/model_metadata.json
```

The model uses a fixed random state of 42.

## Model Validation

The dataset was split chronologically:

| Dataset | Proportion |
|---|---:|
| Training | 80% |
| Testing | 20% |

Cross-validation uses TimeSeriesSplit with 5 splits.

Random shuffling was not used because the temporal ordering of observations must be preserved in time-series forecasting.

## Model Performance

Performance was evaluated against a naive forecasting baseline.

| Metric | XGBoost | Naive Baseline |
|---|---:|---:|
| MAE | 4,606.74 | 16,475.72 |
| RMSE | 6,790.25 | 24,779.80 |

The saved model metadata reports:

- **MAE improvement over naive:** 72.04%
- **RMSE improvement over naive:** 72.60%

The metrics represent performance on the chronological test set.

## Backend API

The backend is implemented with FastAPI.

### Run the API locally

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

### Health check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

### Generate a forecast

```http
POST /forecast
```

Request:

```json
{
  "horizon": 24
}
```

The `horizon` must be between **1 and 24 hours**.

The API obtains the latest 168 hours of historical demand and generates the requested forecast horizon.

Example response structure:

```json
{
  "horizon": 24,
  "forecasts": [
    {
      "datetime": "2026-01-01T01:00:00",
      "forecast": 123456.78
    }
  ]
}
```

### Retrieve saved forecasts

```http
GET /forecasts?limit=100
```

The endpoint returns previously generated forecasts stored in the database.

The accepted limit is between 1 and 500 records.

## Database

SQLite is used to store generated forecasts.

The application initializes the database when the FastAPI application starts.

The database is used for application-level forecast history rather than for storing the original training dataset.

The local database file is excluded from version control.

## Frontend

The frontend is built using:

- React
- Vite
- Recharts

The frontend provides an interface for:

- Checking API status
- Requesting forecasts
- Selecting a forecast horizon
- Displaying forecast results
- Viewing previously saved forecasts

### Run the frontend locally

```bash
cd frontend
npm install
npm run dev
```

The development server runs on:

```text
http://localhost:5173
```

The frontend communicates with the backend through the `VITE_API_URL` environment variable.

Example:

```text
VITE_API_URL=http://localhost:8000
```

## Project Structure

```text
Energy-Project/
│
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── crud.py
│   │   ├── services/
│   │   │   ├── forecasting.py
│   │   │   └── model_loader.py
│   │   ├── main.py
│   │   └── schemas.py
│   └── load_database.py
│
├── database/
│   ├── migrations/
│   └── schema.sql
│
├── frontend/
│   ├── public/
|   ├── src/
|   ├── index.html
|   ├── package.json
|   ├── package-lock.json
|   ├── vite.config.js
|   ├── .gitignore
|   └── .oxlintrc.json
│
├── models/
│   ├── model_metadata.json
│   └── xgboost_energy_forecaster.joblib
│
├── NoteBooks/
│   └── ...
│
├── Reports/
│   └── ...
│
├── test/
│   └── ...
│
├── requirements.txt
├── .env.example
└── .gitignore
```

## Installation

### Python environment

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bat
venv\Scripts\activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

### Frontend dependencies

```bash
cd frontend
npm install
```

## Running the Full Application Locally

Start the backend:

```bash
uvicorn backend.app.main:app --reload
```

In a second terminal, start the frontend:

```bash
cd frontend
npm run dev
```

Then open the frontend development URL in your browser.

## Deployment

The application is structured for separate deployment of the frontend and FastAPI backend.

Production deployment requires:

1. Hosting the FastAPI backend.
2. Making the trained model available to the backend.
3. Configuring the production database.
4. Hosting the React frontend.
5. Setting `VITE_API_URL` to the public backend URL.
6. Configuring CORS to allow the production frontend origin.

Local development uses:

```text
Frontend → http://localhost:5173
Backend  → http://localhost:8000
```

Production URLs are configured through environment variables rather than hard-coded into the frontend.

## Limitations

This project has several practical limitations:

- The model predicts total demand rather than individual electricity meters.
- The core model is trained for a one-hour-ahead prediction.
- Multi-hour forecasts depend on recursively generated predictions.
- Weather and other external variables are not included.
- The current application uses SQLite for forecast persistence.
- Forecast accuracy may vary across different periods of electricity demand.

## Future Improvements

Potential extensions include:

- Incorporating weather variables
- Adding additional external demand drivers
- Comparing XGBoost with dedicated time-series models
- Adding prediction intervals
- Implementing model monitoring
- Adding automated retraining
- Moving production persistence to a managed relational database
- Containerizing the backend and frontend
- Adding automated CI/CD tests

## Technologies

```text
Python
Pandas
NumPy
Scikit-learn
XGBoost
FastAPI
Pydantic
SQLite
React
Vite
Recharts
Joblib
```