import os
import streamlit as st
import pandas as pd
import datetime
import requests
import base64

# Configurable Settings
APP_NAME = "\ud83c\udff0 Structural Design Library"
MAIN_IMAGE = "main_image.jpg"  # Path to your main image
GITHUB_REPO = "hawkarabdulhaq/Design-Librarary"  # Replace with your GitHub repo
DATABASE_FILE = "database.csv"  # Database file in the GitHub repo
UPLOAD_FOLDER = "uploaded_files"
GITHUB_BRANCH = "main"  # Branch name for pushing data

# Load GitHub Token from Streamlit secrets
github_token = st.secrets["GITHUB_TOKEN"]

# GitHub API Headers
headers = {
    "Authorization": f"Bearer {github_token}",
    "Accept": "application/vnd.github+json"
}

# App Configuration
st.set_page_config(page_title=APP_NAME, layout="wide")
st.title(APP_NAME)

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CATEGORIES = ["All", "2D Plans", "3D Plans", "Other"]

# Helper Functions
def load_main_image():
    """Load and display the main image."""
    if os.path.exists(MAIN_IMAGE):
        st.image(MAIN_IMAGE, use_container_width=True, caption="Welcome to the Structural Design Library!")
    else:
        st.warning("Main image not found. Please upload a valid image in the Settings section.")

def fetch_file_from_github(file_path):
    """Fetch a file from the GitHub repository."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def save_to_github(file_name, content, message):
    """Save or update a file in the GitHub repository."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_name}"
    existing_file = fetch_file_from_github(file_name)
    
    data = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": GITHUB_BRANCH,
    }
    
    if existing_file:
        data["sha"] = existing_file["sha"]

    response = requests.put(url, headers=headers, json=data)
    return response.status_code == 201 or response.status_code == 200

def load_database():
    """Load the database file from GitHub."""
    file_data = fetch_file_from_github(DATABASE_FILE)
    if file_data:
        content = base64.b64decode(file_data["content"]).decode()
        return pd.read_csv(pd.compat.StringIO(content))
    else:
        return pd.DataFrame(columns=["File Name", "Category", "Upload Date"])

def save_to_database(file_name, category):
    """Save a new entry to the database on GitHub."""
    db = load_database()
    if not ((db["File Name"] == file_name) & (db["Category"] == category)).any():
        new_entry = pd.DataFrame([{
            "File Name": file_name,
            "Category": category,
            "Upload Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        db = pd.concat([db, new_entry], ignore_index=True)
        csv_content = db.to_csv(index=False)
        if save_to_github(DATABASE_FILE, csv_content, "Update database with new upload"):
            st.success("Database updated successfully!")
        else:
            st.error("Failed to update database on GitHub.")

# Sidebar Navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Go to",
    [
        "Dashboard \ud83d\udcca",
        "Upload Files \ud83d\udcc2",
        "View Designs \ud83d\udd41\ufe0f",
        "Settings \u2699\ufe0f",
    ]
)

# Dashboard
if menu == "Dashboard \ud83d\udcca":
    st.header("\ud83d\udcca Dashboard")
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
elif menu == "Upload Files \ud83d\udcc2":
    st.header("\ud83d\udcc2 Upload and Manage Files")
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

# View Designs
elif menu == "View Designs \ud83d\udd41\ufe0f":
    st.header("\ud83d\udd41\ufe0f View Uploaded Files")
    selected_category = st.selectbox("Choose Category", CATEGORIES)
    db = load_database()

    if not db.empty:
        filtered_db = db if selected_category == "All" else db[db["Category"] == selected_category]
        for _, row in filtered_db.iterrows():
            st.subheader(row["File Name"])
            st.write(f"Category: {row['Category']}")
            st.write(f"Uploaded On: {row['Upload Date']}")
    else:
        st.info(f"No files found in {selected_category} category.")

# Settings
elif menu == "Settings \u2699\ufe0f":
    st.header("\u2699\ufe0f Settings")
    uploaded_main_image = st.file_uploader("Upload a new main image (jpg/png):", type=["jpg", "png"])
    if st.button("Update Main Image"):
        if uploaded_main_image:
            with open(MAIN_IMAGE, "wb") as f:
                f.write(uploaded_main_image.getbuffer())
            st.success("Main image updated!")
            load_main_image()
