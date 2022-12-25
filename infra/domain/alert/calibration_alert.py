from infra.domain.alert.alert import Alert


class CalibrationAlert(Alert):
    def __init__(
            self,
            command,
            step,
            devices
    ):
        self.command = command
        self.step = step
        self.devices = devices

    def prepare_to_send(self):
        return {
            "command": self.command,
            "step": self.step,
            "devices": self.devices
        }
