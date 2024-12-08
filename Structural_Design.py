import os
import streamlit as st
from PIL import Image
import json
import datetime
import pandas as pd
import base64

# Configurable Settings
APP_NAME = "🏗️ Structural Design Library"
MAIN_IMAGE = "main_image.jpg"  # Path to your main image (place it in the app folder)

# App Configuration
st.set_page_config(page_title=APP_NAME, layout="wide")
st.title(APP_NAME)

# Display Main Image
if os.path.exists(MAIN_IMAGE):
    st.image(MAIN_IMAGE, use_column_width=True, caption="Welcome to the Structural Design Library!")
else:
    st.warning("Main image not found. Please upload a valid image named 'main_image.jpg' to the app folder.")

# Sidebar Navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Dashboard", "Upload Files", "View Designs", "Manage Files", "Settings", "About"])

# Create necessary directories
UPLOAD_FOLDER = "uploaded_files"
COMMENTS_FOLDER = "comments"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMMENTS_FOLDER, exist_ok=True)

CATEGORIES = ["All", "2D Plans", "3D Plans", "Other"]

# Initialize session state for file management
if "file_list" not in st.session_state:
    st.session_state.file_list = os.listdir(UPLOAD_FOLDER)

# Helper Functions
def refresh_file_list():
    """Refresh the file list in session state."""
    st.session_state.file_list = os.listdir(UPLOAD_FOLDER)

def parse_category_from_file(file_name):
    """Extract the category from the file name."""
    return file_name.split("_")[0] if "_" in file_name else "Other"

def display_file_preview(file_path, file_type):
    """Render file preview for supported file types."""
    if file_type in ["jpg", "png", "jpeg"]:
        st.image(file_path, caption=os.path.basename(file_path), use_column_width=True)
    elif file_type == "pdf":
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    elif file_type == "txt":
        with open(file_path, "r") as f:
            content = f.read()
        st.text_area("Text File Content", content, height=300)
    else:
        st.info("Preview not supported for this file type.")

# Dashboard
if menu == "Dashboard":
    st.header("📊 Dashboard")
    files = st.session_state.file_list
    stats = {"total": len(files), "categories": {cat: 0 for cat in CATEGORIES if cat != "All"}}
    for file in files:
        category = parse_category_from_file(file)
        if category in stats["categories"]:
            stats["categories"][category] += 1

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Files", stats["total"])
    with col2:
        st.metric("2D Plans", stats["categories"]["2D Plans"])
    with col3:
        st.metric("3D Plans", stats["categories"]["3D Plans"])
    with col4:
        st.metric("Other", stats["categories"]["Other"])

    st.subheader("Recent Uploads")
    recent_files = sorted(files, key=lambda x: os.path.getctime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
    recent_data = []
    for i, file in enumerate(recent_files, start=1):
        file_path = os.path.join(UPLOAD_FOLDER, file)
        recent_data.append({
            "No.": i,
            "File Name": file,
            "Category": parse_category_from_file(file),
            "Uploaded On": datetime.datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        })
    st.table(pd.DataFrame(recent_data))

# File Upload Module
elif menu == "Upload Files":
    st.header("📂 Upload and Manage Files")
    uploaded_files = st.file_uploader(
        "Upload your design files (.pdf, .txt, .jpg, .png, .dwg, .skp)", 
        accept_multiple_files=True
    )
    category = st.selectbox("Select File Category", CATEGORIES[1:])  # Exclude "All" for uploads

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(UPLOAD_FOLDER, f"{category}_{uploaded_file.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        refresh_file_list()
        st.success("Files uploaded successfully!")

# File Viewing Module
elif menu == "View Designs":
    st.header("👁️ View Uploaded Files")
    selected_category = st.selectbox("Choose Category", CATEGORIES)

    if selected_category == "All":
        files = st.session_state.file_list
    else:
        files = [file for file in st.session_state.file_list if parse_category_from_file(file) == selected_category]

    if files:
        for file in files:
            st.subheader(file)
            file_path = os.path.join(UPLOAD_FOLDER, file)
            file_ext = file.split(".")[-1].lower()
            display_file_preview(file_path, file_ext)
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download File",
                    data=f,
                    file_name=file,
                    mime="application/octet-stream"
                )
            st.markdown("---")
    else:
        st.info(f"No files found in {selected_category} category.")

# Manage Files
elif menu == "Manage Files":
    st.header("🔧 Manage Uploaded Files")
    files = st.session_state.file_list

    if files:
        selected_file = st.selectbox("Select a file to manage", files)

        if selected_file:
            st.write(f"Managing: {selected_file}")
            # Delete Single File
            if st.button("Delete File"):
                delete_single_file(selected_file)
                st.success("File deleted successfully!")

            # Replace File
            replacement_file = st.file_uploader("Upload a replacement file")
            if replacement_file:
                file_path = os.path.join(UPLOAD_FOLDER, selected_file)
                with open(file_path, "wb") as f:
                    f.write(replacement_file.getbuffer())
                st.success("File replaced successfully!")
                refresh_file_list()

    else:
        st.info("No files available to manage.")

    # Delete All Files
    if st.button("Delete All Files"):
        delete_all_files()
        st.success("All files have been deleted!")

# Settings
elif menu == "Settings":
    st.header("⚙️ Settings")
    new_app_name = st.text_input("Change App Name", value=APP_NAME)
    uploaded_main_image = st.file_uploader("Upload New Main Image", type=["jpg", "png"])
    if st.button("Save Changes"):
        if uploaded_main_image:
            with open(MAIN_IMAGE, "wb") as f:
                f.write(uploaded_main_image.getbuffer())
            st.success("Main image updated!")
        if new_app_name:
            st.experimental_set_query_params(app_name=new_app_name)
            st.success("App name updated! Refresh the page to see changes.")

# About Section
elif menu == "About":
    st.header("ℹ️ About This App")
    st.write("""
        **Structural Design Library** is a web app for civil engineers and architects to:
        - Upload and manage design files.
        - Categorize files for better organization.
        - View files by category or see all files at once with previews and download options.
        - Manage files (delete, replace, or change categories).
        - Delete all files at once if needed.
        - Dashboard with detailed stats and recent uploads.
    """)

# Footer
st.sidebar.info("The app created by Eng. Rekar J.")
