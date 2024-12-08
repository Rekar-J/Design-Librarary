import os
import streamlit as st
from PIL import Image
import base64
import datetime

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
menu = st.sidebar.radio("Go to", ["Dashboard", "Upload Files", "View Designs", "Settings", "About"])

# Create necessary directories
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper Functions
def get_file_stats():
    """Return total files and breakdown by category."""
    files = os.listdir(UPLOAD_FOLDER)
    stats = {"total": len(files), "categories": {}}
    for file in files:
        ext = file.split(".")[-1].lower()
        stats["categories"][ext] = stats["categories"].get(ext, 0) + 1
    return stats

def display_file_preview(file_path, file_type):
    """Render preview for supported file types."""
    if file_type == "pdf":
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        st.info("If the PDF does not load, use the download button below.")
    elif file_type == "txt":
        with open(file_path, "r") as f:
            content = f.read()
        st.text_area("Text File Content", content, height=300)
    elif file_type in ["jpg", "png"]:
        image = Image.open(file_path)
        st.image(image, caption=os.path.basename(file_path))
    else:
        st.info("File preview not supported. You can download the file below.")

# Dashboard
if menu == "Dashboard":
    st.header("📊 Dashboard")
    stats = get_file_stats()
    st.subheader(f"Total Files: {stats['total']}")
    st.write("File Breakdown by Category:")
    for category, count in stats["categories"].items():
        st.write(f"- **{category.upper()}**: {count}")
    st.write("Recent Uploads:")
    recent_files = sorted(os.listdir(UPLOAD_FOLDER), key=lambda x: os.path.getctime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
    for file in recent_files[:5]:
        st.write(f"- {file} (Uploaded on {datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(UPLOAD_FOLDER, file))).strftime('%Y-%m-%d %H:%M:%S')})")

# File Upload Module
elif menu == "Upload Files":
    st.header("📂 Upload and Manage Files")
    uploaded_files = st.file_uploader(
        "Upload your design files (.pdf, .txt, .jpg, .png, .dwg, .skp)", 
        accept_multiple_files=True
    )
    category = st.selectbox("Select File Category", ["PDF", "Image", "Drawing", "Other"])

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(UPLOAD_FOLDER, f"{category}_{uploaded_file.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success("Files uploaded successfully!")

# File Viewing Module
elif menu == "View Designs":
    st.header("👁️ View Uploaded Files")
    files = os.listdir(UPLOAD_FOLDER)

    if files:
        search_query = st.text_input("Search Files")
        filtered_files = [file for file in files if search_query.lower() in file.lower()]

        file_category = st.selectbox("Filter by Category", ["All", "PDF", "Image", "Drawing", "Other"])
        if file_category != "All":
            filtered_files = [file for file in filtered_files if file.startswith(file_category)]

        selected_file = st.selectbox("Select a file to view", filtered_files)

        if selected_file:
            file_path = os.path.join(UPLOAD_FOLDER, selected_file)
            file_ext = selected_file.split(".")[-1].lower()
            if file_ext == "pdf":
                display_file_preview(file_path, "pdf")
            elif file_ext == "txt":
                display_file_preview(file_path, "txt")
            elif file_ext in ["jpg", "png"]:
                display_file_preview(file_path, file_ext)
            else:
                st.download_button(label="Download File", data=open(file_path, "rb"), file_name=selected_file)
    else:
        st.info("No files available to view.")

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
        - View files (e.g., PDFs, text files, images).
        - Categorize files for better organization.
        - Search and filter uploaded files.
        - View a dashboard of file stats and recent uploads.
    """)

# Footer
st.sidebar.info("Developed by a Civil Engineer.")
