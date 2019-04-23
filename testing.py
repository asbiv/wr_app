#Read, process and output data

#LOAD LIBRARIES
import os
import pandas as pd
import numpy as np


#PREP ENVIRONMENT
#Read in functions file
os.chdir('/Users/Ab/Desktop/Capstone/wr_app/')
from udf import *

path = '/Users/Ab/Desktop/Capstone/wr_app/data/'

######
df = pd.read_csv(path + 'SDB_2018-2.csv', encoding="ISO-8859-1")
df.columns = ['Unnamed: 0', 'Sales Org', 'European Customer', 'Sold to Customer',
       'Ship To Country', 'Type', 'confi', 'size', 'Die Reference',
       'Board Type', 'Board Item', 'WRK Filter', 'Grade', 'Certification', 'x',
       ' new Cal + width', 'Category', 'old Cal + width', 'Unchanged?', 'GSM',
       'Caliper', 'new std width mm', 'std width mm', 'std width',
       'Std Width Round (in)', 'optimum width', 'optimum width (in)',
       'optimum std?', 'repeat', 'NB ON', 'x.1', 'producer 2019',
       'Forecast Quantity board MT - OCT 2018',
       'Forecast Quantity board MT - NOV 2018',
       'Forecast Quantity board MT - DEC 2018',
       'Forecast Quantity board MT - JAN 2019',
       'Forecast Quantity board MT - FEB 2019',
       'Forecast Quantity board MT - MAR 2019',
       'Forecast Quantity board MT - APR 2019',
       'Forecast Quantity board MT - MAY 2019',
       'Forecast Quantity board MT - JUN 2019',
       'Forecast Quantity board MT - JUL 2019',
       'Forecast Quantity board MT - AUG 2019',
       'Forecast Quantity board MT - SEP 2019',
       'Forecast Quantity board MT - Q1 2019',
       'Forecast Quantity board MT - Q2 2019',
       'Forecast Quantity board MT - Q3 2019',
       'Forecast Quantity board MT - Q4 2019',
       'Forecast Quantity board MT - FY 2019', 'Average', 'Standarddeviation']
df.columns = [c.lower().replace(' ', '_') for c in df.columns]
#df.iloc[:,32:] = df.iloc[:,32:].apply(lambda x : x.str.extract('(\d+)',expand=False).astype(float))
df.dtypes


#LOAD DATA
sdb_dat = pd.read_excel(path + 'SKU excercise File v1.5 - send out.xlsx',
                        sheet_name=3, skiprows=2)
#Clean up column names
sdb_dat.columns = [c.lower().replace(' ', '_') for c in sdb_dat.columns]


#TODO
#1. Read in data from GH
    #ISSUE: Can't read xlsx from GH - Convert to CSV?
#url = 'https://raw.githubusercontent.com/asbiv/westrock/master/data/SDB_2018.csv?token=ANWm2SLsqi67e3OZfRzUZwOH86n0HgQXks5b9MJ9wA%3D%3D'
#df = pd.read_csv(url, skiprows=2) #preserving original form

#2. Store assumptions as dict?
initial_assumptions = {'order_inter': 0.5,
               'lead_time': 1.0,
               'service_level': 0.95,
               'inv_cost': 8,
               'waste_trim': 400,
               'waste_wacc': 800,
               'wacc': 0.08}
               #Period_cost = WACC/12

#EXAMPLE WITH CALIPER 23
df['forecast_quantity_board_mt_-_fy_2019'].sum()
sdb_dat['forecast_quantity_board_mt_-_fy_2019'].sum()
#sdb_23 = sdb_dat[(sdb_dat.caliper == 23)]
sdb_23 = df[(df.caliper == 23)]

#Standard sizes for 23
std_size_23 = [1531, 1465, 1276, 1079, 1010, 945, 912, 838]

#Re-create the outputs table
output = calculate_waste(sdb_23, initial_assumptions, 23, std_size_23)

#Let's explore some of the data
#Monthly savings
output[['sel_size','total_savings']]
output['total_savings'].sum()
#Annual savings
output['total_savings'].sum() * 12

#Something more inspiring...WACC
output['wacc'].sum()


#NEW STARTING 02.06.19
#ITERATE THROUGH PARAMETERS
plot_df = []

for i in np.linspace(0.9, 0.98, 9):
    initial_assumptions['service_level'] = i
    output = calculate_waste(sdb_23, initial_assumptions, 23, std_size_23)
    plot_df.append(output['total_savings'].sum()*12)
print(plot_df)
plot_df_ = pd.DataFrame([np.linspace(0.9, 0.98, 9).tolist(), plot_df])\
    .transpose()
plot_df_.columns = ['a', 'b']
plot_df_.plot(x='a', y='b')

pd.DataFrame(np.linspace(0.9, 0.98, 9))

#Add outputs to a df
    #Which outputs?

#TODO
#NEXT STEPS
    #Build function for number of SKUs limit
    #Iterate through number of SKUs for plot