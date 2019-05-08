import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json


def create_plot(plot_df_savings_, plot_df_waste_):
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
        yaxis2= dict(
            overlaying='y',
            side='right',
            showgrid=False,
        )
    )
    fig = go.Figure(data, layout)
    #plot(fig, auto_open=True)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON