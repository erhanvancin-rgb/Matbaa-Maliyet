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

# --- 3. ÜST GEZİNTİ BUTONLARI ---
st.markdown("### 🖨️ MATBAAM PRO - Ambalaj & Matbaa Maliyet ve Teklif Sistemi")
st.info(f"🏦 TCMB Anlık Efektif Satış Kurları — USD: ₺{canli_usd:.2f} | EUR: ₺{canli_eur:.2f}")

nav_c1, nav_c2, nav_c3, nav_c4 = st.columns(4)
with nav_c1:
    if st.button("🏠 1. Ana Menü", use_container_width=True, type="primary" if st.session_state.page == 'home' else "secondary"):
        go_page('home')
        st.rerun()
with nav_c2:
    if st.button("⚙️ 2. Parametreler (37 Kalem)", use_container_width=True, type="primary" if st.session_state.page == 'params' else "secondary"):
        go_page('params')
        st.rerun()
with nav_c3:
    if st.button("📋 3. Fiyat Çıkart (Form)", use_container_width=True, type="primary" if st.session_state.page == 'calc' else "secondary"):
        go_page('calc')
        st.rerun()
with nav_c4:
    if st.button("📄 4. Müşteri Fiyat Teklifi", use_container_width=True, type="primary" if st.session_state.page == 'teklif' else "secondary"):
        go_page('teklif')
        st.rerun()

st.markdown("---")

# ==========================================
# MENÜ 1 & 2: ANA SAYFA VE PARAMETRELER
# ==========================================
if st.session_state.page == 'home':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>Yönetim & Hesaplama Modülü</h2><br>", unsafe_allow_html=True)
        if st.button("1. Parametreler (Fiyat Listesi Yönetimi - 37 Kalem)", use_container_width=True): go_page('params'); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("2. Fiyat Çıkart (Maliyet Hesaplama Formu)", use_container_width=True): go_page('calc'); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("3. 📄 Müşteri Fiyat Teklifi Mektubu ve Tablosu", use_container_width=True): go_page('teklif'); st.rerun()

elif st.session_state.page == 'params':
    st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi")
    # ... (Aynı parametre ayar formu)
    if st.button("Forma Dön", key="btn_p2c"): go_page('calc'); st.rerun()

# ==========================================
# MENÜ 3: PÜR MATEMATİKSEL HESAPLAMA MODÜLÜ
# ==========================================
elif st.session_state.page == 'calc':
    st.subheader("📋 Ürün Tanımlama & Maliyet Hesaplama Formu")
    st.markdown("---")

    col_r1_1, col_r1_2, col_r1_3 = st.columns(3)
    with col_r1_1: firma_adi = st.text_input("Firma Adı", "Erhan Ticaret")
    with col_r1_2: urun_adi = st.text_input("Ürün Adı", "Kutu / Ambalaj Üretimi")
    with col_r1_3:
        urun_tipi = st.selectbox("Ürün Tipi", ["Föy", "Kartonet", "Poster", "Etiket", "Standart Kutu", "Dip Kilitli Kutu", "Dip Kilit Yapıştırmalı Kutu"])

    is_kutu = "Kutu" in urun_tipi

    col_r2_1, col_r2_2, col_r2_3 = st.columns(3)
    with col_r2_1: net_a = st.number_input("Ürün Adedi A", value=1000, step=100)
    with col_r2_2: net_b = st.number_input("Ürün Adedi B", value=2000, step=100)
    with col_r2_3: net_c = st.number_input("Ürün Adedi C", value=25000, step=100)

    col_ka_head, col_kb_head = st.columns(2)
    with col_ka_head:
        ca_g, ca_c = st.columns(2)
        with ca_g: gramaj_a = st.number_input("Gramaj A (gr/m²)", value=350, step=10, min_value=50)
        with ca_c: kagit_cinsi_a = st.selectbox("Kağıt Cinsi A", ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"])
    with col_kb_head:
        cb_g, cb_c = st.columns(2)
        with cb_g: gramaj_b = st.number_input("Gramaj B (Opsiyonel)", value=400, step=10, min_value=50)
        with cb_c: kagit_cinsi_b = st.selectbox("Kağıt Cinsi B", ["Yok / Kullanma", "Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"])

    ikinci_kagit_var = kagit_cinsi_b != "Yok / Kullanma"

    col_ebat1, col_ebat2, col_ebat3, col_baski1, col_baski2 = st.columns(5)
    with col_ebat1: ebat_en = st.number_input("En (mm) [A]", value=100)
    with col_ebat2: ebat_boy = st.number_input("Boy (mm) [B]", value=150)
    with col_ebat3: ebat_yukseklik = st.number_input("Yükseklik (mm) [C]", value=50.0 if is_kutu else 0.0, disabled=not is_kutu)
    with col_baski1: cmyk_secim = st.selectbox("Baskı CMYK", ["Tek Yüz", "Ön&Arka", "CMYK Baskı yok"])
    with col_baski2: pantone_secimi = st.selectbox("Baskı Pantone renk sayısı", ["Yok", "1 renk zemin", "2 renk lokal", "1 renk zemin (Ön&Arka)"])

    c_lam, c_ob1, c_bs = st.columns(3)
    with c_lam: laminasyon = st.selectbox("Laminasyon", ["Parlak Selofan", "Mat Selofan", "Dispersiyon Lak", "Yok"])
    with c_ob1: ozel_baski_1 = st.selectbox("Özel İşlem", ["Yok", "Lokal Lak", "Kabartma Lak", "Varak Yaldız"])
    with c_bs: baski_sonrasi = st.selectbox("Baskı Sonrası", ["Düz Kesim", "Özel kesim", "Kutu Kesim + Yapıştırma"])

    st.markdown("---")

    def kademeli_fire_hesapla(baski_tabaka_sayisi):
        kalan = baski_tabaka_sayisi
        fire = 0.0
        if kalan > 0: d = min(kalan, 1000); fire += 100.0; kalan -= d
        if kalan > 0: d = min(kalan, 1000); fire += d * 0.05; kalan -= d
        if kalan > 0: d = min(kalan, 1000); fire += d * 0.04; kalan -= d
        if kalan > 0: d = min(kalan, 1000); fire += d * 0.03; kalan -= d
        if kalan > 0: fire += kalan * 0.02
        return math.ceil(fire)

    def get_machine_code(w, h):
        max_dim, min_dim = max(w, h), min(w, h)
        if max_dim > 1020 or min_dim > 720: return None # Makine sınırını aşanları eler
        if min_dim < 250: return None # A4 altı aşırı küçükleri eler (makine tutamaz)
        if max_dim <= 500 and min_dim <= 350: return "3550"
        elif max_dim <= 700 and min_dim <= 500: return "5070"
        else: return "70100"

    def get_makas(machine_code):
        if machine_code == "70100": return 15.0
        elif machine_code == "5070": return 12.0
        else: return 10.0

    # PÜR MATEMATİKSEL BOBİN VE TABAKA ÜRETİCİSİ (Sinir Tanımaz)
    def bobin_adaylarini_uret():
        cands = []
        enler = list(range(550, 1001, 50)) # 55, 60, 65... 100 cm
        boylar = list(range(500, 1001, 10)) # Kesim 50'den 100'e 1cm adımlarla
        
        for e in enler:
            for b in boylar:
                ana_w, ana_h = float(e), float(b)
                ana_isim = f"Bobin Kesim {int(e//10)}x{int(b//10)} cm"
                
                # Bobin tabakasını X ve Y yönünde limitsiz matematikle böl 
                # (1x1, 1x2, 2x1, 2x2, 3x3 vb.. oranlar kendiliğinden doğar)
                for x_div in range(1, 6):
                    for y_div in range(1, 6):
                        bolunme_orani = x_div * y_div
                        alt_w = ana_w / x_div
                        alt_h = ana_h / y_div
                        
                        mc = get_machine_code(alt_w, alt_h)
                        if mc: # Eğer çıkan parça makine ebadına uyuyorsa, yarışmaya dahil et
                            ebat_str = f"{alt_w/10:.1f}x{alt_h/10:.1f} cm".replace(".0", "")
                            cands.append((ana_isim, ebat_str, ana_w, ana_h, alt_w, alt_h, mc, get_makas(mc), bolunme_orani))
        return cands

    def icsel_planla_ve_hesapla(net_adet, gramaj, kagit):
        params = st.session_state.params
        
        # Net Kesim Alanı Hesaplama
        if is_kutu:
            acinin_en = ((ebat_en * 2) + (ebat_yukseklik * 2)) + 15.0
            acinin_boy = (ebat_boy + (ebat_yukseklik * 2)) + 30.0
        else:
            acinin_en = ebat_en + 3.0
            acinin_boy = ebat_boy + 3.0

        standart_adaylar = [
            ("70x100 cm", "70x100 cm", 700.0, 1000.0, 700.0, 1000.0, get_machine_code(700.0, 1000.0), get_makas(get_machine_code(700.0, 1000.0)), 1),
            ("70x100 cm", "50x70 cm", 700.0, 1000.0, 500.0, 700.0, get_machine_code(500.0, 700.0), get_makas(get_machine_code(500.0, 700.0)), 2),
            ("70x100 cm", "35x50 cm", 700.0, 1000.0, 350.0, 500.0, get_machine_code(350.0, 500.0), get_makas(get_machine_code(350.0, 500.0)), 4),
        ]

        en_iyi_secim = None
        min_maliyet = float('inf')

        def adaylari_degerlendir(aday_listesi):
            nonlocal en_iyi_secim, min_maliyet
            for ana_tabaka, baski_ebat_adi, ana_w, ana_h, tw, th, makine_kodu, makas, bolunme_orani in aday_listesi:
                avail_w = tw - makas
                avail_h = th
                
                # PÜR MATEMATİKSEL MONTAJ: Kısıtlı diziler söküldü, alan bazlı net sığdırma (geometri)
                s1_w = int(avail_w // acinin_en)
                s1_h = int(avail_h // acinin_boy)
                m1 = s1_w * s1_h
                
                s2_w = int(avail_w // acinin_boy)
                s2_h = int(avail_h // acinin_en)
                m2 = s2_w * s2_h
                
                montaj = max(m1, m2)

                if montaj <= 0: continue

                net_baski_tabaka = math.ceil(net_adet / montaj)
                fire_tabaka = kademeli_fire_hesapla(net_baski_tabaka)
                brut_baski_tabaka = net_baski_tabaka + fire_tabaka
                if brut_baski_tabaka < 100: brut_baski_tabaka = 100

                tabaka_adeti = math.ceil(brut_baski_tabaka / bolunme_orani)
                if tabaka_adeti < 50: tabaka_adeti = 50

                baskiya_giren_tabaka = tabaka_adeti * bolunme_orani
                toplam_m2 = round(tabaka_adeti * (ana_w/1000.0) * (ana_h/1000.0), 2)
                kg_kagit = round((toplam_m2 * gramaj) / 1000.0, 2)

                ton_fiyat = params['bristol'] * canli_usd # Default
                if kagit == "Krome Karton": ton_fiyat = params['krome']
                elif kagit == "Kuşe Kağıt": ton_fiyat = params['kuse'] * canli_eur
                elif kagit == "1. Hamur Kağıt": ton_fiyat = params['hamur'] * canli_usd

                kagit_maliyeti = (kg_kagit / 1000.0) * ton_fiyat
                b_cmyk = params.get(f"b_{makine_kodu}_cmyk", 3500.0)
                b_tiraj = params.get(f"b_{makine_kodu}_tiraj", 800.0)
                fazla_vurus = max(0, baskiya_giren_tabaka - 2000)
                baski_maliyeti = b_cmyk + (fazla_vurus / 1000.0) * b_tiraj
                toplam_maliyet = kagit_maliyeti + baski_maliyeti + 400.0

                brut_adet = baskiya_giren_tabaka * montaj
                fire_pct_ortalama = round((fire_tabaka / max(1, net_baski_tabaka)) * 100.0, 1)

                if toplam_maliyet < min_maliyet:
                    min_maliyet = toplam_maliyet
                    en_iyi_secim = {
                        "brut_adet": brut_adet, "fire_pct": fire_pct_ortalama, "fire_tabaka": fire_tabaka,
                        "montaj_adedi": montaj, "tabaka_adeti": tabaka_adeti, "baskiya_giren_tabaka": baskiya_giren_tabaka,
                        "ana_ebat": ana_tabaka, "baski_ebat_str": baski_ebat_adi, "toplam_m2": toplam_m2,
                        "kg_kagit": kg_kagit, "kagit_maliyeti": kagit_maliyeti, "baski_maliyeti": baski_maliyeti,
                        "toplam_uretim_maliyeti": toplam_maliyet, "makine_kodu": makine_kodu
                    }
                # Aynı maliyetteyse kağıdı en verimli kullananı (en az kg) seç
                elif abs(toplam_maliyet - min_maliyet) < 1.0:
                    if kg_kagit < en_iyi_secim['kg_kagit']:
                        min_maliyet = toplam_maliyet
                        en_iyi_secim = {
                            "brut_adet": brut_adet, "fire_pct": fire_pct_ortalama, "fire_tabaka": fire_tabaka,
                            "montaj_adedi": montaj, "tabaka_adeti": tabaka_adeti, "baskiya_giren_tabaka": baskiya_giren_tabaka,
                            "ana_ebat": ana_tabaka, "baski_ebat_str": baski_ebat_adi, "toplam_m2": toplam_m2,
                            "kg_kagit": kg_kagit, "kagit_maliyeti": kagit_maliyeti, "baski_maliyeti": baski_maliyeti,
                            "toplam_uretim_maliyeti": toplam_maliyet, "makine_kodu": makine_kodu
                        }

        # 1. Standartlar
        adaylari_degerlendir(standart_adaylar)

        # 2. Dinamik Matematiksel Bobin Havuzu (Sadece ağırlık 600kg üstüyse bobin kesime değer)
        geici_kg = en_iyi_secim['kg_kagit'] if en_iyi_secim else 0.0
        if (kagit in ["Amerikan Bristol", "Krome Karton"]) and geici_kg >= 600.0:
            adaylari_degerlendir(bobin_adaylarini_uret())

        return en_iyi_secim

    plan_params = []
    res_a = icsel_planla_ve_hesapla(net_a, gramaj_a, kagit_cinsi_a)
    res_b = icsel_planla_ve_hesapla(net_b, gramaj_a, kagit_cinsi_a)
    res_c = icsel_planla_ve_hesapla(net_c, gramaj_a, kagit_cinsi_a)
    plan_params.extend([{'adet': net_a, 'gramaj': gramaj_a, 'kagit': kagit_cinsi_a, 'res': res_a, 'kod': 'A'},
                        {'adet': net_b, 'gramaj': gramaj_a, 'kagit': kagit_cinsi_a, 'res': res_b, 'kod': 'B'},
                        {'adet': net_c, 'gramaj': gramaj_a, 'kagit': kagit_cinsi_a, 'res': res_c, 'kod': 'C'}])

    kar_orani = st.slider("Hedef Kar Marjı (%)", 0, 100, 30)
    
    st.session_state.teklif_data = {
        "firma_adi": firma_adi, "urun_adi": urun_adi, "urun_tipi": urun_tipi,
        "ebat_en": ebat_en, "ebat_boy": ebat_boy, "ebat_yukseklik": ebat_yukseklik,
        "cmyk_secim": cmyk_secim, "pantone_secimi": pantone_secimi,
        "laminasyon": laminasyon, "baski_sonrasi": baski_sonrasi,
        "ozel_baski": ozel_baski_1, "kar_orani": kar_orani, "alternatifler": plan_params
    }

    st.markdown("### 📊 ÜRETİM VE PLANLAMA ÖZETİ (PÜR MATEMATİKSEL ZEKÂ)")

    def plan_kartini_yazdir(p):
        r = p['res']
        st.markdown(f"**{p['adet']:,} adet - {p['gramaj']}g {p['kagit']}**")
        
        baski_metodu_str = "Tek Yüz" if cmyk_secim == "Tek Yüz" else "Ön&Arka"
        
        plan_df = pd.DataFrame([
            {"Parametre": "Montaj", "Değer": f"1 Tabakada {r['montaj_adedi']} Ürün"},
            {"Parametre": "Ana Tabaka Ebadı", "Değer": f"{r['ana_ebat']} - {r['tabaka_adeti']:,} Tabaka"},
            {"Parametre": "Baskı Ebadı", "Değer": f"{r['baski_ebat_str']} - {r['baskiya_giren_tabaka']:,} Tabaka"},
            {"Parametre": "Kağıt Ağırlığı", "Değer": f"{r['kg_kagit']} kg"},
            {"Parametre": "Üretim Maliyeti", "Değer": f"₺{r['toplam_uretim_maliyeti']:,.2f}"}
        ])
        st.table(plan_df)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("##### Alternatif A"); plan_kartini_yazdir(plan_params[0])
    with c2: st.markdown("##### Alternatif B"); plan_kartini_yazdir(plan_params[1])
    with c3: st.markdown("##### Alternatif C"); plan_kartini_yazdir(plan_params[2])

    st.markdown("---")
    if st.button("📄 Müşteri Teklifine Git", use_container_width=True): go_page('teklif'); st.rerun()

# ==========================================
# MENÜ 4: MÜŞTERİ FİYAT TEKLİFİ
# ==========================================
elif st.session_state.page == 'teklif':
    st.subheader("📄 Müşteri Fiyat Teklifi ve Ürün Şartnamesi")
    if not st.session_state.teklif_data:
        st.warning("⚠️ Henüz hesaplama yapılmadı.")
    else:
        td = st.session_state.teklif_data
        st.markdown(f"<div style='background-color: #f8f9fa; padding: 20px; border-left: 5px solid #1F4E78;'>"
                    f"<h3 style='margin: 0; color: #1F4E78;'>FİYAT TEKLİF MEKTUBU</h3>"
                    f"<p><strong>Sayın:</strong> {td['firma_adi']}</p></div><br>", unsafe_allow_html=True)
        
        table_rows = []
        for alt in td['alternatifler']:
            res = alt['res']
            satis = res['toplam_uretim_maliyeti'] * (1 + td['kar_orani']/100.0)
            table_rows.append({
                "Adet": f"{alt['adet']:,}", "Kağıt": f"{alt['gramaj']}g {alt['kagit']}",
                "Ebat": res['ana_ebat'], "Birim Fiyat": f"₺{(satis/alt['adet']):.4f}", "Toplam": f"₺{satis:,.2f}"
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
