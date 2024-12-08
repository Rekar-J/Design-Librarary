import os
import streamlit as st
import shutil
from PIL import Image
import base64

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
        "Upload your design files (.pdf, .txt, .dwg, .skp)", accept_multiple_files=True
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

# File Viewing Module
elif menu == "View Designs":
    st.header("👁️ View Uploaded Files")
    files = os.listdir(UPLOAD_FOLDER)

    if files:
        selected_file = st.selectbox("Select a file to view", files)
        file_path = os.path.join(UPLOAD_FOLDER, selected_file)

        # File Viewing
        if selected_file.endswith(".pdf"):
            with open(file_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

        elif selected_file.endswith(".txt"):
            with open(file_path, "r") as f:
                content = f.read()
            st.text_area("Text File Content", content, height=300)

        elif selected_file.endswith(".jpg") or selected_file.endswith(".png"):
            image = Image.open(file_path)
            st.image(image, caption=selected_file)

        elif selected_file.endswith(".dwg") or selected_file.endswith(".skp"):
            st.info(f"File format `{selected_file.split('.')[-1]}` is not supported for viewing yet.")
            st.download_button(label="Download File", data=open(file_path, "rb"), file_name=selected_file)

        else:
            st.warning("Unsupported file format. Download the file to view it.")
            st.download_button(label="Download File", data=open(file_path, "rb"), file_name=selected_file)

    else:
        st.info("No files available to view.")

# About Section
elif menu == "About":
    st.header("ℹ️ About This App")
    st.write("""
        **Structural Design Library** is a web app for civil engineers and architects to:
        - Upload and manage design files.
        - View files (e.g., PDFs, text files, images).
        - Provide download links for unsupported formats.
    """)

# Footer
st.sidebar.info("Developed by a Civil Engineer.")
