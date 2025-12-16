import streamlit as st
import os
import json
import PyPDF2 as pdf
from dotenv import load_dotenv
from google import genai
from db import reports_collection

# Streamlit config
st.set_page_config(page_title="Resume Screening System", page_icon=":briefcase:", layout="wide")

# Load environment variables
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# PDF text extractor
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += str(page.extract_text())
    return text

# Gemini API call
def get_gemini_response(resume_text, jd_text):
    prompt = f"""
You are an ATS (Applicant Tracking System).

Return ONLY valid JSON in this exact format:
{{
  "JD Match": "percentage%",
  "MissingKeywords": [],
  "Profile Summary": ""
}}

Resume:
{resume_text}

Job Description:
{jd_text}
"""
    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )
        return response.text.strip()

    except Exception as e:
        return json.dumps({
            "JD Match": "0%",
            "MissingKeywords": [],
            "Profile Summary": str(e)
        })

# Custom Header
def custom_header():
    st.markdown("""
        <style>
            .header {
                background-color: #003366;
                color: white;
                padding: 30px;
                text-align: center;
                font-size: 50px;
                font-weight: bold;
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            }
        </style>
        """, unsafe_allow_html=True)
    st.markdown('<div class="header">Welcome to the Resume Screening System</div>', unsafe_allow_html=True)

# Hero Section
def hero_section():
    st.markdown("""
    <style>
        .hero-section {
            font-weight: bold;
            font-size: 20px;
            color: black;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="hero-section">This tool analyzes your resume against a job description and highlights match percentage, missing keywords, and suggestions.</div>', unsafe_allow_html=True)

# Save report to collection
def save_report(uploaded_file, job_description, parsed):
    from datetime import datetime
    report = {
        "user_email": st.session_state.user_email,
        "resume_name": uploaded_file.name,
        "job_description": job_description,
        "jd_match": parsed.get("JD Match"),
        "missing_keywords": parsed.get("MissingKeywords"),
        "profile_summary": parsed.get("Profile Summary"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    reports_collection.insert_one(report)

# Upload Section
def upload_section():
    st.markdown('<h2>Upload Your Resume and Job Description</h2>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"], key="resume_upload")
    job_description = st.text_area("Enter Job Description (Plain Text)", height=200, key="jd_input")
    submit = st.button("Submit", key="submit_resume")

    if submit:
        if uploaded_file is None or job_description.strip() == "":
            st.warning("Please upload a resume and enter a job description.")
            return

        with st.spinner("Analyzing..."):
            resume_text = input_pdf_text(uploaded_file)
            response = get_gemini_response(resume_text, job_description)

            try:
                parsed = json.loads(response)
            except Exception:
                st.error("Gemini response was not valid JSON")
                st.subheader("Raw Response:")
                st.write(response)
                return

            st.subheader("📊 Screening Result")
            st.metric("JD Match", parsed.get("JD Match", "N/A"))
            st.write("**Missing Keywords:**", parsed.get("MissingKeywords", []))
            st.write("**Profile Summary:**")
            st.write(parsed.get("Profile Summary", ""))

            # Save user-specific report
            save_report(uploaded_file, job_description, parsed)

# User History Page
def show_user_history():
    st.subheader("📜 My Resume Screening History")
    reports = list(
        reports_collection.find({"user_email": st.session_state.user_email}).sort("created_at", -1)
    )
    if not reports:
        st.info("No history found.")
        return

    for report in reports:
        with st.expander(f"{report['resume_name']} | {report['created_at']}"):
            st.metric("JD Match", report["jd_match"])
            st.write("**Missing Keywords:**", report["missing_keywords"])
            st.write("**Profile Summary:**")
            st.write(report["profile_summary"])

# Main Function with Navigation
def main():
    if "user_email" not in st.session_state:
        st.warning("You must be logged in to access this page.")
        return

    custom_header()
    hero_section()

    # Logout button at top-right
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("Logout", key="logout_main"):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.current_page = "Login_Register"
            st.rerun()

    # Horizontal navigation using tabs
    tab1, tab2 = st.tabs(["New Resume Analysis", "My History"])

    with tab1:
        upload_section()

    with tab2:
        show_user_history()


if __name__ == "__main__":
    main()
