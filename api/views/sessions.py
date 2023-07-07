import logging
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, mixins, generics

from infra.models import Session, SessionTypes, StatusChoices, SessionTreatmentIPCReceived
from users.models import DecisionLevel2
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


class DecisionToProceedView(generics.GenericAPIView):
    """
    Check if the user is eligible to proceed to sessions based on the Decision questionnaire
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = None
    pagination_class = None
    scoring_map = {
        "1-4 weeks": 1,
        "4-8 weeks": 1,
        "Pain in the upper region of your back": 1,
        "Pain in the middle region of your back": 1,
        "Pain in the lower region of your back": 1,
        "Comes and goes": 3,
        "Constant": 2,
        "During the morning": 1,
        "In the afternoon": 2,
        "In the evening": 3,
        "At night": 2,
        "Present entire day": 0,
        "Pain starts with physical activity": 1,
        "Pain ends with physical activity": 2,
        "Pain starts after physical activity": 3,
        "Pain is not related with physical activity": 1,
        "Pain relieved with rest": 3,
        "Pain starts while resting": 2,
        "Pain is not related with rest": 1,
        "Pain is localised": 3,
        "Pain is spreading to back only": 2,
        "Pain is spreading outside of my back area": 1,
        "Aching": 3,
        "Burning": 2,
        "Dull": 3,
        "Gripping": 1,
        "Heavy": 2,
        "Intense": 2,
        "Prickly": 1,
        "Sharp": 1,
        "Shooting": 1,
        "Stabbing": 1,
        "Stinging": 1,
        "Throbbing": 1,
    }

    def get(self, request, *args, **kwargs):
        try:
            decision_q = DecisionLevel2.objects.filter(user=request.user)
            if decision_q.exists():
                user_q_values = list(
                    decision_q.values_list('pain_since', 'pain_location', 'constant_pain', 'pain_start',
                                           'relation_physical_activity', 'relation_rest', 'is_pain_spreading',
                                           'pain_description'))[0]
                user_q_sum = 0
                for value in user_q_values:
                    value_score = self.scoring_map.get(value, 0)
                    logger.info(f"Calculated value {value_score} for Option: {value}")
                    user_q_sum += value_score
            return Response(data={"score": user_q_sum, "eligible": True if user_q_sum >= 9 else False},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
