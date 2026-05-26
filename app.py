import streamlit as st
from google import genai
from google.genai import types

# 【後台金鑰隱藏】請在此處填入你的 Gemini 金鑰
HIDDEN_GEMINI_KEY = "AIzaSyC2UTzsT9VXCqLKMVz8hs7mb8jTimm0kt4"

# 將 layout 改為 "wide"（寬版模式），initial_sidebar_state 設為 "expanded" 確保左側面板正常展開
st.set_page_config(
    page_title="AI 護理紀錄自動整理系統", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= 🎨 CSS 樣式：整體文字放大 2 號 ＆ 徹底移除頂部官方按鈕 =================
st.markdown("""
    <style>
        /* 🚨 終極大絕招：精準點名最新版 Streamlit 的工具列與所有官方按鈕（貓咪、Fork、三個點），強制集體物理蒸發 */
        header, 
        [data-testid="stHeader"], 
        [data-testid="stAppToolbar"], 
        [data-testid="stHeaderButtons"],
        .stAppToolbar,
        .stHeader {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
            width: 0px !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* 修正因為頂部元件被隱藏後，網頁上方可能產生的額外大空白 */
        .main .block-container {
            padding-top: 2rem !important;
        }

        /* 全域基礎文字放大（大約增加 4px，即大 2 號） */
        html, body, [data-testid="stWidgetLabel"], p, div, label {
            font-size: 20px !important;
        }
        /* 大標題放大 */
        h1 {
            font-size: 2.5rem !important;
        }
        /* 中標題放大 */
        h3 {
            font-size: 1.8rem !important;
        }
        /* 單選按鈕文字放大 */
        div[data-testid="stRadio"] label {
            font-size: 20px !important;
        }
        /* 輸入框內的文字與預設提示字放大 */
        textarea, input {
            font-size: 20px !important;
        }
        /* 反灰結果區塊的文字放大 */
        code, pre {
            font-size: 19px !important;
            line-height: 1.6 !important;
        }
        /* 側邊欄文字微調 */
        [data-testid="stSidebar"] {
            min-width: 320px;
        }
    </style>
""", unsafe_allow_html=True)
# =============================================================

# ================= 🔒 左邊面板：安全登入設計 =================
with st.sidebar:
    st.header("🔐 系統安全登入")
    
    # 將密碼輸入框移至左邊面板
    login_password = st.text_input("請輸入系統登入密碼：", type="password")
    
    st.write("---")
    st.caption("本系統僅供內部授權人員使用。")

# 檢查左邊面板輸入的密碼是否正確（設定為 820719）
if login_password != "820719":
    # 右邊主畫面顯示提示訊息
    st.title("🔐 歡迎使用 AI 護理紀錄自動整理系統")
    if login_password == "":
        st.info("💡 請在【左側面板】輸入正確的系統密碼以解鎖功能。")
    else:
        st.error("❌ 密碼錯誤！請重新輸入。")
    st.stop() 
# =============================================================


# ---- 🔓 密碼正確（820719）才會解鎖顯示以下主畫面 ----
st.title("🩺 AI 護理紀錄自動整理系統")
st.write("將破碎、口語化的臨床交班或隨手筆記，自動轉換為標準的醫療紀錄格式。")

# 主要介面
format_type = st.radio("請選擇欲轉換的紀錄格式：", ["SOAP", "Focus Charting (DART)"], horizontal=True)

# 🎯 已修正：這裡完全設定為空字串 ""，框框內絕對不會再出現任何灰色範例文字了
raw_notes = st.text_area(
    "請輸入原始口語筆記或交班重點：", 
    placeholder="",
    height=200 
)

# 執行轉換按鈕（包含自訂符號）
if st.button("👉 🪄 開始自動整理 ⚡", type="primary"):
    if not HIDDEN_GEMINI_KEY or HIDDEN_GEMINI_KEY == "這裡換成你複製的完整金鑰":
        st.error("後台金鑰尚未設定正確，請聯繫系統管理員。")
    elif not raw_notes.strip():
        st.warning("請先輸入護理筆記內容。")
    else:
        with st.spinner("AI 正在專業整理中，請稍候..."):
            try:
                # 初始化 Gemini 客戶端
                client = genai.Client(api_key=HIDDEN_GEMINI_KEY)
                
                # 設定系統提示詞
                if format_type == "SOAP":
                    system_instruction = """
                    你是一位專業的資深臨床護理師。請將使用者輸入的破碎、口語化護理內容，整理成標準的 SOAP 護理紀錄格式。
                    - S (Subjective): 主觀敘述
                    - O (Objective): 客觀評估
                    - A (Assessment): 護理評估
                    - P (Plan): 護理計畫
                    - 請確保專有名詞與醫學縮寫使用正確，語氣專業、客觀、精簡。
                    """
                else:
                    system_instruction = """
                    你是一位專業的資深臨床護理師。請將使用者輸入的破碎、口語化護理內容，整理成標準的 Focus Charting (DART) 護理紀錄格式。
                    - Focus (焦點)
                    - D (Data): 資料
                    - A (Action): 措施
                    - R (Response): 反應
                    - T (Teaching): 衛教
                    - 請確保專有名詞與醫學縮寫使用正確，語氣專業、客觀、精簡。
                    """

                # 呼叫模型
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"請整理以下護理內容：\n{raw_notes}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2,
                    )
                )
                
                # 顯示結果
                st.success("✨ 整理完成！")
                st.markdown("### 📋 生成紀錄結果")
                
                # 強迫反灰區塊內的文字自動換行
                st.code(response.text, language="markdown", wrap_lines=True)
                st.caption("💡 您可以點擊右上角的按鈕直接複製文字。")
                
            except Exception as e:
                st.error(f"轉換過程中發生錯誤: {str(e)}")
