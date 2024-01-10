import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    dcc.Dropdown(id='site-dropdown',
                 options=[{'label': 'All Sites', 'value': 'ALL'},
                          {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                          {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                          {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                          {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}],
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True),
    html.Br(),

    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=max_payload, step=1000,
                    marks={0: '0', 100: '100'},
                    value=[min_payload, max_payload]),

    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value')]
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df
        fig = px.pie(filtered_df, values='class', names='Launch Site', title=f'Success Rate for {entered_site}')
        return fig
    else:
        filtered_df=spacex_df[spacex_df['Launch Site'] == entered_site]['class']
        i=0
        for j in filtered_df:
            if j==0:
                i+=1
        k = filtered_df.mean()
        fil = np.array([k,i/len(filtered_df)])
        fig = plt.pie(fil, labels=[f'Successful {round(k, 2)}%',f'Failed {round(i/len(filtered_df), 2)}%'],labeldistance=1.1)
        plt.title(f'Success Rate of {entered_site} site')
        plt.legend()
        return fig

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)

    if entered_site == 'ALL':
        fig = px.scatter(spacex_df[mask], x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title='Payload vs. Outcome for All Sites')
    else:
        filtered_df = spacex_df[mask & (spacex_df['Launch Site'] == entered_site)]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title=f'Payload vs. Outcome for {entered_site}')

    return fig

if __name__ == '__main__':
    app.run_server()