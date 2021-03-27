import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from plotly import graph_objs as go
#import dash_auth
#from users import VALID_USERNAME_PASSWORD_PAIRS


df = pd.read_csv("global_power_plant_database.csv")
countries = df['country_long'].unique()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

#auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

df = pd.read_csv("global_power_plant_database.csv")
countries = df['country_long'].unique()

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "26rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "28rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H3("Welcome to the Global Power Plants Dashboard"),
        html.Hr(),   # Mets une barre horizontale
        html.P(
            "Explore distribution of power plants by country", className="lead"
        ),
      
          dbc.FormGroup( # GROUP 1
            [
                dbc.Label("Select Countries"),
                dcc.Dropdown(id='country',
                             placeholder='Select a Country',
                             options=[{'label': i, 'value': i} for i in countries],
                             value=['United States of America', 'China',
                                   'United Kingdom', 'Brazil', 'France','Canada'],
                             multi=True
                           ),
            ]
          ),
        dbc.FormGroup( # GROUP 2
            [
                dbc.Label("Click on any power plant to get more information"),
                dcc.Markdown(id='plant_summary')
            ]
        ),
        
        html.Hr(),
            html.A("Source of Global Power Plants Data", href='https://datasets.wri.org/dataset/globalpowerplantdatabase', target="_blank")
                
    ],
    style=SIDEBAR_STYLE,
)

content =html.Div(children= [dcc.Graph(id='map',clickData={'points': [{'hovertext': 'Chelsea'}]}),
                  dcc.Graph(id='graph')],style=CONTENT_STYLE)
                            



app.layout = html.Div([sidebar, content])

@app.callback([
    Output('map', 'figure'),
    Output('graph', 'figure')],
    [Input('country', 'value')])
def update_map(countries):    
    dff = df[df.country_long.isin(countries)]
    
    fig = px.scatter_mapbox(dff, lat="latitude", lon="longitude",
                        hover_name="name", hover_data=["country_long", "primary_fuel"],
                        color="primary_fuel",zoom=2,
                        center = {'lat': 45.4215, 'lon' :-75.6972},opacity = 0.6,
                        mapbox_style='open-street-map',
                        labels = {'primary_fuel': 'Primary fuel'},
                        size = 'capacity_mw')
    fig.update_layout( # customize font and legend orientation & position
    
    # font and legend 
    font_family="Rockwell",
    autosize=True,
    margin=go.layout.Margin(l=0, r=0, t=0, b=35),
        legend=dict(
                title= None, orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
        )
    )
    
    Grouped = dff.groupby(['country_long','primary_fuel'])['primary_fuel'].count().rename_axis(['Country','Fuel']).reset_index(name='Count')
    graph = px.sunburst(Grouped,path=['Country', 'Fuel'], values='Count')
    
    graph.update_layout(margin=go.layout.Margin(l=0, r=0, t=0, b=0)
            )
    
    return fig, graph

@app.callback(dash.dependencies.Output('plant_summary', 'children'),
              [dash.dependencies.Input('map', 'clickData')])
def update_summary(click_Data):
    plant_name  = click_Data['points'][0]['hovertext']
    owner = df[df['name'] == plant_name]['owner'].iloc[0]
    gwh = round(df[df['name'] == plant_name]['estimated_generation_gwh'].iloc[0],2)
    commissioning_year = df[df['name'] == plant_name]['commissioning_year'].iloc[0]
    capacity_mw = df[df['name'] == plant_name]['capacity_mw'].iloc[0]
    year_capacity = df[df['name'] == plant_name]['year_of_capacity_data'].iloc[0]
    source = df[df['name'] == plant_name]['source'].iloc[0]
    url = df[df['name'] == plant_name]['url'].iloc[0]
   

    update = f'''
                    **Summary of *{plant_name}*:**
                    - Plant owner: {owner}
                    - Estimated Yearly Generation (GWH): {gwh}
                    - First Year the Plant Generated Energy: {commissioning_year}
                    - Electrical capacity (MW): {capacity_mw}
                    - Year of Reported Capacity: {year_capacity}
                    - Source for Plant info: [{source}]({url})
                    
                    
                    
                    **Note**: nan means the information is not in the database
                    '''
                    
    
    return update
                
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
