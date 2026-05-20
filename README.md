# CIFRA
### CFDI Intelligence, Forecasting & Reporting Architecture

Pipeline de datos end-to-end sobre AWS para ingesta, transformación y análisis de CFDIs (facturas emitidas). Implementa arquitectura Medallion (Bronze → Silver → Gold) con una app Streamlit para carga y visualización, y modelos de forecasting de flujo de caja.

---

## Arquitectura

```
Streamlit App
     │  (upload XML)
     ▼
API Gateway → Lambda (ingest)
                    │
                    ▼
           S3 Bronze (raw XML)
                    │
              Glue Job (ETL)
                    │
                    ▼
           S3 Silver (Parquet)
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
    Amazon Athena         SageMaker
   (análisis SQL)       (forecasting)
          │                    │
          └─────────┬──────────┘
                    ▼
           S3 Gold (agregados)
                    │
                    ▼
           Streamlit Dashboard
```

## Capas del Datalake

| Capa | Formato | Contenido |
|------|---------|-----------|
| **Bronze** | XML original | CFDIs sin modificar, particionados por RFC/año/mes |
| **Silver** | Parquet | Campos parseados, tipados, enriquecidos con catálogos SAT |
| **Gold** | Parquet | Agregados mensuales por RFC, cliente, concepto |

## Estructura del repo

```
cifra/
├── ingestion/          # Lambda de carga de XMLs a S3 Bronze
├── bronze/             # Utilidades S3 para raw layer
├── silver/             # Glue Job ETL: XML → Parquet
│   └── schemas/        # Schema CFDI 4.0
├── gold/               # Queries Athena y agregaciones
├── ml/
│   ├── training/       # Entrenamiento modelo forecasting
│   └── inference/      # Endpoint SageMaker
├── app/                # Streamlit app
│   ├── pages/          # Upload, Dashboard, Forecast
│   ├── components/     # Gráficas reutilizables
│   └── utils/          # Conector Athena
├── infrastructure/
│   ├── cloudformation/ # Stack AWS (S3, Glue, Lambda, etc.)
│   └── lambda/         # Código de la función Lambda
├── data/
│   └── sample_cfdis/   # CFDIs de ejemplo (SAT público)
├── notebooks/          # Exploración y prototipado
└── docs/               # Arquitectura y diccionario de datos
```

## Setup

```bash
git clone https://github.com/ManuelDLTG/cifra.git
cd cifra
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Llenar con tus credenciales AWS
```

## Correr la app localmente

```bash
streamlit run app/main.py
```

## Deploy infraestructura

```bash
aws cloudformation deploy \
  --template-file infrastructure/cloudformation/cifra_stack.yaml \
  --stack-name cifra-stack \
  --capabilities CAPABILITY_IAM
```

## Stack

- **Ingesta**: API Gateway + AWS Lambda
- **Storage**: Amazon S3 (Medallion)
- **ETL**: AWS Glue (PySpark)
- **Query**: Amazon Athena + Glue Data Catalog
- **ML**: Amazon SageMaker
- **App**: Streamlit
- **IaC**: AWS CloudFormation

## Datos

Los CFDIs de ejemplo provienen del portal de datos abiertos del SAT. No incluir XMLs con datos fiscales reales en el repo.

---

*Proyecto académico — ITAM MCD*
