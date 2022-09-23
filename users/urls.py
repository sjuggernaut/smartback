from .views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),

    path('personal', PersonalCharacteristicsCreateView.as_view()),
    path('personal/<str:pk>', PersonalCharacteristicsDetailUpdateView.as_view()),

]
