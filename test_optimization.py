import unittest

from optimization import Machine, Rect, best_box_montage, bobin_cutting_allowed, box_blank_size, rectangular_imposition, recommend, score_candidate


class OptimizationTests(unittest.TestCase):
    def test_grid_yield_checks_both_orientations_without_multiplier(self):
        self.assertEqual(rectangular_imposition(Rect(700, 1000), Rect(333, 350)), 4)

    def test_standard_box_keeps_existing_blank_formula(self):
        self.assertEqual(box_blank_size(100, 150, 50), Rect(315, 280))

    def test_standard_box_eight_up_module_matches_user_formula(self):
        self.assertEqual(box_blank_size(100, 150, 50, "standard", 4, 2), Rect(630, 925))
        montage = best_box_montage(Rect(685, 1000), 100, 150, 50)
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


if __name__ == "__main__":
    unittest.main()
