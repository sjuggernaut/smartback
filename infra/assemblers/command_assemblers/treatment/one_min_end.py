"""
This class will do processing of the data after it is collected for 1 minute during treatment stage.
The 1 minute sending process is started by the command, Commands.treatment_start.
Everytime a one mind end is completed, engine processes that data received for a whole minute and the result is an stimulation output value through the sensors.
"""
import logging
from time import sleep

from infra.utils import *
from infra.models import *
import numpy as np
from infra.domain.dataclasses import *
from random import randrange
from infra.exceptions.nan_data_mean import DataMeanNanException

logger = logging.getLogger(__name__)


class TreatmentOneMinuteEndDataProcessor:

    @staticmethod
    def check_all_ipc_commands(session: Session):
        """
        To check if all the 3 IPC commands are received.
        If received from all the three (3) sensors - process the data for all the 3 sensors for 1 minute data.
        Else - return and let the sensors send the command again. then this will succeed.
        :param session:
        :param name:
        :return:
        """

        logger.info(f"Processing Treatment one-minute end IPC command for session {session.id}")
        ipc_commands = TreatmentOneMinuteEndDataProcessor.is_ipc_commands_received(session)

        if ipc_commands.session_exists:
            """
            If this condition is True: All the 3 required sensor one min end commands have been received from the 
            sensors during treatment stage. 
            """
            # It is important to set this to true to avoid duplicate processing of the same session one minute
            ipc_commands.session_instance.save()

            """
            Start processing the data from IRSensorData, SEMGSensorData, InertialSensorData for the session
            """
            stimulation_energy, stimulation_site = TreatmentOneMinuteEndDataProcessor.process_data(session)

            TreatmentOneMinuteEndDataProcessor.update_ipc_processing_status(session)

            """
            Set read_status=True for all the data from TreatmentSEMGData, TreatmentInertialData with session.
            """
            TreatmentOneMinuteEndDataProcessor.set_treatment_data_read_status(session)

            if not stimulation_site or not stimulation_energy:
                "Error with the one minute cycle data Setting the current one minute cycle"
                return False

            return {
                "energy": stimulation_energy,
                "side": stimulation_site.side
            }
        else:
            # TODO: raise Exception("Session {session.id} hasn't received all three sensor commands for one minute data processing")
            logger.info(
                f"Session {session.id} hasn't received all three sensor commands for one minute data processing")
            return False

    @staticmethod
    def set_treatment_data_read_status(session: Session):
        """
        Update the read status for all the sensor data rows in SEMG and Inertial Tables
        :param session:
        :return:
        """
        TreatmentSEMGData.objects.filter(session=session).update(read_status=True)
        TreatmentInertialData.objects.filter(session=session).update(read_status=True)

    @staticmethod
    def update_ipc_processing_status(session: Session):
        # SessionTreatmentIPCReceived.objects.filter(session=session,
        #                                            processing_status=False,
        #                                            semg_received=True,
        #                                            inertial_received=True,
        #                                            ir_received=True).update(processing_status=True)

        SessionTreatmentIPCReceived.objects.filter(session=session, processing_status=False).update(
            processing_status=True)

    @staticmethod
    def is_ipc_commands_received(session: Session) -> DataClassIPCCommandReceived:
        # session_query = SessionTreatmentIPCReceived.objects.filter(session=session,
        #                                                            processing_status=False,
        #                                                            semg_received=True,
        #                                                            inertial_received=True,
        #                                                            ir_received=True)

        session_query = SessionTreatmentIPCReceived.objects.filter(session=session, processing_status=False)

        session_exists = session_query.exists()
        session_instance = session_query.first()
        return DataClassIPCCommandReceived(session_exists=session_exists, session_instance=session_instance)

    @staticmethod
    def process_data(session: Session):
        """
        DO :: Fetch data from IRSensorData, SEMGSensorData, InertialSensorData by Session and read_status=False
        All this data is expected to be from the latest One minute send process from sensors.
        DO ::
            1. Inertial Data: compute Mean data => compute difference between mean data and gold standard
            2. SEMG Data: compute Mean data =>
                2.1: compare with gold standard
                2.2: determine left or right side for stimulation
            3. IR Data: Compute Mean data: check if mean data is less than 42 degrees celsius
        DO :: Compute Stimulation Output based on the above data
        :param session:
        :return:
        """
        try:
            """
            User's thermal value is below the threshold.
            Now process the session's previous one minute data and send the stimulation energy
            """
            user_data_mean = TreatmentOneMinuteEndDataProcessor.get_session_one_minute_data_mean(session)

            logger.info("USER DATA MEAN")
            logger.info(user_data_mean)

            """
            TODO: Uncomment below code after attaching IR sensor
            """
            # ir_mean = user_data_mean.ir[0]
            #
            # thermal_check = is_temp_higher(ir_mean)
            # if thermal_check:
            #     """
            #     Thermal value from the IR sensor is higher than the allowed value.
            #     """
            #     logger.warning(
            #         f"Thermal value from the IR sensor is higher than the allowed value. Session : {session.pk}")
            #     # raise exception
            #     return False

            user_treatment_gold_standard = TreatmentOneMinuteEndDataProcessor.get_user_treatment_gold_standard(session)

            """
            Calculate differential values for Inertial sensor, SEMG 
            """
            differential_values = TreatmentOneMinuteEndDataProcessor.calculate_differential_values(
                user_treatment_gold_standard,
                user_data_mean)

            """
            Calculate center of mass differential values 
            """
            center_of_mass_differential_values = TreatmentOneMinuteEndDataProcessor.get_center_of_mass_differential(
                differential_values.inertial)

            stimulation_site = TreatmentOneMinuteEndDataProcessor.calculate_stimulation_site(differential_values)
            stimulation_energy = TreatmentOneMinuteEndDataProcessor.calculate_stimulation_energy(
                center_of_mass_differential_values, differential_values.inertial)

            return stimulation_energy, stimulation_site

        except DataMeanNanException as ex:
            logger.info(str(ex))
            """
            Set the current one minute cycle to processed and create a new treatment cycle.
            
            """
            return False, False

        except Exception as e:
            logger.info(f"Treatment IPC: There is an error during treatment one minute end data processing: [{str(e)}]")
            return False, False

    @staticmethod
    def get_session_one_minute_data_mean(session):
        inertial_data = TreatmentInertialData.objects.filter(session=session, read_status=False)
        semg_data = TreatmentSEMGData.objects.filter(session=session, read_status=False)
        # ir_data = TreatmentIRData.objects.filter(session=session, read_status=False) # TODO: Uncomment after IR sensors are attached

        inertial_data_list = list(inertial_data.values_list(*INERTIAL_DATA_FIELDS))
        inertial_data_array = np.array(inertial_data_list)
        inertial_data_mean = inertial_data_array.mean(0).tolist()

        logger.info("INERTIAL DATA MEAN")
        logger.info(inertial_data_mean)

        semg_data_list = list(semg_data.values_list(*SEMG_DATA_FIELDS))
        semg_data_array = np.array(semg_data_list)
        semg_data_mean = semg_data_array.mean(0).tolist()

        logger.info("SEMG DATA MEAN")
        logger.info(semg_data_mean)

        if np.isnan(inertial_data_mean).any() or np.isnan(semg_data_mean).any():
            raise DataMeanNanException(session.id)

        # ir_data_list = list(ir_data.values_list('thermal'))
        # ir_data_mean = get_mean(ir_data_list)

        # return DataClassUserTreatmentMean(inertial=inertial_data_mean, semg=semg_data_mean, ir=ir_data_mean)
        return DataClassUserTreatmentMean(inertial=inertial_data_mean, semg=semg_data_mean, ir=[38])

    @staticmethod
    def get_user_treatment_gold_standard(session: Session):
        """
        UserGoldStandardInertialData and UserGoldStandardSEMGData
        Retrieve user's gold standard values for Treatment.
        :param session:
        :return:
        """
        user_inertial_gs = UserGoldStandardInertialData.objects.filter(user=session.user, is_final_data=True)
        user_semg_gs = UserGoldStandardSEMGData.objects.filter(user=session.user, is_final_data=True)

        inertial_gs_list = list(user_inertial_gs.values_list(*INERTIAL_DATA_FIELDS))
        semg_gs_list = list(user_semg_gs.values_list(*SEMG_DATA_FIELDS))

        if len(inertial_gs_list) == 1:
            inertial_gs_list = inertial_gs_list[0]

        if len(semg_gs_list) == 1:
            semg_gs_list = semg_gs_list[0]

        logger.info("========================================================")
        logger.info("USER TREATMENT GOLD STANDARD")
        logger.info(inertial_gs_list)
        logger.info(semg_gs_list)
        logger.info("========================================================")
        return DataClassTreatmentGoldStandardForUser(semg=semg_gs_list, inertial=inertial_gs_list)

    @staticmethod
    def calculate_differential_values(user_treatment_gs: DataClassTreatmentGoldStandardForUser,
                                      user_data_mean: DataClassUserTreatmentMean):
        """
        ===========================================================================================================
        SEMG Differential Value
        ===========================================================================================================

        [(Right side of the golden standard treatment sEMG values) - (Right side of client’s sEMG data)] -
        [(Left side of golden standard treatment sEMG values) - (Left side of client’s sEMG data)]

        ===========================================================================================================
        Inertial Differential Value
        ===========================================================================================================

        Inertial Gold Standard Values - Client's Inertial Data Mean

        :return:
        """
        # ====================== 1. SEMG Calculation ======================
        right_semg_gs = [right_semg_item for right_semg_index, right_semg_item in enumerate(user_treatment_gs.semg) if
                         right_semg_index in SEMG_DATA_FIELDS_RIGHT_INDICES]
        right_semg_mean = [right_semg_mean_item for right_semg_mean_index, right_semg_mean_item in
                           enumerate(user_data_mean.semg) if right_semg_mean_index in SEMG_DATA_FIELDS_RIGHT_INDICES]

        right_diff = subtract(right_semg_gs, right_semg_mean)  # This is a list of 4 SEMG values

        logger.info("========================================================")
        logger.info("DIFFERENTIAL VALUES: RIGHT SEMG")
        logger.info(right_diff)
        logger.info("========================================================")

        # Left SEMG
        left_semg_gs = [left_semg_item for left_semg_index, left_semg_item in enumerate(user_treatment_gs.semg) if
                        left_semg_index in SEMG_DATA_FIELDS_LEFT_INDICES]
        left_semg_mean = [left_semg_mean_item for left_semg_mean_index, left_semg_mean_item in
                          enumerate(user_data_mean.semg) if left_semg_mean_index in SEMG_DATA_FIELDS_LEFT_INDICES]
        left_diff = subtract(left_semg_gs, left_semg_mean)

        logger.info("========================================================")
        logger.info("DIFFERENTIAL VALUES: LEFT SEMG")
        logger.info(left_diff)
        logger.info("========================================================")

        semg_differential_value = subtract(right_diff,
                                           left_diff)  # TODO: Check this - this is a list of 4 values from SEMG

        logger.info("========================================================")
        logger.info("SEMG DIFFERENTIAL VALUES")
        logger.info(semg_differential_value)
        logger.info("========================================================")

        # ====================== 2. Inertial Calculation ======================
        inertial_differential_value = subtract(user_treatment_gs.inertial,
                                               user_data_mean.inertial)  # TODO: Check this - this is a list of 18 Inertial joint angles

        logger.info("========================================================")
        logger.info("INERTIAL DIFFERENTIAL VALUES")
        logger.info(inertial_differential_value)
        logger.info("========================================================")

        return DataClassDifferentialValuesForTreatment(semg=semg_differential_value,
                                                       inertial=inertial_differential_value)

    @staticmethod
    def calculate_stimulation_site(differential_values: DataClassDifferentialValuesForTreatment):
        """
        Compute stimulation site for the current loop cycle.
        - Step 1: Compute Inertial data
        - Step 2: Compute SEMG data
        - Step 3: Return side of stimulation site (instance of dataclass)

        ========================================================================================================
        1. Inertial Inertial Differential Value = User Treatment Gold Standard - User 1 Minute Cycle Mean Data
        ========================================================================================================

            If the Inertial Differential Value is NEGATIVE = LEFT SIDE
                   Inertial Differential Value is POSITIVE = RIGHT SIDE
                                     NEGATIVE AND POSITIVE = BOTH SIDES

        ========================================================================================================
        2. SEMG Differential Value = User Treatment Gold Standard - User 1 Minute Cycle Mean Data
        ========================================================================================================

             If the SEMG Differential Value is NEGATIVE = LEFT SIDE
                   SEMG Differential Value is POSITIVE  = RIGHT SIDE
                                            Value is 0  = BOTH SIDES

        :param differential_values:DataClassDifferentialValuesForTreatment
        :return:
        """
        inertial_result_side = None

        # ==============================================================================
        # Inertial Sensors provide 18 joint values and 3 Center of mass values
        # ==============================================================================
        inertial_positive_count = positive_count(differential_values.inertial)
        inertial_negative_count = negative_count(differential_values.inertial)

        if inertial_positive_count == len(INERTIAL_DATA_FIELDS):
            inertial_result_side = StimulationSide.right

        if inertial_negative_count == len(INERTIAL_DATA_FIELDS):
            inertial_result_side = StimulationSide.left

        if inertial_positive_count > 0 and inertial_negative_count > 0:
            inertial_result_side = StimulationSide.both

        # ==============================================================================
        # SEMG Differential values count is 2 based on the formula in calculate_differential_values()
        # ==============================================================================
        semg_positive_count = positive_count(differential_values.semg)
        semg_negative_count = negative_count(differential_values.semg)
        semg_result_side = None

        if semg_positive_count == len(differential_values.semg):
            semg_result_side = StimulationSide.right

        if semg_negative_count == len(differential_values.semg):
            semg_result_side = StimulationSide.left

        if count_nonzero(differential_values.semg) == 0:
            semg_result_side = StimulationSide.both

        # ==============================================================================
        # FINALIZE THE SIDE OF STIMULATION SITE
        # ==============================================================================
        return StimulationSide.right
        # if semg_result_side is None:
        #     return inertial_result_side
        # elif inertial_result_side == semg_result_side:
        #     return inertial_result_side
        # else:
        #     return semg_result_side

    @staticmethod
    def get_center_of_mass_differential(inertial_differential: list):
        return [com_value for com_index, com_value in enumerate(inertial_differential) if
                com_index in CENTER_OF_MASS_FIELD_INDICES]

    @staticmethod
    def calculate_stimulation_energy(com_differential: list, inertial_differential: list) -> float:
        """
        Compute stimulation energy output value for the current loop cycle.

        ========================================================================================================
        Required IR-Energy = (
            [Difference between final golden standard treatment values of CoM with client’s values of CoM]
            *
            [Difference between final golden standard treatment values of 18 inertial measurements with client’s 18 values]
        )
        /
        [60 seconds duration of IR-energy muscle stimulation]
        ========================================================================================================

        :param self:
        :return: float -  Percentage of the stimulation output value
        """
        logger.info("========================================================")
        logger.info("FINAL DIFFERENTIAL CALCULATION VALUE")
        logger.info(com_differential)
        logger.info(inertial_differential)
        logger.info("========================================================")

        # Remove center of mass values from the inertial differential
        new_inertial_differential = inertial_differential[: len(inertial_differential) - 3]

        # Original formula retained
        energy_old = (average(com_differential) * average(new_inertial_differential)) / 60
        logger.info(f"Old energy result value for this session = {energy_old}")

        energy = ((average(com_differential) * average(new_inertial_differential)) / 10) / 60

        logger.info(f"(Updated) Final result value for this session = {energy}")

        return abs(energy) * 100

        # Temporary code to send a randomly picked value under 25% to the raspberry PI PCBs.
        # return randrange(25)
