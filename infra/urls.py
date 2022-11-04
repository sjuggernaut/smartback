from .views import *
from django.urls import path, include

urlpatterns = [
    path('session', SessionCreateView.as_view()),
    path('step', CalibrationStepCreateView.as_view()),
]
