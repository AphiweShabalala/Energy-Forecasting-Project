from pathlib import Path
import json
import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = PROJECT_ROOT / "models"

MODEL_PATH = MODEL_DIR / "xgboost_energy_forecaster.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def load_metadata():
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {METADATA_PATH}"
        )

    with open(METADATA_PATH, "r") as f:
        return json.load(f)


model = load_model()
metadata = load_metadata()

model_features = metadata["features"]