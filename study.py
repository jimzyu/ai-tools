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

# Initialize Gemini with Gatekeeping System Instructions
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', 
    system_instruction=(
        "You are a Chinese-American pastor with a conservative evangelical background. "
        "Your primary role is to provide Bible study guides. "
        "CRITICAL RULE: If the user input is NOT a biblical reference, passage, or book name "
        "(e.g., 'Chicken Soup', 'Batman', 'How to cook'), you must respond ONLY with the word '[INVALID_REF]'. "
        "If it is a valid reference, provide the study guide in [CHINESE] and [ENGLISH] tags. "
        "The English section must be a direct translation of the Chinese section."
    )
)

# Initialize Simplified/Traditional converter
cc = OpenCC('t2s')

# 2. Helper Functions
def parse_ai_response(text):
    """Reliably extract sections and handle invalid reference flags."""
    if "[INVALID_REF]" in text.upper():
        return None, None
        
    ch_pattern = r"\[CHINESE\](.*?)\[ENGLISH\]"
    en_pattern = r"\[ENGLISH\](.*)"
    
    ch_match = re.search(ch_pattern, text, re.DOTALL | re.IGNORECASE)
    en_match = re.search(en_pattern, text, re.DOTALL | re.IGNORECASE)
    
    ch_content = ch_match.group(1).strip() if ch_match else text
    en_content = en_match.group(1).strip() if en_match else "English translation not available."
    
    return ch_content, en_content

def render_study_content(content):
    """Splits content into Questions and Summary and renders them in the UI."""
    # List of possible headers to split on (Traditional, Simplified, and English)
    headers = ["### 主題摘要", "### 主题摘要", "### Theme Summary"]
    
    questions = content
    summary = None

    for header in headers:
        if header in content:
            parts = content.split(header)
            questions = parts[0].strip()
            summary = parts[1].strip() if len(parts) > 1 else None
            break 

    st.subheader("📝 提問+小結 (Reflections & Summary)")
    st.markdown(questions)
    
    if summary:
        with st.expander("📖 查看主題摘要 (View Theme Summary)"):
            st.markdown(summary)

# 3. UI Layout
st.title("📖 聖經研讀工具")
st.subheader("Biblical Study & Theme Tool")
st.markdown("輸入經文引用以獲取啟發提問與深度摘要。")
st.markdown("---")

if 'ai_result' not in st.session_state:
    st.session_state.ai_result = None

reference = st.text_input(
    "經文引用 Scriptural Reference", 
    placeholder="例如: Matthew 14:1-36"
)

# 4. Logic Execution
if st.button("開始研讀 Start Study", type="primary"):
    if reference.strip():
        with st.spinner('正在驗證並準備內容...'):
            try:
                # Merged prompt: includes the structure of study_good and the validation of study_check
                user_prompt = f"""
                Analyze the following reference: "{reference}".
                If it is a Bible verse or passage, provide the study guide.
                If it is not a Bible passage, reply ONLY with [INVALID_REF].

                [CHINESE]
                ### 啟發式提問
                1. **觀察 (Observation)**: (Question about facts)
                2. **解釋 (Interpretation)**: (Question about meaning)
                3. **應用 (Application)**: (Question about life)
                
                ### 主題摘要
                - **簡要主題**: (4-8個繁體中文字)
                - **神學意義說明**: (約兩句話，深入淺出)
                - **歷史背景補充**: (若適用，請提到特定背景如：流亡時期、受難週等)

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
    
    if ch_text is None:
        st.error("❌ 無法識別該經文引用。請輸入有效的聖經章節（例如：約翰福音 3:16）。")
        st.info("Invalid scriptural reference. Please enter a valid Bible passage (e.g., John 3:16).")
    else:
        sim_text = cc.convert(ch_text)
        st.divider()
        tab1, tab2, tab3 = st.tabs(["繁體中文", "简体中文", "English"])
        
        with tab1:
            render_study_content(ch_text)
        with tab2:
            render_study_content(sim_text)
        with tab3:
            render_study_content(en_text)