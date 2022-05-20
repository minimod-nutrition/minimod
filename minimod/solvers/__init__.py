from minimod.solvers.costsolver import CostSolver
from minimod.solvers.benefitsolver import BenefitSolver

class Minimod:
    
    def __new__(self, solver_type = None):
        
        if solver_type == 'covmax':
            
            return BenefitSolver
        
        elif solver_type == 'costmin':
            
            return CostSolver
        