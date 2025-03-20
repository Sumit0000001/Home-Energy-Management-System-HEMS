import unittest
from models.ev_model import EVModel
from config import PARAMETERS, SETS

class TestEVModel(unittest.TestCase):
    def setUp(self):
        """Initialize the model before tests."""
        self.ev_model = EVModel()
        self.ev_model.solve()
        self.results = self.ev_model.get_results()

    def test_ev_charge_limits(self):
        """Ensure EV charging power does not exceed limit."""
        for h in self.results["Pevcha"]:
            max_charge = PARAMETERS["Pevcharateps1"][h]
            self.assertLessEqual(self.results["Pevcha"][h], max_charge, f"Charge power exceeded for {h}")

    def test_ev_discharge_limits(self):
        """Ensure EV discharging power does not exceed limit."""
        for h in self.results["Pevdis"]:
            max_discharge = PARAMETERS["Pevdisrateps1"][h]
            self.assertLessEqual(self.results["Pevdis"][h], max_discharge, f"Discharge power exceeded for {h}")

    def test_ev_energy_within_limits(self):
        """Ensure SOEev remains within its min and max limits."""
        for h in self.results["SOEev"]:
            min_soe = PARAMETERS["SOEevminps1"][h]
            max_soe = PARAMETERS["SOEevmaxps1"][h]
            self.assertGreaterEqual(self.results["SOEev"][h], min_soe, f"SOEev too low for {h}")
            self.assertLessEqual(self.results["SOEev"][h], max_soe, f"SOEev too high for {h}")

if __name__ == "__main__":
    unittest.main()
