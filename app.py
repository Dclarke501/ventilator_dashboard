# Import necessary libraries
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from datetime import datetime, timedelta
import os

''' set the DATA_PATH environment variable to the path of your CSV file before running the app
    e.g., in the terminal, run:
    export DATA_PATH='path/to/your/data.csv'
    '''

# Load csv data
csv_path = os.getenv('DATA_PATH')
if csv_path:
    df = pd.read_csv(csv_path)
else:
    print("Error: DATA_PATH environment variable not set")

''' Load your CSV data - can also do it this way if you want to load the data from a CSV file
df = pd.read_csv('folder/data.csv')
'''



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

# Convert intubation date and date of VAE back to datetime for filtering
df['date of intubation'] = pd.to_datetime(df['date of intubation'])
df['date of VAE'] = pd.to_datetime(df['date of VAE'], errors='coerce')

# Count the number of reintubations within 24 hours in the last month
reintubations_last_month = df[(df['reintubation within 24 hours of extubation (0 = no)'] == 1) & 
                              (df['date of intubation'] >= one_month_ago)].shape[0]

# Convert Period objects to strings before grouping
df['VAE_month_year'] = df['date of VAE'].dt.to_period('M').astype(str)

# Group by year-month and count the occurrences of VAE
vae_by_month = df[df['VAE (0 = no, 1 = yes)'] == 1].groupby('VAE_month_year').size().reset_index(name='count')

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

    # VAE Frequency by Month Graph
    html.H2('VAE Frequency by Month'),
    dcc.Graph(id='vae-by-month-graph'),

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

# Define callback to update the VAE graph and other elements
@app.callback(
    [Output('vae-by-month-graph', 'figure'),
     Output('data-table', 'children'),
     Output('chart', 'figure'),
     Output('histogram', 'figure')],
    [Input('dropdown', 'value')]
)
def update_dashboard(selected_column):
    # Generate VAE by Month Graph
    vae_fig = px.bar(vae_by_month, x='VAE_month_year', y='count', title='Frequency of VAE by Month', labels={'VAE_month_year': 'Month', 'count': 'VAE Count'})

    # Generate Data Table
    table_header = [html.Tr([html.Th(col) for col in df.columns])]
    table_body = [html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(min(len(df), 10))]  # Display first 10 rows
    table = html.Table(table_header + table_body)

    # Create a Chart (e.g., scatter plot)
    chart = px.scatter(df, x='MRN', y=selected_column, title=f'Scatter Plot: MRN vs {selected_column}')

    # Create a Histogram
    histogram = px.histogram(df, x=selected_column, title=f'Histogram of {selected_column}')

    return vae_fig, table, chart, histogram

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)