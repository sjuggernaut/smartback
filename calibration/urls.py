from .views import *
from django.urls import path, include

urlpatterns = [
    path('', CalibrationSessionCreateView.as_view()),

    path('step', CalibrationStepCreateView.as_view()),
]
