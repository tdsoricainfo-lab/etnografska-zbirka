import streamlit as st
import pandas as pd
import zipfile
import requests
import io

# Set up browser page configurations
st.set_page_config(page_title="Multi-Excel Dataset Viewer", layout="wide")

st.title("📊 Multi-Excel Dataset Viewer")
st.write("This application dynamically downloads, extracts, and displays highly compressed datasets.")

# ⚠️ PASTE YOUR DIRECT DOWNLOAD LINK HERE
ZIP_URL = "https://drive.google.com/file/d/1Gd2OQAX9nqxt5tfpcmPaBMkNQR3WijdO/view?usp=drive_link"

# 1. Download and extract the zip file directly in the cloud memory cache
@st.cache_data
def load_zip_from_cloud(url):
    """Downloads the remote zip file into memory and unzips it."""
    response = requests.get(url)
    response.raise_for_status() # Check for download errors
    return io.BytesIO(response.content)

@st.cache_data
def get_excel_file_names(zip_buffer):
    """Returns a list of Excel files found inside the zip archive archive."""
    with zipfile.ZipFile(zip_buffer, 'r') as z:
        return [f for f in z.namelist() if f.endswith(('.xlsx', '.xls')) and not f.startswith('__MACOSX')]

@st.cache_data
def load_data_from_zip(zip_buffer, excel_filename):
    """Extracts a specific Excel file from the memory buffer and reads it into a DataFrame."""
    with zipfile.ZipFile(zip_buffer, 'r') as z:
        with z.open(excel_filename) as f:
            return pd.read_excel(f, engine="openpyxl")

# 2. Main Logic Execution
if "YOUR_DIRECT_DOWNLOAD_LINK_HERE" in ZIP_URL or not ZIP_URL:
    st.warning("Please edit 'app.py' and replace the ZIP_URL variable placeholder with your actual direct download link.")
else:
    try:
        # Fetch the large zip archive file from the external host link
        with st.spinner("Downloading 458MB data archive from cloud storage... (This takes a moment on first load)"):
            zip_buffer = load_zip_from_cloud(ZIP_URL)
            
        excel_files = get_excel_file_names(zip_buffer)
        
        if not excel_files:
            st.error("No Excel files (.xlsx) found inside the cloud zip archive.")
        else:
            # 3. Sidebar dropdown menu selector to switch between spreadsheets
            st.sidebar.header("📁 Document Selection")
            selected_file = st.sidebar.selectbox("Choose a sheet to view:", excel_files)
            
            # 4. Load the selected sheet with a loading animation
            with st.spinner(f"Extracting and processing {selected_file}..."):
                df = load_data_from_zip(zip_buffer, selected_file)
            
            # 5. Show quick statistics in the sidebar for the active sheet
            st.sidebar.markdown("---")
            st.sidebar.header("📊 Sheet Properties")
            st.sidebar.metric(label="Total Rows", value=f"{len(df):,}")
            st.sidebar.metric(label="Total Columns", value=len(df.columns))
            
            # 6. Global text search tool setup
            search_query = st.text_input(f"🔍 Search rows dynamically inside '{selected_file}':", "")
            
            if search_query:
                mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
                filtered_df = df[mask]
            else:
                filtered_df = df

            # 7. Render the optimized, paginated interactive sheet window
            st.subheader(f"Viewing: {selected_file} ({len(filtered_df):,} rows displayed)")
            st.dataframe(filtered_df, use_container_width=True, height=600)

    except Exception as e:
        st.error(f"An error occurred while fetching or parsing your archive: {e}")
