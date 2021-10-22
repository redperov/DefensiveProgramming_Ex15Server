import struct


class Response:
    def __init__(self, version, code, payload_size, payload):
        self.version = version
        self.code = code
        self.payload_size = payload_size
        self.payload = payload

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
