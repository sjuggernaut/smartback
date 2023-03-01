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
            "step": self.step
        }


class CalibrationStartAlert(Alert):
    def __init__(
            self,
            command,
            session,
            session_type
    ):
        self.command = command
        self.session = session
        self.session_type = session_type

    def prepare_to_send(self):
        return {
            "command": self.command,
            "session": self.session,
            "session_type": self.session_type
        }


class CalibrationStepStartAlert(Alert):
    def __init__(
            self,
            command,
            step
    ):
        self.command = command
        self.step = step

    def prepare_to_send(self):
        return {
            "command": self.command,
            "step": self.step,
        }


class CalibrationEndAlert(Alert):
    def __init__(
            self,
            command,
            session
    ):
        self.command = command
        self.session = session

    def prepare_to_send(self):
        return {
            "command": self.command,
            "session": self.session
        }

