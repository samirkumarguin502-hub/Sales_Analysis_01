import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import streamlit as st,pandas as pd
from src.demo_data import load_demo_data
from dashboard.style import apply_style,header,metric
apply_style();df=load_demo_data();header('Data quality & cleaning','A transparent view of completeness, duplicates and validation checks.','DATA OPERATIONS / QUALITY')
missing=df.isna().sum().rename('missing_values').to_frame();missing['missing_pct']=(missing.missing_values/len(df)*100).round(2)
dups=int(df.duplicated().sum());bad_qty=int((df.quantity<0).sum());bad_price=int((df.unit_price<=0).sum());bad_dates=int(df.order_date.isna().sum())
a,b,c,d=st.columns(4)
with a: metric('ROWS INSPECTED',f'{len(df):,}','Synthetic sample')
with b: metric('DUPLICATE ROWS',f'{dups:,}','Full-row duplicates')
with c: metric('INVALID QUANTITY',f'{bad_qty:,}','Negative quantity')
with d: metric('INVALID PRICE',f'{bad_price:,}','Zero or negative price')
st.subheader('Missing value profile');st.dataframe(missing,use_container_width=True)
st.subheader('Validation results');checks=pd.DataFrame([['Quantity >= 0',bad_qty,'Pass' if bad_qty==0 else 'Review'],['Unit price > 0',bad_price,'Pass' if bad_price==0 else 'Review'],['Valid order date',bad_dates,'Pass' if bad_dates==0 else 'Review'],['Full-row duplicates',dups,'Pass' if dups==0 else 'Review']],columns=['Rule','Exceptions','Status']);st.dataframe(checks,hide_index=True,use_container_width=True)
st.warning('This page demonstrates the quality-report interface. In the production version, every cleaning decision will be logged and justified; raw source files will remain unchanged.')
