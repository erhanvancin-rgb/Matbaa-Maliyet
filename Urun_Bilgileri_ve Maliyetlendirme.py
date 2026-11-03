import streamlit as st

def hesapla_maliyet(adet, gramaj, kagit_cinsi, baski_cmyk, laminasyon, baski_sonrasi, basilacak_ebat, fire_orani, ebat_en, ebat_boy, canli_usd, canli_eur):
    params = st.session_state.params
    ton_fiyat = params['bristol']
    birim_tip = 'USD'
    if kagit_cinsi == "Amerikan Bristol": ton_fiyat, birim_tip = params['bristol'], 'USD'
    elif kagit_cinsi == "Krome Karton": ton_fiyat, birim_tip = params['krome'], 'TL'
    elif kagit_cinsi == "Kuşe Kağıt": ton_fiyat, birim_tip = params['kuse'], 'EUR'
    elif kagit_cinsi == "1. Hamur Kağıt": ton_fiyat, birim_tip = params['hamur'], 'USD'

    ton_fiyat_tl = ton_fiyat
    if birim_tip == 'USD': ton_fiyat_tl = ton_fiyat * canli_usd
    elif birim_tip == 'EUR': ton_fiyat_tl = ton_fiyat * canli_eur

    brut_adet = int(adet * (1 + (fire_orani / 100)))
    tabaka_adeti = max(1, brut_adet // 2)
    
    kağıt_en_m = 0.70 if "70x100" in basilacak_ebat else (0.50 if "50x70" in basilacak_ebat else 0.35)
    kağıt_boy_m = 1.00 if "70x100" in basilacak_ebat else (0.70 if "50x70" in basilacak_ebat else 0.50)
    toplam_m2 = round(tabaka_adeti * kağıt_en_m * kağıt_boy_m, 2)

    kg_kagit = round((tabaka_adeti * kağıt_en_m * kağıt_boy_m * gramaj) / 1000, 2)
    kagit_maliyeti = (kg_kagit / 1000) * ton_fiyat_tl

    baski_maliyeti = params['b_5070_cmyk'] + (adet * params['b_5070_tiraj'] / 1000)
    if "70x100" in basilacak_ebat:
        baski_maliyeti = params['b_70100_cmyk'] + (adet * params['b_70100_tiraj'] / 1000)
    if baski_cmyk == "Çift Yüz": baski_maliyeti *= 1.8
    elif baski_cmyk == "CMYK Baskı Yok": baski_maliyeti = 0

    selofan_m2 = tabaka_adeti * 0.35
    selofan_maliyeti = 0
    if laminasyon == "Mat Selofan": selofan_maliyeti = selofan_m2 * params['mat_sel']
    elif laminasyon == "Parlak Selofan": selofan_maliyeti = selofan_m2 * params['par_sel']
    elif laminasyon == "Dispresiyon Lak": selofan_maliyeti = params['disp_5070'] + (adet * params['disp_5070_tiraj'] / 1000)

    kesim_maliyeti = 0
    if baski_sonrasi == "Özel Kesim": kesim_maliyeti = params['bobst'] + (adet * params['bobst_tiraj'])
    elif baski_sonrasi in ["Kutu Kesim + Yapıştırma", "Yan Yapıştırmalı Kutu", "Dip Yapıştırmalı Kutu"]:
        kesim_maliyeti = params['kazanli'] + (adet * params['kazanli_tiraj']) + params['omega_dip'] + (adet * params['omega_dip_tiraj'])
    elif baski_sonrasi == "Özel Kesim+Düz Kesim": kesim_maliyeti = (params['bobst'] + (adet * params['bobst_tiraj'])) * 1.3
    elif baski_sonrasi == "Pencereli Kutu Kesim+Yapıştırma": kesim_maliyeti = (params['kazanli'] + (adet * params['kazanli_tiraj']) + params['omega_dip'] + (adet * params['omega_dip_tiraj'])) * 1.4

    toplam_maliyet = kagit_maliyeti + baski_maliyeti + selofan_maliyeti + kesim_maliyeti
    return brut_adet, tabaka_adeti, toplam_m2, kg_kagit, kagit_maliyeti, baski_maliyeti, selofan_maliyeti, kesim_maliyeti, toplam_maliyet

def render_urun_bilgileri_ve_maliyetlendirme(canli_usd, canli_eur):
    st.subheader("📋 Matbaa Teklif & Maliyet Hesaplama Formu")
    st.markdown("---")

    # 1. Bölüm: Genel Bilgiler
    st.markdown("##### 1. Ürün Genel Bilgileri")
    col1, col2 = st.columns(2)
    with col1: firma_adi = st.text_input("Firma Adı", "Erhan Ticaret", key="form_firma")
    with col2: urun_adi = st.text_input("Ürün Adı", "Lüks Ambalaj Kutusu", key="form_urun_adi")

    urun_tipleri = ["Föy", "Tek Kırımlı Broşür", "İki Kırımlı Broşür", "Kartonet", "Yan Yapıştırmalı Kutu", "Dip Yapıştırmalı Kutu", "Sıvamalı Kutu", "Etiket", "Prospektüs"]
    urun_tipi = st.selectbox("Ürün Tipi", urun_tipleri, key="form_urun_tipi")

    st.markdown("---")

    # 2. Bölüm: 3'lü Adet / Tiraj Alternatifleri
    st.markdown("##### 2. Ürün Adedi (Tiraj Alternatifleri A, B, C)")
    col_a, col_b, col_c = st.columns(3)
    with col_a: adet_a = st.number_input("Adet A", value=1000, step=500, key="form_adet_a")
    with col_b: adet_b = st.number_input("Adet B", value=3000, step=500, key="form_adet_b")
    with col_c: adet_c = st.number_input("Adet C", value=5000, step=500, key="form_adet_c")

    st.markdown("---")

    # 3. Bölüm: Kağıt ve Malzeme Seçimi
    kagit_listesi = ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"]
    st.markdown("##### 3. Kağıt ve Malzeme Seçimi")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        st.markdown("**Kağıt Cinsi ve Gramajı (Ana)**")
        kagit_a = st.selectbox("Kağıt Cinsi A", kagit_listesi, key="form_kagit_a")
        gramaj_a = st.number_input("Gramaj A (gr/m²)", value=300, step=10, min_value=50, key="form_gramaj_a")
    with col_k2:
        st.markdown("**Kağıt Cinsi ve Gramajı Alternatif B**")
        kagit_b = st.selectbox("Kağıt Cinsi B", kagit_listesi, key="form_kagit_b")
        gramaj_b = st.number_input("Gramaj B (gr/m²)", value=350, step=10, min_value=50, key="form_gramaj_b")

    st.markdown("---")

    # 4. Bölüm: Baskı & Ölçüler
    st.markdown("##### 4. Baskı Detayları ve Planlama Kriterleri")
    col_bc1, col_bc2 = st.columns(2)
    with col_bc1: baski_cmyk = st.selectbox("Baskı CMYK", ["Tek Yüz", "Çift Yüz", "CMYK Baskı Yok"], key="form_baski_cmyk")
    with col_bc2: pantone_sayisi = st.selectbox("Baskı Pantone Renk Sayısı", ["Yok", "1 renk zemin", "2 renk zemin", "3 renk zemin", "4 renk zemin", "1 renk lokal", "2 renk lokal", "3 renk lokal", "4 renk lokal"], key="form_pantone_sayisi")

    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    with col_e1: ebat_en = st.number_input("En (mm)", value=200, key="form_ebat_en")
    with col_e2: ebat_boy = st.number_input("Boy (mm)", value=150, key="form_ebat_boy")
    with col_e3: ebat_yukseklik = st.number_input("Yükseklik (mm)", value=50, key="form_ebat_yukseklik")
    with col_e4: fire_orani = st.number_input("Fire Oranı (%)", value=5.0, step=0.5, key="form_fire_orani")

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1: basilacak_ebat = st.selectbox("Basılacak Kağıdın Ebadı", ["50x70 cm", "70x100 cm", "35x50 cm"], key="form_basilacak_ebat")
    with col_p2: baski_metodu = st.selectbox("Baskı Metodu", ["Tabaka Ofset", "Bobin Ofset", "Dijital Baskı"], key="form_baski_metodu")
    with col_p3: montaj_plani = st.selectbox("Montaj Planı", ["Forma (Tek Yüz)", "Karşılıklı Forma", "Özel Yerleşim"], key="form_montaj_plani")

    st.markdown("---")

    # 5. Bölüm: Yüzey İşlemleri ve Baskı Sonrası (Laminasyon solda, Özel Baskılar sağda)
    st.markdown("##### 5. Yüzey İşlemleri ve Mücellit")
    baski_sonrasi_secenekleri = ["Düz Kesim", "Özel Kesim", "Yan Yapıştırmalı Kutu", "Dip Yapıştırmalı Kutu", "Özel Kesim+Düz Kesim", "Pencereli Kutu Kesim+Yapıştırma"]
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        laminasyon = st.selectbox("Laminasyon", ["Parlak Selofan", "Mat Selofan", "Dispresiyon Lak", "Yok"], key="form_laminasyon")
        baski_sonrasi = st.selectbox("Baskı Sonrası", baski_sonrasi_secenekleri, key="form_baski_sonrasi")
    with col_l2:
        ozel_baski_1 = st.selectbox("Özel Baskılar 1", ["Yok", "Lokal Lak", "Kabartma Lak", "Gofre", "Varak Yaldız"], key="form_ozel_baski_1")
        ozel_baski_2 = st.selectbox("Özel Baskılar 2", ["Yok", "Lokal Lak", "Kabartma Lak", "Gofre", "Varak Yaldız"], key="form_ozel_baski_2")

    st.markdown("---")
    ozel_istekler = st.text_area("Özel İstekler / Notlar", placeholder="Müşteriye özel ek talepler...", key="form_ozel_istekler")

    st.markdown("---")
    st.markdown("### 📊 3 Farklı Adet (A, B, C) İçin Planlama ve Maliyet Dökümü")
    kar_orani = st.slider("Hedef Kar Marjı (%)", 0, 100, 30, key="form_kar_orani")

    # Adet A Hesaplaması
    res_a = hesapla_maliyet(adet_a, gramaj_a, kagit_a, baski_cmyk, laminasyon, baski_sonrasi, basilacak_ebat, fire_orani, ebat_en, ebat_boy, canli_usd, canli_eur)
    kar_a = res_a[8] * (kar_orani / 100)
    top_a = res_a[8] + kar_a

    # Adet B Hesaplaması
    res_b = hesapla_maliyet(adet_b, gramaj_a, kagit_a, baski_cmyk, laminasyon, baski_sonrasi, basilacak_ebat, fire_orani, ebat_en, ebat_boy, canli_usd, canli_eur)
    kar_b = res_b[8] * (kar_orani / 100)
    top_b = res_b[8] + kar_b

    # Adet C Hesaplaması
    res_c = hesapla_maliyet(adet_c, gramaj_a, kagit_a, baski_cmyk, laminasyon, baski_sonrasi, basilacak_ebat, fire_orani, ebat_en, ebat_boy, canli_usd, canli_eur)
    kar_c = res_c[8] * (kar_orani / 100)
    top_c = res_c[8] + kar_c

    tab1, tab2, tab3 = st.tabs([f"🔹 Adet A ({adet_a:,})", f"🔹 Adet B ({adet_b:,})", f"🔹 Adet C ({adet_c:,})"])

    with tab1:
        st.markdown(f"**Tiraj A: {adet_a:,} Adet Özet Raporu**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Brüt Adet", f"{res_a[0]:,} adet")
        c2.metric("Tabaka", f"{res_a[1]:,} tabaka")
        c3.metric("Kağıt Kg", f"{res_a[3]} kg")
        c4.metric("Toplam Alan", f"{res_a[2]:,.2f} m²")
        
        f1, f2, f3 = st.columns(3)
        f1.metric("Toplam Maliyet", f"₺{res_a[8]:,.2f}")
        f2.metric("Karlı Satış (Toplam)", f"₺{top_a:,.2f}")
        f3.metric("Karlı Birim Fiyat", f"₺{top_a/adet_a:,.4f}")

    with tab2:
        st.markdown(f"**Tiraj B: {adet_b:,} Adet Özet Raporu**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Brüt Adet", f"{res_b[0]:,} adet")
        c2.metric("Tabaka", f"{res_b[1]:,} tabaka")
        c3.metric("Kağıt Kg", f"{res_b[3]} kg")
        c4.metric("Toplam Alan", f"{res_b[2]:,.2f} m²")
        
        f1, f2, f3 = st.columns(3)
        f1.metric("Toplam Maliyet", f"₺{res_b[8]:,.2f}")
        f2.metric("Karlı Satış (Toplam)", f"₺{top_b:,.2f}")
        f3.metric("Karlı Birim Fiyat", f"₺{top_b/adet_b:,.4f}")

    with tab3:
        st.markdown(f"**Tiraj C: {adet_c:,} Adet Özet Raporu**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Brüt Adet", f"{res_c[0]:,} adet")
        c2.metric("Tabaka", f"{res_c[1]:,} tabaka")
        c3.metric("Kağıt Kg", f"{res_c[3]} kg")
        c4.metric("Toplam Alan", f"{res_c[2]:,.2f} m²")
        
        f1, f2, f3 = st.columns(3)
        f1.metric("Toplam Maliyet", f"₺{res_c[8]:,.2f}")
        f2.metric("Karlı Satış (Toplam)", f"₺{top_c:,.2f}")
        f3.metric("Karlı Birim Fiyat", f"₺{top_c/adet_c:,.4f}")
