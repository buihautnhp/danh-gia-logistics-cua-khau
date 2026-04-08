import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Logistics Cửa khẩu", layout="wide")

# Khởi tạo kết nối với Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

gates = ["Hữu Nghị", "Lào Cai", "Móng Cái", "Tân Thanh"]

# Hàm đọc dữ liệu từ Sheet
def get_all_data():
    try:
        # Đọc dữ liệu từ sheet tên là "Sheet1" (mặc định)
        return conn.read(ttl="5m") # Lưu bộ nhớ tạm 5 phút để load nhanh hơn
    except:
        return pd.DataFrame(columns=["Gate", "XNK", "Xe", "KCN", "ThongQuan", "Timestamp"])

# --- GIAO DIỆN ---
st.title("Hệ thống Đánh giá Logistics & Google Sheets")

menu = st.sidebar.radio("Vai trò:", ["Người Đánh Giá", "Quản Trị Viên (Admin)"])

if menu == "Người Đánh Giá":
    st.header("Nhập số liệu thực tế")
    st.write("Bạn có thể chọn đánh giá một cửa khẩu cụ thể. Các cửa khẩu khác sẽ không bị ảnh hưởng.")
    
    # Dữ liệu mặc định để mồi sẵn cho người dùng đỡ phải gõ từ số 0
    defaults = {
        "Hữu Nghị": [3000.0, 730, 815.0, 72.0],
        "Lào Cai": [1800.0, 300, 1084.0, 96.0],
        "Móng Cái": [4000.0, 300, 182.0, 60.0],
        "Tân Thanh": [1500.0, 600, 150.0, 48.0]
    }
    
    with st.form("form_danh_gia"):
        # Cho phép người dùng CHỌN 1 cửa khẩu thay vì nhập cả 4
        selected_gate = st.selectbox("📌 Chọn cửa khẩu bạn muốn đánh giá:", gates)
        
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        
        # Tự động điền số gợi ý dựa trên cửa khẩu đã chọn
        xnk = c1.number_input("XNK (Tr.USD)", value=defaults[selected_gate][0], min_value=0.0, step=10.0)
        xe = c2.number_input("Số xe/ngày", value=defaults[selected_gate][1], min_value=0, step=1)
        kcn = c3.number_input("KCN (ha)", value=defaults[selected_gate][2], min_value=0.0, step=1.0)
        tq = c4.number_input("Thông quan (h)", value=defaults[selected_gate][3], min_value=0.0, step=1.0)
            
        submit = st.form_submit_button("Gửi đánh giá cửa khẩu này")
        
        if submit:
            # Chỉ tạo 1 bản ghi (1 dòng) duy nhất cho cửa khẩu được chọn
            new_record = {
                "Gate": selected_gate, 
                "XNK": xnk, 
                "Xe": xe, 
                "KCN": kcn, 
                "ThongQuan": tq, 
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            existing_data = get_all_data()
            new_data = pd.DataFrame([new_record])
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            
            # Ghi lên Google Sheet
            conn.update(data=updated_df)
            st.success(f"✅ Đã ghi nhận thành công dữ liệu cho cửa khẩu {selected_gate}! Các cửa khẩu khác không bị ảnh hưởng.")

elif menu == "Quản Trị Viên (Admin)":
    pwd = st.sidebar.text_input("Mật khẩu Admin:", type="password")
    if pwd == "NCKH2026":
        st.header("Báo cáo tổng hợp từ Google Sheet")
        
        df = get_all_data()
        
        if df.empty:
            st.info("Chưa có dữ liệu nào trong Sheet.")
        else:
            # Hiển thị bảng trọng số của Admin (Bạn có thể điều chỉnh như trước)
            st.subheader("Trọng số đánh giá")
            c1, c2, c3, c4 = st.columns(4)
            w_xnk = c1.slider("XNK (%)", 0, 100, 40)
            w_xe = c2.slider("Xe (%)", 0, 100, 20)
            w_kcn = c3.slider("KCN (%)", 0, 100, 20)
            w_tq = c4.slider("Thông quan (%)", 0, 100, 20)

            # Tính toán dựa trên dữ liệu từ Sheet (Sử dụng hàm tính trung bình như trước)
            # ... (Phần logic tính toán tương tự code cũ nhưng lấy từ 'df')
            
            st.subheader("Dữ liệu thô từ Sheet")
            st.dataframe(df)
