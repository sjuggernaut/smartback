import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.exceptions.filter_out import FilterOutException
from infra.models import Session, SessionTreatmentIPCReceived
from infra.assemblers.device_types import DeviceTypes
from infra.domain.alert.alert import Alert
from infra.assemblers.command_assemblers.treatment.one_min_end import TreatmentOneMinuteEndDataProcessor

logger = logging.getLogger(__name__)

"""
Data comes into ipc-alerts topic from the sensor  
In this assembler: read data from the db for the "session" & "device": calculate mean data  
"""


class TreatmentOneMinEndAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> Alert:
        logger.info(f"Received Treatment One Minute End command.")

        try:
            session_id = command_data.get("session")
            session = Session.objects.get(id=session_id)

            data_device_type = command_data.get("device_type")
            device_type = DeviceTypes.__getitem__(data_device_type)

            device_type_received_field = f"{device_type.label}_received"
            device_type_received_time_field = f"{device_type.label}_received_time"

            """
            Update the SessionTreatmentIPCReceived object based on the type of sensor sender
            """
            SessionTreatmentIPCReceived.objects.filter(session=session).update(**{device_type_received_field: True})

            """
            Send the treatment data to IR LED through ipc-alerts topic.
            """
            treatment_data = TreatmentOneMinuteEndDataProcessor.check_all_ipc_commands(session)

            ipc_producer.send(treatment_data)
        except Exception as e:
            raise FilterOutException(__name__, e)
