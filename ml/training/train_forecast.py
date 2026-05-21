from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.utils.athena_connector import get_serie_temporal


MODEL_PATH = Path("artifacts/models/forecast_model.joblib")


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["periodo"] + "-01")
    df = df.sort_values("date")

    for lag in [1, 2, 3]:
        df[f"lag_{lag}"] = df["total_facturado"].shift(lag)

    df["month_num"] = df["date"].dt.month
    df["num_cfdis_lag_1"] = df["num_cfdis"].shift(1)

    return df.dropna()


def train_model() -> None:
    df = get_serie_temporal()
    features_df = build_features(df)

    feature_cols = ["lag_1", "lag_2", "lag_3", "month_num", "num_cfdis_lag_1"]
    target_col = "total_facturado"

    X = features_df[feature_cols]
    y = features_df[target_col]

    split_idx = int(len(features_df) * 0.8)

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        min_samples_leaf=2,
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds) ** 0.5

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "model": model,
            "feature_cols": feature_cols,
            "target_col": target_col,
            "mae": mae,
            "rmse": rmse,
            "last_history": df,
        },
        MODEL_PATH,
    )

    print("Modelo entrenado correctamente.")
    print(f"MAE:  {mae:,.2f}")
    print(f"RMSE: {rmse:,.2f}")
    print(f"Modelo guardado en: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()