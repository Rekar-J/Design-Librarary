import os
import streamlit as st
import pandas as pd
import datetime
import subprocess

# Configurable Settings
APP_NAME = "🏗️ Structural Design Library"
MAIN_IMAGE = "main_image.jpg"  # Path to your main image
DATABASE_FILE = "database.csv"  # Database file for storing file metadata
UPLOAD_FOLDER = "uploaded_files"

# GitHub Configuration
GITHUB_TOKEN = st.secrets["github"]["token"]
GITHUB_REPO = "your_username/your_repo_name"  # Replace with your GitHub repo details
GITHUB_URL = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"

# App Configuration
st.set_page_config(page_title=APP_NAME, layout="wide")
st.title(APP_NAME)

# Ensure directories and files exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(DATABASE_FILE):
    # Create the database.csv file with the appropriate structure
    pd.DataFrame(columns=["File Name", "Category", "Upload Date"]).to_csv(DATABASE_FILE, index=False)

CATEGORIES = ["All", "2D Plans", "3D Plans", "Other"]

# Helper Functions
def load_main_image():
    """Load and display the main image."""
    if os.path.exists(MAIN_IMAGE):
        st.image(MAIN_IMAGE, use_container_width=True, caption="Welcome to the Structural Design Library!")
    else:
        st.warning("Main image not found. Please upload a valid image in the Settings section.")

def load_database():
    """Load the database file as a DataFrame."""
    return pd.read_csv(DATABASE_FILE)

def save_to_database(file_name, category):
    """Save a new entry to the database without duplications."""
    db = load_database()
    if not ((db["File Name"] == file_name) & (db["Category"] == category)).any():
        new_entry = pd.DataFrame([{
            "File Name": file_name,
            "Category": category,
            "Upload Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        db = pd.concat([db, new_entry], ignore_index=True)
        db.to_csv(DATABASE_FILE, index=False)

def update_github():
    """Commit and push the updated database.csv to GitHub."""
    try:
        # Set the GitHub remote URL with authentication
        subprocess.run(["git", "remote", "set-url", "origin", GITHUB_URL], check=True)

        # Stage the database.csv file
        subprocess.run(["git", "add", "database.csv"], check=True)

        # Check for changes before committing
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
        if not status.strip():
            st.info("No changes detected in database.csv. Skipping commit.")
            return

        # Commit and push the changes
        subprocess.run(["git", "commit", "-m", "Update database.csv"], check=True)
        subprocess.run(["git", "push"], check=True)

        st.success("database.csv updated on GitHub successfully!")
    except subprocess.CalledProcessError as e:
        st.error(f"Error updating GitHub: {e}")

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
        "Export Data 📤",
        "About ℹ️"
    ]
)

# Dashboard
if menu == "Dashboard 📊":
    st.header("📊 Dashboard")
    load_main_image()
    db = load_database()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Files", len(db))
    with col2:
        st.metric("2D Plans", len(db[db["Category"] == "2D Plans"]))
    with col3:
        st.metric("3D Plans", len(db[db["Category"] == "3D Plans"]))
    with col4:
        st.metric("Other", len(db[db["Category"] == "Other"]))

    st.subheader("Recent Uploads")
    st.dataframe(db.sort_values("Upload Date", ascending=False))

# Upload Files
elif menu == "Upload Files 📂":
    st.header("📂 Upload and Manage Files")
    uploaded_files = st.file_uploader(
        "Upload your design files (.pdf, .txt, .jpg, .png, .dwg, .skp)", 
        accept_multiple_files=True
    )
    category = st.selectbox("Select File Category", CATEGORIES[1:])  # Exclude "All" for uploads

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            save_to_database(uploaded_file.name, category)
        st.success("Files uploaded successfully!")

        # Push changes to GitHub
        update_github()
