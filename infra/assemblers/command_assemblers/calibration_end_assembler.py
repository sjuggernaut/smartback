import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.alert import Alert
from infra.exceptions.filter_out import FilterOutException
from infra.models import *
from infra.utils import get_mean, compare_with_gold_standard, multiply_list_with, subtract_then_average, average, \
    INERTIAL_DATA_FIELDS, SEMG_DATA_FIELDS
from infra.domain.sensor_commands import SensorCommands
from infra.domain.dataclasses import *

logger = logging.getLogger(__name__)

"""
Command Name: Calibration_end
Command Received From: User Interface  
Command Purpose: Calibration phase is ended when this command is received from the user interface. 
                 The User Interface application will send the command to Kafka topic: IPC
                 The current Calibration Session is set to COMPLETED 
                 Clear_Session command is sent to the Sensors to clear the session ID from the sensor devices.   
"""


class CalibrationEndAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> Alert:
        logger.info(f"Received Calibration End command.")

        try:
            session_id = command_data.get("session")
            session = Session.objects.get(id=session_id)

            procedure_id = command_data.get("procedure")
            procedure = Procedure.objects.get(id=procedure_id)

            # self._calculate_user_gold_standard(session)


            # Send calibration stop command to user's sensors to stop the data sending process
            return Alert(command=SensorCommands.set_calibration_stop, devices=command_data.get("devices"))
        except Exception as e:
            raise FilterOutException(__name__, e)

    def _get_session_sensor_data(self, session):
        calibration_semg_data = CalibrationStepSEMGData.objects.filter(session=session, read_status=False)
        calibration_inertial_data = CalibrationStepInertialData.objects.filter(session=session, read_status=False)
        calibration_ir_data = CalibrationStepIRData.objects.filter(session=session, read_status=False)

        inertial_data_list = list(calibration_inertial_data.values_list(*INERTIAL_DATA_FIELDS))
        semg_data_list = list(calibration_semg_data.values_list(*SEMG_DATA_FIELDS))
        ir_data_list = list(calibration_ir_data.values_list('thermal'))

        semg_data_mean = get_mean(semg_data_list)
        inertial_data_mean = get_mean(inertial_data_list)
        ir_data_mean = get_mean(ir_data_list)

    def _update_read_status(self, semg_queryset, inertial_queryset, ir_queryset):
        semg_queryset.update(read_status=True)
        ir_queryset.update(read_status=True)
        inertial_queryset.update(read_status=True)

    def _calculate_user_gold_standard(self, session: Session, procedure: Procedure):
        user_calibration_gs = self._calculate_user_calibration_gold_standard(session, procedure)
        user_data_mean = DataClassUserCalibrationMean(semg=None, inertial=None)

        calibration_factor = self._calculate_calibration_factor(user_calibration_gs, user_data_mean)
        treatment_gs = self._get_treatment_gold_standard()

        user_treatment_gs = self._calculate_user_treatment_gold_standard(calibration_factor, treatment_gs)

        self._save_user_gold_standard(session, user_treatment_gs)

    def _get_treatment_gold_standard(self):
        """
        Returns the Treatment Gold standard from the models: [TreatmentGoldStandardInertialData, TreatmentGoldStandardSEMGData]
        Treatment gold standard data has no multiple data rows. Only one row data with is_final_data=True is possible.
        :return: list, list
        """
        try:
            inertial_gs = TreatmentGoldStandardInertialData.objects.filter(is_final_data=True)
            inertial_gs_list = list(inertial_gs.values_list(*INERTIAL_DATA_FIELDS))

            semg_gs = TreatmentGoldStandardSEMGData.objects.filter(is_final_data=True)
            semg_gs_list = list(semg_gs.values_list(*SEMG_DATA_FIELDS))

            return DataClassTreatmentGoldStandard(semg_gs_list, inertial_gs_list)
        except (TreatmentGoldStandardInertialData.DoesNotExist, TreatmentGoldStandardSEMGData.DoesNotExist):
            logger.info("CalibrationEnd Assembler: Failed to fetch treatment gold standard.")

        return None, None

    def _get_calibration_gold_standard(self, procedure):
        """
        Returns the Calibration Gold standard for a procedure from the models: [ProcedureGoldStandardSEMGData, ProcedureGoldStandardInertialData]
        :param procedure: Procedure instance for which the user has performed calibration process
        :return: list, list
        """
        try:
            inertial_gs = ProcedureGoldStandardInertialData.objects.get(procedure=procedure, is_final=True)
            inertial_gs_list = list(inertial_gs.values_list(*INERTIAL_DATA_FIELDS))

            semg_gs = ProcedureGoldStandardSEMGData.objects.get(procedure=procedure, is_final=True)
            semg_gs_list = list(semg_gs.values_list(*SEMG_DATA_FIELDS))

            return DataClassProcedureGoldStandard(semg_gs_list, inertial_gs_list)
        except (ProcedureGoldStandardSEMGData.DoesNotExist, ProcedureGoldStandardInertialData.DoesNotExist):
            logger.info("CalibrationEnd Assembler: Failed to fetch procedure gold standard.")

        return None, None

    def _calculate_user_calibration_gold_standard(self, session, procedure):
        """
        STEP 1
        This is Step 1 in calculation of user's treatment gold standard:
        Formula: calibration gold standard values * BMI (scalar value) = User's calibration gold standard (vector)
        :param session:
        :param procedure:
        :return:
        """
        procedure_calibration_gs = self._get_calibration_gold_standard(procedure)
        user_bmi = session.user.bmi

        user_inertial_gs = multiply_list_with(user_bmi, procedure_calibration_gs.inertial)
        user_semg_gs = multiply_list_with(user_bmi, procedure_calibration_gs.semg)
        return DataClassUserCalibrationGoldStandard(user_semg_gs, user_inertial_gs)

    def _calculate_calibration_factor(self, user_gs: DataClassUserCalibrationGoldStandard,
                                      data_mean: DataClassUserCalibrationMean):
        """
        STEP 2
        Step 2: user's data mean (vector value) - user's calibration gold standard (vector value) = Calibration factor (scalar value)
        :return:
        """
        semg_diff = subtract_then_average(user_gs.semg, data_mean.semg)
        inertial_diff = subtract_then_average(user_gs.inertial, data_mean.inertial)

        return average([semg_diff, inertial_diff])

    def _calculate_user_treatment_gold_standard(self, calibration_factor: float,
                                                treatment_gs: DataClassTreatmentGoldStandard):
        """
        STEP 3
        Step 3: Calibration Factor * Treatment Gold Standard = User's treatment gold standard values (vector value)
        :return:
        """
        semg_gs = multiply_list_with(calibration_factor, treatment_gs.semg)
        inertial_gs = multiply_list_with(calibration_factor, treatment_gs.inertial)

        return DataClassTreatmentGoldStandardForUser(semg=semg_gs, inertial=inertial_gs)

    def _save_user_gold_standard(self, session, gold_standard: DataClassTreatmentGoldStandardForUser):
        """
        Step 1: store the gold standard for the user to UserGoldStandardSEMGData, UserGoldStandardInertialData
        Step 2:
                Step 2.1: use update or create to create users gold standard. UserGoldStandardInertialData, UserGoldStandardSEMGData
                Step 2.2: set is_final=True on the gold standard data instance.
        :param session:
        :param gold_standard:
        :return:
        """
        pass
