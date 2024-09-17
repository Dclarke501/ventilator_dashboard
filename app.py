# Import necessary libraries
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from datetime import datetime, timedelta

# Load your CSV data
df = pd.read_csv('/Users/davidclarke/Desktop/programming_projects/Ventilator_dashboard/data/ventilation_dashboard_recreated_dummy_data.csv')

# Calculate VAE rate per 1000 ventilator days
total_vae_cases = df['VAE (0 = no, 1 = yes)'].sum()
total_ventilator_days = df['duration of mechanical ventilation (days)'].sum()
vae_rate_per_1000_days = (total_vae_cases / total_ventilator_days) * 1000

# Calculate VAP rate per 1000 ventilator days
total_vap_cases = df['VAP (0 = no, 1 = yes)'].sum()
vap_rate_per_1000_days = (total_vap_cases / total_ventilator_days) * 1000

# Calculate median ventilator days
median_ventilator_days = df['duration of mechanical ventilation (days)'].median()

# Filter data for reintubations within the last month
current_date = datetime.now()
one_month_ago = current_date - timedelta(days=30)

# Convert intubation date back to datetime for filtering
df['date of intubation'] = pd.to_datetime(df['date of intubation'])

# Count the number of reintubations within 24 hours in the last month
reintubations_last_month = df[(df['reintubation within 24 hours of extubation (0 = no)'] == 1) & 
                              (df['date of intubation'] >= one_month_ago)].shape[0]

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1('Mechanical Ventilation Quality Dashboard', style={'text-align': 'center'}),

    # Row of tiles with Flexbox
    html.Div([
        # VAE Rate Tile
        html.Div([
            html.H2('VAE Rate per 1000 Ventilator Days', style={'text-align': 'center'}),
            html.Div(f'{vae_rate_per_1000_days:.2f}', 
                     style={'font-size': '48px', 'font-weight': 'bold', 'color': 'black', 'text-align': 'center', 
                            'padding': '20px', 'background-color': '#F0F0F0', 'border-radius': '10px'}),
        ], style={'flex': '1', 'margin': '10px', 'padding': '10px', 'background-color': '#FFFFFF', 'box-shadow': '2px 2px 10px #ccc'}),

        # VAP Rate Tile
        html.Div([
            html.H2('VAP Rate per 1000 Ventilator Days', style={'text-align': 'center'}),
            html.Div(f'{vap_rate_per_1000_days:.2f}', 
                     style={'font-size': '48px', 'font-weight': 'bold', 'color': 'black', 'text-align': 'center', 
                            'padding': '20px', 'background-color': '#F0F0F0', 'border-radius': '10px'}),
        ], style={'flex': '1', 'margin': '10px', 'padding': '10px', 'background-color': '#FFFFFF', 'box-shadow': '2px 2px 10px #ccc'}),

        # Median Ventilator Days Tile
        html.Div([
            html.H2('Median Ventilator Days', style={'text-align': 'center'}),
            html.Div(f'{median_ventilator_days:.2f}', 
                     style={'font-size': '48px', 'font-weight': 'bold', 'color': 'black', 'text-align': 'center', 
                            'padding': '20px', 'background-color': '#F0F0F0', 'border-radius': '10px'}),
        ], style={'flex': '1', 'margin': '10px', 'padding': '10px', 'background-color': '#FFFFFF', 'box-shadow': '2px 2px 10px #ccc'}),

        # Reintubations Last Month Tile
        html.Div([
            html.H2('Reintubations within 24 Hours (Last Month)', style={'text-align': 'center'}),
            html.Div(f'{reintubations_last_month}', 
                     style={'font-size': '48px', 'font-weight': 'bold', 'color': 'black', 'text-align': 'center', 
                            'padding': '20px', 'background-color': '#F0F0F0', 'border-radius': '10px'}),
        ], style={'flex': '1', 'margin': '10px', 'padding': '10px', 'background-color': '#FFFFFF', 'box-shadow': '2px 2px 10px #ccc'}),

    ], style={'display': 'flex', 'justify-content': 'center', 'padding': '20px'}),  # Flexbox for side-by-side layout

    # Dropdown for data selection
    html.Label('Select a Column to Visualize'),
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': col, 'value': col} for col in df.columns if df[col].dtype in ['float64', 'int64']],
        value='% MV spent above 8ml/kg'
    ),

    # Data Table
    html.H2('Data Table'),
    html.Div(id='data-table'),

    # Graph for Scatter/Bar Chart
    html.H2('Chart'),
    dcc.Graph(id='chart'),

    # Graph for Histogram
    html.H2('Histogram'),
    dcc.Graph(id='histogram'),
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)