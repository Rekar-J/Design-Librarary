import os
import streamlit as st
import pandas as pd
import datetime
from github import Github  # For GitHub API integration

# Configurable Settings
APP_NAME = "🏗️ Structural Design Library"
MAIN_IMAGE = "main_image.jpg"  # Path to your main image
DATABASE_FILE = "database.csv"  # Database file for storing file metadata
UPLOAD_FOLDER = "uploaded_files"
GITHUB_REPO = "Rekar-J/Design-Librarary"  # Replace with your repository name

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
    db = pd.read_csv(DATABASE_FILE)
    db["Upload Date"] = pd.to_datetime(db["Upload Date"], errors='coerce').dt.date  # Format Upload Date
    return db

def save_to_database(file_name, category):
    """Save a new entry to the database without duplications."""
    db = load_database()
    if not ((db["File Name"] == file_name) & (db["Category"] == category)).any():
        new_entry = pd.DataFrame([{
            "File Name": file_name,
            "Category": category,
            "Upload Date": datetime.date.today()
        }])
        db = pd.concat([db, new_entry], ignore_index=True)
        db.to_csv(DATABASE_FILE, index=False)

def delete_from_database(file_name):
    """Delete an entry from the database."""
    db = load_database()
    db = db[db["File Name"] != file_name]
    db.to_csv(DATABASE_FILE, index=False)

def delete_all_from_database():
    """Clear all entries from the database."""
    pd.DataFrame(columns=["File Name", "Category", "Upload Date"]).to_csv(DATABASE_FILE, index=False)

def filter_files_by_category(category):
    """Filter files by category."""
    db = load_database()
    if category == "All":
        return db
    return db[db["Category"] == category]

def update_github_database():
    """
    Push the updated database.csv to GitHub.
    """
    github_token = st.secrets["GITHUB_TOKEN"]  # Load GitHub token from Streamlit secrets
    if not github_token:
        st.error("GitHub token is missing. Please set the GITHUB_TOKEN in Streamlit secrets.")
        return

    try:
        # Authenticate with GitHub
        g = Github(github_token)
        repo = g.get_repo(GITHUB_REPO)

        # Read the updated database.csv content
        with open(DATABASE_FILE, "r") as f:
            content = f.read()

        # Check if the file exists in the repository
        try:
            file = repo.get_contents(DATABASE_FILE)
            repo.update_file(
                path=file.path,
                message="Updated database.csv via Streamlit app",
                content=content,
                sha=file.sha,
            )
            st.success("Database successfully updated on GitHub!")
        except Exception:
            # If the file doesn't exist, create it
            repo.create_file(
                path=DATABASE_FILE,
                message="Created database.csv via Streamlit app",
                content=content,
            )
            st.success("Database created and uploaded to GitHub!")
    except Exception as e:
        st.error(f"Failed to update GitHub: {e}")

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
        "User Feedback 💬",
        "File Analytics 📈",
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
    if not db.empty:
        db = db.sort_values("Upload Date", ascending=False).reset_index(drop=True)  # Sort and reset index
        db["No."] = range(1, len(db) + 1)  # Add sequential numbering
        db_display = db[["No.", "File Name", "Category", "Upload Date"]]  # Select relevant columns
        st.table(db_display)  # Use st.table() for clean display
    else:
        st.info("No files uploaded yet.")

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

        # Push database.csv to GitHub
        update_github_database()
