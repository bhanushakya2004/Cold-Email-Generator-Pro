import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
import fitz  # PyMuPDF

# Page config
st.set_page_config(
    page_title="Cold Email Generator",
    page_icon="📧",
    layout="centered"
)

# --- CSS Styling ---
st.markdown("""
<style>
    body {
        color: #001524;
        background-color: #AFCBD5;
    }

    .main-title {
        text-align: center;
        color: #445D48;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: #5E3023;
        margin-top: -10px;
        font-size: 1rem;
    }

    .step-box {
        background-color: #D6CC99;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
        color: #001524;
        font-weight: 500;
    }

    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 6px;
        margin-top: 1rem;
        color: #001524;
    }

    .error-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        border-radius: 6px;
        margin-top: 1rem;
        color: #001524;
    }

    .stTextInput > div > input, .stTextArea > div > textarea {
        background-color: #FDE5D4 !important;
        color: #001524 !important;
        border-radius: 8px !important;
    }

    .stDownloadButton, .stButton {
        border-radius: 8px !important;
        font-weight: 600 !important;
        background-color: #445D48 !important;
        color: white !important;
        border: none !important;
    }

    .stDownloadButton:hover, .stButton:hover {
        background-color: #5E3023 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<h1 class="main-title">📧 Cold Email Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Generate personalized cold emails for job applications</p>', unsafe_allow_html=True)

# --- Step 1: Job Info ---
st.markdown('<div class="step-box"><h4>🔗 Step 1: Job Information</h4></div>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📎 Job URL", "📝 Manual Input"])

with tab1:
    url_input = st.text_input("Paste job posting URL:", placeholder="https://company.com/careers/job-title")

with tab2:
    manual_job_text = st.text_area("Paste job description:", height=200, placeholder="Copy and paste the job post here...")

# --- Step 2: Resume Upload ---
st.markdown('<div class="step-box"><h4>📄 Step 2: Upload Resume (PDF)</h4></div>', unsafe_allow_html=True)
resume_file = st.file_uploader("Choose your resume (PDF only)", type=["pdf"])

# --- Step 3: Additional Info ---
st.markdown('<div class="step-box"><h4>✨ Step 3: Extra Info (Optional)</h4></div>', unsafe_allow_html=True)
extra_input = st.text_area("Add additional info (e.g. portfolio, achievements, etc):", height=100)

# --- Generate Button ---
generate_btn = st.button("🚀 Generate Cold Email", type="primary", use_container_width=True)

# --- Helpers ---
@st.cache_data
def extract_resume_text(uploaded_file):
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        resume_text = "".join([page.get_text() for page in doc])
        doc.close()
        return resume_text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def get_job_content():
    if manual_job_text and manual_job_text.strip():
        return manual_job_text.strip()
    elif url_input:
        try:
            loader = WebBaseLoader([url_input])
            content = loader.load()[0].page_content
            return content
        except Exception as e:
            st.error(f"Could not fetch URL: {str(e)}")
            st.info("💡 Try using the Manual Input tab instead")
            return None
    return None

# --- Main Logic ---
if generate_btn:
    job_content = get_job_content()

    if not job_content:
        st.markdown('<div class="error-box">❌ Please provide job info (URL or manual input)</div>', unsafe_allow_html=True)
    elif not resume_file:
        st.markdown('<div class="error-box">❌ Please upload your resume</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Generating cold email..."):
            try:
                resume_text = extract_resume_text(resume_file)
                if not resume_text:
                    st.error("Failed to read resume. Please check your PDF file.")
                    st.stop()

                user_data = {
                    "resume_text": resume_text,
                    "additional_info": extra_input or ""
                }

                llm = Chain()
                job_info = llm.extract_jobs(job_content)

                if job_info:
                    st.markdown('<div class="success-box">✅ Email generated successfully!</div>', unsafe_allow_html=True)
                    
                    job = job_info[0]
                    st.subheader("📋 Job Details")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Position:**", job.get('title', 'N/A'))
                        st.write("**Company:**", job.get('company', 'N/A'))
                    with col2:
                        st.write("**Location:**", job.get('location', 'N/A'))

                    email_content = llm.write_mail(job, user_data)
                    st.subheader("✉️ Your Cold Email")
                    st.text_area("Generated Email:", value=email_content, height=400)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button("💾 Download Email", email_content, file_name="cold_email.txt", mime="text/plain")
                    with col2:
                        if st.button("🔄 Generate Another"):
                            st.rerun()
                else:
                    st.error("Could not extract job details. Try a different job post.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #5E3023;">
    <p>Built with ❤️ using Streamlit & LangChain by Bhanu Shakya</p>
</div>
""", unsafe_allow_html=True)
