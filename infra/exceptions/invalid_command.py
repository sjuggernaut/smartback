class InvalidCommandException(Exception):
    def __init__(self, command, *args):
        super().__init__(args)
        self.command = command

    def __str__(self):
        return f"The incoming message has invalid command {self.command}"
