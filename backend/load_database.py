from pathlib import Path

import pandas as pd

from app.database.connection import get_connection
from app.database.crud import initialize_database


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "Processed"
    / "hourly_demand_features.csv"
)


def load_historical_demand():
    print(f"Loading data from: {DATA_PATH}")

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Data file not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    print(f"Rows loaded: {len(df):,}")
    print(f"Columns: {list(df.columns)}")

    required_columns = {"Unnamed: 0", "total_demand"}

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Convert the saved index back into a datetime column
    df["datetime"] = pd.to_datetime(df["Unnamed: 0"])

    # Keep only what the database needs
    df = df[["datetime", "total_demand"]].copy()

    # Sort chronologically
    df = df.sort_values("datetime")

    # Validate timestamps
    if df["datetime"].duplicated().any():
        raise ValueError("Duplicate timestamps found.")

    if df["datetime"].isna().any():
        raise ValueError("Missing datetime values found.")

    # Validate demand values
    if df["total_demand"].isna().any():
        raise ValueError("Missing total_demand values found.")

    # Validate hourly frequency
    time_difference = df["datetime"].diff().iloc[1:]

    if not time_difference.eq(pd.Timedelta(hours=1)).all():
        raise ValueError(
            "Data does not contain continuous hourly observations."
        )

    # Make sure database tables exist
    initialize_database()

    connection = get_connection()

    # Clear existing historical data
    connection.execute("DELETE FROM historical_demand")

    # Prepare records
    records = [
        (
            row.datetime.isoformat(),
            float(row.total_demand)
        )
        for row in df.itertuples(index=False)
    ]

    # Insert records
    connection.executemany(
        """
        INSERT INTO historical_demand
        (datetime, total_demand)
        VALUES (?, ?)
        """,
        records,
    )

    connection.commit()
    connection.close()

    print("\nDatabase load complete.")
    print(f"Rows inserted: {len(records):,}")
    print(f"First timestamp: {df['datetime'].iloc[0]}")
    print(f"Last timestamp:  {df['datetime'].iloc[-1]}")


if __name__ == "__main__":
    load_historical_demand()