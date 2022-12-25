from django.test import TestCase
from unittest.mock import patch, Mock

from infra.models import Session
from infra.domain.alert.alert import Alert
from infra.domain.alert.generic_sensor_alert import GenericSensorAlert
from infra.domain.sensor_commands import SensorCommands
from infra.assemblers.command_assemblers.calibration_start_assembler import CalibrationStartAssembler


class CalibrationStartAssemblerTest(TestCase):
    def setUp(self) -> None:
        self.assembler = CalibrationStartAssembler()
        self.command_data = {
            "user": "1",
            "command": "calibration_start",
            "type": "ipc_command",
        }

    @patch('infra.assemblers.command_assemblers.calibration_start_assembler.CalibrationStartAssembler._create_session')
    def test_GivenCommand_whenAssemble_thenReturnAlert(self, create_session):
        create_session.return_value = Mock(spec=Session)
        alert = self.assembler.assemble(self.command_data)
        self.assertIsInstance(alert, Alert)

    @patch('infra.assemblers.command_assemblers.calibration_start_assembler.CalibrationStartAssembler._create_session')
    def test_GivenCommand_thenReturnAlertWithCommandSetSession(self, create_session):
        create_session.return_value = Mock(spec=Session)
        alert = self.assembler.assemble(self.command_data)
        self.assertEqual(alert.command, SensorCommands.set_session_alert)
        self.assertIsInstance(alert, GenericSensorAlert)

    # @patch('infra.assemblers.command_assemblers.calibration_start_assembler.get_user_model')
    #     get_user_model.return_value.objects.get.return_value = user
