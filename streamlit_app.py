import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Automated Data Insight Generator", layout="wide")

# Helper function for Gemini API call
def call_gemini_api(api_key, prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # Replace with actual Gemini endpoint & formatting as per Gemini's docs
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"  # Update if needed
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        res = response.json()
        # Parse Gemini response (update as per Gemini API)
        return res["candidates"][0]["content"]["parts"][0]["text"]
    else:
        st.error(f"Gemini API Error: {response.text}")
        return None

# Progress display utility
def progress_step(step_num, step_name, total_steps):
    st.info(f"Step {step_num}/{total_steps}: {step_name}")

# PDF generation (simple)
def create_pdf(report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in report_text.split('\n'):
        pdf.multi_cell(0, 10, line)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

st.title("🔎 AI-Powered Data Insights (Gemini + Streamlit)")

st.write("""
Upload your Gemini API key and a dataset (CSV or Excel). The app will analyze, clean, and extract actionable insights automatically.
""")

api_key = st.text_input("Enter your Gemini API Key", type="password")
uploaded_file = st.file_uploader("Upload your data file (CSV/XLSX)", type=["csv", "xlsx"])

if api_key and uploaded_file:
    st.success("API key and data file received!")

    if st.button("Generate Report"):
        # Read file into dataframe
        file_ext = uploaded_file.name.split('.')[-1]
        if file_ext == 'csv':
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        total_steps = 6
        step = 1

        # 1. Data Profiling
        progress_step(step, "Profiling Data...", total_steps)
        st.dataframe(df.head(10))
        profile_prompt = f"You are an expert data analyst. Here are the top 2 rows:\n{df.head(2).to_csv(index=False)}\n\nColumn names: {', '.join(df.columns)}\n\nProfile this data and guess the domain/use-case. Return the profile, types, missing values, and business context."
        profile_result = call_gemini_api(api_key, profile_prompt)
        st.markdown("**Profile Result:**")
        st.write(profile_result)
        step += 1
        time.sleep(1)

        # 2. Data Cleaning Suggestions
        progress_step(step, "Data Cleaning...", total_steps)
        cleaning_prompt = f"Given this data profile:\n{profile_result}\nSuggest cleaning steps and apply them. Return python code for cleaning and a summary of changes."
        cleaning_result = call_gemini_api(api_key, cleaning_prompt)
        st.markdown("**Cleaning Steps:**")
        st.write(cleaning_result)
        step += 1
        time.sleep(1)

        # 3. Metric Calculation & Feature Engineering
        progress_step(step, "Calculating Metrics and Engineering Features...", total_steps)
        metrics_prompt = f"Based on the cleaned data and profile, identify the most important KPIs and metrics to track. Suggest feature engineering if any. Output metric definitions and a sample calculation."
        metrics_result = call_gemini_api(api_key, metrics_prompt)
        st.markdown("**Key Metrics & Features:**")
        st.write(metrics_result)
        step += 1
        time.sleep(1)

        # 4. Analysis & Hidden Patterns
        progress_step(step, "Finding Hidden Patterns & Analysis...", total_steps)
        analysis_prompt = f"Given the data and metrics:\n{metrics_result}\nPerform exploratory data analysis and highlight hidden patterns, outliers, or unusual trends."
        analysis_result = call_gemini_api(api_key, analysis_prompt)
        st.markdown("**Hidden Patterns:**")
        st.write(analysis_result)
        step += 1
        time.sleep(1)

        # 5. Insights & Recommendations
        progress_step(step, "Generating Insights & Recommendations...", total_steps)
        insights_prompt = f"Summarize actionable business insights and recommendations from the previous analysis. Focus on recent performance, possible optimizations, and next steps."
        insights_result = call_gemini_api(api_key, insights_prompt)
        st.markdown("**Actionable Insights:**")
        st.write(insights_result)
        step += 1
        time.sleep(1)

        # 6. Assemble PDF Report
        progress_step(step, "Generating PDF Report...", total_steps)
        full_report = (
            "DATA PROFILE:\n" + profile_result + "\n\n" +
            "DATA CLEANING STEPS:\n" + cleaning_result + "\n\n" +
            "KEY METRICS & FEATURES:\n" + metrics_result + "\n\n" +
            "HIDDEN PATTERNS & ANALYSIS:\n" + analysis_result + "\n\n" +
            "ACTIONABLE INSIGHTS & RECOMMENDATIONS:\n" + insights_result + "\n\n"
        )
        pdf_buffer = create_pdf(full_report)
        st.success("Analysis Complete! Download your report below:")
        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="data_analysis_report.pdf",
            mime="application/pdf"
        )

        # Show the report on-screen as well
        with st.expander("Full Report"):
            st.text(full_report)
else:
    st.warning("Please enter your Gemini API key and upload a dataset to proceed.")

st.markdown("---")
st.caption("Created with ❤️ using Streamlit and Google Gemini")
