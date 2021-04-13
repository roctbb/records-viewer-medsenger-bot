
from flask import Flask, request, render_template, make_response
import plotly
import plotly.graph_objs as go
from datetime import datetime
from config import *
from agents_api import *
import requests
import pandas as pd
import numpy as np
import json
from transliterate import translit
import os
import tempfile
import weasyprint




app = Flask(__name__)



def render_template_to_pdf(template_name_or_list, filename=None, save=False, download=False,
                           wkhtmltopdf_args=None, **context):

    rendered = render_template(template_name_or_list, **context)

    # Checks to see if the pdf directory exists and generates a random pdf name
    if PDF_DIR_PATH is None:
        raise ValueError('PDF_DIR_PATH config variable must be set in the Flask app')
    if not os.path.isdir(PDF_DIR_PATH):
        os.makedirs(PDF_DIR_PATH)
    with tempfile.NamedTemporaryFile(suffix='.pdf', dir=PDF_DIR_PATH, delete=False) as temp_pdf:
        pass

    pdf = weasyprint.HTML(string=rendered).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    if download is True:
        response.headers['Content-Disposition'] = 'attachment; filename=%s.pdf' % filename if filename else temp_pdf.name
    else:
        response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % filename if filename else temp_pdf.name

    if save is False:
        os.remove(temp_pdf.name)

    return response



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

@app.route('/status', methods=['POST'])
def status():

    answer = {
        "is_tracking_data": False,
        "supported_scenarios": [],
    }

    return json.dumps(answer)

@app.route('/init', methods=['POST'])
def init():
    return 'ok'


@app.route('/remove', methods=['POST'])
def remove():
    return 'ok'


@app.route('/settings', methods=['GET'])
def settings():
    return get_report()


@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'


@app.route('/message', methods=['POST'])
def message():
    return "ok"

def get_full_report(contract_id):
    info = get_patient_info(contract_id)
    records = get_records(contract_id, full=True)
    dates = []

    current_date = None
    for record in records:
        if record['category_info']['default_representation'] == 'non_zero_dates' and record['value'] == 0:
            continue

        record['formatted_date'] = datetime.fromtimestamp(record['timestamp']).strftime('%H:%M:%S %d.%m.%Y')
        record_date = datetime.fromtimestamp(record['timestamp']).strftime('%d.%m.%Y')
        if not current_date or current_date != record_date:
            current_date = record_date
            dates.append({"date": current_date, "records": [], "symptoms": []})
        if record['category_info']['default_representation'] == 'non_zero_dates':
            dates[-1]["symptoms"].append(record)
        else:
            dates[-1]["records"].append(record)

    return info, dates

@app.route('/report', methods=['POST'])
def export_report():
    key = request.args.get('api_key', '')
    contract_id = str(request.args.get('contract_id', ''))

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    info, dates = get_full_report(contract_id)
    return render_template_to_pdf('report.html', filename=translit(info['name'] + '.pdf', reversed=True), download=True, save=False,
                                              dates=dates, info=info, export=True)

@app.route('/report', methods=['GET'])
def get_report():
    key = request.args.get('api_key', '')
    contract_id = str(request.args.get('contract_id', ''))

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."

    info, dates = get_full_report(contract_id)
    return render_template('report.html', export=False, dates=dates, info=info)

@app.route('/view', methods=['GET'])
def action():
    key = request.args.get('api_key', '')
    contract_id = str(request.args.get('contract_id', ''))

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."

    available_categories = get_available_categories(contract_id)

    data = []

    for category in available_categories:
        data.append(get_records(contract_id, category['name']))
    for category in data:
        for row in category['values']:
            row['formatted_date'] = datetime.fromtimestamp(row['timestamp']).strftime('%Y-%m-%d %H.%M')

        category['plot'] = create_plot(category)
        category['value_list'] = category['values']

    return render_template('viewer.html', data=data)

if __name__ == "__main__":
    app.run(port=PORT, host=HOST)
