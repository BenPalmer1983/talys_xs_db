import sys
sys.path.append("../../src")

from talys import talys



talys.set("../../data/talys", "../../data/isotopes.pz")

talys.plot_pxs_all('plots/pxs')
