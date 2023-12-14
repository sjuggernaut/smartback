import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.alert import Alert
from infra.exceptions.filter_out import FilterOutException
from infra.models import *
from infra.domain.sensor_commands import SensorCommands
from infra.domain.alert.generic_sensor_alert import TreatmentStartDataSendAlert

logger = logging.getLogger(__name__)


class TreatmentCreateNewCycleAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> Alert:
        """
        :param command_data:
        :return:
        """
        try:
            session_id = command_data.get("session")
            session = Session.objects.get(id=session_id)

            logger.info(f"Received request to Create new Treatment cycle command for Session [{session.id}].")

            """
            Check if session not ENDED
            """
            if session.status in (StatusChoices.COMPLETED, StatusChoices.FAILED):
                raise FilterOutException(
                    __name__,
                    f"Will not create a new treatment cycle. Invalid Session provided. Session [{session.id}] is either Completed or Failed"
                )

            treatment_cycle = self.create_new_ipc_treatment_record(session)
            logger.info(f"Created Treatment cycle for Session {session_id} | Treatment Cycle ID = {treatment_cycle.id}")

            """
            Upon creation of new treatment cycle - send Command.treatment_start_data_send to Inertial Sensor and SEMG Sensor
            """
            return TreatmentStartDataSendAlert(
                command=SensorCommands.set_treatment_start_data_send.name,
                session=str(session.pk)
            )
        except Exception as e:
            raise FilterOutException(__name__, e)

    def create_new_ipc_treatment_record(self, session: Session):
        """
        Create new record for SessionTreatmentIPCReceived for next one minute cycle.
        Record created for current treatment session for the user.
        :param session:Session
        """
        if session.type != SessionTypes.TREATMENT:
            logger.info(
                f"The provided session type is not {SessionTypes.TREATMENT}. Skipping creation of IPC Treatment record.")
            return False

        # TODO: check if there's an existing In progress treatment cycle before creating new cycle.

        logger.info(f"Creating new treatment cycle for session {session.id}")
        session = SessionTreatmentIPCReceived.objects.create(
            session=session,
            processing_status=False,
            semg_received=False,
            inertial_received=False,
            ir_received=False
        )
        return session
