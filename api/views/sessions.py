import logging
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, mixins, generics

from infra.models import Session, SessionTypes, StatusChoices, SessionTreatmentIPCReceived
from infra.domain.alert.generic_sensor_alert import SessionStartAlert
from infra.domain.commands import Commands
from api.serializers.sessions import SessionSerializer, SessionDetailSerializer
from api.serializers.segments import SegmentsSerializer
from api.views.view_config import *

logger = logging.getLogger(__name__)


class SessionCreateView(generics.CreateAPIView):
    """
    Create a new session for the authorized user (user that supplied token)
    Send to kafka backend to start the session
    """
    permission_classes = (IsAuthenticated,)
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            session_type = request.data["type"]
            if session_type == session_types.get("treatment"):
                alert = SessionStartAlert(command=Commands.treatment_start.name, user=request.user.id)
            else:
                alert = SessionStartAlert(command=Commands.calibration_start.name, user=request.user.id)

            kafka_service.send(alert)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SessionListView(generics.ListAPIView):
    """
    List all the sessions for the authorized user (user that supplied token)
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = SessionSerializer
    pagination_class = None

    def get_queryset(self):
        """
        Prepare queryset for the given session.type
        """
        session_type = self.kwargs.get('type')
        return Session.objects.filter(type=session_types.get(session_type, SessionTypes.TREATMENT),
                                      user=self.request.user)


class SessionDetailView(generics.RetrieveAPIView):
    """
    Detail of a session
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = SessionDetailSerializer
    pagination_class = None
    queryset = Session.objects.all()


class LatestSessionView(generics.GenericAPIView):
    """
    Last created session based on type for the authenticated user.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = SessionDetailSerializer
    pagination_class = None

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object(self):
        """
        Prepare last queryset for the given session.type
        """
        session_type = self.kwargs.get('type')

        latest_started_session = Session.objects.filter(type=session_types.get(session_type, SessionTypes.TREATMENT),
                                                        status=StatusChoices.STARTED,
                                                        user=self.request.user).order_by('started_at').last()

        if not latest_started_session:
            latest_created_session = Session.objects.filter(
                type=session_types.get(session_type, SessionTypes.TREATMENT),
                status=StatusChoices.CREATED,
                user=self.request.user).order_by('started_at').last()

            if not latest_created_session:
                return Session.objects.filter(type=session_types.get(session_type, SessionTypes.TREATMENT),
                                              user=self.request.user).order_by('started_at').last()

            return latest_created_session

        return latest_started_session


class SessionSegmentsView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    serializer_class = SegmentsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Prepare segments queryset for the given session
        """
        session = Session.objects.get(pk=self.kwargs.get('pk'))
        return SessionTreatmentIPCReceived.objects.filter(session=session)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request.data["session"] = self.kwargs.get('pk')
        alert = SessionStartAlert(command=Commands.treatment_start_data_send.name, user=request.user.id)
        kafka_service.send(alert)
        return Response(status=status.HTTP_201_CREATED)

    # class CalibrationStepCreateView(generics.CreateAPIView):
#     """
#     Add a new Calibration Session Step for the user.
#     This means the FE will start calibration process for a Procedure Step
#     This CalibrationStep instance will be used to identify the data from the 3 Sensors : Inertial, SEMG and IR data.
#     """
#     permission_classes = (IsAuthenticated,)
#     queryset = CalibrationStep.objects.all()
#     serializer_class = CalibrationStepCreateSerializer
#     pagination_class = None
#
#     def create(self, request, *args, **kwargs):
#         try:
#             request.data["user"] = request.user.id
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             # self.perform_create(serializer)
#             headers = self.get_success_headers(serializer.data)
#
#             """
#             KAFKA produce to IPC topic to capture data for the step
#             Send Calibration ID, Device ID, Step ID,
#             If the Device ID matches with the consuming process's env var - DEVICE_ID - the sensor will start producing
#             to the topic.
#             the produced data includes Calibration ID, Device ID, Step ID
#             """
#             self._send_to_kafka(request)
#
#             return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#         except IntegrityError as exception:
#             logger.exception(f"There is an error while adding a calibration step. [{exception}]")
#             return Response({"message": "Duplicate calibration step failed to add."},
#                             status=status.HTTP_400_BAD_REQUEST)
