import logging

from django.contrib.auth import get_user_model

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.command_process import CommandProcess
from infra.exceptions.filter_out import FilterOutException
from infra.domain.alert.generic_sensor_alert import TreatmentStartAlert
from infra.domain.sensor_commands import SensorCommands
from infra.models import Session, SessionTypes, StatusChoices, CalibrationAndTreatmentSessionRelation

from infra.domain.session_type import SessionType
from infra.domain.alert.alert import Alert

logger = logging.getLogger(__name__)

"""
Command Name: Treatment_Start
Command Received From: User Interface  
Command Purpose: Treatment phase is to be started when this command is received from the user interface. 
                 The User Interface application will send the command to Kafka topic: IPC topic
                 A new Treatment Session is created for the user and the SESSION ID is sent to the sensors. (produced to IPC topic) 
                 The message to send the SESSION ID is a generic message. Along with the SESSION ID, session type is also sent to the sensors. 
                 Sensors store the SESSION ID in their ENVIRONMENT Variables until a new session ID is sent.  
"""


class TreatmentStartAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> Alert:
        try:
            logger.info(f"Received Treatment Start command.")

            if "user" not in command_data:
                logger.info("Calibration Start: User data not found in the message received from the user interface.")
                return False

            # Get the user who has triggered calibration start command
            user_id = command_data.get("user")
            user = get_user_model().objects.get(pk=user_id)

            # Create a treatment session to be set in all the sensors' ENV
            session = self._create_session(user)

            # Link Calibration to treatment session
            link_record = self._link_calibration_to_treatment(session, user)
            if link_record:
                logger.info(f"Linked Sessions: [Treatment] {str(session.pk)} to Calibration {str(link_record.pk)}")

            # Produce the session to sensors.
            alert = TreatmentStartAlert(command=SensorCommands.set_treatment_start.name,
                                        session=str(session.pk),
                                        session_type=SessionType.TREATMENT.name.lower(),
                                        )
            return alert
        except Exception as e:
            raise FilterOutException(__name__, e)

    def _create_session(self, user):
        """
        If there's a Session object with type=Treatment, status=CREATED or STARTED user=user: use that session
        Else: create a new session record with the given parameters
        :param user_id:
        :return:
        """
        latest_session = Session.objects.filter(user=user, status__in=(StatusChoices.CREATED, StatusChoices.STARTED),
                                                type=SessionTypes.TREATMENT).last()

        if latest_session:
            logger.info("Responding with existing treatment session.")
            return latest_session

        session = Session(user=user, type=SessionTypes.TREATMENT, status=StatusChoices.CREATED)
        session.save()
        return session

    def _link_calibration_to_treatment(self, treatment_session, user):
        calibration_session = Session.objects.filter(user=user,
                                                     status=StatusChoices.COMPLETED,
                                                     type=SessionTypes.CALIBRATION).order_by('started_at').last()

        if calibration_session:
            link = CalibrationAndTreatmentSessionRelation(calibration_session=calibration_session,
                                                          treatment_session=treatment_session)
            link.save()
            return link
        return False
