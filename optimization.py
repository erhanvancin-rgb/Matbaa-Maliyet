"""Conservative rectangular imposition and production-plan scoring.

Die-line geometry is not inferred: box layouts use their supplied bounding box
only and are marked as requiring die-line validation in the returned plan.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil
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
        return ((sheet.width_mm <= self.max_width_mm and sheet.height_mm <= self.max_height_mm)
                or (sheet.height_mm <= self.max_width_mm and sheet.width_mm <= self.max_height_mm))


def box_blank_size(width_mm: float, length_mm: float, height_mm: float,
                   style: str = "standard", row_count: int = 1,
                   column_count: int = 1) -> Rect:
    """Return the user's supplied box blank bounds; die-line still needs validation."""
    if min(width_mm, length_mm) <= 0 or height_mm < 0 or row_count < 1 or column_count < 1:
        raise ValueError("Ürün ölçüleri pozitif, sıra sayısı en az 1 olmalıdır.")
    blank_width = (width_mm * 2 + height_mm * 2 + 15) * column_count
    if style == "standard":
        blank_height = (length_mm + height_mm + 15) * row_count + height_mm + 15
    elif style in {"dip_kilit", "dip_yapistirmali"}:
        blank_height = (length_mm + height_mm + 15 + (height_mm / 2 + 15) * 2) * row_count
        if row_count in {1, 3, 5, 6, 7, 9, 10, 11}:
            blank_height += height_mm + 15
    else:
        raise ValueError("Bilinmeyen kutu tipi.")
    return Rect(blank_width, blank_height)


def best_box_montage(sheet: Rect, width_mm: float, length_mm: float,
                     height_mm: float, style: str = "standard",
                     max_rows: int = 12, max_columns: int = 4) -> dict:
    """Search row/column groupings and both orientations for box blank yield."""
    best = {"product_count": 0, "rows": 0, "columns": 0, "blank": None}
    for rows in range(1, max_rows + 1):
        for columns in range(1, max_columns + 1):
            blank = box_blank_size(width_mm, length_mm, height_mm, style, rows, columns)
            groups = rectangular_imposition(sheet, blank, gap_mm=0)
            products = groups * rows * columns
            if (products > best["product_count"] or
                    (products == best["product_count"] and rows * columns > best["rows"] * best["columns"])):
                best = {"product_count": products, "rows": rows,
                        "columns": columns, "blank": blank}
    return best


def bobin_cutting_allowed(paper_name: str, paper_kg: float) -> bool:
    """Bristol/Krome stay on 70x100 through 600 kg; bobin is considered above it."""
    return paper_name in {"Amerikan Bristol", "Krome Karton"} and paper_kg > 600.0


def rectangular_imposition(sheet: Rect, product: Rect, gap_mm: float = 3.0) -> int:
    """Max grid yield for either orientation; no hidden efficiency multiplier."""
    if min(sheet.width_mm, sheet.height_mm, product.width_mm, product.height_mm) <= 0:
        return 0
    def count(w: float, h: float) -> int:
        return int((sheet.width_mm + gap_mm) // (w + gap_mm)) * int((sheet.height_mm + gap_mm) // (h + gap_mm))
    return max(count(product.width_mm, product.height_mm), count(product.height_mm, product.width_mm))


def score_candidate(*, stock: Rect, press_sheet: Rect, product: Rect, quantity: int,
                    gsm: float, paper_ton_cost: float, press: Machine,
                    cutter: Machine, stock_sheets_per_press: int = 1,
                    box_blank: bool = False, gap_mm: float = 3.0) -> dict | None:
    """Return a costed, capacity-checked candidate; None means infeasible."""
    if (quantity <= 0 or gsm <= 0 or stock_sheets_per_press < 1
            or not press.fits(press_sheet) or not cutter.fits(stock)):
        return None
    yield_per_sheet = rectangular_imposition(press_sheet, product, gap_mm)
    if yield_per_sheet == 0:
        return None
    net_press = ceil(quantity / yield_per_sheet)
    # No fabricated waste percentage: callers supply their validated make-ready allowance.
    press_sheets = net_press
    stock_sheets = ceil(press_sheets / stock_sheets_per_press)
    area_m2 = stock.width_mm * stock.height_mm / 1_000_000
    kg = stock_sheets * area_m2 * gsm / 1000
    paper_cost = kg / 1000 * paper_ton_cost
    if press.setup_cost is None or press.run_cost_per_1000 is None or cutter.setup_cost is None or cutter.run_cost_per_1000 is None:
        press_cost = cutter_cost = None
        total = None
    else:
        press_cost = press.setup_cost + max(0, press_sheets - 2000) / 1000 * press.run_cost_per_1000
        cutter_cost = cutter.setup_cost + stock_sheets / 1000 * cutter.run_cost_per_1000
        total = paper_cost + press_cost + cutter_cost
    return {
        "stock_sheets": stock_sheets, "press_sheets": press_sheets,
        "yield_per_sheet": yield_per_sheet, "kg": kg, "paper_cost": paper_cost,
        "press_cost": press_cost, "cutter_cost": cutter_cost, "total_cost": total,
        "press": press.name, "cutter": cutter.name,
        "die_line_validation_required": box_blank,
    }


def recommend(candidates: Iterable[dict]) -> dict[str, dict | None]:
    """Select independent cost, paper and balanced recommendations."""
    rows = list(candidates)
    priced = [r for r in rows if r.get("total_cost") is not None]
    return {
        "lowest_total_cost": min(priced, key=lambda r: r["total_cost"], default=None),
        "lowest_paper_use": min(rows, key=lambda r: r["kg"], default=None),
        # Balanced ranking normalizes paper and known operating cost, then averages.
        "balanced": min(priced, key=lambda r: (r["kg"] / max(1.0, max(x["kg"] for x in priced))
                     + r["total_cost"] / max(1.0, max(x["total_cost"] for x in priced))) / 2, default=None),
    }
