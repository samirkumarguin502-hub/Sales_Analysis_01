import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import streamlit as st
from src.demo_data import load_demo_data
from dashboard.style import apply_style,header
apply_style();df=load_demo_data();header('Reports & exports','Review the reporting structure and export demo outputs.','REPORTING / DELIVERABLES')
st.markdown('### Executive summary')
st.write('This sample workspace demonstrates the proposed reporting experience for an e-commerce analytics project. The final report will be populated only after the selected Olist source data has been downloaded, inspected, cleaned and analyzed.')
st.markdown('### Final report structure')
for item in ['1. Title and objective','2. Dataset overview','3. Cleaning summary','4. KPI summary','5. Trend analysis','6. Customer insights','7. Visualization section','8. Key findings','9. Recommendations','10. Limitations and assumptions']:
 st.markdown(f'- {item}')
st.download_button('Download demo dataset (CSV)',df.to_csv(index=False).encode('utf-8'),'commerceiq_demo_data.csv','text/csv')
st.caption('The downloadable file is synthetic demonstration data, not the original Olist dataset.')
