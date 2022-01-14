from flask import Flask, jsonify
from helpers import *

app = Flask(__name__)


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

    if contract_id not in contracts.keys():
        init_contract(contract_id)

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

    if contract_id not in contracts.keys():
        init_contract(contract_id)

    return get_ui(contract_id, 'report')


@app.route('/api/report', methods=['POST'])
@verify_args
def get_data(args, form):
    contract_id = int(request.args.get('contract_id'))
    data = request.json

    page = data.get('page', 0)
    dates = data.get('dates', None)
    categories = data.get('categories', None)

    result, page_cnt = get_report_page(contract_id, dates, page, categories)
    return jsonify({'dates': result, 'page': page, 'page_cnt': page_cnt})


@app.route('/graph', methods=['GET'])
@verify_args
def graph_page(args, form):
    contract_id = int(request.args.get('contract_id'))
    return get_ui(contract_id, 'graph')


@app.route('/graph/<category_id>', methods=['GET'])
@verify_args
def graph_page_with_args(args, form, category_id):
    contract_id = int(request.args.get('contract_id'))
    return get_ui(contract_id, 'graph', object_id=category_id)


@app.route('/api/categories', methods=['GET'])
@verify_args
def graph_categories(args, form):
    contract_id = args.get('contract_id')
    categories = medsenger_api.get_available_categories(contract_id)

    return jsonify(categories)


@app.route('/api/graph/group', methods=['POST'])
@verify_args
def graph_data(args, form):
    contract_id = args.get('contract_id')
    data = request.json
    group = data.get('group')
    dates = data.get('dates', None)

    answer = [(medsenger_api.get_records(contract_id, category_name) if dates is None
               else medsenger_api.get_records(contract_id, category_name, time_from=dates['start'], time_to=dates['end']))
              for category_name in group['categories']]
    answer = list(filter(lambda x: x is not None, answer))

    return jsonify(answer)


@app.route('/params', methods=['GET'])
@verify_args
def get_params(args, data):
    contract_id = args.get('contract_id')
    return jsonify(search_params(contract_id))


@app.route('/api/settings/get_patient', methods=['GET'])
@verify_args
def get_patient(args, form):
    contract_id = request.args.get('contract_id')
    return jsonify(get_patient_data(contract_id))


if __name__ == "__main__":
    load()
    app.run(HOST, PORT, debug=API_DEBUG)
