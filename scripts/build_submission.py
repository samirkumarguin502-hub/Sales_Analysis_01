from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "cleaned"
REPORTS = ROOT / "reports"
CHARTS = ROOT / "outputs" / "charts"

fact = pd.read_csv(DATA / "fact_order_items.csv", low_memory=False)
orders = pd.read_csv(DATA / "olist_orders_dataset.csv")
payments = pd.read_csv(DATA / "olist_order_payments_dataset.csv")
translation = pd.read_csv(DATA / "product_category_name_translation.csv")

fact["order_purchase_timestamp"] = pd.to_datetime(
    fact["order_purchase_timestamp"], errors="coerce"
)

delivered = fact.loc[fact["order_status"].eq("delivered")].copy()
delivered = delivered.merge(
    translation, on="product_category_name", how="left"
)
delivered["category"] = (
    delivered["product_category_name_english"]
    .fillna(delivered["product_category_name"])
    .fillna("unknown")
)

revenue = delivered["price"].sum()
order_count = delivered["order_id"].nunique()
customers = delivered.groupby("customer_unique_id")["order_id"].nunique()
repeat_customers = int((customers > 1).sum())
customer_count = len(customers)

kpis = pd.DataFrame([
    ("Delivered item revenue (BRL)", revenue),
    ("Delivered orders", order_count),
    ("Average order value (BRL)", revenue / order_count),
    ("Delivered order items", len(delivered)),
    ("Unique delivered customers", customer_count),
    ("Repeat customers", repeat_customers),
    ("Repeat customer rate (%)", repeat_customers / customer_count * 100),
    ("Delivered freight (BRL)", delivered["freight_value"].sum()),
    ("Total source orders", orders["order_id"].nunique()),
    ("Payment value (BRL)", payments["payment_value"].sum()),
], columns=["KPI", "Value"])

kpis.to_csv(REPORTS / "kpi_summary.csv", index=False)

# Monthly revenue
monthly = (
    delivered.assign(month=delivered["order_purchase_timestamp"].dt.to_period("M").astype(str))
    .groupby("month")["price"].sum()
)
plt.figure(figsize=(12, 5))
monthly.plot(marker="o")
plt.title("Monthly Delivered Item Revenue")
plt.ylabel("Revenue (BRL)")
plt.xlabel("Month")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(CHARTS / "monthly_sales_trend.png", dpi=160)
plt.close()

# Category revenue
category = delivered.groupby("category")["price"].sum().nlargest(10).sort_values()
plt.figure(figsize=(10, 6))
category.plot(kind="barh")
plt.title("Top 10 Product Categories by Revenue")
plt.xlabel("Revenue (BRL)")
plt.tight_layout()
plt.savefig(CHARTS / "revenue_by_category.png", dpi=160)
plt.close()

# State revenue
state = delivered.groupby("customer_state")["price"].sum().nlargest(10).sort_values()
plt.figure(figsize=(9, 5))
state.plot(kind="barh")
plt.title("Top 10 Customer States by Delivered Revenue")
plt.xlabel("Revenue (BRL)")
plt.tight_layout()
plt.savefig(CHARTS / "revenue_by_state.png", dpi=160)
plt.close()

# Top products
products = delivered.groupby("product_id")["price"].sum().nlargest(10).sort_values()
plt.figure(figsize=(10, 6))
products.plot(kind="barh")
plt.title("Top 10 Products by Delivered Revenue")
plt.xlabel("Revenue (BRL)")
plt.tight_layout()
plt.savefig(CHARTS / "top_products.png", dpi=160)
plt.close()

# Payment mix
payment_mix = payments.groupby("payment_type")["payment_value"].sum().sort_values()
plt.figure(figsize=(9, 5))
payment_mix.plot(kind="barh")
plt.title("Payment Method Distribution by Payment Value")
plt.xlabel("Payment value (BRL)")
plt.tight_layout()
plt.savefig(CHARTS / "payment_method_distribution.png", dpi=160)
plt.close()

# Payment method share (pie chart)
plt.figure(figsize=(8, 6))
payment_mix.plot(
    kind="pie",
    autopct="%1.1f%%",
    startangle=90
)
plt.title("Payment Method Share by Recorded Payment Value")
plt.ylabel("")
plt.tight_layout()
plt.savefig(CHARTS / "payment_method_share_pie.png", dpi=160)
plt.close()

# Evidence-based observations
top_category = delivered.groupby("category")["price"].sum().idxmax()
top_category_revenue = delivered.groupby("category")["price"].sum().max()
top_state = delivered.groupby("customer_state")["price"].sum().idxmax()
top_state_revenue = delivered.groupby("customer_state")["price"].sum().max()
top_payment = payments.groupby("payment_type")["payment_value"].sum().idxmax()
top_payment_value = payments.groupby("payment_type")["payment_value"].sum().max()
top_month = monthly.idxmax()
top_month_revenue = monthly.max()
repeat_rate = repeat_customers / customer_count * 100
top_product_id = delivered.groupby("product_id")["price"].sum().idxmax()
top_product_revenue = delivered.groupby("product_id")["price"].sum().max()

observations = [
    f"Delivered merchandise revenue totals R$ {revenue:,.2f}, excluding freight.",
    f"The dataset contains {order_count:,} delivered orders and {len(delivered):,} delivered order-item records.",
    f"Average delivered order value is R$ {revenue / order_count:,.2f}, calculated as merchandise revenue divided by delivered orders.",
    f"{repeat_customers:,} of {customer_count:,} delivered customers purchased more than once ({repeat_rate:.2f}% repeat-customer rate).",
    f"The highest-revenue product category is {top_category}, generating R$ {top_category_revenue:,.2f}.",
    f"The highest-revenue customer state is {top_state}, generating R$ {top_state_revenue:,.2f}.",
    f"The highest-value payment method is {top_payment}, with R$ {top_payment_value:,.2f} in recorded payment value.",
    f"The strongest month by delivered merchandise revenue is {top_month}, at R$ {top_month_revenue:,.2f}.",
    f"The highest-revenue product ID is {top_product_id}, generating R$ {top_product_revenue:,.2f}."
]

with open(REPORTS / "business_observations.md", "w", encoding="utf-8") as f:
    f.write("# CommerceIQ — Evidence-based Business Observations\n\n")
    for i, item in enumerate(observations, 1):
        f.write(f"{i}. {item}\n\n")
    f.write(
        "## Methodology note\n"
        "Revenue uses delivered item price and excludes freight. "
        "Payment value is aggregated from the payment table. "
        "The dataset is historical Olist data, so findings are descriptive "
        "and should not be interpreted as current market forecasts.\n"
    )

print("KPI summary created:", REPORTS / "kpi_summary.csv")
print("Business observations created:", REPORTS / "business_observations.md")
print("Charts created:", len(list(CHARTS.glob("*.png"))))
print(kpis.to_string(index=False))
