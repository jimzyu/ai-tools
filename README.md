📖 Biblical Theme Tool
A specialized research assistant designed for Bible study, utilizing Google Gemini-3-Flash AI to provide theological analysis and historical context for biblical passages.

✨ Key Features

*Deep Theological Summaries: Professional insights provided by a virtual AI scholar with a conservative evangelical background.

*Historical Context Support: Automatically identifies and explains key historical settings such as the "Exile" or "Passion Week".

*Multi-Language Synchronization:

  -Traditional Chinese: Precise academic and theological terminology.

  -Simplified Chinese: Locally converted to ensure 100% semantic consistency with the Traditional version.

  -English: Provides an exact academic translation of the Chinese content, ideal for cross-linguistic teaching.

🚀 How to Use

*Input Reference: Enter a biblical chapter or verse (e.g., Mark 10:45 or Isaiah 53:1-5) in the search box.

*Generate Summary: Click the "Generate Summary" button.

*Toggle Tabs: Once generated, use the three tabs at the bottom to switch between language versions.

📊 Technical Info & Quota

*Daily Limit: Due to free-tier API restrictions, this tool is limited to 20 requests per day.

*Reset Time: The quota resets daily at 12:00 AM Pacific Time (PT).

*Safety Filters: Passages involving intense historical narratives or sensitive themes may trigger the AI safety filter. If blocked, the tool will display a warning rather than crashing.

🛠️ Development & Deployment
To run this tool locally, ensure you have the following Python libraries installed:

Bash

pip install streamlit google-generativeai opencc-python-reimplemented

Environment Variables (Secrets): 
This application uses st.secrets to securely read your API key. When deploying to Streamlit Cloud, add the following to your Advanced Settings: GEMINI_API_KEY = "your_actual_key_here".

Disclaimer: This tool is intended for academic and devotional aid. AI-generated content should always be cross-referenced with original scripture and traditional exegesis.
