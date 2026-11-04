import streamlit as st
import xml.etree.ElementTree as ET
import urllib.request
import math
import pandas as pd
import json
import os

st.set_page_config(page_title="Matbaa ve Ambalaj Maliyet & Teklif Sistemi", layout="wide")

# --- 0. KALICI JSON PARAMETRE YÖNETİMİ ---
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

if 'page' not in st.session_state: st.session_state.page = 'home'
if 'teklif_data' not in st.session_state: st.session_state.teklif_data = None
def go_page(page_name): st.session_state.page = page_name

# --- 3. ÜST GEZİNTİ VE MENÜ ---
st.markdown("### 🖨️ MATBAAM PRO - Ambalaj & Matbaa Maliyet ve Teklif Sistemi")
st.info(f"🏦 TCMB Anlık Efektif Satış Kurları — USD: ₺{canli_usd:.2f} | EUR: ₺{canli_eur:.2f}")

nav_c1, nav_c2, nav_c3, nav_c4 = st.columns(4)
with nav_c1:
    if st.button("🏠 1. Ana Menü", use_container_width=True, type="primary" if st.session_state.page == 'home' else "secondary"): go_page('home'); st.rerun()
with nav_c2:
    if st.button("⚙️ 2. Parametreler (37 Kalem)", use_container_width=True, type="primary" if st.session_state.page == 'params' else "secondary"): go_page('params'); st.rerun()
with nav_c3:
    if st.button("📋 3. Fiyat Çıkart (Form)", use_container_width=True, type="primary" if st.session_state.page == 'calc' else "secondary"): go_page('calc'); st.rerun()
with nav_c4:
    if st.button("📄 4. Müşteri Fiyat Teklifi", use_container_width=True, type="primary" if st.session_state.page == 'teklif' else "secondary"): go_page('teklif'); st.rerun()
st.markdown("---")

# ==========================================
# MENÜ 1: ANA SAYFA
# ==========================================
if st.session_state.page == 'home':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>Yönetim & Hesaplama Modülü</h2><br>", unsafe_allow_html=True)
        if st.button("1. Parametreler (Fiyat Listesi Yönetimi - 37 Kalem)", use_container_width=True): go_page('params'); st.rerun()
        if st.button("2. Fiyat Çıkart (Maliyet Hesaplama Formu)", use_container_width=True): go_page('calc'); st.rerun()
        if st.button("3. 📄 Müşteri Fiyat Teklifi Mektubu ve Tablosu", use_container_width=True): go_page('teklif'); st.rerun()

# ==========================================
# MENÜ 2: PARAMETRELER SAYFASI (KALICI JSON)
# ==========================================
elif st.session_state.page == 'params':
    st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi")
    
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
        st.markdown("##### 🧪 Dispresiyon Lak")
        st.session_state.params['disp_5070'] = st.number_input("50x70 Dispresiyon Lak Hazırlık (₺)", value=st.session_state.params['disp_5070'], key="p_d50")
        st.session_state.params['disp_5070_tiraj'] = st.number_input("50x70 Dispresiyon Lak Tiraj (1.000 Adet/₺)", value=st.session_state.params['disp_5070_tiraj'], key="p_d50t")
        st.session_state.params['disp_70100'] = st.number_input("70x100 Dispresiyon Lak Hazırlık (₺)", value=st.session_state.params['disp_70100'], key="p_d70")
        st.session_state.params['disp_70100_tiraj'] = st.number_input("70x100 Dispresiyon Lak Tiraj (1.000 Adet/₺)", value=st.session_state.params['disp_70100_tiraj'], key="p_d70t")

    with col2:
        st.markdown("#### 3. Yüzey İşlemleri ve Kaplama Grubu")
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
        st.session_state.params['kazanli'] = st.number_input("Kazanlı Kesim Hazırlık (₺)", value=st.session_state.params['kazanli'], key="p_kaz")
        st.session_state.params['kazanli_tiraj'] = st.number_input("Kazanlı Kesim Tiraj (Adet/₺)", value=st.session_state.params['kazanli_tiraj'], key="p_kazt")
        st.session_state.params['pedal'] = st.number_input("Pedal Kesim Hazırlık (₺)", value=st.session_state.params['pedal'], key="p_ped")
        st.session_state.params['pedal_tiraj'] = st.number_input("Pedal Kesim Tiraj (Adet/₺)", value=st.session_state.params['pedal_tiraj'], key="p_pedt")
        st.session_state.params['bobst'] = st.number_input("Bobst Otomatik Kesim Hazırlık (₺)", value=st.session_state.params['bobst'], key="p_bob")
        st.session_state.params['bobst_tiraj'] = st.number_input("Bobst Kesim Tiraj (Adet/₺)", value=st.session_state.params['bobst_tiraj'], key="p_bobt")
        st.session_state.params['omega_tek'] = st.number_input("Omega Tek Kulak Yapıştırma Hazırlık (₺)", value=st.session_state.params['omega_tek'], key="p_omt")
        st.session_state.params['omega_tek_tiraj'] = st.number_input("Omega Tek Kulak Tiraj (Adet/₺)", value=st.session_state.params['omega_tek_tiraj'], key="p_omtt")
        st.session_state.params['omega_dip'] = st.number_input("Omega Dip Yapıştırma Hazırlık (₺)", value=st.session_state.params['omega_dip'], key="p_omd")
        st.session_state.params['omega_dip_tiraj'] = st.number_input("Omega Dip Yapıştırma Tiraj (Adet/₺)", value=st.session_state.params['omega_dip_tiraj'], key="p_omdt")

    parametreleri_kaydet(st.session_state.params)
    st.success("💾 Tüm parametre değişiklikleri kalıcı olarak kaydedildi.")

# ==========================================
# MENÜ 3: FORM VE HESAPLAMA MODÜLÜ
# ==========================================
elif st.session_state.page == 'calc':
    
    def fiziksel_montaj_bul(tw, th, en, boy, yukseklik, makas, kutu_formu):
        if tw > th:
            tw, th = th, tw 
        best_m = 0
        kutu_acik_en = (en * 2.0) + (yukseklik * 2.0) + 15.0
        
        for s_en in range(1, 15):
            for s_boy in range(1, 15):
                item_w = kutu_acik_en * s_en
                if kutu_formu in ["Dip Kilitli Kutu", "Dip Kilit Yapıştırmalı Kutu", "Dip Yapıştırmalı Kutu"]:
                    pair_boy = (boy * 2.0) + ((yukseklik + 15.0) * 2.0)
                    tek_boy = boy + ((yukseklik + 15.0) * 2.0)
                    item_h = ((s_boy // 2) * pair_boy) + ((s_boy % 2) * tek_boy)
                else:
                    item_h = (boy + ((yukseklik + 15.0) * 2.0)) * s_boy
                
                sigar_mi = False
                if tw > makas and (item_w <= tw - makas and item_h <= th) or (item_h <= tw - makas and item_w <= th):
                    sigar_mi = True
                if th > makas and (item_w <= th - makas and item_h <= tw) or (item_h <= th - makas and item_w <= tw):
                    sigar_mi = True

                if sigar_mi:
                    if (s_en * s_boy) > best_m:
                        best_m = s_en * s_boy
        return best_m

    def hesapla_maliyet_detayli(net_adet, gramaj, kagit_cinsi, baski_yuzu, pantone_secimi, laminasyon, ozel_baski_1, ozel_baski_2, baski_sonrasi, kagit_adi, makine_kodu, tab_en_mm, tab_boy_mm, makas_payi_mm, montaj_adedi, ebat_en, ebat_boy, ebat_yukseklik):
        params = st.session_state.params
        fire_pct = 10.0 if net_adet <= 1500 else (7.0 if net_adet <= 3000 else 5.0)
        brut_adet = int(math.ceil(net_adet * (1 + (fire_pct / 100.0))))
        tab_en, tab_boy = tab_en_mm / 1000.0, tab_boy_mm / 1000.0

        gercek_baski_yuzu = baski_yuzu
        if baski_yuzu in ["Çift Yüz", "Ön ve Arka Baskı"]:
            gercek_baski_yuzu = "Revolta Baskı" if (kagit_cinsi in ["Kuşe Kağıt", "1. Hamur Kağıt"] and montaj_adedi % 2 == 0) else "Çift Yüz (Normal)"

        tabaka_adeti = math.ceil(brut_adet / montaj_adedi) if montaj_adedi > 0 else 0
        if 0 < tabaka_adeti < 100: tabaka_adeti = 100

        gecis_sayisi, kalıp_sayisi = 1, 4 
        has_pantone = pantone_secimi != "Yok"
        if has_pantone: kalıp_sayisi = 5 if "1 renk" in pantone_secimi else 6
        if (baski_yuzu in ["Çift Yüz", "Ön ve Arka Baskı"] and kagit_cinsi in ["Amerikan Bristol", "Krome Karton"]) or (has_pantone and "Çift Yüz" not in pantone_secimi) or ("Çift Yüz" in pantone_secimi):
            gecis_sayisi = 2

        toplam_m2 = round(tabaka_adeti * tab_en * tab_boy, 2)
        kg_kagit = round((toplam_m2 * gramaj) / 1000.0, 2)

        ton_fiyat_tl = params['krome'] if kagit_cinsi == "Krome Karton" else (params['kuse'] * canli_eur if kagit_cinsi == "Kuşe Kağıt" else (params['hamur'] * canli_usd if kagit_cinsi == "1. Hamur Kağıt" else params['bristol'] * canli_usd))
        kagit_maliyeti = (kg_kagit / 1000.0) * ton_fiyat_tl

        b_cmyk_base = params.get(f"b_{makine_kodu}_cmyk", 2400.0)
        b_pantone_base = params.get(f"b_{makine_kodu}_pantone", 1200.0)
        b_tiraj_rate = params.get(f"b_{makine_kodu}_tiraj", 500.0)
        
        fazla_vurus = max(0, (tabaka_adeti * gecis_sayisi) - 2000)
        baski_maliyeti = b_cmyk_base + (fazla_vurus / 1000.0) * b_tiraj_rate
        if gercek_baski_yuzu == "Çift Yüz (Normal)": baski_maliyeti *= 1.8
        if has_pantone: baski_maliyeti += b_pantone_base * (2 if "2 renk" in pantone_secimi else 1)

        selofan_maliyeti = 0.0
        if laminasyon == "Mat Selofan": selofan_maliyeti = toplam_m2 * params['mat_sel']
        elif laminasyon == "Parlak Selofan": selofan_maliyeti = toplam_m2 * params['par_sel']
        elif "Dispersiyon" in laminasyon:
            d_base = params['disp_5070'] if makine_kodu != "70100" else params['disp_70100']
            d_rate = params['disp_5070_tiraj'] if makine_kodu != "70100" else params['disp_70100_tiraj']
            selofan_maliyeti = d_base + max(0, (tabaka_adeti - (1000 if makine_kodu != "70100" else 2000)) / 1000.0) * d_rate

        ozel_baski_maliyeti = 0.0
        for ob in [ozel_baski_1, ozel_baski_2]:
            if "Lokal Lak" in ob: ozel_baski_maliyeti += (params['lokal_5070'] if makine_kodu != "70100" else params['lokal_70100']) + max(0, tabaka_adeti - 1000) * (params['lokal_5070_tiraj'] if makine_kodu != "70100" else params['lokal_70100_tiraj'])
            elif "Kabartma Lak" in ob: ozel_baski_maliyeti
