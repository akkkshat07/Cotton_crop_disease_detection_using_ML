import streamlit as st
import tensorflow as tf
import numpy as np
import json
import hashlib
import os
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image


USERS_FILE = "users.json"
HISTORY_FILE = "history.json"


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)


try:
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trained_cotton_disease_model.h5")
    model = tf.keras.models.load_model(model_path)
except Exception as e:
    st.error(f"Error loading model: {e}")
    model = None


def model_prediction(test_image):
    if model is None:
        st.error("Model is not loaded.")
        return None
    
    image = Image.open(test_image).convert('RGB')
    image = image.resize((128, 128))
    input_arr = np.array(image)
    input_arr = np.expand_dims(input_arr, axis=0) 
    predictions = model.predict(input_arr)
    return np.argmax(predictions)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


st.sidebar.title("Dashboard")

if not st.session_state.logged_in:
    app_mode = st.sidebar.selectbox("Select Page", ["Login/Register", "About"])
else:
    app_mode = st.sidebar.selectbox("Select Page", ["Home", "About", "Disease Recognition", "History", "Logout"])


if app_mode == "Login/Register":
    st.header("Login or Register")

    users = load_users()

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if login_username in users and users[login_username] == hashlib.sha256(login_password.encode()).hexdigest():
                st.success("Logged in successfully!")
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

    with register_tab:
        reg_username = st.text_input("Choose a Username", key="reg_username")
        reg_password = st.text_input("Choose a Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
        if st.button("Register"):
            if reg_username in users:
                st.error("Username already exists")
            elif reg_password != reg_password_confirm:
                st.error("Passwords do not match")
            elif len(reg_username) == 0 or len(reg_password) == 0:
                st.error("Username and password cannot be empty")
            else:
                users[reg_username] = hashlib.sha256(reg_password.encode()).hexdigest()
                save_users(users)
                st.success("Registration successful! Please login.")
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.experimental_rerun()

elif app_mode == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("Logged out successfully!")
    st.experimental_rerun()


elif st.session_state.logged_in:
    if app_mode == "Home":
        st.header("COTTON CROP DISEASE RECOGNITION SYSTEM")
        image_path = "home_page.png"
        if os.path.exists(image_path):
            st.image(image_path, use_column_width=True)
        st.markdown(
            """
            Welcome to the Cotton Leaf Disease Detection System! 🌿🔍
            
            Our mission is to help in identifying cotton crop diseases efficiently. Upload an image, and our system will analyze it to detect any signs of diseases. Together, let's protect our cotton crops and ensure a healthier harvest!

            ### How It Works
            1. **Upload Image:** Go to the **Disease Recognition** page and upload an image of a plant with suspected diseases.
            2. **Analysis:** Our system will process the image using advanced algorithms to identify potential diseases.
            3. **Results:** View the results and recommendations for further action.

            ### Why Choose Us?
            - **Accuracy:** Our system utilizes state-of-the-art machine learning techniques for accurate disease detection.
            - **User-Friendly:** Simple and intuitive interface for seamless user experience.
            - **Fast and Efficient:** Receive results in seconds, allowing for quick decision-making.

            ### Get Started
            Click on the **Disease Recognition** page in the sidebar to upload an image and experience the power of our cotton Disease Recognition System!

            ### About Us
            Learn more about the project and our goals on the **About** page.
            """
        )

    elif app_mode == "About":
        st.header("About")
        st.markdown(
            """
            #### About Dataset
            This dataset is recreated using offline augmentation from the original dataset. The original dataset can be found on this GitHub repo.
            This dataset consists of about 6.2K RGB images of healthy and diseased crop leaves, categorized into 9 different classes. The total dataset is divided into 80/20 ratio of training and validation set preserving the directory structure.
            
            #### Content
            1. Train (6251 images)
            2. Validation (1563 images)
            
            #### Project Goals
            - **Early Disease Detection:** Identify cotton crop diseases at an early stage to prevent crop loss
            - **Sustainable Farming:** Promote sustainable agricultural practices through timely interventions
            - **Reduce Chemical Usage:** Help farmers minimize pesticide use by enabling targeted treatments
            - **Increase Crop Yield:** Improve overall cotton production by maintaining plant health
            - **Education:** Raise awareness about common cotton crop diseases and their symptoms
            - **Accessibility:** Make advanced disease detection technology accessible to farmers of all scales

            #### Developed by Akshat 
            """
        )

    elif app_mode == "Disease Recognition":
        st.header("Disease Recognition")
        test_image = st.file_uploader("Choose an Image:")
        
        if test_image is not None:
            st.image(test_image, use_column_width=True, caption="Uploaded Image")
            
            if st.button("Predict"):
                st.snow()
                st.write("Our Prediction:")
                result_index = model_prediction(test_image)
                
                if result_index is not None:
                    class_name = [
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
                    
                    prediction_label = class_name[result_index]
                    st.success(f"Model is Predicting it's a {prediction_label}")

                    # Save prediction to history
                    history = load_history()
                    user_history = history.get(st.session_state.username, [])
                    user_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "prediction": prediction_label
                    })
                    history[st.session_state.username] = user_history
                    save_history(history)

    elif app_mode == "History":
        st.header("Prediction History")
        st.markdown("### Your Cotton Disease Detection Records")
        history = load_history()
        user_history = history.get(st.session_state.username, [])
        
        if user_history:
            
            total_predictions = len(user_history)
            
            
            prediction_counts = {}
            for record in user_history:
                prediction = record["prediction"]
                if prediction in prediction_counts:
                    prediction_counts[prediction] += 1
                else:
                    prediction_counts[prediction] = 1
            
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Predictions", total_predictions)
            with col2:
                most_common = max(prediction_counts.items(), key=lambda x: x[1])[0] if prediction_counts else "None"
                st.metric("Most Common Result", most_common)
            
           
            st.markdown("### Filter Your Results")
            filter_col1, filter_col2 = st.columns(2)
            
            with filter_col1:
               
                prediction_types = list(set([record["prediction"] for record in user_history]))
                selected_type = st.selectbox("Filter by Disease Type", ["All"] + prediction_types)
            
            with filter_col2:
                
                date_options = ["All Time", "Last 7 Days", "Last 30 Days"]
                date_filter = st.selectbox("Time Period", date_options)
            
           
            filtered_history = user_history
            
            
            if selected_type != "All":
                filtered_history = [record for record in filtered_history if record["prediction"] == selected_type]
            
            
            if date_filter != "All Time":
                current_date = datetime.now()
                days = 7 if date_filter == "Last 7 Days" else 30
                cutoff_date = current_date - datetime.timedelta(days=days)
                filtered_history = [
                    record for record in filtered_history 
                    if datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S") > cutoff_date
                ]
            
            
            st.markdown("### Detailed History")
            
            if not filtered_history:
                st.info("No records match your filter criteria.")
            else:
                
                history_df = {
                    "Date": [],
                    "Time": [],
                    "Prediction": [],
                    "Status": []
                }
                
                for record in reversed(filtered_history):
                    timestamp = datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S")
                    date_str = timestamp.strftime("%Y-%m-%d")
                    time_str = timestamp.strftime("%H:%M:%S")
                    prediction = record["prediction"]
                    status = "Healthy" if prediction == "Healthy" else "Infected"
                    
                    history_df["Date"].append(date_str)
                    history_df["Time"].append(time_str)
                    history_df["Prediction"].append(prediction)
                    history_df["Status"].append(status)
                
                df = pd.DataFrame(history_df)
                
                
                def color_status(val):
                    color = 'green' if val == 'Healthy' else 'red'
                    return f'background-color: {color}; color: white'
                
                
                st.dataframe(
                    df.style.map(color_status, subset=['Status']),  # Updated from applymap to map
                    use_container_width=True  # Removed unsupported hide_index argument
                )
                
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download History as CSV",
                    data=csv,
                    file_name="cotton_disease_detection_history.csv",
                    mime="text/csv",
                )
        else:
            st.info("No prediction history found. Go to the Disease Recognition page to analyze cotton images.")
            st.markdown("""
                **How to get started:**
                1. Navigate to the Disease Recognition page
                2. Upload an image of a cotton plant
                3. Click "Predict" to analyze the image
                4. Your results will appear in your history
            """)

else:
    st.header("Please login to access the application.")