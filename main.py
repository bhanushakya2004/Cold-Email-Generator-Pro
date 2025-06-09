import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
import fitz  # PyMuPDF
import re

# Page configuration
st.set_page_config(
    page_title="Cold Email Generator",
    page_icon="📧",
    layout="centered"
)

# Simple CSS styling
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2E86AB;
        padding: 1rem 0;
    }
    
    .step-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    
    .error-box {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">📧 Cold Email Generator</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Generate personalized cold emails for job applications</p>', unsafe_allow_html=True)

# Step 1: Job Input
st.markdown("""
<div class="step-box">
    <h3>🔗 Step 1: Job Information</h3>
</div>
""", unsafe_allow_html=True)

# Tabs for URL vs Manual input
tab1, tab2 = st.tabs(["📎 Job URL", "📝 Manual Input"])

with tab1:
    url_input = st.text_input(
        "Paste job posting URL:",
        placeholder="https://company.com/careers/job-title"
    )

with tab2:
    manual_job_text = st.text_area(
        "Paste job description:",
        height=200,
        placeholder="Copy and paste the complete job posting here..."
    )

# Step 2: Resume Upload
st.markdown("""
<div class="step-box">
    <h3>📄 Step 2: Upload Resume</h3>
</div>
""", unsafe_allow_html=True)

resume_file = st.file_uploader("Choose your resume (PDF only)", type=["pdf"])

# Step 3: Additional Info
st.markdown("""
<div class="step-box">
    <h3>✨ Step 3: Extra Info (Optional)</h3>
</div>
""", unsafe_allow_html=True)

extra_input = st.text_area(
    "Add any additional information:",
    placeholder="• Portfolio links\n• Key achievements\n• Relevant projects",
    height=100
)

# Generate Button
st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("🚀 Generate Cold Email", type="primary", use_container_width=True)

# Helper Functions
@st.cache_data
def extract_resume_text(uploaded_file):
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        resume_text = ""
        for page in doc:
            resume_text += page.get_text()
        doc.close()
        return resume_text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def get_job_content():
    """Get job content from URL or manual input"""
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

# Main Processing
if generate_btn:
    # Validation
    job_content = get_job_content()
    
    if not job_content:
        st.markdown('<div class="error-box">❌ Please provide job information (URL or manual input)</div>', unsafe_allow_html=True)
    elif not resume_file:
        st.markdown('<div class="error-box">❌ Please upload your resume</div>', unsafe_allow_html=True)
    else:
        # Processing
        with st.spinner("Processing..."):
            try:
                # Extract resume
                resume_text = extract_resume_text(resume_file)
                if not resume_text:
                    st.error("Failed to read resume. Please check your PDF file.")
                    st.stop()
                
                # Prepare data
                user_data = {
                    "resume_text": resume_text,
                    "additional_info": extra_input or ""
                }
                
                # Extract job info and generate email
                llm = Chain()
                job_info = llm.extract_jobs(job_content)
                
                if job_info:
                    # Success message
                    st.markdown('<div class="success-box">✅ Email generated successfully!</div>', unsafe_allow_html=True)
                    
                    # Show job info
                    st.subheader("📋 Job Details")
                    job = job_info[0]  # Use first job
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Position:**", job.get('title', 'N/A'))
                        st.write("**Company:**", job.get('company', 'N/A'))
                    with col2:
                        st.write("**Location:**", job.get('location', 'N/A'))
                    
                    # Generate and show email
                    st.subheader("✉️ Your Cold Email")
                    email_content = llm.write_mail(job, user_data)
                    
                    # Display email in a text area for easy copying
                    st.text_area(
                        "Generated Email:",
                        value=email_content,
                        height=400,
                        help="You can copy this email and use it directly"
                    )
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "💾 Download Email",
                            email_content,
                            file_name="cold_email.txt",
                            mime="text/plain"
                        )
                    with col2:
                        if st.button("🔄 Generate Another"):
                            st.rerun()
                
                else:
                    st.error("Could not extract job information. Please try a different job posting.")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please try again or check your inputs.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>Built with ❤️ using Streamlit & LangChain</p>
</div>
""", unsafe_allow_html=True)