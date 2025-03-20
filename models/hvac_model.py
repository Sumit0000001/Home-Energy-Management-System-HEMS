from pyomo.environ import ConcreteModel, Var, Objective, Constraint, SolverFactory, NonNegativeReals, Binary
from config import PARAMETERS, SETS

class HVACModel:
    def __init__(self):
        self.model = ConcreteModel()
        self.define_variables()
        self.define_constraints()
        self.define_objective()

    def define_variables(self):
        """Define decision variables for HVAC operation."""
        homes = SETS["homes"]

        # Indoor temperature (Tr)
        self.model.Tr = Var(homes, within=NonNegativeReals)

        # HVAC power consumption
        self.model.Pac = Var(homes, within=NonNegativeReals)

        # Binary variable to switch HVAC on/off
        self.model.Uac = Var(homes, within=Binary)

    def define_constraints(self):
        """Define constraints for HVAC temperature control and power limits."""
        homes = SETS["homes"]

        # Room temperature bounds
        def temperature_max_constraint(model, h):
            return model.Tr[h] <= PARAMETERS["Trmaxps1"][h]
        self.model.TempMax = Constraint(homes, rule=temperature_max_constraint)

        def temperature_min_constraint(model, h):
            return model.Tr[h] >= PARAMETERS["Trminps1"][h]
        self.model.TempMin = Constraint(homes, rule=temperature_min_constraint)

        # HVAC power consumption model
        def hvac_power_constraint(model, h):
            return model.Pac[h] == PARAMETERS["ACpowerps1"][h] * model.Uac[h]
        self.model.HVACPower = Constraint(homes, rule=hvac_power_constraint)

        # Thermal balance equation
        def thermal_balance(model, h):
            return model.Tr[h] == (0.8258 * PARAMETERS["Trinips1"][h]) + (0.1741 * PARAMETERS["Trminps1"][h]) - (model.Uac[h] * (PARAMETERS["COPps1"][h] * PARAMETERS["ACpowerps1"][h]) / 0.4975)
        self.model.ThermalBalance = Constraint(homes, rule=thermal_balance)

    def define_objective(self):
        """Define objective function (Minimize HVAC energy cost)."""
        homes = SETS["homes"]
        self.model.cost = Objective(
            expr=sum(
                self.model.Pac[h] * PARAMETERS["PL1ps1"][h] for h in homes
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
            "Tr": {h: self.model.Tr[h].value for h in self.model.Tr},
            "Pac": {h: self.model.Pac[h].value for h in self.model.Pac}
        }

# If run as standalone script, test the model
if __name__ == "__main__":
    hvac_model = HVACModel()
    hvac_model.solve()
    results = hvac_model.get_results()
    
    print("HVAC Model Results:")
    print(results)

