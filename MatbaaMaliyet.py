import streamlit as st
import xml.etree.ElementTree as ET
import urllib.request
import math
import pandas as pd
import json
import os

st.set_page_config(page_title="Matbaa ve Ambalaj Maliyet & Teklif Sistemi", layout="wide")

# --- 0. KALICI JSON PARAMETRE YÖNETİMİ VE STATE SENKRONİZASYONU ---
PARAM_FILE = "matbaa_parametreleri.json"

default_params = {
    'bristol': 825.0, 'krome': 40000.0, 'kuse': 850.0, 'hamur': 1200.0,
    'b_3550_cmyk': 2400.0, 'b_3550_pantone': 1200.0, 'b_3550_tiraj': 500.0,
    'b_5070_cmyk': 3500.0, 'b_5070_pantone': 1750.0, 'b_5070_tiraj': 800.0,
    'b_70100_cmyk': 5000.0, 'b_70100_pantone': 1750.0, 'b_70100_tiraj': 1400.0,
    'disp_5070': 1500.0, 'disp_5070_tiraj': 800.0,
    'disp_70100': 2000.0, 'disp_70100_tiraj': 1000.0,
    'mat_sel': 4.70, 'par_sel': 4.50,
    'lokal_5070': 1500.0, 'lokal_5070_tiraj': 1.5,
    'lokal_70100': 1800.0, 'lokal_70100_tiraj': 1.5,
    'kab_5070': 1600.0, 'kab_5070_tiraj': 1.6,
    'kab_70100': 1900.0, 'kab_70100_tiraj': 1.9,
    'kazanli': 1800.0, 'kazanli_tiraj': 0.75,
    'pedal': 2500.0, 'pedal_tiraj': 1.0,
    'bobst': 3000.0, 'bobst_tiraj': 1.5,
    'omega_tek': 2000.0, 'omega_tek_tiraj': 0.2,
    'omega_dip': 2500.0, 'omega_dip_tiraj': 0.25
}

def parametreleri_yukle():
    if os.path.exists(PARAM_FILE):
        try:
            with open(PARAM_FILE, "r", encoding="utf-8") as f:
                kayitli = json.load(f)
                for k, v in default_params.items():
                    if k not in kayitli:
                        kayitli[k] = v
                return kayitli
        except Exception:
            return default_params.copy()
    return default_params.copy()

def parametreleri_kaydet(params_dict):
    try:
        with open(PARAM_FILE, "w", encoding="utf-8") as f:
            json.dump(params_dict, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

if 'params' not in st.session_state:
    st.session_state.params = parametreleri_yukle()

# --- 1. TCMB ANLIK EFEKTİF SATIŞ KURLARINI ÇEKME ---
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

# --- 2. OTURUM DURUMU ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'teklif_data' not in st.session_state:
    st.session_state.teklif_data = None

def go_page(page_name):
    st.session_state.page = page_name

# --- 3. ÜST GEZİNTİ VE 4'LÜ GEÇİŞ BUTONLARI ---
st.markdown("### 🖨️ MATBAAM PRO - Ambalaj & Matbaa Maliyet ve Teklif Sistemi")
st.info(f"🏦 TCMB Anlık Efektif Satış Kurları — USD: ₺{canli_usd:.2f} | EUR: ₺{canli_eur:.2f}")

nav_c1, nav_c2, nav_c3, nav_c4 = st.columns(4)
with nav_c1:
    type_a = "primary" if st.session_state.page == 'home' else "secondary"
    if st.button("🏠 1. Ana Menü", use_container_width=True, type=type_a, key="btn_nav_home"):
        go_page('home')
        st.rerun()
with nav_c2:
    type_b = "primary" if st.session_state.page == 'params' else "secondary"
    if st.button("⚙️ 2. Parametreler (37 Kalem)", use_container_width=True, type=type_b, key="btn_nav_params"):
        go_page('params')
        st.rerun()
with nav_c3:
    type_c = "primary" if st.session_state.page == 'calc' else "secondary"
    if st.button("📋 3. Fiyat Çıkart (Form)", use_container_width=True, type=type_c, key="btn_nav_calc"):
        go_page('calc')
        st.rerun()
with nav_c4:
    type_d = "primary" if st.session_state.page == 'teklif' else "secondary"
    if st.button("📄 4. Müşteri Fiyat Teklifi", use_container_width=True, type=type_d, key="btn_nav_teklif"):
        go_page('teklif')
        st.rerun()

st.markdown("---")

# ==========================================
# MENÜ 1: ANA SAYFA
# ==========================================
if st.session_state.page == 'home':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>Yönetim & Hesaplama Modülü</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("1. Parametreler (Fiyat Listesi Yönetimi - 37 Kalem)", use_container_width=True, key="main_btn_params"):
            go_page('params')
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("2. Fiyat Çıkart (Maliyet Hesaplama Formu)", use_container_width=True, key="main_btn_calc"):
            go_page('calc')
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("3. 📄 Müşteri Fiyat Teklifi Mektubu ve Tablosu", use_container_width=True, key="main_btn_teklif"):
            go_page('teklif')
            st.rerun()

# ==========================================
# MENÜ 2: PARAMETRELER SAYFASI (STATE KORUMALI)
# ==========================================
elif st.session_state.page == 'params':
    st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi (Excel 37 Parametre Tam Listesi)")
    st.caption("Değiştirdiğiniz tüm fiyatlar otomatik olarak kalıcı dosyaya kaydedilir ve sayfa geçişlerinde sıfırlanmaz.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 1. Kağıt ve Karton Grubu (Ton Maliyetleri)")
        st.session_state.params['bristol'] = st.number_input("Amerikan Bristol Ton ($ USD)", value=float(st.session_state.params['bristol']), key="p_bris")
        st.session_state.params['krome'] = st.number_input("Krome Karton Ton (TL)", value=float(st.session_state.params['krome']), key="p_krom")
        st.session_state.params['kuse'] = st.number_input("Kuşe Ton (€ EUR)", value=float(st.session_state.params['kuse']), key="p_kus")
        st.session_state.params['hamur'] = st.number_input("1. Hamur Ton ($ USD)", value=float(st.session_state.params['hamur']), key="p_ham")
        
        st.markdown("---")
        st.markdown("#### 2. Baskı Grubu (9 Parametre)")
        st.markdown("##### 📐 35x50 Ebadı")
        st.session_state.params['b_3550_cmyk'] = st.number_input("35x50 CMYK Hazırlık (₺)", value=float(st.session_state.params['b_3550_cmyk']), key="p_b35c")
        st.session_state.params['b_3550_pantone'] = st.number_input("35x50 Pantone 1 Renk (₺)", value=float(st.session_state.params['b_3550_pantone']), key="p_b35p")
        st.session_state.params['b_3550_tiraj'] = st.number_input("35x50 Tiraj (1.000 Adet/₺)", value=float(st.session_state.params['b_3550_tiraj']), key="p_b35t")
        
        st.markdown("##### 📐 50x70 Ebadı")
        st.session_state.params['b_5070_cmyk'] = st.number_input("50x70 CMYK Hazırlık (₺)", value=float(st.session_state.params['b_5070_cmyk']), key="p_b50c")
        st.session_state.params['b_5070_pantone'] = st.number_input("50x70 Pantone 1 Renk (₺)", value=float(st.session_state.params['b_5070_pantone']), key="p_b50p")
        st.session_state.params['b_5070_tiraj'] = st.number_input("50x70 Tiraj (1.000 Adet/₺)", value=float(st.session_state.params['b_5070_tiraj']), key="p_b50t")
        
        st.markdown("##### 📐 70x100 Ebadı")
        st.session_state.params['b_70100_cmyk'] = st.number_input("70x100 CMYK Hazırlık (₺)", value=float(st.session_state.params['b_70100_cmyk']), key="p_b70c")
        st.session_state.params['b_70100_pantone'] = st.number_input("70x100 Pantone 1 Renk (₺)", value=float(st.session_state.params['b_70100_pantone']), key="p_b70p")
        st.session_state.params['b_70100_tiraj'] = st.number_input("70x100 Tiraj (1.000 Adet/₺)", value=float(st.session_state.params['b_70100_tiraj']), key="p_b70t")

        st.markdown("---")
        st.markdown("##### 🧪 Dispresiyon Lak (Baskı Grubu Altı)")
        st.session_state.params['disp_5070'] = st.number_input("50x70 Dispresiyon Lak Hazırlık (₺)", value=float(st.session_state.params['disp_5070']), key="p_d50")
        st.session_state.params['disp_5070_tiraj'] = st.number_input("50x70 Dispresiyon Lak Tiraj (1.000 Adet/₺)", value=float(st.session_state.params['disp_5070_tiraj']), key="p_d50t")
        st.session_state.params['disp_70100'] = st.number_input("70x100 Dispresiyon Lak Hazırlık (₺)", value=float(st.session_state.params['disp_70100']), key="p_d70")
        st.session_state.params['disp_70100_tiraj'] = st.number_input("70x100 Dispresiyon Lak Tiraj (1.000 Adet/₺)", value=float(st.session_state.params['disp_70100_tiraj']), key="p_d70t")

    with col2:
        st.markdown("#### 3. Yüzey İşlemleri ve Kaplama Grubu")
        
        st.markdown("##### 1. Selofan M2 Fiyatları")
        st.session_state.params['mat_sel'] = st.number_input("Mat Selofan M2 (₺)", value=float(st.session_state.params['mat_sel']), key="p_msel")
        st.session_state.params['par_sel'] = st.number_input("Parlak Selofan M2 (₺)", value=float(st.session_state.params['par_sel']), key="p_psel")
        
        st.markdown("##### 2. Lokal Lak (UV)")
        st.session_state.params['lokal_5070'] = st.number_input("Lokal Lak 50x70 Hazırlık (₺)", value=float(st.session_state.params['lokal_5070']), key="p_l50")
        st.session_state.params['lokal_5070_tiraj'] = st.number_input("Lokal Lak 50x70 Tiraj (Adet/₺)", value=float(st.session_state.params['lokal_5070_tiraj']), key="p_l50t")
        st.session_state.params['lokal_70100'] = st.number_input("Lokal Lak 70x100 Hazırlık (₺)", value=float(st.session_state.params['lokal_70100']), key="p_l70")
        st.session_state.params['lokal_70100_tiraj'] = st.number_input("Lokal Lak 70x100 Tiraj (Adet/₺)", value=float(st.session_state.params['lokal_70100_tiraj']), key="p_l70t")

        st.markdown("##### 3. Kabartma Lak (3D)")
        st.session_state.params['kab_5070'] = st.number_input("Kabartma Lak 50x70 Hazırlık (₺)", value=float(st.session_state.params['kab_5070']), key="p_k50")
        st.session_state.params['kab_5070_tiraj'] = st.number_input("Kabartma Lak 50x70 Tiraj (Adet/₺)", value=float(st.session_state.params['kab_5070_tiraj']), key="p_k50t")
        st.session_state.params['kab_70100'] = st.number_input("Kabartma Lak 70x100 Hazırlık (₺)", value=float(st.session_state.params['kab_70100']), key="p_k70")
        st.session_state.params['kab_70100_tiraj'] = st.number_input("Kabartma Lak 70x100 Tiraj (Adet/₺)", value=float(st.session_state.params['kab_70100_tiraj']), key="p_k70t")

        st.markdown("---")
        st.markdown("#### 4. Kesim ve Mücellit Grubu")
        
        st.markdown("##### 4. Kazanlı Kesim")
        st.session_state.params['kazanli'] = st.number_input("Kazanlı Kesim Hazırlık (₺)", value=float(st.session_state.params['kazanli']), key="p_kaz")
        st.session_state.params['kazanli_tiraj'] = st.number_input("Kazanlı Kesim Tiraj (Adet/₺)", value=float(st.session_state.params['kazanli_tiraj']), key="p_kazt")
        
        st.markdown("##### 5. Pedal & Bobst Otomatik Kesim")
        st.session_state.params['pedal'] = st.number_input("Pedal Kesim Hazırlık (₺)", value=float(st.session_state.params['pedal']), key="p_ped")
        st.session_state.params['pedal_tiraj'] = st.number_input("Pedal Kesim Tiraj (Adet/₺)", value=float(st.session_state.params['pedal_tiraj']), key="p_pedt")
        st.session_state.params['bobst'] = st.number_input("Bobst Otomatik Kesim Hazırlık (₺)", value=float(st.session_state.params['bobst']), key="p_bob")
        st.session_state.params['bobst_tiraj'] = st.number_input("Bobst Kesim Tiraj (Adet/₺)", value=float(st.session_state.params['bobst_tiraj']), key="p_bobt")

        st.markdown("##### 6. Otomatik Yapıştırma (Omega)")
        st.session_state.params['omega_tek'] = st.number_input("Omega Tek Kulak Yapıştırma Hazırlık (₺)", value=float(st.session_state.params['omega_tek']), key="p_omt")
        st.session_state.params['omega_tek_tiraj'] = st.number_input("Omega Tek Kulak Tiraj (Adet/₺)", value=float(st.session_state.params['omega_tek_tiraj']), key="p_omtt")
        st.session_state.params['omega_dip'] = st.number_input("Omega Dip Yapıştırma Hazırlık (₺)", value=float(st.session_state.params['omega_dip']), key="p_omd")
        st.session_state.params['omega_dip_tiraj'] = st.number_input("Omega Dip Yapıştırma Tiraj (Adet/₺)", value=float(st.session_state.params['omega_dip_tiraj']), key="p_omdt")

    parametreleri_kaydet(st.session_state.params)
    st.success("💾 Tüm parametre değişiklikleri kalıcı olarak kaydedildi.")

# ==========================================
# MENÜ 3: FORM VE HESAPLAMA MODÜLÜ
# ==========================================
elif st.session_state.page == 'calc':
    
    st.subheader("📋 Ürün Tanımlama & Maliyet Hesaplama Formu")
    st.markdown("---")

    col_r1_1, col_r1_2, col_r1_3 = st.columns(3)
    with col_r1_1:
        firma_adi = st.text_input("Firma Adı", "Erhan Ticaret")
    with col_r1_2:
        urun_adi = st.text_input("Ürün Adı", "Kutu / Ambalaj Üretimi")
    with col_r1_3:
        urun_tipleri = [
            "Föy", 
            "Tek Kırımlı Broşür", 
            "İki Kırımlı Broşür", 
            "Kartonet", 
            "Poster", 
            "Etiket", 
            "Prospektüs", 
            "Standart Kutu", 
            "Dip Kilitli Kutu", 
            "Dip Kilit Yapıştırmalı Kutu"
        ]
        urun_tipi = st.selectbox("Ürün Tipi", urun_tipleri)

    kutu_urunleri = ["Standart Kutu", "Dip Kilitli Kutu", "Dip Kilit Yapıştırmalı Kutu"]
    is_kutu = urun_tipi in kutu_urunleri

    col_r2_1, col_r2_2, col_r2_3 = st.columns(3)
    with col_r2_1:
        net_a = st.number_input("Ürün Adedi A", value=1000, step=100, key="net_a")
    with col_r2_2:
        net_b = st.number_input("Ürün Adedi B", value=2000, step=100, key="net_b")
    with col_r2_3:
        net_c = st.number_input("Ürün Adedi C", value=5000, step=100, key="net_c")

    col_ka_head, col_kb_head = st.columns(2)
    with col_ka_head:
        ca_g, ca_c = st.columns(2)
        with ca_g:
            gramaj_a = st.number_input("Gramaj A (gr/m²)", value=350, step=10, min_value=50, key="gramaj_a")
        with ca_c:
            kagit_cinsi_a = st.selectbox("Kağıt Cinsi A", ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"], key="kagit_cinsi_a")
            
    with col_kb_head:
        cb_g, cb_c = st.columns(2)
        with cb_g:
            gramaj_b = st.number_input("Gramaj B (Opsiyonel)", value=400, step=10, min_value=50, key="gramaj_b")
        with cb_c:
            kagit_cinsi_b = st.selectbox("Kağıt Cinsi B", ["Yok / Kullanma", "Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"], key="kagit_cinsi_b")

    ikinci_kagit_var = kagit_cinsi_b != "Yok / Kullanma"

    col_ebat1, col_ebat2, col_ebat3, col_baski1, col_baski2 = st.columns(5)
    with col_ebat1:
        ebat_en = st.number_input("En (mm) [A]", value=100, key="ebat_en")
    with col_ebat2:
        ebat_boy = st.number_input("Boy (mm) [B]", value=150, key="ebat_boy")
    with col_ebat3:
        if is_kutu:
            ebat_yukseklik = st.number_input("Yükseklik (mm) [C]", value=50, key="ebat_yukseklik")
        else:
            ebat_yukseklik = st.number_input("Yükseklik (mm) [C] (Kilitli)", value=0.0, disabled=True, key="ebat_yukseklik_locked")
    with col_baski1:
        cmyk_secim = st.selectbox("Baskı CMYK", ["Tek Yüz", "Ön&Arka", "CMYK Baskı yok"], key="cmyk_secim")
    with col_baski2:
        pantone_secenekleri = [
            "Yok", 
            "1 renk zemin", 
            "2 renk zemin", 
            "1 renk lokal", 
            "2 renk lokal", 
            "1 renk zemin (Ön&Arka)", 
            "2 renk zemin (Ön&Arka)", 
            "1 renk lokal (Ön&Arka)", 
            "2 renk lokal (Ön&Arka)"
        ]
        pantone_secimi = st.selectbox("Baskı Pantone renk sayısı", pantone_secenekleri, key="pantone_secimi")

    c_lam, c_ob1, c_ob2, c_bs = st.columns(4)
    with c_lam:
        laminasyon_secenekleri = ["Parlak Selofan", "Mat Selofan", "Dispersiyon Lak", "Yok"]
        laminasyon = st.selectbox("Laminasyon", laminasyon_secenekleri, key="laminasyon")
    with c_ob1:
        ozel_baski_1_secenekleri = ["Yok", "Lokal Lak", "Kabartma Lak", "Gofre", "Varak Yaldız"]
        ozel_baski_1 = st.selectbox("Özel Baskılar 1", ozel_baski_1_secenekleri, key="ozel_baski_1")
    with c_ob2:
        ozel_baski_2_secenekleri = ["Yok", "Lokal Lak", "Kabartma Lak", "Gofre", "Varak Yaldız"]
        ozel_baski_2 = st.selectbox("Özel Baskılar 2", ozel_baski_2_secenekleri, key="ozel_baski_2")
    with c_bs:
        baski_sonrasi_secenekleri = ["Düz Kesim", "Özel kesim", "Kutu Kesim + Yapıştırma", "Dip Yapıştırmalı Kutu", "Pencereli Kutu Kesim+Yapıştırma"]
        baski_sonrasi = st.selectbox("Baskı Sonrasi", baski_sonrasi_secenekleri, key="baski_sonrasi")

    ozel_istekler = st.text_input("Özel İstekler", "", placeholder="Özel talepleri buraya yazınız...", key="ozel_istekler")
    st.markdown("---")

    # --- KADEMELİ FIRE HESAPLAMA FONKSİYONU ---
    def kademeli_fire_hesapla(baski_tabaka_sayisi):
        kalan = baski_tabaka_sayisi
        fire = 0.0
        
        dilim_1 = min(kalan, 1000)
        if dilim_1 > 0:
            fire += 100.0  
            kalan -= dilim_1
            
        if kalan > 0:
            dilim_2 = min(kalan, 1000)
            fire += dilim_2 * 0.05
            kalan -= dilim_2
            
        if kalan > 0:
            dilim_3 = min(kalan, 1000)
            fire += dilim_3 * 0.04
            kalan -= dilim_3
            
        if kalan > 0:
            dilim_4 = min(kalan, 1000)
            fire += dilim_4 * 0.03
            kalan -= dilim_4
            
        if kalan > 0:
            fire += kalan * 0.02
            
        return math.ceil(fire)

    # --- PLANLAMA VE HESAPLAMA MOTORU (AKILLI BÖLME VE EKONOMİK EBAT OPTİMİZASYONU) ---
    def icsel_planla_ve_hesapla(net_adet, gramaj, kagit):
        params = st.session_state.params
        
        if is_kutu:
            acinin_en = ((ebat_en * 2) + (ebat_yukseklik * 2)) + 15.0
            acinin_boy = (ebat_boy + (ebat_yukseklik * 2)) + 30.0
        else:
            acinin_en = ebat_en + 3.0
            acinin_boy = ebat_boy + 3.0

        is_karton = kagit in ["Amerikan Bristol", "Krome Karton"]
        tum_adaylar = []
        
        if is_karton:
            karton_ebatlar = [
                ("70x100 cm", "35x50 cm", 700.0, 1000.0, 350.0, 500.0, "3550", 10.0, 4),
                ("70x100 cm", "50x70 cm", 700.0, 1000.0, 500.0, 700.0, "5070", 12.0, 2),
                ("70x100 cm", "70x100 cm", 700.0, 1000.0, 700.0, 1000.0, "70100", 15.0, 1),
                ("70x100 cm", "33,3x70 cm", 700.0, 1000.0, 333.0, 700.0, "3550", 10.0, 3),
                ("70x100 cm", "35x65 cm", 700.0, 1000.0, 350.0, 650.0, "3550", 10.0, 4),
                ("70x100 cm", "35x33,3 cm", 700.0, 1000.0, 350.0, 333.0, "3550", 10.0, 6),
                ("70x100 cm", "23x50 cm", 700.0, 1000.0, 230.0, 500.0, "3550", 10.0, 6),
                ("70x100 cm", "25x45 cm", 700.0, 1000.0, 250.0, 450.0, "3550", 10.0, 6),
            ]
            
            seriler = [550, 600, 650, 700]
            boylar = [600, 650, 700, 750, 800, 850, 900, 950, 1000]
            for s in seriler:
                for b in boylar:
                    if s == 700 and b > 950: continue
                    mk = "3550" if s <= 500 and b <= 700 else ("5070" if max(s, b) <= 700 else "70100")
                    bol = 1 if max(s, b) > 700 else 2
                    karton_ebatlar.append((f"Bobin Kesim {s//10}x{b//10} cm", f"{s//10}x{b//10} cm", float(s), float(b), float(s), float(b), mk, 12.0, bol))
            
            tum_adaylar = karton_ebatlar
        else:
            kuse_hamur_ebatlar = [
                ("64x90 cm", "32x45 cm", 640.0, 900.0, 320.0, 450.0, "3550", 10.0, 4),
                ("64x90 cm", "45x64 cm", 640.0, 900.0, 450.0, 640.0, "5070", 12.0, 2),
                ("64x90 cm", "64x90 cm", 640.0, 900.0, 640.0, 900.0, "70100", 15.0, 1),
                ("70x100 cm", "35x50 cm", 700.0, 1000.0, 350.0, 500.0, "3550", 10.0, 4),
                ("70x100 cm", "50x70 cm", 700.0, 1000.0, 500.0, 700.0, "5070", 12.0, 2),
                ("70x100 cm", "70x100 cm", 700.0, 1000.0, 700.0, 1000.0, "70100", 15.0, 1),
            ]
            if gramaj <= 170:
                kuse_hamur_ebatlar.extend([
                    ("57x82 cm", "41x57 cm", 570.0, 820.0, 410.0, 570.0, "5070", 12.0, 2),
                    ("57x82 cm", "57x82 cm", 570.0, 820.0, 570.0, 820.0, "70100", 15.0, 1),
                ])
            tum_adaylar = kuse_hamur_ebatlar

        en_iyi_secim = None
        min_maliyet = float('inf')

        for ana_tabaka, baski_ebat_adi, ana_w, ana_h, tw, th, makine_kodu, makas, bolunme_orani in tum_adaylar:
            avail_w = tw - makas
            avail_h = th
            
            if is_kutu:
                montaj = 1
                for sira_w in [1, 2, 3, 4]:
                    for sira_h in [1, 2, 3, 4]:
                        m_deneme = sira_w * sira_h
                        if m_deneme <= 0: continue
                        
                        yerlesim_en = acinin_en * sira_w
                        yerlesim_boy = ((ebat_boy + ebat_yukseklik + 15.0) * sira_h) + ((ebat_yukseklik + 15.0) * 2)
                        
                        if (yerlesim_en <= avail_w and yerlesim_boy <= avail_h) or (yerlesim_en <= avail_h and yerlesim_boy <= avail_w):
                            if m_deneme > montaj:
                                montaj = m_deneme
            else:
                s1_x = int(avail_w // acinin_en)
                s1_y = int(avail_h // acinin_boy)
                adet_1 = s1_x * s1_y

                s2_x = int(avail_w // acinin_boy)
                s2_y = int(avail_h // acinin_en)
                adet_2 = s2_x * s2_y
                montaj = max(adet_1, adet_2)

            if montaj <= 0: continue

            net_baski_tabaka = math.ceil(net_adet / montaj)
            fire_tabaka = kademeli_fire_hesapla(net_baski_tabaka)
            brut_baski_tabaka = net_baski_tabaka + fire_tabaka
            if brut_baski_tabaka < 100: brut_baski_tabaka = 100

            tabaka_adeti = math.ceil(brut_baski_tabaka / bolunme_orani)
            if tabaka_adeti < 50: tabaka_adeti = 50

            baskiya_giren_tabaka_adeti = tabaka_adeti * bolunme_orani

            tab_en = ana_w / 1000.0
            tab_boy = ana_h / 1000.0
            toplam_m2 = round(tabaka_adeti * tab_en * tab_boy, 2)
            kg_kagit = round((toplam_m2 * gramaj) / 1000.0, 2)

            # Kağıt alanı / boşa giden alanı minimize eden verimlilik cezası (Akıllı Bölme Optimizasyonu)
            kagit_alan_m2 = (ana_w / 100.0) * (ana_h / 100.0)
            urun_kapladigi_alan = montaj * ((acinin_en / 100.0) * (acinin_boy / 100.0))
            bosluk_orani = max(0.0, 1.0 - (urun_kapladigi_alan / max(0.001, kagit_alan_m2 * bolunme_orani)))

            if kagit == "Amerikan Bristol": ton_fiyat = params['bristol'] * canli_usd
            elif kagit == "Krome Karton": ton_fiyat = params['krome']
            elif kagit == "Kuşe Kağıt": ton_fiyat = params['kuse'] * canli_eur
            elif kagit == "1. Hamur Kağıt": ton_fiyat = params['hamur'] * canli_usd
            else: ton_fiyat = params['bristol'] * canli_usd

            kagit_maliyeti = (kg_kagit / 1000.0) * ton_fiyat
            b_cmyk = params.get(f"b_{makine_kodu}_cmyk", 3500.0)
            b_tiraj = params.get(f"b_{makine_kodu}_tiraj", 800.0)
            fazla_vurus = max(0, baskiya_giren_tabaka_adeti - 2000)
            baski_maliyeti = b_cmyk + (fazla_vurus / 1000.0) * b_tiraj
            
            # Verimlilik cezası ile bobin kesimlerde en dar ve ekonomik ebadın seçilmesi sağlanır
            toplam_maliyet = kagit_maliyeti + baski_maliyeti + 400.0 + (bosluk_orani * 500.0)

            brut_adet = baskiya_giren_tabaka_adeti * montaj
            fire_pct_ortalama = round((fire_tabaka / max(1, net_baski_tabaka)) * 100.0, 1)

            if toplam_maliyet < min_maliyet:
                min_maliyet = toplam_maliyet
                en_iyi_secim = {
                    "brut_adet": brut_adet,
                    "fire_pct": fire_pct_ortalama,
                    "fire_tabaka": fire_tabaka,
                    "montaj_adedi": montaj,
                    "tabaka_adeti": tabaka_adeti,
                    "baskiya_giren_tabaka": baskiya_giren_tabaka_adeti,
                    "ana_ebat": ana_tabaka,
                    "baski_ebat_str": baski_ebat_adi,
                    "toplam_m2": toplam_m2,
                    "kg_kagit": kg_kagit,
                    "kagit_maliyeti": kagit_maliyeti,
                    "baski_maliyeti": baski_maliyeti,
                    "toplam_uretim_maliyeti": toplam_maliyet,
                    "makine_kodu": makine_kodu
                }

        if en_iyi_secim is None:
            en_iyi_secim = {
                "brut_adet": net_adet, "fire_pct": 5.0, "fire_tabaka": 100, "montaj_adedi": 1, "tabaka_adeti": net_adet,
                "baskiya_giren_tabaka": net_adet, "ana_ebat": "70x100 cm", "baski_ebat_str": "35x50 cm",
                "toplam_m2": 100.0, "kg_kagit": 50.0, "kagit_maliyeti": 1000.0, "baski_maliyeti": 1000.0,
                "toplam_uretim_maliyeti": 2500.0, "makine_kodu": "3550"
            }

        return en_iyi_secim

    plan_params = []
    
    res_a = icsel_planla_ve_hesapla(net_a, gramaj_a, kagit_cinsi_a)
    res_b = icsel_planla_ve_hesapla(net_b, gramaj_a, kagit_cinsi_a)
    res_c = icsel_planla_ve_hesapla(net_c, gramaj_a, kagit_cinsi_a)

    plan_params.append({'adet': net_a, 'gramaj': gramaj_a, 'kagit': kagit_cinsi_a, 'res': res_a, 'kod': 'A'})
    plan_params.append({'adet': net_b, 'gramaj': gramaj_a, 'kagit': kagit_cinsi_a, 'res': res_b, 'kod': 'B'})
    plan_params.append({'adet': net_c, 'gramaj': gramaj_a, 'kagit': kagit_cinsi_a, 'res': res_c, 'kod': 'C'})

    if ikinci_kagit_var:
        res_a2 = icsel_planla_ve_hesapla(net_a, gramaj_b, kagit_cinsi_b)
        res_b2 = icsel_planla_ve_hesapla(net_b, gramaj_b, kagit_cinsi_b)
        res_c2 = icsel_planla_ve_hesapla(net_c, gramaj_b, kagit_cinsi_b)

        plan_params.append({'adet': net_a, 'gramaj': gramaj_b, 'kagit': kagit_cinsi_b, 'res': res_a2, 'kod': 'A2'})
        plan_params.append({'adet': net_b, 'gramaj': gramaj_b, 'kagit': kagit_cinsi_b, 'res': res_b2, 'kod': 'B2'})
        plan_params.append({'adet': net_c, 'gramaj': gramaj_b, 'kagit': kagit_cinsi_b, 'res': res_c2, 'kod': 'C2'})

    kar_orani = st.slider("Hedef Kar Marjı (%)", 0, 100, 30)

    teklif_alternatifleri = []
    for p in plan_params:
        teklif_alternatifleri.append(p)

    ozel_baski_ozet = ", ".join([ob for ob in [ozel_baski_1, ozel_baski_2] if ob != "Yok"]) or "Yok"
    st.session_state.teklif_data = {
        "firma_adi": firma_adi,
        "urun_adi": urun_adi,
        "urun_tipi": urun_tipi,
        "ebat_en": ebat_en,
        "ebat_boy": ebat_boy,
        "ebat_yukseklik": ebat_yukseklik,
        "cmyk_secim": cmyk_secim,
        "pantone_secimi": pantone_secimi,
        "laminasyon": laminasyon,
        "baski_sonrasi": baski_sonrasi,
        "ozel_baski": ozel_baski_ozet,
        "ozel_istekler": ozel_istekler,
        "kar_orani": kar_orani,
        "alternatifler": teklif_alternatifleri
    }

    st.markdown("### 📊 ÜRETİM VE PLANLAMA ÖZETİ (KUTU AÇINIM VE ALTERNATİF OPTİMİZASYON)")

    def plan_kartini_yazdir(p):
        r = p['res']
        net_kullanici_adeti = p['adet']
        secilen_kagit = p['kagit']
        montaj_adedi = r['montaj_adedi']
        
        st.markdown(f"**Kağıt & Adet:** {net_kullanici_adeti:,} adet - {p['gramaj']}g {secilen_kagit}")
        
        cmyk_on_arka = (cmyk_secim == "Ön&Arka")
        pantone_on_arka = "(Ön&Arka)" in pantone_secimi
        cmyk_yok = (cmyk_secim == "CMYK Baskı yok")
        pantone_yok = (pantone_secimi == "Yok")

        kagit_revolta_uygun = secilen_kagit in ["Kuşe Kağıt", "1. Hamur Kağıt"]

        if cmyk_yok and pantone_yok:
            baski_metodu_str = "Baskı Yok"
        elif (cmyk_on_arka or pantone_on_arka) and (montaj_adedi % 2 == 0) and kagit_revolta_uygun:
            baski_metodu_str = "Revolta"
        elif cmyk_on_arka or pantone_on_arka:
            baski_metodu_str = "Ön&Arka"
        else:
            baski_metodu_str = "Tek Yüz"

        ham_tabaka = r['baskiya_giren_tabaka']
        final_baski_tabaka = ham_tabaka
        
        if baski_metodu_str == "Revolta":
            baski_ifadesi_adet = ham_tabaka * 2  
            gecis_sayisi = 1
        elif baski_metodu_str == "Ön&Arka":
            baski_ifadesi_adet = ham_tabaka
            gecis_sayisi = 2
        else:
            baski_ifadesi_adet = ham_tabaka
            gecis_sayisi = 1

        tabaka_fmt = f"{r['tabaka_adeti']:,}".replace(',', '.')
        baski_tabaka_fmt = f"{final_baski_tabaka:,}".replace(',', '.')
        baski_ifadesi_fmt = f"{baski_ifadesi_adet:,}".replace(',', '.')
        
        baski_adedi_gecis_str = f"{baski_ifadesi_fmt} tabaka x {gecis_sayisi} geçiş"

        p_adet = 0
        if not pantone_yok:
            try:
                p_adet = int(pantone_secimi.split()[0])
            except Exception:
                p_adet = 1

        cmyk_aktif = not cmyk_yok
        pantone_aktif = not pantone_yok

        if not cmyk_aktif: cmyk_kalip = 0
        elif cmyk_secim == "Ön&Arka" and baski_metodu_str != "Revolta": cmyk_kalip = 8
        else: cmyk_kalip = 4

        if not pantone_aktif: pantone_kalip = 0
        elif pantone_on_arka and baski_metodu_str != "Revolta": pantone_kalip = p_adet * 2
        else: pantone_kalip = p_adet

        if cmyk_aktif and not pantone_aktif: kalip_metni = f"{cmyk_kalip} Kalıp"
        elif not cmyk_aktif and pantone_aktif: kalip_metni = f"{pantone_kalip} Kalıp"
        elif cmyk_aktif and pantone_aktif: kalip_metni = f"{cmyk_kalip}+{pantone_kalip} Kalıp"
        else: kalip_metni = "0 Kalıp"

        baski_ebat_detay = f"{kalip_metni} {r['baski_ebat_str']}" if baski_metodu_str != "Baskı Yok" else f"0 Kalıp {r['baski_ebat_str']}"

        plan_df = pd.DataFrame([
            {"Parametre / Kriter": "Fire Tabaka / Oranı", "Değer": f"{r['fire_tabaka']} Tabaka (Ort. %{r['fire_pct']})"},
            {"Parametre / Kriter": "Brüt Ürün Adedi", "Değer": f"{r['brut_adet']:,} adet"},
            {"Parametre / Kriter": "Montaj Planı", "Değer": f"1 Tabakada {r['montaj_adedi']} Ürün ({urun_tipi})"},
            {"Parametre / Kriter": "Ana Tabaka Ebadı ve Sayısı", "Değer": f"{r['ana_ebat']} {tabaka_fmt} Tabaka"},
            {"Parametre / Kriter": "Baskı Ebadı ve Sayısı", "Değer": baski_ebat_detay},
            {"Parametre / Kriter": "Baskıya Girecek Kağıt Ebadı ve Sayısı", "Değer": f"{r['baski_ebat_str']} {baski_tabaka_fmt} Tabaka"},
            {"Parametre / Kriter": "Kağıt Kilogram (kg)", "Değer": f"{r['kg_kagit']} kg"},
            {"Parametre / Kriter": "Baskı Adedi ve Geçiş Sayısı", "Değer": baski_adedi_gecis_str},
            {"Parametre / Kriter": "Baskı Metodu", "Değer": baski_metodu_str},
            {"Parametre / Kriter": "Kaç M2", "Değer": f"{r['toplam_m2']:,.2f} m²"}
        ])
        
        st.table(plan_df)

    if ikinci_kagit_var:
        st.markdown("#### 🔹 Kağıt A Alternatifleri")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1: 
            st.markdown("##### Alternatif A")
            plan_kartini_yazdir(teklif_alternatifleri[0])
        with col_p2: 
            st.markdown("##### Alternatif B")
            plan_kartini_yazdir(teklif_alternatifleri[1])
        with col_p3: 
            st.markdown("##### Alternatif C")
            plan_kartini_yazdir(teklif_alternatifleri[2])

        st.markdown("#### 🔹 Kağıt B Alternatifleri")
        col_p4, col_p5, col_p6 = st.columns(3)
        with col_p4: 
            st.markdown("##### Alternatif A2")
            plan_kartini_yazdir(teklif_alternatifleri[3])
        with col_p5: 
            st.markdown("##### Alternatif B2")
            plan_kartini_yazdir(teklif_alternatifleri[4])
        with col_p6: 
            st.markdown("##### Alternatif C2")
            plan_kartini_yazdir(teklif_alternatifleri[5])
    else:
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1: 
            st.markdown("##### Alternatif A")
            plan_kartini_yazdir(teklif_alternatifleri[0])
        with col_p2: 
            st.markdown("##### Alternatif B")
            plan_kartini_yazdir(teklif_alternatifleri[1])
        with col_p3: 
            st.markdown("##### Alternatif C")
            plan_kartini_yazdir(teklif_alternatifleri[2])

    st.markdown("---")
    if st.button("📄 Müşteri İçin Hazır Fiyat Teklif Sayfasına Git", use_container_width=True, key="calc_to_teklif"):
        go_page('teklif')
        st.rerun()

# ==========================================
# MENÜ 4: MÜŞTERİ FİYAT TEKLİF SAYFASI
# ==========================================
elif st.session_state.page == 'teklif':
    st.subheader("📄 Müşteri Fiyat Teklifi ve Ürün Şartnamesi")
    
    if st.session_state.teklif_data is None:
        st.warning("⚠️ Henüz bir hesaplama yapılmadı. Lütfen önce 'Fiyat Çıkart' modülünden ürün hesaplamasını gerçekleştirin.")
        if st.button("Forma Dön", key="teklif_to_calc"):
            go_page('calc')
            st.rerun()
    else:
        td = st.session_state.teklif_data
        kar_orani = td['kar_orani']

        st.markdown(
            "<div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1F4E78;'>"
            "<h3 style='margin: 0; color: #1F4E78;'>OFFICIAL PRICE QUOTATION / FİYAT TEKLİF MEKTUBU</h3>"
            f"<p style='margin: 5px 0 0 0;'><strong>Sayın:</strong> {td['firma_adi']}</p>"
            "<p style='margin: 2px 0 0 0;'><strong>Tarih:</strong> 05 Kasım 2026 | <strong>Teklif No:</strong> OFF-2026-8493</p>"
            "</div>", 
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 1. Ürün & İmalat Teknik Özellikleri")
        
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.write(f"**Ürün Adı:** {td['urun_adi']}")
            st.write(f"**Ürün Tipi:** {td['urun_tipi']}")
            st.write(f"**Ebat:** {td['ebat_en']}x{td['ebat_boy']}x{td['ebat_yukseklik']} mm")
        with col_t2:
            st.write(f"**Baskı CMYK:** {td['cmyk_secim']}")
            st.write(f"**Pantone Renk:** {td['pantone_secimi']}")
            st.write(f"**Yüzey Kaplama:** {td['laminasyon']}")
        with col_t3:
            st.write(f"**Özel İşlem:** {td['ozel_baski']}")
            st.write(f"**Kesim/Mücellit:** {td['baski_sonrasi']}")

        st.markdown("---")
        st.markdown("#### 2. Adet Alternatiflerine Göre Fiyat Tablosu")

        table_rows = []
        for alt in td['alternatifler']:
            res = alt['res']
            net_adet = alt['adet']
            net_maliyet = res['toplam_uretim_maliyeti']
            kar_tutari = net_maliyet * (kar_orani / 100.0)
            toplam_satis_tl = net_maliyet + kar_tutari
            birim_satis_tl = toplam_satis_tl / net_adet if net_adet > 0 else 0

            table_rows.append({
                "Alternatif": f"Option {alt['kod']}",
                "Net Adet": f"{net_adet:,} adet",
                "Kağıt Özelliği": f"{alt['gramaj']} gr {alt['kagit']}",
                "Ana Tabaka": res['ana_ebat'],
                "Kağıt Ağırlığı": f"{res['kg_kagit']} kg",
                "Birim Satış Fiyatı (TL)": f"₺{birim_satis_tl:,.4f}",
                "Karlı Toplam Tutar (TL)": f"₺{toplam_satis_tl:,.2f}"
            })

        df_teklif = pd.DataFrame(table_rows)
        st.dataframe(df_teklif, use_container_width=True, hide_index=True)
