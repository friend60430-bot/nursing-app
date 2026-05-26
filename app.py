import streamlit as st
import time

# ================= 🔒 從後台安全保險箱讀取金鑰 =================
if "GEMINI_API_KEY" in st.secrets:
    HIDDEN_GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
else:
    HIDDEN_GEMINI_KEY = "未設定"
# =============================================================

# 🎯 已修正：將 initial_sidebar_state 改為 "expanded"，確保左側面板永遠正常顯示！
st.set_page_config(
    page_title="AI 護理紀錄自動整理系統", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= 🎨 終極全頂部移除 CSS（讓所有官方按鈕徹底消失 ＆ 文字放大） =================
st.markdown("""
    <style>
        /* 🚨 終極大絕招：直接將 Streamlit 頂部黑邊與所有官方按鈕整排永久隱藏、高度歸零 */
        /* 這會使貓咪、Fork、三個點全部徹底消失，再也無法顯示或點擊 */
        header, [data-testid="stHeader"] {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
        }
        
        /* 修正頂部被移除後可能產生的網頁排版空白 */
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
        /* 輸入框內的文字放大 */
        textarea, input {
            font-size: 20px !important;
        }
        /* 反灰結果區塊的文字放大 */
        code, pre {
            font-size: 19px !important;
            line-height: 1.6 !important;
        }
        /* 側邊欄寬度微調 */
        [data-testid="stSidebar"] {
            min-width: 320px;
        }
    </style>
""", unsafe_allow_html=True)
# =============================================================


# 初始化安全驗證狀態
if "login_success" not in st.session_state:
    st.session_state["login_success"] = False

# ================= 🔒 左邊面板：安全登入設計 =================
with st.sidebar:
    st.header("🔐 系統安全登入")
    login_password = st.text_input("請輸入系統登入密碼：", type="password")
    st.write("---")
    st.caption("本系統僅供內部授權人員使用。")

# 密碼檢查與轉跳邏輯
if login_password == "820719":
    if not st.session_state["login_success"]:
        st.title("🔐 安全認證成功")
        st.success("✅ 密碼正確！正在進行安全加密連線...")
        
        # 轉跳動畫進度條
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.01)
            progress_bar.progress(percent_complete + 1)
            
        st.session_state["login_success"] = True
        st.rerun()
else:
    st.session_state["login_success"] = False
    st.title("🔐 歡迎使用 AI 護理紀錄自動整理系統")
    if login_password == "":
        st.info("💡 請在【左側面板】輸入正確的系統密碼以解鎖功能。")
    else:
        st.error("❌ 密碼錯誤！請重新輸入。")
    st.stop()
# =============================================================


# ---- 🔓 轉跳成功後才會解鎖顯示以下主畫面 ----
st.title("🩺 AI 護理紀錄自動整理系統")
st.write("將破碎、口語化的臨床交班或隨手筆記，自動轉換為標準的醫療紀錄格式。")

# 主要介面
format_type = st.radio("請選擇欲轉換的紀錄格式：", ["SOAP", "Focus Charting (DART)"], horizontal=True)

# 💡 這裡已將 placeholder 設定為空字串 ""，輸入框內不會再出現任何反灰範例文字
raw_notes = st.text_area(
    "請輸入原始口語筆記或交班重點：", 
    placeholder="",
    height=250 
)

# 🎯 執行轉換按鈕（已包含符號）
if st.button("👉 🪄 開始自動整理 ⚡", type="primary"):
    if HIDDEN_GEMINI_KEY == "未設定":
        st.error("後台安全密鑰尚未設定，請先至 Streamlit 後台 Secrets 填寫 GEMINI_API_KEY。")
    elif not raw_notes.strip():
        st.warning("請先輸入護理筆記內容。")
    else:
        with st.spinner("AI 正在專業整理中，請稍候..."):
            try:
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=HIDDEN_GEMINI_KEY)
                
                if format_type == "SOAP":
                    system_instruction = """
                    你是一位精通精神醫療科（Psychiatric Ward）與一般內外科臨床護理的資深護理師。
                    請將使用者提供的精神科臨床口語、交班範本片段，整理成正式、精簡且專業的 SOAP 護理紀錄。

                    【撰寫準則】：
                    1. S (Subjective): 記錄病人主觀訴求（如：幻聽/幻覺內容、頭暈、主訴幻聽改善、對家庭或生日的想法等），儘量精準摘錄重要字句。
                    2. O (Objective): 記錄客觀觀察。包含：
                       - 精神症狀與行為（自語、意念飛躍、吐藥、服藥推拖、言談混亂等）。
                       - 臨床重要數據（如：血壓/脈搏 V/S、每日多時段血糖 F/S 追蹤、連續抽血數值如 CPK 變化、每日體重 BW、I/O 引流量與點滴進度）。
                       - 生理評估與照顧狀態（留置尿管色澤、步態緩慢、服藥後軟腳現象、保護性約束、家屬/看護陪伴等）。
                       - 醫療動態（會診回覆、新增或更換醫學用藥、預計 MBD 出院等）。
                    3. A (Assessment): 針對精神、心理及內外科合併症進行專業護理評估（如：知覺感受改變：幻聽、潛在危險性：自殺/自傷、潛在危險性：跌倒、服藥遵從性不佳/拒藥行為、高血糖狀態、組織灌流改變等）。
                    4. P (Plan): 記錄執行的護理措施與計畫（如：續防自殺/維持安全、加強防跌注意事項、加強規則服藥與防吐藥衛教、給予傾聽 or 安撫、維持約束/尿管照護、持續追蹤各項生理指標與 data、準備出院護理指導等）。
                    
                    【文字要求】：專業、精簡、流暢，專有名詞與醫學縮寫（如：Auditory hallucination, Compliance, MBD）使用正確。
                    """
                else:
                    system_instruction = """
                    你是一位精通精神醫療科（Psychiatric Ward）與一般內外科臨床護理的資深護理師。
                    請將使用者提供的精神科臨床口語、交班範本片段，整理成標準的 Focus Charting (DART) 護理紀錄。

                    【撰寫準則】：
                    1. Focus (焦點): 確立明確的焦點問題（例如：知覺感受改變：幻聽、潛在危險性：自傷、潛在危險性：跌倒、服藥遵從性不佳、高血糖狀態、體液容積改變、準備出院）。
                    2. D (Data): 包含病人主客觀資料。精準整合病人主訴、行為表現（吐藥、拒藥、言談混亂）、所有臨床數據（各日 F/S 血糖、連續 CPK 抽血追蹤、V/S 數據如 116/65 mmHg、I/O 及 BW）與生理狀態（服藥後軟腳、步態、留置尿管順暢色黃等）。
                    3. A (Action): 記錄護理人員執行的醫療與護理措施（如：予傾聽、適時安撫、加強防跌注意事項、加強規則服藥衛教與執行服藥監督、依醫囑調整藥物與施打點滴/抗生素、維持尿管/約束護理、預備 MBD 衛教等）。
                    4. R (Response): 記錄病人接受措施後的反應 or 當前評估（如：勸說後可配合服下藥物、主訴幻聽改善、心情趨平靜、外出狀況可等）。
                    5. T (Teaching): 若有相關衛教請精簡列出（如：防跌衛教、糖尿病飲食與用藥指導、規則服藥重要性，若無則可省略或併入A）。
                    
                    【文字要求】：結構清晰、重點突出，醫學術語與縮寫呈現需精準專業。
                    """

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"請將以下臨床交班內容整理成標準的專業護理紀錄：\n{raw_notes}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2,
                    )
                )
                
                st.success("✨ 整理完成！")
                st.markdown("### 📋 生成紀錄結果")
                st.code(response.text, language="markdown", wrap_lines=True)
                st.caption("💡 您可以點擊右上角的按鈕直接複製文字。")
                
            except Exception as e:
                st.error("轉換過程中發生錯誤，請檢查後台金鑰或網路連線。")
                st.exception(e)
