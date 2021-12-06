from flask import Flask, jsonify, request, render_template, make_response
import plotly
import plotly.graph_objs as go
from helpers import *
from agents_api import *
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


@app.route('/status', methods=['POST'])
def status():
    answer = {
        "is_tracking_data": False,
        "supported_scenarios": [],
        "tracked_contracts": [str(contract_id) for contract_id in contracts.keys() if contracts[contract_id]['is_active']]
    }

    return json.dumps(answer)


@app.route('/init', methods=['POST'])
@verify_json
def init(data):
    contract_id = data.get('contract_id')
    if not contract_id:
        abort(422)

    init_contract(contract_id)
    return 'ok'


@app.route('/remove', methods=['POST'])
@verify_json
def remove(data):
    contract_id = data.get('contract_id')
    if not contract_id:
        abort(422)

    remove_contract(contract_id)
    return 'ok'


@app.route('/settings', methods=['GET'])
def settings():
    contract_id = request.args.get('contract_id', '')
    return get_ui(contract_id)

# @app.route('/settings', methods=['POST'])
# def post_settings():
#     return export_report()


@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'


@app.route('/message', methods=['POST'])
def message():
    return "ok"


@app.route('/report', methods=['GET'])
@verify_args
def get_report(args, form):
    contract_id = args.get('contract_id', '')
    return get_ui(contract_id)


@app.route('/api/report', methods=['POST'])
@verify_args
def get_data(args, form):
    contract_id = int(request.args.get('contract_id'))
    data = request.json

    page = data.get('page', 0)
    dates = data.get('dates', None)
    category = data.get('category', None)

    result, page_cnt = get_report_page(contract_id, dates, page, category)
    return jsonify({'dates': result, 'page_cnt': page_cnt})


@app.route('/api/settings/get_patient', methods=['GET'])
@verify_args
def get_patient(args, form):
    contract_id = request.args.get('contract_id')
    return jsonify(get_patient_data(contract_id))


if __name__ == "__main__":
    load()
    app.run(HOST, PORT, debug=API_DEBUG)
