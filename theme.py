import streamlit as st
import google.generativeai as genai
from opencc import OpenCC
import time # 用於處理 429 錯誤

# 1. 程式設定與 API 金鑰 (安全讀取方式)
# 在部署到 Streamlit Cloud 後，這會從 "Secrets" 設定中讀取
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = "000000" # 本地測試時暫用

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

# 初始化繁簡轉換器
cc = OpenCC('t2s') 

# 2. UI 介面設計
st.set_page_config(page_title="聖經主題工具", layout="centered")
st.title("📖 聖經主題工具")
st.title("Biblical Theme Tool")
st.markdown("請輸入聖經經文引用（如：馬可福音 10:45）以獲取主題摘要。")
st.markdown("Please enter biblical passages (e.g. Mark 10:45) to obtain a summary.")

# 初始化 Session State 以儲存結果
if 'ai_result' not in st.session_state:
    st.session_state.ai_result = None

# 3. 使用者輸入
reference = st.text_input("經文引用 Scriptural Reference", placeholder="例如 e.g.: Mark 10:45")

# 4. 按鈕邏輯
if st.button("生成摘要 Generate Summary"):
    if reference:
        with st.spinner('正在進行諮詢 Consulting the text...'):
            try:
                # 強化後的 Prompt：要求英文必須是中文的精確翻譯
                prompt = f"""
                You are a Chinese-American pastor with conservative evangelical background.
                Provide a deep, concise summary of the theme for: {reference}.
                
                Step 1: Write the content in Traditional Chinese first.
                Step 2: Provide an exact English translation of that Chinese content.

                Please use exactly this format with the tags [CHINESE] and [ENGLISH]. 
                Ensure section titles are wrapped in double asterisks like **Title**:

                [CHINESE]
                - **主題名稱**: (4-8個繁體中文字)
                - **神學意義說明**: (約兩句話，深入淺出)
                - **歷史背景補充**: (若適用，請提到特定背景如：流亡時期、受難週等)

                [ENGLISH]
                (The English content below must be an EXACT translation of the Chinese section above.)
                - **Theme Title**: 
                - **Theological Significance**: 
                - **Historical Context**: 
                """            

                response = model.generate_content(prompt)
                st.session_state.ai_result = response.text
            except Exception as e:
                if "429" in str(e):
                    st.warning("系統繁忙，請稍候 30 秒再試一次。 (Rate limit reached, please wait.)")
                else:
                    st.error(f"發生錯誤: {e}") 
    else:
        st.error("請輸入有效的經文引用。")

# 5. 顯示邏輯 (精確拆分內容並顯示於三個分頁)
if st.session_state.ai_result:
    st.divider()
    
    full_text = st.session_state.ai_result
    
    try:
        # 根據標籤拆分區塊
        chinese_raw = full_text.split("[CHINESE]")[1].split("[ENGLISH]")[0].strip()
        english_part = full_text.split("[ENGLISH]")[1].strip()
        
        # 移除可能出現在開頭的提示文字 (The English content below...)
        if ")" in english_part:
            english_part = english_part.split(")", 1)[1].strip()
            
    except IndexError:
        chinese_raw = full_text
        english_part = "無法解析格式，請重新生成。"

    # 本地端將繁體內容轉換為簡體
    simplified_text = cc.convert(chinese_raw)

    # 建立三個分頁
    tab1, tab2, tab3 = st.tabs(["繁體中文", "简体中文", "English"])
    
    with tab1:
        st.info(chinese_raw)
    
    with tab2:
        st.info(simplified_text)
        
    with tab3:
        st.info(english_part)