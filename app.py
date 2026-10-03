import streamlit as st
import pandas as pd
import zipfile
import os

# Set up browser page configurations
st.set_page_config(page_title="Multi-Excel Dataset Viewer", layout="wide")

st.title("📊 Multi-Excel Dataset Viewer")
st.write("This application dynamically extracts and displays compressed large datasets cleanly.")

ZIP_FILE_PATH = "groharjeva_hisa_etnografska_zbirka.zip"

# 1. Cache the extraction and data loading process so it's super fast after the first load
@st.cache_data
def get_excel_file_names(zip_path):
    """Returns a list of Excel files found inside the zip archive."""
    with zipfile.ZipFile(zip_path, 'r') as z:
        # Filter for file extensions ending in .xlsx or .xls, ignoring hidden system files
        return [f for f in z.namelist() if f.endswith(('.xlsx', '.xls')) and not f.startswith('__MACOSX')]

@st.cache_data
def load_data_from_zip(zip_path, excel_filename):
    """Extracts a specific Excel file from the zip archive into memory and reads it into a DataFrame."""
    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(excel_filename) as f:
            return pd.read_excel(f, engine="openpyxl")

# 2. Main Logic Execution
if os.path.exists(ZIP_FILE_PATH):
    try:
        # Get list of files inside the zip
        excel_files = get_excel_file_names(ZIP_FILE_PATH)
        
        if not excel_files:
            st.error("No Excel files (.xlsx) found inside 'data.zip'.")
        else:
            # 3. Sidebar dropdown menu selector to switch between spreadsheets
            st.sidebar.header("📁 Document Selection")
            selected_file = st.sidebar.selectbox(
                "Choose a sheet to view:",
                excel_files
            )
            
            # 4. Load the selected sheet with a loading animation
            with st.spinner(f"Extracting and processing {selected_file}... Please wait..."):
                df = load_data_from_zip(ZIP_FILE_PATH, selected_file)
            
            # 5. Show quick statistics in the sidebar for the active sheet
            st.sidebar.markdown("---")
            st.sidebar.header("📊 Sheet Properties")
            st.sidebar.metric(label="Total Rows", value=f"{len(df):,}")
            st.sidebar.metric(label="Total Columns", value=len(df.columns))
            
            # 6. Global text search tool setup
            search_query = st.text_input(f"🔍 Search rows dynamically inside '{selected_file}':", "")
            
            if search_query:
                # Filter rows where any column matches the search term
                mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
                filtered_df = df[mask]
            else:
                filtered_df = df

            # 7. Render the optimized, paginated interactive sheet window
            st.subheader(f"Viewing: {selected_file} ({len(filtered_df):,} rows displayed)")
            st.dataframe(filtered_df, use_container_width=True, height=600)

    except Exception as e:
        st.error(f"An error occurred while parsing the zip file archive: {e}")
else:
    st.error("Error: 'data.zip' was not found in the root directory. Please upload your file via the GitHub browser interface and ensure it is named exactly 'data.zip'.")
