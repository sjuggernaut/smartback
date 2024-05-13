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


class TreatmentAbruptDataSendAlert(Alert):
    def __init__(
            self,
            command,
            user
    ):
        self.command = command
        self.user = user

    def prepare_to_send(self):
        return {
            "command": self.command,
            "user": self.user,
        }


class TreatmentResultAlert(Alert):
    def __init__(
            self,
            command,
            session,
            energy,
            side
    ):
        self.command = command
        self.session = session
        self.energy = energy
        self.side = side

    def prepare_to_send(self):
        return {
            "command": self.command,
            "session": self.session,
            "energy": self.energy,
            "side": self.side
        }


class SessionStartAlert(Alert):
    def __init__(
            self,
            command,
            user
    ):
        self.command = command
        self.user = user

    def prepare_to_send(self):
        return {
            "command": self.command,
            "user": self.user
        }


class CalibrationStepStartAlertEngine(Alert):
    def __init__(
            self,
            command,
            user,
            step
    ):
        self.command = command
        self.user = user
        self.step = step

    def prepare_to_send(self):
        return {
            "command": self.command,
            "user": self.user,
            "step": self.step
        }


class CalibrationEndAlertEngine(Alert):
    def __init__(
            self,
            command,
            user,
            procedure
    ):
        self.command = command
        self.user = user
        self.procedure = procedure

    def prepare_to_send(self):
        return {
            "command": self.command,
            "user": self.user,
            "procedure": self.procedure
        }
