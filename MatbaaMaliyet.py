import streamlit as st
import xml.etree.ElementTree as ET
import urllib.request
import math
import pandas as pd

st.set_page_config(page_title="Matbaa ve Ambalaj Maliyet & Teklif Sistemi", layout="wide")

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

# --- 2. OTURUM DURUMU VE EXCEL PARAMETRELERİ ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'teklif_data' not in st.session_state:
    st.session_state.teklif_data = None

default_params = {
    'bristol': 825.0, 'krome': 40000.0, 'kuse': 850.0, 'hamur': 1200.0,
    'b_3550_cmyk': 1800.0, 'b_3550_pantone': 900.0, 'b_3550_tiraj': 400.0,
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

if 'params' not in st.session_state:
    st.session_state.params = default_params
else:
    for k, v in default_params.items():
        if k not in st.session_state.params:
            st.session_state.params[k] = v

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
# MENÜ 2: PARAMETRELER SAYFASI
# ==========================================
elif st.session_state.page == 'params':
    st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi (Excel 37 Parametre Tam Listesi)")
    st.caption("Parametre yönetimi: Sol tarafta Kağıt, Baskı ve Dispersiyon Lak; Sağ tarafta diğer yüzey ve kesim işlemleri yer almaktadır.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 1. Kağıt ve Karton Grubu (Ton Maliyetleri)")
        st.session_state.params['bristol'] = st.number_input("Amerikan Bristol Ton ($ USD)", value=st.session_state.params['bristol'], key="p_bris")
        st.session_state.params['krome'] = st.number_input("Krome Karton Ton (TL)", value=st.session_state.params['krome'], key="p_krom")
        st.session_state.params['kuse'] = st.number_input("Kuşe Ton (€ EUR)", value=st.session_state.params['kuse'], key="p_kus")
        st.session_state.params['hamur'] = st.number_input("1. Hamur Ton ($ USD)", value=st.session_state.params['hamur'], key="p_ham")
        
        st.markdown("---")
        st.markdown("#### 2. Baskı Grubu (9 Parametre)")
        st.markdown("##### 📐 35x50 Ebadı")
        st.session_state.params['b_3550_cmyk'] = st.number_input("35x50 CMYK Hazırlık (₺)", value=st.session_state.params['b_3550_cmyk'], key="p_b35c")
        st.session_state.params['b_3550_pantone'] = st.number_input("35x50 Pantone 1 Renk (₺)", value=st.session_state.params['b_3550_pantone'], key="p_b35p")
        st.session_state.params['b_3550_tiraj'] = st.number_input("35x50 Tiraj (1.000 Adet/₺)", value=st.session_state.params['b_3550_tiraj'], key="p_b35t")
        
        st.markdown("##### 📐 50x70 Ebadı")
        st.session_state.params['b_5070_cmyk'] = st.number_input("50x70 CMYK Hazırlık (₺)", value=st.session_state.params['b_5070_cmyk'], key="p_b50c")
        st.session_state.params['b_5070_pantone'] = st.number_input("50x70 Pantone 1 Renk (₺)", value=st.session_state.params['b_5070_pantone'], key="p_b50p")
        st.session_state.params['b_5070_tiraj'] = st.number_input("50x70 Tiraj (1.000 Adet/₺)", value=st.session_state.params['b_5070_tiraj'], key="p_b50t")
        
        st.markdown("##### 📐 70x100 Ebadı")
        st.session_state.params['b_70100_cmyk'] = st.number_input("70x100 CMYK Hazırlık (₺)", value=st.session_state.params['b_70100_cmyk'], key="p_b70c")
        st.session_state.params['b_70100_pantone'] = st.number_input("70x100 Pantone 1 Renk (₺)", value=st.session_state.params['b_70100_pantone'], key="p_b70p")
        st.session_state.params['b_70100_tiraj'] = st.number_input("70x100 Tiraj (1.000 Adet/₺)", value=st.session_state.params['b_70100_tiraj'], key="p_b70t")

        st.markdown("---")
        st.markdown("##### 🧪 Dispresiyon Lak (Baskı Grubu Altı)")
        st.session_state.params['disp_5070'] = st.number_input("50x70 Dispresiyon Lak Hazırlık (₺)", value=st.session_state.params['disp_5070'], key="p_d50")
        st.session_state.params['disp_5070_tiraj'] = st.number_input("50x70 Dispresiyon Lak Tiraj (1.000 Adet/₺)", value=st.session_state.params['disp_5070_tiraj'], key="p_d50t")
        st.session_state.params['disp_70100'] = st.number_input("70x100 Dispresiyon Lak Hazırlık (₺)", value=st.session_state.params['disp_70100'], key="p_d70")
        st.session_state.params['disp_70100_tiraj'] = st.number_input("70x100 Dispresiyon Lak Tiraj (1.000 Adet/₺)", value=st.session_state.params['disp_70100_tiraj'], key="p_d70t")

    with col2:
        st.markdown("#### 3. Yüzey İşlemleri ve Kaplama Grubu")
        
        st.markdown("##### 1. Selofan M2 Fiyatları")
        st.session_state.params['mat_sel'] = st.number_input("Mat Selofan M2 (₺)", value=st.session_state.params['mat_sel'], key="p_msel")
        st.session_state.params['par_sel'] = st.number_input("Parlak Selofan M2 (₺)", value=st.session_state.params['par_sel'], key="p_psel")
        
        st.markdown("##### 2. Lokal Lak (UV)")
        st.session_state.params['lokal_5070'] = st.number_input("Lokal Lak 50x70 Hazırlık (₺)", value=st.session_state.params['lokal_5070'], key="p_l50")
        st.session_state.params['lokal_5070_tiraj'] = st.number_input("Lokal Lak 50x70 Tiraj (Adet/₺)", value=st.session_state.params['lokal_5070_tiraj'], key="p_l50t")
        st.session_state.params['lokal_70100'] = st.number_input("Lokal Lak 70x100 Hazırlık (₺)", value=st.session_state.params['lokal_70100'], key="p_l70")
        st.session_state.params['lokal_70100_tiraj'] = st.number_input("Lokal Lak 70x100 Tiraj (Adet/₺)", value=st.session_state.params['lokal_70100_tiraj'], key="p_l70t")

        st.markdown("##### 3. Kabartma Lak (3D)")
        st.session_state.params['kab_5070'] = st.number_input("Kabartma Lak 50x70 Hazırlık (₺)", value=st.session_state.params['kab_5070'], key="p_k50")
        st.session_state.params['kab_5070_tiraj'] = st.number_input("Kabartma Lak 50x70 Tiraj (Adet/₺)", value=st.session_state.params['kab_5070_tiraj'], key="p_k50t")
        st.session_state.params['kab_70100'] = st.number_input("Kabartma Lak 70x100 Hazırlık (₺)", value=st.session_state.params['kab_70100'], key="p_k70")
        st.session_state.params['kab_70100_tiraj'] = st.number_input("Kabartma Lak 70x100 Tiraj (Adet/₺)", value=st.session_state.params['kab_70100_tiraj'], key="p_k70t")

        st.markdown("---")
        st.markdown("#### 4. Kesim ve Mücellit Grubu")
        
        st.markdown("##### 4. Kazanlı Kesim")
        st.session_state.params['kazanli'] = st.number_input("Kazanlı Kesim Hazırlık (₺)", value=st.session_state.params['kazanli'], key="p_kaz")
        st.session_state.params['kazanli_tiraj'] = st.number_input("Kazanlı Kesim Tiraj (Adet/₺)", value=st.session_state.params['kazanli_tiraj'], key="p_kazt")
        
        st.markdown("##### 5. Pedal & Bobst Otomatik Kesim")
        st.session_state.params['pedal'] = st.number_input("Pedal Kesim Hazırlık (₺)", value=st.session_state.params['pedal'], key="p_ped")
        st.session_state.params['pedal_tiraj'] = st.number_input("Pedal Kesim Tiraj (Adet/₺)", value=st.session_state.params['pedal_tiraj'], key="p_pedt")
        st.session_state.params['bobst'] = st.number_input("Bobst Otomatik Kesim Hazırlık (₺)", value=st.session_state.params['bobst'], key="p_bob")
        st.session_state.params['bobst_tiraj'] = st.number_input("Bobst Kesim Tiraj (Adet/₺)", value=st.session_state.params['bobst_tiraj'], key="p_bobt")

        st.markdown("##### 6. Otomatik Yapıştırma (Omega)")
        st.session_state.params['omega_tek'] = st.number_input("Omega Tek Kulak Yapıştırma Hazırlık (₺)", value=st.session_state.params['omega_tek'], key="p_omt")
        st.session_state.params['omega_tek_tiraj'] = st.number_input("Omega Tek Kulak Tiraj (Adet/₺)", value=st.session_state.params['omega_tek_tiraj'], key="p_omtt")
        st.session_state.params['omega_dip'] = st.number_input("Omega Dip Yapıştırma Hazırlık (₺)", value=st.session_state.params['omega_dip'], key="p_omd")
        st.session_state.params['omega_dip_tiraj'] = st.number_input("Omega Dip Yapıştırma Tiraj (Adet/₺)", value=st.session_state.params['omega_dip_tiraj'], key="p_omdt")

# ==========================================
# MENÜ 3: FORM VE HESAPLAMA MODÜLÜ
# ==========================================
elif st.session_state.page == 'calc':
    def hesapla_maliyet_detayli(
        net_adet, gramaj, kagit_cinsi, baski_yuzu, pantone_sayisi, 
        laminasyon, ozel_baski_1, ozel_baski_2, baski_sonrasi, basilacak_ebat, 
        fire_orani_override, ebat_en, ebat_boy, ebat_yukseklik
    ):
        params = st.session_state.params
        
        if fire_orani_override > 0:
            fire_pct = fire_orani_override
        else:
            if net_adet <= 1500:
                fire_pct = 10.0
            elif net_adet <= 3000:
                fire_pct = 7.0
            else:
                fire_pct = 5.0

        brut_adet = int(math.ceil(net_adet * (1 + (fire_pct / 100.0))))
        
        if "70x100" in basilacak_ebat:
            tab_en, tab_boy = 0.70, 1.00
            ebat_kodu = "70100"
        elif "50x70" in basilacak_ebat:
            tab_en, tab_boy = 0.50, 0.70
            ebat_kodu = "5070"
        elif "35x50" in basilacak_ebat:
            tab_en, tab_boy = 0.35, 0.50
            ebat_kodu = "3550"
        elif "57x82" in basilacak_ebat:
            tab_en, tab_boy = 0.57, 0.82
            ebat_kodu = "5070"
        elif "64x90" in basilacak_ebat:
            tab_en, tab_boy = 0.64, 0.90
            ebat_kodu = "70100"
        else:
            tab_en, tab_boy = 0.70, 1.00
            ebat_kodu = "70100"

        en_m = ebat_en / 1000.0
        boy_m = ebat_boy / 1000.0
        fit_h = math.floor((tab_en - 0.02) / (en_m + 0.005)) * math.floor((tab_boy - 0.02) / (boy_m + 0.005))
        fit_v = math.floor((tab_en - 0.02) / (boy_m + 0.005)) * math.floor((tab_boy - 0.02) / (en_m + 0.005))
        montaj_adedi = max(1, max(fit_h, fit_v))

        tabaka_adeti = math.ceil(brut_adet / montaj_adedi)
        if tabaka_adeti < 100:
            tabaka_adeti = 100

        toplam_m2 = round(tabaka_adeti * tab_en * tab_boy, 2)
        kg_kagit = round((toplam_m2 * gramaj) / 1000.0, 2)

        if kagit_cinsi == "Amerikan Bristol":
            ton_fiyat_tl = params['bristol'] * canli_usd
        elif kagit_cinsi == "Krome Karton":
            ton_fiyat_tl = params['krome']
        elif kagit_cinsi == "Kuşe Kağıt":
            ton_fiyat_tl = params['kuse'] * canli_eur
        elif kagit_cinsi == "1. Hamur Kağıt":
            ton_fiyat_tl = params['hamur'] * canli_usd
        else:
            ton_fiyat_tl = params['bristol'] * canli_usd

        kagit_maliyeti = (kg_kagit / 1000.0) * ton_fiyat_tl

        revolta_uygun = kagit_cinsi in ["Kuşe Kağıt", "1. Hamur Kağıt"]
        
        b_cmyk_base = params.get(f"b_{ebat_kodu}_cmyk", 3500.0)
        b_pantone_base = params.get(f"b_{ebat_kodu}_pantone", 1750.0)
        b_tiraj_rate = params.get(f"b_{ebat_kodu}_tiraj", 800.0)

        baski_vurus = tabaka_adeti
        if baski_yuzu in ["Çift Yüz", "Ön ve Arka Baskı"]:
            if revolta_uygun:
                baski_vurus = tabaka_adeti * 2
                baski_maliyeti = b_cmyk_base + max(0, (baski_vurus - 2000) / 1000.0) * b_tiraj_rate
            else:
                baski_maliyeti = (b_cmyk_base + max(0, (baski_vurus - 2000) / 1000.0) * b_tiraj_rate) * 1.8
        elif baski_yuzu == "Revolta Baskı":
            baski_vurus = tabaka_adeti * 2
            baski_maliyeti = b_cmyk_base + max(0, (baski_vurus - 2000) / 1000.0) * b_tiraj_rate
        elif baski_yuzu in ["Tek Yüz", "Tek Yüz Baskı"]:
            baski_maliyeti = b_cmyk_base + max(0, (baski_vurus - 2000) / 1000.0) * b_tiraj_rate
        else:
            baski_maliyeti = 0.0

        if pantone_sayisi != "Yok":
            renk_katsayi = 1
            if "2" in pantone_sayisi: renk_katsayi = 2
            elif "3" in pantone_sayisi: renk_katsayi = 3
            elif "4" in pantone_sayisi: renk_katsayi = 4
            baski_maliyeti += b_pantone_base * renk_katsayi

        selofan_maliyeti = 0.0
        if laminasyon == "Mat Selofan":
            selofan_maliyeti = toplam_m2 * params['mat_sel']
        elif laminasyon == "Parlak Selofan":
            selofan_maliyeti = toplam_m2 * params['par_sel']
        elif laminasyon in ["Dispersiyon Lak", "Dispresiyon Lak"]:
            disp_base = params['disp_5070'] if ebat_kodu != "70100" else params['disp_70100']
            disp_tiraj = params['disp_5070_tiraj'] if ebat_kodu != "70100" else params['disp_70100_tiraj']
            disp_limit = 1000 if ebat_kodu != "70100" else 2000
            selofan_maliyeti = disp_base + max(0, (tabaka_adeti - disp_limit) / 1000.0) * disp_tiraj

        ozel_baski_maliyeti = 0.0
        for ob in [ozel_baski_1, ozel_baski_2]:
            if ob != "Yok":
                if "Lokal Lak" in ob:
                    l_base = params['lokal_5070'] if ebat_kodu != "70100" else params['lokal_70100']
                    l_rate = params['lokal_5070_tiraj'] if ebat_kodu != "70100" else params['lokal_70100_tiraj']
                    ozel_baski_maliyeti += l_base + max(0, tabaka_adeti - 1000) * l_rate
                elif "Kabartma Lak" in ob:
                    k_base = params['kab_5070'] if ebat_kodu != "70100" else params['kab_70100']
                    k_rate = params['kab_5070_tiraj'] if ebat_kodu != "70100" else params['kab_70100_tiraj']
                    ozel_baski_maliyeti += k_base + max(0, tabaka_adeti - 1000) * k_rate
                elif ob in ["Gofre", "Varak Yaldız"]:
                    ozel_baski_maliyeti += 2000.0 + (tabaka_adeti * 0.5)

        yuzey_lak_toplam = selofan_maliyeti + ozel_baski_maliyeti

        kesim_maliyeti = 0.0
        if baski_sonrasi == "Düz Kesim":
            kesim_maliyeti = 400.0
        elif baski_sonrasi in ["Özel kesim", "Özel Kesim"]:
            kesim_maliyeti = params['bobst'] + max(0, net_adet - 1000) * params['bobst_tiraj']
        elif baski_sonrasi == "Yan Yapıştırmalı Kutu":
            kesim_maliyeti = (params['kazanli'] + max(0, net_adet - 1000) * params['kazanli_tiraj']) + (params['omega_tek'] + max(0, net_adet - 10000) * params['omega_tek_tiraj'])
        elif baski_sonrasi in ["Dip Yapıştırmalı Kutu", "Kutu Kesim + Yapıştırma"]:
            kesim_maliyeti = (params['kazanli'] + max(0, net_adet - 1000) * params['kazanli_tiraj']) + (params['omega_dip'] + max(0, net_adet - 10000) * params['omega_dip_tiraj'])
        elif baski_sonrasi == "Özel Kesim+Düz Kesim":
            kesim_maliyeti = (params['bobst'] + max(0, net_adet - 1000) * params['bobst_tiraj']) + 400.0
        elif baski_sonrasi == "Pencereli Kutu Kesim+Yapıştırma":
            base_k = (params['kazanli'] + max(0, net_adet - 1000) * params['kazanli_tiraj']) + (params['omega_dip'] + max(0, net_adet - 10000) * params['omega_dip_tiraj'])
            kesim_maliyeti = base_k * 1.35

        toplam_uretim_maliyeti = kagit_maliyeti + baski_maliyeti + yuzey_lak_toplam + kesim_maliyeti

        return {
            "brut_adet": brut_adet,
            "fire_pct": fire_pct,
            "montaj_adedi": montaj_adedi,
            "tabaka_adeti": tabaka_adeti,
            "toplam_m2": toplam_m2,
            "kg_kagit": kg_kagit,
            "kagit_maliyeti": kagit_maliyeti,
            "baski_maliyeti": baski_maliyeti,
            "selofan_maliyeti": selofan_maliyeti,
            "ozel_baski_maliyeti": ozel_baski_maliyeti,
            "yuzey_lak_toplam": yuzey_lak_toplam,
            "kesim_maliyeti": kesim_maliyeti,
            "toplam_uretim_maliyeti": toplam_uretim_maliyeti,
            "revolta_uygun": revolta_uygun
        }

    st.subheader("📋 Ürün Tanımlama & Maliyet Hesaplama Formu")
    st.markdown("---")

    st.markdown("### 📦 ÜRÜN TANIMLAMA")

    col_r1_1, col_r1_2, col_r1_3 = st.columns(3)
    with col_r1_1:
        firma_adi = st.text_input("Firma Adı", "Erhan Ticaret")
    with col_r1_2:
        urun_adi = st.text_input("Ürün Adı", "Lüks Ambalaj Kutusu")
    with col_r1_3:
        urun_tipleri = ["Föy", "Tek Kırımlı Broşür", "İki Kırımlı Broşür", "Kartonet", "Kutu", "Yan Yapıştırmalı Kutu", "Dip Yapıştırmalı Kutu", "Sıvamalı Kutu", "Etiket", "Prospektüs"]
        urun_tipi = st.selectbox("Ürün Tipi", urun_tipleri)

    col_r2_1, col_r2_2, col_r2_3 = st.columns(3)
    with col_r2_1:
        net_a = st.number_input("Ürün Adedi A (Axxx)", value=1000, step=500, key="net_a")
    with col_r2_2:
        net_b = st.number_input("Ürün Adedi B (Bxxx)", value=3000, step=500, key="net_b")
    with col_r2_3:
        net_c = st.number_input("Ürün Adedi C (Cxxx)", value=5000, step=500, key="net_c")

    col_ka_head, col_kb_head = st.columns(2)
    with col_ka_head:
        ca_g, ca_c = st.columns(2)
        with ca_g:
            gramaj_a = st.number_input("Gramaj A (gr/m²)", value=300, step=10, min_value=50, key="gramaj_a")
        with ca_c:
            kagit_cinsi_a = st.selectbox("Kağıt Cinsi A", ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"], key="kagit_cinsi_a")
            
    with col_kb_head:
        cb_g, cb_c = st.columns(2)
        with cb_g:
            gramaj_b = st.number_input("Gramaj B (gr/m² - 2. İhtimal Opsiyonel)", value=350, step=10, min_value=50, key="gramaj_b")
        with cb_c:
            kagit_cinsi_b = st.selectbox("Kağıt Cinsi B (2. İhtimal Opsiyonel)", ["Yok / Kullanma", "Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"], key="kagit_cinsi_b")

    ikinci_kagit_var = kagit_cinsi_b != "Yok / Kullanma"

    col_ebat1, col_ebat2, col_ebat3, col_baski1, col_baski2 = st.columns(5)
    with col_ebat1:
        ebat_en = st.number_input("En (mm)", value=200, key="ebat_en")
    with col_ebat2:
        ebat_boy = st.number_input("Boy (mm)", value=150, key="ebat_boy")
    with col_ebat3:
        ebat_yukseklik = st.number_input("Yükseklik (mm)", value=50, key="ebat_yukseklik")
    with col_baski1:
        cmyk_secim = st.selectbox("Baskı CMYK", ["Tek Yüz", "Çift Yüz", "CMYK Baskı yok"], key="cmyk_secim")
    with col_baski2:
        pantone_secenekleri = ["Yok", "1 renk zemin", "2 renk zemin", "3 renk zemin", "4 renk zemin", "1 renk lokal", "2 renk lokal", "3 renk lokal", "4 renk lokal"]
        pantone_sayisi = st.selectbox("Baskı Pantone renk sayısı", pantone_secenekleri, key="pantone_sayisi")

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
        baski_sonrasi_secenekleri = ["Düz Kesim", "Özel kesim", "Kutu Kesim + Yapıştırma", "Yan Yapıştırmalı Kutu", "Dip Yapıştırmalı Kutu", "Pencereli Kutu Kesim+Yapıştırma"]
        baski_sonrasi = st.selectbox("Baskı Sonrası", baski_sonrasi_secenekleri, key="baski_sonrasi")

    ozel_istekler = st.text_input("Özel İstekler", "", placeholder="Özel talepleri buraya yazınız...", key="ozel_istekler")

    st.markdown("---")

    st.markdown("### 🛠️ MATBAA PLANLAMA DETAYLARI (OTOMATİK HESAPLAMA)")
    
    if ikinci_kagit_var:
        st.info("💡 2. Kağıt seçimi aktif olduğu için sistem tarafından otomatik hesaplanan 3x2 blok halinde toplam 6 adet planlama alternatifi gösterilmektedir.")
    else:
        st.info("💡 Sistem tarafından otomatik hesaplanan 3 adet planlama alternatifi gösterilmektedir.")

    def otomatik_planlama_hesapla(adet, gramaj, kagit):
        if adet <= 1500:
            fire = 10.0
        elif adet <= 3000:
            fire = 7.0
        else:
            fire = 5.0
            
        if adet <= 2000:
            ebat = "50x70 cm"
        else:
            ebat = "70x100 cm"
            
        return {'adet': adet, 'gramaj': gramaj, 'kagit': kagit, 'fire': fire, 'ebat': ebat}

    plan_params = []
    
    plan_params.append({**otomatik_planlama_hesapla(net_a, gramaj_a, kagit_cinsi_a), 'kod': 'A1'})
    plan_params.append({**otomatik_planlama_hesapla(net_b, gramaj_a, kagit_cinsi_a), 'kod': 'B1'})
    plan_params.append({**otomatik_planlama_hesapla(net_c, gramaj_a, kagit_cinsi_a), 'kod': 'C1'})

    if ikinci_kagit_var:
        plan_params.append({**otomatik_planlama_hesapla(net_a, gramaj_b, kagit_cinsi_b), 'kod': 'A2'})
        plan_params.append({**otomatik_planlama_hesapla(net_b, gramaj_b, kagit_cinsi_b), 'kod': 'B2'})
        plan_params.append({**otomatik_planlama_hesapla(net_c, gramaj_b, kagit_cinsi_b), 'kod': 'C2'})

    st.markdown("---")
    kar_orani = st.slider("Hedef Kar Marjı (%)", 0, 100, 30)

    teklif_alternatifleri = []
    
    for p in plan_params:
        res = hesapla_maliyet_detayli(
            p['adet'], p['gramaj'], p['kagit'], cmyk_secim, pantone_sayisi, 
            laminasyon, ozel_baski_1, ozel_baski_2, baski_sonrasi, p['ebat'], 
            p['fire'], ebat_en, ebat_boy, ebat_yukseklik
        )
        p['res'] = res
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
        "pantone_sayisi": pantone_sayisi,
        "laminasyon": laminasyon,
        "baski_sonrasi": baski_sonrasi,
        "ozel_baski": ozel_baski_ozet,
        "ozel_istekler": ozel_istekler,
        "kar_orani": kar_orani,
        "alternatifler": teklif_alternatifleri
    }

    st.markdown("### 📊 ÜRETİM VE PLANLAMA ÖZETİ (EXCEL ŞABLONU GÖRÜNÜMÜ)")

    def plan_kartini_yazdir(p):
        r = p['res']
        net_kullanici_adeti = p['adet']
        
        st.markdown(f"**Kağıt & Adet:** {net_kullanici_adeti:,} adet - {p['gramaj']}g {p['kagit']}")
        
        plan_df = pd.DataFrame([
            {"Parametre / Kriter": "Fire Oranı (%)", "Değer": f"%{r['fire_pct']:.1f}"},
            {"Parametre / Kriter": "Brüt Adet", "Değer": f"{r['brut_adet']:,} adet"},
            {"Parametre / Kriter": "Montaj Planı", "Değer": f"1 Tabakada {r['montaj_adedi']} İmalat"},
            {"Parametre / Kriter": "Basılacak Kağıdın Ebadı", "Değer": p['ebat']},
            {"Parametre / Kriter": "Kağıt Kilogram (kg)", "Değer": f"{r['kg_kagit']} kg"},
            {"Parametre / Kriter": "Baskı Adedi Ön Ve Arka", "Değer": f"{r['tabaka_adeti']:,} tabaka"},
            {"Parametre / Kriter": "Baskı Metodu", "Değer": "Revolta" if r['revolta_uygun'] and cmyk_secim == "Çift Yüz" else "Standart Ofset"},
            {"Parametre / Kriter": "Kaç M2", "Değer": f"{r['toplam_m2']:,.2f} m²"}
        ])
        
        st.table(plan_df)

    if ikinci_kagit_var:
        st.markdown("#### 🔹 Kağıt A Alternatifleri")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1: 
            st.markdown("##### Alternatif A1")
            plan_kartini_yazdir(teklif_alternatifleri[0])
        with col_p2: 
            st.markdown("##### Alternatif B1")
            plan_kartini_yazdir(teklif_alternatifleri[1])
        with col_p3: 
            st.markdown("##### Alternatif C1")
            plan_kartini_yazdir(teklif_alternatifleri[2])

        st.markdown("---")
        st.markdown("#### 🔸 Kağıt B (2. İhtimal) Alternatifleri")
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

    st.markdown("<br>", unsafe_allow_html=True)
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
        if st.button("Forma Dön ve Hesapla", key="teklif_to_calc"):
            go_page('calc')
            st.rerun()
    else:
        td = st.session_state.teklif_data
        kar_orani = td['kar_orani']

        st.markdown("<div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1F4E78;'>"
                    "<h3 style='margin: 0; color: #1F4E78;'>OFFICIAL PRICE QUOTATION / FİYAT TEKLİF MEKTUBU</h3>"
                    f"<p style='margin: 5px 0 0 0;'><strong>Sayın:</strong> {td['firma_adi']}</p>"
                    "<p style='margin: 2px 0 0 0;'><strong>Tarih:</strong> 03 Kasım 2026 | <strong>Teklif No:</strong> OFF-2026-8492</p>"
                    "</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 1. Ürün & İmalat Teknik Özellikleri")
        
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.write(f"**Ürün Adı:** {td['urun_adi']}")
            st.write(f"**Ürün Tipi:** {td['urun_tipi']}")
            st.write(f"**Ebat:** {td['ebat_en']} mm x {td['ebat_boy']} mm x {td['ebat_yukseklik']} mm")
        with col_t2:
            st.write(f"**Baskı CMYK:** {td['cmyk_secim']}")
            st.write(f"**Pantone Renk:** {td['pantone_sayisi']}")
            st.write(f"**Yüzey Kaplama:** {td['laminasyon']}")
        with col_t3:
            st.write(f"**Özel İşlem:** {td['ozel_baski']}")
            st.write(f"**Kesim/Mücellit:** {td['baski_sonrasi']}")
            if td.get('ozel_istekler'):
                st.write(f"**Özel İstekler:** {td['ozel_istekler']}")

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
            
            toplam_satis_usd = toplam_satis_tl / canli_usd
            toplam_satis_eur = toplam_satis_tl / canli_eur
            birim_satis_usd = birim_satis_tl / canli_usd

            table_rows.append({
                "Alternatif": f"Option {alt['kod']}",
                "Net Adet": f"{net_adet:,} adet",
                "Kağıt Özelliği": f"{alt['gramaj']} gr {alt['kagit']}",
                "Tabaka Ebadı": alt['ebat'],
                "Kağıt Ağırlığı": f"{res['kg_kagit']} kg",
                "Birim Satış Fiyatı (TL)": f"₺{birim_satis_tl:,.4f}",
                "Birim Satış ($ USD)": f"${birim_satis_usd:,.4f}",
                "Karlı Toplam Tutar (TL)": f"₺{toplam_satis_tl:,.2f}",
                "Karlı Toplam ($ USD)": f"${toplam_satis_usd:,.2f}",
                "Karlı Toplam (€ EUR)": f"€{toplam_satis_eur:,.2f}"
            })

        df_teklif = pd.DataFrame(table_rows)
        st.dataframe(df_teklif, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### 3. Hazır Teklif Mektubu Metni (Kopyalanabilir)")
        
        letter_lines = [
            f"SAYIN {td['firma_adi'].upper()},",
            "",
            f"Talep etmiş olduğunuz '{td['urun_adi']}' ambalaj/matbaa işine ait teknik imalat ve fiyat teklifimiz aşağıda bilginize sunulmuştur.",
            "",
            "ÜRÜN TEKNİK ŞARTNAMESİ:",
            f"• Ürün Tipi / Adı: {td['urun_tipi']} / {td['urun_adi']}",
            f"• Ebat: {td['ebat_en']} mm x {td['ebat_boy']} mm x {td['ebat_yukseklik']} mm",
            f"• Baskı CMYK: {td['cmyk_secim']} | Pantone: {td['pantone_sayisi']}",
            f"• Yüzey Kaplama: {td['laminasyon']} | Özel İşlem: {td['ozel_baski']}",
            f"• Baskı Sonrasi: {td['baski_sonrasi']}",
        ]
        
        if td.get('ozel_istekler'):
            letter_lines.append(f"• Özel İstekler: {td['ozel_istekler']}")
            
        letter_lines.extend([
            "",
            "FİYAT VE ADET SEÇENEKLERİ:"
        ])
        
        for alt in td['alternatifler']:
            res = alt['res']
            net_adet = alt['adet']
            net_maliyet = res['toplam_uretim_maliyeti']
            kar_tutari = net_maliyet * (kar_orani / 100.0)
            toplam_satis_tl = net_maliyet + kar_tutari
            birim_satis_tl = toplam_satis_tl / net_adet if net_adet > 0 else 0
            letter_lines.append(f"- Alternatif {alt['kod']} | {net_adet:,} Adet ({alt['gramaj']} gr {alt['kagit']}): Birim Fiyat: ₺{birim_satis_tl:,.4f} + KDV | Toplam: ₺{toplam_satis_tl:,.2f} + KDV")

        letter_lines.extend([
            "",
            "GENEL ŞARTLAR:",
            "1. Teklifimiz 15 (on beş) gün süreyle geçerlidir.",
            "2. Fiyatlarımıza KDV dahil değildir.",
            "3. Teslimat süresi onaylanan grafik baskı onayı sonrası 7-10 iş günüdür.",
            "",
            "Bilgilerinize arz eder, hayırlı işler dileriz.",
            "Saygılarımızla,",
            "Matbaa & Ambalaj Üretim Yönetimi"
        ])

        letter_text = chr(10).join(letter_
