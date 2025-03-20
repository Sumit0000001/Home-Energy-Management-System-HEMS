 # Configuration file for HEMS (Home Energy Management System)
# Stores global sets, parameters, and system constants

# **Sets**: Define households, time steps, appliances, and constraints
SETS = {
    "homes": ["h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8", "h9", "h10"],
    "prosumers": ["h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8", "h9", "h10"],
    "hours": [f"t{i}" for i in range(1, 25)],
    "shifting_appliances": ["washing_machine", "dish_washer", "Iron_box", "vaccum_cleaner", "blender", "oven"],
    "appliance_phases": ["p1", "p2", "p3"],
    "housesdata": ["Cbuy", "Csold", "Constantloads", "Pvgen", "WTgen", "Tair"],
    "schedulable_appliance_data": ["Tstart", "Tend", "Operationtimes", "ActualTOP", "Delayparameter", "LOP"],
    "appliance_power_period": ["Power", "Period"]
}

# **Parameters**: Store energy constraints and limits
PARAMETERS = {
    # Grid power limits (KW)
    "PL1ps1": {h: 10 for h in SETS["prosumers"]},
    "PL2ps1": {h: 10 for h in SETS["prosumers"]},

    # Battery Constraints (KW)
    "Pbcharateps1": {"h1": 1.3, "h2": 1.2, "h3": 1, "h4": 1.3, "h5": 1.2},
    "Pbdisrateps1": {"h1": 1, "h2": 1, "h3": 0.8, "h4": 1, "h5": 1},
    "SOEbinips1": {"h1": 1, "h2": 1, "h3": 0.8, "h4": 1, "h5": 1},
    "SOEbmaxps1": {"h1": 3, "h2": 3, "h3": 2.8, "h4": 3, "h5": 3},
    "SOEbminps1": {"h1": 0.5, "h2": 0.5, "h3": 0.4, "h4": 0.5, "h5": 0.5},

    # EV Constraints (KW)
    "Pevdisrateps1": {"h1": 3, "h2": 3, "h3": 2.5, "h4": 3, "h5": 3, "h6": 2.5, "h7": 3, "h8": 3, "h9": 2.5, "h10": 3},
    "Pevcharateps1": {"h1": 3.3, "h2": 3.3, "h3": 3, "h4": 3.3, "h5": 3.3, "h6": 3, "h7": 3.3, "h8": 3.3, "h9": 3, "h10": 3.3},
    "SOEevinips1": {"h1": 4, "h2": 3, "h3": 2, "h4": 4, "h5": 3, "h6": 2, "h7": 4, "h8": 3, "h9": 2, "h10": 4},
    "SOEevmaxps1": {"h1": 8, "h2": 7, "h3": 6, "h4": 8, "h5": 7, "h6": 6, "h7": 8, "h8": 7, "h9": 6, "h10": 8},
    "SOEevminps1": {"h1": 2, "h2": 2, "h3": 2, "h4": 2, "h5": 2, "h6": 2, "h7": 2, "h8": 2, "h9": 2, "h10": 2},

    # Electric Water Heater (EWH) Constraints
    "Qps1": {h: 2 for h in SETS["prosumers"]},
    "Rps1": {h: 8 for h in SETS["prosumers"]},
    "Cps1": {h: 863.4 for h in SETS["prosumers"]},
    "Thwminps1": {h: 30 for h in SETS["prosumers"]},
    "Thwmaxps1": {h: 60 for h in SETS["prosumers"]},

    # HVAC Constraints
    "Tmaxps1": {h: 38 for h in SETS["prosumers"]},
    "Maps1": {h: 1778.369 for h in SETS["prosumers"]},
    "Caps1": {h: 1.01 for h in SETS["prosumers"]},
    "COPps1": {h: 2 for h in SETS["prosumers"]},
    "ACpowerps1": {h: 2 for h in SETS["prosumers"]},
    "Reqps1": {h: 0.0000031965 for h in SETS["prosumers"]},
    "Trinips1": {h: 35 for h in SETS["prosumers"]},
    "Trmaxps1": {h: 28 for h in SETS["prosumers"]},
    "Trminps1": {h: 20 for h in SETS["prosumers"]}
}

# **Solver Configuration**
SOLVER = {
    "name": "glpk",
    "timeout": 600  # Max solver time in seconds
}

