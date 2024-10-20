class BaseStrategy:
    def get_next_server(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def register_server(self, server_ip):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def remove_server(self, server_ip):
        raise NotImplementedError("This method should be overridden by subclasses.")
