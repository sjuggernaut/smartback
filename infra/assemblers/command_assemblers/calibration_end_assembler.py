import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.command_process import CommandProcess
from infra.exceptions.filter_out import FilterOutException
from infra.models import *
from infra.utils import get_mean, compare_with_gold_standard, INERTIAL_DATA_FIELDS, SEMG_DATA_FIELDS

logger = logging.getLogger(__name__)


class CalibrationEndAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> CommandProcess:
        logger.info(f"Received Calibration End command.")

        try:
            session_id = command_data.get("session")
            session = Session.objects.get(id=session_id)

            calibration_semg_data = CalibrationStepSEMGData.objects.get(session=session, read_status=False)
            calibration_inertial_data = CalibrationStepInertialData.objects.get(session=session, read_status=False)
            calibration_ir_data = CalibrationStepIRData.objects.get(session=session, read_status=False)

            inertial_data_list = list(calibration_inertial_data.values_list(*INERTIAL_DATA_FIELDS))
            semg_data_list = list(calibration_semg_data.values_list(*SEMG_DATA_FIELDS))
            ir_data_list = list(calibration_ir_data.values_list('thermal'))

            semg_data_mean = get_mean(semg_data_list)
            inertial_data_mean = get_mean(inertial_data_list)
            ir_data_mean = get_mean(ir_data_list)

            inertial_gold_std, semg_gold_std = self._get_procedure_gold_standard()
            if None in (inertial_gold_std, semg_gold_std):
                logger.info(f"CalibrationEnd Assembler: Stopping creation of gold standard for the user {session.user.id}")
                return False

            self._calculate_user_gold_standard(session.user, inertial_gold_std, semg_gold_std)


            # TODO:
            # DONE:  In this assembler - fetch data from CalibrationStepSEMGData, CalibrationStepInertialData, CalibrationStepIRData per session
            # YET TO Review the process, but get the Gold standard from ProcedureGoldStandardSEMGData, ProcedureGoldStandardInertialData
            # compute gold standard by BMI on the procedure gold standard
            # and store the gold standard for the user to UserGoldStandardSEMGData, UserGoldStandardInertialData
            # use this gold standard value during treatment one minute end process
            # pseudo method calls:-
            # self._get_procedure_gold_standard(procedure)
            # self._calculate_user_gold_standard(user)
            # self.__save_user_gold_standard(user)

            self._update_read_status(calibration_semg_data, calibration_inertial_data, calibration_ir_data)
        except Exception as e:
            raise FilterOutException(__name__, e)

    def _update_read_status(self, semg_queryset, inertial_queryset, ir_queryset):
        semg_queryset.update(read_status=True)
        ir_queryset.update(read_status=True)
        inertial_queryset.update(read_status=True)

    def _calculate_user_gold_standard(self, user, **kwargs):
        # use the bmi for the user and the gold standard values to prepare user's gold standard
        pass

    def _get_procedure_gold_standard(self, procedure):
        # Get the Gold standard from ProcedureGoldStandardSEMGData, ProcedureGoldStandardInertialData
        try:
            inertial_gs = ProcedureGoldStandardInertialData.objects.get(procedure=procedure, is_final=True)
            semg_gs = ProcedureGoldStandardSEMGData.objects.get(procedure=procedure, is_final=True)
            return inertial_gs, semg_gs
        except (ProcedureGoldStandardSEMGData.DoesNotExist, ProcedureGoldStandardInertialData.DoesNotExist):
            logger.info("CalibrationEnd Assembler: Failed to fetch procedure gold standard.")
            return None, None

    def _save_user_gold_standard(self, user, inertial_data, semg_data):
        # store the gold standard for the user to UserGoldStandardSEMGData, UserGoldStandardInertialData
        # use update or create to create users gold standard and set is_final attribute on the model = True
        pass