#PREP ENV
import pandas as pd
import numpy as np
from scipy.stats import norm
import os
import matplotlib.pyplot as plt
import matplotlib
from pylab import rcParams

os.chdir('/Users/Ab/Desktop/Capstone/wr_app/')
from udf import * #udf.py functions


#READ IN DATA
dat = pd.read_csv('https://raw.githubusercontent.com/asbiv/wr_app/master/data/SDB_2018-2.csv?token=ADK2NWLZOVOAL7R4QQOXVEK43HHB2',
                  encoding='ISO-8859-1')

#FORMAT COL NAMES
dat.columns = [c.lstrip().rstrip().lower().replace(' ', '_') for c in dat.columns]
    #NOTE: ['new_cal_+_width', 'x_.1'] is different from the excel import, make sure nothing breaks...

#INITIAL ASSUMPTIONS
#dat.caliper.unique()
initial_assumptions = {'order_inter': 0.5,
               'lead_time': 1.0,
               'service_level': 0.95,
               'inv_cost': 8,
               'waste_trim': 400,
               'waste_wacc': 800,
               'wacc': 0.08,
               'caliper_num': 23}

#BUILD PLOT DATA
def build_plot_data(data, assumptions):
    dat = build_caliper_subset(data, assumptions)
    std_size = get_remove_order(get_delta_cost(dat))

    sel_sizes_list = []
    plot_df_savings = []
    plot_df_waste = []
    for i in range(0, len(std_size)):
        std_size_tmp = std_size[i:] #Drop i values
        output = calculate_waste(dat, initial_assumptions, std_size_tmp)
        #Selected sizes df
        #sel_sizes_df.iloc[:, i] = output['sel_size']
        sel_sizes_list.append(output['sel_size'])
        #Plotting data
        plot_df_savings.append(output['total_savings'].sum()*12)
        plot_df_waste.append(output['waste'].sum()*12)

    plot_df_savings_ = pd.DataFrame([list(reversed(range(len(std_size)))), plot_df_savings]).transpose()
    plot_df_savings_.columns = ['x', 'y1']    
    plot_df_waste_ = pd.DataFrame([list(reversed(range(len(std_size)))), plot_df_waste]).transpose()
    plot_df_waste_.columns = ['x', 'y2']
    return(plot_df_savings_, plot_df_waste_)
    
plot_df_savings_, plot_df_waste_ = build_plot_data(dat, initial_assumptions)


#PLOTLY
from plotly.offline import plot
import plotly.graph_objs as go


#TEST DATA
data=[
    go.Scatter(
        x = plot_df_savings_['x'], 
        y=plot_df_savings_['y1'], 
        name='Savings'
    ),
    go.Scatter(
        x=plot_df_waste_['x'],
        y=plot_df_waste_['y2'],
        name='Waste', 
        yaxis='y2'
    ),
]

layout = go.Layout(
    title='Here is a title',
    yaxis2= dict(
        overlaying='y',
        side='right',
        showgrid=False,
    )
)
fig = go.Figure(data, layout)
plot(fig, auto_open=True)