import os
import streamlit as st
import shutil

# App Configuration
st.set_page_config(page_title="Structural Design Library", layout="wide")
st.title("🏗️ Structural Design Library")
st.sidebar.title("Navigation")

# Create necessary directories
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Sidebar Navigation
menu = st.sidebar.radio("Go to", ["Upload Files", "View Designs", "About"])

# File Upload Module
if menu == "Upload Files":
    st.header("📂 Upload and Manage Files")
    uploaded_files = st.file_uploader(
        "Upload your design files (.txt, .pdf for testing)", accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            with open(os.path.join(UPLOAD_FOLDER, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success("Files uploaded successfully!")

    # Display Uploaded Files
    st.subheader("Uploaded Files")
    files = os.listdir(UPLOAD_FOLDER)
    if files:
        for file in files:
            st.write(file)
    else:
        st.info("No files uploaded yet.")

# Placeholder for File Viewer Module
elif menu == "View Designs":
    st.header("👁️ View Designs")
    st.write("Viewing designs will be implemented later.")

# About Section
elif menu == "About":
    st.header("ℹ️ About This App")
    st.write("""
        **Structural Design Library** is a simplified demo version to test uploads.
    """)

# Footer
st.sidebar.info("Developed by a Civil Engineer.")
