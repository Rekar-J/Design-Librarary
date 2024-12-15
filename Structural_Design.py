import os
import streamlit as st
import pandas as pd
import datetime

# Try importing matplotlib, catch ImportError
try:
    import matplotlib.pyplot as plt
except ImportError:
    st.error("Matplotlib is not installed. Please ensure it is added to requirements.txt.")
    plt = None

from PIL import Image

# Configurable Settings
APP_NAME = "🏗️ Structural Design Library"
MAIN_IMAGE = "main_image.jpg"  # Path to your main image
DATABASE_FILE = "database.csv"  # Database file for storing file metadata
UPLOAD_FOLDER = "uploaded_files"
LOG_FILE = "activity_log.csv"

# App Configuration
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    menu_items={
        'Get Help': 'mailto:civil.eng2019s@gmail.com',
        'Report a bug': 'mailto:civil.eng2019s@gmail.com',
        'About': f"{APP_NAME} - Manage your structural design files efficiently."
    }
)

# Ensure directories and files exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(DATABASE_FILE):
    pd.DataFrame(columns=["File Name", "Category", "Upload Date"]).to_csv(DATABASE_FILE, index=False)
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Action", "File Name", "Category", "Timestamp"]).to_csv(LOG_FILE, index=False)

CATEGORIES = ["All", "2D Plans", "3D Plans", "Other"]

# Helper Functions
def load_main_image():
    if os.path.exists(MAIN_IMAGE):
        st.image(MAIN_IMAGE, use_container_width=True, caption="Welcome to the Structural Design Library!")
    else:
        st.warning("Main image not found. Please upload a valid image in the Settings section.")

def load_database():
    return pd.read_csv(DATABASE_FILE)

def log_action(action, file_name, category):
    log_entry = pd.DataFrame([{
        "Action": action,
        "File Name": file_name,
        "Category": category,
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    log = pd.read_csv(LOG_FILE)
    log = pd.concat([log, log_entry], ignore_index=True)
    log.to_csv(LOG_FILE, index=False)

def save_to_database(file_name, category):
    db = load_database()
    if not ((db["File Name"] == file_name) & (db["Category"] == category)).any():
        new_entry = pd.DataFrame([{
            "File Name": file_name,
            "Category": category,
            "Upload Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        db = pd.concat([db, new_entry], ignore_index=True)
        db.to_csv(DATABASE_FILE, index=False)
        log_action("Uploaded", file_name, category)

def delete_from_database(file_name):
    db = load_database()
    db = db[db["File Name"] != file_name]
    db.to_csv(DATABASE_FILE, index=False)
    log_action("Deleted", file_name, "")

def filter_files_by_category(category):
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
        "Help / FAQ ❓",
        "User Feedback 💬",
        "Activity Log 📜",
        "About ℹ️"
    ]
)

# Dashboard
if menu == "Dashboard 📊":
    st.header("📊 Dashboard")
    load_main_image()
    db = load_database()

    if plt:
        # File Statistics Pie Chart
        st.subheader("File Category Distribution")
        fig, ax = plt.subplots()
        category_counts = db["Category"].value_counts()
        ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=90)
        ax.set_title("File Category Distribution")
        st.pyplot(fig)

    # Recent Uploads as Cards
    st.subheader("Recent Uploads")
    for _, row in db.sort_values("Upload Date", ascending=False).head(5).iterrows():
        st.markdown(f"""
        **{row['File Name']}**
        - Category: {row['Category']}
        - Uploaded On: {row['Upload Date']}
        """)

# Upload Files
elif menu == "Upload Files 📂":
    st.header("📂 Upload and Manage Files")
    uploaded_files = st.file_uploader(
        "Upload your design files (.pdf, .txt, .jpg, .png, .dwg, .skp)", 
        accept_multiple_files=True
    )
    category = st.selectbox("Select File Category", CATEGORIES[1:])
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
        st.dataframe(db)
        search_query = st.text_input("Search Files")
        if search_query:
            db = db[db["File Name"].str.contains(search_query, case=False)]
            st.dataframe(db)
    else:
        st.info("No files found.")

# Manage Files
elif menu == "Manage Files 🔧":
    st.header("🔧 Manage Files")
    selected_category = st.selectbox("Filter by Category", CATEGORIES)
    db = filter_files_by_category(selected_category)
    if not db.empty:
        selected_file = st.selectbox("Select a File", db["File Name"])
        if st.button("Delete File"):
            file_path = os.path.join(UPLOAD_FOLDER, selected_file)
            if os.path.exists(file_path):
                os.remove(file_path)
            delete_from_database(selected_file)
            st.success(f"{selected_file} deleted.")
    else:
        st.info("No files to manage.")

# Help / FAQ
elif menu == "Help / FAQ ❓":
    st.header("Help / FAQ")
    st.write("Email your queries to: **civil.eng2019s@gmail.com**")

# User Feedback
elif menu == "User Feedback 💬":
    st.header("User Feedback")
    feedback_name = st.text_input("Your Name")
    feedback_email = st.text_input("Your Email")
    feedback_message = st.text_area("Your Feedback")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")
