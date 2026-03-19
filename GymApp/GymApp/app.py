import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="專業訓練管理系統 v3.0", page_icon="🏋️", layout="wide")

DATA_FILE = 'exercises.csv'

# 奧運正式項目清單
OLYMPIC_SPORTS_LIST = ["田徑", "游泳", "體操", "舉重", "籃球", "足球", "排球", "羽球", "桌球", "網球","手球", "高爾夫", "拳擊", "柔道", "空手道", "跆拳道", "角力", "擊劍", "射箭","射擊", "划船", "輕艇", "帆船", "馬術", "現代五項", "鐵人三項", "自行車", "滑板", "運動攀登", "衝浪", "霹靂舞", "橄欖球", "曲棍球", "棒球/壘球"]

# --- 資料處理邏輯 ---
def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=['動作名稱', '分類', '使用肌群', '器材', '操作重點', '媒體連結', '訓練效果說明'])
        df.to_csv(DATA_FILE, index=False)
        return df
    df = pd.read_csv(DATA_FILE)
    # 自動補齊新欄位：訓練效果說明
    if '訓練效果說明' not in df.columns:
        df['訓練效果說明'] = ""
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# --- 頁面分頁設定 ---
tab1, tab2 = st.tabs(["📚 動作資料庫管理", "📋 今日訓練課表生成"])

# --- Tab 1: 動作資料庫 (含效果說明) ---
with tab1:
    st.header("動作庫與訓練說明")
    
    # 側邊欄：新增/編輯動作
    st.sidebar.header("➕ 管理動作")
    with st.sidebar.form("add_form", clear_on_submit=True):
        name = st.text_input("動作名稱")
        category = st.selectbox("功能分類", ["下肢推", "下肢拉", "上肢推", "上肢拉", "爆發力", "肌耐力", "最大肌力", "CT訓練", "核心", "其他"])
        muscle_options = ["胸大肌", "背括肌", "三角肌", "股四頭肌", "腿後腱", "臀大肌", "核心群", "全身性"]
        selected_muscles = st.multiselect("主要使用肌群", options=muscle_options)
        equipment = st.text_input("所需器材")
        media_link = st.text_input("影片/圖片連結")
        tips = st.text_area("教學重點")
        performance = st.text_area("🚀 訓練效果說明")
        
        submit = st.form_submit_button("儲存至資料庫")
        if submit and name:
            new_row = pd.DataFrame([[name, category, ", ".join(selected_muscles), equipment, tips, media_link, performance]], 
                                    columns=['動作名稱', '分類', '使用肌群', '器材', '操作重點', '媒體連結', '訓練效果說明'])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.sidebar.success(f"✅ {name} 已更新")
            st.rerun()

    # 搜尋與顯示
    search = st.text_input("🔍 快速搜尋動作...", placeholder="輸入動作或肌群")
    display_df = df[df['動作名稱'].str.contains(search, case=False, na=False)] if search else df
    
    for idx, row in display_df.iterrows():
        with st.expander(f"⭐ {row['動作名稱']} ({row['分類']})"):
            c1, c2 = st.columns([1, 1])
            with c1:
                st.write(f"**💪 肌群:** `{row['使用肌群']}` | **🛠️ 器材:** {row['器材']}")
                st.info(f"**💡 教學重點:**\n{row['操作重點']}")
                st.success(f"**📈 訓練效果說明:**\n{row['訓練效果說明']}")
            with c2:
                if "youtube.com" in str(row['媒體連結']) or "youtu.be" in str(row['媒體連結']):
                    st.video(row['媒體連結'])
                elif str(row['媒體連結']).endswith(('.png', '.jpg', '.jpeg')):
                    st.image(row['媒體連結'], use_container_width=True)
            
            if st.button(f"🗑️ 移除", key=f"del_{idx}"):
                df = df.drop(idx).reset_index(drop=True)
                save_data(df)
                st.rerun()

# --- Tab 2: 今日訓練課表生成 ---
with tab2:
    st.header(f"📅 今日訓練課表 ({datetime.now().strftime('%Y-%m-%d')})")
    
    if df.empty:
        st.warning("動作庫目前沒有資料，請先至『動作資料庫管理』新增動作。")
    else:
        # 1. 選擇動作
        selected_ex = st.multiselect("🎯 從動作庫挑選今日訓練動作", options=df['動作名稱'].tolist())
        
        if selected_ex:
            st.write("---")
            st.subheader("📝 設定訓練參數")
            
            workout_data = []
            for ex in selected_ex:
                st.markdown(f"#### **{ex}**")
                col_p1, col_p2, col_p3, col_p4 = st.columns(4)
                with col_p1:
                    sets = st.number_input(f"組數 (Sets)", min_value=1, max_value=20, value=3, key=f"sets_{ex}")
                with col_p2:
                    reps = st.text_input(f"次數 (Reps)", value="8-12", key=f"reps_{ex}")
                with col_p3:
                    weight = st.text_input(f"重量 (kg)", value="20", key=f"weight_{ex}")
                with col_p4:
                    rest = st.text_input(f"休息 (sec)", value="90", key=f"rest_{ex}")
                workout_data.append({"動作": ex, "組數": sets, "次數": reps, "重量": weight, "休息": rest})
            
            # 2. 生成預覽表格
            st.write("---")
            st.subheader("📋 課表預覽")
            workout_df = pd.DataFrame(workout_data)
            st.table(workout_df)
            
            # 3. 匯出功能
            if st.button("📱 產生手機截圖格式"):
                st.code(f"【今日訓練課表 - {datetime.now().strftime('%Y-%m-%d')}】\n" + 
                        "\n".join([f"• {d['動作']}: {d['組數']}組 x {d['reps']}次 ({d['重量']}kg)" for d in workout_data]), 
                        language="text")
                st.success("你可以複製上方文字到 Line 或手機備忘錄！")