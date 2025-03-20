import unittest
import sys
import os

# Ensure Python finds the HEMS module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_loader import DataLoader  # Now Python can locate this

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        """Initialize DataLoader before each test."""
        self.loader = DataLoader("data/Input_Data.xlsx")
        self.loader.load_data()

    def test_load_household_data(self):
        """Test loading of household energy data (buyers & sellers)."""
        buyers, sellers = self.loader.get_household_data()

        # Extract unique households
        unique_buyers = buyers['Household'].unique()
        unique_sellers = sellers['Household'].unique()

        # Ensure exactly 5 unique buyers and 5 unique sellers
        self.assertEqual(len(unique_buyers), 5, "Buyers should contain exactly 5 unique households.")
        self.assertEqual(len(unique_sellers), 5, "Sellers should contain exactly 5 unique households.")

        # Ensure all time slots exist for each buyer
        expected_rows_per_buyer = 24  # Assuming 24 hourly records per household
        for household in unique_buyers:
            self.assertEqual(len(buyers[buyers['Household'] == household]), expected_rows_per_buyer)

        # Ensure all time slots exist for each seller
        for household in unique_sellers:
            self.assertEqual(len(sellers[sellers['Household'] == household]), expected_rows_per_buyer)


    def test_load_appliance_data(self):
        """Test loading of appliance scheduling data."""
        appliances = self.loader.get_appliance_data()
        self.assertGreater(len(appliances), 0)  # Ensure data exists

    def test_load_phase_power_data(self):
        """Test loading of phase-wise power consumption data."""
        phase_power = self.loader.get_phase_power_data()
        self.assertGreater(len(phase_power), 0)  # Ensure data exists

if __name__ == "__main__":
    unittest.main()
