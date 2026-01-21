import streamlit as st
import google.generativeai as genai
from opencc import OpenCC
import re

# 1. Configuration & Security
st.set_page_config(page_title="聖經主題工具 | Biblical Theme Tool", layout="centered")

# Attempt to load API Key
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
    model_name='gemini-3-flash',
    system_instruction=(
        "You are a Chinese-American pastor with a conservative evangelical background. "
        "Your goal is to provide deep, concise theological summaries. "
        "Always output in the requested [CHINESE] and [ENGLISH] format. "
        "The English section must be a direct and faithful translation of the Chinese section."
    )
)

# Initialize Simplified/Traditional converter
cc = OpenCC('t2s')

# 2. Helper Functions
def parse_ai_response(text):
    """Uses regex to reliably extract Chinese and English sections."""
    # Pattern to find content between [CHINESE] and [ENGLISH]
    ch_pattern = r"\[CHINESE\](.*?)\[ENGLISH\]"
    # Pattern to find content after [ENGLISH]
    en_pattern = r"\[ENGLISH\](.*)"
    
    ch_match = re.search(ch_pattern, text, re.DOTALL | re.IGNORECASE)
    en_match = re.search(en_pattern, text, re.DOTALL | re.IGNORECASE)
    
    ch_content = ch_match.group(1).strip() if ch_match else text
    en_content = en_match.group(1).strip() if en_match else "Parsing error. Please try again."
    
    # Remove any AI 'meta-talk' or parenthetical instructions
    en_content = re.sub(r"\(The English content below.*?\)", "", en_content, flags=re.IGNORECASE).strip()
    
    return ch_content, en_content

# 3. UI Layout
st.title("📖 聖經主題工具")
st.subheader("Biblical Theme Tool")
st.markdown("---")

# Session State for results
if 'ai_result' not in st.session_state:
    st.session_state.ai_result = None

# Sidebar for controls
with st.sidebar:
    st.header("Settings & Tools")
    if st.button("清除結果 Clear Results"):
        st.session_state.ai_result = None
        st.rerun()

# User Input
reference = st.text_input(
    "經文引用 Scriptural Reference", 
    placeholder="例如: John 3:16 or 馬太福音 5:3-10"
)

# 4. Logic Execution
if st.button("生成摘要 Generate Summary", type="primary"):
    if reference.strip():
        with st.spinner('正在進行諮詢 Consulting the text...'):
            try:
                # Optimized Prompt
                user_prompt = f"""
                Provide a summary for: {reference}.
                
                Format:
                [CHINESE]
                - **主題名稱**: (4-8 Traditional Chinese characters)
                - **神學意義說明**: (2 sentences)
                - **歷史背景補充**: (Contextual details)

                [ENGLISH]
                (Translate the above Chinese content exactly)
                """
                
                response = model.generate_content(user_prompt)
                st.session_state.ai_result = response.text
            except Exception as e:
                if "429" in str(e):
                    st.warning("系統繁忙，請稍候 30 秒再試。 (Rate limit reached.)")
                else:
                    st.error(f"Error: {e}")
    else:
        st.warning("請輸入有效的經文引用。 Please enter a reference.")

# 5. Display Results
if st.session_state.ai_result:
    ch_text, en_text = parse_ai_response(st.session_state.ai_result)
    sim_text = cc.convert(ch_text)
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["繁體中文", "简体中文", "English"])
    
    with tab1:
        st.markdown(ch_text)
    
    with tab2:
        st.markdown(sim_text)
        
    with tab3:
        st.markdown(en_text)