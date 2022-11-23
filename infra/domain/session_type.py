from enum import Enum


class SessionType(Enum):
    calibration = {"name": "calibration"}
    treatment = {"name": "treatment"}

    def __init__(self, value):
        if "name" not in value:
            raise ValueError("Key 'name' not provided.")

    @property
    def name(self):
        return self.value["name"]

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
