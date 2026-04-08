import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Đánh giá Logistics", layout="wide")

# Thư mục lưu ảnh (Nếu bạn dùng link online thì không cần quan tâm phần này)
ASSETS_DIR = "assets/portraits"
os.makedirs(ASSETS_DIR, exist_ok=True)

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

gates = ["Hữu Nghị", "Lào Cai", "Móng Cái", "Tân Thanh"]

# --- HÀM ĐỌC DỮ LIỆU (ĐÃ SỬA LỖI GHI ĐÈ) ---
def get_all_data():
    try:
        # SỬA LỖI: Đổi ttl="5m" thành ttl=0 để luôn lấy dữ liệu mới nhất, không bị lưu bộ nhớ tạm
        return conn.read(worksheet="Sheet1", ttl=0)
    except:
        return pd.DataFrame(columns=["Gate", "XNK", "Xe", "KCN", "ThongQuan", "Timestamp"])

# --- CƠ SỞ DỮ LIỆU ẢNH ---
gate_info = {
    "Hữu Nghị": {
        "mieu_ta": "Cửa khẩu Quốc tế Hữu Nghị (Lạng Sơn) là điểm nối quan trọng trên hành lang kinh tế Nam Ninh - Lạng Sơn - Hà Nội.",
        "anh_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80" 
    },
    "Lào Cai": {
        "mieu_ta": "Cửa khẩu Quốc tế Kim Thành (Lào Cai) đóng vai trò chiến lược kết nối với tỉnh Vân Nam (Trung Quốc).",
        "anh_url": "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?auto=format&fit=crop&w=800&q=80" 
    },
    "Móng Cái": {
        "mieu_ta": "Cửa khẩu Quốc tế Móng Cái (Quảng Ninh) sở hữu lợi thế to lớn về giao thương đường bộ lẫn đường biển.",
        "anh_url": "https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80" 
    },
    "Tân Thanh": {
        "mieu_ta": "Cửa khẩu phụ Tân Thanh (Lạng Sơn) là trung tâm giao thương hàng nông sản, trái cây lớn nhất biên giới phía Bắc.",
        "anh_url": "https://images.unsplash.com/photo-1605810230434-7631ac76ec81?auto=format&fit=crop&w=800&q=80" 
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
            
        submit = st.form_submit_button("Gửi đánh giá cửa khẩu này")
        
        if submit:
            new_record = {
                "Gate": selected_gate, 
                "XNK": xnk, 
                "Xe": xe, 
                "KCN": kcn, 
                "ThongQuan": tq, 
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # XÓA BỘ NHỚ TẠM TRƯỚC KHI GHI ĐỂ KHÔNG BỊ GHI ĐÈ
            st.cache_data.clear() 
            
            existing_data = get_all_data()
            new_data = pd.DataFrame([new_record])
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            
            # Ghi lên Sheet
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success(f"✅ Đã ghi nhận thành công! Bạn có thể tiếp tục đánh giá lần nữa.")

# ==========================================
# TAB 2: QUẢN TRỊ VIÊN (ADMIN) - TÍNH ĐIỂM
# ==========================================
elif menu == "Quản Trị Viên (Admin)":
    pwd = st.sidebar.text_input("Mật khẩu Admin:", type="password")
    if pwd == "admin123":
        st.header("Báo cáo Leaderboard (Thang điểm 100)")
        
        # Lấy dữ liệu mới nhất
        df = get_all_data()
        
        if df.empty or len(df) == 0:
            st.info("Chưa có dữ liệu nào trong Google Sheet.")
        else:
            # 1. BẢNG ĐIỀU KHIỂN TRỌNG SỐ
            st.subheader("Cài đặt Trọng số (%)")
            c1, c2, c3, c4 = st.columns(4)
            w_xnk = c1.slider("XNK (%)", 0, 100, 40)
            w_xe = c2.slider("Xe (%)", 0, 100, 20)
            w_kcn = c3.slider("KCN (%)", 0, 100, 20)
            w_tq = c4.slider("Thông quan (%)", 0, 100, 20)
            
            if (w_xnk + w_xe + w_kcn + w_tq) != 100:
                st.error("Tổng trọng số phải bằng đúng 100%!")
            else:
                # 2. THUẬT TOÁN TÍNH TRUNG BÌNH & CHUẨN HÓA
                # Bước A: Tính số liệu trung bình của từng cửa khẩu từ TẤT CẢ các lượt đánh giá
                # Ép kiểu dữ liệu về số thực (float) để tránh lỗi tính toán
                for col in ["XNK", "Xe", "KCN", "ThongQuan"]:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                df_avg = df.groupby('Gate')[["XNK", "Xe", "KCN", "ThongQuan"]].mean().reset_index()
                
                # Bổ sung các cửa khẩu chưa có ai đánh giá (để biểu đồ không bị khuyết)
                for gate in gates:
                    if gate not in df_avg['Gate'].values:
                        df_avg.loc[len(df_avg)] = [gate, 0, 0, 0, 0]
                
                df_norm = pd.DataFrame()
                df_norm['Gate'] = df_avg['Gate']
                
                # Bước B: Chuẩn hóa Min-Max Thuận (XNK, Xe, KCN)
                for col in ["XNK", "Xe", "KCN"]:
                    min_val = df_avg[col].min()
                    max_val = df_avg[col].max()
                    if max_val == min_val:
                        df_norm[col] = 0 if max_val == 0 else 1.0
                    else:
                        df_norm[col] = (df_avg[col] - min_val) / (max_val - min_val)
                        
                # Bước C: Chuẩn hóa Min-Max Nghịch (Thời gian thông quan - càng nhỏ càng tốt)
                col = "ThongQuan"
                min_val = df_avg[col].min()
                max_val = df_avg[col].max()
                if max_val == min_val:
                    df_norm[col] = 0 if max_val == 0 else 1.0
                else:
                    df_norm[col] = (max_val - df_avg[col]) / (max_val - min_val)
                
                # Bước D: Nhân trọng số tính điểm Tổng (Thang 100)
                df_norm['Điểm Đánh Giá'] = (
                    df_norm['XNK'] * (w_xnk/100) +
                    df_norm['Xe'] * (w_xe/100) +
                    df_norm['KCN'] * (w_kcn/100) +
                    df_norm['ThongQuan'] * (w_tq/100)
                ) * 100
                
                # Làm tròn 1 chữ số thập phân (VD: 68.2)
                df_norm['Điểm Đánh Giá'] = df_norm['Điểm Đánh Giá'].round(1)
                
                # 3. HIỂN THỊ BIỂU ĐỒ LEADERBOARD
                st.markdown("### 🏆 Bảng Xếp Hạng Tiềm Năng (Leaderboard)")
                
                # Sắp xếp lại thứ tự cột cho đúng với list gates ban đầu
                df_norm = df_norm.set_index('Gate').reindex(gates).reset_index()
                
                # Vẽ biểu đồ cột
                st.bar_chart(data=df_norm.set_index('Gate')['Điểm Đánh Giá'])
                
                # Hiển thị bảng số liệu chi tiết
                st.markdown("### 📊 Dữ liệu trung bình các lượt đánh giá")
                st.dataframe(df_avg.set_index('Gate').round(1))
