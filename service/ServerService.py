from module.Server import Server


class ServerService(object):
    def __init__(self):
        self.server_db = Server()

    def get_list(self, state):
        return self.server_db.get_list(state)
