from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from users.serializers import UserSerializer, PersonalCharacteristicsSerializer
from rest_framework import generics, response
from rest_framework.permissions import IsAuthenticated

from users.models import PersonalCharacteristics


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


class PersonalCharacteristicsDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or Update Personal Characteristics instance for a user
    """
    queryset = PersonalCharacteristics.objects.all()
    serializer_class = PersonalCharacteristicsSerializer
    pagination_class = None
