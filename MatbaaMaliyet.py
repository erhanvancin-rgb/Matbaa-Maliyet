import streamlit as st

st.set_page_config(page_title="Matbaa ve Ambalaj Maliyet Sistemi", layout="wide")

# Oturum Durumu (Modül Yönetimi)
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_home():
    st.session_state.page = 'home'

def go_params():
    st.session_state.page = 'params'

def go_calc():
    st.session_state.page = 'calc'

# Üst Başlık & Bilgi Çubuğu
st.markdown("### 🖨️ MATBAAM PRO - Ambalaj & Matbaa Maliyet Sistemi")
st.info("Güncel Kur: USD: ₺49.97 | EUR: ₺56.00 (Tarih: 28.01.2026)")
st.markdown("---")

# 1. ANA SAYFA (Yalnızca 2 Buton)
if st.session_state.page == 'home':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>Yönetim & Hesaplama Modülü</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Lütfen işlem yapmak istediğiniz modülü seçiniz.</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("1. Parametreler (Fiyat Listesi)", use_container_width=True):
            go_params()
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("2. Fiyat Çıkart (Maliyet Hesaplama Formu)", use_container_width=True):
            go_calc()
            st.rerun()

# 2. PARAMETRELER SAYFASI
elif st.session_state.page == 'params':
    if st.button("⬅️ Ana Menüye Dön"):
        go_home()
        st.rerun()
        
    st.subheader("Parametre Fiyat Listesi Yönetimi")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 1. Kağıt ve Karton Grubu (Ton)")
        p_bristol = st.number_input("Amerikan Bristol Ton ($ USD)", value=825.0)
        p_krome = st.number_input("Krome Karton Ton (TRY TL)", value=40000.0)
        p_kuse = st.number_input("Kuşe Ton (€ EUR)", value=850.0)
        p_hamur = st.number_input("1. Hamur Ton ($ USD)", value=1200.0)
    with col2:
        st.markdown("#### 2. Baskı Grubu")
        p_5070_cmyk = st.number_input("50x70 Cmyk Proses (TL)", value=3500.0)
        p_5070_tiraj = st.number_input("50x70 Tiraj Fiyatı (TL)", value=800.0)
        p_70100_cmyk = st.number_input("70x100 Cmyk Proses (TL)", value=5000.0)
        p_70100_tiraj = st.number_input("70x100 Tiraj Fiyatı (TL)", value=1400.0)

# 3. FİYAT ÇIKART (HESAPLAMA) SAYFASI
elif st.session_state.page == 'calc':
    if st.button("⬅️ Ana Menüye Dön"):
        go_home()
        st.rerun()
        
    st.subheader("Maliyet Hesaplama Formu")
    
    c1, c2 = st.columns(2)
    with c1:
        firma = st.text_input("Firma Adı", "Erhan Ticaret")
        urun_adi = st.text_input("Ürün Adı / Modeli", "Lüks Parfüm Kutusu")
        adet = st.number_input("Ürün Adedi (Tiraj)", value=5000, step=500, min_value=1)
        kagit_cinsi = st.selectbox("Kağıt Cinsi", ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur"])
        gramaj = st.selectbox("Kağıt Gramajı (gr/m²)", [200, 250, 300, 350, 400], index=2)
    with c2:
        baski_turu = st.selectbox("Baskı Türü", ["50x70 CMYK", "70x100 CMYK", "35x50 CMYK"])
        
        st.markdown("**Ebat (mm x mm x mm)**")
        ex, ey, ez = st.columns(3)
        with ex: x_val = st.number_input("X", value=200)
        with ey: y_val = st.number_input("Y", value=150)
        with ez: z_val = st.number_input("Z", value=50)
        
        laminasyon = st.selectbox("Yüzey Laminasyonu", ["Mat Selofan", "Parlak Selofan", "Yok"])
        kesim = st.selectbox("Kesim Türü", ["Bobst Kesim", "Kazanlı / Pedal Kesim", "Yok"])

    yapistirma = st.checkbox("Omega Yapıştırma Dahil", value=True)
    nakliye = st.checkbox("Nakliye Dahil", value=True)
    kar_orani = st.slider("Hedef Kar Marjı (%)", 0, 100, 30)

    # Hesaplama Motoru
    usd_kur = 49.97
    eur_kur = 56.00
    
    ton_fiyat = 825.0
     birim_tip = 'USD'
    if kagit_cinsi == "Amerikan Bristol": ton_fiyat, birim_tip = 825.0, 'USD'
    elif kagit_cinsi == "Krome Karton": ton_fiyat, birim_tip = 40000.0, 'TL'
    elif kagit_cinsi == "Kuşe Kağıt": ton_fiyat, birim_tip = 850.0, 'EUR'
    elif kagit_cinsi == "1. Hamur": ton_fiyat, birim_tip = 1200.0, 'USD'

    ton_fiyat_tl = ton_fiyat
    if birim_tip == 'USD': ton_fiyat_tl = ton_fiyat * usd_kur
    elif birim_tip == 'EUR': ton_fiyat_tl = ton_fiyat * eur_kur

    tabaka_adeti = max(1, adet // 2)
    kg_kagit = round((tabaka_adeti * (x_val/1000) * (y_val/1000) * gramaj) / 2)
    kagit_maliyeti = (kg_kagit / 1000) * ton_fiyat_tl

    baski_maliyeti = 3500.0 + (adet * 800.0 / 1000)
    if "70x100" in baski_turu:
        baski_maliyeti = 5000.0 + (adet * 1400.0 / 1000)

    selofan_m2 = tabaka_adeti * 0.35
    selofan_maliyeti = selofan_m2 * 4.70 if laminasyon != "Yok" else 0

    kesim_maliyeti = (3000.0 + (adet * 1.50)) if kesim == "Bobst Kesim" else (1800.0 + (adet * 0.75) if kesim == "Kazanlı / Pedal Kesim" else 0)
    yapistirma_maliyeti = (2500.0 + (adet * 0.25)) if yapistirma else 0
    nakliye_maliyeti = 4000.0 if nakliye else 0
    toplam_ek = yapistirma_maliyeti + nakliye_maliyeti

    toplam_maliyet = kagit_maliyeti + baski_maliyeti + selofan_maliyeti + kesim_maliyeti + toplam_ek
    net_kar = toplam_maliyet * (kar_orani / 100)
    toplam_karli_fiyat = toplam_maliyet + net_kar
    birim_maliyet = toplam_maliyet / adet if adet > 0 else 0
    karli_birim_fiyat = toplam_karli_fiyat / adet if adet > 0 else 0

    st.markdown("---")
    st.subheader("📊 Maliyet ve Teklif Özeti")
    
    r1, r2, r3 = st.columns(3)
    r1.metric("Kağıt Miktarı", f"{kg_kagit} kg")
    r2.metric("Tabaka Adedi", f"{tabaka_adeti:,} tabaka")
    r3.metric("Baskı Maliyeti", f"₺{baski_maliyeti:,.2f}")

    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Maliyet", f"₺{toplam_maliyet:,.2f}")
    m2.metric("Net Kar", f"₺{net_kar:,.2f}")
    m3.metric("Karlı Satış Fiyatı", f"₺{toplam_karli_fiyat:,.2f}")

    b1, b2 = st.columns(2)
    b1.metric("Birim Maliyet", f"₺{birim_maliyet:,.4f}")
    b2.metric("Karlı Birim Satış Fiyatı", f"₺{karli_birim_fiyat:,.4f}")
