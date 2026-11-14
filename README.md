# CommerceIQ — E-Commerce Business Intelligence & Customer Analytics Platform

CommerceIQ is a multi-page Business Intelligence and analytics platform built using Python, Pandas, Plotly and Streamlit. It analyzes the Olist Brazilian E-Commerce Public Dataset to provide insights into sales performance, products, customers and data quality.

## Project Highlights

- Real-world e-commerce data analysis using the Olist dataset.
- Data ingestion, profiling and validation.
- Data cleaning with documented quality checks.
- Relational data integration and order-item fact table creation.
- Interactive dashboards with date and category filters.
- Sales, product and customer analytics.
- Data quality monitoring and cleaning reports.
- Automated tests for core data pipeline functionality.

## Dashboard Pages

1. Executive Overview — key business KPIs and overall performance.
2. Sales Analysis — revenue trends, category performance and order status.
3. Product Insights — product revenue, units sold and category contribution.
4. Customer Analytics — customer purchase frequency, repeat customers and revenue.
5. Data Quality & Cleaning — missing values, duplicates, validation and cleaning summaries.
6. Reports & Exports — project reports and analytical outputs.
7. About — project information, dataset and methodology.

## Technology Stack

- Python
- Pandas and NumPy
- Streamlit
- Plotly
- Pytest
- Git and GitHub

## Dataset

**Olist Brazilian E-Commerce Public Dataset**

The project uses nine relational CSV datasets covering customers, orders, order items, payments, reviews, products, sellers, geolocation and product category translations.

Raw source files are preserved separately from cleaned datasets.

- `data/raw/` — original source datasets
- `data/cleaned/` — cleaned datasets and analytical fact table
- `reports/` — ingestion, validation and cleaning reports

The dataset represents historical Brazilian e-commerce activity. Monetary values are represented in Brazilian Real (BRL).

## Project Structure

```text
Sales_Analysis_01/
├── dashboard/
│   ├── app.py
│   ├── style.py
│   └── pages/
├── src/
│   ├── data_ingestion.py
│   ├── data_validation.py
│   ├── data_cleaning.py
│   ├── build_analytics.py
│   └── analytics_data.py
├── data/
│   ├── raw/
│   └── cleaned/
├── reports/
├── tests/
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/samirkumarguin502-hub/Sales_Analysis_01.git
cd Sales_Analysis_01
```

### 2. Create a virtual environment

For Linux / WSL:

```bash
python3 -m venv .venv-linux
source .venv-linux/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run dashboard/app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

## Testing

Run the automated test suite:

```bash
python -m pytest -q
```

Compile-check the dashboard and source modules:

```bash
python -m compileall -q dashboard src tests
```

## Data Integrity and Analytical Methodology

- Raw source datasets are kept separate from cleaned datasets.
- Duplicate and missing-value checks are performed during validation.
- Foreign-key relationships are checked before analytical integration.
- Reviews are handled using the composite key `(order_id, review_id)`.
- Payment and review data are aggregated at order level before joining to order items.
- The analytical fact table uses order-item grain.
- Delivered merchandise revenue is calculated using item price; freight is excluded.
- Order-level payment totals are not summed directly across item rows because they can repeat for multiple items.
- Repeat-customer analysis uses `customer_unique_id`.
- Data-quality anomalies are reported transparently rather than silently treated as valid records.

## Test Status

The project currently has 13 automated tests passing.

Run the test command above to verify the current checkout.

## GitHub Repository

[Sales_Analysis_01](https://github.com/samirkumarguin502-hub/Sales_Analysis_01)

## Project Context

Developed as an advanced implementation of the WeIntern Pvt Ltd Data Science Internship Week 1 assignment, extending the initial dashboard concept into a real-dataset analytics project.
