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
