class ConnectionDetails:
    def __init__(
        self,
        method,
        user=None,
        password=None,
        server=None,
        port=None,
        dir=None,
        share=None,
    ):
        self.method = method
        self.user = user
        self.password = password
        self.server = server
        self.port = port
        self.dir = dir
        self.share = share
