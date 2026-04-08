import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Logistics Cửa khẩu", layout="wide")

# Khởi tạo kết nối với Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

gates = ["Hữu Nghị", "Lào Cai", "Móng Cái", "Tân Thanh"]
# --- CƠ SỞ DỮ LIỆU THÔNG TIN CỬA KHẨU ---
gate_info = {
    "Hữu Nghị": {
        "mieu_ta": "Cửa khẩu Quốc tế Hữu Nghị (Lạng Sơn) là điểm nối quan trọng trên hành lang kinh tế Nam Ninh - Lạng Sơn - Hà Nội. Thế mạnh lớn nhất là xuất nhập khẩu máy móc, thiết bị và xuất khẩu trái cây chính ngạch.",
        "anh_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80" 
    },
    "Lào Cai": {
        "mieu_ta": "Cửa khẩu Quốc tế Kim Thành (Lào Cai) đóng vai trò chiến lược kết nối với tỉnh Vân Nam (Trung Quốc). Nổi bật với khả năng thông quan hàng nông sản nhanh chóng và hệ thống đường cao tốc nối liền thủ đô.",
        "anh_url": "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?auto=format&fit=crop&w=800&q=80" 
    },
    "Móng Cái": {
        "mieu_ta": "Cửa khẩu Quốc tế Móng Cái (Quảng Ninh) sở hữu lợi thế to lớn về giao thương đường bộ lẫn đường biển. Khu vực này đang được đầu tư mạnh mẽ về hạ tầng logistics và hệ thống kho bãi hiện đại.",
        "anh_url": "https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80" 
    },
    "Tân Thanh": {
        "mieu_ta": "Cửa khẩu phụ Tân Thanh (Lạng Sơn) là trung tâm giao thương hàng nông sản, trái cây lớn nhất biên giới phía Bắc. Lượng xe tải đổ về đây vào mùa vụ có thể lên tới hàng nghìn xe mỗi ngày.",
        "anh_url": "https://images.unsplash.com/photo-1605810230434-7631ac76ec81?auto=format&fit=crop&w=800&q=80" 
    }
}

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
    st.write("Vui lòng đọc kỹ thông tin cửa khẩu trước khi đưa ra dự báo bằng số liệu tuyệt đối.")
    
    # 1. Bắt người dùng chọn cửa khẩu trước tiên
    selected_gate = st.selectbox("📌 Chọn cửa khẩu bạn muốn đánh giá:", gates)
    
    # 2. HIỂN THỊ THÔNG TIN GIỚI THIỆU TỰ ĐỘNG BẰNG GIAO DIỆN CHIA CỘT
    st.markdown("---")
    col_img, col_text = st.columns([1, 2]) # Khung ảnh chiếm 1 phần, Khung chữ chiếm 2 phần
    
    with col_img:
        st.image(gate_info[selected_gate]["anh_url"], use_container_width=True)
        
    with col_text:
        st.subheader(f"Thông tin: Cửa khẩu {selected_gate}")
        st.write(gate_info[selected_gate]["mieu_ta"])
        st.info("💡 Bạn chỉ đang đánh giá riêng cửa khẩu này. Các cửa khẩu khác không bị ảnh hưởng.")
    st.markdown("---")
    
    # 3. Giao diện nhập liệu
    defaults = {
        "Hữu Nghị": [3000.0, 730, 815.0, 72.0],
        "Lào Cai": [1800.0, 300, 1084.0, 96.0],
        "Móng Cái": [4000.0, 300, 182.0, 60.0],
        "Tân Thanh": [1500.0, 600, 150.0, 48.0]
    }
    
    with st.form("form_danh_gia"):
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
            
            existing_data = get_all_data()
            new_data = pd.DataFrame([new_record])
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            
            conn.update(data=updated_df)
            st.success(f"✅ Đã ghi nhận thành công dữ liệu cho cửa khẩu {selected_gate}!")

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
