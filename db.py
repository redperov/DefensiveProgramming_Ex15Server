from client import Client
from message import Message


class DBConnection:
    """
    Database connection handler.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.clients = {}
        self.messages = {}

    def insert_client(self, client):
        """
        Inserts a client to the clients table.
        :param client: client to insert
        """
        if client is not Client:
            raise ValueError("Expected to receive a Client but received:", client)
        self.clients[client.get_id()] = client

    def get_client_by_id(self, client_id):
        """
        Retrieves a client from the clients table according to the given id.
        :param client_id: client id
        :return: client if found, None otherwise
        """
        if client_id in self.clients:
            return self.clients[client_id]
        return None

    def get_client_by_name(self, client_name):
        """
        Retrieves a client from the clients table according to the given name.
        :param client_name: client name
        :return: client if found, None otherwise
        """
        for client in self.clients.values():
            if client.get_name() == client:
                return client
        return None

    def get_all_clients(self):
        """
        Retrieves all the clients in the clients table.
        :return: clients
        """
        return self.clients

    def insert_message(self, message):
        """
        Inserts a message to the messages table.
        :param message: message to insert
        """
        if message is not Message:
            raise ValueError("Expected to receive a Message but received:", message)
        if message.get_to_client() in self.messages:
            client_messages = self.messages[message.get_to_client]
        else:
            client_messages = []
        client_messages.append(message)

        self.messages[message.get_to_client] = client_messages

    # def get_message(self, message_id):
    #     """
    #     Retrieves a message from the messages table.
    #     :param message_id: message id
    #     :return: message if found, None otherwise
    #     """
    #     if message_id in self.messages:
    #         return self.messages[message_id]
    #     return None

    def get_messages_by_receiver_id(self, receiver_id):
        """
        Retrieves all the messages that wait for the given receiver id.
        :param receiver_id: receiver id
        :return: list of messages
        """
        if receiver_id in self.messages:
            return self.messages[receiver_id]
        return None
