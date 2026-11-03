import streamlit as st
import xml.etree.ElementTree as ET
import urllib.request

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

def render_urun_bilgileri_ve_maliyetlendirme():
    canli_usd, canli_eur = tcmb_kurlarini_getir()

    # Varsayılan Parametre Yönetimi
    if 'params' not in st.session_state:
        st.session_state.params = {
            'bristol': 825.0, 'krome': 40000.0, 'kuse': 850.0, 'hamur': 1200.0,
            'b_3550_cmyk': 1800.0, 'b_3550_pantone': 900.0, 'b_3550_tiraj': 400.0,
            'b_5070_cmyk': 3500.0, 'b_5070_pantone': 1750.0, 'b_5070_tiraj': 800.0,
            'b_70100_cmyk': 5000.0, 'b_70100_pantone': 1750.0, 'b_70100_tiraj': 1400.0,
            'mat_sel': 4.70, 'par_sel': 4.50, 'disp_5070': 1500.0, 'disp_5070_tiraj': 800.0,
            'lokal_5070': 1500.0, 'lokal_5070_tiraj': 1.5, 'kab_5070': 1600.0, 'kab_5070_tiraj': 1.6,
            'kazanli': 1800.0, 'kazanli_tiraj': 0.75, 'bobst': 3000.0, 'bobst_tiraj': 1.5,
            'omega_dip': 2500.0, 'omega_dip_tiraj': 0.25
        }

    st.subheader("📋 Ürün Bilgileri ve Maliyet Hesaplama Formu")
    st.markdown(f"🏦 *Anlık Kur Bilgisi — USD: ₺{canli_usd:.2f} | EUR: ₺{canli_eur:.2f}*")
    st.markdown("---")

    # 1. Firma ve Ürün Genel Bilgileri
    col1, col2 = st.columns(2)
    with col1:
        firma_adi = st.text_input("Firma Adı", "Erhan Ticaret", key="form_firma")
    with col2:
        urun_adi = st.text_input("Ürün Adı", "Lüks Ambalaj Kutusu", key="form_urun_adi")

    # 2. Ürün Tipi Listesi
    urun_tipleri = [
        "Föy", "Tek Kırımlı Broşür", "İki Kırımlı Broşür", 
        "Kartonet", "Kutu", "Sıvamalı Kutu", "Etiket", "Prospektüs"
    ]
    urun_tipi = st.selectbox("Ürün Tipi", urun_tipleri, key="form_urun_tipi")

    st.markdown("---")

    # 3. Ürün Adedi A, B, C
    st.markdown("##### 🔢 Ürün Adedi (Tiraj Seçenekleri)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        adet_a = st.number_input("Adet A", value=1000, step=500, key="form_adet_a")
    with col_b:
        adet_b = st.number_input("Adet B", value=3000, step=500, key="form_adet_b")
    with col_c:
        adet_c = st.number_input("Adet C", value=5000, step=500, key="form_adet_c")

    st.markdown("---")

    # 4. Kağıt Gramajı ve Cinsi (Ana ve Alternatif B)
    kagit_listesi = ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"]
    gramaj_listesi = [200, 250, 300, 350, 400]

    st.markdown("##### 📄 Kağıt ve Malzeme Seçimi")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        st.markdown("**Kağıt Cinsi ve Gramajı (Ana)**")
        kagit_a = st.selectbox("Kağıt Cinsi A", kagit_listesi, key="form_kagit_a")
        gramaj_a = st.selectbox("Gramaj A", gramaj_listesi, index=2, key="form_gramaj_a")
    with col_k2:
        st.markdown("**Kağıt Cinsi ve Gramajı Alternatif B**")
        kagit_b = st.selectbox("Kağıt Cinsi B", kagit_listesi, key="form_kagit_b")
        gramaj_b = st.selectbox("Gramaj B", gramaj_listesi, index=2, key="form_gramaj_b")

    st.markdown("---")

    # 5. Baskı CMYK ve Pantone Renk Sayısı
    col_bc1, col_bc2 = st.columns(2)
    with col_bc1:
        baski_cmyk = st.selectbox("Baskı CMYK", ["Tek Yüz", "Çift Yüz", "CMYK Baskı Yok"], key="form_baski_cmyk")
    with col_bc2:
        pantone_sayisi = st.selectbox("Baskı Pantone Renk Sayısı", [
            "Yok", "1 renk zemin", "2 renk zemin", "3 renk zemin", "4 renk zemin", 
            "1 renk lokal", "2 renk lokal", "3 renk lokal", "4 renk lokal"
        ], key="form_pantone_sayisi")

    st.markdown("---")

    # 6. Ebat Bilgileri (En x Boy x Yükseklik)
    st.markdown("##### 📐 Bitmiş Ebat (mm)")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        ebat_en = st.number_input("En (mm)", value=200, key="form_ebat_en")
    with col_e2:
        ebat_boy = st.number_input("Boy (mm)", value=150, key="form_ebat_boy")
    with col_e3:
        ebat_yukseklik = st.number_input("Yükseklik (mm)", value=50, key="form_ebat_yukseklik")

    st.markdown("---")

    # 7. Laminasyon ve Özel Baskılar
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        laminasyon = st.selectbox("Laminasyon", ["Parlak Selofan", "Mat Selofan", "Dispresiyon Lak", "Yok"], key="form_laminasyon")
        ozel_baski_1 = st.selectbox("Özel Baskılar 1", ["Yok", "Lokal Lak", "Kabartma Lak", "Gofre", "Varak Yaldız"], key="form_ozel_baski_1")
    with col_l2:
        ozel_baski_2 = st.selectbox("Özel Baskılar 2", ["Yok", "Lokal Lak", "Kabartma Lak", "Gofre", "Varak Yaldız"], key="form_ozel_baski_2")
        baski_sonrasi = st.selectbox("Baskı Sonrası", ["Düz Kesim", "Özel Kesim", "Kutu Kesim + Yapıştırma"], key="form_baski_sonrasi")

    st.markdown("---")

    # 8. Özel İstekler
    ozel_istekler = st.text_area("Özel İstekler", placeholder="Müşteriye özel ek talepler...", key="form_ozel_istekler")

    st.markdown("---")
    st.markdown("### 📊 Maliyet ve Fiyatlandırma Bölümü (A Adet Bazlı)")
    
    kar_orani = st.slider("Hedef Kar Marjı (%)", 0, 100, 30, key="form_kar_orani")

    # --- HESAPLAMA MOTORU (Adet A Üzerinden) ---
    params = st.session_state.params
    ton_fiyat = params['bristol']
    birim_tip = 'USD'
    if kagit_a == "Amerikan Bristol": ton_fiyat, birim_tip = params['bristol'], 'USD'
    elif kagit_a == "Krome Karton": ton_fiyat, birim_tip = params['krome'], 'TL'
    elif kagit_a == "Kuşe Kağıt": ton_fiyat, birim_tip = params['kuse'], 'EUR'
    elif kagit_a == "1. Hamur Kağıt": ton_fiyat, birim_tip = params['hamur'], 'USD'

    ton_fiyat_tl = ton_fiyat
    if birim_tip == 'USD': ton_fiyat_tl = ton_fiyat * canli_usd
    elif birim_tip == 'EUR': ton_fiyat_tl = ton_fiyat * canli_eur

    tabaka_adeti = max(1, adet_a // 2)
    kg_kagit = round((tabaka_adeti * (ebat_en/1000) * (ebat_boy/1000) * gramaj_a) / 2)
    kagit_maliyeti = (kg_kagit / 1000) * ton_fiyat_tl

    baski_maliyeti = params['b_5070_cmyk'] + (adet_a * params['b_5070_tiraj'] / 1000)
    if baski_cmyk == "Çift Yüz":
        baski_maliyeti *= 1.8
    elif baski_cmyk == "CMYK Baskı Yok":
        baski_maliyeti = 0

    selofan_m2 = tabaka_adeti * 0.35
    selofan_maliyeti = 0
    if laminasyon == "Mat Selofan": selofan_maliyeti = selofan_m2 * params['mat_sel']
    elif laminasyon == "Parlak Selofan": selofan_maliyeti = selofan_m2 * params['par_sel']
    elif laminasyon == "Dispresiyon Lak": selofan_maliyeti = params['disp_5070'] + (adet_a * params['disp_5070_tiraj'] / 1000)

    kesim_maliyeti = 0
    if baski_sonrasi == "Özel Kesim": kesim_maliyeti = params['bobst'] + (adet_a * params['bobst_tiraj'])
    elif baski_sonrasi == "Kutu Kesim + Yapıştırma": kesim_maliyeti = params['kazanli'] + (adet_a * params['kazanli_tiraj']) + params['omega_dip'] + (adet_a * params['omega_dip_tiraj'])

    toplam_maliyet = kagit_maliyeti + baski_maliyeti + selofan_maliyeti + kesim_maliyeti
    net_kar = toplam_maliyet * (kar_orani / 100)
    toplam_karli_fiyat = toplam_maliyet + net_kar
    birim_maliyet = toplam_maliyet / adet_a if adet_a > 0 else 0
    karli_birim_fiyat = toplam_karli_fiyat / adet_a if adet_a > 0 else 0

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

if __name__ == "__main__":
    render_urun_bilgileri_ve_maliyetlendirme()
