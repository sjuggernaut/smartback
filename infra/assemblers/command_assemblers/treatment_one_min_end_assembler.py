import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.exceptions.filter_out import FilterOutException
from infra.models import Session, SessionTreatmentIPCReceived, StatusChoices, SessionTypes
from infra.assemblers.device_types import DeviceTypes
from infra.domain.alert.generic_sensor_alert import TreatmentResultAlert
from infra.domain.alert.alert import Alert
from infra.assemblers.command_assemblers.treatment.one_min_end import TreatmentOneMinuteEndDataProcessor
import json
from infra.domain.sensor_commands import SensorCommands

logger = logging.getLogger(__name__)

"""
Data comes into ipc-alerts topic from the sensor  
In this assembler: read data from the db for the "session" & "device": calculate mean data  
"""


class TreatmentOneMinEndAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> Alert:
        logger.info(f"Received Treatment One Minute End command.")

        try:
            user = command_data.get("user")
            session = Session.objects.filter(user=user, status=StatusChoices.STARTED, type=SessionTypes.TREATMENT).last()

            treatment_data = TreatmentOneMinuteEndDataProcessor.check_all_ipc_commands(session)

            if treatment_data:
                """
                Send the treatment data to IR LED through ipc-results-* topic.
                """
                logger.info(f"Treatment data for the session: {session} :: {treatment_data}")
                return TreatmentResultAlert(command=SensorCommands.implement_treatment_result.name,
                                            session=str(session.id),
                                            energy=treatment_data.get("energy"), side=treatment_data.get("side"))
            else:
                logger.exception(f"There was an error processing the one minute data for the session: {session.pk}")
        except Exception as e:
            raise FilterOutException(__name__, str(e))
