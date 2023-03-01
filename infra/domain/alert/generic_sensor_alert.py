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


class TreatmentStartAlert(Alert):
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


class TreatmentStartDataSendAlert(Alert):
    def __init__(
            self,
            command,
            session,
    ):
        self.command = command
        self.session = session

    def prepare_to_send(self):
        return {
            "command": self.command,
            "session": self.session,
        }
