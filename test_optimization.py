import ast
import math
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# Load just the pure planning helpers from the single application source file,
# without importing Streamlit's interactive page.
app_source = Path(__file__).with_name("MatbaaMaliyet.py").read_text(encoding="utf-8-sig")
app_tree = ast.parse(app_source)
helper_names = {"Rect", "Machine", "box_blank_size", "best_box_montage",
                "bobin_cutting_allowed", "rectangular_imposition", "rectangular_imposition_layout",
                "score_candidate", "recommend",
                "estimate_knife_cost", "tiered_operation_cost", "press_cost_from_params",
                "cutting_operation_cost", "layout_process_costs", "sheet_fits_limits",
                "automatic_postpress_for_product", "included_quantity_operation_cost",
                "pricing_summary"}
helper_nodes = [node for node in app_tree.body
                if getattr(node, "name", None) in helper_names]
helper_namespace = {"__name__": "matbaa_helpers", "dataclass": dataclass,
                    "ceil": math.ceil, "Iterable": Iterable}
exec(compile(ast.Module(body=helper_nodes, type_ignores=[]), "MatbaaMaliyet.py", "exec"), helper_namespace)
Rect = helper_namespace["Rect"]
Machine = helper_namespace["Machine"]
best_box_montage = helper_namespace["best_box_montage"]
bobin_cutting_allowed = helper_namespace["bobin_cutting_allowed"]
box_blank_size = helper_namespace["box_blank_size"]
rectangular_imposition = helper_namespace["rectangular_imposition"]
rectangular_imposition_layout = helper_namespace["rectangular_imposition_layout"]
recommend = helper_namespace["recommend"]
score_candidate = helper_namespace["score_candidate"]
estimate_knife_cost = helper_namespace["estimate_knife_cost"]
tiered_operation_cost = helper_namespace["tiered_operation_cost"]
cutting_operation_cost = helper_namespace["cutting_operation_cost"]
included_quantity_operation_cost = helper_namespace["included_quantity_operation_cost"]
press_cost_from_params = helper_namespace["press_cost_from_params"]
layout_process_costs = helper_namespace["layout_process_costs"]
sheet_fits_limits = helper_namespace["sheet_fits_limits"]
automatic_postpress_for_product = helper_namespace["automatic_postpress_for_product"]
pricing_summary = helper_namespace["pricing_summary"]


class OptimizationTests(unittest.TestCase):
    def test_sheet_layout_reports_real_columns_and_rows(self):
        layout = rectangular_imposition_layout(Rect(100, 200), Rect(90, 90), gap_mm=0)
        self.assertEqual(layout, {"count": 2, "columns": 1, "rows": 2})

    def test_cost_markup_reports_profit_and_gross_margin(self):
        summary = pricing_summary(1000, 30)
        self.assertEqual(summary["total_profit"], 300)
        self.assertEqual(summary["total_sales"], 1300)
        self.assertAlmostEqual(summary["gross_margin_percent"], 300 / 1300 * 100)

    def test_box_product_selection_automatically_sets_box_cutting_and_gluing(self):
        for product_type in ("Standart Kutu", "Dip Kilitli Kutu", "Dip Kilit Yapıştırmalı Kutu"):
            with self.subTest(product_type=product_type):
                self.assertEqual(
                    automatic_postpress_for_product(product_type),
                    "Kutu Kesim + Yapıştırma",
                )
        self.assertIsNone(automatic_postpress_for_product("Kartonet"))

    def test_standard_and_dip_lock_boxes_use_same_default_gluing_tariff(self):
        params = {
            "b_3550_cmyk": 1800, "b_3550_pantone": 900, "b_3550_tiraj": 400,
            "kazanli": 1800, "kazanli_tiraj": 0.75,
            "bicak_metre_fiyati": 500,
            "omega_tek": 2000, "omega_tek_tiraj": 0.2,
            "omega_dip": 2500, "omega_dip_tiraj": 0.25,
        }
        glue_costs = []
        for product_type in ("Standart Kutu", "Dip Kilitli Kutu"):
            costs = layout_process_costs(
                params=params,
                press_code="3550",
                sheet_quantity=1000,
                order_quantity=5000,
                cutting_machine="Kazanlı Kesim",
                cmyk_enabled=True,
                pantone_colors=0,
                lamination="Yok",
                special_finishes=[],
                product_width_mm=100,
                product_length_mm=150,
                is_box=True,
                is_dip_glued=False,
                special_cut=False,
                postpress=automatic_postpress_for_product(product_type),
                total_area_m2=1.0,
            )
            glue_costs.append(costs["Yapıştırma"])
        self.assertEqual(glue_costs, [2000, 2000])

    def test_gluing_setup_includes_first_10000_units(self):
        self.assertEqual(included_quantity_operation_cost(5000, 10000, 2000, 0.2), 2000)
        self.assertEqual(included_quantity_operation_cost(10000, 10000, 2000, 0.2), 2000)
        self.assertEqual(included_quantity_operation_cost(15000, 10000, 2000, 0.2), 3000)
        self.assertEqual(included_quantity_operation_cost(15000, 10000, 2500, 0.25), 3750)

    def test_dip_glued_box_adds_dip_tariff_only_above_included_quantity(self):
        params = {
            "b_3550_cmyk": 1800, "b_3550_pantone": 900, "b_3550_tiraj": 400,
            "kazanli": 1800, "kazanli_tiraj": 0.75,
            "bicak_metre_fiyati": 500,
            "omega_tek": 2000, "omega_tek_tiraj": 0.2,
            "omega_dip": 2500, "omega_dip_tiraj": 0.25,
        }
        costs = layout_process_costs(
            params=params,
            press_code="3550",
            sheet_quantity=1000,
            order_quantity=15000,
            cutting_machine="Kazanlı Kesim",
            cmyk_enabled=True,
            pantone_colors=0,
            lamination="Yok",
            special_finishes=[],
            product_width_mm=100,
            product_length_mm=150,
            is_box=True,
            is_dip_glued=True,
            special_cut=False,
            postpress=automatic_postpress_for_product("Dip Kilit Yapıştırmalı Kutu"),
            total_area_m2=1.0,
        )
        self.assertEqual(costs["Yapıştırma"], 6750)

    def test_grid_yield_checks_both_orientations_without_multiplier(self):
        self.assertEqual(rectangular_imposition(Rect(700, 1000), Rect(333, 350)), 4)

    def test_standard_box_keeps_existing_blank_formula(self):
        self.assertEqual(box_blank_size(100, 150, 50), Rect(315, 280))

    def test_standard_box_eight_up_module_matches_user_formula(self):
        self.assertEqual(box_blank_size(100, 150, 50, "standard", 4, 2), Rect(630, 925))
        montage = best_box_montage(Rect(685, 1000), 100, 150, 50)
        self.assertEqual(montage["count"], 8)
        self.assertEqual(montage["product_count"], 8)
        self.assertEqual((montage["columns"], montage["rows"], montage["blank"]),
                         (2, 4, Rect(630, 925)))

    def test_dip_lock_even_rows_use_base_formula_times_rows(self):
        self.assertEqual(box_blank_size(100, 150, 50, "dip_kilit", 2), Rect(315, 590))

    def test_dip_lock_odd_rows_add_end_flap_allowance(self):
        self.assertEqual(box_blank_size(100, 150, 50, "dip_yapistirmali", 3), Rect(315, 950))

    def test_bobin_cutting_starts_only_above_600_kg_for_bristol_and_krome(self):
        self.assertFalse(bobin_cutting_allowed("Amerikan Bristol", 600))
        self.assertFalse(bobin_cutting_allowed("Krome Karton", 600))
        self.assertTrue(bobin_cutting_allowed("Krome Karton", 600.01))
        self.assertFalse(bobin_cutting_allowed("Kuşe Kağıt", 800))

    def test_press_capacity_rejects_oversize(self):
        press = Machine("35x50", 500, 350, 100, 10)
        cutter = Machine("cutter", 700, 1000, 20, 2)
        self.assertIsNone(score_candidate(stock=Rect(700, 1000), press_sheet=Rect(700, 1000),
            product=Rect(100, 150), quantity=1000, gsm=300, paper_ton_cost=1000,
            press=press, cutter=cutter))

    def test_missing_real_rates_are_not_fabricated(self):
        press = Machine("press", 700, 1000, None, None)
        cutter = Machine("cutter", 700, 1000, None, None)
        result = score_candidate(stock=Rect(700, 1000), press_sheet=Rect(700, 1000),
            product=Rect(100, 150), quantity=1000, gsm=300, paper_ton_cost=1000,
            press=press, cutter=cutter)
        self.assertIsNone(result["total_cost"])

    def test_cutter_capacity_is_enforced_on_stock_sheet(self):
        press = Machine("press", 700, 1000, 100, 10)
        cutter = Machine("small cutter", 500, 700, 20, 2)
        self.assertIsNone(score_candidate(stock=Rect(700, 1000), press_sheet=Rect(500, 700),
            product=Rect(100, 150), quantity=1000, gsm=300, paper_ton_cost=1000,
            press=press, cutter=cutter))

    def test_recommendations_are_independent(self):
        rows = [dict(kg=10, total_cost=100), dict(kg=8, total_cost=120)]
        result = recommend(rows)
        self.assertEqual(result["lowest_total_cost"]["kg"], 10)
        self.assertEqual(result["lowest_paper_use"]["total_cost"], 120)

    def test_box_and_2d_knife_costs_convert_mm_to_meter(self):
        self.assertEqual(estimate_knife_cost(100, 150, 500, is_box=True), 900)
        self.assertEqual(estimate_knife_cost(100, 150, 500), 250)

    def test_tiered_operation_cost_adds_each_setup_tier_and_run(self):
        self.assertEqual(tiered_operation_cost(1500, 1000, 1800, 0.75), 4725)

    def test_k_bobts_charges_sheet_tariff_only_after_first_thousand(self):
        self.assertEqual(cutting_operation_cost(1000, 1000, 1800, 0.75), 1800)
        self.assertEqual(cutting_operation_cost(1500, 1000, 1800, 0.75), 2175)
        self.assertEqual(cutting_operation_cost(0, 1000, 1800, 0.75), 0)

    def test_cutting_tariffs_include_first_thousand_sheets_for_all_machines(self):
        self.assertEqual(cutting_operation_cost(600, 1000, 1800, 0.75), 1800)
        self.assertEqual(cutting_operation_cost(2672, 1000, 1800, 0.75), 3054)
        self.assertEqual(cutting_operation_cost(6515, 1000, 1800, 0.75), 5936.25)
        self.assertEqual(cutting_operation_cost(1500, 1000, 3000, 1.0), 3500)

    def test_press_tirage_is_priced_per_1000_press_sheets(self):
        params = {
            "b_3550_cmyk": 1800,
            "b_3550_pantone": 900,
            "b_3550_tiraj": 400,
        }
        self.assertEqual(press_cost_from_params(params, "3550", 1500, True, 2), 4200)
        self.assertEqual(press_cost_from_params(params, "3550", 3000, False, 0), 0)

    def test_layout_uses_the_same_press_sheet_count_for_print_and_cut(self):
        params = {
            "b_3550_cmyk": 1800, "b_3550_pantone": 900, "b_3550_tiraj": 400,
            "kazanli": 1800, "kazanli_tiraj": 0.75,
            "pedal": 1800, "pedal_tiraj": 0.75,
            "bobst": 3000, "bobst_tiraj": 1.0,
            "bicak_metre_fiyati": 500,
            "omega_tek": 2000, "omega_tek_tiraj": 0.2,
            "omega_dip": 2500, "omega_dip_tiraj": 0.25,
        }
        costs = layout_process_costs(
            params=params,
            press_code="3550",
            sheet_quantity=1500,
            order_quantity=5000,
            cutting_machine="Kazanlı Kesim",
            cmyk_enabled=True,
            pantone_colors=0,
            lamination="Yok",
            special_finishes=[],
            product_width_mm=100,
            product_length_mm=150,
            is_box=True,
            is_dip_glued=False,
            special_cut=False,
            postpress="Düz Kesim",
            total_area_m2=1.0,
            products_per_sheet=4,
        )
        self.assertEqual(costs["Baskı"], 2400)
        self.assertEqual(costs["Kesim"], 2175)
        self.assertEqual(costs["Bıçak"], 3600)

    def test_k_bobts_excess_is_based_on_print_sheets_not_order_units(self):
        params = {
            "b_3550_cmyk": 1800, "b_3550_pantone": 900, "b_3550_tiraj": 400,
            "kazanli": 1800, "kazanli_tiraj": 0.75,
            "pedal": 1800, "pedal_tiraj": 0.75,
            "bobst": 3000, "bobst_tiraj": 1.0,
            "bicak_metre_fiyati": 500,
            "omega_tek": 2000, "omega_tek_tiraj": 0.2,
            "omega_dip": 2500, "omega_dip_tiraj": 0.25,
        }
        costs = layout_process_costs(
            params=params,
            press_code="3550",
            sheet_quantity=1500,
            order_quantity=25000,
            cutting_machine="K. Bobts",
            cmyk_enabled=True,
            pantone_colors=0,
            lamination="Yok",
            special_finishes=[],
            product_width_mm=100,
            product_length_mm=150,
            is_box=False,
            is_dip_glued=False,
            special_cut=False,
            postpress="Düz Kesim",
            total_area_m2=1.0,
        )
        self.assertEqual(costs["Baskı"], 2400)
        self.assertEqual(costs["Kesim"], 2175)

    def test_cutting_machine_size_limits_allow_rotation(self):
        self.assertTrue(sheet_fits_limits(500, 700, 500, 700))
        self.assertTrue(sheet_fits_limits(700, 500, 500, 700))
        self.assertFalse(sheet_fits_limits(700, 1000, 500, 700))
        self.assertTrue(sheet_fits_limits(700, 1000, 700, 1000))


if __name__ == "__main__":
    unittest.main()
