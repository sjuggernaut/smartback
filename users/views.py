from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from users.serializers import *
from rest_framework import generics, response
from rest_framework.permissions import IsAuthenticated

from users.models import PersonalCharacteristics, PhysicalActivityLevel, BackPainLevel, Diseases, DecisionLevel2


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (AllowAny,)

        return super(UserViewSet, self).get_permissions()


class PersonalCharacteristicsCreateView(generics.CreateAPIView):
    """
    Create Personal Characteristics instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = PersonalCharacteristics.objects.all()
    serializer_class = PersonalCharacteristicsSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().create(request, args, kwargs)


class PersonalCharacteristicsDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or Update Personal Characteristics instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = PersonalCharacteristics.objects.all()
    serializer_class = PersonalCharacteristicsUpdateSerializer
    pagination_class = None


class PhysicalActivityLevelCreateView(generics.CreateAPIView):
    """
    Create Physical Activity instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = PhysicalActivityLevel.objects.all()
    serializer_class = PhysicalActivityLevelSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().create(request, args, kwargs)


class PhysicalActivityLevelDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or Update Physical Activity instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = PhysicalActivityLevel.objects.all()
    serializer_class = PhysicalActivityLevelUpdateSerializer
    pagination_class = None


class BackPainLevelCreateView(generics.CreateAPIView):
    """
    Create BackPainLevel instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = BackPainLevel.objects.all()
    serializer_class = BackPainLevelSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().create(request, args, kwargs)


class BackPainLevelDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or Update BackPainLevel instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = BackPainLevel.objects.all()
    serializer_class = BackPainLevelUpdateSerializer
    pagination_class = None


class DiseasesCreateView(generics.CreateAPIView):
    """
    Create Diseases instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = Diseases.objects.all()
    serializer_class = DiseasesSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().create(request, args, kwargs)


class DiseasesDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or Update Diseases instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = Diseases.objects.all()
    serializer_class = DiseasesUpdateSerializer
    pagination_class = None


class DecisionLevel2CreateView(generics.CreateAPIView):
    """
    Create Decision Level 2 instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = DecisionLevel2.objects.all()
    serializer_class = DecisionLevel2Serializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        return super().create(request, args, kwargs)


class DecisionLevel2DetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or Update Decision Level 2 instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = DecisionLevel2.objects.all()
    serializer_class = DecisionLevel2UpdateSerializer
    pagination_class = None