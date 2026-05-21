from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.utils.athena_connector import get_serie_temporal_completa


MODEL_PATH = Path("artifacts/models/forecast_model.joblib")


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["periodo"] + "-01")
    df = df.sort_values("date")

    for lag in [1, 2, 3]:
        df[f"lag_total_{lag}"]    = df["total_facturado"].shift(lag)
        df[f"lag_ingresos_{lag}"] = df["total_ingresos"].shift(lag)
        df[f"lag_egresos_{lag}"]  = df["total_egresos"].shift(lag)
        df[f"lag_iva_{lag}"]      = df["iva_total"].shift(lag)

    df["month_num"] = df["date"].dt.month

    return df.dropna()


def train_model() -> None:
    df = get_serie_temporal_completa()
    features_df = build_features(df)

    feature_cols = [
        "lag_total_1", "lag_total_2", "lag_total_3",
        "lag_ingresos_1", "lag_ingresos_2", "lag_ingresos_3",
        "lag_egresos_1", "lag_egresos_2", "lag_egresos_3",
        "lag_iva_1", "lag_iva_2", "lag_iva_3",
        "month_num",
    ]

    targets = {
        "total_facturado": "forecast_total",
        "total_ingresos":  "forecast_ingresos",
        "total_egresos":   "forecast_egresos",
        "iva_total":       "forecast_iva",
    }

    models = {}
    metrics = {}

    for target_col, forecast_name in targets.items():
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

        mae  = mean_absolute_error(y_test, preds)
        rmse = mean_squared_error(y_test, preds) ** 0.5

        models[forecast_name] = model
        metrics[forecast_name] = {"mae": mae, "rmse": rmse}

        print(f"\n{forecast_name}:")
        print(f"  MAE:  {mae:,.2f}")
        print(f"  RMSE: {rmse:,.2f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "models":       models,
            "feature_cols": feature_cols,
            "metrics":      metrics,
            "last_history": df,
        },
        MODEL_PATH,
    )

    print(f"\nModelos guardados en: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()