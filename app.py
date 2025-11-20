import streamlit as st
from sentence_transformers import SentenceTransformer
import base64
from streamlit_pdf_viewer import pdf_viewer

import os 
import re 

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
 
    st.stop()


st.set_page_config(page_title="TalentTune", layout="wide")

def clean_output_text(text):
    """Removes job start/end markers and triple dashes from AI output."""
   
    text = re.sub(r'---JOB\s+(START|END)---|^\s*---\s*$', '', text, flags=re.MULTILINE)
    return text.strip()


def display_user_guide():
    """Displays guidelines focusing on PII related to images."""
    st.markdown("---")
    st.markdown("## Resume Upload Guidelines")
    st.info("""
    ** PII Warning:** Please ensure you **remove all candidate images, photos, or headshots** from your resume before uploading. These are considered **Personal Identifiable Information (PII)** and can interfere with the data extraction process.
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

    if "t1_resume_text" not in st.session_state: st.session_state.t1_resume_text = ""

    if uploaded_file:
        try:
            
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
            
          
            if st.button("Format Resume", key="format_btn_1"):
                with st.spinner("Formatting... (Template 1)"):
                    api_key = st.secrets.get("PORTKEY_API_KEY")
                    base_url = st.secrets.get("PORTKEY_BASE_URL")
                    prompt = t1_prompt(st.session_state.t1_resume_text)
                    
                    formatted_resume = t1_call_portkey(prompt,
                                                 portkey_api_key=api_key,
                                                 portkey_base_url=base_url
                                                                    ) 
                    
                    st.session_state.formatted_resume_1 = formatted_resume

            if st.session_state.formatted_resume_1:
                
                cleaned_output = clean_output_text(st.session_state.formatted_resume_1)
              
                file_buffer, candidate_name = t1_convert_to_docx(st.session_state.formatted_resume_1)
                file_size_kb = len(file_buffer.getvalue()) / 1024
                
                st.subheader(" DOCX Content Preview (Structured Text)")
                st.markdown(cleaned_output)

                file_name_safe = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '_')).rstrip()
                dynamic_file_name = f"{file_name_safe}_PRFT_Resume_T1.docx"
                
                st.success(f"Document ready! File size: {file_size_kb:.2f} KB")

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

    # Session state to store the extracted text needed for processing
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

            # --- Format Button (Removed regeneration logic) ---
            if st.button("Format Resume", key="format_btn_2"):
                with st.spinner("Formatting... (Template 2)"):
                    api_key = st.secrets.get("PORTKEY_API_KEY")
                    base_url = st.secrets.get("PORTKEY_BASE_URL")
                    prompt = t2_prompt(st.session_state.t2_resume_text)
                    formatted_resume = t2_call_portkey(prompt,
                                                 portkey_api_key=api_key,
                                                 portkey_base_url=base_url
                                                                    ) 
                    st.session_state.formatted_resume_2 = formatted_resume

            if st.session_state.formatted_resume_2:
                
                
                cleaned_output = clean_output_text(st.session_state.formatted_resume_2)
                
               
                file_buffer, candidate_name = t2_convert_to_docx(st.session_state.formatted_resume_2)
                file_size_kb = len(file_buffer.getvalue()) / 1024

              
                st.subheader(" DOCX Content Preview (Structured Text)")
                st.markdown(cleaned_output)

                file_name_safe = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '_')).rstrip()
                dynamic_file_name = f"{file_name_safe}_PRFT_Resume_T2.docx"
                
                st.success(f" Document ready! File size: {file_size_kb:.2f} KB")

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
    
    if not os.path.isfile(main_bg):
        st.warning(f"Background image '{main_bg}' not found. Skipping background.")
        return

    try:
        
        with open(main_bg, "rb") as f:
            base664_image = base64.b64encode(f.read()).decode()
            
        st.markdown(
             f"""
             <style>
             .stApp {{
                 background: url(data:image/{main_bg_ext};base64,{base64_image});
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