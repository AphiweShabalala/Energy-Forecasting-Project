# Energy Demand Forecasting

An end-to-end machine learning application for forecasting electricity demand. The project combines time-series feature engineering, XGBoost regression, a FastAPI backend, a React frontend, and SQLite-based forecast storage.

## Live Application

**Frontend:** https://energy-forecasting-project.vercel.app/

**Backend API:** https://energy-forecasting-project-1-phvr.onrender.com

The deployed application allows users to request a forecast horizon of **1–24 hours** and visualize the predicted electricity demand through a React interface.

## Project Overview

The application forecasts total electricity demand one hour ahead using historical demand and calendar/time-series features.

The trained model is an `XGBRegressor`. The backend uses the one-hour-ahead model recursively to generate forecasts for a requested horizon of **1–24 hours**.

For example, a 24-hour request generates the first hour using historical observations, then uses that prediction as part of the input for the next hour, continuing recursively until the requested horizon is reached.

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
- **Backend hosting:** Render
- **Frontend hosting:** Vercel

## Forecasting Pipeline

```text
UCI Electricity Load Diagrams Dataset
                ↓
Data Cleaning & Aggregation
                ↓
Hourly Total Demand
                ↓
Time-Series Feature Engineering
                ↓
Chronological Train/Test Split
                ↓
XGBoost Model Training
                ↓
TimeSeriesSplit Validation
                ↓
Model Evaluation
                ↓
Saved XGBoost Model
                ↓
FastAPI Prediction Service
                ↓
SQLite Forecast Storage
                ↓
React Frontend
                ↓
1–24 Hour Demand Forecast
```

## Dataset

The project uses the **UCI Electricity Load Diagrams dataset**.

The original dataset contains electricity consumption measurements recorded at 15-minute intervals for multiple meter series.

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

### Lag Features

Historical demand is used to provide the model with information about recent and seasonal demand patterns.

- `lag_1` — previous hour
- `lag_2` — two hours previously
- `lag_3` — three hours previously
- `lag_24` — same hour on the previous day
- `lag_48` — same hour two days previously
- `lag_168` — same hour one week previously

### Calendar Features

The model also receives:

- Hour of day
- Day of week
- Weekend indicator

### Cyclical Time Features

Hour of day is represented using sine and cosine transformations:

```text
hour_sin
hour_cos
```

This allows the model to represent the cyclical relationship between the end and beginning of the day.

### Rolling Statistics

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

Cross-validation uses `TimeSeriesSplit` with 5 splits.

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

### Production API

The deployed API is available at:

https://energy-forecasting-project-1-phvr.onrender.com

FastAPI's interactive documentation is available at:

https://energy-forecasting-project-1-phvr.onrender.com/docs

### Health Check

```http
GET /health
```

The endpoint verifies that the API is running and that the forecasting service is available.

### Generate a Forecast

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

Example response:

```json
{
  "horizon": 24,
  "forecasts": [
    {
      "datetime": "2015-01-01T00:00:00",
      "forecast": 106385.95
    },
    {
      "datetime": "2015-01-01T01:00:00",
      "forecast": 102445.76
    }
  ]
}
```

The actual response contains one forecast object for each requested hour.

### Retrieve Saved Forecasts

```http
GET /forecasts?limit=100
```

The endpoint returns previously generated forecasts stored in the SQLite database.

The accepted limit is between 1 and 500 records.

## Database

SQLite is used to store:

- Historical demand required for inference
- Generated forecasts
- Forecast creation timestamps

The application initializes the database when the FastAPI application starts.

For deployment, a small historical seed dataset is included at:

```text
Data/Processed/historical_seed.csv
```

This provides the backend with sufficient historical observations to generate forecasts when the production SQLite database is initially empty.

The local database file itself is excluded from version control.

### Production Persistence

The current deployment uses SQLite. On cloud hosting, local filesystem persistence may not survive service recreation or redeployment.

The seed dataset allows the application to recreate the minimum historical state required for forecasting, but generated forecast history should not be considered durable production storage.

A managed relational database such as PostgreSQL would be more appropriate for persistent production storage.

## Frontend

The frontend is built using:

- React
- Vite
- Recharts

The frontend provides an interface for:

- Checking API status
- Selecting a forecast horizon
- Requesting forecasts
- Displaying forecast results
- Viewing previously saved forecasts

### Production Frontend

The deployed frontend is available at:

https://energy-forecasting-project.vercel.app/

The frontend communicates with the backend through the `VITE_API_URL` environment variable.

### Run the Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

The development server runs on:

```text
http://localhost:5173
```

For local development:

```text
VITE_API_URL=http://localhost:8000
```

## Running the Full Application Locally

### 1. Start the Backend

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

The backend will run at:

```text
http://localhost:8000
```

### 2. Start the Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at:

```text
http://localhost:5173
```

The local architecture is:

```text
React Frontend
      ↓
FastAPI Backend
      ↓
XGBoost Model
      ↓
SQLite Database
```

## Installation

### Python Environment

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

### Frontend Dependencies

```bash
cd frontend
npm install
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
├── Data/
│   ├── Raw/
│   ├── Interim/
│   └── Processed/
│       └── historical_seed.csv
│
├── database/
│   ├── migrations/
│   └── schema.sql
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── .gitignore
│   └── .oxlintrc.json
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

## Deployment

The application is deployed as two separate services.

```text
                    ┌──────────────────────┐
                    │   React Frontend     │
                    │       Vercel         │
                    └──────────┬───────────┘
                               │
                               │ HTTPS
                               ↓
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │       Render         │
                    └──────────┬───────────┘
                               │
                     ┌─────────┴─────────┐
                     ↓                   ↓
              XGBoost Model        SQLite Database
```

### Frontend

Hosted on Vercel.

Production environment variable:

```text
VITE_API_URL=https://energy-forecasting-project-1-phvr.onrender.com
```

### Backend

Hosted on Render.

The backend uses the production frontend URL for CORS configuration through:

```text
FRONTEND_URL
```

The trained model is included in the repository so that the deployed API can load it during startup.

## Limitations

This project has several practical limitations:

- The model predicts total demand rather than individual electricity meters.
- The core model is trained for a one-hour-ahead prediction.
- Multi-hour forecasts depend on recursively generated predictions.
- Weather and other external variables are not included.
- The current application uses SQLite for forecast persistence.
- Cloud-hosted SQLite storage is not intended as durable production persistence.
- Forecast accuracy may vary across different periods of electricity demand.
- The model does not currently provide prediction intervals or uncertainty estimates.

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
- Evaluating direct multi-step forecasting against recursive forecasting

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
Render
Vercel
Git
GitHub
```

## Project Status

**Completed — deployed end-to-end.**

The project includes the complete machine learning and application pipeline from electricity demand preprocessing and model development through to a publicly deployed forecasting application.