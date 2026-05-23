import streamlit as st
from google import genai
from google.genai import types

# 將 layout 改為 "wide"（寬版模式）
st.set_page_config(page_title="AI 護理紀錄自動整理系統", page_icon="🩺", layout="wide")

# 側邊欄：設定自動填入的預設金鑰
with st.sidebar:
    st.header("🔑 API 設定")
    
    # 【請在此處填入你的 Gemini 金鑰】
    default_key = "AIzaSyC2UTzsT9VXCqLKMVz8hs7mb8jTimm0kt4"
    
    # 自動填入金鑰，並隱藏欄位內容
    api_key = st.text_input("請輸入您的 Gemini API Key:", value=default_key, type="password")
    st.markdown("[如何取得免費的 Gemini API Key?](https://aistudio.google.com/)")

# ================= 🔒 密碼登入關卡設計 =================
st.title("🔐 系統安全登入")

# 建立一個讓使用者輸入登入密碼的框框
login_password = st.text_input("本系統僅供內部人員使用，請輸入登入密碼：", type="password")

# 檢查密碼是否正確（設定為你指定的 820719）
if login_password != "820719":
    if login_password == "":
        st.info("💡 請在上方欄位輸入正確的密碼以解鎖系統。")
    else:
        st.error("❌ 密碼錯誤！請重新輸入。")
    st.stop() # 如果密碼不對，程式碼會在此處中斷，不顯示下方的功能
# =======================================================

# ---- 🔓 密碼正確才會顯示以下主畫面 ----
st.write("---") # 分隔線
st.title("🩺 AI 護理紀錄自動整理系統")
st.write("將破碎、口語化的臨床交班或隨手筆記，自動轉換為標準的醫療紀錄格式。")

# 主要介面
format_type = st.radio("請選擇欲轉換的紀錄格式：", ["SOAP", "Focus Charting (DART)"], horizontal=True)

raw_notes = st.text_area(
    "請輸入原始口語筆記或交班重點：", 
    placeholder="例如：302床林阿伯，早上10點血壓168/95，頭很脹、有點暈。給予Hydralazine 1amp IV... ",
    height=180
)

# 執行轉換按鈕
if st.button("🪄 開始自動整理", type="primary"):
    if not api_key:
        st.error("請在左側邊欄確認已輸入您的 Gemini API Key 才能開始使用喔！")
    elif not raw_notes.strip():
        st.warning("請先輸入護理筆記內容。")
    else:
        with st.spinner("AI 正在專業整理中，請稍候..."):
            try:
                # 初始化 Gemini 客戶端
                client = genai.Client(api_key=api_key)
                
                # 設定系統提示詞
                if format_type == "SOAP":
                    system_instruction = """
                    你是一位專業的資深臨床護理師。請將使用者輸入的破碎、口語化護理內容，整理成標準的 SOAP 護理紀錄格式。
                    - S (Subjective): 主觀敘述
                    - O (Objective): 客觀評估
                    - A (Assessment): 護理評估
                    - P (Plan): 護理計畫
                    請確保專有名詞與醫學縮寫使用正確，語氣專業、客觀、精簡。
                    """
                else:
                    system_instruction = """
                    你是一位專業的資深臨床護理師。請將使用者輸入的破碎、口語化護理內容，整理成標準的 Focus Charting (DART) 護理紀錄格式。
                    - Focus (焦點)
                    - D (Data): 資料
                    - A (Action): 措施
                    - R (Response): 反應
                    - T (Teaching): 衛教
                    請確保專有名詞與醫學縮寫使用正確，語氣專業、客觀、精簡。
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
                
                # 加上 wrap_lines=True，強迫反灰區塊內的文字自動換行
                st.code(response.text, language="markdown", wrap_lines=True)
                st.caption("💡 您可以點擊右上角的按鈕直接複製文字。")
                
            except Exception as e:
                st.error(f"轉換過程中發生錯誤: {str(e)}")
