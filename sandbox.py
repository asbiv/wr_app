#PREP ENV
import pandas as pd
import numpy as np
from scipy.stats import norm
import os
os.chdir('/Users/Ab/Desktop/Capstone/wr_app/')
from udf import * #udf.py functions


#READ IN DATA
dat = pd.read_csv('https://raw.githubusercontent.com/asbiv/wr_app/master/data/SDB_2018-2.csv?token=ANWm2eSf4iusHj99tlKTXRN8dcDi4lewks5cpmUswA%3D%3D',
                  encoding='ISO-8859-1')

#FORMAT COL NAMES
dat.columns = [c.lstrip().rstrip().lower().replace(' ', '_') for c in dat.columns]
    #NOTE: ['new_cal_+_width', 'x_.1'] is different from the excel import, make sure nothing breaks...

#INITIAL ASSUMPTIONS
initial_assumptions = {'order_inter': 0.5,
               'lead_time': 1.0,
               'service_level': 0.95,
               'inv_cost': 8,
               'waste_trim': 400,
               'waste_wacc': 800,
               'wacc': 0.08,
               'caliper': 23}

dat_23 = dat[(dat.caliper == initial_assumptions['caliper'])].reset_index(drop=True)

#Testing
test_size = get_remove_order(get_delta_cost(dat_23))[3:] #Drop 3 values

#Re-create the outputs table
output = calculate_waste(dat_23, initial_assumptions, 23, test_size)

#Let's explore some of the data
#Monthly savings
output[['sel_size','total_savings']]
output['total_savings'].sum()
#Annual savings
output['total_savings'].sum() * 12

#Something more inspiring...WACC
output['wacc'].sum()

#ITERATE THROUGH STD SIZE
std_size = get_remove_order(get_delta_cost(dat_23))

plot_df = []

for i in range(0, len(std_size)-1):
    std_size_tmp = std_size[i:] #Drop i values
    output = calculate_waste(dat_23, initial_assumptions, 23, std_size_tmp)
    plot_df.append(output['total_savings'].sum()*12)
print(plot_df)
plot_df_ = pd.DataFrame([list(reversed(range(len(std_size)))), plot_df]).transpose()
plot_df_.columns = ['a', 'b']
plot_df_.plot(x='a', y='b')