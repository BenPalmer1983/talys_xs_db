import sys
sys.path.append("../../src")

from talys import talys



talys.set("../../data/talys", "../../data/isotopes.pz")

talys.plot_rxs_all('plots/rxs')
