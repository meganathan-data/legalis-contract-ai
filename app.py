import streamlit as st
import json
import base64
import plotly.graph_objects as go
from utils import extract_text_from_file, truncate_text
from analyzer import analyze_agreement, create_template_draft

# --- CONFIGURATION ---
st.set_page_config(page_title="Legalis", layout="wide")

# --- HARDCODED API KEY ---
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("Missing API Key. Please configure secrets.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("Legalis AI ⚖️")
st.sidebar.caption("Powered by OpenAI GPT-4")

mode = st.sidebar.radio("Select Mode", ["Analyze Contract", "Draft Template"])

# --- ANALYZE CONTRACT MODE ---
if mode == "Analyze Contract":
    st.title("📄 Contract Risk Analyzer")
    st.markdown("Upload a contract to identify risks for Indian SMEs.")
    
    f = st.file_uploader("Upload Agreement", type=['pdf', 'docx', 'txt'])
    
    if f and st.button("Analyze Contract"):
        with st.spinner("Extracting text and identifying legal risks..."):
            # 1. Extract Text
            txt = extract_text_from_file(f)
            
            # 2. Analyze using Hardcoded Key
            res = analyze_agreement(txt, API_KEY)
            
            if "error" in res:
                st.error(res["error"])
            else:
                # 3. Dashboard Layout
                score = res.get("overall_risk_score", 0)
                
                # Top Row: Score & Summary
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Risk Score", f"{score}/100", delta="-High Risk" if score > 70 else "Safe")
                    st.info(f"**Type:** {res.get('contract_type', 'Unknown')}")
                with col2:
                    st.subheader("Executive Summary")
                    st.write(res.get("summary", "No summary available."))
                
                st.divider()
                
                # Clause Breakdown
                st.subheader("🚩 Clause Analysis")
                for c in res.get("clauses", []):
                    # Color Logic
                    risk_color = "red" if c['risk'] == "High" else "orange" if c['risk'] == "Medium" else "green"
                    
                    with st.expander(f":{risk_color}[{c['risk']} Risk]: {c['topic']}"):
                        st.markdown(f"**Context:** {c['excerpt']}")
                        st.markdown(f"**Why it matters:** {c['explanation']}")
                        st.info(f"**Recommendation:** {c['recommendation']}")

# --- DRAFT TEMPLATE MODE ---
elif mode == "Draft Template":
    st.title("📝 Smart Legal Drafter")
    
    ctype = st.selectbox("Contract Type", ["NDA", "Employment Agreement", "Service Contract", "Rent Agreement"])
    details = st.text_area("Enter Details (Names, Dates, Salaries, Role etc.)", height=150)
    
    if st.button("Generate Draft"):
        if not details:
            st.warning("Please enter some details first.")
        else:
            with st.spinner("Drafting legal document..."):
                draft = create_template_draft(ctype, details, API_KEY)
                st.subheader("Draft Preview")
                st.text_area("Copy your contract:", draft, height=600)