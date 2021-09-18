class Request:
    def __init__(self, client_id, client_version, code, payload_size, payload):
        self.client_id = client_id
        self.client_version = client_version
        self.code = code
        self.payload_size = payload_size
        self.payload = payload

    def get_client_id(self):
        return self.client_id

    def get_code(self):
        return self.code

    def get_payload_size(self):
        return self.payload_size

    def get_payload(self):
        return self.payload
