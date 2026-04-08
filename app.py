import streamlit as st
import pandas as pd
import json
import os

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Đánh giá Trung tâm Logistics", layout="wide")

# File lưu trữ dữ liệu các lượt đánh giá
DATA_FILE = 'evaluations_data.json'

# Danh sách cửa khẩu
gates = ["Hữu Nghị", "Lào Cai", "Móng Cái", "Tân Thanh"]

# Khởi tạo file dữ liệu nếu chưa có
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# --- THUẬT TOÁN TÍNH ĐIỂM ---
def calculate_scores(data, weights):
    if not data: return pd.DataFrame()
    
    # Tính điểm trung bình của các chỉ số thô từ tất cả người dùng
    df_raw = pd.DataFrame(data)
    df_avg = pd.DataFrame(index=gates)
    
    for metric in ["XNK", "Xe", "KCN", "ThongQuan"]:
        df_avg[metric] = [df_raw[df_raw['Gate'] == gate][metric].mean() for gate in gates]
    
    # Chuẩn hóa Min-Max
    df_norm = pd.DataFrame(index=gates)
    
    # Chuẩn hóa thuận (Càng lớn càng tốt)
    for col in ["XNK", "Xe", "KCN"]:
        min_val = df_avg[col].min()
        max_val = df_avg[col].max()
        if max_val == min_val:
            df_norm[col] = 1.0
        else:
            df_norm[col] = (df_avg[col] - min_val) / (max_val - min_val)
            
    # Chuẩn hóa nghịch (Càng nhỏ càng tốt)
    col = "ThongQuan"
    min_val = df_avg[col].min()
    max_val = df_avg[col].max()
    if max_val == min_val:
        df_norm[col] = 1.0
    else:
        df_norm[col] = (max_val - df_avg[col]) / (max_val - min_val)
        
    # Tính điểm tổng có trọng số
    df_norm["DiemTong"] = (
        df_norm["XNK"] * (weights["XNK"]/100) +
        df_norm["Xe"] * (weights["Xe"]/100) +
        df_norm["KCN"] * (weights["KCN"]/100) +
        df_norm["ThongQuan"] * (weights["ThongQuan"]/100)
    ) * 100
    
    return df_norm

# --- GIAO DIỆN CHÍNH ---
st.title("Hệ thống Đánh giá Tiềm năng Logistics Cửa khẩu")

# Chia menu
menu = st.sidebar.radio("Chọn tư cách truy cập:", ["Người Đánh Giá (Evaluator)", "Quản Trị Viên (Admin)"])

# --- TAB 1: NGƯỜI ĐÁNH GIÁ ---
if menu == "Người Đánh Giá (Evaluator)":
    st.header("Nhập liệu thông số dự báo")
    st.write("Vui lòng nhập các chỉ số đánh giá của bạn cho 4 cửa khẩu. Dữ liệu của bạn sẽ được hệ thống ẩn danh và ghi nhận để tính trung bình.")
    
    with st.form("eval_form"):
        # Tạo lưới nhập liệu
        cols = st.columns(4)
        cols[0].markdown("**Cửa khẩu**")
        cols[1].markdown("**Kim ngạch XNK (Tr.USD)**")
        cols[2].markdown("**Lượng xe/ngày**")
        cols[3].markdown("**KCN (ha) / Thông quan (h)**")
        
        # Dữ liệu mặc định gợi ý
        defaults = {
            "Hữu Nghị": [3000, 730, 815, 72],
            "Lào Cai": [1800, 300, 1084, 96],
            "Móng Cái": [4000, 300, 182, 60],
            "Tân Thanh": [1500, 600, 150, 48]
        }
        
        inputs = {}
        for i, gate in enumerate(gates):
            cols = st.columns(4)
            cols[0].write(f"**{gate}**")
            xnk = cols[1].number_input(f"XNK_{gate}", value=defaults[gate][0], label_visibility="collapsed")
            xe = cols[2].number_input(f"Xe_{gate}", value=defaults[gate][1], label_visibility="collapsed")
            kcn = cols[3].number_input(f"KCN_{gate}", value=defaults[gate][2], label_visibility="collapsed")
            tq = cols[3].number_input(f"TQ_{gate}", value=defaults[gate][3], label_visibility="collapsed")
            
            inputs[gate] = {"Gate": gate, "XNK": xnk, "Xe": xe, "KCN": kcn, "ThongQuan": tq}
            
        submitted = st.form_submit_button("Gửi Đánh Giá")
        
        if submitted:
            current_data = load_data()
            for gate in gates:
                current_data.append(inputs[gate])
            save_data(current_data)
            st.success("✅ Ghi nhận thành công! Dữ liệu của bạn đã được đưa vào hệ thống tính toán tổng.")

# --- TAB 2: QUẢN TRỊ VIÊN ---
elif menu == "Quản Trị Viên (Admin)":
    password = st.sidebar.text_input("Nhập mật khẩu Admin:", type="password")
    
    # MẬT KHẨU ADMIN CỦA BẠN LÀ: admin123
    if password == "admin123":
        st.header("Bảng Điều Khiển Chiến Lược (Dành cho Admin)")
        
        st.subheader("1. Cài đặt Trọng số (Tổng = 100%)")
        col1, col2, col3, col4 = st.columns(4)
        w_xnk = col1.slider("Kim ngạch XNK (%)", 0, 100, 40)
        w_xe = col2.slider("Số xe/ngày (%)", 0, 100, 20)
        w_kcn = col3.slider("Diện tích KCN (%)", 0, 100, 20)
        w_tq = col4.slider("Thời gian Thông quan (%)", 0, 100, 20)
        
        total_weight = w_xnk + w_xe + w_kcn + w_tq
        if total_weight != 100:
            st.error(f"⚠️ Cảnh báo: Tổng trọng số hiện tại là {total_weight}%. Vui lòng điều chỉnh lại cho đúng 100%.")
        else:
            st.success("Trọng số hợp lệ. Hệ thống đang tính toán theo thời gian thực...")
            weights = {"XNK": w_xnk, "Xe": w_xe, "KCN": w_kcn, "ThongQuan": w_tq}
            
            data = load_data()
            if not data:
                st.info("Chưa có ai gửi lượt đánh giá nào. Hãy sang Tab 'Người Đánh Giá' để nhập thử.")
            else:
                total_submissions = int(len(data)/4)
                st.metric("Tổng số lượt đánh giá đã nhận", total_submissions)
                
                # Gọi hàm tính toán
                results_df = calculate_scores(data, weights)
                
                st.subheader("2. Xếp hạng & Kết quả Trung bình")
                
                # Hiển thị Biểu đồ
                st.bar_chart(results_df["DiemTong"])
                
                # Hiển thị Bảng số liệu chi tiết
                st.write("Bảng điểm tổng hợp (0-100):")
                st.dataframe(results_df["DiemTong"].sort_values(ascending=False))
                
                # Nút Reset dữ liệu
                if st.button("Xóa toàn bộ dữ liệu đánh giá"):
                    save_data([])
                    st.rerun()

    elif password != "":
        st.error("Sai mật khẩu!")
