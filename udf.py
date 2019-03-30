import numpy as np
import pandas as pd
from scipy.stats import norm

#HELPER FUNCTIONS
def sqrt_of_ss(values):
    '''
    Takes the square root of the sum of squares
    Used with the calculate waste function
    '''
    val = 0
    for i in values:
        val += i**2
    return(val**(1/2))

#CORE FUNCTIONS
def find_nearest_size(std_size_input, sdb_dat):
    '''
    Takes the array of stantard sizes and the SDB data
    Returns the SDB data with the sel_size column of the
        the nearest standard size within 100mm
    Exceptions for Caliper 23 are HARDCODED into this function
    '''
    std_size_col = []
    
    for i in sdb_dat['std_width_mm']:
        tmp = []
        for j in std_size_input:
            if j - i <= 100 and j - i >= 0:
                tmp.append(j)
            else:
                continue
        if len(tmp) >= 1:
            tmp2 = []
            for h in tmp:
                tmp2.append(abs(i - h))
            ind = np.argmin(tmp2)
            std_size_col.append(tmp[ind])
        else:
            std_size_col.append(i)
    
    sdb_dat['sel_size'] = std_size_col
    
    #HARDCODED EXCEPTIONS:
    #715 becomes 838
    sdb_dat['sel_size'][(sdb_dat.std_width_mm == 715)] = 838
    #960 stays the same
    sdb_dat['sel_size'][(sdb_dat.std_width_mm == 960)] = 960
    #1394 stays the same
    sdb_dat['sel_size'][(sdb_dat.std_width_mm == 1394)] = 1394
    return(sdb_dat)


def calculate_loss(sdb_dat):
    '''
    Takes the SDB data including the sel_size column from find_nearest_size()
    Calculates the loss percentage per column
    Returns the loss percentage as column of SDB data and returns modified
        SDB data including loss_pct column
    '''
    loss_pct = []    
    for i in range(0, len(sdb_dat)):
        loss_pct.append((sdb_dat.iloc[i]['sel_size'] - sdb_dat.iloc[i]['std_width_mm'])/sdb_dat.iloc[i]['sel_size'])

    sdb_dat['loss_pct'] = loss_pct
    return(sdb_dat)


def calculations_from_forecast(sdb_dat):
    '''
    Takes the SDB data
    Calculates forecast mean and sd
    Returns the tmp_forecast_count data
    '''
    tmp_forecast = sdb_dat.iloc[:, np.r_[32:44]]
    #Add index for grouping
    tmp_forecast['index_num'] = range(1,51)
    tmp_forecast_calc = tmp_forecast.set_index('index_num').stack().\
        groupby(['index_num']).agg({'forecast_mean': 'mean', 'forecast_sd': 'std'}).reset_index()
    
    return(tmp_forecast_calc)


def group_to_sel_size_and_prod(sdb_dat_calc, assumptions):
    '''
    Takes the SDB calc data including the sel_size and loss_pct columns
        and tmp_forecast_calc data
    Takes assumptions dictionary
    Groups by producer and sel_size
    Calculates the sums of forecast_mean, forecast_sd and waste by group
    Calculates individual target and network target
    Returns the final SDB data
    '''
    #MARCELO NO. 1
    sdb_dat_summary = sdb_dat_calc[['producer_2019','sel_size', 'waste', 'forecast_mean','forecast_sd']]
    group_producer = sdb_dat_summary.groupby(['producer_2019', 'sel_size']).\
        agg({'sum'}).reset_index()
    group_producer.columns = ['producer', 'sel_size', 'waste', 'forecast_mean_sum', 'forecast_sd_sum']
        
    #MARCELO NO. 2
    #FUNCTION: sum avg * (order int + lead time) + normsinv(service level) * stdv * sqrt(order int + lead time) 
    group_producer['individual_target'] = group_producer['forecast_mean_sum'] *\
        (assumptions['order_inter'] + assumptions['lead_time']) + norm.ppf(assumptions['service_level']) *\
        group_producer['forecast_sd_sum'] * (assumptions['order_inter'] + assumptions['lead_time'])**(1/2)
    
    #MARCELO NO. 3
    #Sum by the sel_size
    #Square, sum and take sqrt of sum
    #Group by sel_size
    group_sel_size = group_producer.groupby('sel_size').agg('sum').reset_index()
    #Use sqrt_of_ss
    group_sel_size['forecast_sd_sum'] = group_producer.groupby('sel_size').forecast_sd_sum.agg(sqrt_of_ss).reset_index().forecast_sd_sum
    #Network target
    group_sel_size['network_target'] = group_sel_size['forecast_mean_sum'] *\
        (assumptions['order_inter'] + assumptions['lead_time']) + norm.ppf(assumptions['service_level']) *\
        group_sel_size['forecast_sd_sum'] * (assumptions['order_inter'] + assumptions['lead_time'])**(1/2)
    
    return(group_sel_size)


def build_output_table(group_sel_size, assumptions):
    '''
    Takes the final grouped data from group_to_sel_size_and_prod
        Takes assumptions dictionary
    Builds final summary table from Martin's spreadsheet
    Returns final summary table
    '''
    group_sel_size['target_delta'] = group_sel_size['individual_target'] - group_sel_size['network_target']
    group_sel_size['inv_savings'] = group_sel_size['target_delta'] * assumptions['inv_cost']
    group_sel_size['trim_lost'] = -group_sel_size['waste'] * assumptions['waste_trim']
    group_sel_size['impact'] = group_sel_size['inv_savings'] + group_sel_size['trim_lost']
    group_sel_size['wacc'] = group_sel_size['target_delta'] * assumptions['waste_wacc'] * (assumptions['wacc']/12)
    group_sel_size['total_savings'] = group_sel_size['impact'] + group_sel_size['wacc']
    return(group_sel_size)


def calculate_waste(sdb_dat, assumptions, caliper, std_size_input):
    '''
    Calls the following functions IN ORDER
        find_nearest_size
        calculate_loss
        tmp_forecast_calc
        group_to_sel_size_and_prod
            Calls sqrt_of_ss
        build_output_table
    Performs some other nonsense joins
    Returns the final table from Martin's spreadsheet
    '''
    #FIND NEAREST SIZE
    sdb_dat = find_nearest_size(std_size_input, sdb_dat)
    
    #CALCULATE LOSS
    sdb_dat = calculate_loss(sdb_dat)

    #FORECAST AVERAGE (FROM MONTHLY, 12 MONTHS DATA)
    tmp_forecast_calc = calculations_from_forecast(sdb_dat)
    
    #CALCULATE THE WASTE
    sdb_dat_tmp = sdb_dat.reset_index()

    #Join in forecast data
    sdb_dat_calc = pd.concat([sdb_dat_tmp, tmp_forecast_calc], axis=1)

    #Calculate waste
    sdb_dat_calc['waste'] = sdb_dat_calc['loss_pct'] * sdb_dat_calc['forecast_mean']

    ###OUTPUTS
    #TRANSFORM 
    group_sel_size = group_to_sel_size_and_prod(sdb_dat_calc, assumptions)

    #BUILD OUTPUT TABLE
    group_sel_size = build_output_table(group_sel_size, assumptions)
    
    #Return the DF
    return(group_sel_size)


###DIFFERENCE DELTA FUNCTIONS

def get_delta_cost(caliper_subset_df):
    '''
    NOTE: Assumes column order is consistent for inputs
    Takes the complete df subset by caliper
    Creates a df of cost based on the delta in widths * forecast quantity
    '''
    #Group and sum by std_width_mm
    tmp = pd.DataFrame(caliper_subset_df.iloc[:, np.r_[22,32:44]].groupby('std_width_mm').sum()).sum(axis=1)
    df = pd.DataFrame({'std_width_mm': tmp.index, 'forecast': tmp}).reset_index(drop=True)
    
    #Create delta table
    df_ = pd.DataFrame(index=tmp.index, columns=tmp.index)
    
    for i in range(0,len(df_.index)):
        for j in range(0,len(df_.columns)):
            #Index at i, column at j
            df_.iloc[i, j] = df_.iloc[j].name - df_.iloc[i].name
    
    #Remove negative values
    df_[df_ <= 0] = np.NaN
    
    #Create delta cost
    delta_cost = df_.copy()
    
    for i in range(0,len(delta_cost.index)):
        for j in range(0,len(delta_cost.columns)):
            #Index at i, column at j
            delta_cost.iloc[i, j] = df_.iloc[i, j] * df[(df.std_width_mm == df_.iloc[j].name)]['forecast'].values[0]
    return(delta_cost)

def get_remove_order(delta_cost):
    '''
    Takes the delta_cost df produced by get_delta_cost
    Creates an ordered list for subsetting n standard sizes, where the index position
        0 is dropped first, 1 dropped second etc until n=1 is the max size only
    '''
    #Find max index val
    max_index_val = max(delta_cost.index)
    #Reassign names for readability
    delta_cost.index = delta_cost.index.map(lambda x: str(x) + '_row')
    delta_cost.columns = delta_cost.columns.map(lambda x: str(x) + '_col')
    
    #Remove sequentially
    min_ref = pd.DataFrame({'min': delta_cost.min(), 'idxmin': delta_cost.idxmin()}).sort_values(by=['min'])
    ordered_removal_list = list(min_ref['idxmin'].str[:-4].dropna().astype(int))
    #Append the max value
    ordered_removal_list.append(max_index_val)
    return(ordered_removal_list)