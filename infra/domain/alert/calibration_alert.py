class CalibrationAlert:
    def __init__(
            self,
            device_id,
            command,
            session,
            step,
            direction,

    ):
        self.device_id = device_id
        self.command = command
        self.session = session
        self.step = step
        self.direction = direction

    def prepare_to_send(self):
        return {
            "device_id": self.device_id,
            "command": self.command,
            "session": self.session,
            "step": self.step,
            "direction": self.direction
        }
