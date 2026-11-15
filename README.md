# CommerceIQ — E-Commerce Business Intelligence & Customer Analytics Platform

**WeIntern Pvt Ltd | Data Science Internship | Week 1**

CommerceIQ is an end-to-end e-commerce analytics project built using the Olist Brazilian E-Commerce Public Dataset. It covers data ingestion, quality validation, cleaning, analytical modelling, business KPI calculation, visualization and interactive dashboard development.

**Author:** Samir Kumar Guin

## 1. Objectives

- Inspect and understand real-world tabular datasets.
- Identify missing values, duplicates, invalid formats and inconsistent records.
- Clean data while preserving original source files.
- Calculate sales and customer performance KPIs.
- Analyze historical sales trends and customer behaviour.
- Build meaningful visualizations and an interactive dashboard.
- Document findings, assumptions and recommendations.

## 2. Dataset Overview

**Dataset:** Olist Brazilian E-Commerce Public Dataset
**Currency:** Brazilian Real (BRL)

The project uses nine relational datasets:

- Customers
- Geolocation
- Order items
- Payments
- Reviews
- Orders
- Products
- Sellers
- Product category translation

Original and cleaned datasets are kept separately.

### Dataset Deliverables

- `data/raw/` — original source CSV files.
- `data/cleaned/` — cleaned CSV files and analytical fact table.
- `data/cleaned_datasets.zip` — compressed archive containing 10 cleaned CSV files.

The cleaned dataset archive is approximately 57 MB. Extract it to access the cleaned CSV files.

## 3. Data Processing and Methodology

1. Data ingestion and structural inspection.
2. Missing-value and duplicate profiling.
3. Referential-integrity and timestamp validation.
4. Documented cleaning and transformation.
5. Relational integration and order-item fact table creation.
6. KPI calculation and business analysis.
7. Dashboard development and report generation.

Important analytical decisions:

- Reviews use the composite key `(order_id, review_id)`.
- Payment and review attributes are aggregated at order level before joining to item-level records.
- The fact table uses order-item grain.
- Delivered merchandise revenue uses item price; freight is reported separately.
- Payment values are not summed across item-level rows.
- Repeat-customer analysis uses `customer_unique_id`.
- Data-quality anomalies are documented rather than silently overwritten.

## 4. Key Business KPIs

The analysis reports:

| KPI | Result |
|---|---:|
| Delivered merchandise revenue | R$ 13,221,498.11 |
| Delivered orders | 96,478 |
| Average order value | R$ 137.04 |
| Delivered order items | 110,197 |
| Unique delivered customers | 93,358 |
| Repeat customers | 2,801 |
| Repeat-customer rate | 3.00% |
| Delivered freight | R$ 2,198,275.64 |

Revenue represents delivered merchandise item price and excludes freight.

## 5. Major Business Findings

- Health and beauty is the highest-revenue product category.
- São Paulo (SP) contributes the highest customer-state revenue.
- Credit cards account for the largest share of recorded payment value.
- November 2017 is the strongest observed month for delivered merchandise revenue.
- Repeat customers represent approximately 3% of unique delivered customers.
- Product-level revenue analysis identifies the highest-revenue product IDs.

These findings describe the historical dataset and are not forecasts of current market performance.

## 6. Dashboard Pages

1. Executive Overview
2. Sales Analysis
3. Product Insights
4. Customer Analytics
5. Data Quality
6. Reports & Exports
7. About

The dashboard is built using Streamlit and Plotly.

## 7. Visualizations and Reports

- `outputs/charts/` — generated analytical charts.
- `outputs/dashboard/` — dashboard screenshots.
- `notebooks/week1_analysis.ipynb` — analysis notebook.
- `reports/final_report.pdf` — final analytical report.
- `reports/kpi_summary.csv` — KPI results.
- `reports/business_observations.md` — business observations.
- `reports/` — ingestion, cleaning and data-quality reports.
- `screenshots/` — dashboard submission screenshots.

The final report includes dataset overview, cleaning summary, KPI summary, sales trends, customer insights, visual analysis, business findings, data-quality audit, recommendations and limitations.

## 8. Project Structure

```text
Sales_Analysis_01/
├── dashboard/
│   ├── app.py
│   ├── style.py
│   └── pages/
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── cleaned_datasets.zip
├── notebooks/
│   └── week1_analysis.ipynb
├── outputs/
│   ├── charts/
│   └── dashboard/
├── reports/
│   ├── final_report.pdf
│   ├── kpi_summary.csv
│   └── business_observations.md
├── screenshots/
├── scripts/
│   ├── build_submission.py
│   └── build_final_report.py
├── src/
├── tests/
├── requirements.txt
└── README.md
git clone https://github.com/samirkumarguin502-hub/Sales_Analysis_01.git
cd Sales_Analysis_01
python3 -m venv .venv-linux
source .venv-linux/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
python -m pytest -q
python -m compileall -q dashboard src tests scripts
python scripts/build_submission.py
python scripts/build_final_report.py
