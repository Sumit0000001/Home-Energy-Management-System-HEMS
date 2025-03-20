import pandas as pd

class DataLoader:
    def __init__(self, file_path="data/Input_Data.xlsx"):
        self.file_path = file_path
        self.data = {}

    def load_data(self):
        xls = pd.ExcelFile(self.file_path)

        # Load household and appliance data
        self.data['households'] = xls.parse('Sheet1')
        self.data['appliances'] = xls.parse('Sheet2')
        self.data['phase_power'] = xls.parse('Sheet3')

        # Strip spaces from column names
        for key in self.data:
            self.data[key].columns = self.data[key].columns.str.strip()

        # 🔹 Define missing battery parameters manually (from GAMS)
        self.data['battery_params'] = {
            'Pbcharateps1': {'h1': 1.3, 'h2': 1.2, 'h3': 1.0, 'h4': 1.3, 'h5': 1.2},
            'Pbdisrateps1': {'h1': 1.0, 'h2': 1.0, 'h3': 0.8, 'h4': 1.0, 'h5': 1.0},
            'SOEbinips1': {'h1': 1.0, 'h2': 1.0, 'h3': 0.8, 'h4': 1.0, 'h5': 1.0},
            'SOEbmaxps1': {'h1': 3.0, 'h2': 3.0, 'h3': 2.8, 'h4': 3.0, 'h5': 3.0},
            'SOEbminps1': {'h1': 0.5, 'h2': 0.5, 'h3': 0.4, 'h4': 0.5, 'h5': 0.5},
            'CE': 0.9,  # Charging Efficiency
            'DE': 0.9   # Discharging Efficiency
        }

        print("✅ Battery parameters including CE & DE loaded from GAMS fixed values.")

    def get_household_data(self):
        """Return household energy data (buyers: first 5, sellers: next 5)."""
        df = self.data['households']

        # Extract unique households while maintaining order
        unique_households = list(dict.fromkeys(df['Household']))

        # Ensure at least 10 unique households exist
        if len(unique_households) < 10:
            raise ValueError(f"Insufficient unique households. Expected at least 10, found {len(unique_households)}.")

        # Select buyers (first 5) and sellers (next 5)
        buyer_households = unique_households[:5]  # Buyers: h1-h5
        seller_households = unique_households[5:10]  # Sellers: h6-h10

        # Filter dataset to retain all time steps for selected buyers & sellers
        buyers = df[df['Household'].isin(buyer_households)]
        sellers = df[df['Household'].isin(seller_households)]

        return buyers, sellers

    def get_battery_params(self):
        """Return battery-related fixed parameters."""
        return self.data['battery_params']

# If run as standalone script, test the loader
if __name__ == "__main__":
    loader = DataLoader()
    loader.load_data()
    battery_params = loader.get_battery_params()

    print("\nBattery Parameters:")
    for param, values in battery_params.items():
        print(f"{param}: {values}")
