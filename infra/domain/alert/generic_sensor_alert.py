from infra.domain.alert.alert import Alert


class GenericSensorAlert(Alert):
    def __init__(
            self,
            command,
            devices=None,
            session=None
    ):
        self.command = command
        self.session = session
        self.devices = devices

    def prepare_to_send(self):
        return {
            "command": self.command,
            "session": self.session,
            "devices": self.devices
        }
