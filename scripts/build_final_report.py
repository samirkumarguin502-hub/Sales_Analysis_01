from pathlib import Path
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CHARTS = ROOT / "outputs" / "charts"
OUTPUT = REPORTS / "final_report_review.pdf"

AUTHOR = "Samir Kumar Guin"

# Load verified project outputs
kpis = pd.read_csv(REPORTS / "kpi_summary.csv")
cleaning = pd.read_csv(REPORTS / "data_cleaning_summary.csv")
audit = pd.read_csv(REPORTS / "data_quality_audit.csv")

def kpi(name):
    row = kpis.loc[kpis["KPI"] == name, "Value"]
    if row.empty:
        raise ValueError(f"Missing KPI: {name}")
    return float(row.iloc[0])

def money(value):
    return f"R$ {value:,.2f}"

revenue = kpi("Delivered item revenue (BRL)")
orders = int(kpi("Delivered orders"))
aov = kpi("Average order value (BRL)")
items = int(kpi("Delivered order items"))
customers = int(kpi("Unique delivered customers"))
repeat = int(kpi("Repeat customers"))
repeat_rate = kpi("Repeat customer rate (%)")
freight = kpi("Delivered freight (BRL)")
source_orders = int(kpi("Total source orders"))
payment_value = kpi("Payment value (BRL)")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverTitle", parent=styles["Title"],
    fontSize=25, leading=31, alignment=TA_CENTER,
    textColor=colors.HexColor("#234536"), spaceAfter=12
))
styles.add(ParagraphStyle(
    name="SubtitleCustom", parent=styles["Normal"],
    fontSize=12, leading=18, alignment=TA_CENTER,
    textColor=colors.HexColor("#53665B")
))
styles.add(ParagraphStyle(
    name="SectionCustom", parent=styles["Heading2"],
    fontSize=15, leading=19, textColor=colors.HexColor("#234536"),
    spaceBefore=12, spaceAfter=8
))
styles.add(ParagraphStyle(
    name="BodyCustom", parent=styles["BodyText"],
    fontSize=9, leading=14, spaceAfter=7
))
styles.add(ParagraphStyle(
    name="SmallCustom", parent=styles["BodyText"],
    fontSize=8, leading=11
))
styles.add(ParagraphStyle(
    name="FigureCaption", parent=styles["Italic"],
    fontSize=8, leading=11, alignment=TA_CENTER,
    textColor=colors.HexColor("#53665B"), spaceAfter=10
))

doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4,
    rightMargin=18*mm, leftMargin=18*mm,
    topMargin=18*mm, bottomMargin=18*mm,
    title="CommerceIQ - Week 1 Analytical Report",
    author=AUTHOR,
    subject="E-Commerce Business Intelligence and Customer Analytics"
)

story = []

def heading(number, title):
    story.append(Paragraph(f"{number}. {title}", styles["SectionCustom"]))

def body(text):
    story.append(Paragraph(text, styles["BodyCustom"]))

def make_table(rows, widths=None, header=True):
    header_style = ParagraphStyle(
        "TableHeaderCustom", parent=styles["SmallCustom"],
        textColor=colors.white, fontName="Helvetica-Bold",
        fontSize=7.5, leading=9
    )
    cell_style = styles["SmallCustom"]

    formatted_rows = []
    for row_index, row in enumerate(rows):
        style = header_style if header and row_index == 0 else cell_style
        formatted_rows.append([
            Paragraph(str(value), style) for value in row
        ])

    table = Table(
        formatted_rows,
        colWidths=widths,
        repeatRows=1 if header else 0,
        hAlign="LEFT"
    )
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7DED8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        commands.append(
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#234536"))
        )
    table.setStyle(TableStyle(commands))
    return table

def add_chart(filename, caption, interpretation):
    path = CHARTS / filename
    if not path.exists():
        raise FileNotFoundError(f"Required chart missing: {path}")
    img = Image(str(path))
    img._restrictSize(165*mm, 85*mm)
    story.append(KeepTogether([
        img,
        Paragraph(caption, styles["FigureCaption"]),
        Paragraph(interpretation, styles["BodyCustom"]),
        Spacer(1, 5)
    ]))

# Cover and objective
story.append(Spacer(1, 30*mm))
story.append(Paragraph("CommerceIQ", styles["CoverTitle"]))
story.append(Paragraph(
    "E-Commerce Business Intelligence &amp; Customer Analytics",
    styles["SubtitleCustom"]
))
story.append(Spacer(1, 8*mm))
story.append(Paragraph("Week 1 Analytical Report", styles["Heading1"]))
story.append(Spacer(1, 5*mm))
story.append(Paragraph(
    "Dataset: Olist Brazilian E-Commerce Public Dataset<br/>"
    "Currency: Brazilian Real (BRL)<br/>"
    f"Prepared by: {AUTHOR}",
    styles["SubtitleCustom"]
))
story.append(Spacer(1, 15*mm))
body(
    "<b>Objective:</b> Inspect and clean the supplied e-commerce data, "
    "calculate sales and customer KPIs, identify historical trends, "
    "and communicate findings through visual analysis."
)
body(
    "Scope: All reported metrics are computed from the project datasets "
    "and generated analytical outputs. This is descriptive analysis of "
    "historical Olist data, not a current-market forecast."
)
story.append(PageBreak())

# 1. Dataset overview
heading(1, "Dataset Overview")
body(
    "The project uses nine related Olist CSV datasets: customers, "
    "geolocation, order items, payments, reviews, orders, products, "
    "sellers and product-category translation."
)
body(
    "The analytical fact table is at order-item grain. Payment and review "
    "attributes are summarized at order grain before joining to item rows "
    "to avoid multiplying order-level measures."
)
body(
    "Merchandise revenue is calculated from delivered item price. "
    "Freight is reported separately. Payment value is taken from the "
    "payment table and is not summed across item-grain rows."
)

# 2. Cleaning summary
heading(2, "Data Cleaning Summary")
clean_rows = [[
    "Dataset", "Original rows", "Cleaned rows",
    "Rows removed", "Missing cells"
]]
for _, row in cleaning.iterrows():
    clean_rows.append([
        str(row["dataset"]).replace("_dataset.csv", "").replace(".csv", ""),
        f'{int(row["original_rows"]):,}',
        f'{int(row["cleaned_rows"]):,}',
        f'{int(row["rows_removed"]):,}',
        f'{int(row["remaining_missing_cells"]):,}'
    ])
story.append(make_table(
    clean_rows,
    [48*mm, 27*mm, 27*mm, 25*mm, 25*mm]
))
story.append(Spacer(1, 7))
body(
    "<b>Cleaning decisions:</b> 261,831 exact duplicate geolocation rows "
    "were removed. No rows were removed from the other eight datasets. "
    "The 610 missing product categories were assigned the explicit "
    "'unknown' label. The remaining 1,838 missing product cells were "
    "not imputed."
)
body(
    "The raw products file had 2,448 missing cells; the cleaned file has "
    "1,838. The 610-cell difference is explained by replacing missing "
    "product categories with 'unknown'."
)
body(
    "Missing cells remain in orders (4,908) and reviews (145,903). "
    "These values were retained rather than filled with invented data."
)

# 3. KPI summary
heading(3, "KPI Summary")
kpi_rows = [["KPI", "Result"]]
for name, value in [
    ("Delivered item revenue", money(revenue)),
    ("Delivered orders", f"{orders:,}"),
    ("Average order value", money(aov)),
    ("Delivered order items", f"{items:,}"),
    ("Unique delivered customers", f"{customers:,}"),
    ("Repeat customers", f"{repeat:,} ({repeat_rate:.2f}%)"),
    ("Delivered freight", money(freight)),
    ("Total source orders", f"{source_orders:,}"),
    ("Payment value (all payment records)", money(payment_value)),
]:
    kpi_rows.append([name, value])
story.append(make_table(kpi_rows, [95*mm, 65*mm]))
body(
    "Average order value is delivered merchandise revenue divided by "
    "distinct delivered orders. Freight is excluded from this measure."
)

# 4. Trend analysis
heading(4, "Sales Trend Analysis")
body(
    "Monthly delivered merchandise revenue is used to describe the "
    "historical sales pattern. The strongest observed month was "
    "November 2017, with R$ 987,765.37. The lowest observed month was "
    "December 2016, with R$ 10.90. These are historical observations "
    "and should not be interpreted as current trading performance."
)
add_chart(
    "monthly_sales_trend.png",
    "Figure 1. Monthly delivered merchandise revenue.",
    "Interpretation: The chart shows monthly variation in delivered "
    "item revenue. The peak and low months should be interpreted in "
    "the context of the historical observation period."
)

# 5. Customer insights
heading(5, "Customer Insights")
body(
    f"The delivered dataset contains {customers:,} unique customers. "
    f"{repeat:,} customers placed more than one distinct delivered order, "
    f"representing a repeat-customer rate of {repeat_rate:.2f}%."
)
body(
    "This rate uses customer_unique_id and counts distinct delivered "
    "orders per customer. It indicates that repeat purchasing is a "
    "relatively small share of the observed delivered-customer base. "
    "It does not establish the cause of repeat or one-time purchasing."
)

# 6. Visual analysis
heading(6, "Visual Analysis")
add_chart(
    "revenue_by_category.png",
    "Figure 2. Top product categories by delivered merchandise revenue.",
    "Interpretation: The chart ranks product categories by delivered "
    "item revenue and highlights the categories contributing most "
    "to recorded merchandise sales."
)
add_chart(
    "revenue_by_state.png",
    "Figure 3. Top customer states by delivered merchandise revenue.",
    "Interpretation: The chart compares delivered merchandise revenue "
    "across customer states. It describes revenue distribution, not "
    "population-adjusted demand."
)
add_chart(
    "payment_method_distribution.png",
    "Figure 4. Recorded payment value by payment type.",
    "Interpretation: Payment value is aggregated from the payment "
    "table. It is a separate measure from delivered merchandise revenue."
)
add_chart(
    "payment_method_share_pie.png",
    "Figure 5. Share of recorded payment value by payment type.",
    "Interpretation: The pie chart shows each payment type's proportion "
    "of total recorded payment value."
)
add_chart(
    "top_products.png",
    "Figure 6. Top products by delivered merchandise revenue.",
    "Interpretation: Product identifiers are ranked by delivered item "
    "revenue. Product IDs are used because descriptive product names "
    "are not part of the analytical output."
)

# 7. Key findings (8)
heading(7, "Key Business Findings")
findings = [
    f"Delivered merchandise revenue totals {money(revenue)}, excluding freight.",
    f"Average delivered order value is {money(aov)} across {orders:,} delivered orders.",
    f"{repeat:,} of {customers:,} delivered customers purchased more than once ({repeat_rate:.2f}%).",
    "Health and beauty is the highest-revenue category, at R$ 1,233,131.72.",
    "São Paulo (SP) is the highest-revenue customer state, at R$ 5,067,633.16.",
    "Credit-card payment records total R$ 12,542,084.19, or 78.3% of recorded payment value.",
    "November 2017 is the strongest observed month, with R$ 987,765.37 delivered merchandise revenue.",
    "The highest-revenue product ID generated R$ 63,560 in delivered item revenue."
]
for i, finding in enumerate(findings, 1):
    body(f"<b>{i}.</b> {finding}")

# 8. Audit findings
heading(8, "Data Quality Audit")
audit_rows = [["Audit check", "Dataset", "Value", "Severity"]]
for _, row in audit.iterrows():
    audit_rows.append([
        str(row["check"]),
        str(row["dataset"]),
        f'{int(row["value"]):,}' if pd.notna(row["value"]) else "",
        str(row["severity"])
    ])
audit_table = make_table(
    audit_rows,
    [80*mm, 38*mm, 20*mm, 28*mm]
)
audit_table.setStyle(TableStyle([
    ("FONTSIZE", (0, 0), (-1, -1), 7),
    ("LEADING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 2),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
]))
story.append(audit_table)
body(
    "The audit found 814 repeated review_id values globally, while "
    "the composite key (order_id, review_id) has zero duplicates. "
    "Six foreign-key checks report zero orphan records."
)
body(
    "Timestamp sequence checks flagged 1,359 approval-to-carrier "
    "exceptions and 23 carrier-to-customer delivery exceptions. "
    "These timestamps were not overwritten. Thirteen product categories "
    "have no English translation."
)

# 9. Recommendations
heading(9, "Recommendations")
recommendations = [
    "Investigate timestamp sequence exceptions against source records before applying any correction.",
    "Keep missing product attributes visible and document any future imputation policy.",
    "Translate the 13 unmapped product categories or retain a documented unknown category.",
    "Use order-level deduplication when analyzing review scores or other order-grain measures.",
    "Monitor repeat-customer behaviour and investigate potential retention opportunities.",
    "Align populations and definitions before comparing payment value with delivered merchandise revenue."
]
for i, item in enumerate(recommendations, 1):
    body(f"<b>{i}.</b> {item}")

# 10. Limitations and reproducibility
heading(10, "Limitations, Assumptions and Reproducibility")
body(
    "The Olist dataset covers historical activity from 2016–2018. "
    "The analysis is descriptive and cannot establish causation or "
    "represent current market conditions. The fact table excludes "
    "775 source orders without order-item records."
)
body(
    "Payment values cover payment records and are not directly "
    "comparable with delivered merchandise revenue unless populations "
    "and definitions are aligned. Product IDs are used where product "
    "names are unavailable. Order-level review attributes repeated "
    "across item rows require deduplication for independent review analysis."
)
body(
    "To reproduce the analysis, install dependencies from requirements.txt, "
    "run the project ingestion, cleaning and analytics pipeline, then run "
    "python scripts/build_submission.py followed by "
    "python scripts/build_final_report.py. Run the dashboard with "
    "streamlit run dashboard/app.py and tests with python -m pytest -q."
)
body(
    f"<b>Prepared by:</b> {AUTHOR}<br/>"
    "<b>Project:</b> CommerceIQ — WeIntern Data Science Internship, Week 1"
)

def add_page(canvas, document):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#66756B"))
    canvas.drawString(18*mm, 10*mm, "CommerceIQ | Week 1 Analytical Report")
    canvas.drawRightString(A4[0] - 18*mm, 10*mm, f"Page {document.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=add_page, onLaterPages=add_page)

print("PDF generated:", OUTPUT)
print("Author:", AUTHOR)
print("Sections: 10")
print("Charts embedded: 6")
print("KPI records:", len(kpis))
print("Cleaning records:", len(cleaning))
print("Audit records:", len(audit))
