from dataclasses import dataclass


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
