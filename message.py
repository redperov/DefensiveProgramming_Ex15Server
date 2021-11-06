# import itertools
import uuid
import sizes


class Message:

    def __init__(self, ID, ToClient, FromClient, Type, Content):
        """
        Constructor.
        :param ID: message id, if left empty a new id will be generated
        :param ToClient: message recipient
        :param FromClient: message sender
        :param Type: message type
        :param Content: message content
        """
        # self.ID = next(Message.id_counter)  # Get the next value from the incremental id counter
        if ID:
            self.ID = ID
        else:
            self.ID = uuid.uuid4().bytes[:sizes.MESSAGE_ID_SIZE]
        self.ToClient = ToClient
        self.FromClient = FromClient
        self.Type = Type
        self.Content = Content

    def get_id(self):
        return self.ID

    def get_from_client(self):
        return self.FromClient

    def get_to_client(self):
        return self.ToClient

    def get_type(self):
        return self.Type

    def get_content(self):
        return self.Content
