import os
import streamlit as st
from PIL import Image
import json
import datetime
import pandas as pd

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

# Helper Functions
def get_file_stats():
    """Return total files and breakdown by category."""
    files = os.listdir(UPLOAD_FOLDER)
    stats = {"total": len(files), "categories": {cat: 0 for cat in CATEGORIES if cat != "All"}}
    for file in files:
        category = file.split("_")[0] if "_" in file else "Other"
        if category in stats["categories"]:
            stats["categories"][category] += 1
    return stats

def parse_category_from_file(file_name):
    """Extract the category from the file name."""
    return file_name.split("_")[0] if "_" in file_name else "Other"

def format_recent_uploads():
    """Format recent uploads into a DataFrame."""
    recent_files = sorted(os.listdir(UPLOAD_FOLDER), key=lambda x: os.path.getctime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
    recent_data = []
    for i, file in enumerate(recent_files, start=1):
        file_path = os.path.join(UPLOAD_FOLDER, file)
        recent_data.append({
            "No.": i,
            "File Name": file,
            "Category": parse_category_from_file(file),
            "Uploaded On": datetime.datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        })
    return pd.DataFrame(recent_data)

# Dashboard
if menu == "Dashboard":
    st.header("📊 Dashboard")
    stats = get_file_stats()

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
    df = format_recent_uploads()
    st.table(df)

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
        st.success("Files uploaded successfully!")

# File Viewing Module
elif menu == "View Designs":
    st.header("👁️ View Uploaded Files")
    selected_category = st.selectbox("Choose Category", CATEGORIES)

    if selected_category == "All":
        files = os.listdir(UPLOAD_FOLDER)
    else:
        files = [file for file in os.listdir(UPLOAD_FOLDER) if parse_category_from_file(file) == selected_category]

    if files:
        st.write(f"Files in {selected_category}:")
        for file in files:
            st.markdown(f"- {file}")
    else:
        st.info(f"No files found in {selected_category} category.")

# Manage Files
elif menu == "Manage Files":
    st.header("🔧 Manage Uploaded Files")
    files = os.listdir(UPLOAD_FOLDER)

    if files:
        selected_file = st.selectbox("Select a file to manage", files)

        if selected_file:
            st.write(f"Managing: {selected_file}")
            # Extract category from file name and validate
            current_category = parse_category_from_file(selected_file)

            # Change Category
            new_category = st.selectbox("Change Category", CATEGORIES[1:], index=CATEGORIES[1:].index(current_category))
            if st.button("Change Category"):
                old_path = os.path.join(UPLOAD_FOLDER, selected_file)
                new_name = f"{new_category}_{selected_file.split('_', 1)[1]}"
                new_path = os.path.join(UPLOAD_FOLDER, new_name)
                os.rename(old_path, new_path)
                st.success(f"File category changed to {new_category}!")

            # Delete File
            if st.button("Delete File"):
                os.remove(os.path.join(UPLOAD_FOLDER, selected_file))
                st.success("File deleted successfully!")

            # Replace File
            replacement_file = st.file_uploader("Upload a replacement file")
            if replacement_file:
                file_path = os.path.join(UPLOAD_FOLDER, selected_file)
                with open(file_path, "wb") as f:
                    f.write(replacement_file.getbuffer())
                st.success("File replaced successfully!")
    else:
        st.info("No files available to manage.")

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
        - View files by category or see all files at once.
        - Manage files (delete, replace, or change categories).
        - Dashboard with detailed stats and recent uploads.
    """)

# Footer
st.sidebar.info("The app created by Eng. Rekar J.")
