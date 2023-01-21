# Needed for tests
import django

django.setup()

import json
from unittest.mock import patch, Mock

from django.test import TestCase
from django.contrib.auth.models import User

from kafka.consumer.fetcher import ConsumerRecord
from infra.assemblers.semg_sensor_assembler import KafkaSEMGSensorAssembler
from infra.models import Session, SessionTypes, TreatmentSEMGData, ProcedureStep, CalibrationStep, Procedure, \
    CalibrationStepSEMGData
from infra.exceptions.filter_out import FilterOutException


class KafkaSEMGSensorAssemblerTest(TestCase):
    def setUp(self) -> None:
        self.assembler = KafkaSEMGSensorAssembler()
        user = User.objects.create_user(username='test_user')
        self.treatment_session = Session.objects.create(type=SessionTypes.TREATMENT, user=user)
        self.calibration_session = Session.objects.create(type=SessionTypes.CALIBRATION, user=user)

    @patch("infra.assemblers.semg_sensor_assembler.json.loads")
    def test_GivenSEMGDataForTreatment_whenAssemble_thenSaveData(self, json_loads):
        command_data = {
            "type": "treatment",
            "session": str(self.treatment_session.id),
            "data": {
                "right_multifidus": "5",
                "left_multifidus": "10",
                "rightc4_paraspinal": "20",
                "leftc4_paraspinal": "30"
            }
        }

        kafka_message = Mock(spec=ConsumerRecord)
        kafka_message.value.decode.return_value = json.dumps(command_data)
        kafka_message.offset = 1
        kafka_message.topic = "semgsensor-alerts-tests"
        kafka_message.timestamp = 281473556639264
        json_loads.return_value = command_data

        self.assembler.assemble(kafka_message)
        db_semg_data = TreatmentSEMGData.objects.filter(session=self.treatment_session)

        self.assertGreater(db_semg_data.count(), 0)
        self.assertEqual(db_semg_data.first().rightc4_paraspinal, 20)
        self.assertEqual(db_semg_data.first().right_multifidus, 5)

    @patch("infra.assemblers.semg_sensor_assembler.json.loads")
    def test_GivenInvalidSEMGDataForTreatment_whenAssemble_thenRaiseException(self, json_loads):
        command_data = {
            "type": "treatment",
            "data": {
                "left_multifidus": "10",
                "rightc4_paraspinal": "20",
                "leftc4_paraspinal": "30"
            }
        }

        kafka_message = Mock(spec=ConsumerRecord)
        kafka_message.value.decode.return_value = json.dumps(command_data)
        kafka_message.offset = 1
        kafka_message.topic = "semgsensor-alerts-tests"
        kafka_message.timestamp = 281473556639264
        json_loads.return_value = command_data

        with self.assertRaises(FilterOutException):
            self.assembler.assemble(kafka_message)

    @patch("infra.assemblers.semg_sensor_assembler.json.loads")
    def test_GivenSEMGDataForCalibration_whenAssemble_thenSaveData(self, json_loads):
        procedure = Procedure.objects.create(name="test_procedure")
        step = ProcedureStep.objects.create(name="test_procedure_step", procedure=procedure)
        calibration_step = CalibrationStep.objects.create(session=self.calibration_session, step=step)

        command_data = {
            "type": "calibration",
            "session": str(self.calibration_session.id),
            "step": str(calibration_step.pk),
            "data": {
                "right_multifidus": "5",
                "left_multifidus": "10",
                "rightc4_paraspinal": "20",
                "leftc4_paraspinal": "30"
            }
        }

        kafka_message = Mock(spec=ConsumerRecord)
        kafka_message.value.decode.return_value = json.dumps(command_data)
        kafka_message.offset = 1
        kafka_message.topic = "semgsensor-alerts-tests"
        kafka_message.timestamp = 281473556639264
        json_loads.return_value = command_data

        self.assembler.assemble(kafka_message)
        db_semg_data = CalibrationStepSEMGData.objects.filter(session=self.calibration_session)

        self.assertGreater(db_semg_data.count(), 0)
        self.assertEqual(db_semg_data.first().rightc4_paraspinal, 20)
        self.assertEqual(db_semg_data.first().right_multifidus, 5)

    @patch("infra.assemblers.semg_sensor_assembler.json.loads")
    def test_GivenInvalidSEMGDataForCalibration_whenAssemble_thenRaiseException(self, json_loads):
        command_data = {
            "type": "calibration",
            "session": str(self.calibration_session.id),
            "data": {
                "right_multifidus": "5",
                "left_multifidus": "10",
                "rightc4_paraspinal": "20",
                "leftc4_paraspinal": "30"
            }
        }

        kafka_message = Mock(spec=ConsumerRecord)
        kafka_message.value.decode.return_value = json.dumps(command_data)
        kafka_message.offset = 1
        kafka_message.topic = "semgsensor-alerts-tests"
        kafka_message.timestamp = 281473556639264
        json_loads.return_value = command_data

        with self.assertRaises(FilterOutException):
            self.assembler.assemble(kafka_message)
