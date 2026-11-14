import streamlit as st

PALETTE = {'ink':'#172B4D','muted':'#667085','teal':'#0F766E','mint':'#DDF4EF','gold':'#E5A93D','line':'#E8ECF2','paper':'#F6F8FB'}

def apply_style():
    st.set_page_config(page_title='CommerceIQ | Business Intelligence', page_icon='◈', layout='wide', initial_sidebar_state='expanded')
    st.markdown('''<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
    .stApp {background:#F6F8FB;color:#172B4D;}
    [data-testid="stSidebar"] {background:#101F35;border-right:1px solid #263951;}
    [data-testid="stSidebar"] * {color:#E9F0F8 !important;}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#AFC0D3 !important;}
    .block-container {padding-top:1.7rem;padding-bottom:2.5rem;max-width:1500px;}
    h1,h2,h3 {font-family:'Manrope',sans-serif;color:#172B4D;letter-spacing:-.035em;}
    .eyebrow {font-size:11px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:#0F766E;margin-bottom:7px;}
    .hero {background:linear-gradient(115deg,#142B45 0%,#1D4960 65%,#0F766E 100%);padding:28px 32px;border-radius:18px;color:white;margin-bottom:22px;box-shadow:0 12px 30px rgba(20,43,69,.12);}
    .hero h1 {color:white;font-size:30px;margin:0 0 8px 0;}
    .hero p {color:#D3E4EA;margin:0;font-size:14px;}
    .metric-card {background:white;border:1px solid #E8ECF2;border-radius:14px;padding:17px 18px;min-height:112px;box-shadow:0 3px 12px rgba(23,43,77,.035);}
    .metric-label {font-size:12px;color:#667085;font-weight:600;margin-bottom:10px;}
    .metric-value {font-family:'Manrope',sans-serif;font-size:25px;font-weight:800;color:#172B4D;line-height:1.1;}
    .metric-note {font-size:11px;color:#0F766E;margin-top:8px;}
    .section-head {display:flex;justify-content:space-between;align-items:center;margin:20px 0 10px;}
    .section-head h3 {font-size:17px;margin:0;}
    .panel {background:white;border:1px solid #E8ECF2;border-radius:14px;padding:18px 20px;}
    .small-muted {font-size:12px;color:#667085;}
    .tag {display:inline-block;background:#DDF4EF;color:#0F766E;border-radius:20px;padding:5px 10px;font-size:11px;font-weight:700;}
    div[data-testid="stDataFrame"] {border:1px solid #E8ECF2;border-radius:12px;overflow:hidden;}
    .stButton button {border-radius:9px;font-weight:600;}

    /* Download button styling */
    div[data-testid="stDownloadButton"] button {
        background-color: #0F766E !important;
        color: #FFFFFF !important;
        border: 1px solid #0F766E !important;
        border-radius: 10px !important;
        min-height: 46px;
        padding: 10px 18px;
        font-weight: 700 !important;
        width: 100%;
    }

    div[data-testid="stDownloadButton"] button p,
    div[data-testid="stDownloadButton"] button span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background-color: #115E59 !important;
        border-color: #115E59 !important;
        color: #FFFFFF !important;
    }

    div[data-testid="stDownloadButton"] button:focus {
        box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.25) !important;
        outline: none !important;
    }
    </style>''', unsafe_allow_html=True)

def header(title, subtitle, eyebrow='COMMERCEIQ ANALYTICS'):
    st.markdown(f'<div class="eyebrow">{eyebrow}</div><h1 style="font-size:29px;margin:0 0 5px">{title}</h1><p style="color:#667085;margin:0 0 20px;font-size:14px">{subtitle}</p>', unsafe_allow_html=True)

def metric(label, value, note=''):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)
