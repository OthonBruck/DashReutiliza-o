import dash 
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

import pandas as pd

df = pd.read_csv("C:/Users/user/Desktop/Exercicio_Dash_Angelo_Lucas/datasets_worldometer.csv", encoding='latin1')

app = dash.Dash(__name__, prevent_initial_callbacks=True)

app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True, "hideable": True}
            if i == "state" or i == "year" or i == "number"
            else {"name": i, "id": i, "deletable": False, "selectable": True}
            for i in df.columns
        ],
        data=df.to_dict('records'), 
        editable=True,             
        filter_action="native",     
        sort_action="native",       
        sort_mode="single",        
        column_selectable="multi", 
        row_selectable="multi",     
        row_deletable=True,        
        selected_columns=[],        
        selected_rows=[],          
        page_action="native",       
        page_current=0,             
        page_size=10,                
        style_cell={                
            'minWidth': 95, 'maxWidth': 95, 'width': 95
        }
    ),

    html.Br(),
    html.Br(),
    html.Div(id='bar-container'),
    html.Div(id='choromap-container')

])

# Cria gráfico de barras
@app.callback(
    Output(component_id='bar-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_row_ids'),
     Input(component_id='datatable-interactivity', component_property='selected_rows'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_indices'),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_row_ids'),
     Input(component_id='datatable-interactivity', component_property='active_cell'),
     Input(component_id='datatable-interactivity', component_property='selected_cells')]
)
def update_bar(all_rows_data, slctd_row_indices, slct_rows_names, slctd_rows,
               order_of_rows_indices, order_of_rows_names, actv_cell, slctd_cell):

    dff = pd.DataFrame(all_rows_data)

    colors = ['#7FDBFF' if i in slctd_row_indices else '#0074D9'
              for i in range(len(dff))]

    if "Country/Region" in dff and "TotalCases" in dff:
        return [
            dcc.Graph(id='bar-chart',
                      figure=px.bar(
                          data_frame=dff,
                          x="Country/Region",
                          y='TotalCases',
                          labels={"País": "Casos Confirmados"}
                      ).update_layout(showlegend=False, xaxis={'categoryorder': 'total ascending'})
                      .update_traces(marker_color=colors, hovertemplate="<b>%{y}%</b><extra></extra>")
                      )
        ]

# Cria mapa
@app.callback(
    Output(component_id='choromap-container', component_property='children'),
    [Input(component_id='datatable-interactivity', component_property="derived_virtual_data"),
     Input(component_id='datatable-interactivity', component_property='derived_virtual_selected_rows')]
)
def update_map(all_rows_data, slctd_row_indices):
    dff = pd.DataFrame(all_rows_data)

    borders = [5 if i in slctd_row_indices else 1
               for i in range(len(dff))]

    if "Country/Region" in dff and "TotalCases" in dff and "TotalDeaths" in dff:
        return [
            dcc.Graph(id='choropleth',
                      style={'height': 700},
                      figure=px.choropleth(
                          data_frame=dff,
                          locations="Country/Region",
                          scope="usa",
                          color="TotalCases",
                          title="Número de Casos Confirmados por País",
                          template='plotly_dark',
                          hover_data=['Country/Region', 'TotalCases'],
                      ).update_layout(showlegend=False, title=dict(font=dict(size=28), x=0.5, xanchor='center'))
                      .update_traces(marker_line_width=borders, hovertemplate="<b>%{customdata[0]}</b><br><br>" +
                                                                              "%{customdata[1]}" + "%")
                      )
        ]



@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]



if __name__ == '__main__':
    app.run_server(debug=True)