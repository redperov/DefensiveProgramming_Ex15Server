import socket
import selectors
import struct
import uuid

import codes
import sizes
from db import DBConnection
from request import Request
from response import Response
from client import Client
from message import Message

# Server port file path
SERVER_PORT_PATH = "port.info"
SERVER_DB_NAME = "server.db"

# Server's version TODO change if implemented the bonus
SERVER_VERSION = 1

# Maximum allowed number of connections by the server
MAX_CONNECTIONS_ALLOWED = 100


class Server:
    def __init__(self):
        # Get the server's port number
        try:
            self.port = self.read_port()
        except Exception as e:
            raise ValueError("Failed reading port number", e)

        # Define a selector to handle multiple connections
        self.selector = selectors.DefaultSelector()

        # Create a DB client
        try:
            self.db = DBConnection(SERVER_DB_NAME)
        except Exception as e:
            raise ValueError("DB error", e)

    def start(self):

        # Set up a socket for accepting connections
        sock = socket.socket()
        sock.bind(("localhost", self.port))
        sock.listen(MAX_CONNECTIONS_ALLOWED)
        sock.setblocking(False)
        self.selector.register(sock, selectors.EVENT_READ, self.accept)

        # Receive connections
        print("Waiting for incoming connections...")
        while True:
            events = self.selector.select()

            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def accept(self, sock, mask):
        # TODO handle disconnection
        connection, address = sock.accept()
        print(f"Received {connection} from {address}")
        connection.setblocking(False)
        self.selector.register(connection, selectors.EVENT_READ, self.read)

    def read(self, connection, mask):
        try:
            response = self.handle_request(connection)
        except Exception as e:
            print("Error occurred while handling request:", e)
            response = Response(SERVER_VERSION, codes.GENERAL_ERROR, 0, None)

        # TODO handle disconnection
        if response:
            print(f"Returning response: {repr(response)} to: {connection}")
            connection.send(response)
        else:
            print("Closing:", connection)
            self.selector.unregister(connection)
            connection.close()

    def handle_request(self, connection):

        # Read the request from the socket
        try:
            request = self.read_request(connection)
        except Exception as e:
            raise ValueError("Failed reading request due to:", e)

        # Handle request according to the received code
        code = request.get_code()

        if code == codes.REGISTER_REQUEST:  # Register client
            response = self.register_client(request)

        elif code == codes.GET_CLIENTS_LIST_REQUEST:  # Get all clients
            response = self.get_clients_list(request)

        elif code == codes.GET_CLIENT_PUBLIC_KEY_REQUEST:  # Get a client's public key
            response = self.get_client_public_key(request)

        elif code == codes.SEND_CLIENT_MESSAGE_REQUEST:  # Send client a message
            response = self.send_client_message(request)

        elif code == codes.GET_WAITING_MESSAGES_REQUEST:  # Get all the waiting messages
            response = self.get_waiting_messages(request)
        else:
            raise ValueError("Received illegal request code", code)

        return response

    @staticmethod
    def read_request(connection):
        """
        Reads the client's request from the socket
        :param connection: socket connection to client.
        :return: Request
        """
        client_id = struct.unpack(f"<{sizes.CLIENT_ID_SIZE}s", connection.recv(sizes.CLIENT_ID_SIZE))[0].decode("utf-8")
        client_version = struct.unpack("<B", connection.recv(sizes.VERSION_SIZE))[0]
        code = struct.unpack("<H", connection.recv(sizes.CODE_SIZE))[0]
        payload_size = struct.unpack("<I", connection.recv(sizes.PAYLOAD_SIZE_SIZE))[0]

        if payload_size:
            payload = struct.unpack(f"<{payload_size}s", connection.recv(payload_size))[0]
        else:
            payload = None

        return Request(client_id, client_version, code, payload_size, payload)

    @staticmethod
    def read_port():
        """
        Reads the server's port number from the configuration file.
        :return: port number
        """
        with open(SERVER_PORT_PATH, "r") as file:
            data = file.readline()
            port = int(data)
            return port

    def register_client(self, request):
        """
        Adds a new client to the DB.
        :param request: client Request
        :return: Response
        """
        # Extract the client's name and public key from the payload
        payload = request.get_payload()
        client_name = struct.unpack(f"<{sizes.NAME_SIZE}s", payload[0:sizes.NAME_SIZE])
        public_key = struct.unpack(f"{sizes.PUBLIC_KEY_SIZE}s", payload[sizes.PUBLIC_KEY_SIZE:])

        # Check if the client already exists in the DB
        if self.db.get_client_by_name(client_name):
            raise ValueError("Can't register an already existing client:", client_name)

        # Generate a unique client id
        client_id = uuid.uuid4()

        # Add a new client to the clients table
        client = Client(client_id, client_name, public_key, None)
        self.db.insert_client(client)

        # Return a successful response to the client
        return Response(SERVER_VERSION, codes.REGISTRATION_SUCCESSFUL_RESPONSE, 0, None)

    def get_clients_list(self, request):
        """
        Retrieves the list of all the clients saved in the server.
        :param request: client Request
        :return: Response
        """
        # Retrieve all the clients from the DB
        clients = self.db.get_all_clients()

        # Exclude the requesting user from the list
        requesting_client_id = request.get_client_id()
        filtered_clients = [client for client in clients if client.get_id() != requesting_client_id]
        payload = ""

        # Pack the list of clients together as the response's payload
        for client in filtered_clients:
            payload += struct.pack(f"<{sizes.CLIENT_ID_SIZE}s{len(client.get_name())}s",
                                   client.get_id().encode("utf-8"), client.get_name().encode("utf-8"))

        # Return a successful response to the client
        return Response(SERVER_VERSION, codes.CLIENTS_LIST_RETURNED_RESPONSE, len(payload), payload)

    def get_client_public_key(self, request):
        """
        Retrieves a client's public key.
        :param request: Request containing the id of the client whose public key to retrieve
        :return: Response
        """
        payload = request.get_payload()
        receiver_client_id = struct.unpack(f"<{sizes.CLIENT_ID_SIZE}s", payload[:sizes.CLIENT_ID_SIZE])[0]

        # Retrieve the corresponding client from the DB
        client = self.db.get_client_by_id(receiver_client_id)

        if not client:
            raise ValueError(f"Client with id: {receiver_client_id} not found")

        # Pack the client's id and public key as the response
        receiver_client_public_key = client.get_public_key()
        response_payload = struct.pack(f"<{sizes.CLIENT_ID_SIZE}s{sizes.PUBLIC_KEY_SIZE}s",
                                       receiver_client_id.encode("utf-8"), receiver_client_public_key.encode("utf-8"))

        # Return a successful response to the client
        return Response(SERVER_VERSION, codes.CLIENT_PUBLIC_KEY_RETURNED_RESPONSE, len(response_payload), response_payload)

    def send_client_message(self, request):
        """
        Adds a message to the messages table in the DB.
        :param request: Request containing a message
        :return: Response
        """
        # Extract the the message type and its content
        payload = request.get_payload()
        current_position = 0
        receiver_client_id = struct.unpack(f"<{sizes.CLIENT_ID_SIZE}s", payload[0:sizes.CLIENT_ID_SIZE])
        current_position += sizes.CLIENT_ID_SIZE
        message_type = struct.unpack("<B", payload[current_position:sizes.MESSAGE_TYPE_SIZE])
        current_position += sizes.MESSAGE_TYPE_SIZE
        content_size = struct.unpack("<I", payload[current_position:sizes.MESSAGE_CONTENT_SIZE_SIZE])
        current_position += sizes.MESSAGE_CONTENT_SIZE_SIZE
        message_content = struct.unpack(f"<{content_size}s", payload[current_position:])

        # Save the message in the DB
        message = Message(receiver_client_id, request.get_client_id(), message_type, message_content)
        self.db.insert_message(message)

        # Pack the receiving client id and message id as the response payload
        response_payload = struct.pack(f"<{sizes.CLIENT_ID_SIZE}sI", receiver_client_id, message.get_id())

        # Return a successful response to the client
        return Response(SERVER_VERSION, codes.MESSAGE_SENT_TO_CLIENT_RESPONSE, len(response_payload), response_payload)

    def get_waiting_messages(self, request):
        """
        Retrieve the client's waiting messages.
        :param request: client Request
        :return: Response
        """
        # Retrieve the client's waiting messages from the DB
        messages = self.db.get_messages_by_receiver_id(request.get_client_id())
        payload = struct.pack(f"<{sizes.CLIENT_ID_SIZE}s", request.get_client_id().encode("utf-8"))

        for message in messages:
            payload += struct.pack(f"<IBI{len(message.get_content())}s", message.get_id(), message.get_type(),
                                   len(message.get_content()), message.get_content().encode("utf-8"))

        # TODO delete messages after sending, maybe move the send into each handler method
        return Response(SERVER_VERSION, codes.WAITING_MESSAGES_RETURNED_RESPONSE, len(payload), payload)
