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

medsenger_api = AgentApiClient(APP_KEY, MAIN_HOST, AGENT_ID, API_DEBUG, USE_GRPC)
text_categories = ['symptom', 'medicine', 'patient_comment', 'information']


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


def get_ui(contract, mode='settings', object_id=None, source=None, params={}):
    return render_template('index.html', contract_id=contract.id, agent_token=contract.agent_token,
                           mode=mode, object_id=object_id, source=source, params=json.dumps(params),
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


def get_graph_data(contract_id, data):
    answer = []
    if 'onload' in data and data['onload']:
        tmp_categories = [category for category in data['group']['categories'] if category not in text_categories]
        tmp_categories = tmp_categories if len(tmp_categories) else data['group']['categories']
        if data['group_data']:
            last = medsenger_api.get_records(contract_id, ','.join(tmp_categories), group=True, limit=1)
        else:
            last = [medsenger_api.get_records(contract_id, category_name, limit=1)['values'] for category_name in
                    tmp_categories]
            last = [values[0] for values in last if len(values)]
            last = sorted(last, key=lambda x: x['timestamp'], reverse=True)
        two_weeks = 1209600
        last_timestamp = last[0]['timestamp'] + 10
        data['dates'] = {
            'start': last_timestamp - two_weeks,
            'end': last_timestamp
        }

    if data['dates'] is None:
        if data['group_data']:
            answer = medsenger_api.get_records(contract_id, ','.join(data['group']['categories']), group=True)
        else:
            answer = [medsenger_api.get_records(contract_id, category_name) for category_name in
                      data['group']['categories']]
    else:
        if data['group_data']:
            answer = medsenger_api.get_records(contract_id, ','.join(data['group']['categories']),
                                               group=True,  # inner_list=True,
                                               time_from=data['dates']['start'], time_to=data['dates']['end'])
        else:
            answer = [medsenger_api.get_records(contract_id, category_name, time_from=data['dates']['start'],
                                                time_to=data['dates']['end']) for category_name in
                      data['group']['categories']]

    return list(filter(lambda x: x is not None, answer)), data['dates']


def get_report_page(contract_id, dates, page=0, categories=None):
    data = []
    records = medsenger_api.get_records(contract_id, time_from=dates[0], time_to=dates[1],
                                        category_name=','.join(categories) if categories else None,
                                        limit=RECORDS_LIMIT, offset=page * RECORDS_LIMIT)

    if not records:
        return data, 0

    all_records = medsenger_api.get_records(contract_id, time_from=dates[0], time_to=dates[1], return_count=True,
                                            category_name=','.join(categories) if categories else None)
    page_cnt = math.ceil(all_records['count'] / RECORDS_LIMIT)

    category_info = records['category'] if categories and len(categories) == 1 else None
    if category_info:
        records = records['values']

    current_date = None
    for record in records:
        if categories and len(categories) == 1:
            record['category_info'] = category_info
        elif record['category_info']['default_representation'] == 'non_zero_dates' and record['value'] == 0:
            continue

        record['formatted_date'] = datetime.fromtimestamp(record['timestamp']).strftime('%H:%M:%S %d.%m.%Y')
        record_date = datetime.fromtimestamp(record['timestamp']).strftime('%d.%m.%Y')
        if not current_date or current_date != record_date:
            current_date = record_date
            data.append({"date": current_date, "records": [], "symptoms": []})
        if not categories and record['category_info']['default_representation'] == 'non_zero_dates':
            data[-1]["symptoms"].append(record)
        else:
            data[-1]["records"].append(record)
    return data, page_cnt


def search_params(contract):
    params = {}
    # fixme
    return []
