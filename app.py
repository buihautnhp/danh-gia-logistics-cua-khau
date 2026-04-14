import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Đánh giá Logistics", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)
gates = ["Hữu Nghị", "Lào Cai", "Móng Cái", "Tân Thanh"]

# 15 Chỉ số định lượng
COLUMNS = [
    "Gate", "XNK", "KhoiLuong", "Xe", "MuaVu", "KCN", "DanSo", "NongNghiep", 
    "CaoToc", "DuongSat", "DaPhuongThuc", "ThongQuan", "PhoiHop", "DN_Log", "KhoLanh", "HaTangHoTro", 
    "Diem_Danh_Gia", "Timestamp"
]

def get_all_data():
    try:
        return conn.read(worksheet="Sheet1", ttl=0)
    except:
        return pd.DataFrame(columns=COLUMNS)

# --- CƠ SỞ DỮ LIỆU ẢNH ---
gate_info = {
    "Hữu Nghị": {"mieu_ta": "Cửa khẩu Quốc tế Hữu Nghị (Lạng Sơn)...", "anh_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80"},
    "Lào Cai": {"mieu_ta": "Cửa khẩu Quốc tế Kim Thành (Lào Cai)...", "anh_url": "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?auto=format&fit=crop&w=800&q=80"},
    "Móng Cái": {"mieu_ta": "Cửa khẩu Quốc tế Móng Cái (Quảng Ninh)...", "anh_url": "https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80"},
    "Tân Thanh": {"mieu_ta": "Cửa khẩu phụ Tân Thanh (Lạng Sơn)...", "anh_url": "https://images.unsplash.com/photo-1605810230434-7631ac76ec81?auto=format&fit=crop&w=800&q=80"}
}

st.title("Hệ thống Đánh giá 15 Chỉ số Logistics Cửa khẩu")
menu = st.sidebar.radio("Vai trò:", ["Người Đánh Giá", "Quản Trị Viên (Admin)"])

# ==========================================
# TAB 1: NGƯỜI ĐÁNH GIÁ (EVALUATOR)
# ==========================================
if menu == "Người Đánh Giá":
    st.header("Thu thập Dữ liệu & Đánh giá Tức thì")
    
    selected_gate = st.selectbox("📌 Chọn cửa khẩu đánh giá:", gates)
    
    # 1. PHẦN GIỚI THIỆU CỬA KHẨU & ẢNH
    col_img, col_text = st.columns([1, 2])
    with col_img: st.image(gate_info[selected_gate]["anh_url"], use_container_width=True)
    with col_text:
        st.subheader(f"Cửa khẩu {selected_gate}")
        st.write(gate_info[selected_gate]["mieu_ta"])
    
    # 2. PHẦN GIỚI THIỆU ĐỊNH NGHĨA 15 CHỈ SỐ (Dành cho Evaluator đọc)
    with st.expander("📖 XEM HƯỚNG DẪN & ĐỊNH NGHĨA 15 CHỈ SỐ (Click để mở rộng)"):
        st.markdown("""
        **I. Dòng hàng (Trade Flow)**
        - **Kim ngạch XNK (USD):** Tổng xuất + nhập. 
        - **Khối lượng (Tấn):** Tổng tấn hàng qua cửa khẩu.
        - **Số xe/ngày:** Lưu lượng xe chở hàng trung bình.
        - **Độ mùa vụ (0-1):** 1 = Ổn định quanh năm; 0 = Tập trung cao điểm.
        
        **II. Hậu phương kinh tế (Hinterland)**
        - **Diện tích KCN (ha):** Tổng diện tích KCN chính vùng ảnh hưởng.
        - **Dân số (Triệu người):** Dân số bán kính 100-150km.
        - **Nông nghiệp (Điểm):** Quy mô hàng nông sản vùng lân cận.
        
        **III. Kết nối hạ tầng (Connectivity)**
        - **Đường cao tốc/QL (km):** Chiều dài đường đến vùng kinh tế.
        - **Đường sắt (km):** Đường sắt nối trực tiếp.
        - **Đa phương thức (0-1):** Có ICD, cảng biển hỗ trợ (1=Có, 0=Không).
        
        **IV. Thể chế & Quản lý (Institutional)**
        - **Thời gian thông quan (giờ):** Càng nhỏ càng tốt.
        - **Cơ chế phối hợp (0-1):** Một cửa, kiểm dịch chung (1=Có, 0=Không).
        
        **V. Hệ sinh thái (Ecosystem)**
        - **Số DN Logistics:** Số DN dịch vụ trên địa bàn.
        - **Kho lạnh (Tấn):** Tổng công suất kho lạnh.
        - **Hạ tầng hỗ trợ (0-1):** Bãi trung chuyển, kho ngoại quan (1=Có, 0=Không).
        """)

    # 3. FORM NHẬP LIỆU & TÍNH ĐIỂM TỪNG LƯỢT
    with st.form("form_15_criteria", clear_on_submit=True):
        st.write("### Nhập liệu các chỉ số định lượng")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**1. Dòng hàng**")
            xnk = st.number_input("Kim ngạch XNK (Tr.USD)", value=1000.0)
            kl = st.number_input("Khối lượng (Nghìn tấn)", value=500.0)
            xe = st.number_input("Số xe/ngày", value=300)
            muavu = st.slider("Độ mùa vụ (0-1)", 0.0, 1.0, 0.8)
            st.markdown("**4. Thể chế**")
            tq = st.number_input("TG Thông quan (Giờ)", value=48.0)
            phoihop = st.selectbox("Cơ chế một cửa (1=Có, 0=Không)", [1, 0])
        with c2:
            st.markdown("**2. Hậu phương**")
            kcn = st.number_input("Diện tích KCN (ha)", value=200.0)
            danso = st.number_input("Dân số (Triệu người)", value=2.0)
            nongnghiep = st.number_input("SL Nông nghiệp (Điểm)", value=50.0)
            st.markdown("**5. Hệ sinh thái**")
            dnlog = st.number_input("Số DN Logistics", value=20)
            kholanh = st.number_input("CS Kho lạnh (Tấn)", value=1000.0)
            hatang = st.selectbox("Hạ tầng ICD (1=Có, 0=Không)", [1, 0])
        with c3:
            st.markdown("**3. Kết nối hạ tầng**")
            caotoc = st.number_input("Cao tốc/QL (km)", value=150.0)
            duongsat = st.number_input("Đường sắt (km)", value=0.0)
            daphuongthuc = st.selectbox("Đa Phương Thức (1=Có, 0=Không)", [1, 0])
            
        submit = st.form_submit_button("Gửi đánh giá & Tính điểm")
        
        if submit:
            st.cache_data.clear() 
            df_old = get_all_data()
            
            new_record = {
                "Gate": selected_gate, "XNK": xnk, "KhoiLuong": kl, "Xe": xe, "MuaVu": muavu,
                "KCN": kcn, "DanSo": danso, "NongNghiep": nongnghiep, 
                "CaoToc": caotoc, "DuongSat": duongsat, "DaPhuongThuc": daphuongthuc,
                "ThongQuan": tq, "PhoiHop": phoihop, "DN_Log": dnlog, "KhoLanh": kholanh, "HaTangHoTro": hatang
            }
            
            df_temp = pd.concat([df_old, pd.DataFrame([new_record])], ignore_index=True)
            for col in COLUMNS[1:16]: df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce').fillna(0)
            
            # Hàm chuẩn hóa
            def norm(col, val, inv=False):
                c_min, c_max = df_temp[col].min(), df_temp[col].max()
                if c_max == c_min: return 1.0
                return (c_max - val)/(c_max - c_min) if inv else (val - c_min)/(c_max - c_min)

            # Trọng số mặc định của Admin (Dùng để báo điểm tức thì cho Evaluator)
            W_BASE = {"XNK":0.12, "KhoiLuong":0.08, "Xe":0.10, "MuaVu":0.05, "KCN":0.10, "DanSo":0.05, "NongNghiep":0.05, "CaoToc":0.08, "DuongSat":0.07, "DaPhuongThuc":0.05, "ThongQuan":0.10, "PhoiHop":0.03, "DN_Log":0.07, "KhoLanh":0.05, "HaTangHoTro":0.05}
            
            score = 0
            for key, weight in W_BASE.items():
                is_inverse = True if key == "ThongQuan" else False
                score += norm(key, new_record[key], is_inverse) * weight
            
            final_score = round(score * 100, 1)
            new_record["Diem_Danh_Gia"] = final_score
            new_record["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            updated_df = pd.concat([df_old, pd.DataFrame([new_record])], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.balloons()
            st.success(f"🎉 Xuất sắc! Điểm của {selected_gate} ở lượt đánh giá này là: {final_score}/100 điểm")

# ==========================================
# TAB 2: QUẢN TRỊ VIÊN (ADMIN) 
# ==========================================
elif menu == "Quản Trị Viên (Admin)":
    pwd = st.sidebar.text_input("Mật khẩu:", type="password")
    if pwd == "admin123":
        st.header("Báo cáo Trung bình & Mô phỏng")
        df = get_all_data()
        
        if not df.empty and "Diem_Danh_Gia" in df.columns:
            # 1. TÍNH ĐIỂM TRUNG BÌNH CÁC LƯỢT ĐÁNH GIÁ
            st.subheader("1. Điểm Trung Bình Khách Quan (Thực tế)")
            df['Diem_Danh_Gia'] = pd.to_numeric(df['Diem_Danh_Gia'], errors='coerce')
            avg_scores = df.groupby('Gate')['Diem_Danh_Gia'].mean().round(1).reset_index()
            st.bar_chart(data=avg_scores.set_index('Gate')['Diem_Danh_Gia'])
            
            st.markdown("---")
            
            # 2. MÔ PHỎNG VỚI 15 TRỌNG SỐ
            st.subheader("2. Khung Mô phỏng Chiến lược (Admin)")
            st.write("Kéo thanh trượt để thay đổi trọng số. Hệ thống tự động quy đổi tỷ lệ nếu tổng khác 100%.")
            
            w = {}
            tabs = st.tabs(["Dòng hàng", "Hậu phương", "Kết nối", "Thể chế", "Sinh thái"])
            with tabs[0]:
                w['XNK'] = st.slider("XNK (%)", 0, 50, 12)
                w['KhoiLuong'] = st.slider("Khối lượng (%)", 0, 50, 8)
                w['Xe'] = st.slider("Số xe (%)", 0, 50, 10)
                w['MuaVu'] = st.slider("Mùa vụ (%)", 0, 50, 5)
            with tabs[1]:
                w['KCN'] = st.slider("KCN (%)", 0, 50, 10)
                w['DanSo'] = st.slider("Dân số (%)", 0, 50, 5)
                w['NongNghiep'] = st.slider("Nông nghiệp (%)", 0, 50, 5)
            with tabs[2]:
                w['CaoToc'] = st.slider("Cao tốc (%)", 0, 50, 8)
                w['DuongSat'] = st.slider("Đường sắt (%)", 0, 50, 7)
                w['DaPhuongThuc'] = st.slider("Đa phương thức (%)", 0, 50, 5)
            with tabs[3]:
                w['ThongQuan'] = st.slider("Thông quan (%)", 0, 50, 10)
                w['PhoiHop'] = st.slider("Phối hợp (%)", 0, 50, 3)
            with tabs[4]:
                w['DN_Log'] = st.slider("DN Logistics (%)", 0, 50, 7)
                w['KhoLanh'] = st.slider("Kho lạnh (%)", 0, 50, 5)
                w['HaTangHoTro'] = st.slider("Hạ tầng hỗ trợ (%)", 0, 50, 5)

            # Auto-normalize weights
            total_w = sum(w.values())
            if total_w == 0: total_w = 1 
            
            for col in COLUMNS[1:16]:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df_avg = df.groupby('Gate')[COLUMNS[1:16]].mean().reset_index()
            for gate in gates:
                if gate not in df_avg['Gate'].values:
                    df_avg.loc[len(df_avg)] = [gate] + [0]*15
                    
            df_norm = pd.DataFrame({'Gate': df_avg['Gate']})
            for col in COLUMNS[1:16]:
                min_val, max_val = df_avg[col].min(), df_avg[col].max()
                if max_val == min_val:
                    df_norm[col] = 1.0
                else:
                    df_norm[col] = (max_val - df_avg[col]) / (max_val - min_val) if col == "ThongQuan" else (df_avg[col] - min_val) / (max_val - min_val)
            
            # Tính điểm với trọng số đã quy đổi
            df_norm['Điểm Mô Phỏng'] = 0
            for col in COLUMNS[1:16]:
                df_norm['Điểm Mô Phỏng'] += df_norm[col] * (w[col] / total_w)
            df_norm['Điểm Mô Phỏng'] = (df_norm['Điểm Mô Phỏng'] * 100).round(1)
            
            df_norm = df_norm.set_index('Gate').reindex(gates).reset_index()
            st.bar_chart(data=df_norm.set_index('Gate')['Điểm Mô Phỏng'])
