import streamlit as st
from dashboard.style import apply_style,header
apply_style();header('About this workspace','Project scope, technology and implementation roadmap.','COMMERCEIQ / ABOUT')
st.markdown('''### E-Commerce Business Intelligence & Customer Analytics Platform
A portfolio-grade implementation of the WeIntern Week 1 assignment, designed around a real multi-table e-commerce dataset.

**Selected production dataset:** Olist Brazilian E-Commerce Public Dataset (Kaggle), consisting of nine relational CSV files. Customer repeat-purchase analysis will use `customer_unique_id`.

### Technology
- Python, Pandas and NumPy — ingestion, cleaning and analysis
- Jupyter Notebook — reproducible analytical workflow
- Plotly — interactive visualizations
- Streamlit — multi-page analytics application
- Git and GitHub — version control and submission

### Development stages
1. Approve this sample UI and page structure.
2. Integrate the original Olist CSV files and validate relationships.
3. Build documented cleaning pipeline and cleaned outputs.
4. Implement KPIs, sales trends and customer analytics.
5. Replace all sample metrics and charts with verified analysis.
6. Complete final report, README, tests and GitHub-ready repository.

**Important:** This is a frontend and workflow sample. All displayed transaction data is synthetic and must not be represented as real business findings.''')
