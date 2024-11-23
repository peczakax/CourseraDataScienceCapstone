# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = spacex_df['Launch Site'].unique()



# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                    {'label': 'All Sites', 'value': 'ALL'},
                                                    {'label': 'CCAFS LC-40', 'value': launch_sites[0]},
                                                    {'label': 'VAFB SLC-4E', 'value': launch_sites[1]},
                                                    {'label': 'KSC LC-39A', 'value': launch_sites[2]},
                                                    {'label': 'CCAFS SLC-40', 'value': launch_sites[3]}
                                             ],
                                             value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True
                                             ),                                             
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df.groupby(['Launch Site', 'class']).size().reset_index(name='Occurrences')
        filtered_df = filtered_df[filtered_df['class'] == 1]
        title = 'Total Success Launches for All Sites'

        fig = px.pie(filtered_df, 
                    values='Occurrences', 
                    names='Launch Site', 
                    title=title
                    )
        return fig
                
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        title = f'Success Launches for Site {entered_site}'

        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']

        fig = px.pie(success_counts, 
                    values='count', 
                    names='class', 
                    title=title,
                    color='class',
                    color_discrete_map={0: 'red', 1: 'green'})
        return fig
    
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

# Function decorator to specify function input and output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'), Input('payload-slider', 'value')]
)
def get_scatter_chart(site, payload_range):
    filtered_df = spacex_df
    if site == 'ALL':
        title = 'Correlation between Payload and Success for all Sites'
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == site]
        title = f'Correlation between Payload and Success for site {site}'

    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= payload_range[0])
        & (filtered_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
