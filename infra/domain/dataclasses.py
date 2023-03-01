from dataclasses import dataclass
from enum import Enum


@dataclass
class DataClassValueLists:
    semg: list
    inertial: list


@dataclass
class DataClassProcedureGoldStandard(DataClassValueLists):
    pass


@dataclass
class DataClassUserCalibrationGoldStandard(DataClassValueLists):
    pass


@dataclass
class DataClassUserCalibrationMean(DataClassValueLists):
    pass


@dataclass
class DataClassTreatmentGoldStandard(DataClassValueLists):
    pass


@dataclass
class DataClassTreatmentGoldStandardForUser(DataClassValueLists):
    pass


@dataclass
class DataClassDifferentialValuesForTreatment(DataClassValueLists):
    pass


@dataclass
class DataClassSEMGRightSideValues:
    rightc4_paraspinal: float
    right_multifidus: float


@dataclass
class DataClassSEMGLefttSideValues:
    left_multifidus: float
    leftc4_paraspinal: float


@dataclass
class DataClassUserTreatmentMean(DataClassValueLists):
    ir: list


@dataclass
class DataClassIPCCommandReceived:
    session_exists: float
    session_instance: float


class StimulationSide(Enum):
    right = {"side": "right"}
    left = {"side": "left"}
    both = {"side": "both"}

    def __init__(self, value):
        if "side" not in value:
            raise ValueError("Key 'side' needs to be provided")

    @property
    def side(self):
        return self.value["side"]

    def __str__(self):
        return self.side

    def __hash__(self):
        return hash(self.side)
