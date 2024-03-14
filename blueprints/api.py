from flask import Blueprint

from manage import *
from helpers import *
from decorators import verify_request

api_blueprint = Blueprint('api_endpoints', __name__, template_folder='templates', static_folder='static')


# get data
@api_blueprint.route('/get_patient', methods=['GET'])
@verify_request(contract_manager, 'patient')
def get_patient(args, form, contract):
    patient = medsenger_api.get_patient_info(contract.id)
    patient["current_contract"] = contract.as_dict()

    return jsonify(patient)


@api_blueprint.route('/get_records', methods=['POST'])
@verify_request(contract_manager, 'patient')
def get_patient_records(args, form, contract):
    data = request.json

    options = data.get('options', None)
    dates = data.get('dates', None)
    categories = data.get('categories', None)
    required_categories = data.get('required_categories', None)

    answer = get_records_list(contract.id, categories, dates, options, required_categories)

    return jsonify(answer)


@api_blueprint.route('/categories', methods=['GET'])
@verify_request(contract_manager, 'patient')
def graph_categories(args, form, contract):
    categories = medsenger_api.get_available_categories(contract.id)
    groups = category_groups_manager.get_all(list(map(lambda x: x['name'], categories)))

    answer = {
        'categories': categories,
        'groups': groups
    }

    return jsonify(answer)


@api_blueprint.route('/get_file/<file_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def get_file(args, form, contract, file_id):
    file = medsenger_api.get_file(contract.id, file_id)

    if not file or file['state'] != 'ok':
        abort(404)

    return jsonify(file)


@api_blueprint.route('/params', methods=['GET'])
@verify_request(contract_manager, 'patient')
def get_params(args, form, contract):
    return jsonify(search_params(contract.id))

