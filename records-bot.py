from flask import Flask, request, render_template
import plotly
import plotly.graph_objs as go
from datetime import datetime
from config import *
from agents_api import *
import requests
import pandas as pd
import numpy as np
import json

app = Flask(__name__)
contracts = {}


def create_plot(category):
    x = np.array([datetime.fromtimestamp(record['timestamp']) for record in category['values']])
    y = np.array([record['value'] for record in category['values']])
    df = pd.DataFrame({'x': x, 'y': y})
    data = []

    if category['category']['default_representation'] == 'scatter':
        data.append(go.Scatter(
            x=df['x'],  # assign x as the dataframe column 'x'
            y=df['y'],
            mode='markers',
        ))

    if category['category']['default_representation'] == 'bars':
        data.append(go.Bar(
            x=df['x'],  # assign x as the dataframe column 'x'
            y=df['y'],
        ))


    if data:
        layout = go.Layout(
            margin=go.layout.Margin(
                l=35,  # left margin
                r=15,  # right margin
                b=30,  # bottom margin
                t=25  # top margin
            )
        )

        graphJSON = json.dumps(dict(data=data, layout=layout), cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON
    return None


@app.route('/init', methods=['POST'])
def init():
    return 'ok'


@app.route('/remove', methods=['POST'])
def remove():
    return 'ok'


@app.route('/settings', methods=['GET'])
def settings():
    return "Этот интеллектуальный агент не требует настройки."


@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'


@app.route('/message', methods=['POST'])
def message():
    return "ok"


@app.route('/view', methods=['GET'])
def action():
    key = request.args.get('api_key', '')
    contract_id = str(request.args.get('contract_id', ''))

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."

    available_categories = get_available_categories(contract_id)
    print(available_categories)

    data = []

    for category in available_categories:
        data.append(get_records(contract_id, category['name']))
    for category in data:
        for row in category['values']:
            row['formatted_date'] = datetime.fromtimestamp(row['timestamp']).strftime('%Y-%m-%d %H.%M')

        category['plot'] = create_plot(category)
        category['value_list'] = category['values']

    print(data)
    return render_template('viewer.html', data=data)


app.run(port='9103', host='0.0.0.0')
