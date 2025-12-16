import streamlit as st
from Login_Register import render_Login_Register
from app import main as render_app
import base64
import os

# PAGE CONFIG 
st.set_page_config(
    page_title="Resume Screening System",
    page_icon="🌟",
    layout="centered"
)



# BACKGROUND HELPERS 
def get_base64_image(image_path):
    with open(image_path, "rb") as file:
        return base64.b64encode(file.read()).decode()

def apply_landing_background():
    image_path = "C:/Users/Anjali Bariya/OneDrive/Desktop/Resume Screening System/Images_folder/pexels-codioful-6984984.jpg"
    if os.path.exists(image_path):
        base64_image = get_base64_image(image_path)
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{base64_image}");
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

def reset_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

#  SESSION STATE
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing_page"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# LANDING PAGE 
def render_landing_page():
    apply_landing_background()

    st.markdown(
        """
        <h1 style="font-size:20px; text-align:center; color:white">
            RESUME SCREENING SYSTEM
        </h1>

        <h2 style="font-size:40px; text-align:center; color:white">
            Optimize Your Resume. Maximize Your Opportunities.
        </h2>

        <p style="font-size:25px; text-align:center; color:white">
            Free to use. Easy to try.
        </p>
        """,
        unsafe_allow_html=True
    )

    if st.button("Get Started"):
        st.session_state.current_page = "Login_Register"
        st.rerun()

# Logout 
def logout_button():
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_page = "landing_page"
            st.rerun()


# PAGE ROUTING 
if st.session_state.current_page == "landing_page":
    render_landing_page()

elif st.session_state.current_page == "Login_Register":
    apply_landing_background()
    render_Login_Register()

elif st.session_state.current_page == "app":
    if st.session_state.logged_in:
        reset_background()
        logout_button()  
        render_app()
    else:
        st.session_state.current_page = "Login_Register"
        st.rerun()
