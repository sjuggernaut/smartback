# Needed for tests
import django

django.setup()

import json
from unittest.mock import patch, Mock

from django.test import TestCase
from django.contrib.auth.models import User

from kafka.consumer.fetcher import ConsumerRecord
from infra.assemblers.inertial_sensor_assembler import KafkaInertialSensorAssembler
from infra.models import Session, SessionTypes, TreatmentInertialData, ProcedureStep, CalibrationStep, Procedure, \
    CalibrationStepInertialData
from infra.exceptions.filter_out import FilterOutException


class KafkaInertialSensorAssemblerTest(TestCase):
    def setUp(self) -> None:
        self.assembler = KafkaInertialSensorAssembler()
        user = User.objects.create_user(username='test_user')
        self.treatment_session = Session.objects.create(type=SessionTypes.TREATMENT, user=user)
        self.calibration_session = Session.objects.create(type=SessionTypes.CALIBRATION, user=user)

    @patch("infra.assemblers.inertial_sensor_assembler.json.loads")
    def test_GivenInertialDataForTreatment_whenAssemble_thenSaveData(self, json_loads):
        command_data = {
            "type": "treatment",
            "session": str(self.treatment_session.id),
            "data": {
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
                "com_posz": "2.4"
            }
        }

        kafka_message = Mock(spec=ConsumerRecord)
        kafka_message.value.decode.return_value = json.dumps(command_data)
        kafka_message.offset = 1
        kafka_message.topic = "inertialsensor-alerts-tests"
        kafka_message.timestamp = 281473556639264
        json_loads.return_value = command_data

        self.assembler.assemble(kafka_message)
        db_inertial_data = TreatmentInertialData.objects.filter(session=self.treatment_session)

        self.assertGreater(db_inertial_data.count(), 0)
        self.assertEqual(db_inertial_data.first().com_posx, 2.4)
        self.assertEqual(db_inertial_data.first().l5s1_lateral, 1.4)

    @patch("infra.assemblers.inertial_sensor_assembler.json.loads")
    def test_GivenInvalidInertialDataForTreatment_whenAssemble_thenRaiseException(self, json_loads):
        command_data = {
            "type": "treatment",
            "data": {
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
                "com_posz": "2.4"
            }
        }

        kafka_message = Mock(spec=ConsumerRecord)
        kafka_message.value.decode.return_value = json.dumps(command_data)
        kafka_message.offset = 1
        kafka_message.topic = "inertialsensor-alerts-tests"
        kafka_message.timestamp = 281473556639264
        json_loads.return_value = command_data

        with self.assertRaises(FilterOutException):
            self.assembler.assemble(kafka_message)

    @patch("infra.assemblers.inertial_sensor_assembler.json.loads")
    def test_GivenInertialDataForCalibration_whenAssemble_thenSaveData(self, json_loads):
        procedure = Procedure.objects.create(name="test_procedure")
        step = ProcedureStep.objects.create(name="test_procedure_step", procedure=procedure)
        calibration_step = CalibrationStep.objects.create(session=self.calibration_session, step=step)

        command_data = {
            "type": "calibration",
            "session": str(self.calibration_session.id),
            "step": str(calibration_step.pk),
            "data": {
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
                "com_posz": "2.4"
            }
        }

        kafka_message = Mock(spec=ConsumerRecord)
        kafka_message.value.decode.return_value = json.dumps(command_data)
        kafka_message.offset = 1
        kafka_message.topic = "inertialsensor-alerts-tests"
        kafka_message.timestamp = 281473556639264
        json_loads.return_value = command_data

        self.assembler.assemble(kafka_message)
        db_inertial_data = CalibrationStepInertialData.objects.filter(session=self.calibration_session)

        self.assertGreater(db_inertial_data.count(), 0)
        self.assertEqual(db_inertial_data.first().com_posx, 2.4)
        self.assertEqual(db_inertial_data.first().l5s1_lateral, 1.4)

    @patch("infra.assemblers.inertial_sensor_assembler.json.loads")
    def test_GivenInvalidInertialDataForCalibration_whenAssemble_thenRaiseException(self, json_loads):
        command_data = {
            "type": "calibration",
            "session": str(self.calibration_session.id),
            "data": {
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
                "com_posz": "2.4"
            }
        }

        kafka_message = Mock(spec=ConsumerRecord)
        kafka_message.value.decode.return_value = json.dumps(command_data)
        kafka_message.offset = 1
        kafka_message.topic = "inertialsensor-alerts-tests"
        kafka_message.timestamp = 281473556639264
        json_loads.return_value = command_data

        with self.assertRaises(FilterOutException):
            self.assembler.assemble(kafka_message)
