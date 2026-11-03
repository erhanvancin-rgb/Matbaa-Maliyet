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

# Oturum Durumu ve EXCEL'DEKİ TÜM PARAMETRELER EKSİKSİZ
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'params' not in st.session_state:
    st.session_state.params = {
        # 1. Kağıt ve Karton Grubu
        'bristol': 825.0, 'krome': 40000.0, 'kuse': 850.0, 'hamur': 1200.0,
        
        # 2. Baskı Grubu
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

# 2. PARAMETRELER SAYFASI (Eksiksiz Excel Tablosu)
elif st.session_state.page == 'params':
    if st.button("⬅️ Ana Menüye Dön"):
        go_home()
        st.rerun()
        
    st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi (Tüm Excel Verileri)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 1. Kağıt ve Karton Grubu (Ton)")
        st.session_state.params['bristol'] = st.number_input("Amerikan Bristol Ton ($ USD)", value=st.session_state.params['bristol'], key="p_bristol")
        st.session_state.params['krome'] = st.number_input("Krome Karton Ton (TRY TL)", value=st.session_state.params['krome'], key="p_krome")
        st.session_state.params['kuse'] = st.number_input("Kuşe Ton (€ EUR)", value=st.session_state.params['kuse'], key="p_kuse")
        st.session_state.params['hamur'] = st.number_input("1. Hamur Ton ($ USD)", value=st.session_state.params['hamur'], key="p_hamur")
        
        st.markdown("#### 3. Yüzey İşlemleri ve Lak Grubu")
        st.session_state.params['disp_5070'] = st.number_input("50x70 Dispresiyon Lak", value=st.session_state.params['disp_5070'], key="p_disp_5070")
        st.session_state.params['disp_5070_tiraj'] = st.number_input("50x70 Dispresiyon Lak Tiraj", value=st.session_state.params['disp_5070_tiraj'], key="p_disp_5070_tiraj")
        st.session_state.params['disp_70100'] = st.number_input("70x100 Dispresiyon Lak", value=st.session_state.params['disp_70100'], key="p_disp_70100")
        st.session_state.params['disp_70100_tiraj'] = st.number_input("70x100 Dispresiyon Lak Tiraj", value=st.session_state.params['disp_70100_tiraj'], key="p_disp_70100_tiraj")
        st.session_state.params['mat_sel'] = st.number_input("Mat Selofan M2", value=st.session_state.params['mat_sel'], key="p_mat_sel")
        st.session_state.params['par_sel'] = st.number_input("Parlak Selofan M2", value=st.session_state.params['par_sel'], key="p_par_sel")
        st.session_state.params['lokal_5070'] = st.number_input("Lokal Lak 50x70", value=st.session_state.params['lokal_5070'], key="p_lokal_5070")
        st.session_state.params['lokal_5070_tiraj'] = st.number_input("Lokal Lak 50x70 Tiraj", value=st.session_state.params['lokal_5070_tiraj'], key="p_lokal_5070_tiraj")
        st.session_state.params['lokal_70100'] = st.number_input("Lokal Lak 70x100", value=st.session_state.params['lokal_70100'], key="p_lokal_70100")
        st.session_state.params['lokal_70100_tiraj'] = st.number_input("Lokal Lak 70x100 Tiraj", value=st.session_state.params['lokal_70100_tiraj'], key="p_lokal_70100_tiraj")
        st.session_state.params['kab_5070'] = st.number_input("Kabartma Lak 50x70", value=st.session_state.params['kab_5070'], key="p_kab_5070")
        st.session_state.params['kab_5070_tiraj'] = st.number_input("Kabartma Lak 50x70 Tiraj", value=st.session_state.params['kab_5070_tiraj'], key="p_kab_5070_tiraj")
        st.session_state.params['kab_70100'] = st.number_input("Kabartma Lak 70x100", value=st.session_state.params['kab_70100'], key="p_kab_70100")
        st.session_state.params['kab_70100_tiraj'] = st.number_input("Kabartma Lak 70x100 Tiraj", value=st.session_state.params['kab_70100_tiraj'], key="p_kab_70100_tiraj")

    with col2:
        st.markdown("#### 2. Baskı Grubu")
        st.session_state.params['b_3550_cmyk'] = st.number_input("35x50 Cmyk Proses", value=st.session_state.params['b_3550_cmyk'], key="p_3550_cmyk")
        st.session_state.params['b_3550_pantone'] = st.number_input("35x50 Pantone 1 Renk", value=st.session_state.params['b_3550_pantone'], key="p_3550_pantone")
        st.session_state.params['b_3550_tiraj'] = st.number_input("35x50 Tiraj Fiyatı", value=st.session_state.params['b_3550_tiraj'], key="p_3550_tiraj")
        st.session_state.params['b_5070_cmyk'] = st.number_input("50x70 Cmyk Proses", value=st.session_state.params['b_5070_cmyk'], key="p_5070_cmyk")
        st.session_state.params['b_5070_pantone'] = st.number_input("50x70 Pantone 1 Renk", value=st.session_state.params['b_5070_pantone'], key="p_5070_pantone")
        st.session_state.params['b_5070_tiraj'] = st.number_input("50x70 Tiraj Fiyatı", value=st.session_state.params['b_5070_tiraj'], key="p_5070_tiraj")
        st.session_state.params['b_70100_cmyk'] = st.number_input("70x100 Cmyk Proses", value=st.session_state.params['b_70100_cmyk'], key="p_70100_cmyk")
        st.session_state.params['b_70100_pantone'] = st.number_input("70x100 Pantone 1 Renk", value=st.session_state.params['b_70100_pantone'], key="p_70100_pantone")
        st.session_state.params['b_70100_tiraj'] = st.number_input("70x100 Tiraj Fiyatı", value=st.session_state.params['b_70100_tiraj'], key="p_70100_tiraj")

        st.markdown("#### 4. Kesim ve Mücellit Grubu")
        st.session_state.params['kazanli'] = st.number_input("Kazanlı Kesim", value=st.session_state.params['kazanli'], key="p_kazanli")
        st.session_state.params['kazanli_tiraj'] = st.number_input("Kazanlı Kesim Tiraj", value=st.session_state.params['kazanli_tiraj'], key="p_kazanli_tiraj")
        st.session_state.params['pedal'] = st.number_input("Pedal Kesim", value=st.session_state.params['pedal'], key="p_pedal")
        st.session_state.params['pedal_tiraj'] = st.number_input("Pedal Kesim Tiraj", value=st.session_state.params['pedal_tiraj'], key="p_pedal_tiraj")
        st.session_state.params['bobst'] = st.number_input("Bobts Kesim", value=st.session_state.params['bobst'], key="p_bobst")
        st.session_state.params['bobst_tiraj'] = st.number_input("Bobts Kesim Tiraj", value=st.session_state.params['bobst_tiraj'], key="p_bobst_tiraj")
        st.session_state.params['omega_tek'] = st.number_input("Omega Tek Kulak", value=st.session_state.params['omega_tek'], key="p_omega_tek")
        st.session_state.params['omega_tek_tiraj'] = st.number_input("Omega Tek Kulak Tiraj", value=st.session_state.params['omega_tek_tiraj'], key="p_omega_tek_tiraj")
        st.session_state.params['omega_dip'] = st.number_input("Omega Dip Yapıştırma", value=st.session_state.params['omega_dip'], key="p_omega_dip")
        st.session_state.params['omega_dip_tiraj'] = st.number_input("Omega Dip Yapıştırma Tiraj", value=st.session_state.params['omega_dip_tiraj'], key="p_omega_dip_tiraj")

# 3. FİYAT ÇIKART (HESAPLAMA) SAYFASI
elif st.session_state.page == 'calc':
    if st.button("⬅️ Ana Menüye Dön"):
        go_home()
        st.rerun()
        
    st.subheader("Maliyet Hesaplama Formu")
    
    c1, c2 = st.columns(2)
    with c1:
        firma = st.text_input("Firma Adı", "Erhan Ticaret")
        urun_adi = st.text_input("Ürün Adı / Modeli", "Lüks Kutu Ambalaj")
        adet = st.number_input("Ürün Adedi (Tiraj)", value=5000, step=500, min_value=1)
        kagit_cinsi = st.selectbox("Kağıt Cinsi", ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur"])
        gramaj = st.selectbox("Kağıt Gramajı (gr/m²)", [200, 250, 300, 350, 400], index=2)
    with c2:
        baski_turu = st.selectbox("Baskı Türü", ["50x70 CMYK", "70x100 CMYK", "35x50 CMYK"])
        
        st.markdown("**Ebat (mm x mm x mm)**")
        ex, ey, ez = st.columns(3)
        with ex: x_val = st.number_input("X", value=200)
        with ey: y_val = st.number_input("Y", value=150)
        with ez: z_val = st.number_input("Z", value=50)
        
        laminasyon = st.selectbox("Yüzey Laminasyonu", ["Mat Selofan", "Parlak Selofan", "Dispresiyon Lak", "Yok"])
        kesim = st.selectbox("Kesim Türü", ["Bobst Kesim", "Kazanlı Kesim", "Pedal Kesim", "Yok"])

    yapistirma = st.checkbox("Omega Dip Yapıştırma Dahil", value=True)
    nakliye = st.checkbox("Nakliye Dahil", value=True)
    kar_orani = st.slider("Hedef Kar Marjı (%)", 0, 100, 30)

    # Hesaplama Motoru (Canlı TCMB Kurları ile)
    ton_fiyat = st.session_state.params['bristol']
    birim_tip = 'USD'
    if kagit_cinsi == "Amerikan Bristol": ton_fiyat, birim_tip = st.session_state.params['bristol'], 'USD'
    elif kagit_cinsi == "Krome Karton": ton_fiyat, birim_tip = st.session_state.params['krome'], 'TL'
    elif kagit_cinsi == "Kuşe Kağıt": ton_fiyat, birim_tip = st.session_state.params['kuse'], 'EUR'
    elif kagit_cinsi == "1. Hamur": ton_fiyat, birim_tip = st.session_state.params['hamur'], 'USD'

    ton_fiyat_tl = ton_fiyat
    if birim_tip == 'USD': ton_fiyat_tl = ton_fiyat * canli_usd
    elif birim_tip == 'EUR': ton_fiyat_tl = ton_fiyat * canli_eur

    tabaka_adeti = max(1, adet // 2)
    kg_kagit = round((tabaka_adeti * (x_val/1000) * (y_val/1000) * gramaj) / 2)
    kagit_maliyeti = (kg_kagit / 1000) * ton_fiyat_tl

    # Baskı Maliyeti Hesaplama
    if "70x100" in baski_turu:
        baski_maliyeti = st.session_state.params['b_70100_cmyk'] + (adet * st.session_state.params['b_70100_tiraj'] / 1000)
    elif "35x50" in baski_turu:
        baski_maliyeti = st.session_state.params['b_3550_cmyk'] + (adet * st.session_state.params['b_3550_tiraj'] / 1000)
    else:
        baski_maliyeti = st.session_state.params['b_5070_cmyk'] + (adet * st.session_state.params['b_5070_tiraj'] / 1000)

    # Selofan / Dispresiyon Lak Maliyeti
    selofan_m2 = tabaka_adeti * 0.35
    if laminasyon == "Mat Selofan":
        selofan_maliyeti = selofan_m2 * st.session_state.params['mat_sel']
    elif laminasyon == "Parlak Selofan":
        selofan_maliyeti = selofan_m2 * st.session_state.params['par_sel']
    elif laminasyon == "Dispresiyon Lak":
        selofan_maliyeti = st.session_state.params['disp_5070'] + (adet * st.session_state.params['disp_5070_tiraj'] / 1000)
    else:
        selofan_maliyeti = 0

    # Kesim Maliyeti Hesaplama
    kesim_maliyeti = 0
    if kesim == "Bobst Kesim":
        kesim_maliyeti = st.session_state.params['bobst'] + (adet * st.session_state.params['bobst_tiraj'])
    elif kesim == "Kazanlı Kesim":
        kesim_maliyeti = st.session_state.params['kazanli'] + (adet * st.session_state.params['kazanli_tiraj'])
    elif kesim == "Pedal Kesim":
        kesim_maliyeti = st.session_state.params['pedal'] + (adet * st.session_state.params['pedal_tiraj'])

    yapistirma_maliyeti = (st.session_state.params['omega_dip'] + (adet * st.session_state.params['omega_dip_tiraj'])) if yapistirma else 0
    nakliye_maliyeti = 4000.0 if nakliye else 0
    toplam_ek = yapistirma_maliyeti + nakliye_maliyeti

    toplam_maliyet = kagit_maliyeti + baski_maliyeti + selofan_maliyeti + kesim_maliyeti + toplam_ek
    net_kar = toplam_maliyet * (kar_orani / 100)
    toplam_karli_fiyat = toplam_maliyet + net_kar
    birim_maliyet = toplam_maliyet / adet if adet > 0 else 0
    karli_birim_fiyat = toplam_karli_fiyat / adet if adet > 0 else 0

    st.markdown("---")
    st.subheader("📊 Maliyet ve Teklif Özeti")
    
    r1, r2, r3 = st.columns(3)
    r1.metric("Kağıt Miktarı", f"{kg_kagit} kg")
    r2.metric("Tabaka Adedi", f"{tabaka_adeti:,} tabaka")
    r3.metric("Baskı Maliyeti", f"₺{baski_maliyeti:,.2f}")

    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Maliyet", f"₺{toplam_maliyet:,.2f}")
    m2.metric("Net Kar", f"₺{net_kar:,.2f}")
    m3.metric("Karlı Satış Fiyatı", f"₺{toplam_karli_fiyat:,.2f}")

    b1, b2 = st.columns(2)
    b1.metric("Birim Maliyet", f"₺{birim_maliyet:,.4f}")
    b2.metric("Karlı Birim Satış Fiyatı", f"₺{karli_birim_fiyat:,.4f}")
