import sys
import pandas as pd

sys.path.append("/home/lordflaron/Documents/minimod")
import minimod as mm

df = pd.DataFrame()
a = mm.BenefitSolver()

a.fit(data = [1])