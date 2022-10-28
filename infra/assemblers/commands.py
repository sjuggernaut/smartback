from enum import Enum


class Commands(Enum):
    calibration_step_start = {"name": "calibration_step_start"}
    calibration_stop = {"name": "calibration_stop"}
    treatment_start = {"name": "treatment_start"}

    def __init__(self, value):
        if "name" not in value:
            raise ValueError("Key 'name' needs to be provided")

    @property
    def name(self):
        return self.value["name"]

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
