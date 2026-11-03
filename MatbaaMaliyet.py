import streamlit as st
import xml.etree.ElementTree as ET
import urllib.request
import math

st.set_page_config(page_title="Matbaa ve Ambalaj Maliyet Sistemi", layout="wide")

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

default_params = {
    # 1. Kağıt Grubu (Ton Maliyetleri)
    'bristol': 825.0,     # USD / Ton
    'krome': 40000.0,     # TL / Ton
    'kuse': 850.0,        # EUR / Ton
    'hamur': 1200.0,      # USD / Ton
    
    # 2. Baskı Grubu (Hazırlık + Tiraj)
    'b_3550_cmyk': 1800.0, 'b_3550_pantone': 900.0, 'b_3550_tiraj': 400.0,
    'b_5070_cmyk': 3500.0, 'b_5070_pantone': 1750.0, 'b_5070_tiraj': 800.0,
    'b_70100_cmyk': 5000.0, 'b_70100_pantone': 1750.0, 'b_70100_tiraj': 1400.0,
    
    # 3. Yüzey İşlemleri ve Lak Grubu
    'disp_5070': 1500.0, 'disp_5070_tiraj': 800.0,
    'disp_70100': 2000.0, 'disp_70100_tiraj': 1000.0,
    'mat_sel': 4.70, 'par_sel': 4.50,
    'lokal_5070': 1500.0, 'lokal_5070_tiraj': 1.5,
    'lokal_70100': 1800.0, 'lokal_70100_tiraj': 1.5,
    'kab_5070': 1600.0, 'kab_5070_tiraj': 1.6,
    'kab_70100': 1900.0, 'kab_70100_tiraj': 1.9,
    
    # 4. Kesim ve Mücellit Grubu
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

# --- 3. ÜST GEZİNTİ BİLGİSİ ---
st.markdown("### 🖨️ MATBAAM PRO - Ambalaj & Matbaa Maliyet Sistemi")
st.info(f"🏦 TCMB Anlık Efektif Satış Kurları — USD: ₺{canli_usd:.2f} | EUR: ₺{canli_eur:.2f}")
st.markdown("---")

# ==========================================
# MENÜ 1: ANA SAYFA
# ==========================================
if st.session_state.page == 'home':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>Yönetim & Hesaplama Modülü</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("1. Parametreler (Fiyat Listesi Yönetimi)", use_container_width=True):
            go_params()
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("2. Fiyat Çıkart (Maliyet Hesaplama Formu)", use_container_width=True):
            go_calc()
            st.rerun()

# ==========================================
# MENÜ 2: PARAMETRELER SAYFASI (EXCEL VERİLERİ)
# ==========================================
elif st.session_state.page == 'params':
    if st.button("⬅️ Ana Menüye Dön"):
        go_home()
        st.rerun()
        
    st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi (Orijinal Excel Verileri)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 1. Kağıt ve Karton Grubu (Ton)")
        st.session_state.params['bristol'] = st.number_input("Amerikan Bristol Ton ($ USD)", value=st.session_state.params['bristol'], key="p_bris")
        st.session_state.params['krome'] = st.number_input("Krome Karton Ton (TL)", value=st.session_state.params['krome'], key="p_krom")
        st.session_state.params['kuse'] = st.number_input("Kuşe Ton (€ EUR)", value=st.session_state.params['kuse'], key="p_kus")
        st.session_state.params['hamur'] = st.number_input("1. Hamur Ton ($ USD)", value=st.session_state.params['hamur'], key="p_ham")
        
        st.markdown("#### 3. Yüzey İşlemleri ve Lak Grubu")
        st.session_state.params['disp_5070'] = st.number_input("50x70 Dispresiyon Lak (Hazırlık)", value=st.session_state.params['disp_5070'], key="p_d50")
        st.session_state.params['mat_sel'] = st.number_input("Mat Selofan M2 (₺)", value=st.session_state.params['mat_sel'], key="p_msel")
        st.session_state.params['par_sel'] = st.number_input("Parlak Selofan M2 (₺)", value=st.session_state.params['par_sel'], key="p_psel")
        st.session_state.params['lokal_5070'] = st.number_input("Lokal Lak 50x70 (Hazırlık)", value=st.session_state.params['lokal_5070'], key="p_l50")

    with col2:
        st.markdown("#### 2. Baskı Grubu")
        st.session_state.params['b_5070_cmyk'] = st.number_input("50x70 CMYK Hazırlık (₺)", value=st.session_state.params['b_5070_cmyk'], key="p_b50c")
        st.session_state.params['b_5070_tiraj'] = st.number_input("50x70 Tiraj (1.000 Adet/₺)", value=st.session_state.params['b_5070_tiraj'], key="p_b50t")
        st.session_state.params['b_70100_cmyk'] = st.number_input("70x100 CMYK Hazırlık (₺)", value=st.session_state.params['b_70100_cmyk'], key="p_b70c")
        st.session_state.params['b_70100_tiraj'] = st.number_input("70x100 Tiraj (1.000 Adet/₺)", value=st.session_state.params['b_70100_tiraj'], key="p_b70t")

        st.markdown("#### 4. Kesim ve Mücellit Grubu")
        st.session_state.params['kazanli'] = st.number_input("Kazanlı Kesim (Hazırlık)", value=st.session_state.params['kazanli'], key="p_kaz")
        st.session_state.params['pedal'] = st.number_input("Pedal Kesim (Hazırlık)", value=st.session_state.params['pedal'], key="p_ped")
        st.session_state.params['bobst'] = st.number_input("Bobst Kesim (Hazırlık)", value=st.session_state.params['bobst'], key="p_bob")
        st.session_state.params['omega_dip'] = st.number_input("Omega Dip Yapıştırma (Hazırlık)", value=st.session_state.params['omega_dip'], key="p_omd")

# ==========================================
# MENÜ 3: FORM VE HESAPLAMA MODÜLÜ
# ==========================================
elif st.session_state.page == 'calc':
    if st.button("⬅️ Ana Menüye Dön"):
        go_home()
        st.rerun()

    # --- MATBAA HESAPLAMA MOTORU ---
    def hesapla_maliyet_detayli(
        net_adet, gramaj, kagit_cinsi, baski_yuzu, pantone_sayisi, 
        laminasyon, ozel_baski, baski_sonrasi, basilacak_ebat, 
        fire_orani_override, ebat_en, ebat_boy, ebat_yukseklik
    ):
        params = st.session_state.params
        
        # 1. Fire Hesaplama Algoritması (Excel Planlama Kuralı)
        # Net Adet <= 1000 -> Min 100 Tabaka (%10)
        # 1000 < Net Adet <= 1500 -> %10
        # 1500 < Net Adet <= 3000 -> %7
        # Net Adet > 3000 -> %5
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
        
        # 2. Tabaka Ebadı ve Montaj Hesabı
        # Kuşe & 1. Hamur: Sabit (57x82, 64x90, 70x100)
        # Bristol & Krome: <600kg 70x100; >=600kg özel imalat
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

        # Ürün Boyutlarına Göre Montaj Hesabı (2D veya Kutu)
        en_m = ebat_en / 1000.0
        boy_m = ebat_boy / 1000.0
        fit_h = math.floor((tab_en - 0.02) / (en_m + 0.005)) * math.floor((tab_boy - 0.02) / (boy_m + 0.005))
        fit_v = math.floor((tab_en - 0.02) / (boy_m + 0.005)) * math.floor((tab_boy - 0.02) / (en_m + 0.005))
        montaj_adedi = max(1, max(fit_h, fit_v))

        tabaka_adeti = math.ceil(brut_adet / montaj_adedi)
        if tabaka_adeti < 100:
            tabaka_adeti = 100

        # Toplam M2 ve Kağıt Ağırlığı (Kg)
        toplam_m2 = round(tabaka_adeti * tab_en * tab_boy, 2)
        kg_kagit = round((toplam_m2 * gramaj) / 1000.0, 2)

        # 3. Kağıt Ton Maliyeti ve Kur Çevrimi
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

        # 4. Baskı ve Revolta Kontrolü (Excel Kuralı)
        # Kuşe & 1. Hamur -> Revolta yapılabilir
        # Bristol & Krome -> Revolta UYGULANAMAZ
        revolta_uygun = kagit_cinsi in ["Kuşe Kağıt", "1. Hamur Kağıt"]
        
        b_cmyk_base = params.get(f"b_{ebat_kodu}_cmyk", 3500.0)
        b_pantone_base = params.get(f"b_{ebat_kodu}_pantone", 1750.0)
        b_tiraj_rate = params.get(f"b_{ebat_kodu}_tiraj", 800.0)

        baski_vurus = tabaka_adeti
        if baski_yuzu == "Ön ve Arka Baskı":
            if revolta_uygun:
                baski_vurus = tabaka_adeti * 2
                baski_maliyeti = b_cmyk_base + max(0, (baski_vurus - 2000) / 1000.0) * b_tiraj_rate
            else:
                baski_maliyeti = (b_cmyk_base + max(0, (baski_vurus - 2000) / 1000.0) * b_tiraj_rate) * 1.8
        elif baski_yuzu == "Revolta Baskı":
            baski_vurus = tabaka_adeti * 2
            baski_maliyeti = b_cmyk_base + max(0, (baski_vurus - 2000) / 1000.0) * b_tiraj_rate
        elif baski_yuzu == "Tek Yüz Baskı":
            baski_maliyeti = b_cmyk_base + max(0, (baski_vurus - 2000) / 1000.0) * b_tiraj_rate
        else:
            baski_maliyeti = 0.0

        if pantone_sayisi != "Yok":
            renk_katsayi = 1
            if "2" in pantone_sayisi: renk_katsayi = 2
            elif "3" in pantone_sayisi: renk_katsayi = 3
            elif "4" in pantone_sayisi: renk_katsayi = 4
            baski_maliyeti += b_pantone_base * renk_katsayi

        # 5. Yüzey İşlemleri, Lak ve Özel Baskılar
        selofan_maliyeti = 0.0
        if laminasyon == "Mat Selofan":
            selofan_maliyeti = toplam_m2 * params['mat_sel']
        elif laminasyon == "Parlak Selofan":
            selofan_maliyeti = toplam_m2 * params['par_sel']
        elif laminasyon == "Dispresiyon Lak":
            disp_base = params['disp_5070'] if ebat_kodu != "70100" else params['disp_70100']
            disp_tiraj = params['disp_5070_tiraj'] if ebat_kodu != "70100" else params['disp_70100_tiraj']
            disp_limit = 1000 if ebat_kodu != "70100" else 2000
            selofan_maliyeti = disp_base + max(0, (tabaka_adeti - disp_limit) / 1000.0) * disp_tiraj

        ozel_baski_maliyeti = 0.0
        if ozel_baski != "Yok":
            if "Lokal Lak" in ozel_baski:
                l_base = params['lokal_5070'] if ebat_kodu != "70100" else params['lokal_70100']
                l_rate = params['lokal_5070_tiraj'] if ebat_kodu != "70100" else params['lokal_70100_tiraj']
                ozel_baski_maliyeti = l_base + max(0, tabaka_adeti - 1000) * l_rate
            elif "Kabartma Lak" in ozel_baski:
                k_base = params['kab_5070'] if ebat_kodu != "70100" else params['kab_70100']
                k_rate = params['kab_5070_tiraj'] if ebat_kodu != "70100" else params['kab_70100_tiraj']
                ozel_baski_maliyeti = k_base + max(0, tabaka_adeti - 1000) * k_rate
            elif ozel_baski in ["Gofre", "Varak Yaldız"]:
                ozel_baski_maliyeti = 2000.0 + (tabaka_adeti * 0.5)

        yuzey_lak_toplam = selofan_maliyeti + ozel_baski_maliyeti

        #
