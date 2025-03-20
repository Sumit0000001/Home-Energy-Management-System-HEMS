# config.py

# Buyers (Consumers) and Sellers (Prosumers)
BUYERS = ["h1", "h2", "h3", "h4", "h5"]
SELLERS = ["h6", "h7", "h8", "h9", "h10"]

# Combined List of All Houses
HOUSES = BUYERS + SELLERS

# Time Slots (24-hour scheduling)
TIME_SLOTS = list(range(1, 25))

# Power Limits
MAX_GRID_POWER = 10  # kW (for buyers)
MAX_SOLD_POWER = 10  # kW (for sellers)

# Price Conditions
PRICE_RANGES = {
    "low": {"start": 0, "end": 6, "price": 4},
    "mid": {"start": 6, "end": 16, "price": 5},
    "high": {"start": 16, "end": 24, "price": 6},
    "constant": 2  # Price when SDR > 1
}

# Lambda constraint for price stability
LAMBDA_THRESHOLD = 0.2
