import streamlit as st

st.set_page_config(page_title="Matbaam - Ambalaj ve Matbaa Maliyet Hesaplama", layout="wide")

# CSS Stilleri (Üçlü tırnak ile Python sözdizimi hatası önlenmiştir)
st.markdown("""
    <style>
        .main { background-color: #1a1f2c; }
        .stApp { background-color: #1a1f2c; color: #e2e8f0; }
        .card-box { background-color: #242b3b; border: 1px solid #2d3748; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
        .step-title { color: #f59e0b; font-weight: bold; font-size: 15px; display: flex; align-items: center; gap: 8px; margin-bottom: 15px; border-bottom: 1px solid #2d3748; padding-bottom: 8px; }
        .step-number { background-color: #f59e0b; color: #1a1f2c; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: bold; }
        .summary-card { background-color: #242b3b; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; }
    </style>
""", unsafe_allow_html=True)

# Üst Başlık
st.markdown("<h1 style='color: #f59e0b;'>MATBAAM - Ambalaj & Matbaa Maliyet Sistemi</h1>", unsafe_allow_html=True)
st.markdown("Parametrik Maliyet Analizi ve Teklif Hesaplama Platformu")
st.markdown("---")

# Modül Seçimi (Parametreler veya Fiyat Çıkart)
menu = st.radio("İşlem Modülü Seçiniz", ["1. Parametreler (Fiyat Listesi)", "2. Fiyat Çıkart (Hesaplama)"], horizontal=True)

if menu == "1. Parametreler (Fiyat Listesi)":
    st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi")
    
    col_kur1, col_kur2 = st.columns(2)
    with col_kur1:
        cur_usd = st.number_input("Dolar Kuru (TL)", value=49.97, step=0.01)
    with col_kur2:
        cur_eur = st.number_input("Euro Kuru (TL)", value=56.00, step=0.01)

    st.markdown("### 1. Kağıt ve Karton Grubu (Ton Maliyetleri)")
    p_bristol = st.number_input("Amerikan Bristol Ton ($ USD)", value=825.0)
    p_krome = st.number_input("Krome Karton Ton (TRY TL)", value=40000.0)
    p_kuse = st.number_input("Kuşe Ton (€ EUR)", value=850.0)
    p_hamur = st.number_input("1. Hamur Ton ($ USD)", value=1200.0)

    st.markdown("### 2. Baskı Grubu")
    p_5070_cmyk = st.number_input("50x70 Cmyk Proses Fiyat (TL)", value=3500.0)
    p_5070_tiraj = st.number_input("50x70 Tiraj Fiyatı (TL)", value=800.0)
    p_70100_cmyk = st.number_input("70x100 Cmyk Proses Fiyat (TL)", value=5000.0)
    p_70100_tiraj = st.number_input("70x100 Tiraj Fiyatı (TL)", value=1400.0)

    st.markdown("### 3. Yüzey İşlemleri")
    p_mat_sel = st.number_input("Mat Selofan M2 (TL)", value=4.70)
    p_par_sel = st.number_input("Parlak Selofan M2 (TL)", value=4.50)

    st.markdown("### 4. Kesim ve Mücellit")
    p_bobst = st.number_input("Bobts Kesim Çember (TL)", value=3000.0)
    p_bobst_tiraj = st.number_input("Bobts Kesim Tiraj (TL)", value=1.50)
    p_yap_tiraj = st.number_input("Omega Yapıştırma Tiraj (TL)", value=0.25)

else:
    st.subheader("Ürün Tanımlama ve Fiyat Çıkart")
    
    col1, col2 = st.columns(2)
    with col1:
        firma = st.text_input("Firma Adı", "Erhan Ticaret")
        urun_adi = st.text_input("Ürün Adı / Modeli", "Lüks Kutu Ambalaj")
        adet = st.number_input("Adet (Tiraj)", value=5000, step=500, min_value=1)
        kagit_cinsi = st.selectbox("Kağıt Cinsi", ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur"])
        kagit_gramaj = st.selectbox("Kağıt Gramajı (gr/m²)", [200, 250, 300, 350, 400], index=2)
    
    with col2:
        baski_turu = st.selectbox("Baskı Ebadı ve Türü", ["50x70 CMYK", "70x100 CMYK", "35x50 CMYK"])
        st.markdown("**Ebat (mm x mm x mm)**")
        col_x, col_y, col_z = st.columns(3)
        with col_x: ebat_x = st.number_input("X", value=200)
        with col_y: ebat_y = st.number_input("Y", value=150)
        with col_z: ebat_z = st.number_input("Z", value=50)
        
        laminasyon = st.selectbox("Laminasyon", ["Mat Selofan", "Parlak Selofan", "Yok"])
        kesim_turu = st.selectbox("Kesim Türü", ["Bobst Kesim", "Kazanlı / Pedal Kesim", "Yok"])
        
    yapistirma_var = st.checkbox("Omega Yapıştırma Dahil", value=True)
    nakliye_var = st.checkbox("Nakliye Dahil", value=True)
    kar_orani = st.slider("Hedef Kar Marjı (%)", min_value=10, max_value=100, value=30)

    # --- HESAPLAMA MOTORU ---
    cur_usd = 49.97
    cur_eur = 56.00

    ton_fiyat = 825.0
    para_birim = 'USD'
    if kagit_cinsi == "Amerikan Bristol": ton_fiyat, para_birim = 825.0, 'USD'
    elif kagit_cinsi == "Krome Karton": ton_fiyat, para_birim = 40000.0, 'TL'
    elif kagit_cinsi == "Kuşe Kağıt": ton_fiyat, para_birim = 850.0, 'EUR'
    elif kagit_cinsi == "1. Hamur": ton_fiyat, para_birim = 1200.0, 'USD'

    ton_fiyat_tl = ton_fiyat
    if para_birim == 'USD': ton_fiyat_tl = ton_fiyat * cur_usd
    elif para_birim == 'EUR': ton_fiyat_tl = ton_fiyat * cur_eur

    tabaka_adeti = max(1, adet // 2)
    kg_kagit = round((tabaka_adeti * 0.5 * 0.7 * kagit_gramaj) / 1000)
    kagit_maliyeti = (kg_kagit / 1000) * ton_fiyat_tl

    baski_maliyeti = 3500.0 + (adet * 800.0 / 1000)
    if "70x100" in baski_turu:
        baski_maliyeti = 5000.0 + (adet * 1400.0 / 1000)

    selofan_m2 = tabaka_adeti * 0.35
    selofan_birim = 4.70 if laminasyon == "Mat Selofan" else 4.50
    selofan_maliyeti = selofan_m2 * selofan_birim if laminasyon != "Yok" else 0

    kesim_maliyeti = 3000.0 + (adet * 1.50) if kesim_turu == "Bobst Kesim" else (1800.0 + (adet * 0.75) if kesim_turu == "Kazanlı / Pedal Kesim" else 0)
    yapistirma_maliyeti = 2500.0 + (adet * 0.25) if yapistirma_var else 0
    nakliye_maliyeti = 4000.0 if nakliye_var else 0
    ek_maliyet = yapistirma_maliyeti + nakliye_maliyeti

    toplam_maliyet = kagit_maliyeti + baski_maliyeti + selofan_maliyeti + kesim_maliyeti + ek_maliyet
    net_kar = toplam_maliyet * (kar_orani / 100)
    toplam_karli_fiyat = toplam_maliyet + net_kar
    birim_maliyet = toplam_maliyet / adet if adet > 0 else 0
    karli_birim_fiyat = toplam_karli_fiyat / adet if adet > 0 else 0

    st.markdown("---")
    st.subheader("Planlama ve Proses Sonuçları")
    c1, c2, c3 = st.columns(3)
    c1.metric("Kağıt Miktarı", f"{kg_kagit} kg")
    c2.metric("Tabaka Adedi", f"{tabaka_adeti:,} tabaka")
    c3.metric("Baskı Maliyeti", f"₺{baski_maliyeti:,.2f}")

    st.markdown("---")
    st.subheader("Maliyet ve Fiyatlandırma Özeti")
    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Maliyet", f"₺{toplam_maliyet:,.2f}")
    m2.metric("Net Kar Toplamı", f"₺{net_kar:,.2f}")
    m3.metric("Toplam Karlı Fiyat", f"₺{toplam_karli_fiyat:,.2f}")

    b1, b2 = st.columns(2)
    b1.metric("Birim Maliyet (Adet)", f"₺{birim_maliyet:,.4f}")
    b2.metric("Karlı Birim Fiyat (Satış)", f"₺{karli_birim_fiyat:,.4f}")
