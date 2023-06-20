import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.exceptions.filter_out import FilterOutException
from infra.models import Session, StatusChoices, SessionTypes, SessionTreatmentIPCReceived
from infra.domain.alert.generic_sensor_alert import TreatmentAbruptDataSendAlert
from infra.domain.alert.alert import Alert
from infra.domain.sensor_commands import SensorCommands

logger = logging.getLogger(__name__)


class TreatmentAbruptEndAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> Alert:
        logger.info(f"Received Treatment Abrupt End command.")

        try:
            """
            This assembler will update treatment session, set the status = COMPLETED for the provided user 
            """
            user = command_data.get("user")
            last_treatment_session = Session.objects.filter(user=user,
                                                            status__in=(StatusChoices.STARTED, StatusChoices.CREATED),
                                                            type=SessionTypes.TREATMENT).last()
            logger.info(f"Treatment Abrupt End: Found session {last_treatment_session} for the user {user}")

            self._update_session_status(last_treatment_session)
            SessionTreatmentIPCReceived.objects.filter(session=last_treatment_session).update(processing_status=True)
            return TreatmentAbruptDataSendAlert(command=SensorCommands.treatment_abrupt_end.name, user=user)
        except Exception as e:
            logger.exception(f"There was an error processing the treatment end request.")
            raise FilterOutException(__name__, str(e))

    def _update_session_status(self, session):
        logger.info(f"Updating session status = COMPLETED for ID = [{session.pk}]")
        session.status = StatusChoices.COMPLETED
        session.save()
