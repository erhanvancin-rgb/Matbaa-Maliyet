import streamlit as st

# Sayfa Yapılandırması ve Geniş Mod
st.set_page_config(page_title="Matbaa Ambalaj Maliyet & Fiyatlandırma Sistemi", layout="wide")

# Koyu / Mavi Kurumsal Tasarım Stilleri (CSS)
st.markdown("""
    <style>
        .main { background-color: #0e1117; }
        .stApp { background-color: #0e1117; color: #c9d1d9; }
        .card-header { background: linear-gradient(135deg, #1f2937 0%, #111827 100%); color: #f59e0b; padding: 12px; border-radius: 6px 6px 0 0; font-weight: bold; border-bottom: 2px solid #f59e0b; }
        .section-box { background-color: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 20px; }
        .metric-card { background-color: #21262d; padding: 15px; border-radius: 6px; border: 1px solid #30363d; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Üst Başlık ve Logo Alanı
st.markdown("<h1 style='color: #f59e0b; text-align: center;'>MATBAAM - Ambalaj ve Matbaa Maliyet Analiz Sistemi</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Parametrik Maliyet ve Teklif Hesaplama Modülü (Güncel Kur / Tarih: 28.01.2026)</p>", unsafe_allow_html=True)
st.markdown("---")

# Ana Sayfa Düzeni (2 Sütun: Sol Parametreler ve Tablolar, Sağ Form ve Hesaplama)
col_left, col_right = st.columns([5, 7], gap="large")

with col_left:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Matbaa Maliyet Parametreleri Fiyat Listesi</div>', unsafe_allow_html=True)
    
    # 1. Kağıt ve Karton Grubu
    st.markdown("#### 1. Kağıt ve Karton Grubu (Ton Maliyetleri)")
    p_bristol = st.number_input("Amerikan Bristol Ton ($/€)", value=1200.0, step=50.0)
    p_krome = st.number_input("Krome Karton Ton ($/€)", value=1100.0, step=50.0)
    p_kuse = st.number_input("Kuşe Ton ($/€)", value=1050.0, step=50.0)
    p_hamur = st.number_input("1. Hamur Ton ($/€)", value=1150.0, step=50.0)

    # 2. Baskı Grubu
    st.markdown("#### 2. Baskı Grubu (Ebat, Renk ve Tiraj)")
    baski_5070_cmyk = st.number_input("50x70 Cmyk Proses Fiyat (TL)", value=2500.0)
    baski_5070_tiraj = st.number_input("50x70 Tiraj Fiyatı (TL)", value=1.50)
    baski_70100_cmyk = st.number_input("70x100 Cmyk Proses Fiyat (TL)", value=3500.0)
    baski_70100_tiraj = st.number_input("70x100 Tiraj Fiyatı (TL)", value=2.00)

    # 3. Yüzey İşlemleri ve Lak Grubu
    st.markdown("#### 3. Yüzey İşlemleri ve Lak Grubu")
    p_mat_selofan = st.number_input("Mat Selofan M2 Fiyatı (TL)", value=4.0)
    p_parlak_selofan = st.number_input("Parlak Selofan M2 Fiyatı (TL)", value=3.5)
    p_lokal_lak = st.number_input("Lokal Lak 50x70 Tabaka (TL)", value=1.20)
    p_kabartma_lak = st.number_input("Kabartma Lak 50x70 Tabaka (TL)", value=1.50)

    # 4. Kesim ve Mücellit Grubu
    st.markdown("#### 4. Kesim ve Mücellit Grubu")
    p_kazanli_kesim = st.number_input("Kazanlı/Pedal Kesim Çember (TL)", value=1500.0)
    p_kazanli_tiraj = st.number_input("Kazanlı Kesim Tiraj (Adet)", value=1.50)
    p_bobst_kesim = st.number_input("Bobst Kesim Çember (TL)", value=2500.0)
    p_yapistirma_tiraj = st.number_input("Omega Yapıştırma Tiraj (Adet)", value=0.50)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Ürün Tanımlama ve Proses Bilgileri</div>', unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        firma = st.text_input("Firma Adı", "Erhan Ticaret")
        urun_adi = st.text_input("Ürün Adı / Modeli", "Lüks Kutu / Ambalaj")
    with col_f2:
        adet = st.number_input("Ürün Adedi (Tiraj)", value=5000, step=500, min_value=1)
        kutu_tipi = st.selectbox("Kutu / Ambalaj Modeli", ["Kilitli Dip Kutu", "Omega Yapıştırma Kutu", "Sallantı Etiket", "Katalog / Broşür", "E-Ticaret Kargo Kutusu"])

    st.markdown("---")
    st.markdown("#### Kağıt ve Malzeme Detayları (Cins ve Gramaj Seçimi)")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        kagit_cinsi = st.selectbox("Kağıt Cinsi", [
            "Amerikan Bristol", 
            "Krome Karton", 
            "Kuşe Kağıt", 
            "1. Hamur Kağıt"
        ])
    with col_k2:
        kagit_gramaj = st.selectbox("Kağıt Gramajı (gr/m²)", [
            "200 gr", 
            "250 gr", 
            "300 gr", 
            "350 gr", 
            "400 gr"
        ])

    st.markdown("---")
    st.markdown("#### Ebat ve Baskı Parametreleri")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1: ebat_x = st.number_input("En (mm)", value=200)
    with col_e2: ebat_y = st.number_input("Boy (mm)", value=150)
    with col_e3: ebat_z = st.number_input("Yükseklik (mm)", value=50)

    baski_turu = st.selectbox("Baskı Ebadı ve Türü", ["50x70 CMYK", "70x100 CMYK", "35x50 CMYK", "Pantone Özel Renk"])
    laminasyon = st.selectbox("Yüzey Laminasyonu", ["Mat Selofan", "Parlak Selofan", "Yok"])
    
    col_is1, col_is2 = st.columns(2)
    with col_is1:
        sivama = st.selectbox("Sıvama / Ondüle", ["Ondüle / Sıvama Var", "Yok"])
        kesim_turu = st.selectbox("Kesim Türü", ["Bobst Kesim", "Kazanlı / Pedal Kesim", "Yok"])
    with col_is2:
        yapistirma_var = st.checkbox("Omega Yapıştırma Var", value=True)
        nakliye_var = st.checkbox("Nakliye / Lojistik Dahil", value=True)

    kar_orani = st.slider("Hedef Kar Marjı (%)", min_value=10, max_value=100, value=30, step=5)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- HESAPLAMA MOTORU ---
    # Gramaj faktörü hesaplama
    gram_val = float(kagit_gramaj.replace(" gr", ""))
    
    # Ton fiyatı belirleme
    ton_fiyat_eur = p_bristol
    if "Krome" in kagit_cinsi: ton_fiyat_eur = p_krome
    elif "Kuşe" in kagit_cinsi: ton_fiyat_eur = p_kuse
    elif "Hamur" in kagit_cinsi: ton_fiyat_eur = p_hamur

    eur_kur = 35.0  # Sabit baz Euro kuru
    ton_fiyat_tl = ton_fiyat_eur * eur_kur

    tabaka_adeti = max(1, adet // 2)
    # Kağıt kg hesabı (Gramaj ve ebat bazlı simülasyon)
    kg_kagit = round((tabaka_adeti * (ebat_x/1000) * (ebat_y/1000) * gram_val) / 2)
    kagit_maliyeti = (kg_kagit / 1000) * ton_fiyat_tl

    # Baskı Maliyeti
    baski_maliyeti = baski_5070_cmyk + (adet * baski_5070_tiraj)
    if "70x100" in baski_turu:
        baski_maliyeti = baski_70100_cmyk + (adet * baski_70100_tiraj)

    # Selofan Maliyeti
    selofan_m2 = tabaka_adeti * 0.35
    selofan_birim = p_mat_selofan if laminasyon == "Mat Selofan" else p_parlak_selofan
    selofan_maliyeti = selofan_m2 * selofan_birim if laminasyon != "Yok" else 0

    # Ek Proses Maliyetleri
    sivama_maliyeti = tabaka_adeti * 2.5 if sivama == "Ondüle / Sıvama Var" else 0
    kesim_maliyeti = p_bobst_kesim + (adet * p_kazanli_tiraj) if kesim_turu != "Yok" else 0
    yapistirma_maliyeti = adet * p_yapistirma_tiraj if yapistirma_var else 0
    nakliye_maliyeti = 4000.0 if nakliye_var else 0

    toplam_maliyet = kagit_maliyeti + baski_maliyeti + selofan_maliyeti + sivama_maliyeti + kesim_maliyeti + yapistirma_maliyeti + nakliye_maliyeti
    net_kar = toplam_maliyet * (kar_orani / 100)
    toplam_karli_fiyat = toplam_maliyet + net_kar
    birim_maliyet = toplam_maliyet / adet if adet > 0 else 0
    karli_birim_fiyat = toplam_karli_fiyat / adet if adet > 0 else 0

    # --- PLANLAMA VE PROSES BİLGİLERİ ---
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Planlama ve Proses Detayları</div>', unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    col_p1.metric("Kağıt Miktarı", f"{kg_kagit} kg")
    col_p2.metric("Tabaka Adedi", f"{tabaka_adeti:,} adet")
    col_p3.metric("Baskı Maliyeti", f"₺{baski_maliyeti:,.2f}")

    col_p4, col_p5, col_p6 = st.columns(3)
    col_p4.metric("Selofan Maliyeti", f"₺{selofan_maliyeti:,.2f}")
    col_p5.metric("Kesim Maliyeti", f"₺{kesim_maliyeti:,.2f}")
    col_p6.metric("Yapıştırma / Nakliye", f"₺{yapistirma_maliyeti + nakliye_maliyeti:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- MALİYET VE FİYATLANDIRMA ÖZETİ ---
    st.markdown('<div class="section-box" style="background-color: #111827; border: 2px solid #f59e0b;">', unsafe_allow_html=True)
    st.markdown('<div class="card-header" style="background: #f59e0b; color: #000;">Maliyet ve Karlı Fiyatlandırma Özeti</div>', unsafe_allow_html=True)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Toplam Maliyet", f"₺{toplam_maliyet:,.2f}")
    col_m2.metric("Net Kar Toplamı", f"₺{net_kar:,.2f}")
    col_m3.metric("Toplam Karlı Fiyat", f"₺{toplam_karli_fiyat:,.2f}")

    col_m4, col_m5 = st.columns(2)
    col_m4.metric("Birim Maliyet (Adet)", f"₺{birim_maliyet:,.4f}")
    col_m5.metric("Karlı Birim Fiyat (Satış)", f"₺{karli_birim_fiyat:,.4f}")
    
    st.markdown('</div>', unsafe_allow_html=True)
