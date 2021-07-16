import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import sqlalchemy as sa

from plotly.subplots import make_subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def build_pareto_chart(
        df: pd.DataFrame,
        x_axis: str,
        y_axis: str,
        x_axis_title: str=None,
        y_axis_title: str=None,
        secondary_y_axis_title: str=None
    ):
    x_axis_title = x_axis_title if x_axis_title else x_axis
    y_axis_title = y_axis_title if y_axis_title else y_axis
    secondary_y_axis_title = secondary_y_axis_title if secondary_y_axis_title else y_axis + '_pct'
    # Sort the dataframe by the y_axis value to build the cummulative percentage.
    # We're not optimizing here, just copying the whole dataframe
    _df = df.sort_values(by=y_axis, ascending=False)
    _df['cummulative_pct'] = _df[y_axis].cumsum()/_df[y_axis].sum()

    pareto_fig = make_subplots(specs=[[{"secondary_y": True}]])
    bars_fig = px.bar(_df, x=x_axis, y=y_axis)
    line_fig = px.line(_df, x=x_axis, y='cummulative_pct')
    # Update the line fig to refer to the secondary axis
    line_fig.update_traces(yaxis='y2')
    line_fig['data'][0]['line']['color']="red"
    # Merge both traces into the main one
    pareto_fig.add_traces(bars_fig.data + line_fig.data)
    # Update axies with titles & formatting
    pareto_fig.update_xaxes(title_text=x_axis_title)
    pareto_fig.update_yaxes(title_text=y_axis_title, secondary_y=False)
    pareto_fig.update_yaxes(title_text=secondary_y_axis_title, tickformat=',.1%', secondary_y=True)
    return pareto_fig

pg_engine = sa.create_engine('postgresql://admin:admin@postgres_db:5433/postgres')

t = sa.text("SELECT * FROM kaggle.pre_road_traffic_incidents__age_bands_vehicle_age")
with pg_engine.connect() as conn:
    df = pd.read_sql(t, conn)

# The heamap doesn't like nulls, so let's coalesce the nulls to 0.
# This might be somewhat misleading, but it's the best option that we have
df['vehicle_age'] = df['vehicle_age'].fillna(0)

vehicle_age_agg = df.groupby(by='vehicle_age', as_index=False).sum()
pareto_fig = build_pareto_chart(vehicle_age_agg, 'vehicle_age', 'num_accidents')

cat_orders = {
    'driver_age_band': [
        '0 - 5', '6 - 10', '11 - 15', '16 - 20', '21 - 25', '26 - 35', '36 - 45', '46 - 55', '56 - 65', '66 - 75', 'Over 75', 'Data missing or out of range'
    ]
}

# Filter out the rows to those where vehicle age is twenty or less
filtered_accidents = df[(df['vehicle_age'] <= 20)]
# Plot the heatmap
heatmap_fig = px.density_heatmap(
        filtered_accidents,
        x='driver_age_band',
        y='vehicle_age',
        nbinsy=21,
        z='num_accidents',
        histnorm='probability',
        histfunc='sum',
        category_orders=cat_orders,
        labels={
            'driver_age_band': 'Driver Age Band (Years)',
            'vehicle_age': 'Vehicle Age (Years)',
            'fraction of sum of num_accidents': '% of accidents'
        }
    )
heatmap_fig.update_coloraxes(
    colorbar_tickformat=',.1%')

app.layout = html.Div(children=[
    html.H1(children='Accident Information Challenge'),

    html.Div(children='''
        This is the (quite plain) display of the visualizations for the Accident Information Challenge. We want to plot the percentage of accidented vehicles
        per driver age band and age of vehicle, but the range of vehicle ages is quite wide and this can pose a challenge for the representation. In order to check how the accidents
        are distributed over the different vehicle ages let's use a pareto chart. Because plotly filters out nulls in numerical axes and all our values are > 0, let's coalesce
        the null values to 0 se we can represent them:
    '''),

    dcc.Graph(
        id='pareto',
        figure=pareto_fig
    ),

    html.Div(children='''
        We can see that although the age range goes over 100 years, 99% of the accidents happen on cars that are less than 20 years old. In addition, for 16.4% of all accidented vehicles we don't
        have vehicle age data. We will therefore only include cars with 20 years or less (including the coalesced 0 years for the missing values), greatly increasing the quality of the 
        representation while keeping essentially all the data. If necessary, the excluded cars could be studied separately.
        In order to represent the percentage of accidented vehicles per age band and vehicle age we'll use a heat map. This visualization will allow us to easily
        compare how the accidents are distributed over the two chosen axes:
    '''),

    dcc.Graph(
        id='pct',
        figure=heatmap_fig
    ),
    html.Div(children='''
        Although the accidents are quite spread over the vehicle and driver ages, they appear to be more frequent in drivers between the age 26 and 55.
        The vehicle age with most accidents is 0, as expected as we have a large amount of vehicles for which we don't have the age data. Regardless, it seems that accidents occur
        somewhat more frequently when cars are new. It seems that younger drivers with newer cars are slightly more likely to have an accident, although this factor is confounded with the amount of car trips
        that each age band does, so we can't draw any definitive conclusion on this topic.\n\n
    ''')
])

if __name__ == '__main__':
    import os
    debug = True if os.environ["DASH_DEBUG_MODE"] == "true" else False
    app.run_server(host="0.0.0.0", port=8050, debug=debug)