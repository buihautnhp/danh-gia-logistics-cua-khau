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

# ==========================================
# CẤU HÌNH MIN-MAX LAI (HYBRID BOUNDS)
# ==========================================
BOUNDS_CONFIG = {
    "DanSo": (1.5, 5.0),          
    "HaTangHoTro": (0, 1),        
    "PhoiHop": (0, 1),            
    "DaPhuongThuc": (0, 1),       
    "MuaVu": (0.0, 1.0),          
    "ThongQuan": (4.0, None)     # Min lý tưởng là 4h
}

# TRỌNG SỐ MẶC ĐỊNH CHUNG
W_BASE = {"XNK":0.12, "KhoiLuong":0.08, "Xe":0.10, "MuaVu":0.05, "KCN":0.10, "DanSo":0.05, "NongNghiep":0.05, "CaoToc":0.08, "DuongSat":0.07, "DaPhuongThuc":0.05, "ThongQuan":0.10, "PhoiHop":0.03, "DN_Log":0.07, "KhoLanh":0.05, "HaTangHoTro":0.05}
total_w_base = sum(W_BASE.values())

# --- CƠ SỞ DỮ LIỆU ẢNH ---
gate_info = {
    "Hữu Nghị": {"mieu_ta": "Cửa khẩu Quốc tế Hữu Nghị (Lạng Sơn)...", "anh_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80"},
    "Lào Cai": {"mieu_ta": "Cửa khẩu Quốc tế Kim Thành (Lào Cai)...", "anh_url": "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?auto=format&fit=crop&w=800&q=80"},
    "Móng Cái": {"mieu_ta": "Cửa khẩu Quốc tế Móng Cái (Quảng Ninh)...", "anh_url": "https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=800&q=80"},
    "Tân Thanh": {"mieu_ta": "Cửa khẩu phụ Tân Thanh (Lạng Sơn)...", "anh_url": "https://images.unsplash.com/photo-1605810230434-7631ac76ec81?auto=format&fit=crop&w=800&q=80"}
}

# ==========================================
# MENU ĐIỀU HƯỚNG
# ==========================================
st.sidebar.title("Hệ thống Mô phỏng")
menu = st.sidebar.radio("Chức năng:", [
    "1. Trang chủ (Giới thiệu)", 
    "2. Đánh giá Cửa khẩu", 
    "3. Xem bảng điểm chi tiết", 
    "4. Quản trị viên (Admin)"
])

# ==========================================
# TRANG 1: TRANG CHỦ (GIỚI THIỆU)
# ==========================================
if menu == "1. Trang chủ (Giới thiệu)":
    st.title("Đánh giá Tiềm năng Phát triển Trung tâm Logistics Cửa khẩu Quốc tế Đường bộ")
    st.image("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1200&q=80", use_container_width=True)
    
    st.header("🎯 Mục tiêu & Nhiệm vụ của Website")
    st.markdown("""
    Hệ thống này được xây dựng như một **Mô hình Hỗ trợ Ra quyết định (DSS)** dựa trên phương pháp Đánh giá Đa tiêu chí (MCDM). 
    *   **Mục tiêu:** Định lượng hóa và xếp hạng tiềm năng phát triển của 4 cụm cửa khẩu trọng điểm phía Bắc (Hữu Nghị, Lào Cai, Móng Cái, Tân Thanh) thành các trung tâm logistics mang tầm quốc tế.
    *   **Chức năng:** Cho phép các chuyên gia, nhà quản lý nhập liệu đánh giá thực tế. Hệ thống sẽ tự động chuẩn hóa dữ liệu (Min-Max) và tổng hợp kết quả theo thời gian thực dựa trên bộ 15 tiêu chí cốt lõi.
    """)
    
    st.header("📖 Giải thích thuật ngữ chuyên môn")
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **1. Dòng hàng (Trade Flow) là gì?**
        Là nhóm chỉ số phản ánh quy mô, sức mạnh và sự ổn định của lượng hàng hóa giao thương đi qua cửa khẩu. 
        Một trung tâm logistics không thể phát triển nếu không có dòng hàng đủ lớn để nuôi dưỡng các dịch vụ lưu kho, bốc xếp, và vận tải. Nhóm này bao gồm: Kim ngạch XNK, Khối lượng hàng, và Số lượng phương tiện.
        """)
    with col2:
        st.success("""
        **2. Độ mùa vụ (Seasonality) là gì?**
        Là hệ số (từ 0 đến 1) đánh giá tính ổn định của dòng hàng trong năm. 
        *   Gần **1.0**: Hàng hóa lưu thông đều đặn quanh năm (Ví dụ: linh kiện điện tử, máy móc). Tốt cho đầu tư logistics lâu dài.
        *   Gần **0.0**: Hàng hóa ồ ạt đổ về trong một thời gian cực ngắn (Ví dụ: Vụ thu hoạch vải thiều, thanh long) gây ùn tắc, sau đó lại vắng vẻ. Gây rủi ro cho nhà đầu tư kho bãi.
        """)

# ==========================================
# TRANG 2: ĐÁNH GIÁ CỬA KHẨU (EVALUATOR)
# ==========================================
elif menu == "2. Đánh giá Cửa khẩu":
    st.header("Thu thập Dữ liệu & Đánh giá Tức thì")
    
    selected_gate = st.selectbox("📌 Chọn cửa khẩu đánh giá:", gates)
    
    col_img, col_text = st.columns([1, 2])
    with col_img: st.image(gate_info[selected_gate]["anh_url"], use_container_width=True)
    with col_text:
        st.subheader(f"Cửa khẩu {selected_gate}")
        st.write(gate_info[selected_gate]["mieu_ta"])

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
            tq = st.number_input("TG Thông quan (Giờ)", value=24.0)
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
            
            def norm(col, val, inv=False):
                c_min, c_max = df_temp[col].min(), df_temp[col].max()
                if col in BOUNDS_CONFIG:
                    conf_min, conf_max = BOUNDS_CONFIG[col]
                    if conf_min is not None: c_min = conf_min
                    if conf_max is not None: c_max = conf_max
                if c_min > c_max: c_max = c_min
                val_clamped = max(c_min, min(val, c_max))
                
                if c_max == c_min: return 1.0
                if inv: 
                    return (c_max - val_clamped) / (c_max - c_min)
                else:
                    return (val_clamped - c_min) / (c_max - c_min)

            score = 0
            for key, weight in W_BASE.items():
                is_inverse = True if key == "ThongQuan" else False
                score += norm(key, new_record[key], is_inverse) * (weight / total_w_base)
            
            final_score = round(score * 100, 1)
            new_record["Diem_Danh_Gia"] = final_score
            new_record["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            updated_df = pd.concat([df_old, pd.DataFrame([new_record])], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.balloons()
            st.success(f"🎉 Xuất sắc! Điểm của {selected_gate} ở lượt đánh giá này là: {final_score}/100 điểm")

# ==========================================
# TRANG 3: XEM BẢNG ĐIỂM CHI TIẾT (NGƯỜI DÙNG)
# ==========================================
elif menu == "3. Xem bảng điểm chi tiết":
    st.header("Bảng Phân Tích Điểm Số Chi Tiết")
    st.write("Trang này hiển thị điểm chi tiết của từng tiêu chí (dựa trên mức trọng số mặc định của hệ thống). Kết quả này được tổng hợp và lấy trung bình từ tất cả các lượt đánh giá.")
    
    df = get_all_data()
    
    if df.empty or "Diem_Danh_Gia" not in df.columns:
        st.info("Hệ thống chưa có dữ liệu đánh giá nào.")
    else:
        for col in COLUMNS[1:16]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        df_avg = df.groupby('Gate')[COLUMNS[1:16]].mean().reset_index()
        for gate in gates:
            if gate not in df_avg['Gate'].values:
                df_avg.loc[len(df_avg)] = [gate] + [0]*15
                
        df_detailed_scores = pd.DataFrame({'Cửa khẩu': df_avg['Gate']})
        
        # Tính điểm chi tiết từng cấu phần (Điểm = Giá trị chuẩn hóa * Trọng số * 100)
        for col in COLUMNS[1:16]:
            c_min, c_max = df_avg[col].min(), df_avg[col].max()
            if col in BOUNDS_CONFIG:
                conf_min, conf_max = BOUNDS_CONFIG[col]
                if conf_min is not None: c_min = conf_min
                if conf_max is not None: c_max = conf_max
            if c_min > c_max: c_max = c_min
            
            clamped_series = df_avg[col].clip(lower=c_min, upper=c_max)
            
            norm_series = pd.Series(1.0, index=df_avg.index)
            if c_max > c_min:
                if col == "ThongQuan":
                    norm_series = (c_max - clamped_series) / (c_max - c_min)
                else:
                    norm_series = (clamped_series - c_min) / (c_max - c_min)
            
            # Tính điểm đóng góp của riêng tiêu chí này vào tổng 100 điểm
            df_detailed_scores[col] = (norm_series * (W_BASE[col] / total_w_base) * 100).round(2)
        
        # Thêm cột Tổng điểm
        df_detailed_scores['TỔNG ĐIỂM'] = df_detailed_scores[COLUMNS[1:16]].sum(axis=1).round(1)
        
        st.markdown("### Bảng phân rã điểm số theo 15 tiêu chí (Thang điểm 100)")
        st.dataframe(df_detailed_scores.set_index('Cửa khẩu'), use_container_width=True)
        
        st.markdown("### Biểu đồ Xếp hạng Tổng điểm (Trọng số cố định)")
        st.bar_chart(data=df_detailed_scores.set_index('Cửa khẩu')['TỔNG ĐIỂM'])

# ==========================================
# TRANG 4: QUẢN TRỊ VIÊN (ADMIN) 
# ==========================================
elif menu == "4. Quản trị viên (Admin)":
    pwd = st.sidebar.text_input("Mật khẩu:", type="password")
    if pwd == "admin123":
        st.header("Khung Mô phỏng Chiến lược (Admin)")
        df = get_all_data()
        
        if not df.empty and "Diem_Danh_Gia" in df.columns:
            st.write("Tại đây, quyền quản trị viên cho phép bạn thay đổi trọng số để quan sát sự biến động của bảng xếp hạng.")
            
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
                c_min, c_max = df_avg[col].min(), df_avg[col].max()
                if col in BOUNDS_CONFIG:
                    conf_min, conf_max = BOUNDS_CONFIG[col]
                    if conf_min is not None: c_min = conf_min
                    if conf_max is not None: c_max = conf_max
                if c_min > c_max: c_max = c_min
                
                clamped_series = df_avg[col].clip(lower=c_min, upper=c_max)
                
                if c_max == c_min:
                    df_norm[col] = 1.0
                else:
                    if col == "ThongQuan":
                        df_norm[col] = (c_max - clamped_series) / (c_max - c_min)
                    else:
                        df_norm[col] = (clamped_series - c_min) / (c_max - c_min)
            
            df_norm['Điểm Mô Phỏng'] = 0
            for col in COLUMNS[1:16]:
                df_norm['Điểm Mô Phỏng'] += df_norm[col] * (w[col] / total_w)
            df_norm['Điểm Mô Phỏng'] = (df_norm['Điểm Mô Phỏng'] * 100).round(1)
            
            df_norm = df_norm.set_index('Gate').reindex(gates).reset_index()
            st.bar_chart(data=df_norm.set_index('Gate')['Điểm Mô Phỏng'])
            
            st.markdown("### Dữ liệu thô trên Hệ thống")
            st.dataframe(df)
