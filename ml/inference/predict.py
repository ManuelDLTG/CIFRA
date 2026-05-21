from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH    = Path("artifacts/models/forecast_model.joblib")
FORECAST_PATH = Path("artifacts/forecast/forecast_next_3_months.csv")


def predict_next_months(n_months: int = 3) -> pd.DataFrame:
    payload = joblib.load(MODEL_PATH)

    models       = payload["models"]
    feature_cols = payload["feature_cols"]
    history      = payload["last_history"].copy()

    history["date"] = pd.to_datetime(history["periodo"] + "-01")
    history = history.sort_values("date")

    forecasts = []

    for _ in range(n_months):
        last = history.tail(3)
        next_date = history["date"].max() + pd.DateOffset(months=1)

        row = {
            "lag_total_1":    last["total_facturado"].iloc[-1],
            "lag_total_2":    last["total_facturado"].iloc[-2],
            "lag_total_3":    last["total_facturado"].iloc[-3],
            "lag_ingresos_1": last["total_ingresos"].iloc[-1],
            "lag_ingresos_2": last["total_ingresos"].iloc[-2],
            "lag_ingresos_3": last["total_ingresos"].iloc[-3],
            "lag_egresos_1":  last["total_egresos"].iloc[-1],
            "lag_egresos_2":  last["total_egresos"].iloc[-2],
            "lag_egresos_3":  last["total_egresos"].iloc[-3],
            "lag_iva_1":      last["iva_total"].iloc[-1],
            "lag_iva_2":      last["iva_total"].iloc[-2],
            "lag_iva_3":      last["iva_total"].iloc[-3],
            "month_num":      next_date.month,
        }

        X_next = pd.DataFrame([row])[feature_cols]

        pred_total    = float(models["forecast_total"].predict(X_next)[0])
        pred_ingresos = float(models["forecast_ingresos"].predict(X_next)[0])
        pred_egresos  = float(models["forecast_egresos"].predict(X_next)[0])
        pred_iva      = float(models["forecast_iva"].predict(X_next)[0])

        new_row = {
            "periodo":         next_date.strftime("%Y-%m"),
            "date":            next_date,
            "total_facturado": pred_total,
            "total_ingresos":  pred_ingresos,
            "total_egresos":   pred_egresos,
            "iva_total":       pred_iva,
            "forecast":        pred_total,
        }

        forecasts.append(new_row)
        history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)

    forecast_df = pd.DataFrame(forecasts)
    return forecast_df[["periodo", "forecast", "total_ingresos",
                         "total_egresos", "iva_total"]]


def main() -> None:
    forecast_df = predict_next_months(n_months=3)

    FORECAST_PATH.parent.mkdir(parents=True, exist_ok=True)
    forecast_df.to_csv(FORECAST_PATH, index=False)

    print(forecast_df)
    print(f"\nForecast guardado en: {FORECAST_PATH}")


if __name__ == "__main__":
    main()