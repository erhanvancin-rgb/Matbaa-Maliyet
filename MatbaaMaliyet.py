import streamlit as st
import xml.etree.ElementTree as ET
import urllib.request
import math
import pandas as pd
import json
import os

st.set_page_config(page_title="Matbaa ve Ambalaj Maliyet & Teklif Sistemi", layout="wide")

--- 0. KALICI JSON PARAMETRE YÖNETİMİ ---

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
if k not in kayitli: kayitli[k] = v
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

--- 1. TCMB ANLIK EFEKTİF SATIŞ KURLARINI ÇEKME ---

@st.cache_data(ttl=3600)
def tcmb_kurlarini_getir():
usd_kur, eur_kur = 49.97, 56.00

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

--- 2. OTURUM DURUMU ---

if 'page' not in st.session_state: st.session_state.page = 'home'
if 'teklif_data' not in st.session_state: st.session_state.teklif_data = None
def go_page(page_name): st.session_state.page = page_name

--- 3. ÜST GEZİNTİ VE 4'LÜ GEÇİŞ BUTONLARI ---

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

==========================================

MENÜ 1: ANA SAYFA

==========================================

if st.session_state.page == 'home':
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
st.markdown("Yönetim & Hesaplama Modülü



", unsafe_allow_html=True)
if st.button("1. Parametreler (Fiyat Listesi Yönetimi - 37 Kalem)", use_container_width=True): go_page('params'); st.rerun()
st.markdown("



", unsafe_allow_html=True)
if st.button("2. Fiyat Çıkart (Maliyet Hesaplama Formu)", use_container_width=True): go_page('calc'); st.rerun()
st.markdown("



", unsafe_allow_html=True)
if st.button("3. 📄 Müşteri Fiyat Teklifi Mektubu ve Tablosu", use_container_width=True): go_page('teklif'); st.rerun()

==========================================

MENÜ 2: PARAMETRELER SAYFASI (KALICI JSON)

==========================================

elif st.session_state.page == 'params':
st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi (37 Kalem)")
col1, col2 = st.columns(2)
with col1:
st.markdown("#### 1. Kağıt ve Karton Grubu (Ton Maliyetleri)")
st.session_state.params['bristol'] = st.number_input("Amerikan Bristol Ton ($ USD)", value=st.session_state.params['bristol'], key="p_bris")
st.session_state.params['krome'] = st.number_input("Krome Karton Ton (TL)", value=st.session_state.params['krome'], key="p_krom")
st.session_state.params['kuse'] = st.number_input("Kuşe Ton (€ EUR)", value=st.session_state.params['kuse'], key="p_kus")
st.session_state.params['hamur'] = st.number_input("1. Hamur Ton ($ USD)", value=st.session_state.params['hamur'], key="p_ham")

    st.markdown("---")
    st.markdown("#### 2. Baskı Grubu")
    st.session_state.params['b_3550_cmyk'] = st.number_input("35x50 CMYK Hazırlık (₺)", value=st.session_state.params['b_3550_cmyk'], key="p_b35c")
    st.session_state.params['b_3550_pantone'] = st.number_input("35x50 Pantone 1 Renk (₺)", value=st.session_state.params['b_3550_pantone'], key="p_b35p")
    st.session_state.params['b_3550_tiraj'] = st.number_input("35x50 Tiraj (1.000 Adet/₺)", value=st.session_state.params['b_3550_tiraj'], key="p_b35t")
    st.session_state.params['b_5070_cmyk'] = st.number_input("50x70 CMYK Hazırlık (₺)", value=st.session_state.params['b_5070_cmyk'], key="p_b50c")
    st.session_state.params['b_5070_pantone'] = st.number_input("50x70 Pantone 1 Renk (₺)", value=st.session_state.params['b_5070_pantone'], key="p_b50p")
    st.session_state.params['b_5070_tiraj'] = st.number_input("50x70 Tiraj (1.000 Adet/₺)", value=st.session_state.params['b_5070_tiraj'], key="p_b50t")
    st.session_state.params['b_70100_cmyk'] = st.number_input("70x100 CMYK Hazırlık (₺)", value=st.session_state.params['b_70100_cmyk'], key="p_b70c")
    st.session_state.params['b_70100_pantone'] = st.number_input("70x100 Pantone 1 Renk (₺)", value=st.session_state.params['b_70100_pantone'], key="p_b70p")
    st.session_state.params['b_70100_tiraj'] = st.number_input("70x100 Tiraj (1.000 Adet/₺)", value=st.session_state.params['b_70100_tiraj'], key="p_b70t")
    st.session_state.params['disp_5070'] = st.number_input("50x70 Dispresiyon Lak Hazırlık (₺)", value=st.session_state.params['disp_5070'], key="p_d50")
    st.session_state.params['disp_5070_tiraj'] = st.number_input("50x70 Dispresiyon Lak Tiraj (1.000 Adet/₺)", value=st.session_state.params['disp_5070_tiraj'], key="p_d50t")
    st.session_state.params['disp_70100'] = st.number_input("70x100 Dispresiyon Lak Hazırlık (₺)", value=st.session_state.params['disp_70100'], key="p_d70")
    st.session_state.params['disp_70100_tiraj'] = st.number_input("70x100 Dispresiyon Lak Tiraj (1.000 Adet/₺)", value=st.session_state.params['disp_70100_tiraj'], key="p_d70t")

with col2:
    st.markdown("#### 3. Yüzey İşlemleri ve Kaplama Grubu")
    st.session_state.params['mat_sel'] = st.number_input("Mat Selofan M2 (₺)", value=st.session_state.params['mat_sel'], key="p_msel")
    st.session_state.params['par_sel'] = st.number_input("Parlak Selofan M2 (₺)", value=st.session_state.params['par_sel'], key="p_psel")
    st.session_state.params['lokal_5070'] = st.number_input("Lokal Lak 50x70 Hazırlık (₺)", value=st.session_state.params['lokal_5070'], key="p_l50")
    st.session_state.params['lokal_5070_tiraj'] = st.number_input("Lokal Lak 50x70 Tiraj (Adet/₺)", value=st.session_state.params['lokal_5070_tiraj'], key="p_l50t")
    st.session_state.params['lokal_70100'] = st.number_input("Lokal Lak 70x100 Hazırlık (₺)", value=st.session_state.params['lokal_70100'], key="p_l70")
    st.session_state.params['lokal_70100_tiraj'] = st.number_input("Lokal Lak 70x100 Tiraj (Adet/₺)", value=st.session_state.params['lokal_70100_tiraj'], key="p_l70t")
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
    st.session_state.params['omega_tek'] = st.number_input("Omega Tek Kulak Hazırlık (₺)", value=st.session_state.params['omega_tek'], key="p_omt")
    st.session_state.params['omega_tek_tiraj'] = st.number_input("Omega Tek Kulak Tiraj (₺)", value=st.session_state.params['omega_tek_tiraj'], key="p_omtt")
    st.session_state.params['omega_dip'] = st.number_input("Omega Dip Hazırlık (₺)", value=st.session_state.params['omega_dip'], key="p_omd")
    st.session_state.params['omega_dip_tiraj'] = st.number_input("Omega Dip Tiraj (₺)", value=st.session_state.params['omega_dip_tiraj'], key="p_omdt")

parametreleri_kaydet(st.session_state.params)
st.success("💾 Tüm parametre değişiklikleri kalıcı olarak kaydedildi.")


==========================================

MENÜ 3: FORM VE HESAPLAMA MODÜLÜ

==========================================

elif st.session_state.page == 'calc':

# MAKİNE SINIRLARI KONTROLÜ
def makine_uygun_mu(tw, th, makine_kodu):
    if tw > th: tw, th = th, tw
    if makine_kodu == "70100":
        return (tw <= 1000 and th <= 700) and (tw >= 350 and th >= 700 or (tw >= 700 and th >= 350))
    elif makine_kodu == "5070":
        return (tw <= 700 and th <= 500) and (tw >= 250 and th >= 350)
    elif makine_kodu == "3550":
        return (tw <= 500 and th <= 350) and (tw >= 200 and th >= 300)
    return True

# DİNAMİK JIGSAW (İÇ İÇE GEÇME) MONTAJ VE ÇİFT SAYI KURALI
def fiziksel_montaj_bul(tw, th, en, boy, yukseklik, makas, kutu_formu):
    if tw > th: tw, th = th, tw 
    best_m = 0
    kutu_acik_en = (en * 2.0) + (yukseklik * 2.0) + 15.0
    
    for s_en in range(1, 15):
        boy_range = range(2, 15, 2) if kutu_formu in ["Dip Kilitli Kutu", "Dip Kilit Yapıştırmalı Kutu", "Dip Yapıştırmalı Kutu"] else range(1, 15)
        
        for s_boy in boy_range:
            item_w = kutu_acik_en * s_en
            if kutu_formu in ["Dip Kilitli Kutu", "Dip Kilit Yapıştırmalı Kutu", "Dip Yapıştırmalı Kutu"]:
                pair_boy = (boy * 2.0) + ((yukseklik + 15.0) * 2.0)
                item_h = (s_boy // 2) * pair_boy
            else:
                item_h = (boy + ((yukseklik + 15.0) * 2.0)) * s_boy
            
            sigar_mi = False
            if tw > makas:
                if (item_w <= tw - makas) and (item_h <= th): sigar_mi = True
                if (item_h <= tw - makas) and (item_w <= th): sigar_mi = True
            if th > makas:
                if (item_w <= th - makas) and (item_h <= tw): sigar_mi = True
                if (item_h <= th - makas) and (item_w <= tw): sigar_mi = True

            if sigar_mi and (s_en * s_boy) > best_m:
                best_m = s_en * s_boy
    return best_m

def hesapla_maliyet_detayli(net_adet, gramaj, kagit_cinsi, baski_yuzu, pantone_secimi, laminasyon, ozel_baski_1, ozel_baski_2, baski_sonrasi, kagit_adi, makine_kodu, tab_en_mm, tab_boy_mm, makas_payi_mm, montaj_adedi, ebat_en, ebat_boy, ebat_yukseklik):
    params = st.session_state.params
    fire_pct = 10.0 if net_adet <= 1500 else (7.0 if net_adet <= 3000 else 5.0)
    brut_adet = int(math.ceil(net_adet * (1 + (fire_pct / 100.0))))
    tab_en, tab_boy = tab_en_mm / 1000.0, tab_boy_mm / 1000.0

    revolta_uygun_kagit = kagit_cinsi in ["Kuşe Kağıt", "1. Hamur Kağıt"]
    gercek_baski_yuzu = baski_yuzu
    if baski_yuzu in ["Çift Yüz", "Ön ve Arka Baskı"]:
        gercek_baski_yuzu = "Revolta Baskı" if (revolta_uygun_kagit and montaj_adedi % 2 == 0) else "Çift Yüz (Normal)"

    tabaka_adeti = math.ceil(brut_adet / montaj_adedi) if montaj_adedi > 0 else 0
    if 0 < tabaka_adeti < 100: tabaka_adeti = 100

    gecis_sayisi = 1
    is_cift_yuz = baski_yuzü = baski_yuzu in ["Çift Yüz", "Ön ve Arka Baskı", "Çift Yüz (Normal)"]
    
    kalıp_sayisi = 8 if (is_cift_yuz and gercek_baski_yuzu != "Revolta Baskı") else 4
    has_pantone = pantone_secimi != "Yok"
    if has_pantone:
        kalıp_sayisi += (4 if is_cift_yuz else 2) if "2 renk" in pantone_secimi else (2 if is_cift_yuz else 1)

    if is_cift_yuz and kagit_cinsi in ["Amerikan Bristol", "Krome Karton"]: gecis_sayisi = 2
    elif has_pantone and "Çift Yüz" not in pantone_secimi: gecis_sayisi = 2
    elif is_cift_yuz and has_pantone: gecis_sayisi = 2

    toplam_m2 = round(tabaka_adeti * tab_en * tab_boy, 2)
    kg_kagit = round((toplam_m2 * gramaj) / 1000.0, 2)

    ton_fiyat_tl = params['krome'] if kagit_cinsi == "Krome Karton" else (params['kuse'] * canli_eur if kagit_cinsi == "Kuşe Kağıt" else (params['hamur'] * canli_usd if kagit_cinsi == "1. Hamur Kağıt" else params['bristol'] * canli_usd))
    kagit_maliyeti = (kg_kagit / 1000.0) * ton_fiyat_tl

    b_cmyk_base = params.get(f"b_{makine_kodu}_cmyk", 2400.0)
    b_pantone_base = params.get(f"b_{makine_kodu}_pantone", 1200.0)
    b_tiraj_rate = params.get(f"b_{makine_kodu}_tiraj", 500.0)
    
    baski_vurus = tabaka_adeti * gecis_sayisi
    fazla_vurus = max(0, baski_vurus - 2000)
    baski_maliyeti = (b_cmyk_base + (fazla_vurus / 1000.0) * b_tiraj_rate) * (1.8 if is_cift_yuz and gercek_baski_yuzu != "Revolta Baskı" else 1.0)
    if has_pantone: baski_maliyeti += b_pantone_base * (2 if "2 renk" in pantone_secimi else 1)

    selofan_maliyeti = 0.0
    if laminasyon == "Mat Selofan": selofan_maliyeti = toplam_m2 * params['mat_sel']
    elif laminasyon == "Parlak Selofan": selofan_maliyeti = toplam_m2 * params['par_sel']
    elif "Dispersiyon" in laminasyon or "Dispresiyon" in laminasyon:
        d_base = params['disp_5070'] if makine_kodu != "70100" else params['disp_70100']
        d_rate = params['disp_5070_tiraj'] if makine_kodu != "70100" else params['disp_70100_tiraj']
        selofan_maliyeti = d_base + max(0, (tabaka_adeti - (1000 if makine_kodu != "70100" else 2000)) / 1000.0) * d_rate

    ozel_baski_maliyeti = 0.0
    for ob in [ozel_baski_1, ozel_baski_2]:
        if "Lokal Lak" in ob: ozel_baski_maliyeti += (params['lokal_5070'] if makine_kodu != "70100" else params['lokal_70100']) + max(0, tabaka_adeti - 1000) * (params['lokal_5070_tiraj'] if makine_kodu != "70100" else params['lokal_70100_tiraj'])
        elif "Kabartma Lak" in ob: ozel_baski_maliyeti += (params['kab_5070'] if makine_kodu != "70100" else params['kab_70100']) + max(0, tabaka_adeti - 1000) * (params['kab_5070_tiraj'] if makine_kodu != "70100" else params['kab_70100_tiraj'])
        elif ob in ["Gofre", "Varak Yaldız"]: ozel_baski_maliyeti += 2000.0 + (tabaka_adeti * 0.5)

    kesim_maliyeti = 0.0
    if baski_sonrasi == "Düz Kesim": kesim_maliyeti = 400.0
    elif baski_sonrasi in ["Özel kesim", "Özel Kesim"]: kesim_maliyeti = params['bobst'] + max(0, net_adet - 1000) * params['bobst_tiraj']
    elif baski_sonrasi == "Yan Yapıştırmalı Kutu": kesim_maliyeti = (params['kazanli'] + max(0, net_adet - 1000) * params['kazanli_tiraj']) + (params['omega_tek'] + max(0, net_adet - 10000) * params['omega_tek_tiraj'])
    elif baski_sonrasi in ["Dip Yapıştırmalı Kutu", "Kutu Kesim + Yapıştırma"]: kesim_maliyeti = (params['kazanli'] + max(0, net_adet - 1000) * params['kazanli_tiraj']) + (params['omega_dip'] + max(0, net_adet - 10000) * params['omega_dip_tiraj'])
    elif baski_sonrasi == "Pencereli Kutu Kesim+Yapıştırma": kesim_maliyeti = ((params['kazanli'] + max(0, net_adet - 1000) * params['kazanli_tiraj']) + (params['omega_dip'] + max(0, net_adet - 10000) * params['omega_dip_tiraj'])) * 1.35

    toplam_uretim_maliyeti = kagit_maliyeti + baski_maliyeti + selofan_maliyeti + ozel_baski_maliyeti + kesim_maliyeti

    return {
        "brut_adet": brut_adet, "fire_pct": fire_pct, "montaj_adedi": montaj_adedi, "tabaka_adeti": tabaka_adeti,
        "gecis_sayisi": gecis_sayisi, "kalıp_sayisi": kalıp_sayisi, "toplam_m2": toplam_m2, "kg_kagit": kg_kagit,
        "kagit_maliyeti": kagit_maliyeti, "baski_maliyeti": baski_maliyeti, "selofan_maliyeti": selofan_maliyeti,
        "ozel_baski_maliyeti": ozel_baski_maliyeti, "kesim_maliyeti": kesim_maliyeti, "toplam_uretim_maliyeti": toplam_uretim_maliyeti,
        "gercek_baski_yuzu": gercek_baski_yuzu, "makine_kodu": makine_kodu
    }

# GÖNDERDİĞİNİZ EBAT MATRİSLERİ VE BOBİN BÖLME OPTİMİZASYONU
def makine_ve_ebat_sec_optimum(adet, gramaj, kagit):
    ebat_havuzu = []
    
    if kagit in ["Amerikan Bristol", "Krome Karton"]:
        ebat_havuzu = [
            ("70x100 cm (Standart)", 700.0, 1000.0, "70100", 15.0),
            ("50x70 cm (Standart)", 500.0, 700.0, "5070", 12.0),
            ("33.3x70 cm (Standart)", 333.0, 700.0, "3550", 10.0),
            ("35x65 cm (Standart)", 350.0, 650.0, "5070", 12.0),
            ("35x50 cm (Standart)", 350.0, 500.0, "3550", 10.0),
            ("23x50 cm (Standart)", 230.0, 500.0, "3550", 10.0),
            ("25x45 cm (Standart)", 250.0, 450.0, "3550", 10.0),
        ]
        for w_cm in [55, 60, 65, 70, 75]:
            max_h = 100 if w_cm != 75 else 65
            min_h = 60
            for h_cm in range(min_h, max_h + 1, 5):
                mk = "5070" if w_cm <= 50 else "70100"
                ebat_havuzu.append((f"Bobin Kesim {w_cm}x{h_cm} cm", float(w_cm*10), float(h_cm*10), mk, 15.0 if mk=="70100" else 12.0))
    else:
        ebat_havuzu = [
            ("70x100 cm (Standart)", 700.0, 1000.0, "70100", 15.0),
            ("50x70 cm (Standart)", 500.0, 700.0, "5070", 12.0),
            ("33.3x70 cm (Standart)", 333.0, 700.0, "3550", 10.0),
            ("35x65 cm (Standart)", 350.0, 650.0, "5070", 12.0),
            ("35x50 cm (Standart)", 350.0, 500.0, "3550", 10.0),
            ("23x50 cm (Standart)", 230.0, 500.0, "3550", 10.0),
            ("25x45 cm (Standart)", 250.0, 450.0, "3550", 10.0),
            ("64x90 cm (Standart)", 640.0, 900.0, "70100", 15.0),
            ("45x64 cm (Standart)", 450.0, 640.0, "5070", 12.0),
            ("30x64 cm (Standart)", 300.0, 640.0, "3550", 10.0),
            ("31x59 cm (Standart)", 310.0, 590.0, "5070", 12.0),
            ("32x45 cm (Standart)", 320.0, 450.0, "3550", 10.0),
            ("21.3x45 cm (Standart)", 213.0, 450.0, "3550", 10.0),
            ("22.5x41.5 cm (Standart)", 225.0, 415.0, "3550", 10.0),
        ]
        if gramaj <= 170:
            ebat_havuzu.extend([
                ("57x82 cm (Standart)", 570.0, 820.0, "70100", 15.0),
                ("41x57 cm (Standart)", 410.0, 570.0, "5070", 12.0),
                ("27.3x57 cm (Standart)", 273.0, 570.0, "3550", 10.0),
            ])

    en_iyi_sonuc = None
    en_dusuk_toplam_maliyet = float('inf')

    for kagit_adi, tw, th, makine_kodu, makas in ebat_havuzu:
        montaj = fiziksel_montaj_bul(tw, th, ebat_en, ebat_boy, ebat_yukseklik, makas, urun_tipi)
        if montaj <= 0: continue

        res = hesapla_maliyet_detayli(
            adet, gramaj, kagit, cmyk_secim, pantone_secimi, 
            laminasyon, ozel_baski_1, ozel_baski_2, baski_sonrasi, 
            kagit_adi, makine_kodu, tw, th, makas, montaj, ebat_en, ebat_boy, ebat_yukseklik
        )

        if "Bobin Kesim" in kagit_adi and res['kg_kagit'] < 600: continue

        if res['toplam_uretim_maliyeti'] < en_dusuk_toplam_maliyet:
            en_dusuk_toplam_maliyet = res['toplam_uretim_maliyeti']
            en_iyi_sonuc = {'adet': adet, 'gramaj': gramaj, 'kagit': kagit, 'fire': res['fire_pct'], 'ebat': kagit_adi, 'res': res}

    if en_iyi_sonuc is None:
        guvenli_m = fiziksel_montaj_bul(700.0, 1000.0, ebat_en, ebat_boy, ebat_yukseklik, 15.0, urun_tipi)
        res = hesapla_maliyet_detayli(adet, gramaj, kagit, cmyk_secim, pantone_secimi, laminasyon, ozel_baski_1, ozel_baski_2, baski_sonrasi, "70x100 cm (Standart)", "70100", 700.0, 1000.0, 15.0, max(guvenli_m, 1), ebat_en, ebat_boy, ebat_yukseklik)
        en_iyi_sonuc = {'adet': adet, 'gramaj': gramaj, 'kagit': kagit, 'fire': 5.0, 'ebat': "70x100 cm (Standart)", 'res': res}

    return en_iyi_sonuc

st.subheader("📋 Ürün Tanımlama & Maliyet Hesaplama Formu")
st.markdown("---")

col_r1_1, col_r1_2, col_r1_3 = st.columns(3)
with col_r1_1: firma_adi = st.text_input("Firma Adı", "Erhan Ticaret")
with col_r1_2: urun_adi = st.text_input("Ürün Adı", "Kilitli/Yapıştırmalı Ambalaj Kutusu")
with col_r1_3: urun_tipi = st.selectbox("Ürün Tipi", ["Föy", "Tek Kırımlı Broşür", "İki Kırımlı Broşür", "Kartonet", "Standart Kutu", "Dip Kilitli Kutu", "Dip Kilit Yapıştırmalı Kutu", "Yan Yapıştırmalı Kutu", "Sıvamalı Kutu", "Etiket", "Prospektüs"])

col_r2_1, col_r2_2, col_r2_3 = st.columns(3)
with col_r2_1: net_a = st.number_input("Ürün Adedi A", value=10000, step=1000, key="net_a")
with col_r2_2: net_b = st.number_input("Ürün Adedi B", value=20000, step=1000, key="net_b")
with col_r2_3: net_c = st.number_input("Ürün Adedi C", value=50000, step=1000, key="net_c")

col_ka_head, col_kb_head = st.columns(2)
with col_ka_head:
    ca_g, ca_c = st.columns(2)
    with ca_g: gramaj_a = st.number_input("Gramaj A (gr/m²)", value=300, step=10, min_value=50, key="gramaj_a")
    with ca_c: kagit_cinsi_a = st.selectbox("Kağıt Cinsi A", ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"], key="kagit_cinsi_a")
with col_kb_head:
    cb_g, cb_c = st.columns(2)
    with cb_g: gramaj_b = st.number_input("Gramaj B (Opsiyonel)", value=350, step=10, min_value=50, key="gramaj_b")
    with cb_c: kagit_cinsi_b = st.selectbox("Kağıt Cinsi B", ["Yok / Kullanma", "Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"], key="kagit_cinsi_b")

ikinci_kagit_var = kagit_cinsi_b != "Yok / Kullanma"

col_ebat1, col_ebat2, col_ebat3, col_baski1, col_baski2 = st.columns(5)
with col_ebat1: ebat_en = st.number_input("En (mm) [A]", value=100, key="ebat_en")
with col_ebat2: ebat_boy = st.number_input("Boy (mm) [B]", value=150, key="ebat_boy")
with col_ebat3: ebat_yukseklik = st.number_input("Yükseklik (mm) [C]", value=30, key="ebat_yukseklik")
with col_baski1: cmyk_secim = st.selectbox("Baskı CMYK", ["Çift Yüz", "Tek Yüz", "CMYK Baskı yok"], key="cmyk_secim")
with col_baski2: pantone_secimi = st.selectbox("Baskı Pantone", ["Yok", "1 renk zemin", "2 renk zemin", "1 renk lokal", "2 renk lokal", "1 renk zemin (Çift Yüz)", "2 renk zemin (Çift Yüz)", "1 renk lokal (Çift Yüz)", "2 renk lokal (Çift Yüz)"], key="pantone_secimi")

c_lam, c_ob1, c_ob2, c_bs = st.columns(4)
with c_lam: laminasyon = st.selectbox("Laminasyon", ["Parlak Selofan", "Mat Selofan", "Dispersiyon Lak", "Yok"], key="laminasyon")
with c_ob1: ozel_baski_1 = st.selectbox("Özel Baskı 1", ["Yok", "Lokal Lak", "Kabartma Lak", "Gofre", "Varak Yaldız"], key="ozel_baski_1")
with c_ob2: ozel_baski_2 = st.selectbox("Özel Baskı 2", ["Yok", "Lokal Lak", "Kabartma Lak", "Gofre", "Varak Yaldız"], key="ozel_baski_2")
with c_bs: baski_sonrasi = st.selectbox("Baskı Sonrası", ["Düz Kesim", "Özel kesim", "Kutu Kesim + Yapıştırma", "Yan Yapıştırmalı Kutu", "Dip Yapıştırmalı Kutu", "Pencereli Kutu Kesim+Yapıştırma"], key="baski_sonrasi")

ozel_istekler = st.text_input("Özel İstekler", "", key="ozel_istekler")
st.markdown("---")

plan_params = []
plan_params.append({**makine_ve_ebat_sec_optimum(net_a, gramaj_a, kagit_cinsi_a), 'kod': 'A'})
plan_params.append({**makine_ve_ebat_sec_optimum(net_b, gramaj_a, kagit_cinsi_a), 'kod': 'B'})
plan_params.append({**makine_ve_ebat_sec_optimum(net_c, gramaj_a, kagit_cinsi_a), 'kod': 'C'})

if ikinci_kagit_var:
    plan_params.append({**makine_ve_ebat_sec_optimum(net_a, gramaj_b, kagit_cinsi_b), 'kod': 'A2'})
    plan_params.append({**makine_ve_ebat_sec_optimum(net_b, gramaj_b, kagit_cinsi_b), 'kod': 'B2'})
    plan_params.append({**makine_ve_ebat_sec_optimum(net_c, gramaj_b, kagit_cinsi_b), 'kod': 'C2'})

kar_orani = st.slider("Hedef Kar Marjı (%)", 0, 100, 30)

st.session_state.teklif_data = {
    "firma_adi": firma_adi, "urun_adi": urun_adi, "urun_tipi": urun_tipi,
    "ebat_en": ebat_en, "ebat_boy": ebat_boy, "ebat_yukseklik": ebat_yukseklik,
    "cmyk_secim": cmyk_secim, "pantone_secimi": pantone_secimi, "laminasyon": laminasyon,
    "baski_sonrasi": baski_sonrasi, "ozel_baski": ", ".join([ob for ob in [ozel_baski_1, ozel_baski_2] if ob != "Yok"]) or "Yok",
    "ozel_istekler": ozel_istekler, "kar_orani": kar_orani, "alternatifler": plan_params
}

st.markdown("### 📊 TAM DİNAMİK AMBALAJ HESAPLAMA SONUÇLARI")

def plan_kartini_yazdir(p):
    r = p['res']
    st.markdown(f"**{p['adet']:,} adet - {p['gramaj']}g {p['kagit']}**")
    plan_df = pd.DataFrame([
        {"Parametre": "Fire Oranı / Brüt", "Değer": f"%{r['fire_pct']:.1f} / {r['brut_adet']:,} adet"},
        {"Parametre": "Montaj Planı", "Değer": f"1 Tabakada {r['montaj_adedi']} Ürün"},
        {"Parametre": "Optimize Ebat / Makine", "Değer": f"{p['ebat']} ({r['makine_kodu']} Makine)"},
        {"Parametre": "Kalıp Sayısı", "Değer": f"{r['kalıp_sayisi']} Adet"},
        {"Parametre": "Kağıt Ağırlığı", "Değer": f"{r['kg_kagit']} kg"},
        {"Parametre": "Baskı Metodu", "Değer": f"{r['tabaka_adeti']:,} tabaka x {r['gecis_sayisi']} / {r['gercek_baski_yuzu']}"}
    ])
    st.table(plan_df)

if ikinci_kagit_var:
    st.markdown("#### 🔹 Kağıt A Alternatifleri")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1: st.markdown("##### Alternatif A"); plan_kartini_yazdir(plan_params[0])
    with col_p2: st.markdown("##### Alternatif B"); plan_kartini_yazdir(plan_params[1])
    with col_p3: st.markdown("##### Alternatif C"); plan_kartini_yazdir(plan_params[2])
    st.markdown("#### 🔹 Kağıt B Alternatifleri")
    col_p4, col_p5, col_p6 = st.columns(3)
    with col_p4: st.markdown("##### Alternatif A2"); plan_kartini_yazdir(plan_params[3])
    with col_p5: st.markdown("##### Alternatif B2"); plan_kartini_yazdir(plan_params[4])
    with col_p6: st.markdown("##### Alternatif C2"); plan_kartini_yazdir(plan_params[5])
else:
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1: st.markdown("##### Alternatif A"); plan_kartini_yazdir(plan_params[0])
    with col_p2: st.markdown("##### Alternatif B"); plan_kartini_yazdir(plan_params[1])
    with col_p3: st.markdown("##### Alternatif C"); plan_kartini_yazdir(plan_params[2])

st.markdown("---")
if st.button("📄 Müşteri İçin Hazır Fiyat Teklif Sayfasına Git", use_container_width=True, key="calc_to_teklif"):
    go_page('teklif')
    st.rerun()


==========================================

MENÜ 4: MÜŞTERİ FİYAT TEKLİF SAYFASI

==========================================

elif st.session_state.page == 'teklif':
st.subheader("📄 Müşteri Fiyat Teklifi ve Ürün Şartnamesi")

if st.session_state.teklif_data is None:
    st.warning("⚠️ Henüz bir hesaplama yapılmadı. Lütfen önce 'Fiyat Çıkart' modülünden ürün hesaplamasını gerçekleştirin.")
    if st.button("Forma Dön", key="teklif_to_calc"): go_page('calc'); st.rerun()
else:
    td = st.session_state.teklif_data
    st.markdown(
        "<div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1F4E78;'>"
        "<h3 style='margin: 0; color: #1F4E78;'>OFFICIAL PRICE QUOTATION / FİYAT TEKLİF MEKTUBU</h3>"
        f"<p style='margin: 5px 0 0 0;'><strong>Sayın:</strong> {td['firma_adi']}</p>"
        "<p style='margin: 2px 0 0 0;'><strong>Tarih:</strong> 04 Kasım 2026 | <strong>Teklif No:</strong> OFF-2026-8492</p>"
        "</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 1. Ürün & İmalat Teknik Özellikleri")
    c1, c2, c3 = st.columns(3)
    with c1: st.write(f"**Ürün Adı:** {td['urun_adi']}"); st.write(f"**Ürün Tipi:** {td['urun_tipi']}"); st.write(f"**Ebat:** {td['ebat_en']}x{td['ebat_boy']}x{td['ebat_yukseklik']} mm")
    with c2: st.write(f"**Baskı CMYK:** {td['cmyk_secim']}"); st.write(f"**Pantone Renk:** {td['pantone_secimi']}"); st.write(f"**Yüzey:** {td['laminasyon']}")
    with c3: st.write(f"**Özel İşlem:** {td['ozel_baski']}"); st.write(f"**Kesim/Mücellit:** {td['baski_sonrasi']}")

    st.markdown("---")
    st.markdown("#### 2. Adet Alternatiflerine Göre Fiyat Tablosu")

    rows = []
    for alt in td['alternatifler']:
        r = alt['res']
        satis = r['toplam_uretim_maliyeti'] * (1 + (td['kar_orani'] / 100.0))
        rows.append({
            "Alternatif": f"Option {alt['kod']}", "Net Adet": f"{alt['adet']:,}", 
            "Kağıt Özelliği": f"{alt['gramaj']} gr {alt['kagit']}", "Tabaka Ebadı": alt['ebat'], 
            "Ağırlık": f"{r['kg_kagit']} kg", "Birim Fiyat (TL)": f"₺{(satis/alt['adet']) if alt['adet']>0 else 0:,.4f}", 
            "Toplam Satış (TL)": f"₺{satis:,.2f}"
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
