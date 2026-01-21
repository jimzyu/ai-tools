import streamlit as st
import google.generativeai as genai
from opencc import OpenCC
import re

# 1. Setup
st.set_page_config(page_title="聖經研讀工具 | Bible Study Tool", layout="centered")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = None

if not API_KEY:
    st.error("API Key missing.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="You are a Chinese-American pastor. Provide a study guide with 3 reflection questions followed by a theme summary."
)
cc = OpenCC('t2s')

# 2. Updated Prompt Logic
def get_ai_response(ref):
    prompt = f"""
    Provide a study guide for: {ref}.
    
    [CHINESE]
    ### 啟發式提問 (Reflection Questions)
    1. **觀察 (Observation)**: (Question about what is happening)
    2. **解釋 (Interpretation)**: (Question about the meaning)
    3. **應用 (Application)**: (Question about personal change)
    
    ### 主題摘要 (Theme Summary)
    - **主題名稱**: 
    - **神學意義**: 
    - **歷史背景**: 

    [ENGLISH]
    (Exact translation of the Chinese sections above)
    """
    response = model.generate_content(prompt)
    return response.text

# 3. UI
st.title("📖 聖經研讀工具")
st.markdown("輸入經文以獲取啟發提問與主題摘要。")

reference = st.text_input("經文引用 (e.g., Matthew 14:1-36)", placeholder="Matthew 14:1-36")

if st.button("開始研讀 Start Study", type="primary"):
    if reference:
        with st.spinner('正在準備內容...'):
            st.session_state.raw_output = get_ai_response(reference)
    else:
        st.warning("請輸入經文。")

# 4. Display Logic
if 'raw_output' in st.session_state:
    # Parsing logic (using simple split for demonstration, Regex recommended for production)
    full_text = st.session_state.raw_output
    ch_section = full_text.split("[CHINESE]")[1].split("[ENGLISH]")[0].strip()
    en_section = full_text.split("[ENGLISH]")[1].strip()
    sim_section = cc.convert(ch_section)

    st.divider()
    tab1, tab2, tab3 = st.tabs(["繁體中文", "简体中文", "English"])

    def render_content(content, lang_label):
        # Split the content into Questions and Summary parts
        parts = content.split("### 主題摘要") if "### 主題摘要" in content else content.split("### Theme Summary")
        
        questions = parts[0]
        summary = parts[1] if len(parts) > 1 else ""

        st.subheader("📝 啟發式提問")
        st.markdown(questions)
        
        with st.expander("查看主題摘要 (View Theme Summary)"):
            st.markdown(summary)

    with tab1: render_content(ch_section, "繁體")
    with tab2: render_content(sim_section, "简体")
    with tab3: render_content(en_section, "English")