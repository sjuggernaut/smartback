from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import PersonalCharacteristics, PhysicalActivityLevel, BackPainLevel, Diseases, DecisionLevel2

import logging

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'username',
            'password',
            'email'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super(UserSerializer, self).update(instance, validated_data)


class PersonalCharacteristicsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = PersonalCharacteristics
        fields = '__all__'
        read_only_fields = ("user",)


class PersonalCharacteristicsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalCharacteristics
        fields = ['birth_year', 'height', 'weight', 'gender', 'ethnicity', 'body_type']


class PhysicalActivityLevelSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = PhysicalActivityLevel
        fields = '__all__'
        read_only_fields = ("user",)


class PhysicalActivityLevelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalActivityLevel
        fields = ['activity_level_before_pain', 'activity_level_during_pain', 'regular_activity', 'activity_per_week']


class BackPainLevelSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = BackPainLevel
        fields = '__all__'
        read_only_fields = ("user",)


class BackPainLevelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackPainLevel
        fields = ['back_pain_level', 'is_job_heavy', 'is_desk_work_all_day', 'healthcare_consult', 'pain_relief',
                  'is_taking_medication']


class DiseasesSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Diseases
        fields = '__all__'
        read_only_fields = ("user",)


class DiseasesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diseases
        fields = ['chronic_back_pain', 'unsteady_gait', 'bowel_bladder_symptoms',
                  'relief_with_rest', 'leg_pain', 'leukaemia', 'chemotherapy', 'gastrointestinal_carcinoma', 'surgery',
                  'myositis']


class DecisionLevel2Serializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = DecisionLevel2
        fields = '__all__'
        read_only_fields = ("user",)


class DecisionLevel2UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionLevel2
        fields = ['pain_since',
                  'pain_location',
                  'constant_pain',
                  'pain_start',
                  'relation_physical_activity',
                  'relation_rest',
                  'is_pain_spreading',
                  'pain_description'
                  ]
