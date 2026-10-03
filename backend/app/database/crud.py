from pathlib import Path
import pandas as pd

from .connection import get_connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_demand (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL UNIQUE,
            total_demand REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL,
            forecast REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def get_latest_history(hours=168):
    """
    Retrieve the most recent historical demand observations.

    Returns:
        pandas Series with DatetimeIndex
    """

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT datetime, total_demand
        FROM historical_demand
        ORDER BY datetime DESC
        LIMIT ?
        """,
        (hours,),
    ).fetchall()

    connection.close()

    if len(rows) < hours:
        raise ValueError(
            f"Not enough historical data. "
            f"Required: {hours}, available: {len(rows)}"
        )

    # Reverse the rows so they are chronological
    rows = rows[::-1]

    history = pd.Series(
        data=[row["total_demand"] for row in rows],
        index=pd.to_datetime([row["datetime"] for row in rows]),
        name="total_demand",
    )

    return history


def save_forecasts(forecasts):
    """
    Save generated forecasts to the database.

    forecasts should be a DataFrame containing:
        datetime
        forecast
    """

    connection = get_connection()

    created_at = pd.Timestamp.now().isoformat()

    records = [
        (
            row.datetime.isoformat(),
            float(row.forecast),
            created_at,
        )
        for row in forecasts.itertuples(index=False)
    ]

    connection.executemany(
        """
        INSERT INTO forecasts
        (datetime, forecast, created_at)
        VALUES (?, ?, ?)
        """,
        records,
    )

    connection.commit()
    connection.close()

def get_saved_forecasts(limit=100):
    """Retrieve previously generated forecasts from the database."""

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT datetime, forecast, created_at
        FROM forecasts
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    connection.close()

    # Return chronological order
    rows = rows[::-1]

    return rows