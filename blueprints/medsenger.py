from flask import Blueprint

from manage import *
from helpers import *
from decorators import verify_request

medsenger_blueprint = Blueprint('medsenger_endpoints', __name__, template_folder='templates', static_folder='static')


@medsenger_blueprint.route('/status', methods=['POST'])
@verify_request(contract_manager, 'backend')
def status(data):
    answer = {
        "is_tracking_data": False,
        "supported_scenarios": [],
        "tracked_contracts": contract_manager.get_active_ids()
    }

    return jsonify(answer)


@medsenger_blueprint.route('/order', methods=['POST'])
@verify_request(contract_manager, 'backend')
def order(data):
    contract_id = data.get('contract_id')
    contract = contract_manager.get(contract_id)

    print(f"Got order data {data}")

    if data['order'] == 'conclusion_params':
        contract_manager.add_params(contract_id, data['params'])
        return 'ok'

    if data['order'] == 'need_conclusion':
        medsenger_api.send_message(contract_id, "Не забудьте сформировать заключение для пациента.",
                                   action_name='Сформировать заключение', action_link='conclusion',
                                   only_doctor=True)
        return 'ok'

    return "not found"


# contract management api

@medsenger_blueprint.route('/init', methods=['POST'])
@verify_request(contract_manager, 'backend')
def init(data):
    contract_id = data.get('contract_id')

    if not contract_id:
        abort(422)

    print("got init payload:", data)

    contract, is_new = contract_manager.add(contract_id)
    params = data.get('params')

    return "ok"


@medsenger_blueprint.route('/remove', methods=['POST'])
@verify_request(contract_manager, 'backend')
def remove(data):
    contract_id = data.get('contract_id')
    if not contract_id:
        abort(422)

    contract_manager.remove(contract_id)

    return "ok"


@medsenger_blueprint.route('/actions', methods=['POST'])
@verify_request(contract_manager, 'backend')
def actions(data):
    print(f"asked for actions for contract {data.get('contract_id')}")
    contract = contract_manager.get(data.get('contract_id'))

    actions = []

    return jsonify(actions)


@medsenger_blueprint.route('/message', methods=['POST'])
@verify_request(contract_manager, 'backend')
def message(data):
    return "ok"


# send to medsenger


@medsenger_blueprint.route('/send_order', methods=['POST'])
@verify_request(contract_manager, 'patient')
def send_order(args, form, contract):
    data = request.json
    answer = medsenger_api.send_order(contract.id, data['order'], receiver_id=data['agent_id'], params=data['params'])

    results = answer.get('results', {})

    if isinstance(results, list):
        results = {}

    result = results.get(str(data['agent_id']), [])

    return result


@medsenger_blueprint.route('/send_message', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def send_message(args, form, contract):
    data = request.json

    medsenger_api.send_message(contract.id, data['message'])
    return 'ok'
