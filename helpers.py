import json
import os
import sys
import math
from datetime import datetime

from flask import request, abort, render_template
from pytz import timezone
from sentry_sdk import capture_exception
from medsenger_api import AgentApiClient

from config import *

medsenger_api = AgentApiClient(APP_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)
contracts = {}


def load():
    global contracts
    with open('contracts.json', 'r') as f:
        contracts = json.load(f)


def save():
    global contracts
    with open('contracts.json', 'w') as f:
        json.dump(contracts, f, indent=6)


def init_contract(contract_id):
    if contract_id not in contracts.keys():
        contract = {
            'agent_token': medsenger_api.get_agent_token(contract_id).get('agent_token'),
            'is_active': True
        }
        contracts.update({contract_id: contract})
    else:
        contracts[contract_id]['is_active'] = True
    save()
    return 'ok'


def remove_contract(contract_id):
    contracts[contract_id]['is_active'] = False
    save()
    return 'ok'


def gts():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S - ")


def log(error, terminating=False):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    if PRODUCTION:
        capture_exception(error)

    if terminating:
        print(gts(), exc_type, file_name, exc_tb.tb_lineno, error, "CRITICAL")
    else:
        print(gts(), exc_type, file_name, exc_tb.tb_lineno, error)


# decorators
def verify_args(func):
    def wrapper(*args, **kwargs):
        if not request.args.get('contract_id'):
            abort(422)
        if request.args.get('api_key') != APP_KEY:
            abort(401)
        try:
            return func(request.args, request.form, *args, **kwargs)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


def verify_json(func):
    def wrapper(*args, **kwargs):
        if not request.json.get('contract_id') and "status" not in request.url:
            abort(422)
        if request.json.get('api_key') != APP_KEY:
            abort(401)
        try:
            return func(request.json, *args, **kwargs)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


def get_ui(contract_id, to_export=0):
    categories = medsenger_api.get_categories()
    return render_template('index.html', contract_id=contract_id, agent_token=contracts[str(contract_id)]['agent_token'],
                           categories=json.dumps(categories), to_export=to_export,
                           api_host=MAIN_HOST.replace('8001', '8000'), local_host=LOCALHOST,
                           agent_id=AGENT_ID, lc=dir_last_updated('static'))


def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))


def timezone_now(zone=None):
    if zone:
        tz = timezone(zone)
    else:
        tz = timezone('Europe/Moscow')
    return datetime.now(tz)


def localize(d, zone=None):
    if zone:
        tz = timezone(zone)
    else:
        tz = timezone('Europe/Moscow')
    return tz.localize(d)


def get_patient_data(contract_id):
    patient = medsenger_api.get_patient_info(contract_id)
    return patient


def get_report_page(contract_id, dates, page=0, category=None):
    data = []
    records = medsenger_api.get_records(contract_id, time_from=dates[0], time_to=dates[1], category_name=category,
                                        limit=RECORDS_LIMIT, offset=page * RECORDS_LIMIT)

    if not records:
        return data, 0

    if page == 0:
        all_records = medsenger_api.get_records(contract_id, time_from=dates[0], time_to=dates[1],
                                                category_name=category, return_count=True)
        page_cnt = math.ceil(all_records['count'] / RECORDS_LIMIT)
    else:
        page_cnt = None

    category_info = records['category'] if category else None
    if category:
        records = records['values']

    current_date = None
    for record in records:
        if category:
            record['category_info'] = category_info
        elif record['category_info']['default_representation'] == 'non_zero_dates' and record['value'] == 0:
            continue

        record['formatted_date'] = datetime.fromtimestamp(record['timestamp']).strftime('%H:%M:%S %d.%m.%Y')
        record_date = datetime.fromtimestamp(record['timestamp']).strftime('%d.%m.%Y')
        if not current_date or current_date != record_date:
            current_date = record_date
            data.append({"date": current_date, "records": [], "symptoms": []})
        if not category and record['category_info']['default_representation'] == 'non_zero_dates':
            data[-1]["symptoms"].append(record)
        else:
            data[-1]["records"].append(record)
    return data, page_cnt
