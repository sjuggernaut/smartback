import logging
import numpy as np
from django.db.models import Q

from infra.models import *
from users.models import PersonalCharacteristics
from infra.utils import get_mean, compare_with_gold_standard, multiply_list_with, subtract_then_average, average, \
    INERTIAL_DATA_FIELDS, SEMG_DATA_FIELDS, add_scalar_to_list_items, subtract, add_two_lists_element_wise
from infra.domain.dataclasses import *
from infra.serializers import UserTreatmentGoldStandardInertialSensorDataSerializer, \
    UserTreatmentGoldStandardSEMGSensorDataSerializer

logger = logging.getLogger(__name__)


class CalibrationEndDataProcessor:
    def __init__(self, session: Session):
        self._session = session

        try:
            # user_pc = PersonalCharacteristics.objects.get(user=session.user.id)
            self.user_bmi = 17.2
            # self.user_bmi = user_pc.get_bmi
        except Exception as e:
            logger.exception(str(e))

    def process_user_calibration_session_data(self, session: Session, procedure: Procedure):
        """
        Entry method to this class.
        The goal is to calculate User's Calibration Session Data and Calculate the User's Treatment Gold Standard
        Values for Inertial Sensor data and sEMG sensor data.
        :param session:
        :param procedure:
        :return:
        """
        if not self.user_bmi:
            logger.warning(
                "Could not find BMI data for the user. Please check the Personal Characteristics data for the user "
                "and try this process again")

        user_data_mean = self._get_session_sensor_data()

        logger.info("User data mean")
        logger.info(user_data_mean)

        if not user_data_mean:
            logger.warning(
                f"SESSION ID = [{session.pk}] :: Error in processing user calibration end session data. Could not find SEMG or Inertial data for the session.")
            return False

        # Calculate Treatment GS
        user_calibration_gs = self._calculate_user_calibration_gold_standard(session, procedure)  # BMI based value

        logger.info(f"BMI based calibration gold standard {user_calibration_gs}")

        calibration_factor_semg, calibration_factor_inertial = self.calculate_calibration_factor(user_calibration_gs,
                                                                                                 user_data_mean)


        treatment_gs = self.get_universal_treatment_gold_standard()
        user_treatment_gs = self.calculate_user_treatment_gold_standard(calibration_factor_semg,
                                                                        calibration_factor_inertial, treatment_gs)

        logger.info(f"User treatment gold standard {user_treatment_gs}")

        # Save user treatment gold standard and set session data read status to true
        self._save_user_treatment_gold_standard(session, user_treatment_gs)
        self._set_session_data_read_flag()

    def _set_session_data_read_flag(self):
        CalibrationStepSEMGData.objects.filter(session=self._session).update(read_status=True)
        CalibrationStepInertialData.objects.filter(session=self._session).update(read_status=True)

    def calculate_user_treatment_gold_standard(self, calibration_factor_semg: float, calibration_factor_inertial: float,
                                               universal_treatment_gs: DataClassTreatmentGoldStandard):
        """
        STEP 3
        Multiply the Universal Treatment Gold with the User's BMI
        Then Multiply the Calibration Factor with the User's BMI Treatment Gold Standard
        Step 3: Calibration Factor * User's BMI Treatment Gold Standard = User's treatment gold standard values (vector value)
        :return:
        """
        # Multiply the Universal Treatment Gold Standard with the User's BMI
        bmi_based_semg_gs = multiply_list_with(self.user_bmi, universal_treatment_gs.semg)
        bmi_based_inertial_gs = multiply_list_with(self.user_bmi, universal_treatment_gs.inertial)

        logger.info(f"BMI based GS {bmi_based_inertial_gs} {bmi_based_semg_gs}")

        # Adjusting to the calibration factor = Add CF to BMI based GS
        # Add each element in the calibration factor list (SEMG and inertial) to the BMI based list (SEMG and inertial)
        # semg_gs = add_scalar_to_list_items(calibration_factor_semg, bmi_based_semg_gs)
        # inertial_gs = add_scalar_to_list_items(calibration_factor_inertial, bmi_based_inertial_gs)

        semg_gs = add_two_lists_element_wise(calibration_factor_semg, bmi_based_semg_gs)
        inertial_gs = add_two_lists_element_wise(calibration_factor_inertial, bmi_based_inertial_gs)

        logger.info("=========================")
        logger.info(semg_gs)
        logger.info(inertial_gs)

        return DataClassTreatmentGoldStandardForUser(semg=semg_gs, inertial=inertial_gs)

    def _calculate_user_calibration_gold_standard(self, session, procedure):
        """
        STEP 1
        This step calculates user's calibration gold standard values.
        Formula: calibration gold standard values * BMI (scalar value) = User's calibration gold standard (vector)
        :param session:
        :param procedure:
        :return:
        """
        procedure_calibration_gs = self.get_universal_calibration_gold_standard(procedure)

        user_inertial_gs = multiply_list_with(self.user_bmi, procedure_calibration_gs.inertial)
        user_semg_gs = multiply_list_with(self.user_bmi, procedure_calibration_gs.semg)

        return DataClassUserCalibrationGoldStandard(user_semg_gs, user_inertial_gs)

    def calculate_calibration_factor(self, user_gs: DataClassUserCalibrationGoldStandard,
                                     data_mean: DataClassUserCalibrationMean):
        """
        STEP 2
        Step 2: user's data mean (vector value) - user's calibration gold standard (vector value) = Calibration factor for SEMG and Inertial (Vector value)
        :return:
        """
        semg_diff = subtract(user_gs.semg, data_mean.semg)
        inertial_diff = subtract(user_gs.inertial, data_mean.inertial)

        """
        Subtract but no average of the list of SEMG and Inertial data 
        """
        logger.info(f"Calibration factor inertial {inertial_diff} and semg = {semg_diff}")

        return semg_diff, inertial_diff

    def _get_session_sensor_data(self):
        calibration_semg_data = CalibrationStepSEMGData.objects.filter(session=self._session, read_status=False)
        calibration_inertial_data = CalibrationStepInertialData.objects.filter(session=self._session, read_status=False)
        # calibration_ir_data = CalibrationStepIRData.objects.filter(session=self._session, read_status=False)

        inertial_data_list = list(calibration_inertial_data.exclude(Q(com_posx__isnull=True) |
                                                                    Q(com_posy__isnull=True) |
                                                                    Q(com_posz__isnull=True) |
                                                                    Q(c1head_flexion__isnull=True) |
                                                                    Q(c1head_axial__isnull=True) |
                                                                    Q(c1head_lateral__isnull=True) |
                                                                    Q(t1c7_flexion__isnull=True) |
                                                                    Q(t1c7_axial__isnull=True) |
                                                                    Q(t1c7_lateral__isnull=True) |
                                                                    Q(t9t8_flexion__isnull=True) |
                                                                    Q(t9t8_axial__isnull=True) |
                                                                    Q(t9t8_lateral__isnull=True) |
                                                                    Q(l1t12_flexion__isnull=True) |
                                                                    Q(l1t12_axial__isnull=True) |
                                                                    Q(l1t12_lateral__isnull=True) |
                                                                    Q(l5s1_lateral__isnull=True) |
                                                                    Q(l5s1_axial__isnull=True) |
                                                                    Q(l5s1_flexion__isnull=True) |
                                                                    Q(l4l3_lateral__isnull=True) |
                                                                    Q(l4l3_axial__isnull=True) |
                                                                    Q(l4l3_flexion__isnull=True)).values_list(
            *INERTIAL_DATA_FIELDS))
        semg_data_list = list(calibration_semg_data.values_list(*SEMG_DATA_FIELDS))
        # ir_data_list = list(calibration_ir_data.values_list('thermal'))

        if len(semg_data_list) == 0 or len(inertial_data_list) == 0:
            return False

        semg_data_array = np.array(semg_data_list)
        semg_data_mean = semg_data_array.mean(0).tolist()

        inertial_data_array = np.array(inertial_data_list)
        inertial_data_mean = inertial_data_array.mean(0).tolist()

        return DataClassUserCalibrationMean(semg=semg_data_mean, inertial=inertial_data_mean)

    def _update_read_status(self, semg_queryset, inertial_queryset, ir_queryset):
        semg_queryset.update(read_status=True)
        ir_queryset.update(read_status=True)
        inertial_queryset.update(read_status=True)

    def _save_user_treatment_gold_standard(self, session, gold_standard: DataClassTreatmentGoldStandardForUser):
        """
        Step 1: store the gold standard for the user to UserGoldStandardSEMGData, UserGoldStandardInertialData
        Step 2:
                Step 2.1: use update or create to create users gold standard. UserGoldStandardInertialData, UserGoldStandardSEMGData
                Step 2.2: set is_final=True on the gold standard data instance.
        :param session:
        :param gold_standard:
        :return:
        """
        inertial_data, semg_data = self._transform_to_model_fields(gold_standard)
        inertial_data["user"] = session.user.pk
        inertial_data["is_final_data"] = True
        semg_data["user"] = session.user.pk
        semg_data["is_final_data"] = True

        # Remove previous gold standard values for the user
        UserGoldStandardInertialData.objects.filter(user=session.user).delete()
        UserGoldStandardSEMGData.objects.filter(user=session.user).delete()

        inertial_serializer = UserTreatmentGoldStandardInertialSensorDataSerializer(data=inertial_data)
        inertial_serializer.is_valid(raise_exception=True)
        inertial_serializer.save()

        semg_serializer = UserTreatmentGoldStandardSEMGSensorDataSerializer(data=semg_data)
        semg_serializer.is_valid(raise_exception=True)
        semg_serializer.save()

    def get_universal_treatment_gold_standard(self):
        """
        Returns the Treatment Gold standard from the models: [TreatmentGoldStandardInertialData, TreatmentGoldStandardSEMGData]
        Treatment gold standard data has no multiple data rows. Only one row data with is_final_data=True is possible.
        :return: list, list
        """
        try:
            inertial_gs = TreatmentGoldStandardInertialData.objects.filter(is_final_data=True)
            inertial_gs_list = list(inertial_gs.values_list(*INERTIAL_DATA_FIELDS))

            inertial_gs_list = inertial_gs_list[0] if len(inertial_gs_list) > 0 else None

            semg_gs = TreatmentGoldStandardSEMGData.objects.filter(is_final_data=True)
            semg_gs_list = list(semg_gs.values_list(*SEMG_DATA_FIELDS))

            semg_gs_list = semg_gs_list[0] if len(semg_gs_list) > 0 else None

            return DataClassTreatmentGoldStandard(semg_gs_list, inertial_gs_list)
        except (TreatmentGoldStandardInertialData.DoesNotExist, TreatmentGoldStandardSEMGData.DoesNotExist):
            logger.info("CalibrationEnd Assembler: Failed to fetch treatment gold standard.")

        return None, None

    def get_universal_calibration_gold_standard(self, procedure: Procedure):
        """
        Returns the Universal Calibration Gold standard for a procedure from the models: ProcedureGoldStandardSEMGData, ProcedureGoldStandardInertialData
        :param procedure: Procedure instance for which the user has performed calibration process
        :return: DataClassProcedureGoldStandard
        """
        try:
            inertial_gs = ProcedureGoldStandardInertialData.objects.filter(procedure=procedure, is_final_data=True)
            inertial_gs_list = list(inertial_gs.values_list(*INERTIAL_DATA_FIELDS))
            inertial_gs_list = inertial_gs_list[0] if len(inertial_gs_list) > 0 else None

            semg_gs = ProcedureGoldStandardSEMGData.objects.filter(procedure=procedure, is_final_data=True)
            semg_gs_list = list(semg_gs.values_list(*SEMG_DATA_FIELDS))
            semg_gs_list = semg_gs_list[0] if len(semg_gs_list) > 0 else None

            return DataClassProcedureGoldStandard(semg_gs_list, inertial_gs_list)
        except (ProcedureGoldStandardSEMGData.DoesNotExist, ProcedureGoldStandardInertialData.DoesNotExist):
            logger.info("CalibrationEnd Assembler: Failed to fetch procedure gold standard.")

        return None, None

    def _transform_to_model_fields(self, values):
        inertial_list = values.inertial
        semg_list = values.semg
        inertial_dict = dict.fromkeys(INERTIAL_DATA_FIELDS)
        semg_dict = dict.fromkeys(SEMG_DATA_FIELDS)

        inertial_dict_keys_list = list(inertial_dict.keys())
        semg_dict_keys_list = list(semg_dict.keys())

        for field_index, field_value in enumerate(inertial_list):
            field_key = inertial_dict_keys_list[field_index]
            inertial_dict[field_key] = field_value

        for field_index, field_value in enumerate(semg_list):
            field_key = semg_dict_keys_list[field_index]
            semg_dict[field_key] = field_value

        return inertial_dict, semg_dict
