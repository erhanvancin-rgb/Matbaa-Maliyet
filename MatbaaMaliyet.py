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

# --- OTURUM VE PARAMETRELER ---
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

# --- ÜST BİLGİ ---
st.markdown("### 🖨️ MATBAAM PRO - Ambalaj & Matbaa Maliyet Sistemi")
st.info(f"🏦 TCMB Anlık Efektif Satış Kurları — USD: ₺{canli_usd:.2f} | EUR: ₺{canli_eur:.2f}")
st.markdown("---")

# ==========================================
# 1. ANA SAYFA
# ==========================================
if st.session_state.page == 'home':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>Yönetim & Hesaplama Modülü</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("1. Parametreler (Fiyat Listesi)", use_container_width=True):
            go_params()
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("2. Fiyat Çıkart (Maliyet Hesaplama Formu)", use_container_width=True):
            go_calc()
            st.rerun()

# ==========================================
# 2. PARAMETRELER SAYFASI
# ==========================================
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

# ==========================================
# 3. FİYAT ÇIKART (DİSİPLİNLİ FORM SAYFASI)
# ==========================================
elif st.session_state.page == 'calc':
    if st.button("⬅️ Ana Menüye Dön"):
        go_home()
        st.rerun()

    # --- HESAPLAMA FONKSİYONU ---
    def hesapla_maliyet(adet, gramaj, kagit_cinsi, on_arka_baski, laminasyon, baski_sonrasi, basilacak_ebat, fire_orani, ebat_en, ebat_boy):
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
        
        if on_arka_baski == "Ön ve Arka Baskı": 
            baski_maliyeti *= 1.8
        elif on_arka_baski == "Baskı Yok": 
            baski_maliyeti = 0

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

    # --- BÖLÜM 1: GENEL ÜRÜN BİLGİLERİ VE KAĞIT ---
    st.markdown("##### 1. Ürün ve Kağıt Bilgileri")
    col1, col2, col3 = st.columns(3)
    with col1: 
        firma_adi = st.text_input("Firma Adı", "Erhan Ticaret")
        urun_tipleri = ["Föy", "Tek Kırımlı Broşür", "İki Kırımlı Broşür", "Kartonet", "Yan Yapıştırmalı Kutu", "Dip Yapıştırmalı Kutu", "Sıvamalı Kutu", "Etiket", "Prospektüs"]
        urun_tipi = st.selectbox("Ürün Tipi", urun_tipleri)
    with col2: 
        urun_adi = st.text_input("Ürün Adı", "Lüks Ambalaj Kutusu")
        kagit_cinsi = st.selectbox("Kağıt Cinsi", ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"])
    with col3:
        gramaj = st.number_input("Kağıt Gramajı (gr/m²)", value=300, step=10)
        pantone_sayisi = st.selectbox("Baskı Pantone Renk Sayısı", ["Yok", "1 renk zemin", "2 renk zemin", "1 renk lokal", "2 renk lokal"])

    st.markdown("---")

    # --- BÖLÜM 2: EBAT VE YÜZEY İŞLEMLERİ ---
    st.markdown("##### 2. Bitmiş Ebat ve Baskı Sonrası İşlemler")
    ce1, ce2, ce3 = st.columns(3)
    with ce1: ebat_en = st.number_input("En (mm)", value=200)
    with ce2: ebat_boy = st.number_input("Boy (mm)", value=150)
    with ce3: ebat_yukseklik = st.number_input("Yükseklik (mm)", value=50)

    cl1, cl2, cl3 = st.columns(3)
    with cl1:
        laminasyon = st.selectbox("Laminasyon", ["Parlak Selofan", "Mat Selofan", "Dispresiyon Lak", "Yok"])
    with cl2:
        baski_sonrasi_secenekleri = ["Düz Kesim", "Özel Kesim", "Yan Yapıştırmalı Kutu", "Dip Yapıştırmalı Kutu", "Özel Kesim+Düz Kesim", "Pencereli Kutu Kesim+Yapıştırma"]
        baski_sonrasi = st.selectbox("Baskı Sonrası Kesim/Mücellit", baski_sonrasi_secenekleri)
    with cl3:
        ozel_baski_1 = st.selectbox("Özel İşlem (Yaldız/Lak/Gofre)", ["Yok", "Lokal Lak", "Kabartma Lak", "Gofre", "Varak Yaldız"])

    st.markdown("---")

    # --- BÖLÜM 3: 3'LÜ ADET VE MATBAA PLANLAMA ---
    st.markdown("##### 3. Tiraj Seçenekleri ve Matbaa Planlama Kriterleri")
    st.caption("Her adet için ayrı ebat, montaj ve fire planlaması yapabilirsiniz.")
    
    col_a, col_b, col_c = st.columns(3)
    
    # Sütun A
    with col_a:
        st.markdown("#### 🔵 Alternatif A")
        adet_a = st.number_input("Net Adet", value=1000, step=500, key="a_adet")
        plan_a = st.text_input("Plan", "Standart", key="a_plan")
        fire_a = st.number_input("Fire Oranı (%)", value=5.0, step=0.5, key="a_fire")
        montaj_a = st.selectbox("Montaj Planı", ["Forma (Tek Yüz)", "Karşılıklı Forma", "Özel Yerleşim"], key="a_mon")
        ebat_a = st.selectbox("Basılacak Kağıdın Ebadı", ["35x50 cm", "50x70 cm", "70x100 cm"], index=1, key="a_ebat")
        onarka_a = st.selectbox("Baskı Adedi Ön ve Arka", ["Tek Yüz Baskı", "Ön ve Arka Baskı", "Baskı Yok"], key="a_onarka")
        metod_a = st.selectbox("Baskı Metodu", ["Tabaka Ofset", "Bobin Ofset"], key="a_metod")

    # Sütun B
    with col_b:
        st.markdown("#### 🟢 Alternatif B")
        adet_b = st.number_input("Net Adet", value=3000, step=500, key="b_adet")
        plan_b = st.text_input("Plan", "Standart", key="b_plan")
        fire_b = st.number_input("Fire Oranı (%)", value=4.5, step=0.5, key="b_fire")
        montaj_b = st.selectbox("Montaj Planı", ["Forma (Tek Yüz)", "Karşılıklı Forma", "Özel Yerleşim"], key="b_mon")
        ebat_b = st.selectbox("Basılacak Kağıdın Ebadı", ["35x50 cm", "50x70 cm", "70x100 cm"], index=1, key="b_ebat")
        onarka_b = st.selectbox("Baskı Adedi Ön ve Arka", ["Tek Yüz Baskı", "Ön ve Arka Baskı", "Baskı Yok"], key="b_onarka")
        metod_b = st.selectbox("Baskı Metodu", ["Tabaka Ofset", "Bobin Ofset"], key="b_metod")

    # Sütun C
    with col_c:
        st.markdown("#### 🟠 Alternatif C")
        adet_c = st.number_input("Net Adet", value=5000, step=500, key="c_adet")
        plan_c = st.text_input("Plan", "Standart", key="c_plan")
        fire_c = st.number_input("Fire Oranı (%)", value=4.0, step=0.5, key="c_fire")
        montaj_c = st.selectbox("Montaj Planı", ["Forma (Tek Yüz)", "Karşılıklı Forma", "Özel Yerleşim"], key="c_mon")
        ebat_c = st.selectbox("Basılacak Kağıdın Ebadı", ["35x50 cm", "50x70 cm", "70x100 cm"], index=2, key="c_ebat")
        onarka_c = st.selectbox("Baskı Adedi Ön ve Arka", ["Tek Yüz Baskı", "Ön ve Arka Baskı", "Baskı Yok"], key="c_onarka")
        metod_c = st.selectbox("Baskı Metodu", ["Tabaka Ofset", "Bobin Ofset"], key="c_metod")

    st.markdown("---")
    kar_orani = st.slider("Hedef Kar Marjı (%)", 0, 100, 30)

    # --- HESAPLAMA VE SONUÇLAR ---
    st.markdown("### 📊 Sonuçlar: Brüt Adet, Kağıt Kilogram ve Finansal Döküm")

    res_a = hesapla_maliyet(adet_a, gramaj, kagit_cinsi, onarka_a, laminasyon, baski_sonrasi, ebat_a, fire_a, ebat_en, ebat_boy)
    res_b = hesapla_maliyet(adet_b, gramaj, kagit_cinsi, onarka_b, laminasyon, baski_sonrasi, ebat_b, fire_b, ebat_en, ebat_boy)
    res_c = hesapla_maliyet(adet_c, gramaj, kagit_cinsi, onarka_c, laminasyon, baski_sonrasi, ebat_c, fire_c, ebat_en, ebat_boy)

    tab1, tab2, tab3 = st.tabs([f"A: {adet_a:,} Adet", f"B: {adet_b:,} Adet", f"C: {adet_c:,} Adet"])

    def goster_sonuclar(adet, res):
        kar = res[8] * (kar_orani / 100)
        toplam_fiyat = res[8] + kar
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Brüt Adet (Fireli)", f"{res[0]:,} adet")
        c2.metric("Kağıt Kilogram", f"{res[3]} kg")
        c3.metric("Kaç M2", f"{res[2]:,.2f} m²")
        c4.metric("Tabaka Adedi", f"{res[1]:,} tabaka")
        
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Kağıt Maliyeti", f"₺{res[4]:,.2f}")
        f2.metric("Toplam Baskı Maliyeti", f"₺{res[5]:,.2f}")
        f3.metric("Toplam Üretim Maliyeti", f"₺{res[8]:,.2f}")
        f4.metric("Karlı Toplam Satış", f"₺{toplam_fiyat:,.2f}")
        
        st.info(f"**Birim Maliyet:** ₺{res[8]/adet:,.4f} &nbsp;&nbsp;|&nbsp;&nbsp; **Karlı Birim Satış Fiyatı:** ₺{toplam_fiyat/adet:,.4f}")

    with tab1: goster_sonuclar(adet_a, res_a)
    with tab2: goster_sonuclar(adet_b, res_b)
    with tab3: goster_sonuclar(adet_c, res_c)
