import streamlit as st
import bcrypt
from db import users_collection 

st.markdown("""
<style>

.css-1fv8s86.e16nr0p30 {  
    color: #000000;
    font-weight: bold;
}

/* Text input labels darker */
div[data-baseweb="form-control"] label {
    color: #000000 !important;
    font-weight: 600;
}

/* Button styling */
.stButton>button {
    background-color: #4CAF50;
    color: white;
    font-weight: bold;
    width: 100%;
}

.stButton>button:hover {
    background-color: #45a049;
    color: white;
}
</style>
""", unsafe_allow_html=True)

def render_Login_Register():
    tab1, tab2 = st.tabs(["Register", "Login"])

    # REGISTER
    with tab1:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register"):
            if email and password:
                if users_collection.find_one({"email": email}):
                    st.warning("User already exists!")
                else:
                    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                    users_collection.insert_one({"email": email, "password": hashed_password})
                    st.success("User registered successfully!")

    # LOGIN
    with tab2:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            user = users_collection.find_one({"email": email})
            if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
                st.session_state.logged_in = True
                st.session_state.user_email = email   
                st.session_state.current_page = "app"
                st.rerun()
            else:
                st.error("Invalid email or password")
