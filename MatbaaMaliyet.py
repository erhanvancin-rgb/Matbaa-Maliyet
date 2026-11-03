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
        st.session_state.params
