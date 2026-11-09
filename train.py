"""Train a classifier on the DVC-tracked dataset and write metrics.

Inputs  : data/raw/train.csv (versioned by DVC), params.yaml
Outputs : models/model.pkl (versioned by DVC), metrics.json (tracked by Git)
"""
import json
import os

import joblib
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

DATA_PATH = "data/raw/train.csv"
MODEL_PATH = "models/model.pkl"
METRICS_PATH = "metrics.json"


def main() -> None:
    with open("params.yaml") as f:
        params = yaml.safe_load(f)["train"]

    df = pd.read_csv(DATA_PATH)
    X, y = df.drop(columns="target"), df["target"]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=params["test_size"],
        random_state=params["seed"],
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=params["n_estimators"],
        random_state=params["seed"],
    ).fit(X_train, y_train)

    preds = model.predict(X_test)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, preds)), 4),
        "f1": round(float(f1_score(y_test, preds)), 4),
        "rows": int(len(df)),
    }

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Trained on {len(X_train)} rows, evaluated on {len(X_test)} rows")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
