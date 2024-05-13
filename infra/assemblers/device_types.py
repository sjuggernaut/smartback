from enum import Enum


class DeviceTypes(Enum):
    device_semg = {"name": "device_semg", "label": "semg"}
    device_inertial = {"name": "device_inertial", "label": "inertial"}
    device_ir = {"name": "device_ir", "label": "ir"}

    def __init__(self, value):
        if "name" not in value:
            raise ValueError("Key 'name' needs to be provided")

    @property
    def name(self):
        return self.value["name"]

    @property
    def label(self):
        return self.value["label"]

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
