import streamlit as st

st.set_page_config(page_title="Matbaa Ambalaj Maliyet Analizi", layout="wide")

# CSS Stilleri
st.markdown("""
    <style>
        .table-header { background-color: #f59e0b; color: #fff; font-weight: bold; padding: 8px; border-radius: 4px; }
        .stTextInput input, .stSelectbox select { border: 1px solid #d1d5db; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

st.title("Matbaa Ambalaj Maliyet & Fiyatlandırma Sistemi")
st.markdown("Parametrik Matbaa Maliyet Analizi ve Teklif Formu (Tarih: 28.01.2026)")

col1, col2 = st.columns([5, 7])

with col1:
    st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi")
    
    st.markdown("##### 1. Kağıt ve Karton Grubu")
    p_bristol = st.number_input("Amerikan Bristol Ton ($/€)", value=1200.0)
    p_krome = st.number_input("Krome Karton Ton ($/€)", value=1100.0)
    p_kuse = st.number_input("Kuşe Ton ($/€)", value=1050.0)
    p_hamur = st.number_input("1. Hamur Ton ($/€)", value=1150.0)

    st.markdown("##### 2. Baskı Grubu")
    baski_5070_cmyk = st.number_input("50x70 Cmyk Proses Fiyat (TL)", value=2500.0)
    baski_5070_tiraj = st.number_input("50x70 Tiraj Fiyatı (TL)", value=1.50)
    baski_70100_cmyk = st.number_input("70x100 Cmyk Proses Fiyat (TL)", value=3500.0)
    baski_70100_tiraj = st.number_input("70x100 Tiraj Fiyatı (TL)", value=2.00)

    st.markdown("##### 3. Yüzey İşlemleri")
    p_mat_selofan = st.number_input("Mat Selofan M2 (TL)", value=4.0)
    p_parlak_selofan = st.number_input("Parlak Selofan M2 (TL)", value=3.5)

    st.markdown("##### 4. Kesim ve Mücellit")
    p_bobst = st.number_input("Bobst Kesim Çember (TL)", value=2500.0)
    p_yapistirma_tiraj = st.number_input("Omega Yapıştırma Tiraj (TL)", value=0.50)

with col2:
    st.subheader("Tanımlama Bilgileri ve Hesaplama")
    
    firma = st.text_input("Firma Adı", "Erhan Ticaret")
    urun_adi = st.text_input("Ürün Adı", "Deneme Ambalaj Kutusu")
    adet = st.number_input("Adet (Tiraj)", value=5000, step=100)
    
    kagit_cinsi = st.selectbox("Kağıt Cinsi", ["300 gr Amerikan Bristol", "300 gr Krome Karton", "300 gr Kuşe", "1. Hamur"])
    baski_turu = st.selectbox("Baskı Türü", ["50x70 CMYK", "70x100 CMYK", "35x50 CMYK"])
    
    st.markdown("##### Ebat (mm x mm x mm)")
    col_x, col_y, col_z = st.columns(3)
    with col_x: ebat_x = st.number_input("X", value=200)
    with col_y: ebat_y = st.number_input("Y", value=150)
    with col_z: ebat_z = st.number_input("Z", value=50)

    laminasyon = st.selectbox("Laminasyon", ["Mat Selofan", "Parlak Selofan", "Yok"])
    sivama = st.selectbox("Sıvama / Ondüle", ["Ondüle / Sıvama Var", "Yok"])
    kesim = st.selectbox("Kesim & Bıçak", ["Bobst / Kazanlı Kesim Var", "Yok"])
    
    yapistirma = st.checkbox("Yapıştırma Var", value=True)
    nakliye = st.checkbox("Nakliye Var", value=True)
    kar_orani = st.number_input("Kar Marjı (%)", value=30.0)

    # Hesaplamalar
    ton_fiyat_eur = p_bristol
    if "Krome" in kagit_cinsi: ton_fiyat_eur = p_krome
    elif "Kuşe" in kagit_cinsi: ton_fiyat_eur = p_kuse
    elif "Hamur" in kagit_cinsi: ton_fiyat_eur = p_hamur

    eur_kur = 35.0
    ton_fiyat_tl = ton_fiyat_eur * eur_kur

    tabaka_adeti = max(1, adet // 2)
    kg_kagit = round((tabaka_adeti * 0.3 * 0.5 * 300) / 1000)
    kagit_maliyeti = (kg_kagit / 1000) * ton_fiyat_tl

    baski_maliyeti = baski_5070_cmyk + (adet * baski_5070_tiraj)
    if "70x100" in baski_turu:
        baski_maliyeti = baski_70100_cmyk + (adet * baski_70100_tiraj)

    selofan_m2 = tabaka_adeti * 0.35
    selofan_birim = p_mat_selofan if "Mat" in laminasyon else p_parlak_selofan
    selofan_maliyeti = selofan_m2 * selofan_birim if laminasyon != "Yok" else 0

    sivama_maliyeti = tabaka_adeti * 2.5 if sivama != "Yok" else 0
    kesim_maliyeti = p_bobst + (adet * 0.8) if kesim != "Yok" else 0
    yapistirma_maliyeti = adet * p_yapistirma_tiraj if yapistirma else 0
    nakliye_maliyeti = 4000.0 if nakliye else 0

    toplam_maliyet = kagit_maliyeti + baski_maliyeti + selofan_maliyeti + sivama_maliyeti + kesim_maliyeti + yapistirma_maliyeti + nakliye_maliyeti
    net_kar = toplam_maliyet * (kar_orani / 100)
    toplam_karli_fiyat = toplam_maliyet + net_kar
    birim_maliyet = toplam_maliyet / adet if adet > 0 else 0
    karli_birim_fiyat = toplam_karli_fiyat / adet if adet > 0 else 0

    st.markdown("---")
    st.subheader("Planlama ve Proses Bilgileri")
    st.write(f"- **Kaç kilogram kağıt:** {kg_kagit} kg")
    st.write(f"- **Kaç tabaka baskı:** {tabaka_adeti} adet tabaka")
    st.write(f"- **Baskı Maliyeti:** ₺{baski_maliyeti:,.2f}")
    st.write(f"- **Selofan Maliyeti:** ₺{selofan_maliyeti:,.2f}")
    st.write(f"- **Sıvama Maliyeti:** ₺{sivama_maliyeti:,.2f}")
    st.write(f"- **Kesim Maliyeti:** ₺{kesim_maliyeti:,.2f}")
    st.write(f"- **Yapıştırma Maliyeti:** ₺{yapistirma_maliyeti:,.2f}")
    st.write(f"- **Nakliye Maliyeti:** ₺{nakliye_maliyeti:,.2f}")

    st.markdown("---")
    st.subheader("Maliyet ve Fiyatlandırma Özeti")
    st.metric("Toplam Maliyet", f"₺{toplam_maliyet:,.2f}")
    st.metric("Toplam Karlı Fiyat (Satış)", f"₺{toplam_karli_fiyat:,.2f}")
    st.metric("Net Kar Toplamı", f"₺{net_kar:,.2f}")
    st.metric("Birim Maliyet", f"₺{birim_maliyet:,.4f}")
    st.metric("Karlı Birim Fiyat (Adet)", f"₺{karli_birim_fiyat:,.4f}")
