import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="GST Reconciliation Bot", layout="wide")
st.title("📊 GST Reconciliation & Analysis Bot")

# --- SIDEBAR: API SETUP ---
with st.sidebar:
    st.header("Setup")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)

# --- STEP 1: FILE UPLOADS ---
col1, col2 = st.columns(2)
with col1:
    gstr1_file = st.file_uploader("Upload GSTR-1 Excel (CSV/XLSX)", type=['csv', 'xlsx'])
with col2:
    pdf_report = st.file_uploader("Upload PDF Export Report", type=['pdf'])

# --- RECONCILIATION LOGIC ---
if gstr1_file and pdf_report:
    st.divider()
    st.subheader("Reconciliation Summary")

    # This is a template of the data we extracted previously. 
    # In a full app, you would use a PDF parser (like PyMuPDF) to automate this.
    recon_data = {
        "Category": ["B2B Taxable Value", "B2CS Taxable Value", "Total CGST", "Total SGST", "Total IGST", "Exempted/Non-GST", "HSN Taxable Total"],
        "GSTR-1 Excel": [20599799.29, 15452678.41, 1493672.88, 1493672.88, 363588.11, 1068679.02, 35842919.18],
        "PDF Report": [20599799.29, 15452678.41, 1493672.88, 1493672.88, 363588.11, 1188648.22, 36344635.70]
    }

    df = pd.DataFrame(recon_data)
    df['Difference'] = df['PDF Report'] - df['GSTR-1 Excel']
    df['Status'] = df['Difference'].apply(lambda x: "✅ Matched" if abs(x) < 1 else "❌ Mismatched")

    # Display Table
    st.table(df.style.format({"GSTR-1 Excel": "{:,.2f}", "PDF Report": "{:,.2f}", "Difference": "{:,.2f}"}))

    # --- STEP 2: AI ANALYSIS ---
    if api_key:
        if st.button("Generate AI Analysis"):
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Constructing the prompt based on the table findings
            mismatches = df[df['Status'] == "❌ Mismatched"]
            prompt = f"""
            Analyze the following GST reconciliation mismatches for Effotel by Sayaji Indore:
            {mismatches.to_string()}
            
            Provide a professional summary of why these differences occur (focus on Exempted supplies and HSN mapping) 
            and what steps the accountant should take.
            """
            
            with st.spinner("Analyzing data..."):
                response = model.generate_content(prompt)
                st.info("### AI Analysis Description")
                st.write(response.text)
    else:
        st.warning("Please enter your Gemini API Key in the sidebar to get the AI analysis description.")

else:
    st.info("Please upload both the GSTR-1 Excel and the PDF Report to begin.")
