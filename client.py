class Client:
    def __init__(self, ID, Name, PublicKey, LastSeen):
        """
        Constructor.
        :param ID: client's id
        :param Name: client's name
        :param PublicKey: client's public key
        :param LastSeen: when the client sent his last message
        """
        self.ID = ID
        self.Name = Name
        self.PublicKey = PublicKey
        self.LastSeen = LastSeen

    # Getters

    def get_id(self):
        return self.ID

    def get_name(self):
        return self.Name

    def get_public_key(self):
        return self.PublicKey

    def get_last_seen(self):
        return self.LastSeen
