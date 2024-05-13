# Needed for tests
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch, Mock

from infra.models import Session
from infra.domain.alert.alert import Alert
from infra.domain.alert.generic_sensor_alert import GenericSensorAlert
from infra.domain.sensor_commands import SensorCommands
from infra.assemblers.command_assemblers.treatment_start_assembler import TreatmentStartAssembler


class TreatmentStartAssemblerTest(TestCase):
    def setUp(self) -> None:
        self.assembler = TreatmentStartAssembler()
        self.command_data = {
            "user": "1",
            "command": "treatment_start",
            "type": "ipc_command",
            "devices": {
                "semg": "1",
                "inertial": "2",
                "ir": "3"
            }
        }

    @patch('infra.assemblers.command_assemblers.treatment_start_assembler.TreatmentStartAssembler._create_session')
    def test_GivenCommand_whenAssemble_thenReturnAlert(self, create_session):
        create_session.return_value = Mock(spec=Session)
        alert = self.assembler.assemble(self.command_data)
        self.assertIsInstance(alert, Alert)

    @patch('infra.assemblers.command_assemblers.treatment_start_assembler.TreatmentStartAssembler._create_session')
    def test_GivenCommand_thenReturnAlertWithCommandSetSession(self, create_session):
        create_session.return_value = Mock(spec=Session)
        alert = self.assembler.assemble(self.command_data)
        self.assertEqual(alert.command, SensorCommands.set_session_alert)
        self.assertIsInstance(alert, GenericSensorAlert)

