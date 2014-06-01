class Api:
    def __init__(self, connection, txn_id):
        self.connection = connection
        self.txn_id = txn_id

    def execute(self, method, **params):
        response = getattr(self.connection, method)(params) # Hack from poaupdater
        if response['status'] != 0:
            raise Exception('Method {0} returned non-zero status {1} and\
                             error {2}'.format(method, response['status'], response['error_message']))
            self.txn_id = None
        else:
            return response.get('result', None)