import sqlite3
from client import Client
from message import Message

# Table names
CLIENTS_TABLE_NAME = "clients"
MESSAGES_TABLE_NAME = "messages"

# Queries
IS_TABLE_EXISTS_QUERY = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"


class DBConnection:
    """
    Database connection handler.
    """

    def __init__(self, db_name):
        """
        Constructor.
        :param db_name: name of the server's db
        """
        # Establish a connection with the DB
        self.connection = sqlite3.connect(db_name)
        self.connection.text_factory = bytes

        # TODO delete
        # self.connection.execute("DROP TABLE clients")
        # self.connection.execute("DROP TABLE messages")
        # self.connection.commit()

        # Ensure that the needed tables exist
        self.check_tables_exist()

    def check_tables_exist(self):
        """
        Checks that the server's tables exist. If they don't, creates them.
        :return: None
        """
        print("Checking if the server's tables exist")
        cursor = self.connection.cursor()

        # Check that the clients table exists
        list_of_tables = cursor.execute(IS_TABLE_EXISTS_QUERY, [CLIENTS_TABLE_NAME]).fetchall()

        if list_of_tables:
            print(f"{CLIENTS_TABLE_NAME} table already exists")
        else:
            print(f"{CLIENTS_TABLE_NAME} table doesn't exist, creating it...")
            cursor.execute(f"""CREATE TABLE {CLIENTS_TABLE_NAME} (ID varchar(16) NOT NULL PRIMARY KEY,
                            Name varchar(255), PublicKey varchar(160), LastSeen TEXT)""")
            self.connection.commit()
            print(f"Created {CLIENTS_TABLE_NAME} table successfully")

        # Check that the messages table exists
        list_of_tables = cursor.execute(IS_TABLE_EXISTS_QUERY, [MESSAGES_TABLE_NAME]).fetchall()

        if list_of_tables:
            print(f"{MESSAGES_TABLE_NAME} table already exists")
        else:
            print(f"{MESSAGES_TABLE_NAME} table doesn't exist, creating it...")
            cursor.execute(f"""CREATE TABLE {MESSAGES_TABLE_NAME} (ID varchar(4) NOT NULL PRIMARY KEY,
                            ToClient varchar(16), FromClient varchar(16), Type varchar(1), Content BLOB)""")
            self.connection.commit()
            print(f"Created {MESSAGES_TABLE_NAME} table successfully")

    def insert_client(self, client):
        """
        Inserts a client to the clients table.
        :param client: client to insert
        """
        print(f"Adding client with id {client.get_id()} to {CLIENTS_TABLE_NAME}...")
        if not isinstance(client, Client):
            raise ValueError("Expected to receive a Client but received:", client)
        # self.clients[client.get_id()] = client
        self.connection.execute(f"INSERT INTO {CLIENTS_TABLE_NAME} VALUES(?, ?, ?, ?)"
                                , [client.get_id(), client.get_name(), client.get_public_key(), client.get_last_seen()])
        self.connection.commit()
        print(f"Client with id {client.get_id()} added to {CLIENTS_TABLE_NAME}")

    def get_client_by_id(self, client_id):
        """
        Retrieves a client from the clients table according to the given id.
        :param client_id: client id
        :return: client if found, None otherwise
        """
        print(f"Retrieving client with id: {client_id}")
        cursor = self.connection.cursor()
        result = cursor.execute(f"SELECT * FROM {CLIENTS_TABLE_NAME} WHERE ID = ?", [client_id]).fetchall()

        if not result:
            print(f"No client with ID {client_id} was found in {CLIENTS_TABLE_NAME} table")
            return None
        client = Client(*result[0])
        print(f"Retrieved client: {client}")

        return Client(*result[0])

    def get_client_by_name(self, client_name):
        """
        Retrieves a client from the clients table according to the given name.
        :param client_name: client name
        :return: client if found, None otherwise
        """
        print(f"Retrieving client with name: {client_name}")
        cursor = self.connection.cursor()
        result = cursor.execute(f"SELECT * FROM {CLIENTS_TABLE_NAME} WHERE Name = ?", [client_name]).fetchall()

        if not result:
            print(f"No client with Name {client_name} was found in {CLIENTS_TABLE_NAME} table")
            return None
        client = Client(*result[0])
        print(f"Retrieved client: {client}")

        return client

    def get_all_clients(self):
        """
        Retrieves all the clients in the clients table.
        :return: clients
        """
        print(f"Retrieving all the clients in {CLIENTS_TABLE_NAME}...")
        cursor = self.connection.cursor()
        rows = cursor.execute(f"SELECT * FROM {CLIENTS_TABLE_NAME}").fetchall()

        if not rows:
            print(f"There are no clients in the {CLIENTS_TABLE_NAME} table")
            return None
        clients = [Client(*row) for row in rows]
        print(f"Retrieved clients: {clients}")

        return clients

    def insert_message(self, message):
        """
        Inserts a message to the messages table.
        :param message: message to insert
        """
        print(f"Adding message with id {message.get_id()} to {MESSAGES_TABLE_NAME}...")
        if not isinstance(message, Message):
            raise ValueError("Expected to receive a Message but received:", message)
        self.connection.execute(f"INSERT INTO {MESSAGES_TABLE_NAME} VALUES(?, ?, ?, ?, ?)"
                                , [message.get_id(), message.get_to_client(), message.get_from_client(),
                                   message.get_type(), message.get_content()])
        self.connection.commit()
        print(f"Message with id {message.get_id()} added to {MESSAGES_TABLE_NAME}")

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
        print(f"Retrieving messages with receiver id: {receiver_id}")
        cursor = self.connection.cursor()
        rows = cursor.execute(f"SELECT * FROM {MESSAGES_TABLE_NAME} WHERE ToClient = ?", [receiver_id]).fetchall()

        if not rows:
            print(f"No messages with receiver id {receiver_id} were found in {CLIENTS_TABLE_NAME} table")
            return None
        messages = [Message(*row) for row in rows]
        print(f"Retrieved messages: {messages}")

        return messages

    def delete_messages_by_ids(self, ids):
        print("Deleting messages with ids:", ids)
        query = "DELETE FROM " + MESSAGES_TABLE_NAME + " WHERE id IN (%s)" % ','.join(['?'] * len(ids))
        self.connection.execute(query, ids)
        self.connection.commit()
        print("successfully delete messages")
