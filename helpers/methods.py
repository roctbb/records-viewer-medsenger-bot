import json
import math
import threading
from datetime import datetime

from flask import request, abort, jsonify, render_template
from medsenger_api import AgentApiClient
from sentry_sdk import capture_exception
import sys, os
from config import *
import os

DATACACHE = {}
medsenger_api = AgentApiClient(APP_KEY, MAIN_HOST, AGENT_ID, API_DEBUG, USE_GRPC, GRPC_HOST, sentry_dsn=SENTRY)
text_categories = ['symptom', 'medicine', 'patient_comment', 'information', 'side_effect']


def get_ui(contract, page='settings', object_id=None, source=None, role='doctor', params=None):
    if params is None:
        params = {}

    token = 'undefined'
    contract_id = 'undefined'

    if contract:
        contract_id = contract.id
        if role == 'doctor':
            token = contract.doctor_agent_token
        else:
            token = contract.patient_agent_token

    print('new', contract.id, contract.agent_token)

    return render_template('index.html',
                           contract_id=contract_id, agent_token=contract.agent_token,
                           mode=page, object_id=object_id, source=source,
                           params=json.dumps(params), agents=json.dumps(AGENTS),
                           api_host=MAIN_HOST.replace('8001', '8000'), js_host=JSHOST, localhost=LOCALHOST,
                           agent_id=AGENT_ID, lc=dir_last_updated('static'))


def delayed(delay, f, args):
    timer = threading.Timer(delay, f, args=args)
    timer.start()


def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))


def toInt(value, default=None):
    try:
        return int(value)
    except:
        return default


text_categories = ['symptom', 'medicine', 'patient_comment', 'information', 'side_effect']


def get_records_list(contract_id, categories, dates, options=None):
    if options is None:
        options = {}
    info = {
        'type': options.get('type'),
        'first_load': options.get('first_load')
    }

    if options.get('first_load'):
        last_record = medsenger_api.get_records(contract_id, (','.join(categories) + ','), limit=1)
        if last_record and len(last_record):
            last_date = datetime.fromtimestamp(last_record[0]['timestamp']).replace(hour=23, minute=59, second=59)
        else:
            last_date = datetime.now().replace(hour=23, minute=59, second=59)
        last_timestamp = int(round(last_date.timestamp()))
        dates = [last_timestamp - 14 * 24 * 60 * 60 + 1, last_timestamp]
    info['dates'] = dates

    if options.get('type') == 'line':
        categories += text_categories

    limit = RECORDS_LIMIT if options.get('type') == 'report' else None
    offset = options.get('page', 0) * RECORDS_LIMIT

    records = medsenger_api.get_records(contract_id, time_from=dates[0], time_to=dates[1],
                                        category_name=(','.join(categories) + ','),
                                        limit=limit, offset=offset)
    if not records:
        records = []

    if options.get('type') == 'report' and options.get('get_pages_count'):
        all_records = medsenger_api.get_records(contract_id, time_from=dates[0], time_to=dates[1], return_count=True,
                                                category_name=','.join(categories) if categories else None)
        count = all_records['count'] if all_records else 0
        info['page_count'] = math.ceil(count / RECORDS_LIMIT)

    for record in records:
        if record['category_info']['default_representation'] == 'non_zero_dates' and record['value'] == 0:
            continue

    answer = {
        'records': records,
        'info': info
    }

    return answer

def search_params(contract):
    params = {}
    # fixme
    return []
