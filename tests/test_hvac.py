import unittest
from models.hvac_model import HVACModel
from config import PARAMETERS, SETS

class TestHVACModel(unittest.TestCase):
    def setUp(self):
        """Initialize the model before tests."""
        self.hvac_model = HVACModel()
        self.hvac_model.solve()
        self.results = self.hvac_model.get_results()

    def test_temperature_within_limits(self):
        """Ensure indoor temperature stays within set bounds."""
        for h in self.results["Tr"]:
            min_temp = PARAMETERS["Trminps1"][h]
            max_temp = PARAMETERS["Trmaxps1"][h]
            self.assertGreaterEqual(self.results["Tr"][h], min_temp, f"Temperature too low for {h}")
            self.assertLessEqual(self.results["Tr"][h], max_temp, f"Temperature too high for {h}")

    def test_hvac_power_logic(self):
        """Ensure HVAC power follows on/off binary constraint."""
        for h in self.results["Pac"]:
            expected_power = PARAMETERS["ACpowerps1"][h] if self.results["Pac"][h] > 0 else 0
            self.assertEqual(self.results["Pac"][h], expected_power, f"HVAC power inconsistency for {h}")

if __name__ == "__main__":
    unittest.main()
