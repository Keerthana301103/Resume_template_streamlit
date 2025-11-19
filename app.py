import streamlit as st
from sentence_transformers import SentenceTransformer
import base64
from streamlit_pdf_viewer import pdf_viewer

import os 

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

def template_1():
    st.write("Old Template Format:")
    pdf_viewer(
    "sample_template-1.pdf",
    width=700,
    height=250,
    zoom_level=1.2,                   
    viewer_align="center",             
    show_page_separator=True,
    key="pdf_viewer_t1"# Show separators between pages
)
    st.markdown("<h3 style='color: rgb(186, 43, 43);'> Format Resume to Company Template (Old)</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"], key="formatter-1")

    if uploaded_file:
        try:
            if uploaded_file.type == "application/pdf":
                resume_text = t1_extract_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = t1_extract_docx(uploaded_file)
            else:
                st.error("Unsupported file type.")
                return

            st.subheader("Extracted Resume Text")
            st.text_area("Resume Content (First 1000 Chars)", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, height=150, key="text_1")

            if "formatted_resume_1" not in st.session_state:
                st.session_state.formatted_resume_1 = ""

            if st.button("Format Resume", key="format_btn_1"):
                with st.spinner("Formatting... (Template 1)"):
                    api_key = st.secrets.get("PORTKEY_API_KEY")
                    base_url = st.secrets.get("PORTKEY_BASE_URL")
                    prompt = t1_prompt(resume_text)
                    
                    formatted_resume = t1_call_portkey(prompt,
                                portkey_api_key=api_key,
                                portkey_base_url=base_url
                                                       ) 
                    
                    st.session_state.formatted_resume_1 = formatted_resume

            if st.session_state.formatted_resume_1:
                st.subheader("Formatted Resume")
                st.markdown(st.session_state.formatted_resume_1)

                file_data = t1_convert_to_docx(st.session_state.formatted_resume_1)
                file_data, candidate_name = t1_convert_to_docx(st.session_state.formatted_resume_1)
                
                
                file_name_safe = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '_')).rstrip()
                dynamic_file_name = f"{file_name_safe}_PRFT_Resume_T1.docx"
                
                st.download_button(
                    "Download DOCX",
                    file_data,
                    dynamic_file_name,

                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        except Exception as e:
            st.error(f"An error occurred in Template 1: {e}")
            st.warning("Make sure your GEMINI_API_KEY is set in Streamlit secrets and your template_1.py file is correct.")


def template_2():
    st.write("New Template Format:")
    pdf_viewer(
    "sample_template-2.pdf",
    width=700,
    height=250,
    zoom_level=1.2,                   
    viewer_align="center",            
    show_page_separator=True,
    key="pdf_viewer_t2"
)
      

    st.markdown("<h3 style='color: rgb(186, 43, 43);'> Format Resume to Company Template (New Template)</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"], key="formatter-2")

    if uploaded_file:
        try:
            if uploaded_file.type == "application/pdf":
                resume_text = t2_extract_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = t2_extract_docx(uploaded_file)
            else:
                st.error("Unsupported file type.")
                return

            st.subheader("Extracted Resume Text")
            st.text_area("Resume Content (First 1000 Chars)", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, height=150, key="text_2")

            if "formatted_resume_2" not in st.session_state:
                st.session_state.formatted_resume_2 = ""

            if st.button("Format Resume", key="format_btn_2"):
                with st.spinner("Formatting... (Template 2)"):
                     api_key = st.secrets.get("PORTKEY_API_KEY")
                     base_url = st.secrets.get("PORTKEY_BASE_URL")
                     prompt = t2_prompt(resume_text)
                     formatted_resume = t2_call_portkey(prompt,
                                portkey_api_key=api_key,
                              portkey_base_url=base_url
                                                       ) 

                     st.session_state.formatted_resume_2 = formatted_resume

            if st.session_state.formatted_resume_2:
                st.subheader("Formatted Resume")
                st.markdown(st.session_state.formatted_resume_2)

                file_data = t2_convert_to_docx(st.session_state.formatted_resume_2)
                file_data, candidate_name = t2_convert_to_docx(st.session_state.formatted_resume_2)
                
                # 2. Create a safe, dynamic filename
                file_name_safe = "".join(c for c in candidate_name if c.isalnum() or c in (' ', '_')).rstrip()
                dynamic_file_name = f"{file_name_safe}_PRFT_Resume_T2.docx"
                
                st.download_button(
                    "Download DOCX",
                    file_data,
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
        st.markdown(
             f"""
             <style>
             .stApp {{
                 background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
                 background-size: cover
             }}
             </style>
             """,
             unsafe_allow_html=True
         )
    except Exception as e:
        st.warning(f"Error setting background: {e}")


def main():
    
    set_bg_hack('bg_final.jpg')  
    st.markdown(
    "<h1 style='color:rgb(186, 43, 43); font-weight: bold; text-align: center;'>TalentTune</h1>",
    unsafe_allow_html=True
)
    st.markdown(
    "<p style='text-align: center; font-size:18px;'><em>Fine-tune your profile for job success.</em></p>",
    unsafe_allow_html=True
)

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