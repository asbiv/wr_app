#PREP ENV
import pandas as pd
import numpy as np
from scipy.stats import norm
import os
import matplotlib.pyplot as plt

os.chdir('/Users/Ab/Desktop/Capstone/wr_app/')
from udf import * #udf.py functions


#READ IN DATA
dat = pd.read_csv('https://raw.githubusercontent.com/asbiv/wr_app/master/data/SDB_2018-2.csv?token=ADK2NWLX2QSFRK3UCZYT2NS4ZB6AO',
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

sel_sizes_list = []#pd.DataFrame(0, columns=range(1, len(std_size)+1), index=range(0, len(std_size)))
plot_df_savings = []
plot_df_waste = []
for i in range(0, len(std_size)):
    std_size_tmp = std_size[i:] #Drop i values
    output = calculate_waste(dat_23, initial_assumptions, 23, std_size_tmp)
    #Selected sizes df
    #sel_sizes_df.iloc[:, i] = output['sel_size']
    sel_sizes_list.append(output['sel_size'])
    #Plotting data
    plot_df_savings.append(output['total_savings'].sum()*12)
    plot_df_waste.append(output['waste'].sum()*12)


#PREP FOR PRINTING
plot_df_savings_ = pd.DataFrame([list(reversed(range(len(std_size)))), plot_df_savings]).transpose()
plot_df_savings_.columns = ['x', 'y1']
#plot_df_savings_.plot(x='x', y='y1')

plot_df_waste_ = pd.DataFrame([list(reversed(range(len(std_size)))), plot_df_waste]).transpose()
plot_df_waste_.columns = ['x', 'y2']
#plot_df_waste_.plot(x='x', y='y2')

#PLOT TWO Y AXES
fig, ax1 = plt.subplots()

ax2 = ax1.twinx()
ax1.plot(plot_df_savings_.x, plot_df_savings_.y1, '#feb24c')
ax2.plot(plot_df_waste_.x, plot_df_waste_.y2, '#0868ac')

ax1.set_xlabel('No. SKUs')
ax1.set_ylabel('Total Savings (€)', color='#feb24c')
ax2.set_ylabel('Total Waste (metric tons)', color='#0868ac')

plt.show()