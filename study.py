import streamlit as st
import google.generativeai as genai
from opencc import OpenCC
import re
import time

# 1. Configuration & Security
st.set_page_config(page_title="聖經研讀工具 | Bible Study Tool", layout="centered")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = None

if not API_KEY:
    st.error("⚠️ API Key not found. Please set 'GEMINI_API_KEY' in your Streamlit Secrets.")
    st.stop()

# Initialize Gemini with a lower temperature for consistency
genai.configure(api_key=API_KEY)
generation_config = genai.types.GenerationConfig(temperature=0.3)

model = genai.GenerativeModel(
    model_name='gemini-2.5-pro', 
    generation_config=generation_config,
    system_instruction=(
        "You are a Chinese-American pastor with a conservative evangelical background. "
        "Your primary role is to provide Bible study guides. "
        "CRITICAL RULE: If the user input is NOT a biblical reference, passage, or book name "
        "(e.g., 'Chicken Soup', 'Batman'), you must respond ONLY with the word '[INVALID_REF]'. "
        "If it is a valid reference, provide the study guide in [CHINESE] and [ENGLISH] tags. "
        "The English section must be a direct translation of the Chinese section."
    )
)

cc = OpenCC('t2s')

# 2. Helper Functions
def parse_ai_response(text):
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

# Deep Mode Toggle
deep_mode = st.checkbox("🔍 啟用深度整合模式 (Deep Study Mode - Generates 3 drafts & merges them)")

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
        # Using a status container for better UX during long waits
        with st.status("正在進行深度研讀 (Conducting Deep Study)...", expanded=True) as status:
            try:
                # Base Prompt Structure
                base_prompt_template = """
                Analyze the following reference: "{ref}".
                If it is a Bible verse or passage, provide the study guide.
                If it is not a Bible passage, reply ONLY with [INVALID_REF].

                Context focus: {focus}

                [CHINESE]
                ### 啟發式提問
                1. **觀察 (Observation)**: (Question about facts)
                2. **解釋 (Interpretation)**: (Question about meaning)
                3. **應用 (Application)**: (Question about life)
                
                ### 主題摘要
                - **主題名稱**: (4-8個繁體中文字)
                - **神學意義說明**: (約兩句話，深入淺出)
                - **歷史背景補充**: (若適用，請提到特定背景如：流亡時期、受難週等)

                [ENGLISH]
                (Translate the content above exactly)
                """

                if deep_mode:
                    # --- DRAFT 1: Standard Balanced ---
                    status.write("Draft 1: Generating Standard Theological View...")
                    prompt_1 = base_prompt_template.format(ref=reference, focus="Standard balanced evangelical theology.")
                    draft_1 = model.generate_content(prompt_1).text
                    
                    if "[INVALID_REF]" in draft_1:
                         st.session_state.ai_result = "[INVALID_REF]"
                         status.update(label="Error: Invalid Reference", state="error")
                    else:
                        # --- DRAFT 2: Historical Focus ---
                        status.write("Draft 2: Digging into Historical & Cultural Context...")
                        prompt_2 = base_prompt_template.format(ref=reference, focus="Deep historical, cultural, and linguistic context.")
                        draft_2 = model.generate_content(prompt_2).text

                        # --- DRAFT 3: Application Focus ---
                        status.write("Draft 3: Focusing on Modern Life Application...")
                        prompt_3 = base_prompt_template.format(ref=reference, focus="Practical application for modern daily life and personal struggles.")
                        draft_3 = model.generate_content(prompt_3).text
                        
                        # --- MERGE STEP ---
                        status.write("Final Step: Merging and Polishing...")
                        merge_prompt = f"""
                        You are an expert editor. I have generated three different study guides for "{reference}".
                        
                        Draft 1 (Standard): {draft_1}
                        Draft 2 (Historical): {draft_2}
                        Draft 3 (Application): {draft_3}

                        Your Goal: Create ONE Master Version.
                        1. Select the most insightful "Observation" question from the drafts.
                        2. Select the deepest "Interpretation" question.
                        3. Select the most challenging "Application" question.
                        4. Combine the historical facts and theological meanings into a rich summary.
                        5. STRICTLY output in the [CHINESE] and [ENGLISH] format.
                        """
                        final_response = model.generate_content(merge_prompt)
                        st.session_state.ai_result = final_response.text
                        status.update(label="Complete! (完成)", state="complete", expanded=False)

                else:
                    # Standard Mode (Single Shot)
                    status.write("Consulting the text...")
                    prompt = base_prompt_template.format(ref=reference, focus="Standard balanced theology.")
                    response = model.generate_content(prompt)
                    st.session_state.ai_result = response.text
                    status.update(label="Complete!", state="complete", expanded=False)

            except Exception as e:
                st.error(f"發生錯誤 (Error): {e}")
                status.update(label="Error", state="error")
    else:
        st.warning("請輸入有效的經文引用。")

# 5. Display Results
if st.session_state.ai_result:
    ch_text, en_text = parse_ai_response(st.session_state.ai_result)
    
    if ch_text is None:
        st.error("❌ 無法識別該經文引用。請輸入有效的聖經章節（例如：約翰福音 3:16）。")
        st.info("Invalid scriptural reference. Please enter a valid Bible passage.")
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