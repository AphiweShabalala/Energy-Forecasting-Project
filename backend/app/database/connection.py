from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATABASE_DIR = PROJECT_ROOT / "Data" / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "energy_forecasting.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection