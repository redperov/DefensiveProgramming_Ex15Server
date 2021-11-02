import struct


class Response:
    """
    A class that represents a response object that will be packed into a bytes representation and sent to a client.
    """
    def __init__(self, version, code, payload_size, payload):
        self.version = version
        self.code = code
        self.payload_size = payload_size
        self.payload = payload

        # Holds messages that should be deleted after the response is sent
        self.messages_to_delete = None

    def get_messages_to_delete(self):
        return self.messages_to_delete

    def set_messages_to_delete(self, messages):
        self.messages_to_delete = messages

    def pack(self):
        """
        Packs the response into a little endian representation.
        :return: packed response
        """
        if self.payload:
            return struct.pack(f"<BHI{self.payload_size}s", self.version, self.code, self.payload_size, self.payload)
        return struct.pack("<BHI", self.version, self.code, self.payload_size)

    def __str__(self):
        return f"Version: {self.version}, code: {self.code}, payload size: {self.payload_size}," \
               f" payload: {self.payload}"
