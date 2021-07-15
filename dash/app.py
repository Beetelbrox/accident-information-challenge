import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import sqlalchemy as sa

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
# df = pd.DataFrame({
#     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#     "Amount": [4, 1, 2, 2, 4, 5],
#     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# })

pg_engine = sa.create_engine('postgresql://admin:admin@postgres_db:5433/postgres')

t = sa.text("SELECT * FROM kaggle.pre_road_traffic_incidents__agg_vehicle_ages")
with pg_engine.connect() as conn:
    df = pd.read_sql(t, conn, index_col='age_of_vehicle')

df['cumsum'] = df['num_accidents'].cumsum()/df['num_accidents'].sum()*100

base_fig = px.bar(df, x=df.index, y="pct_accidents")
pareto_line = px.line(df, x=df.index, y="cumsum")
base_fig.add_trace(pareto_line.data[0])

t = sa.text("SELECT * FROM kaggle.pre_road_traffic_incidents__age_bands_vehicle_age WHERE COALESCE(age_of_vehicle, 0) <= 20")
with pg_engine.connect() as conn:
    df = pd.read_sql(t, conn, index_col='age_band_of_driver')

cat_orders = {
    'age_band_of_driver': [
        '0 - 5', '6 - 10', '11 - 15', '16 - 20', '21 - 25', '26 - 35', '36 - 45', '46 - 55', '56 - 65', '66 - 75', 'Over 75', 'Data missing or out of range'
    ]
}

fig = px.bar(df,
    x=df.index,
    y="pct_accidents",
    color='age_of_vehicle',
    color_continuous_scale='thermal',
    color_continuous_midpoint=5,
    category_orders=cat_orders)

fig_abs = px.bar(df, x=df.index, y="num_accidents", color='age_of_vehicle', color_continuous_scale='RdYlBu', category_orders=cat_orders)

fig_hm = px.density_heatmap(df, x=df.index, y="age_of_vehicle", nbinsy=20, z="num_accidents", histfunc="sum", category_orders=cat_orders)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='pareto',
        figure=base_fig
    ),

    dcc.Graph(
        id='pct',
        figure=fig
    ),

    dcc.Graph(
        id='abs',
        figure=fig_abs
    ),

    dcc.Graph(
        id='geatmap',
        figure=fig_hm
    )
])

if __name__ == '__main__':
    import os
    debug = True if os.environ["DASH_DEBUG_MODE"] == "true" else False
    app.run_server(host="0.0.0.0", port=8050, debug=debug)