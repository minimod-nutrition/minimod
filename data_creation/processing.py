"""This file uses the extracted CSVs and processes them together 
into the robustness code benefits and cost data
"""

from pathlib import Path
import pandas as pd

class CoverageDataCreation:
    
    def __init__(self):
        
        self.data_path = Path('robustness_data',
                              'data_in_gms_code',
                              'processed_data')
        
        self.coveragerobust = pd.read_csv(Path(self.data_path,'benefits_8_13_2018_maxdata.csv'))
        

if __name__ == "__main__":
    
    c = CoverageDataCreation()    
    