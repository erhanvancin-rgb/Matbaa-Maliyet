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


def sheet_fits_limits(width_mm: float, height_mm: float, max_width_mm: float, max_height_mm: float) -> bool:
    """Check a sheet against a machine limit, allowing 90-degree rotation."""
    return (
        (width_mm <= max_width_mm and height_mm <= max_height_mm)
        or (height_mm <= max_width_mm and width_mm <= max_height_mm)
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
        press_cost = press.setup_cost + quantity / 1000 * press.run_cost_per_1000
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


def estimate_knife_cost(
    width_mm: float,
    length_mm: float,
    price_per_meter: float,
    is_box: bool = False,
) -> float:
    """Estimate die cost from the supplied dimensions and the per-meter rate."""
    if min(width_mm, length_mm) <= 0 or price_per_meter < 0:
        raise ValueError("Ölçüler pozitif, bıçak metre fiyatı sıfır veya daha büyük olmalıdır.")
    estimated_length_mm = (
        (width_mm * 6 + length_mm * 6) * 1.20
        if is_box
        else (width_mm * 2 + length_mm * 2)
    )
    return estimated_length_mm / 1000 * price_per_meter


def tiered_operation_cost(
    quantity: int,
    tier_size: int,
    setup_cost: float,
    unit_cost: float,
) -> float:
    """Price each setup tier plus the supplied per-piece run tariff."""
    if quantity < 0 or tier_size <= 0 or min(setup_cost, unit_cost) < 0:
        raise ValueError("Tiraj, kademe ve operasyon tarifeleri geçerli olmalıdır.")
    if quantity == 0:
        return 0.0
    return ceil(quantity / tier_size) * setup_cost + quantity * unit_cost


def pricing_summary(total_cost: float, cost_markup_percent: float) -> dict[str, float]:
    """Calculate profit, sales total and gross margin from a cost markup."""
    if total_cost < 0 or cost_markup_percent < 0:
        raise ValueError("Maliyet ve kâr oranı sıfırdan küçük olamaz.")
    total_profit = total_cost * cost_markup_percent / 100.0
    total_sales = total_cost + total_profit
    gross_margin_percent = total_profit / total_sales * 100.0 if total_sales else 0.0
    return {
        "total_profit": total_profit,
        "total_sales": total_sales,
        "gross_margin_percent": gross_margin_percent,
    }


def cutting_operation_cost(quantity: int, included_sheets: int, setup_cost: float, excess_sheet_cost: float) -> float:
    """Charge one cutting setup, then price only sheets above the included amount."""
    return included_quantity_operation_cost(
        quantity, included_sheets, setup_cost, excess_sheet_cost
    )


def included_quantity_operation_cost(
    quantity: int,
    included_quantity: int,
    setup_cost: float,
    excess_unit_cost: float,
) -> float:
    """Charge a setup covering the included quantity, then the overage only."""
    if quantity < 0 or included_quantity <= 0 or min(setup_cost, excess_unit_cost) < 0:
        raise ValueError("Adet, dahil miktar ve operasyon tarifeleri geçerli olmalıdır.")
    if quantity == 0:
        return 0.0
    return setup_cost + max(0, quantity - included_quantity) * excess_unit_cost


def press_cost_from_params(
    params: dict,
    machine_code: str,
    quantity: int,
    cmyk_enabled: bool,
    pantone_colors: int = 0,
) -> float:
    """Add press setup charges and tirage priced per 1,000 press sheets."""
    if quantity < 0 or pantone_colors < 0:
        raise ValueError("Baskı adedi ve renk sayısı geçerli olmalıdır.")
    if quantity == 0:
        return 0.0
    cmyk_setup = params.get(f"b_{machine_code}_cmyk", 0.0) if cmyk_enabled else 0.0
    pantone_setup = pantone_colors * params.get(f"b_{machine_code}_pantone", 0.0)
    run_rate = params.get(f"b_{machine_code}_tiraj", 0.0)
    run_cost = quantity / 1000 * run_rate if cmyk_enabled or pantone_colors else 0.0
    return cmyk_setup + pantone_setup + run_cost


def automatic_postpress_for_product(product_type: str) -> str | None:
    """Return the required finishing operation for box products."""
    box_types = {
        "Standart Kutu",
        "Dip Kilitli Kutu",
        "Dip Kilit Yapıştırmalı Kutu",
    }
    return "Kutu Kesim + Yapıştırma" if product_type in box_types else None


def layout_process_costs(
    params: dict,
    press_code: str,
    sheet_quantity: int,
    order_quantity: int,
    cutting_machine: str,
    cmyk_enabled: bool,
    pantone_colors: int,
    lamination: str,
    special_finishes: Iterable[str],
    product_width_mm: float,
    product_length_mm: float,
    is_box: bool,
    is_dip_glued: bool,
    special_cut: bool,
    postpress: str,
    total_area_m2: float,
    products_per_sheet: int = 1,
) -> dict:
    """Price one imposition using the same printed-sheet count for press and cutting."""
    press_cost = press_cost_from_params(
        params, press_code, sheet_quantity, cmyk_enabled, pantone_colors
    )

    cutter_keys = {
        "Kazanlı Kesim": ("kazanli", "kazanli_tiraj"),
        "K. Bobts": ("pedal", "pedal_tiraj"),
        "Bobst Kesim": ("bobst", "bobst_tiraj"),
    }
    setup_key, tirage_key = cutter_keys[cutting_machine]
    cutting_cost = cutting_operation_cost(
        sheet_quantity, 1000, params[setup_key], params[tirage_key]
    )

    lamination_key = {
        "Mat Selofan": "mat_sel",
        "Parlak Selofan": "par_sel",
    }.get(lamination)
    lamination_cost = total_area_m2 * params[lamination_key] if lamination_key else 0.0

    knife_cost = 0.0
    if is_box or special_cut:
        knife_cost = estimate_knife_cost(
            product_width_mm,
            product_length_mm,
            params["bicak_metre_fiyati"],
            is_box=is_box,
        ) * max(1, products_per_sheet)

    glue_cost = 0.0
    if postpress == "Kutu Kesim + Yapıştırma" and is_box:
        glue_cost = included_quantity_operation_cost(
            order_quantity, 10000, params["omega_tek"], params["omega_tek_tiraj"]
        )
        if is_dip_glued:
            glue_cost += included_quantity_operation_cost(
                order_quantity, 10000, params["omega_dip"], params["omega_dip_tiraj"]
            )

    lacquer_cost = 0.0
    lacquer_size = {"5070": "5070", "70100": "70100"}.get(press_code)
    for finish in special_finishes:
        if finish not in {"Dispresiyon Lak", "Lokal Lak", "Kabartma Lak"} or not lacquer_size:
            continue
        if finish == "Dispresiyon Lak":
            setup_limit = 1000 if lacquer_size == "5070" else 2000
            lacquer_cost += (
                ceil(sheet_quantity / setup_limit) * params[f"disp_{lacquer_size}"]
                + order_quantity / 1000 * params[f"disp_{lacquer_size}_tiraj"]
            )
        else:
            prefix = "lokal" if finish == "Lokal Lak" else "kab"
            lacquer_cost += (
                ceil(sheet_quantity / 1000) * params[f"{prefix}_{lacquer_size}"]
                + order_quantity * params[f"{prefix}_{lacquer_size}_tiraj"]
            )

    return {
        "Baskı": press_cost,
        "Kesim": cutting_cost,
        "Laminasyon": lamination_cost,
        "Bıçak": knife_cost,
        "Yapıştırma": glue_cost,
        "Ekstra Giderler": lacquer_cost,
    }


st.set_page_config(
    page_title="Matbaa ve Ambalaj Maliyet & Teklif Sistemi",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #172b4d;
        --muted: #64748b;
        --paper: #f5f7fb;
        --line: #e2e8f0;
        --accent: #0f766e;
    }
    [data-testid="stAppViewContainer"] { background: var(--paper); }
    [data-testid="stHeader"] { background: rgba(245, 247, 251, .92); }
    [data-testid="stMainBlockContainer"] {
        max-width: 1500px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3, h4 { color: var(--ink); letter-spacing: -.02em; }
    [data-testid="stMarkdownContainer"] p { color: #334155; }
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea {
        border-radius: 10px;
        border-color: #cbd5e1;
        background: #fff;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border-radius: 10px;
        border-color: #cbd5e1;
    }
    [data-testid="stButton"] > button,
    [data-testid="stDownloadButton"] > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 2.8rem;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    [data-testid="stButton"] > button:hover,
    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 14px rgba(23, 43, 77, .12);
    }
    [data-testid="stButton"] > button[kind="primary"] {
        background: var(--accent);
        border-color: var(--accent);
        color: #fff;
    }
    [data-testid="stAlert"] { border-radius: 12px; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--line);
        border-radius: 16px;
        background: #fff;
        box-shadow: 0 4px 16px rgba(23, 43, 77, .045);
    }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
        background: #fff;
    }
    .app-hero {
        padding: 1.35rem 1.6rem;
        margin-bottom: 1.1rem;
        border: 1px solid #dbe5ef;
        border-radius: 18px;
        background: linear-gradient(120deg, #fff 5%, #eaf4f3 100%);
        box-shadow: 0 8px 24px rgba(23, 43, 77, .06);
    }
    .app-hero-kicker {
        color: var(--accent);
        font-size: .75rem;
        font-weight: 750;
        letter-spacing: .12em;
        text-transform: uppercase;
    }
    .app-hero-title {
        color: var(--ink);
        font-size: clamp(1.55rem, 3vw, 2.1rem);
        font-weight: 760;
        line-height: 1.2;
        margin: .3rem 0;
    }
    .app-hero-subtitle { color: var(--muted); font-size: .98rem; }
    .section-kicker {
        color: var(--accent);
        font-size: .73rem;
        font-weight: 750;
        letter-spacing: .1em;
        text-transform: uppercase;
        margin-bottom: .15rem;
    }
    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] { padding: 1rem .8rem 2rem; }
        .app-hero { padding: 1.1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 0. KALICI JSON PARAMETRE YÖNETİMİ VE STATE SENKRONİZASYONU ---
PARAM_FILE = "matbaa_parametreleri.json"

default_params = {
    "bristol": 825.0,
    "krome": 40000.0,
    "kuse": 850.0,
    "hamur": 1200.0,
    "b_3550_cmyk": 1800.0,
    "b_3550_pantone": 900.0,
    "b_3550_tiraj": 400.0,
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
    "pedal": 1800.0,
    "pedal_tiraj": 0.75,
    "bobst": 3000.0,
    "bobst_tiraj": 1.0,
    "omega_tek": 2000.0,
    "omega_tek_tiraj": 0.2,
    "omega_dip": 2500.0,
    "omega_dip_tiraj": 0.25,
    "bicak_metre_fiyati": 500.0,
}


def parametreleri_yukle():
    if os.path.exists(PARAM_FILE):
        try:
            with open(PARAM_FILE, "r", encoding="utf-8") as file:
                kayitli = json.load(file)
                for key, value in default_params.items():
                    if key not in kayitli:
                        kayitli[key] = value
                eski_tarifeler = {
                    "b_3550_cmyk": (2400.0, 1800.0),
                    "b_3550_pantone": (1200.0, 900.0),
                    "b_3550_tiraj": (500.0, 400.0),
                    "bobst_tiraj": (1.5, 1.0),
                    "pedal": (2500.0, 1800.0),
                    "pedal_tiraj": (1.0, 0.75),
                }
                for key, (eski, yeni) in eski_tarifeler.items():
                    if kayitli.get(key) == eski:
                        kayitli[key] = yeni
                return kayitli
        except Exception:
            return default_params.copy()

    return default_params.copy()


def parametreleri_kaydet(params_dict):
    try:
        with open(PARAM_FILE, "w", encoding="utf-8") as file:
            json.dump(params_dict, file, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False


if "params" not in st.session_state:
    st.session_state.params = parametreleri_yukle()


# --- 1. TCMB GÜNCEL SATIŞ KURLARINI ÇEKME ---
@st.cache_data(ttl=3600)
def tcmb_kurlarini_getir():
    usd_kur = None
    eur_kur = None

    try:
        url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        req = urllib.request.urlopen(url, timeout=5)
        root = ET.fromstring(req.read())

        for currency in root.findall("Currency"):
            code = currency.get("CurrencyCode")
            if code == "USD":
                node = currency.find("BanknoteSelling")
                val = node.text if node is not None else None
                if val:
                    usd_kur = float(val)
            elif code == "EUR":
                node = currency.find("BanknoteSelling")
                val = node.text if node is not None else None
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
st.markdown(
    """
    <div class="app-hero">
      <div class="app-hero-kicker">MATBAAM PRO · ÜRETİM VE FİYATLANDIRMA</div>
      <div class="app-hero-title">Matbaa maliyet ve teklif yönetimi</div>
      <div class="app-hero-subtitle">Üretim planını oluşturun, maliyetleri karşılaştırın ve teklifinizi hazırlayın.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
if canli_usd is not None and canli_eur is not None:
    st.info(
        f"🏦 TCMB güncel döviz satış kurları — USD: ₺{canli_usd:.4f} | EUR: ₺{canli_eur:.4f}"
    )
else:
    st.error("TCMB döviz kurları şu anda alınamadı; dövize bağlı kâğıt maliyetleri hesaplanamaz.")

nav_c1, nav_c2, nav_c3, nav_c4 = st.columns(4)
with nav_c1:
    type_a = "primary" if st.session_state.page == "home" else "secondary"
    if st.button("Ana sayfa", use_container_width=True, type=type_a):
        go_page("home")
        st.rerun()
with nav_c2:
    type_b = "primary" if st.session_state.page == "params" else "secondary"
    if st.button("Parametreler", use_container_width=True, type=type_b):
        go_page("params")
        st.rerun()
with nav_c3:
    type_c = "primary" if st.session_state.page == "calc" else "secondary"
    if st.button("Teklif hesapla", use_container_width=True, type=type_c):
        go_page("calc")
        st.rerun()
with nav_c4:
    type_d = "primary" if st.session_state.page == "teklif" else "secondary"
    if st.button("Teklif çıktısı", use_container_width=True, type=type_d):
        go_page("teklif")
        st.rerun()

st.markdown("---")


# ==========================================
# MENÜ 1: ANA SAYFA
# ==========================================
if st.session_state.page == "home":
    st.subheader("Başlangıç")
    st.caption("İşletme tarifelerinizi yönetin veya yeni bir üretim teklifi hazırlayın.")
    home_cols = st.columns(3)
    home_actions = [
        ("01", "Tarifeleri yönetin", "Kâğıt, baskı, kesim ve diğer işletme fiyatlarını güncelleyin.", "params", "Parametreleri aç"),
        ("02", "Üretimi planlayın", "Ürün ölçülerini ve adetleri girip A/B/C seçeneklerini karşılaştırın.", "calc", "Teklif hesapla"),
        ("03", "Müşteri teklifini hazırlayın", "Hesaplanan üretim maliyetlerini teklif görünümüne taşıyın.", "teklif", "Teklif çıktısını aç"),
    ]
    for col, (step, title, description, page_name, button_label) in zip(home_cols, home_actions):
        with col:
            st.markdown(
                f"<div class='app-hero'><div class='app-hero-kicker'>ADIM {step}</div>"
                f"<h3>{title}</h3><div class='app-hero-subtitle'>{description}</div></div>",
                unsafe_allow_html=True,
            )
            if st.button(button_label, use_container_width=True, key=f"home_{page_name}"):
                go_page(page_name)
                st.rerun()


# ==========================================
# MENÜ 2: PARAMETRELER SAYFASI
# ==========================================
elif st.session_state.page == 'params':
    st.subheader("Matbaa Maliyet Parametreleri Fiyat Listesi")
    st.caption("Girilen işletme tarifeleri KDV hariçtir. Tekliflerde KDV ayrıca belirtilir ve eklenir.")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 1. Kağıt ve Karton Grubu (Ton Maliyetleri)")
        st.session_state.params['bristol'] = st.number_input("Amerikan Bristol Ton ($ USD)", value=float(st.session_state.params['bristol']))
        st.session_state.params['krome'] = st.number_input("Krome Karton Ton (TL)", value=float(st.session_state.params['krome']))
        st.session_state.params['kuse'] = st.number_input("Kuşe Ton (€ EUR)", value=float(st.session_state.params['kuse']))
        st.session_state.params['hamur'] = st.number_input("1. Hamur Ton ($ USD)", value=float(st.session_state.params['hamur']))

        st.markdown("---")
        st.markdown("#### 2. Baskı Grubu (TL)")
        st.session_state.params['b_3550_cmyk'] = st.number_input("35×50 CMYK — hazırlık/proses (iş başına, ₺)", value=float(st.session_state.params['b_3550_cmyk']))
        st.session_state.params['b_3550_pantone'] = st.number_input("35×50 Pantone 1 renk — hazırlık/proses (renk başına, ₺)", value=float(st.session_state.params['b_3550_pantone']))
        st.session_state.params['b_3550_tiraj'] = st.number_input("35×50 tiraj (1.000 adet başına, ₺)", value=float(st.session_state.params['b_3550_tiraj']))
        st.session_state.params['b_5070_cmyk'] = st.number_input("50×70 CMYK — hazırlık/proses (iş başına, ₺)", value=float(st.session_state.params['b_5070_cmyk']))
        st.session_state.params['b_5070_pantone'] = st.number_input("50×70 Pantone 1 renk — hazırlık/proses (renk başına, ₺)", value=float(st.session_state.params['b_5070_pantone']))
        st.session_state.params['b_5070_tiraj'] = st.number_input("50×70 tiraj (1.000 adet başına, ₺)", value=float(st.session_state.params['b_5070_tiraj']))
        st.session_state.params['b_70100_cmyk'] = st.number_input("70×100 CMYK — hazırlık/proses (iş başına, ₺)", value=float(st.session_state.params['b_70100_cmyk']))
        st.session_state.params['b_70100_pantone'] = st.number_input("70×100 Pantone 1 renk — hazırlık/proses (renk başına, ₺)", value=float(st.session_state.params['b_70100_pantone']))
        st.session_state.params['b_70100_tiraj'] = st.number_input("70×100 tiraj (1.000 adet başına, ₺)", value=float(st.session_state.params['b_70100_tiraj']))
    with col2:
        st.markdown("#### 3. Yüzey İşlemleri ve Lak Grubu")
        st.session_state.params['disp_5070'] = st.number_input("50×70 dispresiyon lak (1.000 tabaka sınırı, ₺)", value=float(st.session_state.params['disp_5070']))
        st.session_state.params['disp_5070_tiraj'] = st.number_input("50×70 dispresiyon lak tiraj (1.000 adet başına, ₺)", value=float(st.session_state.params['disp_5070_tiraj']))
        st.session_state.params['disp_70100'] = st.number_input("70×100 dispresiyon lak (2.000 tabaka sınırı, ₺)", value=float(st.session_state.params['disp_70100']))
        st.session_state.params['disp_70100_tiraj'] = st.number_input("70×100 dispresiyon lak tiraj (1.000 adet başına, ₺)", value=float(st.session_state.params['disp_70100_tiraj']))
        st.session_state.params['mat_sel'] = st.number_input("Mat selofan (m² başına, ₺)", value=float(st.session_state.params['mat_sel']))
        st.session_state.params['par_sel'] = st.number_input("Parlak selofan (m² başına, ₺)", value=float(st.session_state.params['par_sel']))
        st.session_state.params['lokal_5070'] = st.number_input("50×70 lokal lak (1.000 tabaka sınırı, ₺)", value=float(st.session_state.params['lokal_5070']))
        st.session_state.params['lokal_5070_tiraj'] = st.number_input("50×70 lokal lak tiraj (adet başına, ₺)", value=float(st.session_state.params['lokal_5070_tiraj']))
        st.session_state.params['lokal_70100'] = st.number_input("70×100 lokal lak (1.000 tabaka sınırı, ₺)", value=float(st.session_state.params['lokal_70100']))
        st.session_state.params['lokal_70100_tiraj'] = st.number_input("70×100 lokal lak tiraj (adet başına, ₺)", value=float(st.session_state.params['lokal_70100_tiraj']))
        st.session_state.params['kab_5070'] = st.number_input("50×70 kabartma lak (1.000 tabaka sınırı, ₺)", value=float(st.session_state.params['kab_5070']))
        st.session_state.params['kab_5070_tiraj'] = st.number_input("50×70 kabartma lak tiraj (adet başına, ₺)", value=float(st.session_state.params['kab_5070_tiraj']))
        st.session_state.params['kab_70100'] = st.number_input("70×100 kabartma lak (1.000 tabaka sınırı, ₺)", value=float(st.session_state.params['kab_70100']))
        st.session_state.params['kab_70100_tiraj'] = st.number_input("70×100 kabartma lak tiraj (adet başına, ₺)", value=float(st.session_state.params['kab_70100_tiraj']))

    st.markdown("#### 4. Kesim ve Mücellit Grubu")
    cut_col1, cut_col2 = st.columns(2)
    with cut_col1:
        st.session_state.params['kazanli'] = st.number_input("Kazanlı kesim (1.000 adet sınırı, çember başına ₺)", value=float(st.session_state.params['kazanli']))
        st.session_state.params['kazanli_tiraj'] = st.number_input("Kazanlı kesim tiraj (adet başına, ₺)", value=float(st.session_state.params['kazanli_tiraj']))
        st.session_state.params['pedal'] = st.number_input("K. Bobts (60×80 cm; ilk 1.000 tabaka çember başına ₺)", value=float(st.session_state.params['pedal']))
        st.session_state.params['pedal_tiraj'] = st.number_input("K. Bobts tirajı (1.000 tabakadan sonra, tabaka başına ₺)", value=float(st.session_state.params['pedal_tiraj']))
        st.session_state.params['bobst'] = st.number_input("Bobst kesim (1.000 adet sınırı, çember başına ₺)", value=float(st.session_state.params['bobst']))
        st.session_state.params['bobst_tiraj'] = st.number_input("Bobst kesim tiraj (adet başına, ₺)", value=float(st.session_state.params['bobst_tiraj']))
    with cut_col2:
        st.session_state.params['omega_tek'] = st.number_input("Omega tek kulak (10.000 adet sınırı, çember başına ₺)", value=float(st.session_state.params['omega_tek']))
        st.session_state.params['omega_tek_tiraj'] = st.number_input("Omega tek kulak tiraj (10.000 adedi aşan adet başına, ₺)", value=float(st.session_state.params['omega_tek_tiraj']))
        st.session_state.params['omega_dip'] = st.number_input("Omega dip yapıştırma (10.000 adet sınırı, çember başına ₺)", value=float(st.session_state.params['omega_dip']))
        st.session_state.params['omega_dip_tiraj'] = st.number_input("Omega dip yapıştırma tiraj (10.000 adedi aşan adet başına, ₺)", value=float(st.session_state.params['omega_dip_tiraj']))

    st.markdown("#### 5. Bıçak Maliyeti")
    st.session_state.params['bicak_metre_fiyati'] = st.number_input(
        "Bıçak fiyatı (metre başına, ₺)",
        value=float(st.session_state.params['bicak_metre_fiyati']),
        min_value=0.0,
        step=10.0,
    )

    if parametreleri_kaydet(st.session_state.params):
        st.success("💾 Parametreler uygulamanın JSON dosyasına kaydedildi.")
    else:
        st.error("Parametreler JSON dosyasına kaydedilemedi.")
    st.download_button(
        "Güncel parametre JSON dosyasını indir",
        data=json.dumps(st.session_state.params, ensure_ascii=False, indent=4).encode("utf-8"),
        file_name="matbaa_parametreleri.json",
        mime="application/json",
        help="İndirdiğiniz dosyayı GitHub deposundaki matbaa_parametreleri.json dosyasına yükleyerek varsayılanları da güncelleyebilirsiniz.",
    )

# ==========================================
# MENÜ 3: FORM VE AKILLI DİNAMİK HESAPLAMA
# ==========================================
elif st.session_state.page == "calc":
    st.subheader("Teklif hesaplama")
    st.caption("Önce ürün ve üretim bilgilerini girin; ardından A/B/C adet seçeneklerinin maliyetini karşılaştırın.")
    st.markdown('<div class="section-kicker">01 · Sipariş bilgileri</div>', unsafe_allow_html=True)

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
        net_a = st.number_input("Ürün Adedi A", value=1000, min_value=1, step=100)
    with col_r2_2:
        net_b = st.number_input("Ürün Adedi B", value=5000, min_value=1, step=100)
    with col_r2_3:
        net_c = st.number_input("Ürün Adedi C", value=25000, min_value=1, step=100)

    st.markdown('<div class="section-kicker">02 · Kâğıt ve ebat</div>', unsafe_allow_html=True)
    col_ka_head, _ = st.columns(2)
    with col_ka_head:
        ca_g, ca_c = st.columns(2)
        with ca_g:
            gramaj_a = st.number_input("Gramaj (gr/m²)", value=350, step=10, min_value=50)
        with ca_c:
            kagit_cinsi_a = st.selectbox(
                "Kağıt Cinsi",
                ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"],
            )

    st.markdown('<div class="section-kicker">03 · Baskı</div>', unsafe_allow_html=True)
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

    st.markdown('<div class="section-kicker">04 · Yüzey ve son işlemler</div>', unsafe_allow_html=True)
    c_lam, c_ob1, c_ob2, c_bs = st.columns(4)
    with c_lam:
        laminasyon = st.selectbox(
            "Laminasyon",
            ["Parlak Selofan", "Mat Selofan", "Yok"],
        )
    with c_ob1:
        ozel_baski_1 = st.selectbox(
            "Özel Baskılar 1",
            ["Yok", "Dispresiyon Lak", "Lokal Lak", "Kabartma Lak", "Varak Yaldız"],
        )
    with c_ob2:
        ozel_baski_2 = st.selectbox(
            "Özel Baskılar 2",
            ["Yok", "Dispresiyon Lak", "Lokal Lak", "Kabartma Lak", "Varak Yaldız"],
        )
    with c_bs:
        otomatik_son_islem = automatic_postpress_for_product(urun_tipi)
        if otomatik_son_islem:
            baski_sonrasi = otomatik_son_islem
            st.info(f"Otomatik işlem: **{baski_sonrasi}**")
        else:
            baski_sonrasi = st.selectbox(
                "Baskı Sonrası",
                ["Düz Kesim", "Özel kesim"],
            )

    st.markdown('<div class="section-kicker">05 · Kesim ve özel istekler</div>', unsafe_allow_html=True)
    kesim_makinesi = st.selectbox(
        "Kesim makinesi tarifesi",
        ["Kazanlı Kesim", "K. Bobts", "Bobst Kesim"],
    )
    st.caption("Kazanlı maksimum ebat: 50×70 cm. K. Bobts maksimum ebat: 60×80 cm. Bobst maksimum ebat: 70×100 cm.")

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
                cutter_max = {
                    "Kazanlı Kesim": (500.0, 700.0),
                    "K. Bobts": (600.0, 800.0),
                    "Bobst Kesim": (700.0, 1000.0),
                }.get(kesim_makinesi)
                if cutter_max and not sheet_fits_limits(tw, th, *cutter_max):
                    continue

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
                    if canli_usd is None:
                        st.error("Amerikan Bristol maliyeti için TCMB USD kuru alınamadı.")
                        st.stop()
                    ton_fiyat = params["bristol"] * canli_usd
                elif kagit == "Krome Karton":
                    ton_fiyat = params["krome"]
                elif kagit == "Kuşe Kağıt":
                    if canli_eur is None:
                        st.error("Kuşe kâğıt maliyeti için TCMB EUR kuru alınamadı.")
                        st.stop()
                    ton_fiyat = params["kuse"] * canli_eur
                else:
                    if canli_usd is None:
                        st.error("1. Hamur maliyeti için TCMB USD kuru alınamadı.")
                        st.stop()
                    ton_fiyat = params["hamur"] * canli_usd

                kagit_maliyeti = (kg_kagit / 1000.0) * ton_fiyat
                pantone_colors = {
                    "Yok": 0,
                    "1 renk zemin": 1,
                    "2 renk zemin": 2,
                    "1 renk lokal": 1,
                }.get(pantone_secimi, 0)
                cmyk_enabled = cmyk_secim != "CMYK Baskı yok"
                process_costs = layout_process_costs(
                    params=params,
                    press_code=makine_kodu,
                    sheet_quantity=baskiya_giren_tabaka_adeti,
                    order_quantity=net_adet,
                    cutting_machine=kesim_makinesi,
                    cmyk_enabled=cmyk_enabled,
                    pantone_colors=pantone_colors,
                    lamination=laminasyon,
                    special_finishes=[ozel_baski_1, ozel_baski_2],
                    product_width_mm=ebat_en,
                    product_length_mm=ebat_boy,
                    is_box=is_kutu,
                    is_dip_glued=urun_tipi == "Dip Kilit Yapıştırmalı Kutu",
                    special_cut=baski_sonrasi == "Özel kesim",
                    postpress=baski_sonrasi,
                    total_area_m2=toplam_m2,
                    products_per_sheet=montaj,
                )
                baski_maliyeti = process_costs["Baskı"]
                kesim_maliyeti = process_costs["Kesim"]
                bicak_maliyeti = process_costs["Bıçak"]

                toplam_maliyet = kagit_maliyeti + sum(process_costs.values())

                aday_sonuclari.append(
                    {
                        "ana_ebat": ana_tabaka,
                        "baski_ebat_str": baski_ebat_adi,
                        "montaj_adedi": montaj,
                        "kg": kg_kagit,
                        "kagit_maliyeti": kagit_maliyeti,
                        "baski_maliyeti": baski_maliyeti,
                        "kesim_maliyeti": kesim_maliyeti,
                        "bicak_maliyeti": bicak_maliyeti,
                        "process_costs": process_costs,
                        "press_sheets": baskiya_giren_tabaka_adeti,
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
                        "kesim_maliyeti_dahil": True,
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
                            "kesim_maliyeti": kesim_maliyeti,
                            "bicak_maliyeti": bicak_maliyeti,
                            "toplam_uretim_maliyeti": toplam_maliyet,
                            "makine_kodu": makine_kodu,
                            "kesim_maliyeti_dahil": True,
                            "geometri_dogrulama_gerekli": is_kutu,
                        }

        adaylari_degerlendir(standart_adaylar)

        gecici_kg = en_iyi_secim["kg_kagit"] if en_iyi_secim else 0.0
        if bobin_cutting_allowed(kagit, gecici_kg):
            adaylari_degerlendir(bobin_adaylarini_uret())

        if en_iyi_secim is None:
            raise ValueError(
                f"{kesim_makinesi} sınırlarına uygun üretim planı bulunamadı."
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

    st.markdown('<div class="section-kicker">06 · Maliyet kalemleri</div>', unsafe_allow_html=True)
    # Read the last entered margin before calculating; its editable field is shown
    # below the cost breakdown so the user can review costs first.
    kar_oranlari = {
        code: float(st.session_state.get(f"hedef_kar_orani_{code}", 30.0))
        for code in ["A", "B", "C"]
    }
    st.markdown("#### A/B/C için işletme giderleri (TL / iş)")
    st.caption(
        "Mücellit, nakliye ve tanımlı olmayan ekstra gider tarifeleri verilmediği için "
        "bu tutarları her adet alternatifi için girin. Varak bedelini de ekstra giderlere ekleyin."
    )
    ek_giderler = {}
    gider_sutunlari = st.columns(3)
    for col, kod in zip(gider_sutunlari, ["A", "B", "C"]):
        with col:
            st.markdown(f"**Alternatif {kod}**")
            ek_giderler[kod] = {
                "mucellit": st.number_input(
                    f"{kod} mücellit (₺)", min_value=0.0, value=0.0, step=100.0,
                    key=f"mucellit_{kod}",
                ),
                "nakliye": st.number_input(
                    f"{kod} nakliye (₺)", min_value=0.0, value=0.0, step=100.0,
                    key=f"nakliye_{kod}",
                ),
                "ekstra": st.number_input(
                    f"{kod} ekstra gider (₺)", min_value=0.0, value=0.0, step=100.0,
                    key=f"ekstra_{kod}",
                ),
            }

    teklif_alternatifleri = [plan for plan in plan_params]

    pantone_colors = {
        "Yok": 0,
        "1 renk zemin": 1,
        "2 renk zemin": 2,
        "1 renk lokal": 1,
    }.get(pantone_secimi, 0)

    for plan in teklif_alternatifleri:
        r = plan["res"]
        quantity = plan["adet"]
        code = plan["kod"][0]
        press_code = r["makine_kodu"]
        press_sheets = r["baskiya_giren_tabaka"]

        is_box_plan = "Kutu" in urun_tipi
        process_costs = layout_process_costs(
            params=st.session_state.params,
            press_code=press_code,
            sheet_quantity=press_sheets,
            order_quantity=quantity,
            cutting_machine=kesim_makinesi,
            cmyk_enabled=cmyk_secim != "CMYK Baskı yok",
            pantone_colors=pantone_colors,
            lamination=laminasyon,
            special_finishes=[ozel_baski_1, ozel_baski_2],
            product_width_mm=ebat_en,
            product_length_mm=ebat_boy,
            is_box=is_box_plan,
            is_dip_glued=urun_tipi == "Dip Kilit Yapıştırmalı Kutu",
            special_cut=baski_sonrasi == "Özel kesim",
            postpress=baski_sonrasi,
            total_area_m2=r["toplam_m2"],
            products_per_sheet=r["montaj_adedi"],
        )
        paper_cost = r["kagit_maliyeti"]
        print_cost = process_costs["Baskı"]
        cutting_cost = process_costs["Kesim"]
        lamination_cost = process_costs["Laminasyon"]
        knife_cost = process_costs["Bıçak"]
        glue_cost = process_costs["Yapıştırma"]
        lacquer_cost = process_costs["Ekstra Giderler"]
        r["baski_maliyeti"] = print_cost
        r["kesim_maliyeti"] = cutting_cost

        manual = ek_giderler[code]
        breakdown = {
            "Kağıt": paper_cost,
            "Baskı": print_cost,
            "Laminasyon": lamination_cost,
            "Kesim": cutting_cost,
            "Mücellit": manual["mucellit"],
            "Yapıştırma": glue_cost,
            "Bıçak": knife_cost,
            "Nakliye": manual["nakliye"],
            "Ekstra Giderler": manual["ekstra"] + lacquer_cost,
        }
        total_cost = sum(breakdown.values())
        unit_cost = total_cost / quantity if quantity else 0.0
        breakdown["Toplam Maliyet"] = total_cost
        breakdown["Birim Maliyet"] = unit_cost
        kar_orani = kar_oranlari[code]
        fiyat_ozeti = pricing_summary(total_cost, kar_orani)
        breakdown["Kar Oranı"] = kar_orani
        breakdown["Toplam Kâr"] = fiyat_ozeti["total_profit"]
        breakdown["Toplam Kâr Marjı"] = fiyat_ozeti["gross_margin_percent"]
        breakdown["Toplam Satış Fiyatı"] = fiyat_ozeti["total_sales"]
        breakdown["Birim Satış Fiyatı"] = (
            fiyat_ozeti["total_sales"] / quantity if quantity else 0.0
        )
        r["maliyet_dagilimi"] = breakdown
        r["toplam_uretim_maliyeti"] = total_cost

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
        "kar_oranlari": kar_oranlari,
        "kesim_makinesi": kesim_makinesi,
        "ek_giderler": ek_giderler,
        "alternatifler": teklif_alternatifleri,
    }

    st.markdown("### 📊 ÜRETİM VE PLANLAMA ÖZETİ")
    st.warning(
        "Montaj, verilen kutu açınımı formüllerinin dikdörtgen yerleşim tahminidir; "
        "üretim öncesi gerçek ölçü ve bıçak çizimiyle doğrulayın. Amerikan Bristol ve "
        "Krome Karton'da 600 kg'a kadar 70×100 ana tabaka kullanılır; üzerindeki "
        "miktarlarda bobin kesim adayları da değerlendirilir. Plan maliyet sıralaması "
        "kâğıt, baskı ve kesimle birlikte tanımlı son işlem ve bıçak tarifelerini içerir. "
        "Makine ebat sınırına uymayan adaylar elenir."
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
        oneriler_listesi = [
            ("En düşük toplam maliyet", oneriler.get("lowest_total_cost")),
            ("En az kâğıt tüketimi", oneriler.get("lowest_paper_use")),
            ("Dengeli makine/operasyon", oneriler.get("balanced")),
        ]
        for etiket, secim in oneriler_listesi:
            if secim is None:
                continue
            costs = secim["process_costs"]
            other_process_cost = sum(costs.values()) - sum(
                costs[name] for name in ["Baskı", "Kesim", "Bıçak"]
            )
            with st.container(border=True):
                st.markdown(f"**{etiket}**")
                st.caption(
                    f"{secim['ana_ebat']} ana tabaka · {secim['baski_ebat_str']} baskı · "
                    f"{secim['montaj_detay']} · montajda {secim['montaj_adedi']} ürün"
                )
                st.write(
                    f"Baskı/kesim: **{secim['press_sheets']:,} tabaka** · "
                    f"Kâğıt: **{secim['kg']:,.2f} kg**"
                )
                st.caption(
                    f"Kâğıt ₺{secim['kagit_maliyeti']:,.2f} · "
                    f"Baskı ₺{costs['Baskı']:,.2f} · "
                    f"Kesim ₺{costs['Kesim']:,.2f} · "
                    f"Bıçak ₺{costs['Bıçak']:,.2f} · "
                    f"Diğer işlemler ₺{other_process_cost:,.2f}"
                )
                st.markdown(f"**Plan tarifeli maliyeti: ₺{secim['total_cost']:,.2f}**")

    plan_cols = st.columns(3)
    for col, plan, label in zip(plan_cols, teklif_alternatifleri, ["A", "B", "C"]):
        with col:
            with st.container(border=True):
                st.markdown(f"##### Alternatif {label} · {plan['adet']:,} adet")
                plan_kartini_yazdir(plan)

    def maliyet_dokumu_yazdir(plans, title, suffix=""):
        st.markdown(f"#### {title} — Maliyet Dökümü")
        by_code = {
            plan["kod"][0]: plan["res"]["maliyet_dagilimi"]
            for plan in plans
            if (
                plan["kod"].endswith("2")
                if suffix == "2"
                else plan["kod"] in {"A", "B", "C"}
            )
        }
        row_names = [
            "Kağıt", "Baskı", "Laminasyon", "Kesim", "Mücellit", "Yapıştırma",
            "Bıçak", "Nakliye", "Ekstra Giderler", "Toplam Maliyet",
            "Birim Maliyet", "Kar Oranı", "Toplam Kâr", "Toplam Kâr Marjı",
            "Toplam Satış Fiyatı", "Birim Satış Fiyatı",
        ]
        rows = []
        for name in row_names:
            row = {"Maliyet Unsuru": name}
            for code in ["A", "B", "C"]:
                value = by_code.get(code, {}).get(name, 0.0)
                row[code] = (
                    f"%{value:.2f}"
                    if name in {"Kar Oranı", "Toplam Kâr Marjı"}
                    else f"₺{value:,.2f}"
                )
            rows.append(row)
        # st.table renders every cost row without an inner scrolling area.
        st.table(pd.DataFrame(rows))

    st.markdown("### 💰 Üretim Maliyeti ve Satış Özeti")
    st.caption(
        f"Kesim tarifesi: {kesim_makinesi}. Bıçak hesabı kutuda "
        "(en×6 + boy×6)×1,20 mm; 2D özel kesimde (en×2 + boy×2) mm kabul edilerek "
        "500 TL/metre tarifesine çevrilir. Bıçak tutarı iş başına bir defa eklenir."
    )
    if any(
        finish in {"Dispresiyon Lak", "Lokal Lak", "Kabartma Lak"}
        and plan["res"]["makine_kodu"] == "3550"
        for finish in [ozel_baski_1, ozel_baski_2]
        for plan in teklif_alternatifleri
    ):
        st.info(
            "35×50 için lak tarifesi parametrelerde yok; bu kalemi "
            "Ekstra Giderler alanına elle ekleyin. Varak fiyatı da ayrıca girilmelidir."
        )

    maliyet_dokumu_yazdir(teklif_alternatifleri, f"Kâğıt ({kagit_cinsi_a})")
    st.caption("Teklif tutarları KDV hariçtir; KDV ayrıca eklenecektir.")

    st.markdown('<div class="section-kicker">07 · Kâr ve satış fiyatı</div>', unsafe_allow_html=True)
    st.caption(
        "A, B ve C için kâr oranını ayrı belirleyin. Girilen oran maliyete eklenir; "
        "toplam kâr marjı kâr tutarının satış toplamına oranıdır."
    )
    kar_sutunlari = st.columns(3)
    for col, code in zip(kar_sutunlari, ["A", "B", "C"]):
        with col:
            st.number_input(
                f"Alternatif {code} kâr oranı (%)",
                min_value=0.0,
                max_value=1000.0,
                value=kar_oranlari[code],
                step=1.0,
                key=f"hedef_kar_orani_{code}",
                help="Bu alternatifin maliyetine eklenecek kâr oranı.",
            )

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
        kar_oranlari = td["kar_oranlari"]

        st.warning(
            "Teklif toplamına kâğıt, baskı, laminasyon, seçilen kesim ve kutu yapıştırma "
            "tarifeleri ile girilen mücellit/nakliye/ekstra giderler eklenmiştir. Bıçak "
            "uzunluğu tahminidir; gerçek kalıp çizimiyle doğrulayın. Tüm fiyatlar KDV hariçtir; KDV ayrıca eklenir."
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
            kar_orani = kar_oranlari[alt["kod"][0]]
            fiyat_ozeti = pricing_summary(net_maliyet, kar_orani)
            toplam_satis_tl = fiyat_ozeti["total_sales"]
            birim_satis_tl = toplam_satis_tl / net_adet if net_adet > 0 else 0

            table_rows.append(
                {
                    "Alternatif": f"Option {alt['kod']}",
                    "Net Adet": f"{net_adet:,} adet",
                    "Kağıt Özelliği": f"{alt['gramaj']} gr {alt['kagit']}",
                    "Ana Tabaka": res["ana_ebat"],
                    "Kağıt Ağırlığı": f"{res['kg_kagit']} kg",
                    "Kâr Oranı (%)": f"%{kar_orani:g}",
                    "Toplam Kâr (TL)": f"₺{fiyat_ozeti['total_profit']:,.2f}",
                    "Toplam Kâr Marjı (%)": f"%{fiyat_ozeti['gross_margin_percent']:.2f}",
                    "Birim Satış Fiyatı (TL)": f"₺{birim_satis_tl:,.4f}",
                    "Karlı Toplam Tutar (TL)": f"₺{toplam_satis_tl:,.2f}",
                }
            )

        st.dataframe(
            pd.DataFrame(table_rows),
            use_container_width=True,
            hide_index=True,
        )
