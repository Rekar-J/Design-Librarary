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
DASHBOARD_IMAGE = "dashboard_image.jpg"  # Path to the dashboard image
FEEDBACK_FILE = "feedback.json"  # File to store user feedback

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

def load_feedback():
    """Load feedback from the JSON file."""
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
    return []

def save_feedback(feedback_data):
    """Save feedback to the JSON file."""
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback_data, f, indent=4)

# Dashboard
if menu == "Dashboard 📊":
    st.header("📊 Dashboard")

    # Dashboard Image
    st.subheader("Dashboard Image")
    if os.path.exists(DASHBOARD_IMAGE):
        st.image(DASHBOARD_IMAGE, use_column_width=True)
    else:
        st.warning("Dashboard image not found. Please upload a new image.")

    uploaded_dashboard_image = st.file_uploader("Upload a new dashboard image", type=["jpg", "png"])
    if uploaded_dashboard_image:
        with open(DASHBOARD_IMAGE, "wb") as f:
            f.write(uploaded_dashboard_image.getbuffer())
        st.success("Dashboard image updated! Refresh the page to see changes.")

    # File Stats
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

# User Feedback
elif menu == "User Feedback 💬":
    st.header("💬 User Feedback")
    feedback = st.text_area("Share your feedback or report an issue:")
    if st.button("Submit Feedback"):
        feedback_data = load_feedback()
        feedback_data.append({
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "feedback": feedback
        })
        save_feedback(feedback_data)
        st.success("Thank you for your feedback!")

    st.subheader("Feedback Received")
    feedback_data = load_feedback()
    if feedback_data:
        for item in feedback_data:
            st.markdown(f"**{item['timestamp']}**: {item['feedback']}")
            st.markdown("---")
    else:
        st.info("No feedback received yet.")

# Export Data
elif menu == "Export Data 📤":
    st.header("📤 Export Data")
    selected_category = st.selectbox("Filter files by category for export", CATEGORIES)

    files_to_export = filter_files_by_category(selected_category)
    if files_to_export:
        df = pd.DataFrame([
            {"File Name": file, "Category": parse_category_from_file(file)}
            for file in files_to_export
        ])
        st.write("Preview of data to be exported:")
        st.table(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download CSV", data=csv, file_name="file_list.csv", mime="text/csv")
    else:
        st.info(f"No files available in the selected category ({selected_category}).")

# Footer
st.sidebar.info("The app created by Eng. Rekar J.")
