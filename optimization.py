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
