import unittest
from data_loader import DataLoader
from models.battery_model import BatteryModel

class TestBatteryModel(unittest.TestCase):
    def setUp(self):
        """Initialize the model before tests."""
        self.loader = DataLoader("data/Input_Data.xlsx")
        self.loader.load_data()
        self.data = self.loader.data

        # Ensure we fetch battery parameters correctly
        self.battery_params = self.loader.get_battery_params()

        self.battery_model = BatteryModel(self.data)
        self.battery_model.solve()
        self.results = self.battery_model.get_results()

    def test_battery_charge_limits(self):
        """Ensure battery charging power does not exceed limit."""
        for h in self.results["Pbcha"]:
            max_charge = self.battery_params['Pbcharateps1'].get(h, None)
            self.assertIsNotNone(max_charge, f"Charge limit missing for {h}")
            self.assertLessEqual(self.results["Pbcha"][h], max_charge, f"Charge power exceeded for {h}")

    def test_battery_discharge_limits(self):
        """Ensure battery discharging power does not exceed limit."""
        for h in self.results["Pbdis"]:
            max_discharge = self.battery_params['Pbdisrateps1'].get(h, None)
            self.assertIsNotNone(max_discharge, f"Discharge limit missing for {h}")
            self.assertLessEqual(self.results["Pbdis"][h], max_discharge, f"Discharge power exceeded for {h}")

    def test_battery_energy_within_limits(self):
        """Ensure SOEb remains within its min and max limits."""
        for h in self.results["SOEb"]:
            min_soe = self.battery_params['SOEbminps1'].get(h, None)
            max_soe = self.battery_params['SOEbmaxps1'].get(h, None)
            
            self.assertIsNotNone(min_soe, f"Min SOE limit missing for {h}")
            self.assertIsNotNone(max_soe, f"Max SOE limit missing for {h}")
            
            self.assertGreaterEqual(self.results["SOEb"][h], min_soe, f"SOEb too low for {h}")
            self.assertLessEqual(self.results["SOEb"][h], max_soe, f"SOEb too high for {h}")

if __name__ == "__main__":
    unittest.main()
