import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard.style import apply_style, header, metric, PALETTE


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"

AUDIT_PATH = REPORTS / "data_quality_audit.csv"
CLEANING_PATH = REPORTS / "data_cleaning_summary.csv"
INGESTION_PATH = REPORTS / "data_ingestion_summary.csv"

st.set_page_config(
    page_title="Data Quality | CommerceIQ",
    layout="wide",
)

apply_style()


@st.cache_data
def load_report(path):
    if not path.exists():
        raise FileNotFoundError(f"Report not found: {path}")
    return pd.read_csv(path)


try:
    audit = load_report(AUDIT_PATH)
    cleaning = load_report(CLEANING_PATH)
    ingestion = load_report(INGESTION_PATH)
except Exception as exc:
    st.error(f"Unable to load quality reports: {exc}")
    st.stop()


header(
    "Data quality & cleaning",
    "Monitor data completeness, validation exceptions and cleaning outcomes.",
    "DATA OPERATIONS / QUALITY",
)

# --------------------------------------------------
# DATASET OVERVIEW
# --------------------------------------------------

total_datasets = len(ingestion)
total_rows = int(ingestion["rows"].sum())
total_missing = int(ingestion["missing_cells"].sum())
total_duplicates_removed = int(cleaning["rows_removed"].sum())

critical_failures = int(
    ((audit["severity"] == "CRITICAL") & (audit["value"] > 0)).sum()
)
warning_checks = int((audit["severity"] == "WARNING").sum())
info_checks = int((audit["severity"] == "INFO").sum())

st.subheader("Data quality overview")

a, b, c, d = st.columns(4)

with a:
    metric("DATASETS INSPECTED", f"{total_datasets:,}", "Olist source datasets")

with b:
    metric("SOURCE ROWS", f"{total_rows:,}", "Before cleaning")

with c:
    metric("MISSING CELLS", f"{total_missing:,}", "Across ingested datasets")

with d:
    metric("ROWS REMOVED", f"{total_duplicates_removed:,}", "During cleaning pipeline")

st.divider()

# --------------------------------------------------
# AUDIT SEVERITY
# --------------------------------------------------

st.subheader("Validation severity distribution")

a, b, c = st.columns(3)

with a:
    metric("CRITICAL FAILURES", f"{critical_failures:,}", "Critical rules with exceptions")

with b:
    metric("WARNING CHECKS", f"{warning_checks:,}", "Require interpretation")

with c:
    metric("INFO CHECKS", f"{info_checks:,}", "Informational findings")

severity_order = ["CRITICAL", "WARNING", "INFO"]

severity_counts = (
    audit["severity"]
    .value_counts()
    .reindex(severity_order, fill_value=0)
    .rename_axis("severity")
    .reset_index(name="checks")
)

severity_fig = px.bar(
    severity_counts,
    x="severity",
    y="checks",
    color="severity",
    text="checks",
    category_orders={"severity": severity_order},
    color_discrete_map={
        "CRITICAL": "#D9534F",
        "WARNING": "#E5A93D",
        "INFO": "#4285A4",
    },
)

severity_fig.update_traces(
    textposition="outside",
    textfont=dict(size=15, color="#111827"),
    cliponaxis=False,
)

severity_fig.update_layout(
    template="plotly_white",
    height=390,
    showlegend=False,
    margin=dict(l=65, r=45, t=45, b=75),
    font=dict(family="Arial", size=15, color="#111827"),
    xaxis=dict(
        title=dict(text="Severity", font=dict(size=15, color="#111827")),
        tickfont=dict(size=14, color="#111827"),
        showgrid=False,
        automargin=True,
    ),
    yaxis=dict(
        title=dict(text="Number of checks", font=dict(size=15, color="#111827")),
        tickfont=dict(size=13, color="#111827"),
        gridcolor="#D9DEE7",
        rangemode="tozero",
        automargin=True,
    ),
    paper_bgcolor="white",
    plot_bgcolor="white",
)

st.plotly_chart(severity_fig, use_container_width=True)

st.caption(
    "Severity counts represent audit checks, not necessarily the number "
    "of failed records. Inspect the exception values below."
)

st.divider()

# --------------------------------------------------
# CLEANING SUMMARY
# --------------------------------------------------

st.subheader("Data cleaning summary")

cleaning_display = cleaning.copy()

cleaning_display["dataset"] = (
    cleaning_display["dataset"]
    .str.replace("_dataset.csv", "", regex=False)
)

st.dataframe(
    cleaning_display,
    hide_index=True,
    use_container_width=True,
)

cleaning_chart = cleaning[
    ["dataset", "original_rows", "cleaned_rows"]
].copy()

cleaning_chart["dataset"] = (
    cleaning_chart["dataset"]
    .str.replace("_dataset.csv", "", regex=False)
)

cleaning_chart = cleaning_chart.melt(
    id_vars="dataset",
    var_name="stage",
    value_name="rows",
)

cleaning_fig = px.bar(
    cleaning_chart,
    y="dataset",
    x="rows",
    color="stage",
    barmode="group",
    orientation="h",
    text="rows",
    category_orders={
        "dataset": cleaning_chart["dataset"].tolist()[::-1]
    },
    color_discrete_map={
        "original_rows": "#A9B8A0",
        "cleaned_rows": "#147D78",
    },
)

cleaning_fig.update_traces(
    texttemplate="%{x:,.0f}",
    textposition="outside",
    textfont=dict(size=11, color="#111827"),
    cliponaxis=False,
)

cleaning_fig.update_layout(
    template="plotly_white",
    height=570,
    margin=dict(l=175, r=95, t=35, b=65),
    font=dict(family="Arial", size=13, color="#111827"),
    xaxis=dict(
        title=dict(text="Number of rows", font=dict(size=14, color="#111827")),
        tickfont=dict(size=12, color="#111827"),
        gridcolor="#D9DEE7",
        tickformat=",",
        automargin=True,
    ),
    yaxis=dict(
        title="",
        tickfont=dict(size=12, color="#111827"),
        automargin=True,
    ),
    legend=dict(
        title=dict(text="Pipeline stage", font=dict(size=13, color="#111827")),
        font=dict(size=12, color="#111827"),
    ),
    paper_bgcolor="white",
    plot_bgcolor="white",
)

st.plotly_chart(cleaning_fig, use_container_width=True)

st.divider()

# --------------------------------------------------
# DATA INGESTION PROFILE
# --------------------------------------------------

st.subheader("Dataset ingestion profile")

ingestion_display = ingestion.copy()

ingestion_display["dataset"] = (
    ingestion_display["dataset"]
    .str.replace("_dataset.csv", "", regex=False)
)

st.dataframe(
    ingestion_display,
    hide_index=True,
    use_container_width=True,
)

# --------------------------------------------------
# MISSING VALUE PROFILE
# --------------------------------------------------

st.subheader("Missing value profile")

missing_profile = (
    ingestion[
        [
            "dataset",
            "missing_cells",
            "missing_percentage",
        ]
    ]
    .sort_values("missing_cells", ascending=False)
    .copy()
)

missing_profile["dataset"] = (
    missing_profile["dataset"]
    .str.replace("_dataset.csv", "", regex=False)
)

missing_profile = missing_profile[
    missing_profile["missing_cells"] > 0
]

if not missing_profile.empty:

    missing_fig = px.bar(
        missing_profile,
        x="missing_cells",
        y="dataset",
        orientation="h",
        text="missing_cells",
    )

    missing_fig.update_traces(
        marker_color=PALETTE["teal"],
        texttemplate="%{x:,.0f}",
        textposition="outside",
        textfont=dict(size=12, color="#111827"),
        cliponaxis=False,
    )

    missing_fig.update_layout(
        template="plotly_white",
        height=400,
        margin=dict(l=175, r=100, t=35, b=70),
        font=dict(family="Arial", size=13, color="#111827"),
        xaxis=dict(
            title=dict(text="Missing cells", font=dict(size=14, color="#111827")),
            tickfont=dict(size=12, color="#111827"),
            gridcolor="#D9DEE7",
            tickformat=",",
            automargin=True,
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=13, color="#111827"),
            automargin=True,
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    st.plotly_chart(missing_fig, use_container_width=True)

st.dataframe(
    missing_profile,
    hide_index=True,
    use_container_width=True,
)

st.divider()

# --------------------------------------------------
# VALIDATION RESULTS
# --------------------------------------------------

st.subheader("Detailed validation results")

audit_display = audit.copy()

audit_display["result"] = audit_display["value"].apply(
    lambda value: "No exceptions" if value == 0 else "Exceptions found"
)

st.dataframe(
    audit_display[
        [
            "check",
            "dataset",
            "value",
            "severity",
            "result",
            "details",
        ]
    ],
    hide_index=True,
    use_container_width=True,
    height=520,
)

# --------------------------------------------------
# IMPORTANT DATA INTERPRETATION
# --------------------------------------------------

st.subheader("Data quality observations")

st.info(
    "**Referential integrity:** All six orphan foreign-key checks "
    "reported zero exceptions. Their CRITICAL label identifies the "
    "importance of the rule, not a failed result."
)

st.warning(
    "**Review IDs:** 814 duplicate review_id records were detected. "
    "The cleaning pipeline uses the composite key (order_id, review_id) "
    "and preserves valid review records."
)

st.warning(
    "**Timestamp anomalies:** 1,359 carrier timestamps precede approval "
    "timestamps, and 23 customer delivery timestamps precede carrier "
    "timestamps. Original timestamps are preserved."
)

st.info(
    "**Geolocation:** 261,831 exact duplicate rows were removed. "
    "No business key was assumed for this dataset."
)

st.caption(
    "Source: CommerceIQ Olist ingestion, validation and cleaning reports. "
    "Raw source datasets remain unchanged."
)
