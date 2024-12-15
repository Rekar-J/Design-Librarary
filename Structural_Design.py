import os
import streamlit as st
import pandas as pd
import datetime

# Configurable Settings
APP_NAME = "🏗️ Structural Design Library"
MAIN_IMAGE = "main_image.jpg"  # Path to your main image
DATABASE_FILE = "database.csv"  # Database file for storing file metadata
UPLOAD_FOLDER = "uploaded_files"

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

# View Designs
elif menu == "View Designs 👁️":
    st.header("👁️ View Uploaded Files")
    selected_category = st.selectbox("Choose Category", CATEGORIES)
    db = filter_files_by_category(selected_category)

    if not db.empty:
        for i, row in db.iterrows():
            st.subheader(row["File Name"])
            file_path = os.path.join(UPLOAD_FOLDER, row["File Name"])
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download File",
                    data=f,
                    file_name=row["File Name"],
                    mime="application/octet-stream",
                    key=f"download_{i}"  # Unique key for each button
                )
    else:
        st.info(f"No files found in {selected_category} category.")

# Manage Files
elif menu == "Manage Files 🔧":
    st.header("🔧 Manage Uploaded Files")
    selected_category = st.selectbox("Filter by Category", CATEGORIES)
    db = filter_files_by_category(selected_category)

    if not db.empty:
        selected_file = st.selectbox("Select a file to manage", db["File Name"])

        if selected_file:
            # Delete Single File
            if st.button("Delete File"):
                file_path = os.path.join(UPLOAD_FOLDER, selected_file)
                if os.path.exists(file_path):
                    os.remove(file_path)
                delete_from_database(selected_file)
                st.success("File deleted successfully!")
        # Delete All Files
        if st.button("Delete All Files"):
            for file_name in db["File Name"]:
                file_path = os.path.join(UPLOAD_FOLDER, file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
            delete_all_from_database()
            st.success("All files deleted successfully!")
    else:
        st.info(f"No files available to manage in {selected_category} category.")

# Settings
elif menu == "Settings ⚙️":
    st.header("⚙️ Settings")
    uploaded_main_image = st.file_uploader("Upload a new main image (jpg/png):", type=["jpg", "png"])
    if st.button("Update Main Image"):
        if uploaded_main_image:
            with open(MAIN_IMAGE, "wb") as f:
                f.write(uploaded_main_image.getbuffer())
            st.success("Main image updated!")
            load_main_image()

# User Feedback
elif menu == "User Feedback 💬":
    st.header("💬 User Feedback")
    st.text_area("Share your feedback", placeholder="Write your feedback here...")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")

# File Analytics
elif menu == "File Analytics 📈":
    st.header("📈 File Analytics")
    db = load_database()
    st.bar_chart(db["Category"].value_counts())

# About
elif menu == "About ℹ️":
    st.header("ℹ️ About This App")
    st.markdown("""
        This app is designed for civil engineers and designers to manage their structural design files.
        You can upload, download, and categorize your files easily. Enjoy!
    """)

# Export Data
elif menu == "Export Data 📤":
    st.header("📤 Export Data")
    db = load_database()  # Load the database.csv in the app
    st.write("Current Database Content:")
    st.dataframe(db)  # Display the current database content
