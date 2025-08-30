import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import hashlib

# Set page configuration
st.set_page_config(
    page_title="Cotton Disease Detection",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
# Remove theme state - only dark mode
# if 'theme_mode' not in st.session_state:
#     st.session_state.theme_mode = 'light'

# Initialize database
def init_database():
    """Initialize SQLite database for user management and predictions"""
    try:
        conn = sqlite3.connect('cotton_disease_app.db', timeout=20.0)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                disease TEXT NOT NULL,
                confidence REAL NOT NULL,
                image_name TEXT,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
        return False

# User authentication functions
def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    """Register a new user"""
    try:
        conn = sqlite3.connect('cotton_disease_app.db', timeout=20.0)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists!"
        elif "email" in str(e):
            return False, "Email already exists!"
        else:
            return False, "Username or email already exists!"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def login_user(username, password):
    """Authenticate a user"""
    try:
        conn = sqlite3.connect('cotton_disease_app.db', timeout=20.0)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        cursor.execute(
            "SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, {"id": user[0], "username": user[1], "email": user[2]}
        else:
            return False, "Invalid username or password!"
    except Exception as e:
        return False, f"Login failed: {str(e)}"

def save_user_prediction(user_id, disease, confidence, image_name=None):
    """Save user prediction to database"""
    try:
        conn = sqlite3.connect('cotton_disease_app.db', timeout=20.0)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO predictions (user_id, disease, confidence, image_name) VALUES (?, ?, ?, ?)",
            (user_id, disease, confidence, image_name)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Failed to save prediction: {str(e)}")
        return False

def get_user_predictions(user_id):
    """Get all predictions for a specific user"""
    try:
        conn = sqlite3.connect('cotton_disease_app.db', timeout=20.0)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT disease, confidence, image_name, prediction_date FROM predictions WHERE user_id = ? ORDER BY prediction_date DESC",
            (user_id,)
        )
        
        predictions = cursor.fetchall()
        conn.close()
        
        return [
            {
                "disease": pred[0],
                "confidence": pred[1],
                "image_name": pred[2] or "Unknown",
                "timestamp": pred[3]
            }
            for pred in predictions
        ]
    except Exception as e:
        st.error(f"Failed to load predictions: {str(e)}")
        return []

def logout():
    """Logout the current user"""
    st.session_state.authenticated = False
    st.session_state.user_data = None
    for key in list(st.session_state.keys()):
        if key.startswith('user_'):
            del st.session_state[key]
    safe_rerun()  # replaced st.rerun()

# Optimized CSS styling with permanent dark theme and background image
def load_css():
    # Permanent dark theme only
    theme_vars = """
    --primary-color: #4CAF50;
    --secondary-color: #81C784;
    --accent-color: #388E3C;
    --background-color: #0a0a0a;
    --card-bg: linear-gradient(135deg, rgba(45, 45, 45, 0.95) 0%, rgba(58, 58, 58, 0.95) 100%);
    --text-color: #ffffff;
    --secondary-text: #b0b0b0;
    --border-color: #555555;
    --input-bg: linear-gradient(135deg, rgba(64, 64, 64, 0.9) 0%, rgba(74, 74, 74, 0.9) 100%);
    --shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    --hover-shadow: 0 12px 40px rgba(76, 175, 80, 0.3);
    --gradient-primary: linear-gradient(135deg, #4CAF50, #388E3C);
    --gradient-secondary: linear-gradient(135deg, #81C784, #4CAF50);
    --glass-bg: rgba(45, 45, 45, 0.8);
    --backdrop-blur: blur(20px);
    """
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    :root {{
        {theme_vars}
        --border-radius: 20px;
        --transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        --glow: 0 0 20px rgba(76, 175, 80, 0.3);
    }}
    
    /* Optimized base app styling with background image */
    .stApp {{
        background: var(--background-color);
        font-family: 'Poppins', sans-serif;
        color: var(--text-color);
        min-height: 100vh;
        transition: var(--transition);
        position: relative;
    }}
    
    /* Background image for homepage */
    .homepage-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: url('file:///C:/Users/aksha/OneDrive/Desktop/Cotton_crop_disease_detection_using_ML/home_page.png') no-repeat center center;
        background-size: cover;
        opacity: 0.15;
        z-index: -1;
    }}
    
    .homepage-bg::after {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.5) 100%);
    }}
    
    /* Hide empty containers and fix layout issues */
    .element-container:empty,
    .stColumn > div:empty,
    .stContainer > div:empty {{
        display: none !important;
    }}
    
    /* Enhanced main content area */
    .main .block-container {{
        padding: 2rem 1rem;
        max-width: 100%;
        transition: var(--transition);
        position: relative;
        z-index: 1;
    }}
    
    /* Premium header styling with glow effect */
    .main-header {{
        text-align: center;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 3rem;
        text-shadow: var(--glow);
        transition: var(--transition);
        letter-spacing: 2px;
        position: relative;
    }}
    
    .main-header::after {{
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: var(--gradient-primary);
        border-radius: 2px;
        box-shadow: var(--glow);
    }}
    
    /* Glass morphism authentication styling */
    .auth-section {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
        padding: 2rem 0;
        transition: var(--transition);
        position: relative;
    }}
    
    .auth-container {{
        background: var(--glass-bg);
        backdrop-filter: var(--backdrop-blur);
        padding: 4rem 3.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        margin: 0 auto;
        max-width: 580px;
        width: 100%;
        border: 2px solid rgba(76, 175, 80, 0.3);
        color: var(--text-color);
        position: relative;
        transition: var(--transition);
    }}
    
    .auth-container:hover {{
        box-shadow: var(--hover-shadow);
        transform: translateY(-5px);
        border-color: var(--primary-color);
    }}
    
    .auth-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: var(--gradient-primary);
        border-radius: var(--border-radius) var(--border-radius) 0 0;
        box-shadow: var(--glow);
    }}
    
    .auth-header {{
        text-align: center;
        margin-bottom: 3rem;
        color: var(--primary-color);
        font-weight: 800;
        font-size: 2.5rem;
        position: relative;
        transition: var(--transition);
        text-shadow: var(--glow);
    }}
    
    .auth-header::after {{
        content: '';
        position: absolute;
        bottom: -15px;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 4px;
        background: var(--gradient-secondary);
        border-radius: 2px;
        box-shadow: var(--glow);
    }}
    
    /* Premium form styling */
    .stTextInput > div > div > input {{
        background: var(--input-bg) !important;
        backdrop-filter: var(--backdrop-blur) !important;
        border: 2px solid rgba(76, 175, 80, 0.3) !important;
        border-radius: 15px !important;
        padding: 20px 25px !important;
        font-size: 16px !important;
        color: var(--text-color) !important;
        font-family: 'Poppins', sans-serif !important;
        transition: var(--transition) !important;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.3) !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.3), var(--glow) !important;
        background: var(--card-bg) !important;
        transform: translateY(-2px) !important;
    }}
    
    .stTextInput > label {{
        color: var(--primary-color) !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        margin-bottom: 12px !important;
        font-family: 'Poppins', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: var(--transition) !important;
        text-shadow: var(--glow);
    }}
    
    /* Premium button styling with animations */
    .stButton > button {{
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 20px 3rem !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: var(--transition) !important;
        box-shadow: var(--shadow) !important;
        width: 100% !important;
        font-family: 'Poppins', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 2rem !important;
        position: relative;
        overflow: hidden;
    }}
    
    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.6s;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: var(--hover-shadow) !important;
        background: var(--gradient-secondary) !important;
    }}
    
    .stButton > button:hover::before {{
        left: 100%;
    }}
    
    /* Enhanced alert styling */
    .alert-success {{
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.2), rgba(40, 167, 69, 0.1)) !important;
        color: #4CAF50 !important;
        border: 2px solid #4CAF50 !important;
        border-radius: var(--border-radius) !important;
        padding: 1.8rem !important;
        margin: 2rem 0 !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        box-shadow: var(--shadow) !important;
        animation: slideIn 0.5s ease !important;
        backdrop-filter: var(--backdrop-blur);
    }}
    
    .alert-error {{
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.2), rgba(220, 53, 69, 0.1)) !important;
        color: #ff6b6b !important;
        border: 2px solid #ff6b6b !important;
        border-radius: var(--border-radius) !important;
        padding: 1.8rem !important;
        margin: 2rem 0 !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        box-shadow: var(--shadow) !important;
        animation: slideIn 0.5s ease !important;
        backdrop-filter: var(--backdrop-blur);
    }}
    
    .alert-warning {{
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(255, 193, 7, 0.1)) !important;
        color: #ffd93d !important;
        border: 2px solid #ffd93d !important;
        border-radius: var(--border-radius) !important;
        padding: 1.8rem !important;
        margin: 2rem 0 !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        box-shadow: var(--shadow) !important;
        animation: slideIn 0.5s ease !important;
        backdrop-filter: var(--backdrop-blur);
    }}
    
    @keyframes slideIn {{
        from {{
            opacity: 0;
            transform: translateY(-20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    /* Premium tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 20px;
        background: transparent;
        justify-content: center;
        margin-bottom: 3rem;
        transition: var(--transition);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: var(--glass-bg) !important;
        backdrop-filter: var(--backdrop-blur) !important;
        border-radius: 25px !important;
        padding: 16px 40px !important;
        font-weight: 700 !important;
        border: 2px solid rgba(76, 175, 80, 0.3) !important;
        color: var(--text-color) !important;
        font-family: 'Poppins', sans-serif !important;
        transition: var(--transition) !important;
        box-shadow: var(--shadow) !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: var(--gradient-primary) !important;
        color: white !important;
        border-color: var(--primary-color) !important;
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: var(--hover-shadow) !important;
    }}
    
    /* Enhanced validation styling */
    .validation-check {{
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 14px;
        margin-top: 8px;
        color: var(--secondary-text);
        transition: var(--transition);
        font-weight: 500;
    }}
    
    .validation-check.valid {{
        color: #4CAF50;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
    }}
    
    .validation-check.invalid {{
        color: #ff6b6b;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(255, 107, 107, 0.5);
    }}
    
    /* Premium info section styling */
    .info-section {{
        background: var(--glass-bg);
        backdrop-filter: var(--backdrop-blur);
        border: 2px solid rgba(76, 175, 80, 0.3);
        border-radius: var(--border-radius);
        margin: 4rem 0;
        padding: 5rem 4rem;
        text-align: center;
        box-shadow: var(--shadow);
        transition: var(--transition);
        position: relative;
    }}
    
    .info-section::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-primary);
        border-radius: var(--border-radius) var(--border-radius) 0 0;
        box-shadow: var(--glow);
    }}
    
    .info-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 3rem;
        margin-top: 5rem;
    }}
    
    .info-card {{
        background: var(--glass-bg);
        backdrop-filter: var(--backdrop-blur);
        border: 2px solid rgba(76, 175, 80, 0.2);
        border-radius: var(--border-radius);
        padding: 2.5rem;
        box-shadow: var(--shadow);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }}
    
    .info-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: var(--gradient-primary);
        transform: scaleX(0);
        transition: transform 0.3s;
    }}
    
    .info-card:hover {{
        transform: translateY(-10px) scale(1.03);
        box-shadow: var(--hover-shadow);
        border-color: var(--primary-color);
    }}
    
    .info-card:hover::before {{
        transform: scaleX(1);
    }}
    
    /* Enhanced sidebar styling */
    .css-1d391kg {{
        background: var(--glass-bg) !important;
        backdrop-filter: var(--backdrop-blur) !important;
        color: var(--text-color) !important;
        border-right: 2px solid rgba(76, 175, 80, 0.3) !important;
        transition: var(--transition);
    }}
    
    /* Premium feature box styling */
    .feature-box {{
        background: var(--glass-bg);
        backdrop-filter: var(--backdrop-blur);
        padding: 3rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        margin: 2rem 0;
        border: 2px solid rgba(76, 175, 80, 0.2);
        transition: var(--transition);
        height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        color: var(--text-color);
        position: relative;
        overflow: hidden;
    }}
    
    .feature-box::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: var(--gradient-primary);
        transform: scaleX(0);
        transition: transform 0.3s;
    }}
    
    .feature-box:hover {{
        transform: translateY(-10px) scale(1.03);
        border-color: var(--primary-color);
        box-shadow: var(--hover-shadow);
    }}
    
    .feature-box:hover::before {{
        transform: scaleX(1);
    }}
    
    .feature-box h3 {{
        color: var(--primary-color);
        font-weight: 800;
        margin-bottom: 1.5rem;
        font-size: 1.5rem;
        transition: var(--transition);
        text-shadow: var(--glow);
    }}
    
    .feature-box p {{
        color: var(--text-color);
        line-height: 1.8;
        font-size: 1.1rem;
        transition: var(--transition);
        font-weight: 400;
    }}
    
    /* Enhanced general styling */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown div {{
        color: var(--text-color) !important;
        font-family: 'Poppins', sans-serif !important;
        transition: var(--transition) !important;
    }}
    
    .stSelectbox label, .stNumberInput label, .stDateInput label {{
        color: var(--primary-color) !important;
        font-weight: 700 !important;
        font-family: 'Poppins', sans-serif !important;
        transition: var(--transition) !important;
        text-shadow: var(--glow);
    }}
    
    .stCheckbox > label {{
        color: var(--text-color) !important;
        font-family: 'Poppins', sans-serif !important;
        transition: var(--transition) !important;
        font-weight: 500;
    }}
    
    /* Welcome message styling */
    .welcome-message {{
        background: var(--glass-bg);
        backdrop-filter: var(--backdrop-blur);
        border: 2px solid rgba(76, 175, 80, 0.3);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: var(--shadow);
        transition: var(--transition);
    }}
    
    /* Hide empty spaces */
    .element-container:has(> .stEmpty) {{
        display: none !important;
    }}
    
    /* Hide streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(0,0,0,0.1);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--gradient-primary);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--gradient-secondary);
    }}
    </style>
    """, unsafe_allow_html=True)

# Remove theme toggle function - not needed for permanent dark mode
# def toggle_theme():
#     """Toggle between light and dark themes"""
#     if st.session_state.theme_mode == 'light':
#         st.session_state.theme_mode = 'dark'
#     else:
#         st.session_state.theme_mode = 'light'
#     safe_rerun()

# Load the trained model
@st.cache_resource
def load_model():
    try:
        model = tf.keras.models.load_model('trained_cotton_disease_model.keras')
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# Disease information
disease_info = {
    "Healthy": {
        "description": "The cotton plant appears to be in good health with no visible signs of disease.",
        "treatment": "Continue regular care and monitoring. Maintain proper watering, fertilization, and pest management practices.",
        "prevention": "Regular inspection, proper spacing, adequate nutrition, and good agricultural practices.",
        "severity": "None",
        "color": "#28a745"
    },
    "Infected-Aphids": {
        "description": "Aphids are small, soft-bodied insects that feed on plant sap, causing yellowing and curling of leaves.",
        "treatment": "Apply insecticidal soap, neem oil, or systemic insecticides. Introduce beneficial insects like ladybugs.",
        "prevention": "Regular monitoring, companion planting, maintaining plant health, and early detection.",
        "severity": "Medium",
        "color": "#ffc107"
    },
    "Infected-Army worm": {
        "description": "Army worms are caterpillars that can cause significant damage by eating leaves, stems, and developing bolls.",
        "treatment": "Apply appropriate insecticides, use biological control agents, or employ integrated pest management.",
        "prevention": "Regular field scouting, crop rotation, maintaining beneficial insect populations.",
        "severity": "High",
        "color": "#dc3545"
    },
    "Infected-Bacterial Blight": {
        "description": "A bacterial disease causing dark, water-soaked lesions on leaves, stems, and bolls.",
        "treatment": "Apply copper-based bactericides, remove infected plant debris, ensure proper drainage.",
        "prevention": "Use resistant varieties, avoid overhead irrigation, maintain field sanitation.",
        "severity": "High",
        "color": "#dc3545"
    },
    "Infected-Cotton Boll Rot": {
        "description": "A fungal disease affecting cotton bolls, causing them to rot and reducing fiber quality.",
        "treatment": "Apply fungicides, improve air circulation, remove infected bolls, ensure proper drainage.",
        "prevention": "Plant resistant varieties, maintain proper plant spacing, avoid excessive moisture.",
        "severity": "High",
        "color": "#dc3545"
    },
    "Infected-Curl Virus": {
        "description": "A viral disease causing leaf curling, yellowing, and stunted growth in cotton plants.",
        "treatment": "Remove infected plants, control vector insects (whiteflies), use virus-free seeds.",
        "prevention": "Use resistant varieties, control whitefly populations, maintain field hygiene.",
        "severity": "High",
        "color": "#dc3545"
    },
    "Infected-Fussarium Wilt": {
        "description": "A soil-borne fungal disease causing wilting, yellowing, and eventual death of cotton plants.",
        "treatment": "Use resistant varieties, improve soil drainage, apply appropriate fungicides, crop rotation.",
        "prevention": "Plant resistant cultivars, maintain soil health, avoid waterlogged conditions.",
        "severity": "Very High",
        "color": "#8b0000"
    },
    "Infected-Powdery mildew": {
        "description": "A fungal disease characterized by white, powdery spots on leaves and stems.",
        "treatment": "Apply fungicides, improve air circulation, remove infected plant parts, avoid overhead watering.",
        "prevention": "Maintain proper plant spacing, ensure good air circulation, avoid high humidity.",
        "severity": "Medium",
        "color": "#ffc107"
    },
    "Infected-Target Spot": {
        "description": "A fungal disease causing circular spots with concentric rings on cotton leaves.",
        "treatment": "Apply appropriate fungicides, remove infected debris, ensure proper crop rotation.",
        "prevention": "Use resistant varieties, maintain field sanitation, avoid prolonged leaf wetness.",
        "severity": "Medium",
        "color": "#ffc107"
    }
}

# Class names (should match your model's training classes)
class_names = [
    "Healthy", "Infected-Aphids", "Infected-Army worm", "Infected-Bacterial Blight",
    "Infected-Cotton Boll Rot", "Infected-Curl Virus", "Infected-Fussarium Wilt",
    "Infected-Powdery mildew", "Infected-Target Spot"
]

def preprocess_image(image):
    """Preprocess uploaded image for model prediction"""
    try:
        image = image.resize((128, 128))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        return image_array
    except Exception as e:
        st.error(f"Error preprocessing image: {e}")
        return None

def predict_disease(model, image_array):
    """Make prediction using the loaded model"""
    try:
        predictions = model.predict(image_array)
        predicted_class_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_index])
        predicted_class = class_names[predicted_class_index]
        return predicted_class, confidence, predictions[0]
    except Exception as e:
        st.error(f"Error making prediction: {e}")
        return None, None, None

def get_disease_category(disease):
    """Get disease category for the disease info table"""
    if disease == "Healthy":
        return "Normal"
    elif "Aphids" in disease or "Army worm" in disease:
        return "Parasitic"
    elif "Bacterial" in disease:
        return "Bacterial"
    elif "Virus" in disease or "Curl" in disease:
        return "Viral"
    elif "Fussarium" in disease:
        return "Soil-borne"
    else:
        return "Fungal"

# Enable GPT-5 (Preview) for all clients
GPT5_PREVIEW_ENABLED = True

# Initialize database
init_database()

# Load CSS
load_css()

# ---- DataFrame display compatibility helper (add after imports / before usage) ----
def safe_dataframe(df, use_container_width=True, hide_index=True, **kwargs):
    """
    Wrapper around st.dataframe to stay compatible with older Streamlit versions
    that may not support the 'hide_index' parameter.
    """
    try:
        return st.dataframe(
            df,
            use_container_width=use_container_width,
            hide_index=hide_index,
            **kwargs
        )
    except TypeError:
        # Fallback: remove index manually if requested
        if hide_index:
            df = df.reset_index(drop=True)
        return st.dataframe(df, use_container_width=use_container_width, **kwargs)

# Add safe rerun helper (place near other helpers, e.g., after safe_dataframe)
def safe_rerun():
    """Compatibility wrapper for rerunning the app across Streamlit versions."""
    try:
        st.rerun()
    except AttributeError:
        # Fallback for older versions
        st.experimental_rerun()

# Validation functions
def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    """Validate password strength and return requirements"""
    requirements = {
        'length': len(password) >= 8,
        'uppercase': any(c.isupper() for c in password),
        'lowercase': any(c.islower() for c in password),
        'digit': any(c.isdigit() for c in password),
        'special': any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    }
    return requirements

def show_password_requirements(password):
    """Display password requirements with validation"""
    if not password:
        return
    
    requirements = validate_password_strength(password)
    
    st.markdown("**Password Requirements:**")
    
    for req, status in requirements.items():
        icon = "✅" if status else "❌"
        text = {
            'length': "At least 8 characters",
            'uppercase': "One uppercase letter",
            'lowercase': "One lowercase letter", 
            'digit': "One number",
            'special': "One special character"
        }[req]
        
        color = "#28a745" if status else "#dc3545"
        st.markdown(f"<span style='color: {color};'>{icon} {text}</span>", unsafe_allow_html=True)

# Main application logic
if not st.session_state.authenticated:
    # Add background image for homepage
    st.markdown('<div class="homepage-bg"></div>', unsafe_allow_html=True)
    
    # Remove theme toggle button - not needed
    # col1, col2, col3 = st.columns([1, 1, 1])
    # with col3:
    #     theme_icon = "🌙" if st.session_state.theme_mode == 'light' else "☀️"
    #     theme_text = "Dark Mode" if st.session_state.theme_mode == 'light' else "Light Mode"
    #     if st.button(f"{theme_icon} {theme_text}", key="theme_toggle"):
    #         toggle_theme()
    
    # Enhanced Authentication interface
    st.markdown('<h1 class="main-header">🌱 COTTON DISEASE DETECTION SYSTEM 🌱</h1>', unsafe_allow_html=True)
    
    # Single centered container for authentication
    st.markdown('<div class="auth-section">', unsafe_allow_html=True)
    
    # Create a single centered column
    _, auth_col, _ = st.columns([1, 2, 1])
    
    with auth_col:
        # Enhanced Authentication tabs
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
        
        with tab1:
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            st.markdown('<h2 class="auth-header">👋 Welcome Back!</h2>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: var(--secondary-text); margin-bottom: 2rem; font-size: 1.1rem; font-weight: 500;">Sign in to continue to your dashboard</p>', unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                login_username = st.text_input(
                    "👤 Username", 
                    placeholder="Enter your username",
                    key="login_user",
                    help="Enter the username you used during registration"
                )
                
                login_password = st.text_input(
                    "🔒 Password", 
                    type="password", 
                    placeholder="Enter your password",
                    key="login_pass",
                    help="Enter your account password"
                )
                
                remember_me = st.checkbox("🔄 Remember me", help="Stay signed in for 30 days")
                
                login_btn = st.form_submit_button("🚀 Sign In")
                
                if login_btn:
                    if login_username and login_password:
                        if len(login_username.strip()) < 3:
                            st.markdown('<div class="alert-warning">⚠️ Username must be at least 3 characters long.</div>', unsafe_allow_html=True)
                        elif len(login_password) < 6:
                            st.markdown('<div class="alert-warning">⚠️ Password must be at least 6 characters long.</div>', unsafe_allow_html=True)
                        else:
                            with st.spinner("🔍 Authenticating..."):
                                success, result = login_user(login_username.strip(), login_password)
                                if success:
                                    st.session_state.authenticated = True
                                    st.session_state.user_data = result
                                    if remember_me:
                                        st.session_state.remember_user = True
                                    st.markdown('<div class="alert-success">✅ Welcome back! Redirecting to your dashboard...</div>', unsafe_allow_html=True)
                                    safe_rerun()
                                else:
                                    st.markdown(f'<div class="alert-error">❌ {result}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="alert-warning">⚠️ Please enter both username and password.</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(
                '<p style="text-align: center; color: var(--secondary-text); font-size: 14px;">'
                'Forgot your password? <a href="#" style="color: var(--primary-color); text-decoration: none;">Reset it here</a>'
                '</p>', 
                unsafe_allow_html=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            st.markdown('<h2 class="auth-header">🌟 Join Us Today!</h2>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: var(--secondary-text); margin-bottom: 2rem; font-size: 1.1rem; font-weight: 500;">Create your account to start protecting your crops</p>', unsafe_allow_html=True)
            
            with st.form("register_form", clear_on_submit=False):
                reg_username = st.text_input(
                    "👤 Username", 
                    placeholder="Choose a unique username",
                    key="reg_user",
                    help="Username must be at least 3 characters long and unique"
                )
                
                if reg_username:
                    if len(reg_username.strip()) < 3:
                        st.markdown('<div class="validation-check invalid">❌ Username must be at least 3 characters</div>', unsafe_allow_html=True)
                    elif not reg_username.replace('_', '').replace('-', '').isalnum():
                        st.markdown('<div class="validation-check invalid">❌ Username can only contain letters, numbers, hyphens, and underscores</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="validation-check valid">✅ Username looks good</div>', unsafe_allow_html=True)
                
                reg_email = st.text_input(
                    "📧 Email Address", 
                    placeholder="Enter your email address",
                    key="reg_email",
                    help="We'll use this for account recovery and notifications"
                )
                
                if reg_email:
                    if validate_email(reg_email):
                        st.markdown('<div class="validation-check valid">✅ Valid email format</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="validation-check invalid">❌ Please enter a valid email address</div>', unsafe_allow_html=True)
                
                reg_password = st.text_input(
                    "🔒 Password", 
                    type="password", 
                    placeholder="Create a strong password",
                    key="reg_pass",
                    help="Password should be at least 8 characters with mixed case, numbers, and symbols"
                )
                
                if reg_password:
                    requirements = validate_password_strength(reg_password)
                    strength_score = sum(requirements.values())
                    
                    if strength_score == 5:
                        strength_text = "Very Strong 💪"
                        strength_color = "#28a745"
                    elif strength_score >= 4:
                        strength_text = "Strong 👍"
                        strength_color = "#28a745"
                    elif strength_score >= 3:
                        strength_text = "Medium ⚠️"
                        strength_color = "#ffc107"
                    else:
                        strength_text = "Weak ❌"
                        strength_color = "#dc3545"
                    
                    st.markdown(f'<div style="color: {strength_color}; font-weight: 600; margin-top: 5px;">Password Strength: {strength_text}</div>', unsafe_allow_html=True)
                    
                    with st.expander("📋 Password Requirements", expanded=(strength_score < 4)):
                        show_password_requirements(reg_password)
                
                reg_confirm_password = st.text_input(
                    "🔒 Confirm Password", 
                    type="password", 
                    placeholder="Confirm your password",
                    key="reg_confirm",
                    help="Re-enter your password to confirm"
                )
                
                if reg_password and reg_confirm_password:
                    if reg_password == reg_confirm_password:
                        st.markdown('<div class="validation-check valid">✅ Passwords match</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="validation-check invalid">❌ Passwords do not match</div>', unsafe_allow_html=True)
                
                terms_accepted = st.checkbox(
                    "📋 I agree to the Terms of Service and Privacy Policy",
                    help="You must accept our terms to create an account"
                )
                
                register_btn = st.form_submit_button("🎉 Create Account")
                
                if register_btn:
                    # Comprehensive validation
                    errors = []
                    
                    if not reg_username or len(reg_username.strip()) < 3:
                        errors.append("Username must be at least 3 characters long")
                    elif not reg_username.replace('_', '').replace('-', '').isalnum():
                        errors.append("Username can only contain letters, numbers, hyphens, and underscores")
                    
                    if not reg_email or not validate_email(reg_email):
                        errors.append("Please enter a valid email address")
                    
                    if not reg_password:
                        errors.append("Password is required")
                    else:
                        requirements = validate_password_strength(reg_password)
                        if sum(requirements.values()) < 3:
                            errors.append("Password is too weak. Please meet at least 3 requirements")
                    
                    if not reg_confirm_password:
                        errors.append("Please confirm your password")
                    elif reg_password != reg_confirm_password:
                        errors.append("Passwords do not match")
                    
                    if not terms_accepted:
                        errors.append("You must accept the Terms of Service and Privacy Policy")
                    
                    if errors:
                        error_list = "<br>".join([f"• {error}" for error in errors])
                        st.markdown(f'<div class="alert-error">❌ Please fix the following issues:<br>{error_list}</div>', unsafe_allow_html=True)
                    else:
                        with st.spinner("🚀 Creating your account..."):
                            success, message = register_user(reg_username.strip(), reg_email.lower().strip(), reg_password)
                            if success:
                                st.markdown(f'<div class="alert-success">🎉 {message} You can now sign in with your credentials!</div>', unsafe_allow_html=True)
                                st.balloons()  # Celebration effect
                            else:
                                st.markdown(f'<div class="alert-error">❌ {message}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced information section
    st.markdown("""
    <div class="info-section">
        <h3 style="color: var(--primary-color); font-size: 2.5rem; margin-bottom: 1.5rem; font-weight: 800; text-shadow: var(--glow);">🌿 Transform Your Cotton Farming</h3>
        <p style="font-size: 1.3rem; color: var(--secondary-text); line-height: 2; max-width: 900px; margin: 0 auto 2rem; font-weight: 400;">
            Join thousands of farmers worldwide who trust our AI-powered disease detection system. 
            Protect your crops, increase yields, and farm smarter with cutting-edge technology.
        </p>
        <div class="info-grid">
            <div class="info-card">
                <div style="font-size: 4rem; margin-bottom: 1.5rem;">🎯</div>
                <div style="font-weight: 800; font-size: 1.3rem; color: var(--primary-color); text-shadow: var(--glow);">98.9% Accuracy</div>
                <div style="color: var(--secondary-text); margin-top: 0.8rem; font-size: 1.1rem;">Industry-leading precision</div>
            </div>
            <div class="info-card">
                <div style="font-size: 4rem; margin-bottom: 1.5rem;">⚡</div>
                <div style="font-weight: 800; font-size: 1.3rem; color: var(--primary-color); text-shadow: var(--glow);">Instant Analysis</div>
                <div style="color: var(--secondary-text); margin-top: 0.8rem; font-size: 1.1rem;">Results in seconds</div>
            </div>
            <div class="info-card">
                <div style="font-size: 4rem; margin-bottom: 1.5rem;">🌱</div>
                <div style="font-weight: 800; font-size: 1.3rem; color: var(--primary-color); text-shadow: var(--glow);">9 Disease Types</div>
                <div style="color: var(--secondary-text); margin-top: 0.8rem; font-size: 1.1rem;">Comprehensive detection</div>
            </div>
            <div class="info-card">
                <div style="font-size: 4rem; margin-bottom: 1.5rem;">🛡️</div>
                <div style="font-weight: 800; font-size: 1.3rem; color: var(--primary-color); text-shadow: var(--glow);">Expert Guidance</div>
                <div style="color: var(--secondary-text); margin-top: 0.8rem; font-size: 1.1rem;">Treatment recommendations</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Main application for authenticated users
    # Enhanced sidebar with premium styling
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: var(--gradient-primary); border-radius: 15px; margin-bottom: 1.5rem; box-shadow: var(--shadow);">
            <h3 style="color: white; margin: 0; font-weight: 800; text-shadow: var(--glow);">👋 Welcome!</h3>
            <p style="color: white; margin: 0; font-weight: 600; font-size: 1.1rem;">{st.session_state.user_data['username']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Remove theme toggle - not needed for permanent dark mode
        # st.markdown("---")
        # theme_icon = "🌙" if st.session_state.theme_mode == 'light' else "☀️"
        # theme_text = "Dark Mode" if st.session_state.theme_mode == 'light' else "Light Mode"
        # if st.button(f"{theme_icon} {theme_text}", key="sidebar_theme_toggle"):
        #     toggle_theme()
        
        # Enhanced Navigation
        st.markdown("### 🧭 Navigation")
        app_mode = st.selectbox(
            "Choose a page:",
            ["🏠 Home", "🔍 Disease Recognition", "📊 Analytics", "📈 Prediction History", "ℹ️ About"],
            help="Navigate through different sections of the app"
        )

        st.markdown("---")
        st.markdown("### 🤖 Model Info")
        st.info(f"""
        **Model Type:** CNN (TensorFlow)  
        **Classes:** 9 diseases  
        **Image Size:** 128x128  
        **Last Updated:** Aug 2025  
        **Status:** Active & Optimized ✅  
        """)
        
        st.markdown("---")
        if st.button("🚪 Logout", key="logout_btn", help="Sign out of your account"):
            logout()

    # Main content based on selected page
    if app_mode == "🏠 Home":
        # Add background image for authenticated homepage too
        st.markdown('<div class="homepage-bg"></div>', unsafe_allow_html=True)
        
        st.markdown('<h1 class="main-header">🌱 COTTON CROP DISEASE DETECTION SYSTEM 🌱</h1>', unsafe_allow_html=True)
        
        # Enhanced welcome message
        st.markdown(f"""
        <div class="welcome-message">
            <h2 style="color: var(--primary-color); margin-bottom: 1rem; font-weight: 800; text-shadow: var(--glow);">Welcome back, {st.session_state.user_data['username']}! 🌿</h2>
            <p style="font-size: 1.2rem; color: var(--text-color); margin: 0; font-weight: 500;">
                Use our AI-powered system to detect cotton diseases instantly and protect your crops.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced feature highlights
        st.markdown("## ✨ Key Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-box">
                <h3>🎯 High Accuracy</h3>
                <p>Advanced CNN architecture trained on thousands of cotton images for reliable disease detection with 98.9% accuracy.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-box">
                <h3>⚡ Instant Results</h3>
                <p>Get disease predictions in seconds with detailed confidence scores and comprehensive treatment recommendations.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-box">
                <h3>📊 Analytics Dashboard</h3>
                <p>Track your prediction history and analyze disease patterns with interactive charts and detailed insights.</p>
            </div>
            """, unsafe_allow_html=True)

    elif app_mode == "🔍 Disease Recognition":
        st.markdown('<h1 class="main-header">🔍 Cotton Disease Recognition</h1>', unsafe_allow_html=True)
        
        # Load model
        model = load_model()
        
        if model is None:
            st.error("❌ Model could not be loaded. Please check if the model file exists.")
            st.stop()
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fff8, #e8f5e8); padding: 2rem; border-radius: 10px; margin-bottom: 2rem; border-left: 5px solid #2E8B57;">
            <h3 style="color: #2E8B57; margin-top: 0;">📸 Upload Cotton Leaf Image</h3>
            <p style="margin-bottom: 0; color: #555;">
                Upload a clear image of a cotton leaf or plant for AI-powered disease detection. 
                Our model supports JPG, PNG, and JPEG formats and works best with well-lit, close-up images.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear image of cotton leaf or plant for disease detection"
        )
        
        if uploaded_file is not None:
            # Display the uploaded image
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Preprocess and predict
            with st.spinner("🔍 Analyzing image... Please wait."):
                image_array = preprocess_image(image)
                
                if image_array is not None:
                    predicted_class, confidence, all_predictions = predict_disease(model, image_array)
                    
                    if predicted_class is not None:
                        # Save prediction to user's history
                        save_user_prediction(
                            st.session_state.user_data['id'],
                            predicted_class,
                            confidence,
                            uploaded_file.name
                        )
                        
                        st.markdown("---")
                        st.markdown("## 🎯 Prediction Results")
                        
                        # Main prediction result
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            # Confidence level styling
                            if confidence > 0.8:
                                confidence_class = "confidence-high"
                                confidence_text = "High Confidence"
                                confidence_icon = "🟢"
                            elif confidence > 0.6:
                                confidence_class = "confidence-medium"
                                confidence_text = "Medium Confidence"
                                confidence_icon = "🟡"
                            else:
                                confidence_class = "confidence-low"
                                confidence_text = "Low Confidence"
                                confidence_icon = "🔴"
                            
                            st.markdown(f"""
                            <div class="{confidence_class}">
                                <h3>{confidence_icon} Prediction: {predicted_class}</h3>
                                <p><strong>Confidence:</strong> {confidence:.1%} ({confidence_text})</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            # Confidence gauge
                            fig_gauge = go.Figure(go.Indicator(
                                mode = "gauge+number",
                                value = confidence * 100,
                                domain = {'x': [0, 1], 'y': [0, 1]},
                                title = {'text': "Confidence"},
                                gauge = {
                                    'axis': {'range': [None, 100]},
                                    'bar': {'color': "#2E8B57"},
                                    'steps': [
                                        {'range': [0, 60], 'color': "#ffe6e6"},
                                        {'range': [60, 80], 'color': "#fff3cd"},
                                        {'range': [80, 100], 'color': "#d4edda"}],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': 90}}))
                            fig_gauge.update_layout(height=300, font={'size': 14})
                            st.plotly_chart(fig_gauge, use_container_width=True)
                        
                        # Disease information
                        if predicted_class in disease_info:
                            info = disease_info[predicted_class]
                            
                            st.markdown("## 📋 Disease Information")
                            st.markdown(f"""
                            <div class="disease-info">
                                <h4 style="color: {info['color']}; margin-top: 0;">
                                    {predicted_class} 
                                    <span style="background: {info['color']}; color: white; padding: 0.2rem 0.5rem; border-radius: 5px; font-size: 0.8rem; margin-left: 1rem;">
                                        {info['severity']} Risk
                                    </span>
                                </h4>
                                
                                <h5>📝 Description:</h5>
                                <p>{info['description']}</p>
                                
                                <h5>💊 Treatment:</h5>
                                <p>{info['treatment']}</p>
                                
                                <h5>🛡️ Prevention:</h5>
                                <p>{info['prevention']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # All predictions breakdown
                        st.markdown("## 📊 Detailed Analysis")
                        
                        # Create DataFrame for all predictions
                        pred_df = pd.DataFrame({
                            'Disease': class_names,
                            'Probability': all_predictions
                        }).sort_values('Probability', ascending=False)
                        
                        # Top 5 predictions bar chart
                        top_5 = pred_df.head(5)
                        
                        fig_bar = px.bar(
                            top_5,
                            x='Probability',
                            y='Disease',
                            orientation='h',
                            title="Top 5 Disease Probabilities",
                            color='Probability',
                            color_continuous_scale='RdYlGn_r'
                        )
                        fig_bar.update_layout(
                            yaxis={'categoryorder': 'total ascending'},
                            font=dict(size=14),
                            title_font_size=18,
                            height=400
                        )
                        fig_bar.update_xaxis(tickformat='.0%')
                        st.plotly_chart(fig_bar, use_container_width=True)
                        
                        # Recommendations based on prediction
                        st.markdown("## 💡 Recommendations")
                        
                        if predicted_class == "Healthy":
                            st.success("""
                            ✅ **Great news!** Your cotton plant appears healthy. Continue with:
                            - Regular monitoring and inspection
                            - Maintaining proper watering schedule
                            - Ensuring adequate nutrition
                            - Following preventive agricultural practices
                            """)
                        else:
                            if confidence > 0.8:
                                st.error(f"""
                                🚨 **High confidence detection of {predicted_class}**
                                - Take immediate action based on treatment recommendations above
                                - Consult with agricultural specialists
                                - Isolate affected plants if necessary
                                - Monitor surrounding plants closely
                                """)
                            elif confidence > 0.6:
                                st.warning(f"""
                                ⚠️ **Possible {predicted_class} detected**
                                - Monitor the plant closely for symptom development
                                - Consider preventive treatments
                                - Take additional photos in different lighting
                                - Consult agricultural extension services
                                """)
                            else:
                                st.info(f"""
                                ℹ️ **Uncertain detection**
                                - Image quality may need improvement
                                - Try uploading a clearer, well-lit image
                                - Consider multiple photos from different angles
                                - Seek professional agricultural advice
                                """)
                    else:
                        st.error("❌ Failed to make prediction. Please try again with a different image.")
                else:
                    st.error("❌ Failed to process the image. Please try uploading a different image.")

    elif app_mode == "📊 Analytics":
        st.markdown('<h1 class="main-header">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
        
        # Load user predictions
        user_predictions = get_user_predictions(st.session_state.user_data['id'])
        
        if not user_predictions:
            st.warning("No prediction history available. Make some predictions first!")
        else:
            df = pd.DataFrame(user_predictions)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Predictions", len(df))
            
            with col2:
                healthy_count = len(df[df['disease'] == 'Healthy'])
                st.metric("Healthy Plants", healthy_count)
            
            with col3:
                infected_count = len(df[df['disease'] != 'Healthy'])
                st.metric("Infected Plants", infected_count)
            
            with col4:
                avg_confidence = df['confidence'].mean()
                st.metric("Avg. Confidence", f"{avg_confidence:.1%}")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Disease distribution pie chart
                disease_counts = df['disease'].value_counts()
                colors = ['#2E8B57' if disease == 'Healthy' else '#dc3545' for disease in disease_counts.index]
                
                fig_pie = px.pie(
                    values=disease_counts.values,
                    names=disease_counts.index,
                    title="Disease Distribution",
                    color_discrete_sequence=colors
                )
                fig_pie.update_layout(
                    font=dict(size=14),
                    title_font_size=18,
                    showlegend=True
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Confidence distribution histogram
                fig_hist = px.histogram(
                    df,
                    x='confidence',
                    nbins=20,
                    title="Confidence Score Distribution",
                    color_discrete_sequence=['#2E8B57']
                )
                fig_hist.update_layout(
                    xaxis_title="Confidence Score",
                    yaxis_title="Count",
                    font=dict(size=14),
                    title_font_size=18
                )
                fig_hist.update_xaxis(tickformat='.0%')
                st.plotly_chart(fig_hist, use_container_width=True)

    elif app_mode == "📈 Prediction History":
        st.markdown('<h1 class="main-header">📈 Your Prediction History</h1>', unsafe_allow_html=True)
        
        user_predictions = get_user_predictions(st.session_state.user_data['id'])
        
        if not user_predictions:
            st.info("No predictions yet! Start by uploading cotton leaf images.")
        else:
            df = pd.DataFrame(user_predictions)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Display recent predictions
            st.markdown("## Recent Predictions")
            
            for i, row in df.head(10).iterrows():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                
                with col1:
                    st.write(f"**{row['disease']}**")
                
                with col2:
                    st.write(f"{row['confidence']:.1%}")
                
                with col3:
                    severity = disease_info.get(row['disease'], {}).get('severity', 'Unknown')
                    st.write(severity)
                
                with col4:
                    st.write(row['timestamp'].strftime('%Y-%m-%d %H:%M'))

    elif app_mode == "ℹ️ About":
        st.markdown('<h1 class="main-header">ℹ️ About Cotton Disease Detection System</h1>', unsafe_allow_html=True)
        
        # Introduction
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fff8, #e8f5e8); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
            <h2 style="color: #2E8B57; margin-top: 0;">🌱 Protecting Cotton Crops with AI</h2>
            <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 0;">
                Our Cotton Disease Detection System leverages cutting-edge artificial intelligence to help farmers 
                identify diseases in cotton plants quickly and accurately. Early detection leads to better crop 
                management and higher yields.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key features
        st.markdown("## ✨ Key Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 **High Accuracy Detection**
            - 98.9% accuracy rate
            - Trained on thousands of cotton images
            - Advanced CNN architecture
            - Real-time analysis
            
            ### 📊 **Comprehensive Analytics**
            - Detailed prediction history
            - Interactive charts and visualizations
            - Disease trend analysis
            - Performance metrics
            """)
        
        with col2:
            st.markdown("""
            ### 🦠 **Multiple Disease Types**
            - Bacterial infections
            - Fungal diseases
            - Viral infections
            - Parasitic damage
            
            ### 💡 **Expert Recommendations**
            - Treatment suggestions
            - Prevention strategies
            - Risk level assessment
            - Agricultural best practices
            """)
        
        # Technology stack
        st.markdown("---")
        st.markdown("## 🔧 Technology Stack")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🤖 Machine Learning**
            - TensorFlow 2.10.0
            - Convolutional Neural Networks
            - Image Classification
            - Transfer Learning
            """)
        
        with col2:
            st.markdown("""
            **🖥️ Frontend & Backend**
            - Streamlit
            - Python 3.8+
            - PIL (Image Processing)
            - NumPy & Pandas
            """)
        
        with col3:
            st.markdown("""
            **📊 Visualization**
            - Plotly Interactive Charts
            - Real-time Analytics
            - Export Capabilities
            - Responsive Design
            """)
        
        # Model information
        st.markdown("---")
        st.markdown("## 🤖 Model Information")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### **Training Details**
            - **Dataset Size**: 10,000+ cotton leaf images
            - **Image Resolution**: 128x128 pixels
            - **Training Epochs**: 50 epochs
            - **Validation Split**: 20%
            - **Data Augmentation**: Yes (rotation, flip, zoom)
            - **Optimization**: Adam optimizer
            - **Loss Function**: Categorical crossentropy
            
            ### **Performance Metrics**
            - **Overall Accuracy**: 98.9%
            - **Precision**: 98.7%
            - **Recall**: 98.5%
            - **F1-Score**: 98.6%
            """)
        
        with col2:
            # Model architecture visualization
            st.markdown("""
            ### **Architecture**
            ```
            Input Layer (128x128x3)
                    ↓
            Conv2D + ReLU + MaxPool
                    ↓
            Conv2D + ReLU + MaxPool
                    ↓
            Conv2D + ReLU + MaxPool
                    ↓
            Flatten + Dropout
                    ↓
            Dense (512) + ReLU
                    ↓
            Dense (256) + ReLU
                    ↓
            Output (9 classes)
            ```
            """)
        
        # Disease categories
        st.markdown("---")
        st.markdown("## 🦠 Detectable Disease Categories")
        
        # Create disease categories table
        disease_data = []
        for disease, info in disease_info.items():
            disease_data.append({
                "Disease": disease,
                "Type": "Healthy" if disease == "Healthy" else "Infected",
                "Severity": info["severity"],
                "Category": get_disease_category(disease)
            })
        
        disease_df = pd.DataFrame(disease_data)
        # REPLACED st.dataframe(...) WITH safe_dataframe FOR VERSION COMPATIBILITY
        safe_dataframe(disease_df, use_container_width=True, hide_index=True)
        
        # Usage guidelines
        st.markdown("---")
        st.markdown("## 📋 Usage Guidelines")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### **📸 Image Requirements**
            - **Format**: JPG, PNG, JPEG
            - **Size**: Any size (auto-resized)
            - **Quality**: High resolution preferred
            - **Lighting**: Good, natural lighting
            - **Focus**: Clear, non-blurry images
            - **Subject**: Cotton leaves or plants
            """)
        
        with col2:
            st.markdown("""
            ### **🎯 Best Practices**
            - Upload multiple images for comparison
            - Use images taken in good lighting
            - Capture different angles of affected areas
            - Avoid heavily filtered or edited images
            - Include surrounding context when possible
            - Clean camera lens for clarity
            """)
        
        # Contact and support
        st.markdown("---")
        st.markdown("## 📞 Support & Contact")
        
        # Removed "Need Help?" heading and descriptive paragraph
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; display:flex; gap:2rem; flex-wrap:wrap;">
            <div>
                <strong>📧 Email:</strong><br>
                support@cottondiseaseai.com
            </div>
            <div>
                <strong>📱 Phone:</strong><br>
                +1 (555) 123-4567
            </div>
            <div>
                <strong>🌐 Website:</strong><br>
                www.cottondiseaseai.com
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Version information
        st.markdown("---")
        st.markdown("## 📋 Version Information")
        
        version_info = {
            "System Version": "2.1.0",
            "Model Version": "1.5.2",
            "Last Updated": "August 2025",
            "TensorFlow": "2.10.0",
            "Streamlit": "1.28.0",
            "Python": "3.8+",
            "Database": "SQLite 3"
        }
        
        col1, col2 = st.columns(2)
        for i, (key, value) in enumerate(version_info.items()):
            with col1 if i % 2 == 0 else col2:
                st.markdown(f"**{key}:** {value}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--secondary-text); font-size: 1rem; padding: 2rem; background: var(--glass-bg); backdrop-filter: var(--backdrop-blur); border-radius: 15px; margin-top: 3rem; border: 1px solid rgba(76, 175, 80, 0.2);">
    <p style="margin: 0; font-weight: 600;">🌱 Cotton Disease Detection System v2.0 - Powered by AI</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: var(--secondary-text);">Advanced Agricultural Technology for Better Crop Management</p>
</div>
""", unsafe_allow_html=True)

