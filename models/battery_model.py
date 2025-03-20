from pyomo.environ import ConcreteModel, Var, Objective, Constraint, SolverFactory, NonNegativeReals, Binary

class BatteryModel:
    def __init__(self, data):
        self.data = data
        self.battery_params = data['battery_params']
        self.model = ConcreteModel()
        self.define_variables()
        self.define_constraints()
        self.define_objective()

    def define_variables(self):
        """Define decision variables for battery charging, discharging, and SOE."""
        households = list(self.battery_params['Pbcharateps1'].keys())  # Get households h1-h5

        self.model.Pbcha = Var(households, within=NonNegativeReals)
        self.model.Pbdis = Var(households, within=NonNegativeReals)
        self.model.SOEb = Var(households, within=NonNegativeReals)
        self.model.Ub = Var(households, within=Binary)

    def define_constraints(self):
        """Define constraints for battery charge/discharge limits and SOE balance."""
        households = list(self.battery_params['Pbcharateps1'].keys())

        # Battery charge limit
        def charge_limit(model, h):
            return model.Pbcha[h] <= self.battery_params['Pbcharateps1'][h] * model.Ub[h]
        self.model.ChargeLimit = Constraint(households, rule=charge_limit)

        # Battery discharge limit
        def discharge_limit(model, h):
            return model.Pbdis[h] <= self.battery_params['Pbdisrateps1'][h] * (1 - model.Ub[h])
        self.model.DischargeLimit = Constraint(households, rule=discharge_limit)

        # Battery energy balance constraint with CE & DE
        def energy_balance(model, h):
            return model.SOEb[h] == (
                self.battery_params['SOEbinips1'][h] + 
                (self.battery_params['CE'] * model.Pbcha[h]) - 
                (model.Pbdis[h] / self.battery_params['DE'])
            )
        self.model.EnergyBalance = Constraint(households, rule=energy_balance)

        # SOE limits
        self.model.SOEMax = Constraint(households, rule=lambda m, h: m.SOEb[h] <= self.battery_params['SOEbmaxps1'][h])
        self.model.SOEMin = Constraint(households, rule=lambda m, h: m.SOEb[h] >= self.battery_params['SOEbminps1'][h])

    def define_objective(self):
        """Define objective function (Minimize battery energy costs)."""
        households = list(self.battery_params['Pbcharateps1'].keys())
        self.model.cost = Objective(
            expr=sum(
                self.model.Pbcha[h] * 8.5  # Assuming Cbuy = 8.5 (from Sheet1)
                - self.model.Pbdis[h] * 3.5  # Assuming Csold = 3.5 (from Sheet1)
                for h in households
            ),
            sense=1  # Minimize cost
        )

    def solve(self, solver="glpk"):
        """Solve the Pyomo model using the specified solver."""
        solver = SolverFactory(solver)
        result = solver.solve(self.model)
        return result

    def get_results(self):
        """Extract results after solving."""
        return {
            "Pbcha": {h: self.model.Pbcha[h].value for h in self.model.Pbcha},
            "Pbdis": {h: self.model.Pbdis[h].value for h in self.model.Pbdis},
            "SOEb": {h: self.model.SOEb[h].value for h in self.model.SOEb}
        }

# If run as standalone script, test the model
if __name__ == "__main__":
    from data_loader import DataLoader

    loader = DataLoader()
    loader.load_data()
    data = loader.data

    battery_model = BatteryModel(data)
    battery_model.solve()
    results = battery_model.get_results()

    print("Battery Model Results:")
    print(results)
