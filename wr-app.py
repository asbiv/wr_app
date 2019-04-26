import os
import sys
from flask import Flask, flash, redirect, render_template, request, session, abort, jsonify
import pandas as pd
import numpy as np
import udf as udf

app = Flask(__name__)


#SHARED UDFs
def build_data(assumptions):
    '''Ingest assumptions dict
    Subset by caliper num
    Produce remove order
    Output data and SKUs subset'''
    sdb_data = dat[(dat.caliper == assumptions['caliper_num'])].reset_index(drop=True)
    std_size = udf.get_remove_order(udf.get_delta_cost(sdb_data))
    skus_removed = len(std_size) - assumptions['num_skus']
    std_size_sdb = std_size[skus_removed:] #[1531, 1465, 1276, 1079, 1010, 945, 912, 838]
    return(sdb_data, std_size_sdb)


#TODO - Change to upload option
#sdb_dat = pd.read_excel('data/SKU excercise File v1.5 - send out.xlsx',
#                        sheet_name=3, skiprows=2)
#Clean up column names
#sdb_dat.columns = [c.lower().replace(' ', '_') for c in sdb_dat.columns]

#START
dat = pd.read_csv('data/SDB_2018-2.csv', encoding="ISO-8859-1")
#FORMAT COL NAMES
dat.columns = [c.lstrip().rstrip().lower().replace(' ', '_') for c in dat.columns]

initial_assumptions = {
        'caliper_num': 23,
        'num_skus': 15,
        'order_inter': 0.5,
        'lead_time': 1.0,
        'service_level': 0.95,
        'inv_cost': 8,
        'waste_trim': 400,
        'waste_wacc': 800,
        'wacc': 0.08
        }

@app.route('/')
def main():

    sdb_data, std_size_sdb = build_data(initial_assumptions)

    #Re-create the outputs table
    output = udf.calculate_waste(sdb_data, initial_assumptions, std_size_sdb)
    savings = round(output['total_savings'].sum() * 12, 2)
    waste_delta = round(output['target_delta'].sum() * 12, 2)
    return render_template("main.html",
        data=output.to_html(classes=['table-bordered', 'table-responsive'],
            float_format=lambda x: '%10.2f' % x),
        savings=savings, waste_delta=waste_delta,
        assumptions=initial_assumptions)
    

#Submit form
@app.route('/handle_data', methods=['POST', 'GET'])
def handle_data():
    #assumptions = request.get_json()
    assumptions = {'caliper_num': int(request.form['caliper_num']),
                   'num_skus': int(request.form['num_skus']),
                   'order_inter': float(request.form['order_inter']),
                   'lead_time': float(request.form['lead_time']),
                   'service_level': float(request.form['service_level']),
                   'inv_cost': float(request.form['inv_cost']),
                   'waste_trim': float(request.form['waste_trim']),
                   'waste_wacc': float(request.form['waste_wacc']),
                   'wacc': float(request.form['wacc'])}

    sdb_data, std_size_sdb = build_data(assumptions)

    #Re-create the outputs table
    output = udf.calculate_waste(sdb_data, assumptions, std_size_sdb)
    savings = round(output['total_savings'].sum() * 12, 2)
    waste_delta = round(output['target_delta'].sum() * 12, 2)
    return render_template("main.html",
        data=output.to_html(classes=['table-bordered', 'table-responsive'],
            float_format=lambda x: '%10.2f' % x),
        savings=savings, waste_delta=waste_delta,
        assumptions=initial_assumptions)


@app.route("/docs")
def docs():
    return render_template(
        'docs.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)