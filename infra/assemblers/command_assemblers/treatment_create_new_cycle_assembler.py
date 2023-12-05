import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.alert import Alert
from infra.domain.alert.calibration_alert import CalibrationEndAlert
from infra.exceptions.filter_out import FilterOutException
from infra.models import *
from infra.domain.sensor_commands import SensorCommands
from infra.assemblers.command_assemblers.calibration.calibration_end_data_processor import CalibrationEndDataProcessor

logger = logging.getLogger(__name__)



class TreatmentCreateNewCycleAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> Alert:
        """
        :param command_data:
        :return:
        """
        logger.info(f"Received Calibration End command.")

        try:
            session_id = command_data.get("session")
            session = Session.objects.get(id=session_id)

            treatment_cycle = self.create_new_ipc_treatment_record(session)
            logger.info(f"Created Treatment cycle for Session {session_id}")
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

        logger.info(f"Creating new treatment cycle for session {session.id}")
        session = SessionTreatmentIPCReceived.objects.create(
            session=session,
            processing_status=False,
            semg_received=False,
            inertial_received=False,
            ir_received=False
        )
        return session

