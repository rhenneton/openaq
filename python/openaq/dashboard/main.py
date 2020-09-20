import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
from sqlalchemy import func

from openaq.common.db import Measure, get_session

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div(["Number of hours for agglomeration: ",
              dcc.Input(id='n-hours', type='number', value=3, min=1)]),
    dcc.Graph(id='graph-id'),
    dcc.Graph(id='barchart-id')
])


@app.callback(
    Output(component_id='barchart-id', component_property='figure'),
    [Input(component_id='n-hours', component_property='value')]
)
def get_bar_chart(n_hours):
    session = get_session()

    min_datetime = _get_min_datetime_utc(n_hours=n_hours)
    results = session.query(func.avg(Measure.value), func.count(Measure.id), Measure.city, func.min(Measure.unit)) \
        .filter(Measure.date_utc > min_datetime) \
        .filter(Measure.unit == 'µg/m³') \
        .group_by(Measure.city) \
        .all()
    df = pd.DataFrame(results, columns=['avg', 'count', 'city', 'unit'])
    df['avg'] = df['avg'].round(3)
    df.sort_values('avg', inplace=True)

    fig = go.Figure([
        go.Bar(name='Average µg/m³',
               x=df['avg'],
               y=df['city'],
               orientation='h'),
        go.Bar(name='N measures',
               x=df['count'],
               y=df['city'],
               orientation='h')
    ])

    fig.update_layout(title='Air quality per province')
    session.close()
    return fig


def _get_min_datetime_utc(n_hours) -> str:
    try:
        n_hours = int(n_hours)
    except Exception as exception:
        n_hours = 3

    return str((datetime.utcnow() - timedelta(hours=n_hours)).replace(microsecond=0))


@app.callback(
    Output(component_id='graph-id', component_property='figure'),
    [Input(component_id='n-hours', component_property='value')]
)
def get_graph(n_hours):
    session = get_session()
    min_datetime = _get_min_datetime_utc(n_hours=n_hours)

    results = session.query(func.avg(Measure.value), func.count(Measure.id), Measure.location,
                            func.min(Measure.latitude), func.min(Measure.longitude), Measure.unit, Measure.city) \
        .filter(Measure.date_utc > min_datetime) \
        .filter(Measure.unit == 'µg/m³') \
        .group_by(Measure.location) \
        .all()

    df = pd.DataFrame(results, columns=['avg', 'count', 'location', 'lat', 'lon', 'unit', 'city'])
    df['avg'] = df['avg'].round(3)
    df['text'] = "Average : " + df['avg'].astype(str) + df['unit'] + ' |  n_measures : ' + df['count'].astype(
        str) + " | location : " + df['location'] + ' | province ' + df['city']

    fig = go.Figure(data=go.Scattergeo(
        lon=df['lon'],
        lat=df['lat'],
        text=df['text'],
        mode='markers',
        marker=dict(
            size=8,
            opacity=0.8,
            reversescale=False,
            autocolorscale=False,
            symbol='square',
            line=dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale='Reds',
            color=df['avg'],
            cmax=df['avg'].max(),
            cmin=df['avg'].min(),
            colorbar_title="Average air quality"
        )))

    fig.update_geos(fitbounds="locations")

    fig.update_layout(
        title='Belgium air quality',
        geo=dict(
            showland=True,
            showcountries=True,
            showsubunits=True,
            landcolor="rgb(250, 250, 250)",
            subunitcolor="rgb(110, 110, 110)",
            countrycolor="rgb(217, 217, 217)",
            countrywidth=2,
            projection_type="natural earth"
        ),
    )
    session.close()
    return fig


if __name__ == '__main__':
    app.run_server(host='0.0.0.0')
