from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from users.serializers import *
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError

from users.models import PersonalCharacteristics, PhysicalActivityLevel, BackPainLevel, Diseases, DecisionLevel2


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (AllowAny,)

        return super(UserViewSet, self).get_permissions()


class PersonalCharacteristicsCreateView(generics.CreateAPIView, generics.RetrieveUpdateAPIView,
                                        generics.GenericAPIView):
    """
    Create Personal Characteristics instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = PersonalCharacteristics.objects.all()
    serializer_class = PersonalCharacteristicsSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            return super().create(request, args, kwargs)
        except IntegrityError:
            return self.update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            user_pc = PersonalCharacteristics.objects.filter(user=request.user).last()
            if not user_pc:
                raise PersonalCharacteristics.DoesNotExist
            serializer = PersonalCharacteristicsSerializer(user_pc, many=False)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except PersonalCharacteristics.DoesNotExist:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            user_pc = PersonalCharacteristics.objects.filter(user=request.user).last()
            serializer = self.get_serializer(user_pc, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class PhysicalActivityLevelCreateView(generics.CreateAPIView, generics.RetrieveUpdateAPIView, generics.GenericAPIView):
    """
    Create Physical Activity Level instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = PhysicalActivityLevel.objects.all()
    serializer_class = PhysicalActivityLevelSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            return super().create(request, args, kwargs)
        except IntegrityError:
            return self.update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            user_pa = PhysicalActivityLevel.objects.filter(user=request.user).last()
            if user_pa:
                serializer = PhysicalActivityLevelSerializer(user_pa, many=False)
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return response.Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            user_pc = PhysicalActivityLevel.objects.filter(user=request.user).last()
            serializer = self.get_serializer(user_pc, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class BackPainLevelCreateView(generics.CreateAPIView, generics.RetrieveUpdateAPIView, generics.GenericAPIView):
    """
    Create Personal Characteristics instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = BackPainLevel.objects.all()
    serializer_class = BackPainLevelSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            return super().create(request, args, kwargs)
        except IntegrityError:
            return self.update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            backpain_level = BackPainLevel.objects.filter(user=request.user).last()
            if backpain_level:
                serializer = BackPainLevelSerializer(backpain_level, many=False)
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return response.Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            user_pc = BackPainLevel.objects.filter(user=request.user).last()
            serializer = self.get_serializer(user_pc, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class DiseasesCreateView(generics.CreateAPIView, generics.RetrieveUpdateAPIView, generics.GenericAPIView):
    """
    Create Personal Characteristics instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = Diseases.objects.all()
    serializer_class = DiseasesSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            return super().create(request, args, kwargs)
        except IntegrityError:
            return self.update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            user_diseases = Diseases.objects.filter(user=request.user).last()
            if user_diseases:
                serializer = DiseasesSerializer(user_diseases, many=False)
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return response.Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            user_pc = Diseases.objects.filter(user=request.user).last()
            serializer = self.get_serializer(user_pc, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class DecisionLevel2CreateView(generics.CreateAPIView, generics.RetrieveUpdateAPIView, generics.GenericAPIView):
    """
    Create Personal Characteristics instance for a user
    """
    permission_classes = (IsAuthenticated,)
    queryset = DecisionLevel2.objects.all()
    serializer_class = DecisionLevel2Serializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            return super().create(request, args, kwargs)
        except IntegrityError:
            return self.update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            level2 = DecisionLevel2.objects.filter(user=request.user).last()
            if level2:
                serializer = DecisionLevel2Serializer(level2, many=False)
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return response.Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            user_pc = DecisionLevel2.objects.filter(user=request.user).last()
            serializer = self.get_serializer(user_pc, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
