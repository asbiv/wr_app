import os
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
df = pd.read_csv('data/SDB_2018-2.csv', encoding="ISO-8859-1")
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

#TODO
#1. Read in data from GH
    #ISSUE: Can't read xlsx from GH - Convert to CSV?
#url = 'https://raw.githubusercontent.com/asbiv/westrock/master/data/SDB_2018.csv?token=ANWm2SLsqi67e3OZfRzUZwOH86n0HgQXks5b9MJ9wA%3D%3D'
#df = pd.read_csv(url, skiprows=2) #preserving original form

#EXAMPLE WITH CALIPER 23
sdb_23 = df[(df.caliper == 23)]

#Standard sizes for 23
std_size_23 = [1531, 1465, 1276, 1079, 1010, 945, 912, 838]

@app.route('/')
def main():
	#2. Store assumptions as dict?
	initial_assumptions = {'order_inter': 0.5,
	               'lead_time': 1.0,
	               'service_level': 0.95,
	               'inv_cost': 8,
	               'waste_trim': 400,
	               'waste_wacc': 800,
	               'wacc': 0.08}

	#Re-create the outputs table
	output = udf.calculate_waste(sdb_23, initial_assumptions, 23, std_size_23)
	savings = round(output['total_savings'].sum() * 12, 2)
	return render_template("main.html", data=output.to_html(), savings=savings,
		assumptions=initial_assumptions)

#Submit form
@app.route('/handle_data', methods=['POST'])
def handle_data():
	assumptions = {'order_inter': float(request.form['order_inter']),
				   'lead_time': float(request.form['lead_time']),
				   'service_level': float(request.form['service_level']),
				   'inv_cost': float(request.form['inv_cost']),
				   'waste_trim': float(request.form['waste_trim']),
				   'waste_wacc': float(request.form['waste_wacc']),
				   'wacc': float(request.form['wacc'])}
	output = udf.calculate_waste(sdb_23, assumptions, 23, std_size_23)
	savings = round(output['total_savings'].sum() * 12, 2)
	waste_delta = round(output['target_delta'].sum() * 12, 2)
	return render_template("main.html", data=output.to_html(),
		savings=savings, waste_delta=waste_delta,
		assumptions=assumptions)


@app.route("/docs")
def docs():
	return render_template(
		'docs.html')

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)