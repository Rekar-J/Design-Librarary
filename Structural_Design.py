import os
import streamlit as st
import ezdxf
import pyvista as pv
from pyvista import Plotter
import shutil

# App Title
st.set_page_config(page_title="Structural Design Library", layout="wide")
st.title("🏗️ Structural Design Library")
st.sidebar.title("Navigation")

# Create necessary directories
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Sidebar Navigation
menu = st.sidebar.radio("Go to", ["Upload Files", "View Designs", "Compare Files", "About"])

# File Upload Module
if menu == "Upload Files":
    st.header("📂 Upload and Manage Files")
    uploaded_files = st.file_uploader("Upload your design files (.dwg, .dxf, .skp, .stl)", 
                                      accept_multiple_files=True)

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

# File Viewer Module
elif menu == "View Designs":
    st.header("👁️ View Designs")
    files = os.listdir(UPLOAD_FOLDER)

    if files:
        selected_file = st.selectbox("Select a file to view", files)
        file_path = os.path.join(UPLOAD_FOLDER, selected_file)

        if selected_file.endswith(".dxf") or selected_file.endswith(".dwg"):
            st.subheader(f"Viewing 2D Design: {selected_file}")
            doc = ezdxf.readfile(file_path)
            msp = doc.modelspace()
            st.write(f"Layers: {[layer.dxf.name for layer in doc.layers]}")

        elif selected_file.endswith(".stl"):
            st.subheader(f"Viewing 3D Design: {selected_file}")
            mesh = pv.read(file_path)
            plotter = Plotter()
            plotter.add_mesh(mesh, show_edges=True)
            plotter.show(auto_close=False)
        else:
            st.error("File format not supported for viewing.")
    else:
        st.info("No files available to view.")

# File Comparison Module
elif menu == "Compare Files":
    st.header("🔍 Compare Files")
    files = os.listdir(UPLOAD_FOLDER)

    if len(files) >= 2:
        file1 = st.selectbox("Select the first file", files)
        file2 = st.selectbox("Select the second file", files)

        if file1 and file2 and file1 != file2:
            st.subheader(f"Comparing: {file1} vs {file2}")
            st.write("Comparison features coming soon...")
        else:
            st.warning("Please select two different files to compare.")
    else:
        st.info("Not enough files to compare. Upload at least two files.")

# About Section
elif menu == "About":
    st.header("ℹ️ About This App")
    st.write("""
        **Structural Design Library** is a web app for civil engineers and architects to:
        - Upload and manage design files.
        - View 2D and 3D structural designs.
        - Compare design versions for changes and improvements.
        
        Developed using Streamlit.
    """)

# Footer
st.sidebar.info("Developed by a passionate Civil Engineer.")
