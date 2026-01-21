import streamlit as st
import google.generativeai as genai
from opencc import OpenCC
import re

# 1. Configuration & Security
st.set_page_config(page_title="聖經研讀工具 | Bible Study Tool", layout="centered")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = None

if not API_KEY:
    st.error("⚠️ API Key not found. Please set 'GEMINI_API_KEY' in your Streamlit Secrets.")
    st.stop()

# Initialize Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=(
        "You are a Chinese-American pastor with a conservative evangelical background. "
        "Provide a study guide consisting of 3 reflection questions (Observation, Interpretation, Application) "
        "followed by a concise theme summary. Always use the [CHINESE] and [ENGLISH] tags. "
        "The English section must be a direct translation of the Chinese section."
    )
)

cc = OpenCC('t2s')

# 2. Session State Initialization
if 'history' not in st.session_state:
    st.session_state.history = []  # Stores list of dictionaries: {"ref": str, "content": str}

if 'current_view' not in st.session_state:
    st.session_state.current_view = None

# 3. Helper Functions
def parse_ai_response(text):
    ch_pattern = r"\[CHINESE\](.*?)\[ENGLISH\]"
    en_pattern = r"\[ENGLISH\](.*)"
    ch_match = re.search(ch_pattern, text, re.DOTALL | re.IGNORECASE)
    en_match = re.search(en_pattern, text, re.DOTALL | re.IGNORECASE)
    
    ch_content = ch_match.group(1).strip() if ch_match else text
    en_content = en_match.group(1).strip() if en_match else "English translation not available."
    return ch_content, en_content

def render_study_content(content):
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

def add_to_history(ref, content):
    # Avoid duplicates: if the reference already exists, remove the old one first
    st.session_state.history = [h for h in st.session_state.history if h['ref'] != ref]
    # Insert at the beginning of the list
    st.session_state.history.insert(0, {"ref": ref, "content": content})
    # Keep only the last 5 items
    st.session_state.history = st.session_state.history[:5]

# 4. Sidebar - History Feature
with st.sidebar:
    st.header("🕒 最近紀錄 History")
    if not st.session_state.history:
        st.info("尚無紀錄 No history yet.")
    else:
        for i, item in enumerate(st.session_state.history):
            # Each history item is a button
            if st.button(f"📄 {item['ref']}", key=f"hist_{i}"):
                st.session_state.current_view = item['content']
    
    st.divider()
    if st.button("清除所有紀錄 Clear All"):
        st.session_state.history = []
        st.session_state.current_view = None
        st.rerun()

# 5. Main UI
st.title("📖 聖經研讀工具")
st.subheader("Biblical Study & Theme Tool")
st.markdown("輸入經文引用以獲取啟發提問與深度摘要。")
st.markdown("---")

reference = st.text_input("經文引用 Scriptural Reference", placeholder="例如: Matthew 14:1-36")

if st.button("開始研讀 Start Study", type="primary"):
    if reference.strip():
        with st.spinner('正在準備研讀內容...'):
            try:
                user_prompt = f"Provide a study guide for: {reference}. [CHINESE] ### 啟發式提問 ... ### 主題摘要 ... [ENGLISH] ..."
                # Note: Using simplified prompt call here for brevity, keep your full prompt structure
                response = model.generate_content(f"Provide the study guide for {reference} following the Pastor persona and [CHINESE]/[ENGLISH] format.")
                
                st.session_state.current_view = response.text
                add_to_history(reference, response.text)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("請輸入有效的經文引用。")

# 6. Display Results
if st.session_state.current_view:
    ch_text, en_text = parse_ai_response(st.session_state.current_view)
    sim_text = cc.convert(ch_text)
    
    st.divider()
    tab1, tab2, tab3 = st.tabs(["繁體中文", "简体中文", "English"])
    
    with tab1: render_study_content(ch_text)
    with tab2: render_study_content(sim_text)
    with tab3: render_study_content(en_text)