import os
import sys
from flask import Flask, flash, redirect, render_template, request, session, abort
import pandas as pd
import numpy as np
import udf as udf

app = Flask(__name__)

#NONSENSE
#sdb_dat = pd.read_excel('data/SKU excercise File v1.5 - send out.xlsx',
#                        sheet_name=3, skiprows=2)
#Clean up column names
#sdb_dat.columns = [c.lower().replace(' ', '_') for c in sdb_dat.columns]

#NEW NONSENSE
dat = pd.read_csv('data/SDB_2018-2.csv', encoding="ISO-8859-1")
#FORMAT COL NAMES
dat.columns = [c.lstrip().rstrip().lower().replace(' ', '_') for c in dat.columns]

initial_assumptions = {
        'num_skus': 15,
        'order_inter': 0.5,
        'lead_time': 1.0,
        'service_level': 0.95,
        'inv_cost': 8,
        'waste_trim': 400,
        'waste_wacc': 800,
        'wacc': 0.08,
        'caliper': 23}
    
sdb_23 = dat[(dat.caliper == initial_assumptions['caliper'])].reset_index(drop=True)

#Standard sizes for 23
std_size = udf.get_remove_order(udf.get_delta_cost(sdb_23))

@app.route('/')
def main():
    std_size_23 = std_size[initial_assumptions['num_skus']:] #[1531, 1465, 1276, 1079, 1010, 945, 912, 838]
    #Re-create the outputs table
    output = udf.calculate_waste(sdb_23, initial_assumptions, 23, std_size_23)
    savings = round(output['total_savings'].sum() * 12, 2)
    waste_delta = round(output['target_delta'].sum() * 12, 2)
    return render_template("main.html",
        data=output.to_html(classes=['table-bordered', 'table-responsive'],
            float_format=lambda x: '%10.2f' % x),
        savings=savings, waste_delta=waste_delta,
        assumptions=initial_assumptions)
    

#Submit form
@app.route('/handle_data', methods=['POST'])
def handle_data():
    assumptions = {'num_skus': int(request.form['num_skus']),
                   'order_inter': float(request.form['order_inter']),
                   'lead_time': float(request.form['lead_time']),
                   'service_level': float(request.form['service_level']),
                   'inv_cost': float(request.form['inv_cost']),
                   'waste_trim': float(request.form['waste_trim']),
                   'waste_wacc': float(request.form['waste_wacc']),
                   'wacc': float(request.form['wacc'])}
    def get_form_data_size(assumptions):
        #tmp = assumptions['num_skus']
        #print(tmp)
        #std_size_23 = std_size[tmp:]
        std_size_23 = [1531, 1465, 1276, 1079, 1010, 945, 912, 838]
        return(std_size_23)
    std_size_23 = get_form_data_size(assumptions)

    output = udf.calculate_waste(sdb_23, assumptions, 23, std_size_23)
    savings = round(output['total_savings'].sum() * 12, 2)
    waste_delta = round(output['target_delta'].sum() * 12, 2)
    return render_template("main.html",
        data=output.to_html(classes=['table-bordered', 'table-responsive'],
            float_format=lambda x: '%10.2f' % x),
        savings=savings, waste_delta=waste_delta,
        assumptions=assumptions)


@app.route("/docs")
def docs():
    return render_template(
        'docs.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)