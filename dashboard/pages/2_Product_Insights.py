import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import streamlit as st,plotly.express as px
from src.demo_data import load_demo_data
from dashboard.style import apply_style,header
apply_style();df=load_demo_data();header('Product insights','Understand category contribution, product demand and pricing patterns.','ANALYTICS / PRODUCTS')
a,b=st.columns(2)
with a:
 st.subheader('Top 10 products by revenue');x=df.groupby('product_name').total_amount.sum().nlargest(10).sort_values().reset_index();st.plotly_chart(px.bar(x,x='total_amount',y='product_name',orientation='h',text_auto='.2s'),use_container_width=True)
with b:
 st.subheader('Category sales contribution');x=df.groupby('category').total_amount.sum().reset_index();st.plotly_chart(px.pie(x,names='category',values='total_amount',hole=.55),use_container_width=True)
st.subheader('Product performance table');x=df.groupby(['category','product_name']).agg(units=('quantity','sum'),orders=('order_id','nunique'),revenue=('total_amount','sum'),avg_unit_price=('unit_price','mean')).reset_index().sort_values('revenue',ascending=False);st.dataframe(x,use_container_width=True,hide_index=True)
st.caption('All product rankings are generated from synthetic demonstration records.')
