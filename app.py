import streamlit as st
from google import genai
from google.genai import types

# 【後台金鑰隱藏】請在此處填入你的 Gemini 金鑰
HIDDEN_GEMINI_KEY = "AIzaSyC2UTzsT9VXCqLKMVz8hs7mb8jTimm0kt4"

# 將 layout 改為 "wide"（寬版模式）
st.set_page_config(page_title="AI 護理紀錄自動整理系統", page_icon="🩺", layout="wide")

# ================= 🎨 CSS 樣式：整體文字放大 2 號 =================
st.markdown("""
    <style>
        html, body, [data-testid="stWidgetLabel"], p, div, label {
            font-size: 20px !important;
        }
        h1 {
            font-size: 2.5rem !important;
        }
        h3 {
            font-size: 1.8rem !important;
        }
        div[data-testid="stRadio"] label {
            font-size: 20px !important;
        }
        textarea, input {
            font-size: 20px !important;
        }
        code, pre {
            font-size: 19px !important;
            line-height: 1.6 !important;
        }
        [data-testid="stSidebar"] {
            min-width: 320px;
        }
    </style>
""", unsafe_allow_html=True)
# =============================================================

# ================= 🔒 左邊面板：安全登入設計 =================
with st.sidebar:
    st.header("🔐 系統安全登入")
    login_password = st.text_input("請輸入系統登入密碼：", type="password")
    st.write("---")
    st.caption("本系統僅供內部授權人員使用。")

# 檢查密碼 (820719)
if login_password != "820719":
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

raw_notes = st.text_area(
    "請輸入原始口語筆記或交班重點：", 
    placeholder="可以貼上個別病人的段落，例如：\n9A19-03 陳語鍹\n精神尚可，情緒起伏，表示幻聽還是很大聲，叫我立刻馬上去死... 6/3要開庭，予傾聽...",
    height=250 
)

# 執行轉換按鈕
if st.button("🪄 開始自動整理", type="primary"):
    if not HIDDEN_GEMINI_KEY or HIDDEN_GEMINI_KEY == "這裡換成你複製的完整金鑰":
        st.error("後台金鑰尚未設定正確，請聯繫系統管理員。")
    elif not raw_notes.strip():
        st.warning("請先輸入護理筆記內容。")
    else:
        with st.spinner("AI 正在專業整理中，請稍候..."):
            try:
                # 初始化 Gemini 客戶端
                client = genai.Client(api_key=HIDDEN_GEMINI_KEY)
                
                # 設定專屬精神科臨床思維與範本模擬的系統提示詞
                if format_type == "SOAP":
                    system_instruction = """
                    你是一位精通精神醫療科（Psychiatric Ward）與一般內外科臨床護理的資深護理師。
                    請將使用者提供的精神科臨床口語、交班範本片段（如包含幻聽、妄想、情緒起伏、約束、自殺防範、拒藥、FS血糖、CPK數據、點滴與抗生素等），整理成正式、精簡且專業的 SOAP 護理紀錄。

                    【撰寫準則】：
                    1. S (Subjective): 記錄病人主觀訴求（如：幻聽內容『叫我立刻去死』、對住院/生日/官司開庭的想法等），儘量精準摘錄或使用引號呈現重要字句。
                    2. O (Objective): 記錄護理人員客觀觀察（如：精神與情緒狀態、自語對空說話、雙手微抖、想法缺乏現實、步態、服藥遵從性如拒藥/漏吃、約束使用、尿管引流狀態、檢驗數值如CPK、血糖FS紀錄、I/O或點滴進度）。
                    3. A (Assessment): 針對當前精神症狀及內科問題進行護理評估（如：知覺感受改變/Auditory hallucination、潛在危險性/危險性自我傷害、服藥遵從性不佳、高血糖/血糖控制不佳、組織灌流改變等）。
                    4. P (Plan): 記錄執行的護理措施與計畫（如：續防自殺/維持安全、傾聽、給予支持、常規與PRN藥物指導、加強規則服藥重要性、執行約束/保護室護理、維持尿管護理、持續追蹤血糖與抽血data）。
                    
                    【文字要求】：專業、精簡、流暢，專有名詞與醫學縮寫使用正確。
                    """
                else:
                    system_instruction = """
                    你是一位精通精神醫療科（Psychiatric Ward）與一般內外科臨床護理的資深護理師。
                    請將使用者提供的精神科臨床口語、交班範本片段（如包含幻聽、妄想、情緒起伏、約束、自殺防範、拒藥、FS血糖、CPK數據、點滴與抗生素等），整理成標準的 Focus Charting (DART) 護理紀錄。

                    【撰寫準則】：
                    1. Focus (焦點): 確立明確的焦點問題（例如：知覺感受改變：幻聽、潛在危險性：自殺/自傷、精神狀態改變、服藥遵從性不佳、高血糖狀態、體液容積改變）。
                    2. D (Data): 包含病人主客觀資料。記錄病人主訴（如幻聽內容、吵架過程）與護理師客觀觀察（自語、意念飛躍、雙手微抖、拒藥、FS血糖值、CPK數值、I/O紀錄、體重BW）。
                    3. A (Action): 記錄護理人員執行的醫療與護理措施（如：予傾聽、心理支持、加強規則服藥衛教、依醫囑給予或調整常規藥物、執行PRN藥物給予/打針、執行保護性約束入保護室、維持點滴/抗生素治療、留置尿管護理）。
                    4. R (Response): 記錄病人接受措施後的反應或當前評估（如：勸說後可配合服下藥物、步態緩慢尚穩、主訴幻聽已有改善、情緒趨向平靜等）。
                    5. T (Teaching): 若有相關衛教請精簡列出（如：加強規則服藥重要性、糖尿病飲食衛教，若無則可省略或併入A）。
                    
                    【文字要求】：結構清晰、重點突出，專有名詞與醫學縮寫使用正確。
                    """

                # 呼叫模型
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"請將以下臨床交班內容整理成標準的專業護理紀錄：\n{raw_notes}",
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
