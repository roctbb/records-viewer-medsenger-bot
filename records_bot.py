from flask import Flask, jsonify
from helpers import *
from managers.ContractsManager import ContractManager
from manage import *

contract_manager = ContractManager(medsenger_api, db)


@app.route('/status', methods=['POST'])
def status():
    answer = {
        "is_tracking_data": False,
        "supported_scenarios": [],
        "tracked_contracts": contract_manager.get_active_ids()
    }

    return json.dumps(answer)


@app.route('/init', methods=['POST'])
@verify_json
def init(data):
    contract_id = data.get('contract_id')
    if not contract_id:
        abort(422)
    contract_manager.add(contract_id)
    return 'ok'


@app.route('/order', methods=['POST'])
@verify_json
def order(data):
    contract_id = data.get('contract_id')
    if data['order'] == 'add_params':
        contract_manager.add_params(contract_id, data['params'])
        return 'ok'
    if data['order'] == 'need_conclusion':
        medsenger_api.send_message(data['contract_id'], "Не забудьте сформировать заключение для пациента.",
                                   action_name='Сформировать заключение', action_link='conclusion',
                                   only_doctor=True)
        return 'ok'


@app.route('/remove', methods=['POST'])
@verify_json
def remove(data):
    contract_id = data.get('contract_id')
    if not contract_id:
        abort(422)

    contract_manager.remove(contract_id)
    return 'ok'


@app.route('/settings', methods=['GET'])
@verify_args
def settings(args, form):
    contract_id = request.args.get('contract_id', '')

    if contract_manager.not_exists(contract_id):
        contract_manager.add(contract_id)

    contract = contract_manager.get(args.get('contract_id'))
    return get_ui(contract, source=request.args.get('source'))

# @app.route('/settings', methods=['POST'])
# def post_settings():
#     return export_report()


@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'


@app.route('/message', methods=['POST'])
def message():
    return "ok"


@app.route('/log', methods=['GET'])
@verify_args
def get_log(args, form):
    contract_id = request.args.get('contract_id', '')

    if contract_manager.not_exists(contract_id):
        contract_manager.add(contract_id)

    contract = contract_manager.get(args.get('contract_id'))

    return get_ui(contract, 'log')


@app.route('/report', methods=['GET'])
@verify_args
def get_report(args, form):
    contract_id = request.args.get('contract_id', '')

    if contract_manager.not_exists(contract_id):
        contract_manager.add(contract_id)

    contract = contract_manager.get(args.get('contract_id'))

    return get_ui(contract, source=args.get('source'))


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
    contract_id = request.args.get('contract_id', '')

    if contract_manager.not_exists(contract_id):
        contract_manager.add(contract_id)

    contract = contract_manager.get(args.get('contract_id'))

    return get_ui(contract, 'graph')


@app.route('/graph/<category_id>', methods=['GET'])
@verify_args
def graph_page_with_args(args, form, category_id):
    contract_id = request.args.get('contract_id', '')

    if contract_manager.not_exists(contract_id):
        contract_manager.add(contract_id)

    contract = contract_manager.get(args.get('contract_id'))
    return get_ui(contract, 'graph', object_id=category_id)


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

    answer = get_graph_data(contract_id, data)
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


@app.route('/api/settings/get_file', methods=['POST'])
@verify_args
def get_file(args, form):
    contract_id = request.args.get('contract_id')
    data = request.json
    file_id = data.get('id')

    file = medsenger_api.get_file(contract_id, file_id)
    if not file or file['state'] != 'ok':
        abort(404)

    return jsonify(medsenger_api.get_file(contract_id, file_id))


@app.route('/conclusion', methods=['GET'])
@verify_args
def conclusion_page(args, form):
    contract_id = request.args.get('contract_id', '')

    if contract_manager.not_exists(contract_id):
        contract_manager.add(contract_id)

    contract = contract_manager.get(args.get('contract_id'))

    return get_ui(contract, 'conclusion', params=contract.params)


@app.route('/send-conclusion', methods=['POST'])
@verify_args
def send_conclusion(args, form):
    contract_id = int(args.get('contract_id'))
    data = request.json

    medsenger_api.send_message(contract_id, data['conclusion'])

    return 'ok'


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(HOST, PORT, debug=API_DEBUG)
