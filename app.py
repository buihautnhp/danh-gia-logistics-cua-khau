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
    
    with st.form("form_danh_gia"):
        # Tạo bảng nhập liệu
        inputs = []
        for gate in gates:
            st.markdown(f"### Cửa khẩu {gate}")
            c1, c2, c3, c4 = st.columns(4)
            xnk = c1.number_input(f"XNK (Tr.USD) - {gate}", min_value=0.0, step=10.0, key=f"x_{gate}")
            xe = c2.number_input(f"Số xe/ngày - {gate}", min_value=0, step=1, key=f"v_{gate}")
            kcn = c3.number_input(f"KCN (ha) - {gate}", min_value=0.0, step=1.0, key=f"k_{gate}")
            tq = c4.number_input(f"Thông quan (h) - {gate}", min_value=0.0, step=1.0, key=f"t_{gate}")
            
            inputs.append({
                "Gate": gate, "XNK": xnk, "Xe": xe, 
                "KCN": kcn, "ThongQuan": tq, 
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
        submit = st.form_submit_button("Gửi dữ liệu lên Google Sheet")
        
        if submit:
            # Lấy dữ liệu cũ, thêm dữ liệu mới và cập nhật lại Sheet
            existing_data = get_all_data()
            new_data = pd.DataFrame(inputs)
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            
            # Ghi đè lại vào Google Sheet
            conn.update(data=updated_df)
            st.success("✅ Dữ liệu đã được lưu trực tiếp vào Google Sheet của bạn!")

elif menu == "Quản Trị Viên (Admin)":
    pwd = st.sidebar.text_input("Mật khẩu Admin:", type="password")
    if pwd == "admin123":
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
