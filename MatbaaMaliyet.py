import streamlit as st
import xml.etree.ElementTree as ET
import urllib.request

st.set_page_config(page_title="Matbaa ve Ambalaj Maliyet Sistemi", layout="wide")

# --- TCMB'DEN ANLIK EFEKTİF SATIŞ KURLARINI ÇEKME ---
@st.cache_data(ttl=3600)
def tcmb_kurlarini_getir():
    usd_kur = 49.97  
    eur_kur = 56.00  
    try:
        url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        req = urllib.request.urlopen(url, timeout=5)
        root = ET.fromstring(req.read())
        
        for currency in root.findall('Currency'):
            code = currency.get('CurrencyCode')
            if code == 'USD':
                val = currency.find('BanknoteSelling').text
                if val: usd_kur = float(val)
            elif code == 'EUR':
                val = currency.find('BanknoteSelling').text
                if val: eur_kur = float(val)
    except Exception:
        pass
    return usd_kur, eur_kur

canli_usd, canli_eur = tcmb_kurlarini_getir()

# Oturum Durumu ve Orijinal Excel Parametreleri
if 'page' not in st.session_state:
    st.session_state.page = 'home'

default_params = {
    'bristol': 825.0, 'krome': 40000.0, 'kuse': 850.0, 'hamur': 1200.0,
    'b_3550_cmyk': 1800.0, 'b_3550_pantone': 900.0, 'b_3550_tiraj': 400.0,
    'b_5070_cmyk': 3500.0, 'b_5070_pantone': 1750.0, 'b_5070_tiraj': 800.0,
    'b_70100_cmyk': 5000.0, 'b_70100_pantone': 1750.0, 'b_70100_tiraj': 1400.0,
    'disp_5070': 1500.0, 'disp_5070_tiraj': 800.0, 'disp_70100': 2000.0, 'disp_70100_tiraj': 1000.0,
    'mat_sel': 4.70, 'par_sel': 4.50, 'lokal_5070': 1500.0, 'lokal_5070_tiraj': 1.5,
    'lokal_70100': 1800.0, 'lokal_70100_tiraj': 1.5, 'kab_5070': 1600.0, 'kab_5070_tiraj': 1.6,
    'kab_70100': 1900.0, 'kab_70100_tiraj': 1.9, 'kazanli': 1800.0, 'kazanli_tiraj': 0.75,
    'pedal': 2500.0, 'pedal_tiraj': 1.0, 'bobst': 3000.0, 'bobst_tiraj': 1.5,
    'omega_tek': 2000.0, 'omega_tek_tiraj': 0.2, 'omega_dip': 2500.0, 'omega_dip_tiraj': 0.25
}

if 'params' not in st.session_state:
    st.session_state.params = default_params
else:
    for k, v in default_params.items():
        if k not in st.session_state.params:
            st.session_state.params[k] = v

def go_home(): st.session_state.page = 'home'
def go_params(): st.session_state.page = 'params'
def go_calc(): st.session_state.page = 'calc'

# Üst Bilgi
st.markdown("### 🖨️ MATBAAM PRO - Ambalaj & Matbaa Maliyet Sistemi")
st.info(f"🏦 TCMB Anlık Efektif Satış Kurları — USD: ₺{canli_usd:.2f} | EUR: ₺{canli_eur:.2f}")
st.markdown("---")

# 1. ANA SAYFA
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
        
    st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi (Orijinal Excel Verileri)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 1. Kağıt ve Karton Grubu")
        st.session_state.params['bristol'] = st.number_input("Amerikan Bristol Ton ($)", value=st.session_state.params['bristol'], key="p_bris")
        st.session_state.params['krome'] = st.number_input("Krome Karton Ton (TL)", value=st.session_state.params['krome'], key="p_krom")
        st.session_state.params['kuse'] = st.number_input("Kuşe Ton (€)", value=st.session_state.params['kuse'], key="p_kus")
        st.session_state.params['hamur'] = st.number_input("1. Hamur Ton ($)", value=st.session_state.params['hamur'], key="p_ham")
        
        st.markdown("#### 3. Yüzey İşlemleri ve Lak")
        st.session_state.params['disp_5070'] = st.number_input("50x70 Dispresiyon Lak", value=st.session_state.params['disp_5070'], key="p_d50")
        st.session_state.params['mat_sel'] = st.number_input("Mat Selofan M2", value=st.session_state.params['mat_sel'], key="p_msel")
        st.session_state.params['par_sel'] = st.number_input("Parlak Selofan M2", value=st.session_state.params['par_sel'], key="p_psel")
        st.session_state.params['lokal_5070'] = st.number_input("Lokal Lak 50x70", value=st.session_state.params['lokal_5070'], key="p_l50")

    with col2:
        st.markdown("#### 2. Baskı Grubu")
        st.session_state.params['b_5070_cmyk'] = st.number_input("50x70 Cmyk Proses", value=st.session_state.params['b_5070_cmyk'], key="p_b50c")
        st.session_state.params['b_5070_tiraj'] = st.number_input("50x70 Tiraj Fiyatı", value=st.session_state.params['b_5070_tiraj'], key="p_b50t")
        st.session_state.params['b_70100_cmyk'] = st.number_input("70x100 Cmyk Proses", value=st.session_state.params['b_70100_cmyk'], key="p_b70c")
        st.session_state.params['b_70100_tiraj'] = st.number_input("70x100 Tiraj Fiyatı", value=st.session_state.params['b_70100_tiraj'], key="p_b70t")

        st.markdown("#### 4. Kesim ve Mücellit Grubu")
        st.session_state.params['kazanli'] = st.number_input("Kazanlı Kesim", value=st.session_state.params['kazanli'], key="p_kaz")
        st.session_state.params['pedal'] = st.number_input("Pedal Kesim", value=st.session_state.params['pedal'], key="p_ped")
        st.session_state.params['bobst'] = st.number_input("Bobts Kesim", value=st.session_state.params['bobst'], key="p_bob")
        st.session_state.params['omega_dip'] = st.number_input("Omega Dip Yapıştırma", value=st.session_state.params['omega_dip'], key="p_omd")

# 3. FİYAT ÇIKART (HESAPLAMA SAYFASI - DİSİPLİNLİ FORM & 3'LÜ ADET ANALİZİ)
elif st.session_state.page == 'calc':
    if st.button("⬅️ Ana Menüye Dön"):
        go_home()
        st.rerun()
        
    def hesapla_maliyet(adet, gramaj, kagit_cinsi, baski_cmyk, laminasyon, baski_sonrasi, basilacak_ebat, fire_orani, ebat_en, ebat_boy):
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

    # 5. Bölüm: Yüzey İşlemleri ve Baskı Sonrası
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

    # A, B, C hesaplamaları
    res_a = hesapla_maliyet(adet_a, gramaj_a, kagit_a, baski_cmyk, laminasyon, baski_sonrasi, basilacak_ebat, fire_orani, ebat_en, ebat_boy)
    kar_a = res_a[8] * (kar_orani / 100)
    top_a = res_a[8] + kar_a

    res_b = hesapla_maliyet(adet_b, gramaj_a, kagit_a, baski_cmyk, laminasyon, baski_sonrasi, basilacak_ebat, fire_orani, ebat_en, ebat_boy)
    kar_b = res_b[8] * (kar_orani / 100)
    top_b = res_b[8] + kar_b

    res_c = hesapla_maliyet(adet_c, gramaj_a, kagit_a, baski_cmyk, laminasyon, baski_sonrasi, basilacak_ebat, fire_orani, ebat_en, ebat_boy)
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
