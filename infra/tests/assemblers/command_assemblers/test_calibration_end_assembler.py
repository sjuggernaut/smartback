# Needed for tests
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch, Mock

from infra.models import Session, Procedure
from infra.assemblers.command_assemblers.calibration_end_assembler import CalibrationEndAssembler
from infra.domain.dataclasses import *


class CalibrationEndAssemblerTest(TestCase):
    def setUp(self) -> None:
        self.assembler = CalibrationEndAssembler()
        self.command_data = {
            "user": "1",
            "command": "calibration_start",
            "type": "ipc_command",
        }

    @patch(
        'infra.assemblers.command_assemblers.calibration_end_assembler.CalibrationEndAssembler._get_calibration_gold_standard')
    def test_GivenSessionAndProcedure_whenCalculateUserGoldStandard_thenReturnUserGoldStandard(self,
                                                                                               get_calibration_gold_standard):
        dataclass_procedure_gold_standard = Mock(spec=DataClassProcedureGoldStandard,
                                                 semg=[1, 2, 3],
                                                 inertial=[1, 2, 3])
        get_calibration_gold_standard.return_value = dataclass_procedure_gold_standard
        session = Mock(spec=Session)
        session.user.bmi = 5
        procedure = Mock(spec=Procedure)

        user_calibration_gs = self.assembler._calculate_user_calibration_gold_standard(session, procedure)

        self.assertIsInstance(user_calibration_gs, DataClassUserCalibrationGoldStandard)
        self.assertEqual(user_calibration_gs.semg, [5.0, 10.0, 15.0])
        self.assertEqual(user_calibration_gs.inertial, [5.0, 10.0, 15.0])

    def test_GivenUserGoldStandardAndMean_whenCalculateCalibrationFactor_thenReturnFactor(self):
        user_gs = DataClassUserCalibrationGoldStandard(semg=[10, 12, 14], inertial=[4, 6, 8])
        user_mean = DataClassUserCalibrationMean(semg=[2, 5, 10], inertial=[1, 2, 5])

        calibration_factor = self.assembler._calculate_calibration_factor(user_gs, user_mean)
        self.assertIsNotNone(calibration_factor)
        self.assertGreater(calibration_factor, 0)

    def test_GivenTreatmentGoldStandardAndCalibrationFactor_whenCalculate_thenReturnUserGoldStandardForTreatment(self):
        treatment_gs = DataClassTreatmentGoldStandard(semg=[10, 12, 14], inertial=[4, 6, 8])
        calibration_factor = 5

        user_treatment_gs = self.assembler._calculate_user_treatment_gold_standard(calibration_factor, treatment_gs)
        self.assertIsInstance(user_treatment_gs, DataClassTreatmentGoldStandardForUser)
        self.assertEqual(user_treatment_gs.semg, [50.0, 60.0, 70.0])
        self.assertEqual(user_treatment_gs.inertial, [20.0, 30.0, 40.0])
