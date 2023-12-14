from api.views.sessions import *
from api.views.calibration import *
from api.views.treatment import *
from django.urls import path

urlpatterns = [
    path('sessions', SessionCreateView.as_view()),
    path('sessions/<str:type>', SessionListView.as_view()),
    path('sessions/<str:type>/latest', LatestSessionView.as_view()),
    path('sessions/<str:pk>/detail', SessionDetailView.as_view()),
    path('sessions/<str:pk>/segments', SessionSegmentsView.as_view()),

    # Calibration specific endpoints
    path('sessions/calibration/step', CalibrationStepCreateView.as_view()),
    path('sessions/calibration/end', CalibrationEndView.as_view()),

    # Treatment specific endpoints
    path('sessions/treatment/abruptend', TreatmentAbruptEndView.as_view()),
    path('sessions/treatment/endonemin', TreatmentOneMinuteEndView.as_view()),
    path('sessions/treatment/startonemin', TreatmentStartDataSendOneMinuteView.as_view()),
    path('sessions/treatment/createnewcycle', TreatmentStartDataSendOneMinuteView.as_view()), # create new api view class

    path('decision', DecisionToProceedView.as_view()),
]
