from pyomo.environ import (
    ConcreteModel, Var, Objective, Constraint, SolverFactory, 
    NonNegativeReals, Binary, Param, minimize , Set
)
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_loader import DataLoader


class GridModel:
    def __init__(self, data):
        self.data = data  # Household energy data
        self.model = ConcreteModel()

        # Define households
        self.households = self.data['households']['Household'].astype(str).str.strip().tolist()
        self.buyers = self.households[:5]  # h1-h5
        self.sellers = self.households[5:]  # h6-h10

        # Manually defined power limits for PL1 and PL2 (since they are missing in the dataset)
        self.PL1_values = {h: 10 for h in self.households}  # Max grid buy power (10 KW)
        self.PL2_values = {h: 10 for h in self.households}  # Max grid sell power (10 KW)

        self.define_parameters()
        self.define_variables()
        self.define_constraints()
        self.define_objective()

    def define_parameters(self):
        """Define sets and fixed parameters like power limits."""
        self.model.households = Set(initialize=self.households)  # Define households as a Pyomo Set

        # Define power limit parameters
        self.model.PL1 = Param(self.model.households, initialize=self.PL1_values)
        self.model.PL2 = Param(self.model.households, initialize=self.PL2_values)


    def define_variables(self):
        """Define decision variables for grid power usage and sales."""
        # Power drawn from grid (Only for Buyers)
        self.model.Pgrid = Var(self.households, within=NonNegativeReals)

        # Power sold to grid (Only for Sellers)
        self.model.Psold = Var(self.households, within=NonNegativeReals)

        # Binary variable to switch between buying & selling
        self.model.Ugrid = Var(self.households, within=Binary)

    def define_constraints(self):
        """Define constraints for grid power limits."""
        model = self.model

        # Buyers can only buy, not sell
        def grid_buy_constraint(model, h):
            if h in self.buyers:
                return model.Psold[h] == 0  # Ensure buyers cannot sell power
            return Constraint.Skip

        model.BuyersCannotSell = Constraint(self.households, rule=grid_buy_constraint)

        # Sellers can only sell, not buy
        def grid_sell_constraint(model, h):
            if h in self.sellers:
                return model.Pgrid[h] == 0  # Ensure sellers cannot buy power
            return Constraint.Skip

        model.SellersCannotBuy = Constraint(self.households, rule=grid_sell_constraint)

        # Buyers can buy up to PL1 limit
        def buyers_power_limit(model, h):
            if h in self.buyers:
                return model.Pgrid[h] <= model.PL1[h]
            return Constraint.Skip

        model.BuyersPowerLimit = Constraint(self.households, rule=buyers_power_limit)

        # Sellers can sell up to PL2 limit
        def sellers_power_limit(model, h):
            if h in self.sellers:
                return model.Psold[h] <= model.PL2[h]
            return Constraint.Skip

        model.SellersPowerLimit = Constraint(self.households, rule=sellers_power_limit)



    def define_objective(self):
        """Define objective function to minimize cost for buyers and maximize revenue for sellers."""

        def objective_rule(model):
            return sum(
                model.Pgrid[h] * float(self.data['households'].set_index('Household').loc[h, 'Cbuy'].iloc[0]) -
                model.Psold[h] * float(self.data['households'].set_index('Household').loc[h, 'Csold'].iloc[0])
                for h in self.households
            )

        self.model.cost = Objective(rule=objective_rule, sense=minimize)

    def solve(self, solver="glpk"):
        """Solve the Pyomo model using the specified solver."""
        solver = SolverFactory(solver)
        result = solver.solve(self.model, tee=True)
        return result

    def get_results(self):
        """Extract results after solving."""
        return {
            "Pgrid": {h: self.model.Pgrid[h].value for h in self.model.Pgrid},
            "Psold": {h: self.model.Psold[h].value for h in self.model.Psold}
        }


# If run as standalone script, test the model
if __name__ == "__main__":
    loader = DataLoader()
    loader.load_data()
    data = loader.data

    grid_model = GridModel(data)
    grid_model.solve()
    results = grid_model.get_results()
    
    print("Grid Power Results:")
    print(results)
