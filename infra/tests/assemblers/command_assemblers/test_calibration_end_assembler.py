# Needed for tests
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch, Mock

from infra.models import *
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

    def test_GivenUserGoldStandardAndMean_whenCalculateCalibrationFactor_thenReturnCalibrationFactor(self):
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

    def test_GivenTreatmentGoldStandard_whenGetTreatmentGoldStandard_thenReturnDataClassTreatmentGoldStandard(self):
        inertial_data = {
            "l5s1_lateral": "1.4",
            "l5s1_axial": "1.4",
            "l5s1_flexion": "2.4",
            "l4l3_lateral": "1.4",
            "l4l3_axial": "1.4",
            "l4l3_flexion": "2.4",
            "l1t12_lateral": "1.4",
            "l1t12_axial": "1.4",
            "l1t12_flexion": "2.4",
            "t9t8_lateral": "1.4",
            "t9t8_axial": "1.4",
            "t9t8_flexion": "2.4",
            "t1c7_lateral": "1.4",
            "t1c7_axial": "1.4",
            "t1c7_flexion": "2.4",
            "c1head_lateral": "1.4",
            "c1head_axial": "1.4",
            "c1head_flexion": "2.4",
            "com_posx": "2.4",
            "com_posy": "2.4",
            "com_posz": "2.4",
            "is_final_data": True
        }
        semg_data = {
            "right_multifidus": "5",
            "left_multifidus": "10",
            "rightc4_paraspinal": "20",
            "leftc4_paraspinal": "30",
            "is_final_data": True
        }
        TreatmentGoldStandardInertialData.objects.create(**inertial_data)
        TreatmentGoldStandardSEMGData.objects.create(**semg_data)
        actual_treatment_gs = self.assembler._get_treatment_gold_standard()

        self.assertIsInstance(actual_treatment_gs, DataClassTreatmentGoldStandard)
        self.assertIsNotNone(actual_treatment_gs.semg)
        self.assertIsNotNone(actual_treatment_gs.inertial)

    def test_GivenCalibrationGoldStandard_whenGetCalibrationGoldStandard_thenReturnDataClassCalibrationGoldStandard(
            self):
        procedure = Procedure.objects.create(name="test_procedure")
        inertial_data = {
            "l5s1_lateral": "1.4",
            "l5s1_axial": "1.4",
            "l5s1_flexion": "2.4",
            "l4l3_lateral": "1.4",
            "l4l3_axial": "1.4",
            "l4l3_flexion": "2.4",
            "l1t12_lateral": "1.4",
            "l1t12_axial": "1.4",
            "l1t12_flexion": "2.4",
            "t9t8_lateral": "1.4",
            "t9t8_axial": "1.4",
            "t9t8_flexion": "2.4",
            "t1c7_lateral": "1.4",
            "t1c7_axial": "1.4",
            "t1c7_flexion": "2.4",
            "c1head_lateral": "1.4",
            "c1head_axial": "1.4",
            "c1head_flexion": "2.4",
            "com_posx": "2.4",
            "com_posy": "2.4",
            "com_posz": "2.4",
            "is_final_data": True,
            "procedure": procedure
        }
        semg_data = {
            "right_multifidus": "5",
            "left_multifidus": "10",
            "rightc4_paraspinal": "20",
            "leftc4_paraspinal": "30",
            "is_final_data": True,
            "procedure": procedure
        }
        ProcedureGoldStandardInertialData.objects.create(**inertial_data)
        ProcedureGoldStandardSEMGData.objects.create(**semg_data)
        actual_gs = self.assembler._get_calibration_gold_standard(procedure)

        self.assertIsInstance(actual_gs, DataClassProcedureGoldStandard)
        self.assertIsNotNone(actual_gs.semg)
        self.assertIsNotNone(actual_gs.inertial)

