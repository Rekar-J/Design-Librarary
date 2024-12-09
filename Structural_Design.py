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
menu = st.sidebar.radio(
    "Go to",
    [
        "Dashboard 📊",
        "Upload Files 📂",
        "View Designs 👁️",
        "Manage Files 🔧",
        "Settings ⚙️",
        "Help / FAQ ❓",
        "User Feedback 💬",
        "File Analytics 📈",
        "Export Data 📤",
        "About ℹ️"
    ]
)

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

def filter_files_by_category(category):
    """Filter files by category."""
    if category == "All":
        return st.session_state.file_list
    return [file for file in st.session_state.file_list if parse_category_from_file(file) == category]

def delete_single_file(file_name):
    """Delete a single file and its associated comments."""
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
    refresh_file_list()

def delete_all_files():
    """Delete all files and associated comments."""
    for file in os.listdir(UPLOAD_FOLDER):
        delete_single_file(file)
    refresh_file_list()

# Dashboard
if menu == "Dashboard 📊":
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

# File Upload Module
elif menu == "Upload Files 📂":
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

# View Designs
elif menu == "View Designs 👁️":
    st.header("👁️ View Uploaded Files")
    selected_category = st.selectbox("Choose Category", CATEGORIES)

    files = filter_files_by_category(selected_category)

    if files:
        for file in files:
            st.subheader(file)
            file_path = os.path.join(UPLOAD_FOLDER, file)
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download File",
                    data=f,
                    file_name=file,
                    mime="application/octet-stream"
                )
    else:
        st.info(f"No files found in {selected_category} category.")

# Manage Files
elif menu == "Manage Files 🔧":
    st.header("🔧 Manage Uploaded Files")
    selected_category = st.selectbox("Filter by Category", CATEGORIES)

    files = filter_files_by_category(selected_category)

    if files:
        selected_file = st.selectbox("Select a file to manage", files)

        if selected_file:
            st.write(f"Managing: {selected_file}")
            # Delete Single File
            if st.button("Delete File"):
                delete_single_file(selected_file)
                st.success("File deleted successfully!")
    else:
        st.info(f"No files available to manage in {selected_category} category.")

# Help / FAQ
elif menu == "Help / FAQ ❓":
    st.header("❓ Help / FAQ")
    st.write("Here you can find answers to frequently asked questions about using this app.")

# User Feedback
elif menu == "User Feedback 💬":
    st.header("💬 User Feedback")
    feedback = st.text_area("Share your feedback or report an issue:")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")

# File Analytics
elif menu == "File Analytics 📈":
    st.header("📈 File Analytics")
    st.write("Coming soon: Visual insights into uploaded file trends!")

# Export Data
elif menu == "Export Data 📤":
    st.header("📤 Export Data")
    if st.button("Export File List as CSV"):
        files = st.session_state.file_list
        df = pd.DataFrame([
            {"File Name": file, "Category": parse_category_from_file(file)}
            for file in files
        ])
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download CSV", data=csv, file_name="file_list.csv", mime="text/csv")
