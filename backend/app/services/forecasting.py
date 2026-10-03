import numpy as np
import pandas as pd

from .model_loader import model, model_features


def forecast_demand(history, horizon=24):
    """
    Generate recursive electricity-demand forecasts.

    Parameters
    ----------
    history : pandas.Series
        Historical hourly total demand with a DatetimeIndex.
    horizon : int
        Number of future hours to forecast.

    Returns
    -------
    pandas.DataFrame
        Forecasts with datetime and forecast columns.
    """

    history = history.copy()

    if not isinstance(history.index, pd.DatetimeIndex):
        raise TypeError("history must have a DatetimeIndex.")

    if history.index.has_duplicates:
        raise ValueError("History contains duplicate timestamps.")

    history = history.sort_index()

    if len(history) < 168:
        raise ValueError(
            "At least 168 historical observations are required."
        )

    if not history.index.to_series().diff().iloc[1:].eq(
        pd.Timedelta(hours=1)
    ).all():
        raise ValueError(
            "History must contain continuous hourly observations."
        )

    values = history.astype(float).tolist()
    timestamps = history.index.tolist()

    forecasts = []

    for _ in range(horizon):

        next_timestamp = timestamps[-1] + pd.Timedelta(hours=1)

        lag_1 = values[-1]
        lag_2 = values[-2]
        lag_3 = values[-3]
        lag_24 = values[-24]
        lag_48 = values[-48]
        lag_168 = values[-168]

        rolling_values = values[-24:]

        rolling_mean_24 = np.mean(rolling_values)
        rolling_std_24 = np.std(rolling_values, ddof=1)

        hour = next_timestamp.hour
        day_of_week = next_timestamp.dayofweek
        is_weekend = int(day_of_week >= 5)

        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)

        features = pd.DataFrame([{
            "total_demand": values[-1],
            "lag_1": lag_1,
            "lag_2": lag_2,
            "lag_3": lag_3,
            "lag_24": lag_24,
            "lag_48": lag_48,
            "lag_168": lag_168,
            "hour": hour,
            "day_of_week": day_of_week,
            "is_weekend": is_weekend,
            "hour_sin": hour_sin,
            "hour_cos": hour_cos,
            "rolling_mean_24": rolling_mean_24,
            "rolling_std_24": rolling_std_24,
        }])

        features = features[model_features]

        prediction = float(model.predict(features)[0])

        timestamps.append(next_timestamp)
        values.append(prediction)

        forecasts.append({
            "datetime": next_timestamp,
            "forecast": prediction,
        })

    return pd.DataFrame(forecasts)