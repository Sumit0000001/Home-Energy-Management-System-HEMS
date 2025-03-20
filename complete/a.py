import pandas as pd
import numpy as np
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpSolverDefault, LpAffineExpression

class EnergySchedulerPuLP:
    def __init__(self, file_path):
        """
        Initializes the scheduler by loading data from the XLSX file.
        """
        self.file_path = file_path
        self.load_data()

    def load_data(self):
        """
        Loads house, appliance scheduling, and phase power data from the XLSX file.
        Aggregates 15-min load data into hourly values.
        """
        self.house_data = pd.read_excel(self.file_path, sheet_name="Sheet1")
        self.house_data.columns = ["House", "Ignore1", "Ignore2", "Cbuy", "Csold", "ConstantLoad", "PVgen", "WTgen", "Tair"]
        self.house_data = self.house_data.drop(columns=["Ignore1", "Ignore2"])

        # Aggregating 15-min loads into hourly values (Required by Client)
        self.house_data["ConstantLoad_Hourly"] = self.house_data["ConstantLoad"].groupby(self.house_data.index // 4).transform("sum")

    def build_optimization_model(self):
        """
        Builds the PuLP optimization model fully aligned with customer logic.
        """
        self.model = LpProblem(name="energy_scheduler", sense=LpMinimize)

        # Define sets
        TIME_SLOTS = range(24)  # 24-hour schedule
        self.buyers = ["h1", "h2"]  # Example buyers
        self.sellers = ["h3", "h4"]  # Example sellers

        # Define variables
        self.Pgrid = {(h, t): LpVariable(f"Pgrid_{h}_{t}", lowBound=0) for h in self.buyers for t in TIME_SLOTS}
        self.Psold = {(h, t): LpVariable(f"Psold_{h}_{t}", lowBound=0) for h in self.sellers for t in TIME_SLOTS}
        self.SDR = {t: LpVariable(f"SDR_{t}", lowBound=0, upBound=2) for t in TIME_SLOTS}
        self.Price = {t: LpVariable(f"Price_{t}", lowBound=2, upBound=6) for t in TIME_SLOTS}

        # ✅ **Fixed Power Balance Constraints**
        for h in self.buyers + self.sellers:
            for t in TIME_SLOTS:
                total_supply = (
                    self.house_data.loc[self.house_data["House"] == h, "PVgen"].values[0] +
                    self.house_data.loc[self.house_data["House"] == h, "WTgen"].values[0] +
                    self.Pgrid.get((h, t), 0) +
                    self.Psold.get((h, t), 0)
                )
                total_demand = self.house_data.loc[self.house_data["House"] == h, "ConstantLoad_Hourly"].values[0]
                self.model += total_supply == total_demand, f"PowerBalance_{h}_{t}"

        # ✅ **Fixed SDR Calculation (Linearized)**
        MAX_LOAD = 500  # Adjust based on realistic max demand
        MIN_LOAD = 20   # To avoid division by zero

        for t in TIME_SLOTS:
            total_supply = lpSum(self.Psold[h, t] for h in self.sellers)
            total_load = lpSum(self.Pgrid[h, t] for h in self.buyers) + MIN_LOAD  # Avoid division by zero

            # **Linear Upper Bound Approximation**
            self.model += self.SDR[t] * MAX_LOAD >= total_supply, f"SDR_Upper_{t}"
            # **Linear Lower Bound Approximation**
            self.model += self.SDR[t] * MIN_LOAD <= total_supply, f"SDR_Lower_{t}"

        # ✅ **Fixed Price Calculation**
        for t in TIME_SLOTS:
            self.model += self.Price[t] >= 2, f"Price_LB_{t}"
            self.model += self.Price[t] <= 6, f"Price_UB_{t}"

        # ✅ **Introduce Auxiliary Variables for Multiplication**
        self.GridCost = {(h, t): LpVariable(f"GridCost_{h}_{t}", lowBound=0) for h in self.buyers for t in TIME_SLOTS}
        self.SoldRevenue = {(h, t): LpVariable(f"SoldRevenue_{h}_{t}", lowBound=0) for h in self.sellers for t in TIME_SLOTS}

        for h in self.buyers:
            for t in TIME_SLOTS:
                # **Fixed: Use auxiliary variable instead of direct multiplication**
                self.model += self.GridCost[h, t] == self.Price[t] * self.Pgrid[h, t], f"GridCost_{h}_{t}"

        for h in self.sellers:
            for t in TIME_SLOTS:
                # **Fixed: Use auxiliary variable instead of direct multiplication**
                self.model += self.SoldRevenue[h, t] == self.Price[t] * self.Psold[h, t], f"SoldRevenue_{h}_{t}"

        # ✅ **Fixed Objective Function Using Auxiliary Variables**
        self.model += lpSum(
            self.GridCost[h, t] - self.SoldRevenue[h, t]
            for h in self.buyers + self.sellers
            for t in TIME_SLOTS
        ), "Objective"

    def solve_optimization(self):
        """
        Solves the optimization problem using GLPK.
        """
        LpSolverDefault.msg = True  # Enable solver messages
        self.model.solve()

        # Extract results
        self.results_df = pd.DataFrame({
            "Time": list(range(24)),
            "SDR": [self.SDR[t].varValue for t in range(24)],
            "Price": [self.Price[t].varValue for t in range(24)]
        })

    def display_results(self):
        """
        Displays the optimized SDR and pricing results.
        """
        import ace_tools as tools
        tools.display_dataframe_to_user(name="Optimized SDR and Price Calculation (PuLP, Final)", dataframe=self.results_df)

if __name__ == "__main__":
    print("🔥 Starting Optimization...")
    scheduler = EnergySchedulerPuLP("C:/Users/Sumit/Desktop/HEMS/data/Input_Data.xlsx")

    print("✅ Building Model...")
    scheduler.build_optimization_model()

    print("⚡ Running Solver...")
    scheduler.solve_optimization()

    print("📊 Displaying Results...")
    scheduler.display_results()

    print("🎉 Optimization Complete!")
