import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="🏗️ Structural Design Library",
    layout="wide",
    menu_items={
        'Get Help': 'mailto:civil.eng2019s@gmail.com',
        'Report a bug': 'mailto:civil.eng2019s@gmail.com',
        'About': "🏗️ Structural Design Library - Manage your structural design files efficiently."
    }
)

# Other imports
import os
import pandas as pd
import datetime
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
    st.error("Matplotlib is not installed. Please ensure it is added to requirements.txt.")

from PIL import Image

# Configurable settings
MAIN_IMAGE = "main_image.jpg"
DATABASE_FILE = "database.csv"
UPLOAD_FOLDER = "uploaded_files"
LOG_FILE = "activity_log.csv"

# Ensure directories and files exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(DATABASE_FILE):
    pd.DataFrame(columns=["File Name", "Category", "Upload Date"]).to_csv(DATABASE_FILE, index=False)
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Action", "File Name", "Category", "Timestamp"]).to_csv(LOG_FILE, index=False)

CATEGORIES = ["All", "2D Plans", "3D Plans", "Other"]

# Helper functions and the rest of your code...
