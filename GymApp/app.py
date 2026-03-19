import streamlit as st
import pandas as pd
import os

# 設定頁面標題與圖示
st.set_page_config(page_title="肌力與體能動作庫", page_icon="🏋️", layout="wide")

# 資料檔案名稱
DATA_FILE = 'exercises.csv'

# 如果檔案不存在，建立一個空的資料表
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=['動作名稱', '分類', '使用肌群', '器材', '操作重點'])
    df.to_csv(DATA_FILE, index=False)

# 讀取資料的函式
def load_data():
    return pd.read_csv(DATA_FILE)

# 儲存資料的函式
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- 側邊欄：新增動作功能 ---
st.sidebar.header("➕ 新增訓練動作")
with st.sidebar.form("add_form", clear_on_submit=True):
    name = st.text_input("動作名稱 (例如: 背槓深蹲)")
    category = st.selectbox("動作分類", ["下肢推", "下肢拉", "上肢推", "上肢拉", "核心", "其他"])
    muscles = st.text_input("使用肌群 (例如: 股四頭肌, 臀大肌)")
    equipment = st.text_input("使用器材 (例如: 槓鈴)")
    tips = st.text_area("操作重點 (技巧說明)")
    
    submit = st.form_submit_button("儲存到資料庫")

    if submit:
        if name:
            df = load_data()
            new_row = pd.DataFrame([[name, category, muscles, equipment, tips]], 
                                    columns=['動作名稱', '分類', '使用肌群', '器材', '操作重點'])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.sidebar.success(f"✅ 已成功儲存: {name}")
        else:
            st.sidebar.error("❌ 請輸入動作名稱！")

# --- 主畫面：瀏覽與篩選 ---
st.title("🏋️ 肌力與體能訓練動作庫")
st.write("這是一個專為整理動作分類與操作技巧設計的工具。")

df = load_data()

# 搜尋與篩選列
st.subheader("🔍 快速搜尋")
col_search1, col_search2 = st.columns([1, 1])
with col_search1:
    search_query = st.text_input("搜尋動作名稱或肌群")
with col_search2:
    filter_cat = st.multiselect("依分類篩選", options=["下肢推", "下肢拉", "上肢推", "上肢拉", "核心", "其他"])

# 執行篩選邏輯
display_df = df.copy()
if filter_cat:
    display_df = display_df[display_df['分類'].isin(filter_cat)]
if search_query:
    display_df = display_df[
        display_df['動作名稱'].str.contains(search_query, case=False, na=False) | 
        display_df['使用肌群'].str.contains(search_query, case=False, na=False)
    ]

st.divider()

# 顯示動作清單
if not display_df.empty:
    for index, row in display_df.iterrows():
        with st.expander(f"📌 {row['動作名稱']} — 【{row['分類']}】"):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.write(f"**💪 使用肌群：**\n{row['使用肌群']}")
                st.write(f"**🛠️ 使用器材：**\n{row['器材']}")
            with c2:
                st.write("**📝 操作重點：**")
                st.info(row['操作重點'] if row['操作重點'] else "暫無說明")
            
            # 刪除按鈕
            if st.button(f"🗑️ 刪除 {row['動作名稱']}", key=f"del_{index}"):
                df = df.drop(index)
                save_data(df)
                st.rerun()
else:
    st.info("目前資料庫是空的，請從左側選單新增第一個動作！")