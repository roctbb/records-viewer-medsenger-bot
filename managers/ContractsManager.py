from helpers import log
from managers.Manager import Manager
from models import Contract


class ContractManager(Manager):
    def __init__(self, *args):
        super(ContractManager, self).__init__(*args)

    def add(self, contract_id):
        is_new = False
        contract = Contract.query.filter_by(id=contract_id).first()

        if not contract:
            is_new = True
            contract = Contract(id=contract_id)
            self.db.session.add(contract)

        contract.is_active = True

        self.request_tokens(contract)

        self.__commit__()

        return contract, is_new

    def remove(self, contract_id):
        try:
            contract = Contract.query.filter_by(id=contract_id).first()

            if not contract:
                raise Exception("No contract_id = {} found".format(contract_id))

            contract.is_active = False
            self.__commit__()
        except Exception as e:
            log(e)

    def get(self, contract_id, active=None):
        contract = Contract.query.filter_by(id=contract_id).first()

        if not contract:
            raise Exception("No contract_id = {} found".format(contract_id))

        return contract

    def check(self, contract_id, token):
        contract = Contract.query.filter_by(id=contract_id).first()

        if not contract:
            return False
        return True

    def not_exists(self, contract_id):
        contract = Contract.query.filter_by(id=contract_id).first()

        return not contract

    def add_params(self, contract_id, params):
        try:
            contract = Contract.query.filter_by(id=contract_id).first()

            if not contract:
                raise Exception("No contract_id = {} found".format(contract_id))

            if not contract.params:
                contract.params = params
            else:
                contract.params.update(params)

            self.__commit__()
            return contract
        except Exception as e:
            log(e)

    def request_tokens(self, contract, commit=False):
        tokens = self.medsenger_api.get_agent_token(contract.id)

        contract.patient_agent_token = tokens.get('patient_agent_token')
        contract.doctor_agent_token = tokens.get('doctor_agent_token')

        if commit:
            self.__commit__()


    def get_active_ids(self):
        return [contract.id for contract in Contract.query.filter_by(is_active=True).all()]
