import streamlit as st

from dashboard.style import apply_style, header


apply_style()

header(
    "About CommerceIQ",
    "Project overview, analytical methodology, technology and data limitations.",
    "COMMERCEIQ / ABOUT",
)

st.markdown("""
## E-Commerce Business Intelligence & Customer Analytics Platform

CommerceIQ is a multi-page business intelligence application built using
the **Olist Brazilian E-Commerce Public Dataset**.

The platform transforms relational e-commerce data into actionable
business insights through sales analysis, product performance,
customer analytics, data quality monitoring and downloadable reports.

---

### Dataset overview

- **Dataset:** Olist Brazilian E-Commerce Public Dataset
- **Source:** Kaggle
- **Source files:** 9 relational CSV datasets
- **Coverage:** September 2016 – September 2018
- **Currency:** Brazilian Real (BRL)
- **Analytical grain:** One row per order item in the analytics fact table
- **Customer identification:** `customer_unique_id`

### Analytics modules

| Module | Purpose |
|---|---|
| Executive Dashboard | Business KPIs and overall sales performance |
| Sales Analysis | Revenue trends, categories and order status |
| Product Insights | Product and category performance |
| Customer Analytics | Customer value and repeat-purchase behaviour |
| Data Quality | Missing values, validation and cleaning outcomes |
| Reports & Exports | Business summaries and downloadable CSV reports |

### Technology stack

- **Python** — application logic and data processing
- **Pandas** — data ingestion, transformation and analysis
- **Streamlit** — interactive multi-page dashboard
- **Plotly** — interactive charts and visualizations
- **Git and GitHub** — version control and project collaboration

### Data processing methodology

1. Ingest the nine source datasets.
2. Profile missing values, duplicates and dataset structure.
3. Validate primary keys and foreign-key relationships.
4. Clean the datasets while preserving the original raw files.
5. Build an order-item-level analytical fact table.
6. Aggregate order-level payments and reviews before joining them
   to item-level records.
7. Use the analytical fact table to power dashboard metrics,
   visualizations and exports.

### Business metric definitions

- **Item revenue:** Sum of item prices (`price`) for delivered orders.
- **Freight:** Shipping charges (`freight_value`), reported separately.
- **Delivered orders:** Distinct delivered order IDs.
- **Average order value:** Delivered item revenue divided by
  distinct delivered orders.
- **Units sold:** Count of delivered order-item records.
- **Repeat customer:** A customer with more than one delivered order,
  identified using `customer_unique_id`.

### Important assumptions and limitations

- Revenue represents item prices and excludes freight charges.
- Order-level payment values are repeated across item rows in the
  fact table; they must not be summed directly from that table.
- Orders without order-item records are not represented in the
  order-item fact table.
- Customer analytics use delivered orders.
- Findings are descriptive and do not establish causal relationships.
- The dataset represents historical Brazilian e-commerce activity,
  not live business transactions.

---

### Project status

The data ingestion, validation, cleaning pipeline, analytical fact
table and core dashboard modules have been implemented.

The application uses real Olist analytical data. Raw source datasets
are retained separately from cleaned outputs.
""")

st.caption(
    "CommerceIQ | E-Commerce Business Intelligence Portfolio Project"
)
