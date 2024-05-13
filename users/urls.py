from .views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'accounts', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),

    path('personal', PersonalCharacteristicsCreateView.as_view()),

    path('physical', PhysicalActivityLevelCreateView.as_view()),

    path('backpain', BackPainLevelCreateView.as_view()),

    path('diseases', DiseasesCreateView.as_view()),

    path('level2', DecisionLevel2CreateView.as_view()),
]
