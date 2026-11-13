import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import streamlit as st, plotly.express as px
from src.demo_data import load_demo_data
from dashboard.style import apply_style,header,metric,PALETTE
apply_style(); df=load_demo_data(); header('Sales analysis','Explore revenue, order volume and performance patterns across the demo store.','ANALYTICS / SALES')
df=df[df.delivery_status=='Delivered'].copy(); df['month']=df.order_date.dt.to_period('M').astype(str)
a,b,c=st.columns(3)
with a: metric('REVENUE',f"${df.total_amount.sum():,.0f}",'Delivered demo orders')
with b: metric('ORDERS',f"{df.order_id.nunique():,}",'Unique transactions')
with c: metric('AVG. ORDER VALUE',f"${df.total_amount.sum()/df.order_id.nunique():,.2f}",'Revenue per order')
st.subheader('Monthly revenue trend'); monthly=df.groupby('month').total_amount.sum().reset_index(); fig=px.line(monthly,x='month',y='total_amount',markers=True);fig.update_traces(line_color=PALETTE['teal']);fig.update_layout(height=350,xaxis_title='',yaxis_title='Revenue (USD)',paper_bgcolor='white',plot_bgcolor='white');st.plotly_chart(fig,use_container_width=True)
l,r=st.columns(2)
with l:
 st.subheader('Revenue by category'); x=df.groupby('category').total_amount.sum().sort_values(ascending=False).reset_index();st.plotly_chart(px.bar(x,x='category',y='total_amount',text_auto='.2s'),use_container_width=True)
with r:
 st.subheader('Delivery status mix'); x=load_demo_data().delivery_status.value_counts().reset_index();x.columns=['status','orders'];st.plotly_chart(px.pie(x,names='status',values='orders',hole=.5),use_container_width=True)
st.info('Sample interpretation: use the final dataset to identify the actual peak month, category contribution and delivery mix. Do not treat demo patterns as business evidence.')
