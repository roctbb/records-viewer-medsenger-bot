from flask import Blueprint, redirect, url_for

from manage import *
from helpers import *
from decorators import verify_request


actions_blueprint = Blueprint('actions_endpoints', __name__, template_folder='templates', static_folder='static')


@actions_blueprint.route('/settings', methods=['GET'])
@verify_request(contract_manager, 'backend')
def get_settings(args, form, contract):
    return get_ui(contract, 'settings', source=request.args.get('source'), role='doctor')


# reports


@actions_blueprint.route('/report', methods=['GET'])
@verify_request(contract_manager, 'patient')
def report_page(args, form, contract):
    return get_ui(contract, source=args.get('source'))


@actions_blueprint.route('/log', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def log_page(args, form, contract):
    return get_ui(contract, 'log', source='doctor')


# graphs

@actions_blueprint.route('/graph', methods=['GET'])
@verify_request(contract_manager, 'patient')
def graph_page(args, form, contract):
    return get_ui(contract, 'graph')


@actions_blueprint.route('/single_graph/<category_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def single_graph_page(args, form, contract, category_id):
    return get_ui(contract, 'graph-presenter', object_id=category_id)


@actions_blueprint.route('/group/<category_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def group_page_with_args(args, form, contract, category_id):
    return get_ui(contract, 'group-presenter', object_id=category_id)


@actions_blueprint.route('/graph/<category_id>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def graph_page_with_args(args, form, contract, category_id):
    endpoint, object_id = get_graph_id(category_id)

    return redirect(url_for(endpoint, category_id=object_id, source=args.get('source'),
                            contract_id=contract.id, api_key=args.get('api_key')))


@actions_blueprint.route('/group/<category_id>/<mode>/<int:date_from>/<int:date_to>', methods=['GET'])
@verify_request(contract_manager, 'patient')
def group_page_with_args_report(args, form, contract, category_id, mode, date_from, date_to):
    return get_ui(contract, 'group-presenter', object_id=category_id, params={
        "mode": mode,
        "date_from": date_from,
        "date_to": date_to
    })


# conclusion


@actions_blueprint.route('/conclusion', methods=['GET'])
@verify_request(contract_manager, 'doctor')
def conclusion_page(args, form, contract):
    return get_ui(contract, 'conclusion', params=contract.params)


@actions_blueprint.route('/send_conclusion', methods=['POST'])
@verify_request(contract_manager, 'doctor')
def send_conclusion(args, form, contract):
    data = request.json

    medsenger_api.send_message(contract.id, data['conclusion'])
    return 'ok'



