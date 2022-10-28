class Alert:
    def __init__(
            self,
            device_id,
            command,
            session
    ):
        self.device_id = device_id
        self.command = command
        self.session = session
