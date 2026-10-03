import streamlit as st
import pandas as pd
import requests
import io

# Set up browser page configurations
st.set_page_config(page_title="Excel Dataset Viewer", layout="wide")

st.title("📊 Excel Dataset Viewer")
st.write("This application dynamically loads and optimizes a large Excel spreadsheet from Google Drive.")

# 🔗 YOUR OFFICIAL SHARED EXCEL RESOURCE LINK WITH FORCED DOWNLOAD OVERRIDES
EXCEL_URL = "https://docs.google.com/spreadsheets/d/1mXSjfajN24VEDFgbECaLhlyOQZu_I4Eb/edit?usp=drive_link&ouid=111620865490664136973&rtpof=true&sd=true"

# 1. Cache the data load function so it doesn't reload on every user click
@st.cache_data
def load_data_from_google_drive(url):
    """Downloads the remote Excel file into memory and reads it into a DataFrame."""
    # We use a custom User-Agent to make sure Google treats the download smoothly
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    response.raise_for_status() # Check for download errors
    return pd.read_excel(io.BytesIO(response.content), engine="openpyxl")

# 2. Main Logic Execution
try:
    with st.spinner("Downloading and processing spreadsheet from Google Drive... Please wait..."):
        df = load_data_from_google_drive(EXCEL_URL)
    
    # 3. Add a sidebar layout block for data filtering metrics
    st.sidebar.header("📊 Sheet Properties")
    st.sidebar.metric(label="Total Rows Loaded", value=f"{len(df):,}")
    st.sidebar.metric(label="Total Columns", value=len(df.columns))
    
    # 4. Global text search configuration setup
    search_query = st.text_input("🔍 Search rows dynamically across all columns:", "")
    
    if search_query:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        filtered_df = df[mask]
    else:
        filtered_df = df

    # 5. Display the interactive, paginated spreadsheet window
    st.subheader(f"Showing Data ({len(filtered_df):,} rows found)")
    st.dataframe(filtered_df, use_container_width=True, height=600)

except Exception as e:
    st.error(f"An unexpected error occurred while reading the document: {e}")
    st.info("⚠️ Double check: Make sure your file in Google Drive is shared as 'Anyone with the link can view' so the app can pull it!")
