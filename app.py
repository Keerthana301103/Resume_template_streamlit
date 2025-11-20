import streamlit as st
from sentence_transformers import SentenceTransformer
import base64
from streamlit_pdf_viewer import pdf_viewer

import os 
import re # <-- Added import for regex cleaning

try:
    from template_2 import (
        extract_text_from_pdf as t2_extract_pdf,
        extract_text_from_docx as t2_extract_docx,
        prompt as t2_prompt,
        call_portkey_api as t2_call_portkey,
        convert_to_docx as t2_convert_to_docx,
    )
    from template_1 import (
        extract_text_from_pdf as t1_extract_pdf,
        extract_text_from_docx as t1_extract_docx,
        prompt as t1_prompt,
        call_portkey_api as t1_call_portkey,
        convert_to_docx as t1_convert_to_docx,
    )
except ImportError:
    st.error("Could not import from template_1.py or template_2.py. Make sure those files are in your GitHub repository.")
    # Stop the app if core files are missing
    st.stop()


st.set_page_config(page_title="TalentTune", layout="wide")

# --- NEW HELPER FUNCTION TO CLEAN AI OUTPUT ---
def clean_output_text(text):
    """Removes job start/end markers and triple dashes from AI output."""
    # Pattern to match '---JOB START---', '---JOB END---', and other '---' lines
    text = re.sub(r'---JOB\s+(START|END)---|^\s*---\s*$', '', text, flags=re.MULTILINE)
    return text.strip()
# ---------------------------------------------


def display_user_guide():
    """Displays guidelines for users before uploading resumes."""
    st.markdown("---")
    st.markdown("## 📋 Resume Upload Guidelines & Privacy")
    st.info("""
    **Before uploading your resume, please ensure the following:**
    
    1.  **Remove Images:** **Crucially, delete any photos, headshots, or candidate images** from the document. The AI extractor may struggle with embedded images, and we prioritize text-only processing for consistency and privacy.
    2.  **Clean Layout:** Use a clean, simple layout for best extraction results. Complex graphics, excessive tables, or multi-column layouts may lead to errors.
    3.  **Check PII:** While our system attempts to clean PII (like emails and phone numbers) before processing, please review your document to ensure sensitive personal data is minimized.
    """)
    st.markdown("---")

def template_1():
    st.write("Old Template Format:")
    pdf_viewer(
    "ui/sample_template-1.pdf",
    width=700,
    height=250,
    zoom_level=1.2,
    viewer_align="center",
    show_page_separator=True,
    key="pdf_viewer_t1"
)
    st.markdown("<h3 style='color: rgb(186, 43, 43);'> Format Resume to Company Template (Old)</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"], key="formatter-1")

    # Session state to store the extracted text needed for regeneration
    if "t1_resume_text" not in st.session_state: st.session_state.t1_resume_text = ""

    if uploaded_file:
        try:
            # --- Text Extraction Logic ---
            if uploaded_file.type == "application/pdf":
                resume_text = t1_extract_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = t1_extract_docx(uploaded_file)
            else:
                st.error("Unsupported file type.")
                return
            st.session_state.t1_resume_text = resume_text

            st.subheader("Extracted Resume Text")
            st.text_area("Resume Content (First 1000 Chars)", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, height=150, key="text_1")

            if "formatted_resume_1" not in st.session_state:
                st.session_state.formatted_resume_1 = ""
            
            # --- Define the formatting logic as a reusable function ---
            def run_t1_formatting():
                api_key = st.secrets.get("PORTKEY_API_KEY")
                base_url = st.secrets.get("PORTKEY_BASE_URL")
                prompt = t1_prompt(st.session_state.t1_resume_text)
                
                return t1_call_portkey(prompt,
                                     portkey_api_key=api_key,
                                     portkey_base_url=base_url)

            # --- Initial Format Button ---
            if st.button("Format Resume", key="format_btn_1"):
                with st.spinner("Formatting... (Template 1)"):
                    formatted_resume = run_t1_formatting()
                    st.session_state.formatted_resume_1 = formatted_resume

            if st.session_state.formatted_resume_1:
                
                # --- Regeneration Button ---
                if st.button("🔄 Regenerate Formatted Text", key="regenerate_btn_1"):
                    with st.spinner("Regenerating... (Template 1)"):
                        formatted_resume = run_t1_formatting()
                        st.session_state.formatted_resume_1 = formatted_resume
                
                # --- PREVIEW AND DOWNLOAD SECTION ---
                cleaned_output = clean_output_text(st.session_state.formatted_resume_1)
                
                # The docx conversion must use the original uncleaned text
                file_buffer, candidate_name = t1_convert_to_docx(st.session_state.formatted_resume_1)
                file_size_kb = len(file_buffer.getvalue()) / 1024
                
                # 1. Structured Text Preview (Cleaned output)
                st.subheader("📝 DOCX Content Preview (Structured Text)")
                st.markdown(cleaned_output)

                # 2. Download Button
                file_name_safe = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '_')).rstrip()
                dynamic_file_name = f"{file_name_safe}_PRFT_Resume_T1.docx"
                
                st.success(f"✅ Document ready! File size: {file_size_kb:.2f} KB")

                st.download_button(
                    "Download Final DOCX",
                    file_buffer,
                    dynamic_file_name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
        except Exception as e:
            st.error(f"An error occurred in Template 1: {e}")
            st.warning("Ensure your API key is set in Streamlit secrets and your template_1.py file is correct.")


def template_2():
    st.write("New Template Format:")
    pdf_viewer(
    "ui/sample_template-2.pdf",
    width=700,
    height=250,
    zoom_level=1.2,
    viewer_align="center",
    show_page_separator=True,
    key="pdf_viewer_t2"
)
    st.markdown("<h3 style='color: rgb(186, 43, 43);'> Format Resume to Company Template (New Template)</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"], key="formatter-2")

    # Session state to store the extracted text needed for regeneration
    if "t2_resume_text" not in st.session_state: st.session_state.t2_resume_text = ""

    if uploaded_file:
        try:
            # --- Text Extraction Logic ---
            if uploaded_file.type == "application/pdf":
                resume_text = t2_extract_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = t2_extract_docx(uploaded_file)
            else:
                st.error("Unsupported file type.")
                return
            st.session_state.t2_resume_text = resume_text

            st.subheader("Extracted Resume Text")
            st.text_area("Resume Content (First 1000 Chars)", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, height=150, key="text_2")

            if "formatted_resume_2" not in st.session_state:
                st.session_state.formatted_resume_2 = ""

            # --- Define the formatting logic as a reusable function ---
            def run_t2_formatting():
                api_key = st.secrets.get("PORTKEY_API_KEY")
                base_url = st.secrets.get("PORTKEY_BASE_URL")
                prompt = t2_prompt(st.session_state.t2_resume_text)
                
                return t2_call_portkey(prompt,
                                     portkey_api_key=api_key,
                                     portkey_base_url=base_url)

            # --- Initial Format Button ---
            if st.button("Format Resume", key="format_btn_2"):
                with st.spinner("Formatting... (Template 2)"):
                    formatted_resume = run_t2_formatting()
                    st.session_state.formatted_resume_2 = formatted_resume

            if st.session_state.formatted_resume_2:
                
                # --- Regeneration Button ---
                if st.button("🔄 Regenerate Formatted Text", key="regenerate_btn_2"):
                    with st.spinner("Regenerating... (Template 2)"):
                        formatted_resume = run_t2_formatting()
                        st.session_state.formatted_resume_2 = formatted_resume

                # --- PREVIEW AND DOWNLOAD SECTION ---
                cleaned_output = clean_output_text(st.session_state.formatted_resume_2)
                
                # The docx conversion must use the original uncleaned text
                file_buffer, candidate_name = t2_convert_to_docx(st.session_state.formatted_resume_2)
                file_size_kb = len(file_buffer.getvalue()) / 1024

                # 1. Structured Text Preview (Cleaned output)
                st.subheader("📝 DOCX Content Preview (Structured Text)")
                st.markdown(cleaned_output)

                # 2. Download Button
                file_name_safe = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '_')).rstrip()
                dynamic_file_name = f"{file_name_safe}_PRFT_Resume_T2.docx"
                
                st.success(f"✅ Document ready! File size: {file_size_kb:.2f} KB")

                st.download_button(
                    "Download Final DOCX",
                    file_buffer,
                    dynamic_file_name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        except Exception as e:
            st.error(f"An error occurred in Template 2: {e}")
            st.warning("Make sure your PORTKEY_API_KEY is set in Streamlit secrets and your template_2.py file is correct.")


def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
    '''
    # set bg name
    main_bg_ext = "jpg"
    
    # Check if file exists
    if not os.path.isfile(main_bg):
        st.warning(f"Background image '{main_bg}' not found. Skipping background.")
        return

    try:
        # Use base64 encoding to embed the image
        with open(main_bg, "rb") as f:
            base664_image = base64.b64encode(f.read()).decode()
            
        st.markdown(
             f"""
             <style>
             .stApp {{
                 background: url(data:image/{main_bg_ext};base64,{base664_image});
                 background-size: cover
             }}
             </style>
             """,
             unsafe_allow_html=True
         )
    except Exception as e:
        st.warning(f"Error setting background: {e}")


def main():
    
    set_bg_hack('ui/bg_final.jpg') 
    st.markdown(
    "<h1 style='color:rgb(186, 43, 43); font-weight: bold; text-align: center;'>TalentTune</h1>",
    unsafe_allow_html=True
)
    st.markdown(
    "<p style='text-align: center; font-size:18px;'><em>Fine-tune your profile for job success.</em></p>",
    unsafe_allow_html=True
)
    
    display_user_guide()

    tab1, tab2 = st.tabs(["Old Template", "New Template"]) 

    with tab1:
        template_1()

    with tab2:
        template_2()

    # Footer
    st.markdown("<hr style='margin-top: 50px;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>Powered by ModelMinds</p>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()