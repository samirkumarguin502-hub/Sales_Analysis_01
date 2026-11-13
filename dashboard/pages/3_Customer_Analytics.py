import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import streamlit as st,plotly.express as px
from src.demo_data import load_demo_data
from dashboard.style import apply_style,header,metric
apply_style();df=load_demo_data();header('Customer analytics','Explore repeat purchasing, customer value and geographic demand.','ANALYTICS / CUSTOMERS')
cust=df.groupby('customer_unique_id').agg(orders=('order_id','nunique'),revenue=('total_amount','sum'),last_order=('order_date','max')).reset_index(); repeat=(cust.orders>1).sum();a,b,c=st.columns(3)
with a: metric('UNIQUE CUSTOMERS',f'{len(cust):,}','Demo customer identities')
with b: metric('REPEAT CUSTOMERS',f'{repeat:,}',f'{repeat/len(cust):.1%} of demo customers')
with c: metric('CUSTOMER REVENUE',f"${cust.revenue.sum():,.0f}",'Gross demo order value')
l,r=st.columns(2)
with l:
 st.subheader('Customer order frequency');x=cust.orders.value_counts().sort_index().reset_index();x.columns=['orders','customers'];st.plotly_chart(px.bar(x,x='orders',y='customers',text_auto=True),use_container_width=True)
with r:
 st.subheader('Revenue by city');x=df.groupby('city').total_amount.sum().nlargest(7).reset_index();st.plotly_chart(px.bar(x,x='total_amount',y='city',orientation='h'),use_container_width=True)
st.subheader('Highest-value customers');st.dataframe(cust.sort_values('revenue',ascending=False).head(15),hide_index=True,use_container_width=True)
st.info('Repeat-customer logic uses customer_unique_id, as required for the selected Olist dataset. Demo IDs here are synthetic.')
