# CommerceIQ — E-Commerce Business Intelligence & Customer Analytics Platform

A multi-page Streamlit sample for the WeIntern Pvt Ltd Data Science Internship Week 1 assignment.

> **Sample build:** This version uses deterministic synthetic data to demonstrate the approved UI, navigation, filters, KPIs, charts, data-quality screen and reporting flow. It is not an analysis of the real Olist dataset.

## Pages
- Executive Overview
- Sales Analysis
- Product Insights
- Customer Analytics
- Data Quality & Cleaning
- Reports & Exports
- About & Roadmap

## Run locally
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## Production dataset plan
The production implementation will use the Olist Brazilian E-Commerce Public Dataset (nine relational CSV files). Repeat-customer analysis will use `customer_unique_id`. Raw files will be preserved under `data/raw/`; cleaned files will be written separately under `data/cleaned/`.

## Planned repository deliverables
- `data/raw/` and `data/cleaned/`
- `notebooks/` reproducible analysis
- `src/` ingestion, cleaning, KPI and validation modules
- `dashboard/` multi-page analytics application
- `outputs/charts/` and `outputs/dashboard/`
- `reports/final_report.pdf`
- `tests/` automated checks
- GitHub-ready README and execution instructions

## Data integrity
Never quote the sample KPIs or charts as actual Olist findings. The final report will be generated only from validated source data and documented analytical decisions.
