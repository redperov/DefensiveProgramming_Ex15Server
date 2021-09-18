import itertools


class Message:

    # Used to create an incremental id
    id_counter = itertools.count().next

    def __init__(self, ToClient, FromClient, Type, Content):
        """
        Constructor.
        :param ToClient: message recipient
        :param FromClient: message sender
        :param Type: message type
        :param Content: message content
        """
        self.ID = Message.id_counter()
        self.ToClient = ToClient
        self.FromClient = FromClient
        self.Type = Type
        self.Content = Content

    def get_id(self):
        return self.ID

    def get_to_client(self):
        return self.ToClient

    def get_type(self):
        return self.Type

    def get_content(self):
        return self.Content