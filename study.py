import streamlit as st
import google.generativeai as genai
from opencc import OpenCC
import re

# 1. Configuration & Security
st.set_page_config(page_title="聖經研讀工具 | Bible Study Tool", layout="centered")

# Load API Key from Streamlit Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = None

if not API_KEY:
    st.error("⚠️ API Key not found. Please set 'GEMINI_API_KEY' in your Streamlit Secrets.")
    st.stop()

# Initialize Gemini with System Instructions for consistent persona
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(
    model_name='gemini-3-flash-review',
    system_instruction=(
        "You are a Chinese-American pastor with a conservative evangelical background. "
        "Provide a study guide consisting of 3 reflection questions (Observation, Interpretation, Application) "
        "followed by a concise theme summary. Always use the [CHINESE] and [ENGLISH] tags. "
        "The English section must be a direct translation of the Chinese section."
    )
)

# Initialize Simplified/Traditional converter
cc = OpenCC('t2s')

# 2. Helper Functions
def parse_ai_response(text):
    """Uses regex to reliably extract Chinese and English sections, avoiding IndexErrors."""
    ch_pattern = r"\[CHINESE\](.*?)\[ENGLISH\]"
    en_pattern = r"\[ENGLISH\](.*)"
    
    ch_match = re.search(ch_pattern, text, re.DOTALL | re.IGNORECASE)
    en_match = re.search(en_pattern, text, re.DOTALL | re.IGNORECASE)
    
    # Fallback: If tags are missing, treat the whole thing as Chinese for safety
    ch_content = ch_match.group(1).strip() if ch_match else text
    en_content = en_match.group(1).strip() if en_match else "English translation not available."
    
    return ch_content, en_content

def render_study_content(content):
    """Splits content into Questions and Summary and renders them in the UI."""
    # Look for the 'Theme Summary' header in either language
    if "### 主題摘要" in content:
        parts = content.split("### 主題摘要")
    elif "### Theme Summary" in content:
        parts = content.split("### Theme Summary")
    else:
        parts = [content]

    questions = parts[0].strip()
    summary = parts[1].strip() if len(parts) > 1 else None

    st.subheader("📝 啟發式提問 (Reflection Questions)")
    st.markdown(questions)
    
    if summary:
        with st.expander("📖 查看主題摘要 (View Theme Summary)"):
            st.markdown(summary)

# 3. UI Layout
st.title("📖 聖經研讀工具")
st.subheader("Biblical Study & Theme Tool")
st.markdown("輸入經文引用以獲取啟發提問與深度摘要。")
st.markdown("---")

# Session State for results
if 'ai_result' not in st.session_state:
    st.session_state.ai_result = None

# User Input
reference = st.text_input(
    "經文引用 Scriptural Reference", 
    placeholder="例如: Matthew 14:1-36"
)

# 4. Logic Execution
if st.button("開始研讀 Start Study", type="primary"):
    if reference.strip():
        with st.spinner('正在準備研讀內容...'):
            try:
                # Optimized Prompt for the new structure
                user_prompt = f"""
                Provide a study guide for: {reference}.
                
                [CHINESE]
                ### 啟發式提問
                1. **觀察 (Observation)**: (Question about facts)
                2. **解釋 (Interpretation)**: (Question about meaning)
                3. **應用 (Application)**: (Question about life)
                
                ### 主題摘要
                - **主題名稱**: 
                - **神學意義說明**: 
                - **歷史背景補充**: 

                [ENGLISH]
                (Translate the content above exactly)
                """
                
                response = model.generate_content(user_prompt)
                st.session_state.ai_result = response.text
            except Exception as e:
                st.error(f"發生錯誤 (Error): {e}")
    else:
        st.warning("請輸入有效的經文引用。")

# 5. Display Results
if st.session_state.ai_result:
    ch_text, en_text = parse_ai_response(st.session_state.ai_result)
    sim_text = cc.convert(ch_text)
    
    st.divider()
    
    # Main Navigation: Language-based tabs
    tab1, tab2, tab3 = st.tabs(["繁體中文", "简体中文", "English"])
    
    with tab1:
        render_study_content(ch_text)
    
    with tab2:
        render_study_content(sim_text)
        
    with tab3:
        render_study_content(en_text)