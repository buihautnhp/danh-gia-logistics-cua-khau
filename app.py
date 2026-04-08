import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Đánh giá Logistics", layout="wide")

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
gates = ["Hữu Nghị", "Lào Cai", "Móng Cái", "Tân Thanh"]

# --- HÀM ĐỌC DỮ LIỆU ---
def get_all_data():
    try:
        return conn.read(worksheet="Sheet1", ttl=0)
    except:
        return pd.DataFrame(columns=["Gate", "XNK", "Xe", "KCN", "ThongQuan", "Diem_Danh_Gia", "Timestamp"])

# --- CƠ SỞ DỮ LIỆU ẢNH (Giữ nguyên tính năng ảnh) ---
gate_info = {
    "Hữu Nghị": {
        "mieu_ta": "Cửa khẩu Quốc tế Hữu Nghị (Lạng Sơn) là điểm nối quan trọng trên hành lang kinh tế Nam Ninh - Lạng Sơn - Hà Nội.",
        "anh_url": "https://i.postimg.cc/x1y6R5mN/Huu-Nghi.jpg" 
    },
    "Lào Cai": {
        "mieu_ta": "Cửa khẩu Quốc tế Kim Thành (Lào Cai) đóng vai trò chiến lược kết nối với tỉnh Vân Nam (Trung Quốc).",
        "anh_url": "https://i.postimg.cc/jSQMXcfz/Lao-Cai.png" 
    },
    "Móng Cái": {
        "mieu_ta": "Cửa khẩu Quốc tế Móng Cái (Quảng Ninh) sở hữu lợi thế to lớn về giao thương đường bộ lẫn đường biển.",
        "anh_url": "https://i.postimg.cc/dVm5B6Cr/Mong-Cai.jpg" 
    },
    "Tân Thanh": {
        "mieu_ta": "Cửa khẩu phụ Tân Thanh (Lạng Sơn) là trung tâm giao thương hàng nông sản, trái cây lớn nhất biên giới phía Bắc.",
        "anh_url": "https://i.postimg.cc/nhY3k2m4/Tan-Thanh.jpg" 
    }
}

st.title("Hệ thống Đánh giá Tiềm năng Logistics Cửa khẩu")
menu = st.sidebar.radio("Vai trò:", ["Người Đánh Giá", "Quản Trị Viên (Admin)"])

# ==========================================
# TAB 1: NGƯỜI ĐÁNH GIÁ (EVALUATOR)
# ==========================================
if menu == "Người Đánh Giá":
    st.header("Nhập số liệu thực tế")
    
    selected_gate = st.selectbox("📌 Chọn cửa khẩu bạn muốn đánh giá:", gates)
    
    st.markdown("---")
    col_img, col_text = st.columns([1, 2])
    with col_img:
        st.image(gate_info[selected_gate]["anh_url"], use_container_width=True)
    with col_text:
        st.subheader(f"Thông tin: Cửa khẩu {selected_gate}")
        st.write(gate_info[selected_gate]["mieu_ta"])
    st.markdown("---")
    
    defaults = {
        "Hữu Nghị": [3000.0, 730, 815.0, 72.0],
        "Lào Cai": [1800.0, 300, 1084.0, 96.0],
        "Móng Cái": [4000.0, 300, 182.0, 60.0],
        "Tân Thanh": [1500.0, 600, 150.0, 48.0]
    }
    
    with st.form("form_danh_gia", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        xnk = c1.number_input("XNK (Tr.USD)", value=defaults[selected_gate][0], min_value=0.0, step=10.0)
        xe = c2.number_input("Số xe/ngày", value=defaults[selected_gate][1], min_value=0, step=1)
        kcn = c3.number_input("KCN (ha)", value=defaults[selected_gate][2], min_value=0.0, step=1.0)
        tq = c4.number_input("Thông quan (h)", value=defaults[selected_gate][3], min_value=0.0, step=1.0)
            
        submit = st.form_submit_button("Gửi đánh giá & Xem điểm")
        
        if submit:
            st.cache_data.clear() 
            df_old = get_all_data()
            
            # Tính toán Min-Max tức thì cho Evaluator
            new_record = {"Gate": selected_gate, "XNK": xnk, "Xe": xe, "KCN": kcn, "ThongQuan": tq}
            df_temp = pd.concat([df_old, pd.DataFrame([new_record])], ignore_index=True)
            
            for col in ["XNK", "Xe", "KCN", "ThongQuan"]:
                df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce').fillna(0)
                
            def calc_norm(col, val, inverse=False):
                c_min = df_temp[col].min()
                c_max = df_temp[col].max()
                if c_max == c_min: return 1.0
                if inverse: return (c_max - val) / (c_max - c_min)
                return (val - c_min) / (c_max - c_min)

            norm_xnk = calc_norm("XNK", xnk)
            norm_xe = calc_norm("Xe", xe)
            norm_kcn = calc_norm("KCN", kcn)
            norm_tq = calc_norm("ThongQuan", tq, True)
            
            # Trọng số tiêu chuẩn (40-20-20-20) cho điểm cá nhân
            current_score = (norm_xnk*0.4 + norm_xe*0.2 + norm_kcn*0.2 + norm_tq*0.2) * 100
            current_score = round(current_score, 1)
            
            # Bắn pháo hoa và hiện điểm
            st.balloons()
            st.success(f"🎉 **Đã ghi nhận! Điểm tiềm năng bạn vừa đánh giá cho {selected_gate} là: {current_score} / 100 điểm**")
            
            # Lưu vào Sheet kèm Timestamp
            new_record["Diem_Danh_Gia"] = current_score
            new_record["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            updated_df = pd.concat([df_old, pd.DataFrame([new_record])], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)

# ==========================================
# TAB 2: QUẢN TRỊ VIÊN (ADMIN) 
# ==========================================
elif menu == "Quản Trị Viên (Admin)":
    pwd = st.sidebar.text_input("Mật khẩu Admin:", type="password")
    if pwd == "admin123":
        st.header("Báo cáo Leaderboard Tổng Hợp")
        
        df = get_all_data()
        
        if df.empty or len(df) == 0:
            st.info("Chưa có dữ liệu nào trong Google Sheet.")
        else:
            # HIỂN THỊ ĐIỂM TRUNG BÌNH CÁ NHÂN TỪ SHEET (CỘT DIEM_DANH_GIA)
            st.subheader("1. Điểm Trung Bình Khách Quan (Từ các lượt đánh giá)")
            df['Diem_Danh_Gia'] = pd.to_numeric(df['Diem_Danh_Gia'], errors='coerce')
            avg_scores = df.groupby('Gate')['Diem_Danh_Gia'].mean().round(1).reset_index()
            st.bar_chart(data=avg_scores.set_index('Gate')['Diem_Danh_Gia'])
            
            st.markdown("---")
            
            # GIỮ NGUYÊN QUYỀN NĂNG SLIDER CỦA ADMIN
            st.subheader("2. Mô phỏng Chiến lược Admin (Điều chỉnh trọng số)")
            st.write("Bảng dưới đây tính toán lại bảng xếp hạng dựa trên dữ liệu thô và trọng số mới của bạn.")
            c1, c2, c3, c4 = st.columns(4)
            w_xnk = c1.slider("XNK (%)", 0, 100, 40)
            w_xe = c2.slider("Xe (%)", 0, 100, 20)
            w_kcn = c3.slider("KCN (%)", 0, 100, 20)
            w_tq = c4.slider("Thông quan (%)", 0, 100, 20)
            
            if (w_xnk + w_xe + w_kcn + w_tq) != 100:
                st.error("Tổng trọng số phải bằng đúng 100%!")
            else:
                for col in ["XNK", "Xe", "KCN", "ThongQuan"]:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                df_avg = df.groupby('Gate')[["XNK", "Xe", "KCN", "ThongQuan"]].mean().reset_index()
                
                for gate in gates:
                    if gate not in df_avg['Gate'].values:
                        df_avg.loc[len(df_avg)] = [gate, 0, 0, 0, 0]
                
                df_norm = pd.DataFrame()
                df_norm['Gate'] = df_avg['Gate']
                
                for col in ["XNK", "Xe", "KCN"]:
                    min_val = df_avg[col].min()
                    max_val = df_avg[col].max()
                    if max_val == min_val:
                        df_norm[col] = 0 if max_val == 0 else 1.0
                    else:
                        df_norm[col] = (df_avg[col] - min_val) / (max_val - min_val)
                        
                col = "ThongQuan"
                min_val = df_avg[col].min()
                max_val = df_avg[col].max()
                if max_val == min_val:
                    df_norm[col] = 0 if max_val == 0 else 1.0
                else:
                    df_norm[col] = (max_val - df_avg[col]) / (max_val - min_val)
                
                df_norm['Điểm Mô Phỏng'] = (
                    df_norm['XNK'] * (w_xnk/100) + df_norm['Xe'] * (w_xe/100) +
                    df_norm['KCN'] * (w_kcn/100) + df_norm['ThongQuan'] * (w_tq/100)
                ) * 100
                
                df_norm['Điểm Mô Phỏng'] = df_norm['Điểm Mô Phỏng'].round(1)
                df_norm = df_norm.set_index('Gate').reindex(gates).reset_index()
                
                st.bar_chart(data=df_norm.set_index('Gate')['Điểm Mô Phỏng'])
