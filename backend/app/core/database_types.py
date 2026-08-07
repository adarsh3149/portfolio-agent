from sqlalchemy import Numeric

# Monetary values (₹)
Money = Numeric(20, 2)

# Price / NAV
Price = Numeric(20, 4)

# Units / Shares
Quantity = Numeric(20, 8)