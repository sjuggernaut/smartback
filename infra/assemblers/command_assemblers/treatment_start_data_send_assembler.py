import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.generic_sensor_alert import TreatmentStartDataSendAlert
from infra.domain.sensor_commands import SensorCommands
from infra.models import *
from infra.exceptions.filter_out import FilterOutException

from infra.domain.alert.alert import Alert

logger = logging.getLogger(__name__)

"""
Command Name: Treatment_start_data_send
Command Received From: User Interface  
Triggers sensors to start sending the data for the given treatment session. (Session ID is already set in the sesions localstorage before this command is triggered)
"""


class TreatmentStartDataSendAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> Alert:
        """
        Triggers start of sending data from Sensors to Kafka topics.
        - This creates a new treatment cycle record ie. SessionTreatmentIPCReceived
        - Eventually the new treatment cycle records will be created once the existing record is complete.
        :param command_data:
        :return:
        """
        try:
            logger.info(f"Received Treatment start data send command from the User Interface.")

            user = command_data.get("user")
            session = Session.objects.filter(user=user, status=StatusChoices.CREATED,
                                             type=SessionTypes.TREATMENT).last()

            if session:
                self._create_ipc_treatment_commands_received(session)
                self._update_session_status(session)
                alert = TreatmentStartDataSendAlert(command=SensorCommands.set_treatment_start_data_send.name,
                                                    session=str(session.pk))
                return alert
            return None  # replace with InvalidAlert instance
        except Exception as e:
            raise FilterOutException(__name__, str(e))

    def _update_session_status(self, session: Session):
        session.status = StatusChoices.STARTED
        session.save()

    def _create_ipc_treatment_commands_received(self, session: Session):
        SessionTreatmentIPCReceived.objects.create(session=session)
