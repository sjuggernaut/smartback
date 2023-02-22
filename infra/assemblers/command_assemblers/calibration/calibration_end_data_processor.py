import logging

from infra.models import *
from users.models import PersonalCharacteristics
from infra.utils import get_mean, compare_with_gold_standard, multiply_list_with, subtract_then_average, average, \
    INERTIAL_DATA_FIELDS, SEMG_DATA_FIELDS
from infra.domain.dataclasses import *
from infra.serializers import UserTreatmentGoldStandardInertialSensorDataSerializer, \
    UserTreatmentGoldStandardSEMGSensorDataSerializer

logger = logging.getLogger(__name__)


class CalibrationEndDataProcessor:
    def __init__(self, session: Session):
        self._session = session
        user_pc = PersonalCharacteristics.objects.get(user=session.user)
        self.user_bmi = user_pc.get_bmi

    def process_user_calibration_session_data(self, session: Session, procedure: Procedure):
        """
        Entry method to this class.
        The goal is to calculate User's Calibration Session Data and Calculate the User's Treatment Gold Standard
        Values for Inertial Sensor data and sEMG sensor data.
        :param session:
        :param procedure:
        :return:
        """
        # Calculate Calibration GS
        user_calibration_gs = self._calculate_user_calibration_gold_standard(session, procedure)
        user_data_mean = DataClassUserCalibrationMean(semg=None, inertial=None)

        # Calculate Treatment GS
        calibration_factor = self.calculate_calibration_factor(user_calibration_gs, user_data_mean)
        treatment_gs = self.get_universal_treatment_gold_standard()
        user_treatment_gs = self.calculate_user_treatment_gold_standard(calibration_factor, treatment_gs)

        self._save_user_treatment_gold_standard(session, user_treatment_gs)

    def calculate_user_treatment_gold_standard(self, calibration_factor: float,
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

        # Multiply the Calibration Factor with Treatment Gold standard obtained for User's BMI
        semg_gs = multiply_list_with(calibration_factor, bmi_based_semg_gs)
        inertial_gs = multiply_list_with(calibration_factor, bmi_based_inertial_gs)

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
        Step 2: user's data mean (vector value) - user's calibration gold standard (vector value) = Calibration factor (scalar value)
        :return:
        """
        semg_diff = subtract_then_average(user_gs.semg, data_mean.semg)
        inertial_diff = subtract_then_average(user_gs.inertial, data_mean.inertial)

        return average([semg_diff, inertial_diff])

    def _get_session_sensor_data(self):
        calibration_semg_data = CalibrationStepSEMGData.objects.filter(session=self._session, read_status=False)
        calibration_inertial_data = CalibrationStepInertialData.objects.filter(session=self._session, read_status=False)
        # calibration_ir_data = CalibrationStepIRData.objects.filter(session=self._session, read_status=False)

        inertial_data_list = list(calibration_inertial_data.values_list(*INERTIAL_DATA_FIELDS))
        semg_data_list = list(calibration_semg_data.values_list(*SEMG_DATA_FIELDS))
        # ir_data_list = list(calibration_ir_data.values_list('thermal'))

        semg_data_mean = get_mean(semg_data_list)
        inertial_data_mean = get_mean(inertial_data_list)

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
        inertial_serializer = UserTreatmentGoldStandardInertialSensorDataSerializer(data=gold_standard.inertial)
        inertial_serializer.is_valid(raise_exception=True)
        inertial_serializer.save()

        semg_serializer = UserTreatmentGoldStandardSEMGSensorDataSerializer(data=gold_standard.semg)
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
