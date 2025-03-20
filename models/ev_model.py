from pyomo.environ import ConcreteModel, Var, Objective, Constraint, SolverFactory, NonNegativeReals, Binary
from config import PARAMETERS, SETS

class EVModel:
    def __init__(self):
        self.model = ConcreteModel()
        self.define_variables()
        self.define_constraints()
        self.define_objective()

    def define_variables(self):
        """Define decision variables for EV charging, discharging, and SOE."""
        homes = SETS["homes"]

        # EV charge & discharge power
        self.model.Pevcha = Var(homes, within=NonNegativeReals)
        self.model.Pevdis = Var(homes, within=NonNegativeReals)

        # EV State of Energy (SOEev)
        self.model.SOEev = Var(homes, within=NonNegativeReals)

        # Binary variable to switch between charging & discharging
        self.model.Uev = Var(homes, within=Binary)

    def define_constraints(self):
        """Define constraints for EV charge/discharge limits and SOE balance."""
        homes = SETS["homes"]

        # EV charge limit (Only allowed during 00:00-07:00 and 16:00-24:00)
        def charge_limit(model, h):
            return model.Pevcha[h] <= PARAMETERS["Pevcharateps1"][h] * model.Uev[h]
        self.model.ChargeLimit = Constraint(homes, rule=charge_limit)

        # EV discharge limit (Only allowed during 00:00-07:00 and 16:00-24:00)
        def discharge_limit(model, h):
            return model.Pevdis[h] <= PARAMETERS["Pevdisrateps1"][h] * (1 - model.Uev[h])
        self.model.DischargeLimit = Constraint(homes, rule=discharge_limit)

        # EV energy balance constraint
        def energy_balance(model, h):
            return model.SOEev[h] == PARAMETERS["SOEevinips1"][h] + (0.9 * model.Pevcha[h]) - (model.Pevdis[h] / 0.9)
        self.model.EnergyBalance = Constraint(homes, rule=energy_balance)

        # EV SOE bounds
        def soe_max_constraint(model, h):
            return model.SOEev[h] <= PARAMETERS["SOEevmaxps1"][h]
        self.model.SOEMax = Constraint(homes, rule=soe_max_constraint)

        def soe_min_constraint(model, h):
            return model.SOEev[h] >= PARAMETERS["SOEevminps1"][h]
        self.model.SOEMin = Constraint(homes, rule=soe_min_constraint)

    def define_objective(self):
        """Define objective function (Minimize EV energy costs)."""
        homes = SETS["homes"]
        self.model.cost = Objective(
            expr=sum(
                self.model.Pevcha[h] * PARAMETERS["PL1ps1"][h] 
                - self.model.Pevdis[h] * PARAMETERS["PL2ps1"][h]
                for h in homes
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
            "Pevcha": {h: self.model.Pevcha[h].value for h in self.model.Pevcha},
            "Pevdis": {h: self.model.Pevdis[h].value for h in self.model.Pevdis},
            "SOEev": {h: self.model.SOEev[h].value for h in self.model.SOEev}
        }

# If run as standalone script, test the model
if __name__ == "__main__":
    ev_model = EVModel()
    ev_model.solve()
    results = ev_model.get_results()
    
    print("EV Model Results:")
    print(results)
