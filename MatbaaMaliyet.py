import streamlit as st
import xml.etree.ElementTree as ET
import urllib.request
import math
import pandas as pd
import json
import os
from math import ceil
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Rect:
    width_mm: float
    height_mm: float


@dataclass(frozen=True)
class Machine:
    name: str
    max_width_mm: float
    max_height_mm: float
    setup_cost: float | None
    run_cost_per_1000: float | None

    def fits(self, sheet: Rect) -> bool:
        return (
            (sheet.width_mm <= self.max_width_mm and sheet.height_mm <= self.max_height_mm)
            or (sheet.height_mm <= self.max_width_mm and sheet.width_mm <= self.max_height_mm)
        )


def box_blank_size(
    width_mm: float,
    length_mm: float,
    height_mm: float,
    style: str = "standard",
    row_count: int = 1,
    column_count: int = 1,
) -> Rect:
    """Kullanıcının verdiği kutu açınım ölçüleri; bıçak çizimi yerine geçmez."""
    if min(width_mm, length_mm) <= 0 or height_mm < 0 or row_count < 1 or column_count < 1:
        raise ValueError("Ürün ölçüleri pozitif, sıra/sütun sayısı en az 1 olmalıdır.")

    blank_width = (width_mm * 2 + height_mm * 2 + 15) * column_count

    if style == "standard":
        blank_height = (length_mm + height_mm + 15) * row_count + height_mm + 15
    elif style in {"dip_kilit", "dip_yapistirmali"}:
        blank_height = (
            length_mm + height_mm + 15 + (height_mm / 2 + 15) * 2
        ) * row_count

        if row_count in {1, 3, 5, 6, 7, 9, 10, 11}:
            blank_height += height_mm + 15
    else:
        raise ValueError("Bilinmeyen kutu tipi.")

    return Rect(blank_width, blank_height)


def best_box_montage(
    sheet: Rect,
    width_mm: float,
    length_mm: float,
    height_mm: float,
    style: str = "standard",
    max_rows: int = 12,
    max_columns: int = 4,
) -> dict:
    """Satır/sütun kombinasyonları ve iki yönelim arasında kutu verimini arar."""
    best = {
        "count": 0,
        "product_count": 0,
        "rows": 0,
        "columns": 0,
        "blank": None,
    }

    for rows in range(1, max_rows + 1):
        for columns in range(1, max_columns + 1):
            blank = box_blank_size(
                width_mm, length_mm, height_mm, style, rows, columns
            )
            groups = rectangular_imposition(sheet, blank, gap_mm=0)
            products = groups * rows * columns

            if (
                products > best["count"]
                or (
                    products == best["count"]
                    and rows * columns > best["rows"] * best["columns"]
                )
            ):
                best = {
                    "count": products,
                    "product_count": products,
                    "rows": rows,
                    "columns": columns,
                    "blank": blank,
                }

    return best


def bobin_cutting_allowed(paper_name: str, paper_kg: float) -> bool:
    return paper_name in {"Amerikan Bristol", "Krome Karton"} and paper_kg > 600.0


def rectangular_imposition(sheet: Rect, product: Rect, gap_mm: float = 3.0) -> int:
    """Dikdörtgen ürün için iki yönelimin ızgara verimini hesaplar."""
    if min(sheet.width_mm, sheet.height_mm, product.width_mm, product.height_mm) <= 0:
        return 0

    def count(w: float, h: float) -> int:
        across = int((sheet.width_mm + gap_mm) // (w + gap_mm))
        down = int((sheet.height_mm + gap_mm) // (h + gap_mm))
        return across * down

    return max(
        count(product.width_mm, product.height_mm),
        count(product.height_mm, product.width_mm),
    )


def score_candidate(
    *,
    stock: Rect,
    press_sheet: Rect,
    product: Rect,
    quantity: int,
    gsm: float,
    paper_ton_cost: float,
    press: Machine,
    cutter: Machine,
    stock_sheets_per_press: int = 1,
    box_blank: bool = False,
    gap_mm: float = 3.0,
) -> dict | None:
    """Kapasite ve tarife verilmiş adayın maliyetini hesaplar."""
    if (
        quantity <= 0
        or gsm <= 0
        or stock_sheets_per_press < 1
        or not press.fits(press_sheet)
        or not cutter.fits(stock)
    ):
        return None

    yield_per_sheet = rectangular_imposition(press_sheet, product, gap_mm)
    if yield_per_sheet == 0:
        return None

    press_sheets = ceil(quantity / yield_per_sheet)
    stock_sheets = ceil(press_sheets / stock_sheets_per_press)

    area_m2 = stock.width_mm * stock.height_mm / 1_000_000
    kg = stock_sheets * area_m2 * gsm / 1000
    paper_cost = kg / 1000 * paper_ton_cost

    if (
        press.setup_cost is None
        or press.run_cost_per_1000 is None
        or cutter.setup_cost is None
        or cutter.run_cost_per_1000 is None
    ):
        press_cost = cutter_cost = total = None
    else:
        press_cost = press.setup_cost + max(0, press_sheets - 2000) / 1000 * press.run_cost_per_1000
        cutter_cost = cutter.setup_cost + stock_sheets / 1000 * cutter.run_cost_per_1000
        total = paper_cost + press_cost + cutter_cost

    return {
        "stock_sheets": stock_sheets,
        "press_sheets": press_sheets,
        "yield_per_sheet": yield_per_sheet,
        "kg": kg,
        "paper_cost": paper_cost,
        "press_cost": press_cost,
        "cutter_cost": cutter_cost,
        "total_cost": total,
        "press": press.name,
        "cutter": cutter.name,
        "die_line_validation_required": box_blank,
    }


def recommend(candidates: Iterable[dict]) -> dict[str, dict | None]:
    """En düşük maliyet, en az kâğıt ve dengeli planı ayrı seçer."""
    rows = list(candidates)
    priced = [row for row in rows if row.get("total_cost") is not None]

    return {
        "lowest_total_cost": min(
            priced,
            key=lambda row: row["total_cost"],
            default=None,
        ),
        "lowest_paper_use": min(
            rows,
            key=lambda row: row["kg"],
            default=None,
        ),
        "balanced": min(
            priced,
            key=lambda row: (
                row["kg"] / max(1.0, max(item["kg"] for item in priced))
                + row["total_cost"] / max(1.0, max(item["total_cost"] for item in priced))
            ) / 2,
            default=None,
        ),
    }


st.set_page_config(
    page_title="Matbaa ve Ambalaj Maliyet & Teklif Sistemi",
    layout="wide",
)

# --- 0. KALICI JSON PARAMETRE YÖNETİMİ VE STATE SENKRONİZASYONU ---
PARAM_FILE = "matbaa_parametreleri.json"

default_params = {
    "bristol": 825.0,
    "krome": 40000.0,
    "kuse": 850.0,
    "hamur": 1200.0,
    "b_3550_cmyk": 2400.0,
    "b_3550_pantone": 1200.0,
    "b_3550_tiraj": 500.0,
    "b_5070_cmyk": 3500.0,
    "b_5070_pantone": 1750.0,
    "b_5070_tiraj": 800.0,
    "b_70100_cmyk": 5000.0,
    "b_70100_pantone": 1750.0,
    "b_70100_tiraj": 1400.0,
    "disp_5070": 1500.0,
    "disp_5070_tiraj": 800.0,
    "disp_70100": 2000.0,
    "disp_70100_tiraj": 1000.0,
    "mat_sel": 4.70,
    "par_sel": 4.50,
    "lokal_5070": 1500.0,
    "lokal_5070_tiraj": 1.5,
    "lokal_70100": 1800.0,
    "lokal_70100_tiraj": 1.5,
    "kab_5070": 1600.0,
    "kab_5070_tiraj": 1.6,
    "kab_70100": 1900.0,
    "kab_70100_tiraj": 1.9,
    "kazanli": 1800.0,
    "kazanli_tiraj": 0.75,
    "pedal": 2500.0,
    "pedal_tiraj": 1.0,
    "bobst": 3000.0,
    "bobst_tiraj": 1.5,
    "omega_tek": 2000.0,
    "omega_tek_tiraj": 0.2,
    "omega_dip": 2500.0,
    "omega_dip_tiraj": 0.25,
}


def parametreleri_yukle():
    if os.path.exists(PARAM_FILE):
        try:
            with open(PARAM_FILE, "r", encoding="utf-8") as file:
                kayitli = json.load(file)
                for key, value in default_params.items():
                    if key not in kayitli:
                        kayitli[key] = value
                return kayitli
        except Exception:
            return default_params.copy()

    return default_params.copy()


def parametreleri_kaydet(params_dict):
    try:
        with open(PARAM_FILE, "w", encoding="utf-8") as file:
            json.dump(params_dict, file, ensure_ascii=False, indent=4)
    except Exception:
        pass


if "params" not in st.session_state:
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

        for currency in root.findall("Currency"):
            code = currency.get("CurrencyCode")
            if code == "USD":
                val = currency.find("BanknoteSelling").text
                if val:
                    usd_kur = float(val)
            elif code == "EUR":
                val = currency.find("BanknoteSelling").text
                if val:
                    eur_kur = float(val)
    except Exception:
        pass

    return usd_kur, eur_kur


canli_usd, canli_eur = tcmb_kurlarini_getir()


# --- 2. OTURUM DURUMU ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "teklif_data" not in st.session_state:
    st.session_state.teklif_data = None


def go_page(page_name):
    st.session_state.page = page_name


# --- 3. ÜST GEZİNTİ VE NAVİGASYON BARI ---
st.markdown("## 🖨️ MATBAAM PRO - Ambalaj & Matbaa Maliyet ve Teklif Sistemi")
st.info(
    f"🏦 TCMB Anlık Efektif Satış Kurları — USD: ₺{canli_usd:.2f} | EUR: ₺{canli_eur:.2f}"
)

nav_c1, nav_c2, nav_c3, nav_c4 = st.columns(4)
with nav_c1:
    type_a = "primary" if st.session_state.page == "home" else "secondary"
    if st.button("🏠 1. Ana Menü", use_container_width=True, type=type_a):
        go_page("home")
        st.rerun()
with nav_c2:
    type_b = "primary" if st.session_state.page == "params" else "secondary"
    if st.button("⚙️ 2. Parametreler (37 Kalem)", use_container_width=True, type=type_b):
        go_page("params")
        st.rerun()
with nav_c3:
    type_c = "primary" if st.session_state.page == "calc" else "secondary"
    if st.button("📋 3. Fiyat Çıkart (Form)", use_container_width=True, type=type_c):
        go_page("calc")
        st.rerun()
with nav_c4:
    type_d = "primary" if st.session_state.page == "teklif" else "secondary"
    if st.button("📄 4. Müşteri Fiyat Teklifi", use_container_width=True, type=type_d):
        go_page("teklif")
        st.rerun()

st.markdown("---")


# ==========================================
# MENÜ 1: ANA SAYFA
# ==========================================
if st.session_state.page == "home":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<h2 style='text-align: center;'>Yönetim & Hesaplama Modülü</h2><br>",
            unsafe_allow_html=True,
        )
        if st.button(
            "1. Parametreler (Fiyat Listesi Yönetimi)",
            use_container_width=True,
        ):
            go_page("params")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "2. Fiyat Çıkart (Maliyet Hesaplama Formu)",
            use_container_width=True,
        ):
            go_page("calc")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "3. 📄 Müşteri Fiyat Teklifi Mektubu",
            use_container_width=True,
        ):
            go_page("teklif")
            st.rerun()


# ==========================================
# MENÜ 2: PARAMETRELER SAYFASI
# ==========================================
elif st.session_state.page == "params":
    st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 1. Kağıt ve Karton Grubu (Ton Maliyetleri)")
        st.session_state.params["bristol"] = st.number_input(
            "Amerikan Bristol Ton ($ USD)",
            value=float(st.session_state.params["bristol"]),
        )
        st.session_state.params["krome"] = st.number_input(
            "Krome Karton Ton (TL)",
            value=float(st.session_state.params["krome"]),
        )
        st.session_state.params["kuse"] = st.number_input(
            "Kuşe Ton (€ EUR)",
            value=float(st.session_state.params["kuse"]),
        )
        st.session_state.params["hamur"] = st.number_input(
            "1. Hamur Ton ($ USD)",
            value=float(st.session_state.params["hamur"]),
        )

        st.markdown("---")
        st.markdown("#### 2. Baskı Grubu")
        st.session_state.params["b_3550_cmyk"] = st.number_input(
            "35x50 CMYK Hazırlık (₺)",
            value=float(st.session_state.params["b_3550_cmyk"]),
        )
        st.session_state.params["b_3550_pantone"] = st.number_input(
            "35x50 Pantone 1 Renk (₺)",
            value=float(st.session_state.params["b_3550_pantone"]),
        )
        st.session_state.params["b_3550_tiraj"] = st.number_input(
            "35x50 Tiraj (1.000 Adet/₺)",
            value=float(st.session_state.params["b_3550_tiraj"]),
        )
        st.session_state.params["b_5070_cmyk"] = st.number_input(
            "50x70 CMYK Hazırlık (₺)",
            value=float(st.session_state.params["b_5070_cmyk"]),
        )
        st.session_state.params["b_5070_pantone"] = st.number_input(
            "50x70 Pantone 1 Renk (₺)",
            value=float(st.session_state.params["b_5070_pantone"]),
        )
        st.session_state.params["b_5070_tiraj"] = st.number_input(
            "50x70 Tiraj (1.000 Adet/₺)",
            value=float(st.session_state.params["b_5070_tiraj"]),
        )
        st.session_state.params["b_70100_cmyk"] = st.number_input(
            "70x100 CMYK Hazırlık (₺)",
            value=float(st.session_state.params["b_70100_cmyk"]),
        )
        st.session_state.params["b_70100_pantone"] = st.number_input(
            "70x100 Pantone 1 Renk (₺)",
            value=float(st.session_state.params["b_70100_pantone"]),
        )
        st.session_state.params["b_70100_tiraj"] = st.number_input(
            "70x100 Tiraj (1.000 Adet/₺)",
            value=float(st.session_state.params["b_70100_tiraj"]),
        )

    with col2:
        st.markdown("#### 3. Yüzey İşlemleri ve Kesim Grubu")
        st.session_state.params["mat_sel"] = st.number_input(
            "Mat Selofan M2 (₺)",
            value=float(st.session_state.params["mat_sel"]),
        )
        st.session_state.params["par_sel"] = st.number_input(
            "Parlak Selofan M2 (₺)",
            value=float(st.session_state.params["par_sel"]),
        )
        st.session_state.params["kazanli"] = st.number_input(
            "Kazanlı Kesim Hazırlık (₺)",
            value=float(st.session_state.params["kazanli"]),
        )
        st.session_state.params["kazanli_tiraj"] = st.number_input(
            "Kazanlı Kesim Tiraj (Adet/₺)",
            value=float(st.session_state.params["kazanli_tiraj"]),
        )
        st.session_state.params["bobst"] = st.number_input(
            "Bobst Otomatik Kesim Hazırlık (₺)",
            value=float(st.session_state.params["bobst"]),
        )
        st.session_state.params["bobst_tiraj"] = st.number_input(
            "Bobst Kesim Tiraj (Adet/₺)",
            value=float(st.session_state.params["bobst_tiraj"]),
        )
        st.session_state.params["omega_tek"] = st.number_input(
            "Omega Tek Kulak Yapıştırma (₺)",
            value=float(st.session_state.params["omega_tek"]),
        )
        st.session_state.params["omega_tek_tiraj"] = st.number_input(
            "Omega Tek Kulak Tiraj (₺)",
            value=float(st.session_state.params["omega_tek_tiraj"]),
        )

    parametreleri_kaydet(st.session_state.params)
    st.success("💾 Tüm parametre değişiklikleri kalıcı olarak kaydedildi.")


# ==========================================
# MENÜ 3: FORM VE AKILLI DİNAMİK HESAPLAMA
# ==========================================
elif st.session_state.page == "calc":
    st.subheader("📋 Ürün Tanımlama & Maliyet Hesaplama Formu")
    st.markdown("---")

    col_r1_1, col_r1_2, col_r1_3 = st.columns(3)
    with col_r1_1:
        firma_adi = st.text_input("Firma Adı", "Erhan Ticaret")
    with col_r1_2:
        urun_adi = st.text_input("Ürün Adı", "Kutu / Ambalaj Üretimi")
    with col_r1_3:
        urun_tipleri = [
            "Föy",
            "Kartonet",
            "Poster",
            "Etiket",
            "Standart Kutu",
            "Dip Kilitli Kutu",
            "Dip Kilit Yapıştırmalı Kutu",
        ]
        urun_tipi = st.selectbox("Ürün Tipi", urun_tipleri)

    is_kutu = "Kutu" in urun_tipi
    is_dip_kilit = urun_tipi in [
        "Dip Kilitli Kutu",
        "Dip Kilit Yapıştırmalı Kutu",
    ]

    col_r2_1, col_r2_2, col_r2_3 = st.columns(3)
    with col_r2_1:
        net_a = st.number_input("Ürün Adedi A", value=1000, step=100)
    with col_r2_2:
        net_b = st.number_input("Ürün Adedi B", value=5000, step=100)
    with col_r2_3:
        net_c = st.number_input("Ürün Adedi C", value=25000, step=100)

    col_ka_head, col_kb_head = st.columns(2)
    with col_ka_head:
        ca_g, ca_c = st.columns(2)
        with ca_g:
            gramaj_a = st.number_input("Gramaj A (gr/m²)", value=350, step=10, min_value=50)
        with ca_c:
            kagit_cinsi_a = st.selectbox(
                "Kağıt Cinsi A",
                ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"],
            )

    with col_kb_head:
        cb_g, cb_c = st.columns(2)
        with cb_g:
            gramaj_b = st.number_input("Gramaj B (Opsiyonel)", value=400, step=10, min_value=50)
        with cb_c:
            kagit_cinsi_b = st.selectbox(
                "Kağıt Cinsi B",
                [
                    "Yok / Kullanma",
                    "Amerikan Bristol",
                    "Krome Karton",
                    "Kuşe Kağıt",
                    "1. Hamur Kağıt",
                ],
            )

    ikinci_kagit_var = kagit_cinsi_b != "Yok / Kullanma"

    col_ebat1, col_ebat2, col_ebat3, col_baski1, col_baski2 = st.columns(5)
    with col_ebat1:
        ebat_en = st.number_input("En (mm) [A]", value=100)
    with col_ebat2:
        ebat_boy = st.number_input("Boy (mm) [B]", value=150)
    with col_ebat3:
        ebat_yukseklik = st.number_input(
            "Yükseklik (mm) [C]",
            value=50.0 if is_kutu else 0.0,
            disabled=not is_kutu,
        )

    if is_dip_kilit:
        sira_sayisi = st.selectbox(
            "Dip kilit ürün sıra sayısı",
            list(range(1, 13)),
            index=0,
        )
    else:
        sira_sayisi = 1

    with col_baski1:
        cmyk_secim = st.selectbox(
            "Baskı CMYK",
            ["Tek Yüz", "Ön&Arka", "CMYK Baskı yok"],
        )
    with col_baski2:
        pantone_secimi = st.selectbox(
            "Baskı Pantone renk",
            ["Yok", "1 renk zemin", "2 renk zemin", "1 renk lokal"],
        )

    c_lam, c_ob1, c_ob2, c_bs = st.columns(4)
    with c_lam:
        laminasyon = st.selectbox(
            "Laminasyon",
            ["Parlak Selofan", "Mat Selofan", "Yok"],
        )
    with c_ob1:
        ozel_baski_1 = st.selectbox(
            "Özel Baskılar 1",
            ["Yok", "Lokal Lak", "Kabartma Lak", "Varak Yaldız"],
        )
    with c_ob2:
        ozel_baski_2 = st.selectbox(
            "Özel Baskılar 2",
            ["Yok", "Lokal Lak", "Kabartma Lak", "Varak Yaldız"],
        )
    with c_bs:
        baski_sonrasi = st.selectbox(
            "Baskı Sonrası",
            ["Düz Kesim", "Özel kesim", "Kutu Kesim + Yapıştırma"],
        )

    ozel_istekler = st.text_input(
        "Özel İstekler",
        "",
        placeholder="Özel talepleri buraya yazınız...",
    )

    st.markdown("---")

    def kademeli_fire_hesapla(baski_tabaka_sayisi):
        kalan = baski_tabaka_sayisi
        fire = 0.0

        if kalan > 0:
            d = min(kalan, 1000)
            fire += 100.0
            kalan -= d
        if kalan > 0:
            d = min(kalan, 1000)
            fire += d * 0.05
            kalan -= d
        if kalan > 0:
            d = min(kalan, 1000)
            fire += d * 0.04
            kalan -= d
        if kalan > 0:
            d = min(kalan, 1000)
            fire += d * 0.03
            kalan -= d
        if kalan > 0:
            fire += kalan * 0.02

        return math.ceil(fire)

    def get_machine_code(w, h):
        max_dim, min_dim = max(w, h), min(w, h)

        if max_dim > 1020 or min_dim > 720:
            return None
        if min_dim < 230:
            return None
        if max_dim <= 500 and min_dim <= 350:
            return "3550"
        if max_dim <= 700 and min_dim <= 500:
            return "5070"
        return "70100"

    def get_makas(machine_code):
        if machine_code == "70100":
            return 15.0
        if machine_code == "5070":
            return 12.0
        return 10.0

    # Kutu montajı formüllerle hesaplanır; gerçek bıçak çizimi ayrıca doğrulanmalıdır.
    def akilli_montaj_hesapla(w_avail, h_avail, ebat_en, ebat_boy, ebat_yuk):
        if not is_kutu:
            w_net = ebat_en + 3.0
            h_net = ebat_boy + 3.0
            blank = Rect(w_net, h_net)
            return {
                "count": rectangular_imposition(Rect(w_avail, h_avail), blank),
                "rows": 1,
                "columns": 1,
                "blank": blank,
            }

        if is_dip_kilit:
            kutu_tipi = (
                "dip_kilit"
                if urun_tipi == "Dip Kilitli Kutu"
                else "dip_yapistirmali"
            )
            blank = box_blank_size(
                ebat_en,
                ebat_boy,
                ebat_yuk,
                kutu_tipi,
                sira_sayisi,
            )
            grid_count = rectangular_imposition(
                Rect(w_avail, h_avail),
                blank,
            )
            return {
                "count": grid_count * sira_sayisi,
                "rows": sira_sayisi,
                "columns": 1,
                "blank": blank,
            }

        return best_box_montage(
            Rect(w_avail, h_avail),
            ebat_en,
            ebat_boy,
            ebat_yuk,
        )

    # Bobin kesim adayları 5 cm aralıklarla üretilir.
    def bobin_adaylarini_uret():
        cands = []
        enler = list(range(550, 1050, 50))
        boylar = list(range(500, 1050, 50))

        for e in enler:
            for b in boylar:
                ana_w, ana_h = float(e), float(b)
                ana_isim = f"Bobin Kesim {ana_w / 10:g}x{ana_h / 10:g} cm"

                mc1 = get_machine_code(ana_w, ana_h)
                if mc1:
                    cands.append(
                        (
                            ana_isim,
                            f"{ana_w / 10:g}x{ana_h / 10:g} cm",
                            ana_w,
                            ana_h,
                            ana_w,
                            ana_h,
                            mc1,
                            get_makas(mc1),
                            1,
                        )
                    )

                w2, h2 = ana_w / 2, ana_h
                mc2 = get_machine_code(w2, h2)
                if mc2:
                    cands.append(
                        (
                            ana_isim,
                            f"{w2 / 10:g}x{h2 / 10:g} cm",
                            ana_w,
                            ana_h,
                            w2,
                            h2,
                            mc2,
                            get_makas(mc2),
                            2,
                        )
                    )

        return cands

    # Üretim adaylarını kâğıt ve baskı maliyetiyle karşılaştırır.
    def icsel_planla_ve_hesapla(net_adet, gramaj, kagit):
        params = st.session_state.params
        is_karton = kagit in ["Amerikan Bristol", "Krome Karton"]

        standart_adaylar = [
            (
                "70x100 cm", "70x100 cm", 700.0, 1000.0, 700.0, 1000.0,
                get_machine_code(700.0, 1000.0),
                get_makas(get_machine_code(700.0, 1000.0)), 1,
            ),
            (
                "70x100 cm", "50x70 cm", 700.0, 1000.0, 500.0, 700.0,
                get_machine_code(500.0, 700.0),
                get_makas(get_machine_code(500.0, 700.0)), 2,
            ),
            (
                "70x100 cm", "33.3x70 cm", 700.0, 1000.0, 333.3, 700.0,
                get_machine_code(333.3, 700.0),
                get_makas(get_machine_code(333.3, 700.0)), 3,
            ),
            (
                "70x100 cm", "35x50 cm", 700.0, 1000.0, 350.0, 500.0,
                get_machine_code(350.0, 500.0),
                get_makas(get_machine_code(350.0, 500.0)), 4,
            ),
            (
                "70x100 cm", "33.3x35 cm", 700.0, 1000.0, 333.3, 350.0,
                get_machine_code(333.3, 350.0),
                get_makas(get_machine_code(333.3, 350.0)), 6,
            ),
            (
                "70x100 cm", "25x35 cm", 700.0, 1000.0, 250.0, 350.0,
                get_machine_code(250.0, 350.0),
                get_makas(get_machine_code(250.0, 350.0)), 8,
            ),
        ]

        if not is_karton:
            standart_adaylar.extend(
                [
                    (
                        "64x90 cm", "64x90 cm", 640.0, 900.0, 640.0, 900.0,
                        get_machine_code(640.0, 900.0),
                        get_makas(get_machine_code(640.0, 900.0)), 1,
                    ),
                    (
                        "64x90 cm", "45x64 cm", 640.0, 900.0, 450.0, 640.0,
                        get_machine_code(450.0, 640.0),
                        get_makas(get_machine_code(450.0, 640.0)), 2,
                    ),
                    (
                        "64x90 cm", "32x45 cm", 640.0, 900.0, 320.0, 450.0,
                        get_machine_code(320.0, 450.0),
                        get_makas(get_machine_code(320.0, 450.0)), 4,
                    ),
                ]
            )

        en_iyi_secim = None
        min_maliyet = float("inf")
        aday_sonuclari = []

        def adaylari_degerlendir(aday_listesi):
            nonlocal en_iyi_secim, min_maliyet

            for (
                ana_tabaka,
                baski_ebat_adi,
                ana_w,
                ana_h,
                tw,
                th,
                makine_kodu,
                makas,
                bolunme_orani,
            ) in aday_listesi:
                avail_w = tw - makas
                avail_h = th

                montaj_plan = akilli_montaj_hesapla(
                    avail_w,
                    avail_h,
                    ebat_en,
                    ebat_boy,
                    ebat_yukseklik,
                )
                montaj = montaj_plan["count"]

                if montaj <= 0:
                    continue

                blank = montaj_plan["blank"]
                montaj_detay = (
                    f"{montaj_plan['columns']} sütun × {montaj_plan['rows']} sıra; "
                    f"modül {blank.width_mm:g}×{blank.height_mm:g} mm"
                )

                net_baski_tabaka = math.ceil(net_adet / montaj)
                fire_tabaka = kademeli_fire_hesapla(net_baski_tabaka)
                brut_baski_tabaka = net_baski_tabaka + fire_tabaka
                brut_baski_tabaka = max(100, brut_baski_tabaka)

                tabaka_adeti = math.ceil(brut_baski_tabaka / bolunme_orani)
                tabaka_adeti = max(50, tabaka_adeti)
                baskiya_giren_tabaka_adeti = tabaka_adeti * bolunme_orani

                tab_en = ana_w / 1000.0
                tab_boy = ana_h / 1000.0
                toplam_m2 = round(tabaka_adeti * tab_en * tab_boy, 2)
                kg_kagit = round((toplam_m2 * gramaj) / 1000.0, 2)

                if kagit == "Amerikan Bristol":
                    ton_fiyat = params["bristol"] * canli_usd
                elif kagit == "Krome Karton":
                    ton_fiyat = params["krome"]
                elif kagit == "Kuşe Kağıt":
                    ton_fiyat = params["kuse"] * canli_eur
                else:
                    ton_fiyat = params["hamur"] * canli_usd

                kagit_maliyeti = (kg_kagit / 1000.0) * ton_fiyat
                b_cmyk = params.get(f"b_{makine_kodu}_cmyk", 3500.0)
                b_tiraj = params.get(f"b_{makine_kodu}_tiraj", 800.0)
                fazla_vurus = max(0, baskiya_giren_tabaka_adeti - 2000)
                baski_maliyeti = b_cmyk + (fazla_vurus / 1000.0) * b_tiraj

                # Kesim ve diğer işlemlerin gerçek tarifesi modele eklenmediği için
                # burada tahmini sabit bir kesim bedeli kullanılmıyor.
                toplam_maliyet = kagit_maliyeti + baski_maliyeti

                aday_sonuclari.append(
                    {
                        "ana_ebat": ana_tabaka,
                        "baski_ebat_str": baski_ebat_adi,
                        "montaj_adedi": montaj,
                        "kg": kg_kagit,
                        "kagit_maliyeti": kagit_maliyeti,
                        "baski_maliyeti": baski_maliyeti,
                        "total_cost": toplam_maliyet,
                        "makine_kodu": makine_kodu,
                        "tabaka_adeti": tabaka_adeti,
                        "montaj_detay": montaj_detay,
                    }
                )

                brut_adet = baskiya_giren_tabaka_adeti * montaj
                fire_pct_ortalama = round(
                    fire_tabaka / max(1, net_baski_tabaka) * 100.0,
                    1,
                )

                if toplam_maliyet < min_maliyet:
                    min_maliyet = toplam_maliyet
                    en_iyi_secim = {
                        "brut_adet": brut_adet,
                        "fire_pct": fire_pct_ortalama,
                        "fire_tabaka": fire_tabaka,
                        "montaj_adedi": montaj,
                        "montaj_detay": montaj_detay,
                        "tabaka_adeti": tabaka_adeti,
                        "baskiya_giren_tabaka": baskiya_giren_tabaka_adeti,
                        "ana_ebat": ana_tabaka,
                        "baski_ebat_str": baski_ebat_adi,
                        "toplam_m2": toplam_m2,
                        "kg_kagit": kg_kagit,
                        "kagit_maliyeti": kagit_maliyeti,
                        "baski_maliyeti": baski_maliyeti,
                        "toplam_uretim_maliyeti": toplam_maliyet,
                        "makine_kodu": makine_kodu,
                        "kesim_maliyeti_dahil": False,
                        "geometri_dogrulama_gerekli": is_kutu,
                    }
                elif abs(toplam_maliyet - min_maliyet) < 1.0:
                    if kg_kagit < en_iyi_secim["kg_kagit"]:
                        min_maliyet = toplam_maliyet
                        en_iyi_secim = {
                            "brut_adet": brut_adet,
                            "fire_pct": fire_pct_ortalama,
                            "fire_tabaka": fire_tabaka,
                            "montaj_adedi": montaj,
                            "montaj_detay": montaj_detay,
                            "tabaka_adeti": tabaka_adeti,
                            "baskiya_giren_tabaka": baskiya_giren_tabaka_adeti,
                            "ana_ebat": ana_tabaka,
                            "baski_ebat_str": baski_ebat_adi,
                            "toplam_m2": toplam_m2,
                            "kg_kagit": kg_kagit,
                            "kagit_maliyeti": kagit_maliyeti,
                            "baski_maliyeti": baski_maliyeti,
                            "toplam_uretim_maliyeti": toplam_maliyet,
                            "makine_kodu": makine_kodu,
                            "kesim_maliyeti_dahil": False,
                            "geometri_dogrulama_gerekli": is_kutu,
                        }

        adaylari_degerlendir(standart_adaylar)

        gecici_kg = en_iyi_secim["kg_kagit"] if en_iyi_secim else 0.0
        if bobin_cutting_allowed(kagit, gecici_kg):
            adaylari_degerlendir(bobin_adaylarini_uret())

        if en_iyi_secim is None:
            raise ValueError(
                "Bu ebat ve makine sınırlarıyla uygun üretim planı bulunamadı."
            )

        en_iyi_secim["oneriler"] = recommend(aday_sonuclari)
        return en_iyi_secim

    plan_params = []
    res_a = icsel_planla_ve_hesapla(net_a, gramaj_a, kagit_cinsi_a)
    res_b = icsel_planla_ve_hesapla(net_b, gramaj_a, kagit_cinsi_a)
    res_c = icsel_planla_ve_hesapla(net_c, gramaj_a, kagit_cinsi_a)

    plan_params.append(
        {"adet": net_a, "gramaj": gramaj_a, "kagit": kagit_cinsi_a, "res": res_a, "kod": "A"}
    )
    plan_params.append(
        {"adet": net_b, "gramaj": gramaj_a, "kagit": kagit_cinsi_a, "res": res_b, "kod": "B"}
    )
    plan_params.append(
        {"adet": net_c, "gramaj": gramaj_a, "kagit": kagit_cinsi_a, "res": res_c, "kod": "C"}
    )

    if ikinci_kagit_var:
        res_a2 = icsel_planla_ve_hesapla(net_a, gramaj_b, kagit_cinsi_b)
        res_b2 = icsel_planla_ve_hesapla(net_b, gramaj_b, kagit_cinsi_b)
        res_c2 = icsel_planla_ve_hesapla(net_c, gramaj_b, kagit_cinsi_b)

        plan_params.append(
            {"adet": net_a, "gramaj": gramaj_b, "kagit": kagit_cinsi_b, "res": res_a2, "kod": "A2"}
        )
        plan_params.append(
            {"adet": net_b, "gramaj": gramaj_b, "kagit": kagit_cinsi_b, "res": res_b2, "kod": "B2"}
        )
        plan_params.append(
            {"adet": net_c, "gramaj": gramaj_b, "kagit": kagit_cinsi_b, "res": res_c2, "kod": "C2"}
        )

    kar_orani = st.slider("Hedef Kar Marjı (%)", 0, 100, 30)
    teklif_alternatifleri = [plan for plan in plan_params]
    ozel_baski_ozet = ", ".join(
        [item for item in [ozel_baski_1, ozel_baski_2] if item != "Yok"]
    ) or "Yok"

    st.session_state.teklif_data = {
        "firma_adi": firma_adi,
        "urun_adi": urun_adi,
        "urun_tipi": urun_tipi,
        "ebat_en": ebat_en,
        "ebat_boy": ebat_boy,
        "ebat_yukseklik": ebat_yukseklik,
        "sira_sayisi": sira_sayisi,
        "cmyk_secim": cmyk_secim,
        "pantone_secimi": pantone_secimi,
        "laminasyon": laminasyon,
        "baski_sonrasi": baski_sonrasi,
        "ozel_baski": ozel_baski_ozet,
        "ozel_istekler": ozel_istekler,
        "kar_orani": kar_orani,
        "alternatifler": teklif_alternatifleri,
    }

    st.markdown("### 📊 ÜRETİM VE PLANLAMA ÖZETİ")
    st.warning(
        "Montaj, verilen kutu açınımı formüllerinin dikdörtgen yerleşim tahminidir; "
        "gerçek ölçü ve bıçak çizimiyle doğrulayın. Amerikan Bristol ve Krome Karton'da "
        "600 kg'a kadar 70×100 ana tabaka kullanılır; üzerindeki miktarlarda bobin kesim "
        "adayları da değerlendirilir. Gösterilen maliyet kâğıt ve baskıyı kapsar; "
        "kesim/selofan/diğer işlem tarifeleri bu plan hesabına henüz bağlı değildir."
    )

    def plan_kartini_yazdir(p):
        r = p["res"]
        net_kullanici_adeti = p["adet"]
        secilen_kagit = p["kagit"]
        montaj_adedi = r["montaj_adedi"]

        st.markdown(
            f"**Kağıt & Adet:** {net_kullanici_adeti:,} adet - "
            f"{p['gramaj']}g {secilen_kagit}"
        )

        cmyk_on_arka = cmyk_secim == "Ön&Arka"
        pantone_on_arka = "(Ön&Arka)" in pantone_secimi
        cmyk_yok = cmyk_secim == "CMYK Baskı yok"
        pantone_yok = pantone_secimi == "Yok"

        kagit_revolta_uygun = secilen_kagit in ["Kuşe Kağıt", "1. Hamur Kağıt"]

        if cmyk_yok and pantone_yok:
            baski_metodu_str = "Baskı Yok"
        elif (
            (cmyk_on_arka or pantone_on_arka)
            and montaj_adedi % 2 == 0
            and kagit_revolta_uygun
        ):
            baski_metodu_str = "Revolta"
        elif cmyk_on_arka or pantone_on_arka:
            baski_metodu_str = "Ön&Arka"
        else:
            baski_metodu_str = "Tek Yüz"

        ham_tabaka = r["baskiya_giren_tabaka"]

        if baski_metodu_str == "Revolta":
            baski_ifadesi_adet = ham_tabaka * 2
            gecis_sayisi = 1
        elif baski_metodu_str == "Ön&Arka":
            baski_ifadesi_adet = ham_tabaka
            gecis_sayisi = 2
        else:
            baski_ifadesi_adet = ham_tabaka
            gecis_sayisi = 1

        p_adet = 1
        if not pantone_yok:
            try:
                p_adet = int(pantone_secimi.split()[0])
            except Exception:
                p_adet = 1

        cmyk_aktif = not cmyk_yok
        pantone_aktif = not pantone_yok

        if not cmyk_aktif:
            cmyk_kalip = 0
        elif cmyk_secim == "Ön&Arka" and baski_metodu_str != "Revolta":
            cmyk_kalip = 8
        else:
            cmyk_kalip = 4

        if not pantone_aktif:
            pantone_kalip = 0
        elif pantone_on_arka and baski_metodu_str != "Revolta":
            pantone_kalip = p_adet * 2
        else:
            pantone_kalip = p_adet

        if cmyk_aktif and not pantone_aktif:
            kalip_metni = f"{cmyk_kalip} Kalıp"
        elif not cmyk_aktif and pantone_aktif:
            kalip_metni = f"{pantone_kalip} Kalıp"
        elif cmyk_aktif and pantone_aktif:
            kalip_metni = f"{cmyk_kalip}+{pantone_kalip} Kalıp"
        else:
            kalip_metni = "0 Kalıp"

        if baski_metodu_str == "Baskı Yok":
            baski_ebat_detay = f"0 Kalıp {r['baski_ebat_str']}"
        else:
            baski_ebat_detay = f"{kalip_metni} {r['baski_ebat_str']}"

        plan_df = pd.DataFrame(
            [
                {
                    "Parametre / Kriter": "Fire Tabaka / Oranı",
                    "Değer": f"{r['fire_tabaka']} Tabaka (Ort. %{r['fire_pct']})",
                },
                {
                    "Parametre / Kriter": "Brüt Ürün Adedi",
                    "Değer": f"{r['brut_adet']:,} adet",
                },
                {
                    "Parametre / Kriter": "Montaj Planı",
                    "Değer": (
                        f"1 Tabakada {r['montaj_adedi']} Ürün; "
                        f"{r.get('montaj_detay', 'Dikdörtgen yerleşim')} ({urun_tipi})"
                    ),
                },
                {
                    "Parametre / Kriter": "Ana Tabaka Ebadı ve Sayısı",
                    "Değer": (
                        f"{r['ana_ebat']} {r['tabaka_adeti']:,} Tabaka"
                        .replace(",", ".")
                    ),
                },
                {
                    "Parametre / Kriter": "Baskı Ebadı ve Sayısı",
                    "Değer": baski_ebat_detay,
                },
                {
                    "Parametre / Kriter": "Baskıya Girecek Kağıt Ebadı ve Sayısı",
                    "Değer": (
                        f"{r['baski_ebat_str']} {ham_tabaka:,} Tabaka"
                        .replace(",", ".")
                    ),
                },
                {
                    "Parametre / Kriter": "Kağıt Kilogram (kg)",
                    "Değer": f"{r['kg_kagit']} kg",
                },
                {
                    "Parametre / Kriter": "Baskı Adedi ve Geçiş Sayısı",
                    "Değer": (
                        f"{baski_ifadesi_adet:,}".replace(",", ".")
                        + f" tabaka x {gecis_sayisi} geçiş"
                    ),
                },
                {
                    "Parametre / Kriter": "Baskı Metodu",
                    "Değer": baski_metodu_str,
                },
                {
                    "Parametre / Kriter": "Kaç M2",
                    "Değer": f"{r['toplam_m2']:,.2f} m²",
                },
            ]
        )
        st.table(plan_df)

        oneriler = r.get("oneriler", {})
        oneriler_df = pd.DataFrame(
            [
                {
                    "Plan": etiket,
                    "Tabaka": secim["ana_ebat"],
                    "Baskı ebatı": secim["baski_ebat_str"],
                    "Montaj modülü": secim["montaj_detay"],
                    "Montaj": secim["montaj_adedi"],
                    "Kâğıt (kg)": round(secim["kg"], 2),
                    "Kâğıt + baskı (₺)": round(secim["total_cost"], 2),
                }
                for etiket, secim in [
                    ("En düşük kâğıt + baskı", oneriler.get("lowest_total_cost")),
                    ("En az kâğıt", oneriler.get("lowest_paper_use")),
                    ("Dengeli", oneriler.get("balanced")),
                ]
                if secim is not None
            ]
        )

        st.caption(
            "Aşağıdaki sıralama mevcut kâğıt ve baskı girdileriyle yapılır; "
            "kesim ve sonraki işlem tarifeleri eksik olduğu için gerçek toplam maliyeti göstermez."
        )
        st.dataframe(oneriler_df, use_container_width=True, hide_index=True)

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

        st.markdown("#### 🔹 Kağıt B Alternatifleri")
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

    st.markdown("---")
    if st.button(
        "📄 Müşteri İçin Hazır Fiyat Teklif Sayfasına Git",
        use_container_width=True,
        key="calc_to_teklif",
    ):
        go_page("teklif")
        st.rerun()


# ==========================================
# MENÜ 4: MÜŞTERİ FİYAT TEKLİF SAYFASI
# ==========================================
elif st.session_state.page == "teklif":
    st.subheader("📄 Müşteri Fiyat Teklifi ve Ürün Şartnamesi")

    if st.session_state.teklif_data is None:
        st.warning("⚠️ Henüz bir hesaplama yapılmadı.")
        if st.button("Forma Dön", key="teklif_to_calc"):
            go_page("calc")
            st.rerun()
    else:
        td = st.session_state.teklif_data
        kar_orani = td["kar_orani"]

        st.warning(
            "Bu ekrandaki hesap kâğıt ve baskı maliyetine dayanır. Kesim, selofan ve "
            "diğer operasyon tarifeleri hesaba bağlanmadığından müşteriye gönderilecek "
            "nihai teklif olarak kullanılmadan önce bu kalemleri ekleyin."
        )

        st.markdown(
            "<div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; "
            "border-left: 5px solid #1F4E78;'>"
            "<h3 style='margin: 0; color: #1F4E78;'>"
            "OFFICIAL PRICE QUOTATION / FİYAT TEKLİF MEKTUBU</h3>"
            f"<p style='margin: 5px 0 0 0;'><strong>Sayın:</strong> {td['firma_adi']}</p>"
            "<p style='margin: 2px 0 0 0;'><strong>Tarih:</strong> 05 Kasım 2026 | "
            "<strong>Teklif No:</strong> OFF-2026-8493</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 1. Ürün & İmalat Teknik Özellikleri")

        col_t1, col_t2, col_t3 = st.columns(3)

        with col_t1:
            st.write(f"**Ürün Adı:** {td['urun_adi']}")
            st.write(f"**Ürün Tipi:** {td['urun_tipi']}")
            st.write(
                f"**Ebat:** {td['ebat_en']}x{td['ebat_boy']}x"
                f"{td['ebat_yukseklik']} mm"
            )
            if td["urun_tipi"] in [
                "Dip Kilitli Kutu",
                "Dip Kilit Yapıştırmalı Kutu",
            ]:
                st.write(f"**Dip kilit sıra sayısı:** {td['sira_sayisi']}")

        with col_t2:
            st.write(f"**Baskı CMYK:** {td['cmyk_secim']}")
            st.write(f"**Pantone Renk:** {td['pantone_secimi']}")
            st.write(f"**Yüzey Kaplama:** {td['laminasyon']}")

        with col_t3:
            st.write(f"**Özel İşlem:** {td['ozel_baski']}")
            st.write(f"**Kesim/Mücellit:** {td['baski_sonrasi']}")

        st.markdown("---")
        st.markdown("#### 2. Adet Alternatiflerine Göre Fiyat Tablosu")

        table_rows = []
        for alt in td["alternatifler"]:
            res = alt["res"]
            net_adet = alt["adet"]
            net_maliyet = res["toplam_uretim_maliyeti"]
            kar_tutari = net_maliyet * (kar_orani / 100.0)
            toplam_satis_tl = net_maliyet + kar_tutari
            birim_satis_tl = toplam_satis_tl / net_adet if net_adet > 0 else 0

            table_rows.append(
                {
                    "Alternatif": f"Option {alt['kod']}",
                    "Net Adet": f"{net_adet:,} adet",
                    "Kağıt Özelliği": f"{alt['gramaj']} gr {alt['kagit']}",
                    "Ana Tabaka": res["ana_ebat"],
                    "Kağıt Ağırlığı": f"{res['kg_kagit']} kg",
                    "Birim Satış Fiyatı (TL)": f"₺{birim_satis_tl:,.4f}",
                    "Karlı Toplam Tutar (TL)": f"₺{toplam_satis_tl:,.2f}",
                }
            )

        st.dataframe(
            pd.DataFrame(table_rows),
            use_container_width=True,
            hide_index=True,
        )
