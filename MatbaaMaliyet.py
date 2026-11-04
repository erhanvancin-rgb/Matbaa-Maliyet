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
# MENÜ 3: FORM VE HESAPLAMA MODÜLÜ
# ==========================================
if st.session_state.page == 'calc':
    def hesapla_maliyet_detayli(
        net_adet, gramaj, kagit_cinsi, baski_yuzu, pantone_sayisi, 
        laminasyon, ozel_baski_1, ozel_baski_2, baski_sonrasi, 
        kagit_adi, makine_kodu, tab_en_mm, tab_boy_mm, makas_payi_mm, 
        montaj_adedi, fire_orani_override, ebat_en, ebat_boy, ebat_yukseklik
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
        
        tab_en = tab_en_mm / 1000.0
        tab_boy = tab_boy_mm / 1000.0

        revolta_uygun_kagit = kagit_cinsi in ["Kuşe Kağıt", "1. Hamur Kağıt"]
        
        # --- REVOLTA KURALI ---
        gercek_baski_yuzu = baski_yuzu
        if baski_yuzu in ["Çift Yüz", "Ön ve Arka Baskı"]:
            if revolta_uygun_kagit and (montaj_adedi % 2 == 0):
                gercek_baski_yuzu = "Revolta Baskı"
            else:
                gercek_baski_yuzu = "Çift Yüz (Normal)"

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

        b_cmyk_base = params.get(f"b_{makine_kodu}_cmyk", 2400.0)
        b_pantone_base = params.get(f"b_{makine_kodu}_pantone", 1200.0)
        b_tiraj_rate = params.get(f"b_{makine_kodu}_tiraj", 500.0)

        baski_vurus = tabaka_adeti
        if gercek_baski_yuzu == "Revolta Baskı":
            baski_vurus = tabaka_adeti * 2
            fazla_vurus = max(0, baski_vurus - 2000)
            baski_maliyeti = b_cmyk_base + (fazla_vurus / 1000.0) * b_tiraj_rate
        elif gercek_baski_yuzu in ["Çift Yüz", "Ön ve Arka Baskı", "Çift Yüz (Normal)"]:
            fazla_vurus = max(0, baski_vurus - 2000)
            baski_maliyeti = (b_cmyk_base + (fazla_vurus / 1000.0) * b_tiraj_rate) * 1.8
        elif gercek_baski_yuzu in ["Tek Yüz", "Tek Yüz Baskı"]:
            fazla_vurus = max(0, baski_vurus - 2000)
            baski_maliyeti = b_cmyk_base + (fazla_vurus / 1000.0) * b_tiraj_rate
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
            disp_base = params['disp_5070'] if makine_kodu != "70100" else params['disp_70100']
            disp_tiraj = params['disp_5070_tiraj'] if makine_kodu != "70100" else params['disp_70100_tiraj']
            disp_limit = 1000 if makine_kodu != "70100" else 2000
            selofan_maliyeti = disp_base + max(0, (tabaka_adeti - disp_limit) / 1000.0) * disp_tiraj

        ozel_baski_maliyeti = 0.0
        for ob in [ozel_baski_1, ozel_baski_2]:
            if ob != "Yok":
                if "Lokal Lak" in ob:
                    l_base = params['lokal_5070'] if makine_kodu != "70100" else params['lokal_70100']
                    l_rate = params['lokal_5070_tiraj'] if makine_kodu != "70100" else params['lokal_70100_tiraj']
                    ozel_baski_maliyeti += l_base + max(0, tabaka_adeti - 1000) * l_rate
                elif "Kabartma Lak" in ob:
                    k_base = params['kab_5070'] if makine_kodu != "70100" else params['kab_70100']
                    k_rate = params['kab_5070_tiraj'] if makine_kodu != "70100" else params['kab_70100_tiraj']
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
            "gercek_baski_yuzu": gercek_baski_yuzu,
            "makine_kodu": makine_kodu
        }

    st.subheader("📋 Ürün Tanımlama & Maliyet Hesaplama Formu")
    st.markdown("---")

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
        net_a = st.number_input("Ürün Adedi A", value=10000, step=1000, key="net_a")
    with col_r2_2:
        net_b = st.number_input("Ürün Adedi B", value=20000, step=1000, key="net_b")
    with col_r2_3:
        net_c = st.number_input("Ürün Adedi C", value=50000, step=1000, key="net_c")

    col_ka_head, col_kb_head = st.columns(2)
    with col_ka_head:
        ca_g, ca_c = st.columns(2)
        with ca_g:
            gramaj_a = st.number_input("Gramaj A (gr/m²)", value=170, step=10, min_value=50, key="gramaj_a")
        with ca_c:
            kagit_cinsi_a = st.selectbox("Kağıt Cinsi A", ["Kuşe Kağıt", "Amerikan Bristol", "Krome Karton", "1. Hamur Kağıt"], key="kagit_cinsi_a")
            
    with col_kb_head:
        cb_g, cb_c = st.columns(2)
        with cb_g:
            gramaj_b = st.number_input("Gramaj B (Opsiyonel)", value=350, step=10, min_value=50, key="gramaj_b")
        with cb_c:
            kagit_cinsi_b = st.selectbox("Kağıt Cinsi B", ["Yok / Kullanma", "Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"], key="kagit_cinsi_b")

    ikinci_kagit_var = kagit_cinsi_b != "Yok / Kullanma"

    col_ebat1, col_ebat2, col_ebat3, col_baski1, col_baski2 = st.columns(5)
    with col_ebat1:
        ebat_en = st.number_input("En (mm)", value=240, key="ebat_en")
    with col_ebat2:
        ebat_boy = st.number_input("Boy (mm)", value=110, key="ebat_boy")
    with col_ebat3:
        ebat_yukseklik = st.number_input("Yükseklik (mm)", value=0, key="ebat_yukseklik")
    with col_baski1:
        cmyk_secim = st.selectbox("Baskı CMYK", ["Çift Yüz", "Tek Yüz", "CMYK Baskı yok"], key="cmyk_secim")
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

    def fiziksel_montaj_bul(tw, th, w, h, makas):
        if tw > th:
            tw, th = th, tw 
        best_m = 0
        for (pw, ph) in [(w, h), (h, w)]:
            if tw > makas:
                best_m = max(best_m, math.floor((tw - makas) / pw) * math.floor(th / ph))
            if th > makas:
                best_m = max(best_m, math.floor(tw / pw) * math.floor((th - makas) / ph))
        return best_m

    # BÜYÜK OYUN: YENİ NESİL MAKİNE-KAĞIT SAVAŞTIRMA DÖNGÜSÜ
    def en_ekonomik_makineyi_bul(adet, gramaj, kagit):
        aday_kagitlar = []
        
        if kagit in ["Kuşe Kağıt", "1. Hamur Kağıt"]:
            # 1. 70x100 Ailesi
            aday_kagitlar.append(("70x100 cm Kağıt (70x100 Makine)", 700.0, 1000.0, "70100", 15.0))
            aday_kagitlar.append(("50x70 cm Kağıt (50x70 Makine)", 500.0, 700.0, "5070", 12.0))
            aday_kagitlar.append(("35x50 cm Kağıt (35x50 Makine)", 350.0, 500.0, "3550", 10.0))
            
            # 2. 64x90 Ailesi
            aday_kagitlar.append(("64x90 cm Kağıt (70x100 Makine)", 640.0, 900.0, "70100", 15.0))
            aday_kagitlar.append(("45x64 cm Kağıt (50x70 Makine)", 450.0, 640.0, "5070", 12.0))
            aday_kagitlar.append(("32x45 cm Kağıt (35x50 Makine)", 320.0, 450.0, "3550", 10.0))

            # 3. 57x82 Ailesi (Sadece gramaj <= 170g ise çalışır!)
            if gramaj <= 170:
                aday_kagitlar.append(("57x82 cm Kağıt (70x100 Makine)", 570.0, 820.0, "70100", 15.0))
                aday_kagitlar.append(("41x57 cm Kağıt (50x70 Makine)", 410.0, 570.0, "5070", 12.0))
                aday_kagitlar.append(("28.5x41 cm Kağıt (35x50 Makine)", 285.0, 410.0, "3550", 10.0))
                
        else: # Amerikan Bristol veya Krome Karton
            aday_kagitlar.append(("70x100 cm Kağıt (Standart)", 700.0, 1000.0, "70100", 15.0))
            aday_kagitlar.append(("50x70 cm Kağıt (Standart)", 500.0, 700.0, "5070", 12.0))
            aday_kagitlar.append(("35x50 cm Kağıt (Standart)", 350.0, 500.0, "3550", 10.0))
            
            # Özel Bobin Ebatları (5cm'nin katları) - Min 30x30'dan Max 70x100'e kadar tüm olasılıklar
            for w_cm in range(30, 75, 5):
                for h_cm in range(w_cm, 105, 5):
                    if (w_cm, h_cm) not in [(35,50), (50,70), (70,100)]:
                        if w_cm <= 35 and h_cm <= 50:
                            makine_k, makas_k = "3550", 10.0
                        elif w_cm <= 50 and h_cm <= 70:
                            makine_k, makas_k = "5070", 12.0
                        elif w_cm <= 70 and h_cm <= 100:
                            makine_k, makas_k = "70100", 15.0
                        else:
                            continue
                        aday_kagitlar.append((f"{w_cm}x{h_cm} cm (Özel Bobin Ebat)", float(w_cm*10), float(h_cm*10), makine_k, makas_k))

        en_iyi_sonuc = None
        en_dusuk_maliyet = float('inf')
        w_bleed = ebat_en + 4.0
        h_bleed = ebat_boy + 4.0

        for kagit_adi, tw, th, makine_kodu, makas in aday_kagitlar:
            montaj = fiziksel_montaj_bul(tw, th, w_bleed, h_bleed, makas)
            if montaj <= 0: continue

            res = hesapla_maliyet_detayli(
                adet, gramaj, kagit, cmyk_secim, pantone_sayisi, 
                laminasyon, ozel_baski_1, ozel_baski_2, baski_sonrasi, 
                kagit_adi, makine_kodu, tw, th, makas, montaj, 0.0, ebat_en, ebat_boy, ebat_yukseklik
            )
            
            # KARTON/BRISTOL ÖZEL KURALI: Bobinden özel ebat kesilmesi için işin toplam kağıt ağırlığı >= 600kg olmalı
            if "Özel Bobin Ebat" in kagit_adi and res['kg_kagit'] < 600:
                continue
                
            maliyet = res['toplam_uretim_maliyeti']
            if maliyet < en_dusuk_maliyet:
                en_dusuk_maliyet = maliyet
                
                if adet <= 1500: fire = 10.0
                elif adet <= 3000: fire = 7.0
                else: fire = 5.0
                
                en_iyi_sonuc = {'adet': adet, 'gramaj': gramaj, 'kagit': kagit, 'fire': fire, 'ebat': kagit_adi, 'res': res}

        if en_iyi_sonuc is None:
            # Fallback (Hiçbiri tutmazsa Standart 50x70 ile maliyet ver)
            res = hesapla_maliyet_detayli(adet, gramaj, kagit, cmyk_secim, pantone_sayisi, laminasyon, ozel_baski_1, ozel_baski_2, baski_sonrasi, "50x70 cm (Standart)", "5070", 500.0, 700.0, 12.0, 1, 0.0, ebat_en, ebat_boy, ebat_yukseklik)
            en_iyi_sonuc = {'adet': adet, 'gramaj': gramaj, 'kagit': kagit, 'fire': 5.0, 'ebat': "50x70 cm (Standart)", 'res': res}

        return en_iyi_sonuc

    plan_params = []
    plan_params.append({**en_ekonomik_makineyi_bul(net_a, gramaj_a, kagit_cinsi_a), 'kod': 'A'})
    plan_params.append({**en_ekonomik_makineyi_bul(net_b, gramaj_a, kagit_cinsi_a), 'kod': 'B'})
    plan_params.append({**en_ekonomik_makineyi_bul(net_c, gramaj_a, kagit_cinsi_a), 'kod': 'C'})

    if ikinci_kagit_var:
        plan_params.append({**en_ekonomik_makineyi_bul(net_a, gramaj_b, kagit_cinsi_b), 'kod': 'A2'})
        plan_params.append({**en_ekonomik_makineyi_bul(net_b, gramaj_b, kagit_cinsi_b), 'kod': 'B2'})
        plan_params.append({**en_ekonomik_makineyi_bul(net_c, gramaj_b, kagit_cinsi_b), 'kod': 'C2'})

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
        "pantone_sayisi": pantone_sayisi,
        "laminasyon": laminasyon,
        "baski_sonrasi": baski_sonrasi,
        "ozel_baski": ozel_baski_ozet,
        "ozel_istekler": ozel_istekler,
        "kar_orani": kar_orani,
        "alternatifler": teklif_alternatifleri
    }

    st.markdown("### 📊 ÜRETİM VE PLANLAMA ÖZETİ (GELİŞMİŞ KAĞIT OPTİMİZASYONU)")

    def plan_kartini_yazdir(p):
        r = p['res']
        net_kullanici_adeti = p['adet']
        
        st.markdown(f"**Kağıt & Adet:** {net_kullanici_adeti:,} adet - {p['gramaj']}g {p['kagit']}")
        
        plan_df = pd.DataFrame([
            {"Parametre / Kriter": "Fire Oranı (%)", "Değer": f"%{r['fire_pct']:.1f}"},
            {"Parametre / Kriter": "Brüt Adet", "Değer": f"{r['brut_adet']:,} adet"},
            {"Parametre / Kriter": "Montaj Planı", "Değer": f"1 Tabakada {r['montaj_adedi']} Ürün"},
            {"Parametre / Kriter": "Kullanılan Kağıt (Makine)", "Değer": p['ebat']},
            {"Parametre / Kriter": "Kağıt Kilogram (kg)", "Değer": f"{r['kg_kagit']} kg"},
            {"Parametre / Kriter": "Baskı Adedi Ön Ve Arka", "Değer": f"{r['tabaka_adeti']:,} tabaka"},
            {"Parametre / Kriter": "Baskı Metodu", "Değer": r['gercek_baski_yuzu']},
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
            "<p style='margin: 2px 0 0 0;'><strong>Tarih:</strong> 04 Kasım 2026 | <strong>Teklif No:</strong> OFF-2026-8492</p>"
            "</div>", 
            unsafe_allow_html=True
        )
        
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
                "Tabaka Ebadı": alt['ebat'],
                "Kağıt Ağırlığı": f"{res['kg_kagit']} kg",
                "Birim Satış Fiyatı (TL)": f"₺{birim_satis_tl:,.4f}",
                "Karlı Toplam Tutar (TL)": f"₺{toplam_satis_tl:,.2f}"
            })

        df_teklif = pd.DataFrame(table_rows)
        st.dataframe(df_teklif, use_container_width=True, hide_index=True)
