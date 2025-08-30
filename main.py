import streamlit as st
import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# TensorFlow Model Prediction
def model_prediction(test_image):
    model = tf.keras.models.load_model("trained_cotton_disease_model.keras")
    image = tf.keras.preprocessing.image.load_img(test_image, target_size=(128, 128))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])  # Convert single image to batch
    predictions = model.predict(input_arr)
    confidence_scores = tf.nn.softmax(predictions).numpy()[0]
    return np.argmax(predictions), confidence_scores

# Get disease information
def get_disease_info(disease_name):
    disease_info = {
        'Healthy': {
            'description': '🌱 Your cotton plant appears to be healthy! This is great news.',
            'symptoms': ['Green, vibrant leaves', 'Normal growth pattern', 'No visible damage'],
            'prevention': ['Maintain proper irrigation', 'Regular monitoring', 'Balanced fertilization'],
            'treatment': 'No treatment needed. Continue good agricultural practices.',
            'severity': 'None',
            'color': '#28a745'
        },
        'Infected-Aphids': {
            'description': '🐛 Aphid infestation detected. Small insects that suck plant juices.',
            'symptoms': ['Yellowing leaves', 'Sticky honeydew', 'Stunted growth', 'Curled leaves'],
            'prevention': ['Use reflective mulches', 'Encourage natural predators', 'Regular inspection'],
            'treatment': 'Apply insecticidal soap or neem oil. Use beneficial insects like ladybugs.',
            'severity': 'Moderate',
            'color': '#ffc107'
        },
        'Infected-Army worm': {
            'description': '🐛 Army worm damage detected. Caterpillars that feed on leaves and stems.',
            'symptoms': ['Holes in leaves', 'Defoliation', 'Feeding damage on stems', 'Visible caterpillars'],
            'prevention': ['Crop rotation', 'Remove crop residues', 'Use pheromone traps'],
            'treatment': 'Apply Bt (Bacillus thuringiensis) or appropriate insecticides. Hand-pick if infestation is small.',
            'severity': 'High',
            'color': '#dc3545'
        },
        'Infected-Bacterial Blight': {
            'description': '🦠 Bacterial blight infection. Caused by Xanthomonas bacteria.',
            'symptoms': ['Water-soaked spots', 'Brown lesions', 'Yellowing around spots', 'Leaf drop'],
            'prevention': ['Use resistant varieties', 'Avoid overhead irrigation', 'Crop rotation'],
            'treatment': 'Apply copper-based bactericides. Remove infected plant parts. Improve air circulation.',
            'severity': 'High',
            'color': '#dc3545'
        },
        'Infected-Cotton Boll Rot': {
            'description': '🍂 Cotton boll rot detected. Fungal infection affecting cotton bolls.',
            'symptoms': ['Rotting bolls', 'Discolored cotton', 'Fuzzy growth on bolls', 'Reduced yield'],
            'prevention': ['Proper spacing', 'Good drainage', 'Avoid late irrigation'],
            'treatment': 'Apply fungicides. Remove infected bolls. Ensure proper field drainage.',
            'severity': 'Very High',
            'color': '#6f42c1'
        },
        'Infected-Curl Virus': {
            'description': '🦠 Leaf curl virus infection. Transmitted by whiteflies.',
            'symptoms': ['Upward leaf curling', 'Yellowing', 'Stunted growth', 'Reduced flowering'],
            'prevention': ['Control whitefly population', 'Use virus-resistant varieties', 'Remove infected plants'],
            'treatment': 'No direct cure. Focus on vector control and remove infected plants.',
            'severity': 'Very High',
            'color': '#6f42c1'
        },
        'Infected-Fusarium Wilt': {
            'description': '🍄 Fusarium wilt detected. Soil-borne fungal disease.',
            'symptoms': ['Wilting', 'Yellowing leaves', 'Vascular discoloration', 'Plant death'],
            'prevention': ['Use resistant varieties', 'Soil fumigation', 'Crop rotation'],
            'treatment': 'No effective treatment once infected. Focus on prevention and resistant varieties.',
            'severity': 'Very High',
            'color': '#6f42c1'
        },
        'Infected-Powdery mildew': {
            'description': '🍄 Powdery mildew infection. White powdery growth on leaves.',
            'symptoms': ['White powdery spots', 'Yellowing leaves', 'Reduced photosynthesis', 'Stunted growth'],
            'prevention': ['Proper spacing', 'Good air circulation', 'Avoid overhead watering'],
            'treatment': 'Apply sulfur-based fungicides or baking soda solution. Remove affected leaves.',
            'severity': 'Moderate',
            'color': '#ffc107'
        },
        'Infected-Target Spot': {
            'description': '🎯 Target spot disease. Fungal infection causing circular lesions.',
            'symptoms': ['Circular spots with target-like rings', 'Brown lesions', 'Yellowing around spots'],
            'prevention': ['Crop rotation', 'Remove crop debris', 'Proper spacing'],
            'treatment': 'Apply fungicides containing chlorothalonil or copper. Improve air circulation.',
            'severity': 'Moderate',
            'color': '#ffc107'
        }
    }
    return disease_info.get(disease_name, disease_info['Healthy'])

# Load prediction history
def load_prediction_history():
    if os.path.exists('prediction_history.json'):
        with open('prediction_history.json', 'r') as f:
            return json.load(f)
    return []

# Save prediction to history
def save_prediction(disease, confidence, timestamp):
    history = load_prediction_history()
    history.append({
        'disease': disease,
        'confidence': confidence,
        'timestamp': timestamp
    })
    # Keep only last 100 predictions
    if len(history) > 100:
        history = history[-100:]
    
    with open('prediction_history.json', 'w') as f:
        json.dump(history, f)

# Configure page
st.set_page_config(
    page_title="Cotton Disease Detection",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #2E8B57, #90EE90);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #2E8B57;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin: 0.5rem;
    }
    .disease-info {
        background-color: #fff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .severity-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E8B57;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🌱 Navigation Dashboard")
app_mode = st.sidebar.selectbox(
    "Choose a Page", 
    ["🏠 Home", "📊 Analytics", "🔍 Disease Recognition", "📈 Prediction History", "ℹ️ About"],
    help="Select the page you want to navigate to"
)

# Add sidebar metrics
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")

# Create sample metrics (you can replace with real data)
history = load_prediction_history()
total_predictions = len(history)
if history:
    recent_diseases = [pred['disease'] for pred in history[-10:]]
    healthy_percentage = (recent_diseases.count('Healthy') / len(recent_diseases)) * 100 if recent_diseases else 0
else:
    healthy_percentage = 0

col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Total Scans", total_predictions, delta=None)
with col2:
    st.metric("Healthy %", f"{healthy_percentage:.1f}%", delta=None)

# Add model info
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Model Info")
st.sidebar.info("""
**Model Type:** CNN (TensorFlow)  
**Accuracy:** 98.9%  
**Classes:** 9 diseases  
**Image Size:** 128x128  
**Last Updated:** Aug 2025
""")

# Main Page
if app_mode == "🏠 Home":
    st.markdown('<h1 class="main-header">🌱 COTTON CROP DISEASE DETECTION SYSTEM 🌱</h1>', unsafe_allow_html=True)
    
    # Hero section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("home_page.png"):
            st.image("home_page.png", use_column_width=True, caption="AI-Powered Cotton Disease Detection")
    
    st.markdown("---")
    
    # Welcome message
    st.markdown("""
    <div style="text-align: center; font-size: 1.2rem; margin: 2rem 0;">
        Welcome to our advanced AI-powered Cotton Disease Detection System! 🌿�  
        Protect your crops with cutting-edge machine learning technology.
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("## ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-box">
            <h3>🎯 High Accuracy</h3>
            <p>98.9% accuracy with advanced CNN architecture trained on thousands of cotton images.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-box">
            <h3>⚡ Instant Results</h3>
            <p>Get disease predictions in seconds with detailed confidence scores and treatment recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-box">
            <h3>📊 Comprehensive Analysis</h3>
            <p>Track prediction history, view analytics, and monitor crop health trends over time.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works
    st.markdown("## 🔬 How It Works")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>📸</h2>
            <h4>1. Upload Image</h4>
            <p>Take a clear photo of your cotton plant</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>🤖</h2>
            <h4>2. AI Analysis</h4>
            <p>Our AI model analyzes the image</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>📋</h2>
            <h4>3. Get Results</h4>
            <p>Receive detailed disease diagnosis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>💡</h2>
            <h4>4. Take Action</h4>
            <p>Follow treatment recommendations</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Disease categories
    st.markdown("## 🦠 Detectable Diseases")
    
    diseases = [
        ("🌱 Healthy", "Normal healthy cotton plants"),
        ("🐛 Aphids", "Small insects causing yellowing and stunted growth"),
        ("🐛 Army Worm", "Caterpillars causing holes and defoliation"),
        ("🦠 Bacterial Blight", "Water-soaked spots and brown lesions"),
        ("🍂 Cotton Boll Rot", "Fungal infection affecting cotton bolls"),
        ("🦠 Curl Virus", "Virus causing upward leaf curling"),
        ("🍄 Fusarium Wilt", "Soil-borne fungal disease causing wilting"),
        ("🍄 Powdery Mildew", "White powdery growth on leaves"),
        ("🎯 Target Spot", "Circular lesions with target-like rings")
    ]
    
    cols = st.columns(3)
    for i, (disease, description) in enumerate(diseases):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 1rem; margin: 0.5rem 0; border-radius: 8px;">
                <h4>{disease}</h4>
                <p style="font-size: 0.9rem; color: #666;">{description}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; background: linear-gradient(135deg, #2E8B57, #90EE90); padding: 2rem; border-radius: 10px; color: white;">
        <h2>🚀 Ready to Protect Your Cotton Crops?</h2>
        <p style="font-size: 1.1rem;">Upload an image and get instant AI-powered disease detection!</p>
    </div>
    """, unsafe_allow_html=True)

elif app_mode == "📊 Analytics":
    st.markdown('<h1 class="main-header">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load prediction history
    history = load_prediction_history()
    
    if not history:
        st.warning("No prediction history available. Make some predictions first!")
        st.info("Navigate to the Disease Recognition page to start making predictions.")
    else:
        # Convert to DataFrame
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Overview metrics
        st.markdown("## 📈 Overview Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>Total Predictions</h3>
                <h2>{}</h2>
            </div>
            """.format(len(df)), unsafe_allow_html=True)
        
        with col2:
            healthy_count = len(df[df['disease'] == 'Healthy'])
            healthy_percentage = (healthy_count / len(df)) * 100
            st.markdown("""
            <div class="metric-card">
                <h3>Healthy Plants</h3>
                <h2>{:.1f}%</h2>
            </div>
            """.format(healthy_percentage), unsafe_allow_html=True)
        
        with col3:
            avg_confidence = df['confidence'].mean() * 100
            st.markdown("""
            <div class="metric-card">
                <h3>Avg Confidence</h3>
                <h2>{:.1f}%</h2>
            </div>
            """.format(avg_confidence), unsafe_allow_html=True)
        
        with col4:
            disease_count = len(df[df['disease'] != 'Healthy'])
            st.markdown("""
            <div class="metric-card">
                <h3>Diseases Detected</h3>
                <h2>{}</h2>
            </div>
            """.format(disease_count), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🥧 Disease Distribution")
            disease_counts = df['disease'].value_counts()
            fig_pie = px.pie(
                values=disease_counts.values, 
                names=disease_counts.index,
                title="Distribution of Detected Diseases",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Confidence Score Distribution")
            fig_hist = px.histogram(
                df, 
                x='confidence', 
                bins=20,
                title="Distribution of Confidence Scores",
                labels={'confidence': 'Confidence Score', 'count': 'Frequency'}
            )
            fig_hist.update_traces(marker_color='skyblue')
            st.plotly_chart(fig_hist, use_container_width=True)
        
        # Time series analysis
        if len(df['date'].unique()) > 1:
            st.markdown("### 📅 Predictions Over Time")
            daily_counts = df.groupby('date').size().reset_index(name='count')
            fig_line = px.line(
                daily_counts, 
                x='date', 
                y='count',
                title="Daily Prediction Count",
                markers=True
            )
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Recent predictions table
        st.markdown("### 📋 Recent Predictions")
        recent_df = df.tail(10)[['timestamp', 'disease', 'confidence']].copy()
        recent_df['confidence'] = (recent_df['confidence'] * 100).round(2)
        recent_df['confidence'] = recent_df['confidence'].astype(str) + '%'
        recent_df = recent_df.rename(columns={
            'timestamp': 'Time',
            'disease': 'Disease',
            'confidence': 'Confidence'
        })
        st.dataframe(recent_df, use_container_width=True)

elif app_mode == "🔍 Disease Recognition":
    st.markdown('<h1 class="main-header">🔍 Disease Recognition System</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h3>🎯 Upload Your Cotton Plant Image</h3>
        <p>For best results, ensure your image is clear, well-lit, and shows the affected plant parts clearly.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Image upload with enhanced UI
    uploaded_file = st.file_uploader(
        "Choose an image file", 
        type=['jpg', 'jpeg', 'png', 'bmp'],
        help="Upload a clear image of your cotton plant. Supported formats: JPG, JPEG, PNG, BMP"
    )
    
    if uploaded_file is not None:
        # Create two columns for image and info
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📸 Uploaded Image")
            st.image(uploaded_file, use_column_width=True, caption="Uploaded Cotton Plant Image")
            
            # Image info
            image = Image.open(uploaded_file)
            st.markdown(f"""
            **Image Details:**
            - **Size:** {image.size[0]} x {image.size[1]} pixels
            - **Format:** {image.format}
            - **Mode:** {image.mode}
            - **File Size:** {len(uploaded_file.getvalue()) / 1024:.2f} KB
            """)
        
        with col2:
            st.markdown("### 🔬 Analysis")
            
            # Predict button with enhanced styling
            predict_button = st.button(
                "🚀 Analyze Image", 
                type="primary",
                help="Click to start AI analysis of your cotton plant image",
                use_container_width=True
            )
            
            if predict_button:
                with st.spinner('🤖 AI is analyzing your image...'):
                    # Simulate processing time for better UX
                    import time
                    time.sleep(2)
                    
                    try:
                        # Get prediction
                        result_index, confidence_scores = model_prediction(uploaded_file)
                        
                        # Reading Labels
                        class_names = [
                            'Healthy', 
                            'Infected-Aphids', 
                            'Infected-Army worm', 
                            'Infected-Bacterial Blight', 
                            'Infected-Cotton Boll Rot', 
                            'Infected-Curl Virus', 
                            'Infected-Fusarium Wilt', 
                            'Infected-Powdery mildew', 
                            'Infected-Target Spot'
                        ]
                        
                        predicted_disease = class_names[result_index]
                        confidence = confidence_scores[result_index]
                        
                        # Save prediction to history
                        save_prediction(predicted_disease, float(confidence), datetime.now().isoformat())
                        
                        # Display results with enhanced styling
                        st.success("✅ Analysis Complete!")
                        
                        # Main prediction result
                        disease_info = get_disease_info(predicted_disease)
                        
                        st.markdown(f"""
                        <div class="disease-info">
                            <h2 style="color: {disease_info['color']};">🎯 Prediction Result</h2>
                            <h3>{predicted_disease}</h3>
                            <div class="severity-badge" style="background-color: {disease_info['color']};">
                                Confidence: {confidence*100:.2f}%
                            </div>
                            <div class="severity-badge" style="background-color: {disease_info['color']};">
                                Severity: {disease_info['severity']}
                            </div>
                            <p style="margin-top: 1rem; font-size: 1.1rem;">{disease_info['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Detailed information in expandable sections
                        with st.expander("📋 Detailed Disease Information", expanded=True):
                            tab1, tab2, tab3 = st.tabs(["🔍 Symptoms", "🛡️ Prevention", "💊 Treatment"])
                            
                            with tab1:
                                st.markdown("**Common Symptoms:**")
                                for symptom in disease_info['symptoms']:
                                    st.markdown(f"• {symptom}")
                            
                            with tab2:
                                st.markdown("**Prevention Measures:**")
                                for prevention in disease_info['prevention']:
                                    st.markdown(f"• {prevention}")
                            
                            with tab3:
                                st.markdown("**Recommended Treatment:**")
                                st.markdown(disease_info['treatment'])
                        
                        # Confidence scores for all classes
                        with st.expander("📊 Detailed Confidence Scores"):
                            st.markdown("**Confidence scores for all disease classes:**")
                            
                            # Create DataFrame for better visualization
                            conf_df = pd.DataFrame({
                                'Disease': class_names,
                                'Confidence': confidence_scores * 100
                            }).sort_values('Confidence', ascending=False)
                            
                            # Create bar chart
                            fig = px.bar(
                                conf_df, 
                                x='Confidence', 
                                y='Disease',
                                orientation='h',
                                title="Confidence Scores for All Disease Classes",
                                color='Confidence',
                                color_continuous_scale='viridis'
                            )
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show data table
                            conf_df['Confidence'] = conf_df['Confidence'].round(2)
                            st.dataframe(conf_df, use_container_width=True, hide_index=True)
                        
                        # Recommendations
                        if predicted_disease != 'Healthy':
                            st.warning("⚠️ **Important:** This is an AI prediction. Please consult with agricultural experts for professional advice.")
                        
                        # Add to history notification
                        st.info("📝 This prediction has been saved to your history. Check the Analytics page for trends!")
                        
                    except Exception as e:
                        st.error(f"❌ Error during prediction: {str(e)}")
                        st.info("Please try uploading a different image or check if the model file is available.")
    else:
        st.markdown("""
        <div style="border: 2px dashed #ccc; padding: 3rem; text-align: center; border-radius: 10px; margin: 2rem 0;">
            <h3>📁 No Image Uploaded</h3>
            <p>Please upload an image of your cotton plant to get started with disease detection.</p>
            <p><strong>Tips for best results:</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>Use good lighting conditions</li>
                <li>Capture clear, focused images</li>
                <li>Include affected plant parts</li>
                <li>Avoid blurry or dark images</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif app_mode == "📈 Prediction History":
    st.markdown('<h1 class="main-header">📈 Prediction History</h1>', unsafe_allow_html=True)
    
    history = load_prediction_history()
    
    if not history:
        st.warning("📝 No prediction history found!")
        st.info("Make some predictions using the Disease Recognition page to see your history here.")
    else:
        # Convert to DataFrame
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['confidence_percent'] = (df['confidence'] * 100).round(2)
        
        # Summary stats
        st.markdown("## 📊 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Predictions", len(df))
        with col2:
            healthy_pct = (len(df[df['disease'] == 'Healthy']) / len(df)) * 100
            st.metric("Healthy Plants", f"{healthy_pct:.1f}%")
        with col3:
            avg_conf = df['confidence'].mean() * 100
            st.metric("Avg Confidence", f"{avg_conf:.1f}%")
        with col4:
            unique_diseases = df['disease'].nunique()
            st.metric("Unique Diseases", unique_diseases)
        
        # Filters
        st.markdown("## 🔍 Filter History")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            disease_filter = st.selectbox(
                "Filter by Disease",
                ['All'] + sorted(df['disease'].unique().tolist())
            )
        
        with col2:
            min_confidence = st.slider(
                "Minimum Confidence (%)",
                0.0, 100.0, 0.0, 1.0
            )
        
        with col3:
            max_records = st.number_input(
                "Max Records to Show",
                min_value=10, max_value=len(df), value=min(50, len(df))
            )
        
        # Apply filters
        filtered_df = df.copy()
        if disease_filter != 'All':
            filtered_df = filtered_df[filtered_df['disease'] == disease_filter]
        
        filtered_df = filtered_df[filtered_df['confidence_percent'] >= min_confidence]
        filtered_df = filtered_df.tail(max_records)
        
        # Display filtered results
        st.markdown(f"## 📋 History Records ({len(filtered_df)} records)")
        
        if len(filtered_df) > 0:
            # Prepare display DataFrame
            display_df = filtered_df[['timestamp', 'disease', 'confidence_percent']].copy()
            display_df = display_df.rename(columns={
                'timestamp': 'Date & Time',
                'disease': 'Disease',
                'confidence_percent': 'Confidence (%)'
            })
            display_df = display_df.sort_values('Date & Time', ascending=False)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Download button
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download History as CSV",
                data=csv,
                file_name=f"cotton_disease_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No records match your filter criteria.")
        
        # Clear history option
        st.markdown("---")
        if st.button("🗑️ Clear All History", type="secondary"):
            if st.session_state.get('confirm_clear', False):
                # Actually clear the history
                with open('prediction_history.json', 'w') as f:
                    json.dump([], f)
                st.success("✅ History cleared successfully!")
                st.session_state['confirm_clear'] = False
                st.experimental_rerun()
            else:
                st.session_state['confirm_clear'] = True
                st.warning("⚠️ Click again to confirm clearing all history. This action cannot be undone!")

elif app_mode == "ℹ️ About":
    st.markdown('<h1 class="main-header">ℹ️ About the Project</h1>', unsafe_allow_html=True)
    
    # Project overview
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h2>🌱 Cotton Disease Detection System</h2>
        <p style="font-size: 1.1rem;">
            An advanced AI-powered system for early detection and diagnosis of cotton crop diseases 
            using state-of-the-art deep learning technology.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Technical details
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dataset", "🧠 Model", "👥 Team", "🔧 Technical"])
    
    with tab1:
        st.markdown("### 📊 Dataset Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Dataset Overview:**
            - **Total Images:** 7,800+ RGB images
            - **Classes:** 9 different categories
            - **Resolution:** High-quality cotton crop images
            - **Split:** 80/20 train-validation ratio
            
            **Training Set:**
            - Images: 6,251
            - Used for model training
            - Augmented for better generalization
            
            **Validation Set:**
            - Images: 1,563 
            - Used for model evaluation
            - Maintains class distribution
            """)
        
        with col2:
            st.markdown("""
            **Disease Categories:**
            1. 🌱 **Healthy** - Normal cotton plants
            2. 🐛 **Aphids** - Insect infestation  
            3. 🐛 **Army Worm** - Caterpillar damage
            4. 🦠 **Bacterial Blight** - Bacterial infection
            5. 🍂 **Cotton Boll Rot** - Fungal boll infection
            6. 🦠 **Curl Virus** - Viral leaf curling
            7. 🍄 **Fusarium Wilt** - Soil-borne fungus
            8. 🍄 **Powdery Mildew** - White fungal growth
            9. 🎯 **Target Spot** - Circular lesion disease
            """)
    
    with tab2:
        st.markdown("### 🧠 Model Architecture")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Model Type:** Convolutional Neural Network (CNN)
            
            **Architecture:**
            - **Input Layer:** 128x128x3 RGB images
            - **Conv2D Layers:** Progressive filters (32→64→128→256→512)
            - **MaxPooling:** Dimensionality reduction
            - **Dropout:** 0.25 and 0.4 for regularization
            - **Dense Layer:** 1500 units with ReLU
            - **Output:** 9 classes with Softmax activation
            
            **Training:**
            - **Epochs:** 50
            - **Optimizer:** Adam
            - **Loss Function:** Categorical Crossentropy
            """)
        
        with col2:
            st.markdown("""
            **Performance Metrics:**
            - **Training Accuracy:** 98.9%
            - **Validation Accuracy:** 89.1%
            - **Model Size:** Optimized for deployment
            - **Inference Time:** < 2 seconds
            
            **Technology Stack:**
            - **Framework:** TensorFlow 2.10.0
            - **Backend:** Keras
            - **Deployment:** Streamlit Cloud
            - **Libraries:** NumPy, Pandas, Matplotlib
            
            **Model Features:**
            - Batch normalization for stable training
            - Data augmentation for robustness
            - Transfer learning capabilities
            """)
    
    with tab3:
        st.markdown("### 👥 Development Team")
        
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3>🎓 Project Contributors</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Team members
        col1, col2, col3, col4 = st.columns(4)
        
        team_members = [
            ("Akshat", "🧠 AI/ML Lead", "Model development and training"),
            ("Himanshu", "📊 Data Scientist", "Dataset preparation and analysis"),
            ("Minav", "💻 Backend Developer", "Model optimization and deployment"),
            ("Vedansh", "🎨 Frontend Developer", "UI/UX design and Streamlit app")
        ]
        
        for i, (name, role, contribution) in enumerate(team_members):
            with [col1, col2, col3, col4][i]:
                st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem; border: 1px solid #ddd; border-radius: 10px; margin: 0.5rem;">
                    <h2>👨‍💻</h2>
                    <h4>{name}</h4>
                    <p style="color: #666; font-weight: bold;">{role}</p>
                    <p style="font-size: 0.9rem;">{contribution}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; background-color: #f0f2f6; padding: 1.5rem; border-radius: 10px;">
            <h4>🙏 Acknowledgments</h4>
            <p>Special thanks to the agricultural research community and open-source contributors 
            who made this project possible.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 🔧 Technical Specifications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Software Requirements:**
            ```
            Python 3.8+
            TensorFlow 2.10.0
            Streamlit 1.28+
            NumPy 1.24.3
            Pandas 2.1.0
            Matplotlib 3.7.2
            Seaborn 0.13.0
            Plotly 5.17.0
            Pillow 10.0.0
            ```
            
            **Hardware Recommendations:**
            - **CPU:** Multi-core processor (4+ cores)
            - **RAM:** 8GB+ for model inference
            - **Storage:** 2GB+ for model and dependencies
            - **GPU:** Optional (for training)
            """)
        
        with col2:
            st.markdown("""
            **Deployment Details:**
            - **Platform:** Streamlit Cloud
            - **URL:** [Live Application](https://cottoncropdiseasedetectionusingml-atqc2jc4hspduogmtztcmn.streamlit.app/)
            - **Repository:** GitHub (Cotton_crop_disease_detection_using_ML)
            - **License:** Open Source
            
            **Features:**
            - Real-time disease detection
            - Confidence score analysis
            - Prediction history tracking
            - Comprehensive analytics dashboard
            - Downloadable reports
            - Mobile-responsive design
            """)
        
        st.markdown("---")
        
        # Future improvements
        st.markdown("""
        **🚀 Future Enhancements:**
        - Integration with IoT sensors for automated monitoring
        - Mobile application development
        - Multi-language support
        - Integration with farming management systems
        - Advanced analytics and recommendations
        - Real-time alerts and notifications
        """)
    
    # Contact and support
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #e8f5e8; padding: 2rem; border-radius: 10px; text-align: center;">
        <h3>📞 Support & Contact</h3>
        <p>For questions, feedback, or collaboration opportunities:</p>
        <p>📧 <strong>Email:</strong> team@cottondetection.ai</p>
        <p>🐙 <strong>GitHub:</strong> <a href="https://github.com/akkkshat07/Cotton_crop_disease_detection_using_ML">Project Repository</a></p>
        <p>🌐 <strong>Live Demo:</strong> <a href="https://cottoncropdiseasedetectionusingml-atqc2jc4hspduogmtztcmn.streamlit.app/">Try the App</a></p>
    </div>
    """, unsafe_allow_html=True)
