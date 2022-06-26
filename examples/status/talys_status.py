import sys
sys.path.append("../../src")   # path to talys.py

from talys import talys


# Set data and isotopes path
talys.set("../../data/talys", "../../data/isotopes.pz")

# Get status
talys.status()
