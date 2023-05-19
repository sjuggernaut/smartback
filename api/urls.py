from api.views.sessions import *
from django.urls import path

urlpatterns = [
    path('sessions', SessionCreateView.as_view()),
    path('sessions/<str:type>', SessionListView.as_view()),
    path('sessions/<str:type>/latest', LatestSessionView.as_view()),
    path('sessions/<str:pk>/detail', SessionDetailView.as_view()),
]
