import unittest
from pyomo.environ import value
from models.grid_model import GridModel
from data_loader import DataLoader


class TestGridModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load dataset and initialize GridModel before running tests"""
        loader = DataLoader()
        loader.load_data()
        cls.data = loader.data
        cls.grid_model = GridModel(cls.data)
        cls.grid_model.solve()
        cls.results = cls.grid_model.get_results()

    def test_buyers_cannot_sell(self):
        """Ensure buyers (h1-h5) do not sell power"""
        for h in self.grid_model.buyers:
            self.assertEqual(
                self.results["Psold"][h], 0.0,
                f"Buyer {h} should not sell power!"
            )

    def test_sellers_cannot_buy(self):
        """Ensure sellers (h6-h10) do not buy power"""
        for h in self.grid_model.sellers:
            self.assertEqual(
                self.results["Pgrid"][h], 0.0,
                f"Seller {h} should not buy power!"
            )

    def test_non_negative_power_values(self):
        """Ensure all power values are non-negative"""
        for h in self.grid_model.households:
            self.assertGreaterEqual(
                self.results["Pgrid"][h], 0.0,
                f"Pgrid[{h}] should be non-negative"
            )
            self.assertGreaterEqual(
                self.results["Psold"][h], 0.0,
                f"Psold[{h}] should be non-negative"
            )

    def test_model_solves_successfully(self):
        """Ensure the model runs successfully without errors"""
        self.assertIsNotNone(self.results, "Model did not return any results!")

    def test_power_limits_are_respected(self):
        """Ensure grid power does not exceed max limits (PL1 & PL2)"""
        for h in self.grid_model.households:
            self.assertLessEqual(
                self.results["Pgrid"][h], self.grid_model.PL1_values[h],
                f"Pgrid[{h}] exceeds max allowed PL1 limit!"
            )
            self.assertLessEqual(
                self.results["Psold"][h], self.grid_model.PL2_values[h],
                f"Psold[{h}] exceeds max allowed PL2 limit!"
            )


if __name__ == "__main__":
    unittest.main()
