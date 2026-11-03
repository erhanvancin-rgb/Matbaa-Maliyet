import streamlit as st
import xml.etree.ElementTree as ET
import urllib.request
from urun_bilgileri_ve_maliyetlendirme import render_urun_bilgileri_ve_maliyetlendirme

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
    # 1. Kağıt Grubu
    'bristol': 825.0, 'krome': 40000.0, 'kuse': 850.0, 'hamur': 1200.0,
    # 2. Baskı Grubu
    'b_3550_cmyk': 1800.0, 'b_3550_pantone': 900.0, 'b_3550_tiraj': 400.0,
    'b_5070_cmyk': 3500.0, 'b_5070_pantone': 1750.0, 'b_5070_tiraj': 800.0,
    'b_70100_cmyk': 5000.0, 'b_70100_pantone': 1750.0, 'b_70100_tiraj': 1400.0,
    # 3. Yüzey İşlemleri ve Lak
    'disp_5070': 1500.0, 'disp_5070_tiraj': 800.0,
    'disp_70100': 2000.0, 'disp_70100_tiraj': 1000.0,
    'mat_sel': 4.70, 'par_sel': 4.50,
    'lokal_5070': 1500.0, 'lokal_5070_tiraj': 1.5,
    'lokal_70100': 1800.0, 'lokal_70100_tiraj': 1.5,
    'kab_5070': 1600.0, 'kab_5070_tiraj': 1.6,
    'kab_70100': 1900.0, 'kab_70100_tiraj': 1.9,
    # 4. Kesim ve Mücellit
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

# 3. FİYAT ÇIKART (HESAPLAMA SAYFASI)
elif st.session_state.page == 'calc':
    if st.button("⬅️ Ana Menüye Dön"):
        go_home()
        st.rerun()
        
    render_urun_bilgileri_ve_maliyetlendirme(canli_usd, canli_eur)
