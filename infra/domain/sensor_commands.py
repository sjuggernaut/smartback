from enum import Enum
import os

from smartback.configuration import get_config

environment = os.getenv("ENVIRONMENT")
configuration = get_config(environment)


class SensorCommands(Enum):
    # Commands sent by the Engine to the Sensors
    set_session_alert = {"name": "set_session_alert",
                         "assembler": None}  # Sets the session ID on all the Sensor's processes
    set_calibration_start = {"name": "calibration_start",
                             "assembler": None}  # Makes the sensors send data for calibration
    set_calibration_step_start = {"name": "calibration_step_start",
                                  "assembler": None}  # Makes the sensors send data for calibration
    set_calibration_end = {"name": "calibration_end",
                           "assembler": None}  # Makes the sensors stop sending data for calibration
    set_calibration_pause = {"name": "calibration_pause",
                             "assembler": None}  # Makes the sensors stop sending data for calibration
    set_treatment_start = {"name": "treatment_start",
                           "assembler": None}  # Makes the sensors send data for calibration
    set_treatment_start_data_send = {"name": "treatment_start_data_send",
                           "assembler": None}  # Makes the sensors send data for calibration

    def __init__(self, value):
        if "name" not in value:
            raise ValueError("Key 'name' needs to be provided")
        if "assembler" not in value:
            raise ValueError("Key 'assembler' needs to be provided")

    @property
    def name(self):
        return self.value["name"]

    @property
    def assembler(self):
        return self.value["assembler"]

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
