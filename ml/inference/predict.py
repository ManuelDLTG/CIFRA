from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path("artifacts/models/forecast_model.joblib")
FORECAST_PATH = Path("artifacts/forecast/forecast_next_3_months.csv")


def predict_next_months(n_months: int = 3) -> pd.DataFrame:
    payload = joblib.load(MODEL_PATH)

    model = payload["model"]
    feature_cols = payload["feature_cols"]
    history = payload["last_history"].copy()

    history["date"] = pd.to_datetime(history["periodo"] + "-01")
    history = history.sort_values("date")

    forecasts = []

    for _ in range(n_months):
        last_rows = history.tail(3)
        next_date = history["date"].max() + pd.DateOffset(months=1)

        row = {
            "lag_1": last_rows["total_facturado"].iloc[-1],
            "lag_2": last_rows["total_facturado"].iloc[-2],
            "lag_3": last_rows["total_facturado"].iloc[-3],
            "month_num": next_date.month,
            "num_cfdis_lag_1": last_rows["num_cfdis"].iloc[-1],
        }

        X_next = pd.DataFrame([row])[feature_cols]
        prediction = float(model.predict(X_next)[0])

        new_row = {
            "periodo": next_date.strftime("%Y-%m"),
            "date": next_date,
            "num_cfdis": last_rows["num_cfdis"].iloc[-1],
            "total_facturado": prediction,
            "forecast": prediction,
        }

        forecasts.append(new_row)
        history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)

    forecast_df = pd.DataFrame(forecasts)
    return forecast_df[["periodo", "forecast"]]


def main() -> None:
    forecast_df = predict_next_months(n_months=3)

    FORECAST_PATH.parent.mkdir(parents=True, exist_ok=True)
    forecast_df.to_csv(FORECAST_PATH, index=False)

    print(forecast_df)
    print(f"Forecast guardado en: {FORECAST_PATH}")


if __name__ == "__main__":
    main()